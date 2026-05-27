from app.core.engine.manager import EngineManeger
from app.core.engine.components import (
    PositionComponent, CollisionComponent, InteractableComponent, 
    RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent)
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.controllers.game_controller import GameController 
from app.core.engine.components import AIComponent

def carregar_engine_do_banco(mapa_id: int, personagem_id: int, db_session) -> tuple[EngineManeger, list[list[str]], dict]:
    mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id).first()
    if not mapa_db:
        raise ValueError(f"Mapa {mapa_id} inexistente.")

    eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()
    
    controller = GameController(db_session)
    conversor = GameController.converter_para_dominio
    
    personagem_logico = controller.obter_personagem_por_id(personagem_id)
    personagem_logico = conversor(personagem_logico) if personagem_logico else None
    
    if not personagem_logico:
        raise ValueError(f"Personagem {personagem_id} não pôde ser instanciado pelo GameController.")

    engine = EngineManeger()

    # 3. INSTANCIAR O JOGADOR DEFINITIVO (ID 1)
    player_id = engine.create_entity()
    configs = mapa_db.configs if mapa_db.configs else {}
    pos_inicial = configs.get("pos_inicial", [22,14])
    
    engine.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
    engine.add_component(player_id, CollisionComponent(is_solid=True))
    engine.add_component(player_id, RenderComponent(emoji=personagem_logico.raca.emoji if personagem_logico.raca else "🙂"))
    
    # ATRIBUTOS REAIS CALCULADOS: Agora puxamos do objeto Personagem (core) e não do DB!
    engine.add_component(player_id, StatsComponent(
        nome=personagem_logico.nome,
        hp=personagem_logico.pv_atual,       # Propriedade calculada pelo seu arquivo personagens.py!
        max_hp=personagem_logico.pv_max,
        mp=personagem_logico.pm_atual,
        max_mp=personagem_logico.pm_max,
        ataque_base=personagem_logico.mod_atq_corpo or 0, # Verifique se é .ataque ou .calcular_ataque()
        defesa_base= 0
    ))
    
    # Inicializa o inventário base
    engine.add_component(player_id, InventoryComponent(itens={"poção": 2})) 
    engine.add_component(player_id, EquipmentComponent())

    # 2. INSTANCIAR OS EVENTOS COMO ENTIDADES (Monstros/Baús)
    for evt in eventos_db:
        entidade_id = engine.create_entity()
        engine.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
        engine.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
        
        is_solid = evt.parametros.get("atravessavel", True) if evt.parametros else True
        engine.add_component(entidade_id, CollisionComponent(is_solid=is_solid))
        
        parametros_evento = evt.parametros if evt.parametros else {}
        engine.add_component(entidade_id, InteractableComponent(
            event_type=evt.tipo_evento,
            parameters=parametros_evento
        ))

        if "mover" in parametros_evento:
            
            engine.add_component(entidade_id, AIComponent(
                movement_type=parametros_evento["mover"].get("direção", "aleatório"),
                action_on_touch=parametros_evento.get("ação", {})
            ))

    # Converte os objetos estáticos
    objetos_cenario = {}
    if mapa_db.objetos: # Trata se a coluna se chama 'objects' ou 'objetos'
        obj_dict = mapa_db.objetos if isinstance(mapa_db.objetos, dict) else {}
        for coord_str, emoji in obj_dict.items():
            try:
                y_str, x_str = coord_str.split(",")
                objetos_cenario[(int(y_str), int(x_str))] = emoji
            except ValueError: 
                print("Erro nos valores ao atribuir posição a objetos do mapa.")
                continue

    return engine, mapa_db.mapa_em_si, objetos_cenario