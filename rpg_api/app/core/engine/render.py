# app/core/engine/render.py
from rich.text import Text
from app.core.emojis import CatalogoTiles # Reutiliza o catálogo de cores que criamos para o editor!

# app/core/engine/render.py
from rich.text import Text
from app.core.emojis import CatalogoTiles

class RenderSystem:
    def __init__(self, engine_manager):
        self.engine = engine_manager

    def renderizar_frame(self, mapa_matriz: list[list[str]], dict_objetos: dict) -> Text:
        if not mapa_matriz: return Text("Mapa Vazio")
            
        texto_final = Text(no_wrap=True)
        altura, largura = len(mapa_matriz), len(mapa_matriz[0])

        # 🧠 Varredura ECS: Agrupa posições de tudo o que tem geometria e aparência
        posicoes_entidades = {}
        entidades_visiveis = self.engine.get_entities_with("PositionComponent", "RenderComponent")
        
        for ent_id in entidades_visiveis:
            pos = self.engine.get_component(ent_id, "PositionComponent")
            render = self.engine.get_component(ent_id, "RenderComponent")
            posicoes_entidades[(pos.y, pos.x)] = render.emoji

        # Montagem do Buffer Visual (Z-Index)
        for y in range(altura):
            for x in range(largura):
                tile_chao = mapa_matriz[y][x]
                tile_objeto = dict_objetos.get((y, x))
                tile_entidade = posicoes_entidades.get((y, x))
                
                cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                estilo_fundo = f"on {cor_bg}" if cor_bg else ""

                if tile_entidade is not None:
                    texto_final.append(tile_entidade, style=estilo_fundo)
                elif tile_objeto is not None:
                    texto_final.append(tile_objeto, style=estilo_fundo)
                else:
                    texto_final.append(tile_chao)
            texto_final.append("\n")
            
        return texto_final
    
# class RenderSystem:
#     """Sistema responsável por compor as camadas visuais (Terreno, Cenário, Entidades)."""
    
#     def __init__(self, engine_manager, emoji_jogador: str = "🧙‍♂️"):
#         self.engine = engine_manager
#         self.emoji_jogador = emoji_jogador

#     def renderizar_frame(self, mapa_matriz: list[list[str]], dict_objetos: dict) -> Text:
#         """Monta o buffer de texto combinando Z-Index e cores de fundo."""
#         if not mapa_matriz:
#             return Text("Mapa Vazio")
            
#         texto_final = Text(no_wrap=True)
#         altura = len(mapa_matriz)
#         largura = len(mapa_matriz[0])

#         # 1. Mapeia onde estão as entidades dinâmicas (ex: Jogador, Monstros) na tela atualmente
#         # Para performance, criamos um mapa temporário de posições dinâmicas
#         posicoes_entidades = {}
        
#         # Procura todas as entidades com Posição
#         entidades_com_pos = self.engine.get_entities_with("Position")
#         for ent_id in entidades_com_pos:
#             pos_comp = self.engine.get_component(ent_id, "Position")
#             # Se for o ID 1 (Jogador), usamos o emoji do jogador, senão tentamos pegar o emoji do componente Interactable (NPC/Monstro)
#             if ent_id == 1:
#                 posicoes_entidades[(pos_comp.y, pos_comp.x)] = self.emoji_jogador
#             else:
#                 interact_comp = self.engine.get_component(ent_id, "Interactable")
#                 # Se for uma entidade interativa com representação visual (ex: Baú ou Monstro)
#                 if interact_comp and hasattr(interact_comp, 'emoji'):
#                     posicoes_entidades[(pos_comp.y, pos_comp.x)] = interact_comp.emoji
#                 else:
#                     # Fallback padrão caso não tenha emoji cadastrado no componente
#                     posicoes_entidades[(pos_comp.y, pos_comp.x)] = "👾"

#         # 2. Varre o Grid aplicando o Z-Index gráfico
#         for y in range(altura):
#             for x in range(largura):
#                 tile_chao = mapa_matriz[y][x]
#                 tile_objeto = dict_objetos.get((y, x))
#                 tile_entidade = posicoes_entidades.get((y, x))
                
#                 # Descobre o background do terreno abaixo da célula para resolver a transparência
#                 cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
#                 estilo_fundo = f"on {cor_bg}" if cor_bg else ""

#                 # Prioridade do Z-Index: 1° Entidades, 2° Objetos de Cenário, 3° Terreno Base
#                 if tile_entidade is not None:
#                     texto_final.append(tile_entidade, style=estilo_fundo)
#                 elif tile_objeto is not None:
#                     texto_final.append(tile_objeto, style=estilo_fundo)
#                 else:
#                     texto_final.append(tile_chao)
            
#             texto_final.append("\n")
            
#         return texto_final