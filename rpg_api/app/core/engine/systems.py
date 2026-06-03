import esper
import random
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent, AIComponent
)
from app.core.entities.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES


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
        if not (0 <= proximo_y < self.map_loader.altura and 0 <= proximo_x < self.map_loader.largura):
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
                return True
        return False


class AISystem:
    def __init__(self, engine_manager, movement_system, event_bus):
        self.engine = engine_manager
        self.movement_system = movement_system
        self.event_bus = event_bus

    def update(self):
        """Processa movimento autônomo de monstros/NPCs a cada tick."""
        for ent_id, (pos_comp, ai_comp) in esper.get_components(PositionComponent, AIComponent):
            # Só processa monstros com movimento aleatório por enquanto
            if ai_comp.tipo_movimento != "aleatório":
                continue

            # Escolhe uma direção aleatória (4 direções + ficar parado)
            opcoes = ["cima", "baixo", "esquerda", "direita", None]
            direcao = random.choice(opcoes)

            if not direcao:
                continue  # 20% de chance de ficar parado

            # Tenta mover usando a mesma lógica de colisão do jogador
            moveu = self.movement_system.mover_entidade(ent_id, direcao)

            # Se colidiu com algo, verifica se foi o herói
            if not moveu:
                pos_heroi = esper.component_for_entity(1, PositionComponent)
                if pos_heroi:
                    # Calcula a posição alvo que tentou alcançar
                    deltas = {
                        "cima": (0, -1),
                        "baixo": (0, 1),
                        "esquerda": (-1, 0),
                        "direita": (1, 0)
                    }
                    dx, dy = deltas.get(direcao, (0, 0))
                    alvo_x = pos_comp.x + dx
                    alvo_y = pos_comp.y + dy

                    # Se a colisão foi com o herói, emite evento de ataque
                    if pos_heroi.x == alvo_x and pos_heroi.y == alvo_y:
                        if self.event_bus:
                            self.event_bus.publish("ataque_monstro", {
                                "parametros": ai_comp.action_on_touch
                            })
                            
                            
class InventarySystem():
    """ Gerencia estoques de baús e o inventário do personagem. 
    """
       


    def _get_inventory_mapping(self, inv):
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            return itens
        if isinstance(itens, list):
            mapped = {}
            for entry in itens:
                if isinstance(entry, dict):
                    nome = entry.get("nome") or entry.get("item") or entry.get("nome_item")
                    qtd = entry.get("quantidade", 1)
                else:
                    nome = str(entry)
                    qtd = 1
                if not nome:
                    continue
                mapped[nome] = mapped.get(nome, 0) + qtd
            return mapped
        return {}

    def _inventory_has_item(self, inv, nome):
        return self._get_inventory_mapping(inv).get(nome, 0) > 0

    def _inventory_remove_item(self, inv, nome, quantidade=1):
        if not inv:
            return False
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            atual = itens.get(nome, 0)
            if atual >= quantidade:
                itens[nome] = atual - quantidade
                if itens[nome] <= 0:
                    itens.pop(nome, None)
                return True
            return False
        if isinstance(itens, list):
            if any(isinstance(x, dict) for x in itens):
                for entry in itens:
                    if isinstance(entry, dict) and entry.get("nome") == nome:
                        qtd = entry.get("quantidade", 1)
                        if qtd > quantidade:
                            entry["quantidade"] = qtd - quantidade
                        else:
                            itens.remove(entry)
                        return True
                return False
            removed = 0
            while removed < quantidade and nome in itens:
                itens.remove(nome)
                removed += 1
            return removed == quantidade
        return False

    def _inventory_add_item(self, inv, nome, quantidade=1):
        if not inv:
            return False
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            itens[nome] = itens.get(nome, 0) + quantidade
            return True
        if isinstance(itens, list):
            if any(isinstance(x, dict) for x in itens):
                for entry in itens:
                    if isinstance(entry, dict) and entry.get("nome") == nome:
                        entry["quantidade"] = entry.get("quantidade", 1) + quantidade
                        return True
                itens.append({"nome": nome, "quantidade": quantidade})
                return True
            itens.extend([nome] * quantidade)
            return True
        return False