# app/core/engine/engine_loader.py

from app.core.engine.manager import EngineManeger
from app.core.engine.components import (
    PositionComponent, CollisionComponent, InteractableComponent, 
    RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent, AIComponent
)
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.plataforma_db import SaveDB
from app.controllers.game_controller import GameController

def carregar_engine_do_banco(
    db_session, 
    usuario_id: int, 
    cenario_id: int, 
    slot_numero: int = 1, 
    default_mapa_id: int = None
) -> tuple[EngineManeger, list[list[str]], dict, int]:
    """
    Carrega a infraestrutura do jogo interpretando o estado atual (Base + Delta).
    Isolado por Usuário, Cenário e Slot de Salvamento.
    
    Retorna: (engine_manager, mapa_em_si, objetos_cenario, mapa_atual_id)
    """
    engine = EngineManeger()

    # ==========================================
    # STEP 1: CONFERIR SE EXISTE JOGO SALVO (DELTA)
    # ==========================================
    save_db = db_session.query(SaveDB).filter(
        SaveDB.usuario_id == usuario_id,
        SaveDB.cenario_id == cenario_id,
        SaveDB.slot_numero == slot_numero
    ).first()

    has_save = save_db is not None
    dados_sessao = save_db.dados_sessao if has_save else {}

    # Define qual mapa carregar (O salvo ou o padrão do cenário)
    if has_save:
        mapa_id = dados_sessao.get("mapa_atual_id")
    else:
        # Se for um novo jogo e não passamos mapa padrão, pegamos o primeiro mapa cadastrado do cenário
        if default_mapa_id:
            mapa_id = default_mapa_id
        else:
            primeiro_mapa = db_session.query(MapaDB).filter(MapaDB.cenario_id == cenario_id).first()
            if not primeiro_mapa:
                raise ValueError(f"Erro: O Cenário {cenario_id} não possui nenhum mapa cadastrado no editor.")
            mapa_id = primeiro_mapa.id

    # ==========================================
    # STEP 2: CARREGAR OS DADOS BASE DO CENÁRIO (TEMPLATES)
    # ==========================================
    mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id, MapaDB.cenario_id == cenario_id).first()
    if not mapa_db:
        raise ValueError(f"Erro Crítico: Mapa {mapa_id} não pertence ao Cenário {cenario_id}.")

    eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()

    # ==========================================
    # STEP 3: RECONSTRUÇÃO DO JOGADOR (ID 1)
    # ==========================================
    player_id = 1 # Garantimos fixo na arquitetura do motor
    engine.entities[player_id] = {} # Força a criação da assinatura da entidade principal

    # Puxamos o orquestrador para calcular a vida matemática base do herói
    
    
    controller = GameController(db_session)
    conversor = GameController.converter_para_dominio
    
    # ISSO ESTÁ ERRADO MAS PARA FUNCIONAR POR ENQUANTO - ESTÁ PASSANDO O ID DO USUÁRIO PARA PEGAR O PERSONAGEM (Mesmo id só por agora)
    # TODO - AJUSTAR PARA PASSAR O ID DO PERSONAGEM SELECIONADO PELO USUÁRIO (Isso ainda necessita de uma forma de acontecer). 
    personagem_logico = controller.obter_personagem_por_id(usuario_id) # Vinculado ao ID do usuário jogador
    personagem_logico = conversor(personagem_logico) if personagem_logico else None

    if not personagem_logico:
        raise ValueError(f"Nenhum personagem ativo encontrado para o Usuário {usuario_id}.")

    if not has_save:
        # 🆕 NOVO JOGO: Posição inicial vem das configs do editor de mapas
        configs = mapa_db.configs if mapa_db.configs else {}
        pos_inicial = configs.get("pos_inicial", [1, 1])
        
        engine.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
        engine.add_component(player_id, StatsComponent(
            nome=personagem_logico.nome,
            hp=personagem_logico.pv,
            max_hp=personagem_logico.pv,
            mp=personagem_logico.pm,
            max_mp=personagem_logico.pm,
            ataque_base=personagem_logico.ataque,
            defesa_base=personagem_logico.defesa
        ))
        engine.add_component(player_id, InventoryComponent(itens={}))
        engine.add_component(player_id, EquipmentComponent())
    else:
        # 💾 CARREGAR JOGO (DELTA): Restaura exatamente o snapshot do arquivo de save
        save_player = dados_sessao["entidades"].get(str(player_id), {})
        
        engine.add_component(player_id, PositionComponent(
            x=save_player["pos_x"], 
            y=save_player["pos_y"], 
            direcao_olhar=save_player.get("direcao", "baixo")
        ))
        
        saved_stats = save_player.get("stats", {})
        engine.add_component(player_id, StatsComponent(
            nome=saved_stats.get("nome", personagem_logico.nome),
            hp=saved_stats.get("hp", personagem_logico.pv), # HP gasto pelo jogador na sessão anterior
            max_hp=saved_stats.get("max_hp", personagem_logico.pv),
            mp=saved_stats.get("mp", personagem_logico.pm),
            max_mp=saved_stats.get("max_mp", personagem_logico.pm),
            ataque_base=saved_stats.get("atk", personagem_logico.ataque),
            defesa_base=saved_stats.get("def", personagem_logico.defesa)
        ))
        engine.add_component(player_id, InventoryComponent(itens=save_player.get("inventario", {})))
        
        saved_eqp = save_player.get("equipamento", {})
        engine.add_component(player_id, EquipmentComponent(
            arma=saved_eqp.get("arma"),
            armadura=saved_eqp.get("armadura")
        ))

    engine.add_component(player_id, CollisionComponent(is_solid=True))
    engine.add_component(player_id, RenderComponent(emoji=save_player.get("render_emoji", "🧙‍♂️") if has_save else "🧙‍♂️"))

    # ==========================================
    # STEP 4: RECONSTRUÇÃO DOS EVENTOS (MONSTROS / BAÚS)
    # ==========================================
    # Usamos o ID do banco do evento como ID no ECS para um mapeamento Delta indestrutível!
    for evt in eventos_db:
        entidade_id = evt.id
        engine.entities[entidade_id] = {} # Cria assinatura lúdica

        parametros_base = evt.parametros if evt.parametros else {}
        
        # Se existe um save, conferimos se este monstro/baú tem dados guardados da sua última posição
        save_entidade = dados_sessao.get("entidades", {}).get(str(entidade_id)) if has_save else None

        if save_entidade:
            # 💾 DELTA: O monstro andou ou sofreu dano! Carrega o estado alterado do Save
            engine.add_component(entidade_id, PositionComponent(
                x=save_entidade["pos_x"], 
                y=save_entidade["pos_y"], 
                direcao_olhar=save_entidade.get("direcao", "baixo")
            ))
            engine.add_component(entidade_id, RenderComponent(emoji=save_entidade.get("render_emoji", evt.emoji)))
            
            is_active_atual = save_entidade.get("is_active", True)
            
            if "stats" in save_entidade:
                s_stats = save_entidade["stats"]
                engine.add_component(entidade_id, StatsComponent(
                    nome=s_stats["nome"], hp=s_stats["hp"], max_hp=s_stats["max_hp"],
                    mp=s_stats["mp"], max_mp=s_stats["max_mp"], 
                    ataque_base=s_stats["atk"], defesa_base=s_stats["def"]
                ))
        else:
            # 🆕 BASE: Sem modificações salvas para este evento. Carrega o padrão do editor
            engine.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
            engine.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
            is_active_atual = True
            
            # Se for um monstro com atributos base definidos no JSON de parâmetros
            if "ação" in parametros_base and "mudar_hp" in parametros_base["ação"]:
                val_dano = parametros_base["ação"]["mudar_hp"].get("valor", 2)
                engine.add_component(entidade_id, StatsComponent(
                    nome="Monstro", hp=10, max_hp=10, mp=0, max_mp=0, ataque_base=val_dano, defesa_base=2
                ))

        # Componentes de infraestrutura mecânica (mantêm a inteligência do JSON)
        is_solid = parametros_base.get("atravessavel", True)
        engine.add_component(entidade_id, CollisionComponent(is_solid=is_solid))
        engine.add_component(entidade_id, InteractableComponent(
            event_type=evt.tipo_evento,
            parameters=parametros_base,
            is_active=is_active_atual
        ))

        if "mover" in parametros_base:
            engine.add_component(entidade_id, AIComponent(
                movement_type=parametros_base["mover"].get("direção", "aleatório"),
                action_on_touch=parametros_base.get("ação", {})
            ))

    # ==========================================
    # STEP 5: OBJETOS ESTÁTICOS DO CENÁRIO
    # ==========================================
    objetos_cenario = {}
    if mapa_db.objects:
        obj_dict = mapa_db.objects if isinstance(mapa_db.objects, dict) else {}
        for coordenada_str, emoji in obj_dict.items():
            try:
                y_str, x_str = coordenada_str.split(",")
                objetos_cenario[(int(y_str), int(x_str))] = emoji
            except ValueError:
                continue

    return engine, mapa_db.mapa_em_si, objetos_cenario, mapa_id


# from app.core.engine.manager import EngineManeger
# from app.core.engine.components import (
#     PositionComponent, CollisionComponent, InteractableComponent, 
#     RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent)
# from app.models.mapas_db import MapaDB
# from app.models.eventos_db import EventoDB
# from app.controllers.game_controller import GameController 
# from app.core.engine.components import AIComponent

# def carregar_engine_do_banco(mapa_id: int, personagem_id: int, db_session) -> tuple[EngineManeger, list[list[str]], dict]:
#     mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id).first()
#     if not mapa_db:
#         raise ValueError(f"Mapa {mapa_id} inexistente.")

#     eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()
    
#     controller = GameController(db_session)
#     conversor = GameController.converter_para_dominio
    
#     personagem_logico = controller.obter_personagem_por_id(personagem_id)
#     personagem_logico = conversor(personagem_logico) if personagem_logico else None
    
#     if not personagem_logico:
#         raise ValueError(f"Personagem {personagem_id} não pôde ser instanciado pelo GameController.")

#     engine = EngineManeger()

#     # 3. INSTANCIAR O JOGADOR DEFINITIVO (ID 1)
#     player_id = engine.create_entity()
#     configs = mapa_db.configs if mapa_db.configs else {}
#     pos_inicial = configs.get("pos_inicial", [22,14])
    
#     engine.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
#     engine.add_component(player_id, CollisionComponent(is_solid=True))
#     engine.add_component(player_id, RenderComponent(emoji=personagem_logico.raca.emoji if personagem_logico.raca else "🙂"))
    
#     # ATRIBUTOS REAIS CALCULADOS: Agora puxamos do objeto Personagem (core) e não do DB!
#     engine.add_component(player_id, StatsComponent(
#         nome=personagem_logico.nome,
#         hp=personagem_logico.pv_atual,       # Propriedade calculada pelo seu arquivo personagens.py!
#         max_hp=personagem_logico.pv_max,
#         mp=personagem_logico.pm_atual,
#         max_mp=personagem_logico.pm_max,
#         ataque_base=personagem_logico.mod_atq_corpo or 0, # Verifique se é .ataque ou .calcular_ataque()
#         defesa_base= 0
#     ))
    
#     # Inicializa o inventário base
#     engine.add_component(player_id, InventoryComponent(itens={"poção": 2})) 
#     engine.add_component(player_id, EquipmentComponent())

#     # 2. INSTANCIAR OS EVENTOS COMO ENTIDADES (Monstros/Baús)
#     for evt in eventos_db:
#         entidade_id = engine.create_entity()
#         engine.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
#         engine.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
        
#         is_solid = evt.parametros.get("atravessavel", True) if evt.parametros else True
#         engine.add_component(entidade_id, CollisionComponent(is_solid=is_solid))
        
#         parametros_evento = evt.parametros if evt.parametros else {}
#         engine.add_component(entidade_id, InteractableComponent(
#             event_type=evt.tipo_evento,
#             parameters=parametros_evento
#         ))

#         if "mover" in parametros_evento:
            
#             engine.add_component(entidade_id, AIComponent(
#                 movement_type=parametros_evento["mover"].get("direção", "aleatório"),
#                 action_on_touch=parametros_evento.get("ação", {})
#             ))

#     # Converte os objetos estáticos
#     objetos_cenario = {}
#     if mapa_db.objetos: # Trata se a coluna se chama 'objects' ou 'objetos'
#         obj_dict = mapa_db.objetos if isinstance(mapa_db.objetos, dict) else {}
#         for coord_str, emoji in obj_dict.items():
#             try:
#                 y_str, x_str = coord_str.split(",")
#                 objetos_cenario[(int(y_str), int(x_str))] = emoji
#             except ValueError: 
#                 print("Erro nos valores ao atribuir posição a objetos do mapa.")
#                 continue

#     return engine, mapa_db.mapa_em_si, objetos_cenario