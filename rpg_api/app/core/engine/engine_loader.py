# app/core/engine/engine_loader.py
# app/core/engine/engine_loader.py
from app.core.engine.manager import ECSManager
from app.core.engine.components import (
    PositionComponent, CollisionComponent, InteractableComponent, 
    RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent
)
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.personagens_db import PersonagemDB # ✅ IMPORTADO DO SEU REPOSITÓRIO

def carregar_engine_do_banco(mapa_id: int, personagem_id: int, db_session) -> tuple[ECSManager, list[list[str]], dict]:
    mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id).first()
    if not mapa_db:
        raise ValueError(f"Mapa {mapa_id} inexistente.")

    eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()
    
    # ✅ NOVO: Puxa o Personagem real do Banco de Dados!
    pers_db = db_session.query(PersonagemDB).filter(PersonagemDB.id == personagem_id).first()
    if not pers_db:
        raise ValueError(f"Personagem {personagem_id} inexistente.")

    ecs = ECSManager()

    # 1. INSTANCIAR O JOGADOR DEFINITIVO (ID 1)
    player_id = ecs.create_entity()
    configs = mapa_db.configs if mapa_db.configs else {}
    pos_inicial = configs.get("pos_inicial", [1, 1])
    
    ecs.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
    ecs.add_component(player_id, CollisionComponent(is_solid=True))
    ecs.add_component(player_id, RenderComponent(emoji="🧙‍♂️"))
    
    # 🌟 ATRIBUTOS DO BANCO: Acoplamos os valores reais do ORM
    ecs.add_component(player_id, StatsComponent(
        nome=pers_db.nome,
        hp=pers_db.pv, # Usando pv e pm conforme o seu modelo do banco
        max_hp=pers_db.pv,
        mp=pers_db.pm,
        max_mp=pers_db.pm,
        ataque_base=pers_db.ataque,
        defesa_base=pers_db.defesa
    ))
    
    # Inicializa o inventário e os equipamentos vazios/padrão prontos para receber itens dos baús
    ecs.add_component(player_id, InventoryComponent(itens={"poção": 2})) 
    ecs.add_component(player_id, EquipmentComponent())

    # 2. INSTANCIAR OS EVENTOS COMO ENTIDADES (Monstros/Baús)
    for evt in eventos_db:
        entidade_id = ecs.create_entity()
        ecs.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
        ecs.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
        
        is_solid = evt.parametros.get("atravessavel", True) if evt.parametros else True
        ecs.add_component(entidade_id, CollisionComponent(is_solid=is_solid))
        
        parametros_evento = evt.parametros if evt.parametros else {}
        ecs.add_component(entidade_id, InteractableComponent(
            event_type=evt.tipo_evento,
            parameters=parametros_evento
        ))

        if "mover" in parametros_evento:
            from app.core.engine.components import AIComponent
            ecs.add_component(entidade_id, AIComponent(
                movement_type=parametros_evento["mover"].get("direção", "aleatório"),
                action_on_touch=parametros_evento.get("ação", {})
            ))

    # Converte os objetos estáticos
    objetos_cenario = {}
    if mapa_db.objects: # Trata se a coluna se chama 'objects' ou 'objetos'
        obj_dict = mapa_db.objects if isinstance(mapa_db.objects, dict) else {}
        for coord_str, emoji in obj_dict.items():
            try:
                y_str, x_str = coord_str.split(",")
                objetos_cenario[(int(y_str), int(x_str))] = emoji
            except ValueError: continue

    return ecs, mapa_db.mapa_em_si, objetos_cenario


# from app.core.engine.manager import ECSManager
# from app.core.engine.components import PositionComponent, CollisionComponent, InteractableComponent, RenderComponent, AIComponent
# from app.models.mapas_db import MapaDB
# from app.models.eventos_db import EventoDB

# def carregar_engine_do_banco(mapa_id: int, db_session) -> tuple[ECSManager, list[list[str]], dict]:
#     """
#     Consulta o banco de dados real, extrai a matriz do mapa, os objetos de cenário
#     e instancia todos os eventos dinâmicos como entidades lógicas no ECS.
#     """
#     # 1. Puxar dados autênticos do Banco de Dados
#     mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id).first()
#     if not mapa_db:
#         raise ValueError(f"Erro Crítico: Mapa com ID {mapa_id} não existe no banco de dados.")

#     eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()

#     # 2. Inicializar o nosso novo Gestor ECS
#     engine = ECSManager()

#     # 3. INSTANCIAR O JOGADOR (Sempre ID 1 para controle prático no motor)
#     player_id = engine.create_entity()
    
#     # Extrai a posição de início das configurações do mapa salvas no editor, ou usa (1,1) como padrão
#     configs = mapa_db.configs if mapa_db.configs else {}
#     pos_inicial = configs.get("pos_inicial", [46, 42])
    
#     engine.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
#     engine.add_component(player_id, CollisionComponent(is_solid=True))
#     engine.add_component(player_id, RenderComponent(emoji="🧙")) # Nosso herói em jogo

#     # 4. INSTANCIAR OS EVENTOS DO BANCO COMO ENTIDADES ECS
#     for evt in eventos_db:
#         entidade_id = engine.create_entity()
        
#         # Injeta as coordenadas reais onde ele foi colocado no editor de mapas
#         engine.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
        
#         # Registra a sua aparência visual baseada no emoji salvo
#         engine.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
        
#         # Configura as propriedades de colisão física baseadas nos parâmetros JSON
#         is_solid = evt.parametros.get("atravessavel", True) if evt.parametros else True
#         engine.add_component(entidade_id, CollisionComponent(is_solid=is_solid))
        
#         # Configura o gatilho lógico da tecla Enter (Mecânica Engine)
#         engine.add_component(entidade_id, InteractableComponent(
#             event_type=evt.tipo_evento,
#             parameters=evt.parametros if evt.parametros else {}
#         ))
        
#         if "mover" in evt.parametros:
#             engine.add_component(entidade_id, AIComponent(
#                 movement_type=evt.parametros["mover"].get("direção", "aleatório"),
#                 action_on_touch=evt.parametros.get("ação", {})
#             ))

#     # 5. Traduzir o dicionário de objetos estáticos do formato string ("y,x") para tuplas numéricas
#     objetos_cenario = {}
#     if mapa_db.objetos:
#         for coordenada_str, emoji in mapa_db.objetos.items():
#             try:
#                 y_str, x_str = coordenada_str.split(",")
#                 objetos_cenario[(int(y_str), int(x_str))] = emoji
#             except ValueError:
#                 continue

#     # Retorna o pacote completo pronto para rodar na GamePlayScreen
#     return engine, mapa_db.mapa_em_si, objetos_cenario