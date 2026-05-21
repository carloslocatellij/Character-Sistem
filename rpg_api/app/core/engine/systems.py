from app.core.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES

class MovementSystem:
    """Sistema responsável por processar as regras de física e atualizar posições."""
    
    # ✅ NOVO: Adicionado dict_objetos (com valor padrão vazio para não quebrar os testes antigos)
    def __init__(self, ecs_manager, mapa_matriz: list[list[str]], tiles_bloqueio: list[str], dict_objetos: dict = None):
        self.ecs = ecs_manager
        self.mapa = mapa_matriz
        self.tiles_bloqueio = bloqueantes
        self.objetos = dict_objetos if dict_objetos is not None else {} # Guarda os objetos estáticos

    def move_entity(self, entity_id: int, dx: int, dy: int) -> bool:
        # ... (O código deste método mantém-se exatamente igual)
        pos_comp = self.ecs.get_component(entity_id, "Position")
        if not pos_comp:
            return False

        self._update_direction(pos_comp, dx, dy)
        novo_x = pos_comp.x + dx
        novo_y = pos_comp.y + dy

        if self._can_move_to(novo_x, novo_y):
            pos_comp.x = novo_x
            pos_comp.y = novo_y
            return True
            
        return False

    def _update_direction(self, pos_comp, dx: int, dy: int):
        # ... (Mantém-se igual)
        if dy == -1: pos_comp.direcao_olhar = "cima"
        elif dy == 1: pos_comp.direcao_olhar = "baixo"
        elif dx == -1: pos_comp.direcao_olhar = "esquerda"
        elif dx == 1: pos_comp.direcao_olhar = "direita"

    def _can_move_to(self, x: int, y: int) -> bool:
        # A) Limites do Mapa
        altura = len(self.mapa)
        if altura == 0: return False
        largura = len(self.mapa[0])
        
        if not (0 <= y < altura and 0 <= x < largura):
            return False

        # B) Colisão com a Matriz (Chão estático)
        tile_chao = self.mapa[y][x].strip()
        if tile_chao in self.tiles_bloqueio:
            return False

        # ✅ C) Colisão com Objetos de Cenário (Árvores, Cadeiras, etc)
        # O dicionário usa a tupla (linha, coluna) que corresponde a (y, x)
        if (y, x) in self.objetos:
            return False

        # D) Colisão com outras Entidades (NPCs, Baús)
        solid_entities = self.ecs.get_entities_with("Position", "Collision")
        
        for ent_id in solid_entities:
            ent_pos = self.ecs.get_component(ent_id, "Position")
            ent_col = self.ecs.get_component(ent_id, "Collision")
            
            if ent_col.is_solid and ent_pos.x == x and ent_pos.y == y:
                return False

        return True
    
# class MovementSystem:
#     """Sistema responsável por processar as regras de física e atualizar posições."""
    
#     def __init__(self, ecs_manager, mapa_matriz: list[list[str]], tiles_bloqueio: list[str]):
#         self.ecs = ecs_manager
#         self.mapa = mapa_matriz
#         self.tiles_bloqueio = tiles_bloqueio

#     def move_entity(self, entity_id: int, dx: int, dy: int) -> bool:
#         """
#         Tenta mover uma entidade.
#         Retorna True se o movimento foi concluído, False se colidiu.
#         """
#         pos_comp = self.ecs.get_component(entity_id, "Position")
#         if not pos_comp:
#             return False # Se não tem posição, não se pode mover!

#         # 1. Atualiza a direção do olhar IMEDIATAMENTE (crucial para interações futuras)
#         self._update_direction(pos_comp, dx, dy)

#         novo_x = pos_comp.x + dx
#         novo_y = pos_comp.y + dy

#         # 2. Física: Valida a passagem
#         if self._can_move_to(novo_x, novo_y):
#             pos_comp.x = novo_x
#             pos_comp.y = novo_y
#             return True
            
#         return False

#     def _update_direction(self, pos_comp, dx: int, dy: int):
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

#         # C) Colisão com outras Entidades (NPCs, Baús, Árvores)
#         # O sistema procura todas as entidades que têm posição e colisão
#         solid_entities = self.ecs.get_entities_with("Position", "Collision")
        
#         for ent_id in solid_entities:
#             ent_pos = self.ecs.get_component(ent_id, "Position")
#             ent_col = self.ecs.get_component(ent_id, "Collision")
            
#             # Se alguém sólido já está naquela coordenada (X, Y), bloqueia!
#             if ent_col.is_solid and ent_pos.x == x and ent_pos.y == y:
#                 return False

#         return True
    
# app/core/engine/systems.py

# Atualize a inicialização e o método interact no seu systems.py
class InteractionSystem:
    def __init__(self, ecs_manager, event_bus): # <- NOVO: Recebe o mensageiro
        self.ecs = ecs_manager
        self.event_bus = event_bus

    def interact(self, entity_id: int):
        pos_comp = self.ecs.get_component(entity_id, "Position")
        if not pos_comp: return

        target_x, target_y = pos_comp.x, pos_comp.y
        if pos_comp.direcao_olhar == "cima": target_y -= 1
        elif pos_comp.direcao_olhar == "baixo": target_y += 1
        elif pos_comp.direcao_olhar == "esquerda": target_x -= 1
        elif pos_comp.direcao_olhar == "direita": target_x += 1

        interactable_entities = self.ecs.get_entities_with("Position", "Interactable")
        
        for alvo_id in interactable_entities:
            alvo_pos = self.ecs.get_component(alvo_id, "Position")
            alvo_interact = self.ecs.get_component(alvo_id, "Interactable")
            
            if alvo_pos.x == target_x and alvo_pos.y == target_y and alvo_interact.is_active:
                
                # 🪄 A MÁGICA ACONTECE AQUI:
                # Em vez de um simples 'return', a Engine emite o evento para o universo!
                payload = {
                    "entity_id": alvo_id,
                    "parameters": alvo_interact.parameters
                }
                
                # Exemplo: emite("bau", {"entity_id": 2, "parameters": {"item": "Espada"}})
                self.event_bus.emit(alvo_interact.event_type, payload)
                return