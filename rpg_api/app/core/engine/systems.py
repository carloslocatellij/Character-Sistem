import esper
from app.core.engine.components import PositionComponent, InteractableComponent
from app.core.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
import random


# rpg_api/app/core/engine/systems.py


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



# class MovementSystem:
#     """Sistema responsável por processar as regras de física e atualizar posições."""
    
#     # ✅ NOVO: Adicionado dict_objetos (com valor padrão vazio para não quebrar os testes antigos)
#     def __init__(self, engine_manager, mapa_matriz: list[list[str]], dict_objetos: dict = None):
#         self.engine = engine_manager
#         self.mapa = mapa_matriz
#         self.tiles_bloqueio = bloqueantes
#         self.objetos = dict_objetos if dict_objetos is not None else {} # Guarda os objetos estáticos

#     def move_entity(self, entity_id: int, dx: int, dy: int) -> bool:
#         # ... (O código deste método mantém-se exatamente igual)
#         pos_comp = self.engine.get_component(entity_id, "PositionComponent")
#         if not pos_comp:
#             return False

#         self._update_direction(pos_comp, dx, dy)
#         novo_x = pos_comp.x + dx
#         novo_y = pos_comp.y + dy

#         if self._can_move_to(novo_x, novo_y):
#             pos_comp.x = novo_x
#             pos_comp.y = novo_y
#             return True
            
#         return False

#     def _update_direction(self, pos_comp, dx: int, dy: int):
#         # ... (Mantém-se igual)
#         if dy == -1: pos_comp.direcao_olhar = "cima"
#         elif dy == 1: pos_comp.direcao_olhar = "baixo"
#         elif dx == -1: pos_comp.direcao_olhar = "esquerda"
#         elif dx == 1: pos_comp.direcao_olhar = "direita"

#     def _can_move_to(self, x: int, y: int) -> bool:
#         # A) Limites do Mapa
#         altura = len(self.mapa)
#         if altura == 0: return False
#         largura = len(self.mapa[0])
        
#         if not (0 <= y < altura and 0 <= x < largura):
#             return False

#         # B) Colisão com a Matriz (Chão estático)
#         tile_chao = self.mapa[y][x].strip()
#         if tile_chao in self.tiles_bloqueio:
#             return False

#         # ✅ C) Colisão com Objetos de Cenário (Árvores, Cadeiras, etc)
#         # O dicionário usa a tupla (linha, coluna) que corresponde a (y, x)
#         if (y, x) in self.objetos:
#             return False

#         # D) Colisão com outras Entidades (NPCs, Baús)
#         solid_entities = self.engine.get_entities_with("PositionComponent", "CollisionComponent")
        
#         for ent_id in solid_entities:
#             ent_pos = self.engine.get_component(ent_id, "PositionComponent")
#             ent_col = self.engine.get_component(ent_id, "CollisionComponent")
            
#             if ent_col.solido and ent_pos.x == x and ent_pos.y == y:
#                 return False

#         return True


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

# class InteractionSystem:
#     def __init__(self, engine_manager, event_bus): # <- NOVO: Recebe o mensageiro
#         self.engine = engine_manager
#         self.event_bus = event_bus

#     def interact(self, entity_id: int):
#         pos_comp = self.engine.get_component(entity_id, "PositionComponent")
#         if not pos_comp: return

#         target_x, target_y = pos_comp.x, pos_comp.y
#         if pos_comp.direcao_olhar == "cima": target_y -= 1
#         elif pos_comp.direcao_olhar == "baixo": target_y += 1
#         elif pos_comp.direcao_olhar == "esquerda": target_x -= 1
#         elif pos_comp.direcao_olhar == "direita": target_x += 1

#         interactable_entities = self.engine.get_entities_with("PositionComponent", "InteractableComponent")
        
#         for alvo_id in interactable_entities:
#             alvo_pos = self.engine.get_component(alvo_id, "PositionComponent")
#             alvo_interact = self.engine.get_component(alvo_id, "InteractableComponent")
            
#             if alvo_pos.x == target_x and alvo_pos.y == target_y and alvo_interact.is_active:
                
#                 # 🪄 A MÁGICA ACONTECE AQUI:
#                 # Em vez de um simples 'return', a Engine emite o evento para o universo!
#                 payload = {
#                     "entity_id": alvo_id,
#                     "parametros": alvo_interact.parametros
#                 }
                
#                 # Exemplo: emite("bau", {"entity_id": 2, "parametros": {"item": "Espada"}})
#                 self.event_bus.emit(alvo_interact.tipo_evento, payload)
#                 return
            

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