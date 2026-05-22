# app/core/engine/engine_loader.py
# app/core/engine/engine_loader.py
# app/core/engine/engine_loader.py
from app.core.engine.manager import ECSManager
from app.core.engine.components import (
    PositionComponent, CollisionComponent, InteractableComponent, 
    RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent
)
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB

# ✅ IMPORTAMOS O SEU CONTROLADOR QUE COORDENA OS CÁLCULOS
from app.controllers.game_controller import GameController 

def carregar_engine_do_banco(mapa_id: int, personagem_id: int, db_session) -> tuple[ECSManager, list[list[str]], dict]:
    mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id).first()
    if not mapa_db:
        raise ValueError(f"Mapa {mapa_id} inexistente.")

    eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()
    
    # 1. Instanciamos o seu Controlador passando a sessão do banco de dados
    controller = GameController(db_session)
    
    # 2. Pedimos ao controlador para montar o Personagem Lógico (da pasta core)
    # NOTA: Ajuste o nome do método ('obter_personagem' ou 'carregar_personagem') 
    # para o método real que você utiliza no seu GameController!
    personagem_logico = controller.obter_personagem_por_id(personagem_id) 
    personagem_logico.converter_para_dominio()
    
    if not personagem_logico:
        raise ValueError(f"Personagem {personagem_id} não pôde ser instanciado pelo GameController.")

    ecs = ECSManager()

    # 3. INSTANCIAR O JOGADOR DEFINITIVO (ID 1)
    player_id = ecs.create_entity()
    configs = mapa_db.configs if mapa_db.configs else {}
    pos_inicial = configs.get("pos_inicial", [1, 1])
    
    ecs.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
    ecs.add_component(player_id, CollisionComponent(is_solid=True))
    ecs.add_component(player_id, RenderComponent(emoji="🧙‍♂️"))
    
    # 🌟 ATRIBUTOS REAIS CALCULADOS: Agora puxamos do objeto Personagem (core) e não do DB!
    ecs.add_component(player_id, StatsComponent(
        nome=personagem_logico.nome,
        hp=personagem_logico.pv_max,       # Propriedade calculada pelo seu arquivo personagens.py!
        max_hp=personagem_logico.pv_max,
        mp=personagem_logico.pm_max,
        max_mp=personagem_logico.pm_max,
        ataque_base=personagem_logico.ataque, # Verifique se é .ataque ou .calcular_ataque()
        defesa_base=personagem_logico.defesa
    ))
    
    # Inicializa o inventário base
    ecs.add_component(player_id, InventoryComponent(itens={"poção": 2})) 
    ecs.add_component(player_id, EquipmentComponent())

    # ... (O resto do código mantém-se exatamente igual a partir daqui - instanciar monstros, eventos, etc.) ...

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