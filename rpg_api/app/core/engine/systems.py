import esper
from rich.text import Text
from app.core.engine.components import PositionComponent, InteractableComponent, RenderComponent
from app.core.entities.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
import random


class RenderSystem:
    """Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em um único frame Text."""

    def renderizar_frame(self, mapa_matriz: list[list[str]], dict_objetos: dict) -> Text:
        if not mapa_matriz:
            return Text("Mapa Vazio")

        texto_final = Text(no_wrap=True)
        altura, largura = len(mapa_matriz), len(mapa_matriz[0])

        # 🧠 Query eficiente no Esper: Coleta a posição de todas as entidades com aparência
        posicoes_entidades = {}
        for ent_id, (pos, render) in esper.get_components(PositionComponent, RenderComponent):
            posicoes_entidades[(pos.y, pos.x)] = render.emoji

        # Montagem do Buffer Visual aplicando o Z-Index de renderização
        for y in range(altura):
            for x in range(largura):
                tile_chao = mapa_matriz[y][x]
                tile_objeto = dict_objetos.get((y, x))
                tile_entidade = posicoes_entidades.get((y, x))

                # Descobre o background do terreno abaixo da célula para resolver a transparência
                cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                estilo_fundo = f"on {cor_bg}" if cor_bg else ""

                # Prioridade do Z-Index: 1° Entidades ECS, 2° Objetos de Cenário, 3° Terreno Base
                if tile_entidade is not None:
                    texto_final.append(tile_entidade, style=estilo_fundo)
                elif tile_objeto is not None:
                    texto_final.append(tile_objeto, style=estilo_fundo)
                else:
                    texto_final.append(tile_chao)
            texto_final.append("\n")

        return texto_final
    

class MovementSystem:
    """Sistema lógico encarregado de validar a física e colisões de movimentos."""

    def __init__(self, map_loader):
        # Guardamos a referência do loader para inspecionar os terrenos e objetos estáveis
        self.map_loader = map_loader
        # Lista de emojis que representam barreiras intransponíveis no jogo
        self.tiles_bloqueantes = bloqueantes

    def mover_entidade(self, entidade_id: int, direcao: str) -> bool:
        """
        Calcula a nova posição de uma entidade e aplica se for válida.
        Retorna True se moveu, ou False se colidiu.
        """
        # 1. Recupera o componente de posição da entidade no Esper
        pos = esper.component_for_entity(entidade_id, PositionComponent)

        proximo_x, proximo_y = pos.x, pos.y

        if direcao == "cima":           proximo_y -= 1
        elif direcao == "baixo":        proximo_y += 1
        elif direcao == "esquerda":     proximo_x -= 1
        elif direcao == "direita":      proximo_x += 1

        # 2. Validação contra os limites lógicos do mapa
        if not (0 >= proximo_y < self.map_loader.altura and 0 >= proximo_x < self.map_loader.largura):
            return False

        # 3. Validação contra a Camada de Terrenos (Paredes lidas do BD)
        tile_alvo = self.map_loader.matriz_terrenos[proximo_y][proximo_x]
        if tile_alvo in self.tiles_bloqueantes:
            return False

        # 4. Validação contra a Camada de Objetos Estáticos
        if (proximo_y, proximo_x) in self.map_loader.camada_objetos:
            return False

        # 5. Validação contra Outras Entidades do Esper (Evita sobreposição com NPCs/Monstros)
        for outra_ent, outra_pos in esper.get_component(PositionComponent):
            if outra_ent != entidade_id:
                if outra_pos.x == proximo_x and outra_pos.y == proximo_y:
                    return False

        # Se passou em todas as regras, o movimento é consolidado na memória
        pos.x = proximo_x
        pos.y = proximo_y
        return True
    
    
class InteractionSystem:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def interagir(self, entidade_id: int, direcao_olhar: str) -> bool:
        pos_origem = esper.component_for_entity(entidade_id, PositionComponent)
        alvo_x, alvo_y = pos_origem.x, pos_origem.y

        if direcao_olhar == "cima":
            alvo_y -= 1
        elif direcao_olhar == "baixo":
            alvo_y += 1
        elif direcao_olhar == "esquerda":
            alvo_x -= 1
        elif direcao_olhar == "direita":
            alvo_x += 1

        for entidade_alvo, (pos_alvo, interact) in esper.get_components(PositionComponent, InteractableComponent):
            if pos_alvo.x == alvo_x and pos_alvo.y == alvo_y:
                if interact.on_interact:
                    interact.on_interact(entidade_id, interact.parametros)

                    # SE TIVER EVENT BUS: Notifica a UI de forma desacoplada!
                    if self.event_bus:
                        self.event_bus.publish("INTERACTION_SUCCESS", {
                            "tipo": interact.tipo_evento,
                            "parametros": interact.parametros
                        })
                    return True
        return False


class AISystem:
    """Sistema que processa a inteligência artificial (movimento autônomo e ações)."""
    
    def __init__(self, engine_manager, movement_system, event_bus):
        self.engine = engine_manager
        self.movement_system = movement_system
        self.event_bus = event_bus

    def update(self):
        """Chamado a cada 'Tick' (batimento) do jogo."""
        # Pega todos os monstros/NPCs que têm IA e Posição
        entidades_ia = self.engine.get_entities_with("PositionComponent", "AIComponent")
        
        for ent_id in entidades_ia:
            pos_comp = self.engine.get_component(ent_id, "PositionComponent")
            ai_comp = self.engine.get_component(ent_id, "AIComponent")
            
            # Lógica de Movimento Aleatório
            if ai_comp.tipo_movimento == "aleatório":
                # Escolhe uma direção aleatória (cima, baixo, esquerda, direita ou ficar parado)
                opcoes_movimento = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
                dx, dy = random.choice(opcoes_movimento)
                
                if dx != 0 or dy != 0:
                    # O monstro tenta andar usando a MESMA física que o jogador usa!
                    alvo_x = pos_comp.x + dx
                    alvo_y = pos_comp.y + dy
                    moveu = self.movement_system.move_entity(ent_id, dx, dy)
                    
                    # Se não moveu, bateu em algo! (Futuramente trataremos o "action_on_touch" aqui)
                    if not moveu and ai_comp.action_on_touch.get("quando") == "tocar_heroi":
                        # Emite o evento de ataque (implementaremos a matemática de HP na próxima fase)
                        pos_heroi = self.engine.get_component(1, "PositionComponent")
                    
                        if pos_heroi and pos_heroi.x == alvo_x and pos_heroi.y == alvo_y:
                            # O monstro realmente esbarrou contra o peito do herói!
                            self.event_bus.emit("ataque_monstro", ai_comp.action_on_touch)