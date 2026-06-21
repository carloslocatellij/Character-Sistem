 # app/core/engine/engine_loader.py
 # app/core/engine/engine_loader.py
# import esper
# import logging
# from sqlalchemy.orm import Session

# from app.models.mapas_db import MapaDB
# from app.models.eventos_db import EventoDB
# from app.models.plataforma_db import SaveDB
# from app.controllers.game_controller import GameController
# from app.core.engine.components import (
#     PositionComponent, InteractableComponent, RenderComponent,
#     StatsComponent, AIComponent, EquipmentComponent, InventoryComponent
# )

# logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


# class GameEngineLoader:
#     """
#     Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos (esper.WorldContext).
#     Sincroniza snapshots em RAM, persistência de SaveDB e unifica o barramento de eventos do Esper.
#     """

#     def __init__(self):
#         self.mapa_id = None
#         self.nome_mapa = ""
#         self.matriz_terrenos = []
#         self.camada_objetos = {}
#         self.altura = 0
#         self.largura = 0

#         # Dicionários de persistência e transição de Cenas lógicas em RAM
#         self.mundos_carregados = {}          # { mapa_id: objeto_esper_WorldContext }
#         # Snapshot dos componentes nômades do Herói (ID 1)
#         self.dados_salvaguarda_jogador = {}

#         # Unificação mestre do barramento nativo do Esper
#         self.master_event_registry = getattr(esper, "event_registry", {})

#     def carregar_engine_do_banco(self, db_session: Session, usuario_id: int,
#                                 cenario_id: int, slot_numero: int = 1,
#                                 default_mapa_id: int = None) -> tuple[bool, list[list[str]], dict, int]:
#         """
#         Orquestrador central de mudança de cena. Resolve o mapa alvo, gerencia snapshots,
#         restaura da RAM ou constrói um novo ecossistema do zero de forma atômica.
#         """
#         # 1. Resolve o ID do mapa de destino com base no contexto (Save, Porta ou Padrão)
#         save_db = self._obter_dados_save(
#             db_session, usuario_id, cenario_id, slot_numero)
#         target_mapa_id = self._resolver_id_mapa_alvo(
#             db_session, save_db, cenario_id, default_mapa_id)

#         if not target_mapa_id:
#             logging.error(
#                 "Falha fatal: Nenhum mapa_id pôde ser resolvido para o carregamento.")
#             return False, [], {}, None

#         # 2. Fotografa e remove o jogador temporariamente do mapa atual para migração
#         if self.mapa_id is not None and self.mapa_id != target_mapa_id:
#             self._salvar_snapshot_jogador()

#         self.mapa_id = target_mapa_id

#         # 3. ROTA DE CARREGAMENTO A: O mapa já existe congelado na RAM
#         if target_mapa_id in self.mundos_carregados:
#             return self._restaurar_mundo_da_ram(db_session, target_mapa_id)

#         # 4. ROTA DE CARREGAMENTO B: O mapa é inédito. Inicializa um novo ecossistema
#         return self._inicializar_novo_mundo(db_session, save_db, usuario_id, target_mapa_id)

#     # =========================================================================
#     # SUB-MÉTODOS PRIVADOS DE SUPORTE (RESPONSABILIDADE ÚNICA - SRP)
#     # =========================================================================

#     def _obter_dados_save(self, db_session: Session, usuario_id: int, cenario_id: int, slot_numero: int) -> SaveDB:
#         """Busca os dados de persistência salvos no banco relacional."""
#         return db_session.query(SaveDB).filter(
#             SaveDB.usuario_id == usuario_id,
#             SaveDB.cenario_id == cenario_id,
#             SaveDB.slot_numero == slot_numero
#         ).first()

#     def _resolver_id_mapa_alvo(self, db_session: Session, save_db: SaveDB, cenario_id: int, default_mapa_id: int) -> int:
#         """Aplica a ordem de prioridades para descobrir qual mapa deve ser aberto."""
#         if default_mapa_id is not None:
#             return default_mapa_id
#         if save_db:
#             return save_db.dados_sessao.get("mapa_atual_id")

#         primeiro_mapa = db_session.query(MapaDB).filter(
#             MapaDB.cenario_id == cenario_id).first()
#         return primeiro_mapa.id if primeiro_mapa else None

#     def _sincronizar_dados_estaticos_mapa(self, mapa_db: MapaDB):
#         """Atualiza todas as variáveis estruturais e dimensões de leitura da TUI."""
#         self.matriz_terrenos = mapa_db.mapa_em_si
#         self.altura = len(self.matriz_terrenos)
#         self.largura = len(self.matriz_terrenos[0]) if self.altura > 0 else 0
#         self.nome_mapa = mapa_db.nome
#         self._processar_camada_objetos(mapa_db)

#     def _restaurar_mundo_da_ram(self, db_session: Session, target_mapa_id: int) -> tuple[bool, list[list[str]], dict, int]:
#         """Reativa o contexto do Esper congelado em memória sem corromper as entidades existentes."""
#         esper.switch_world(self.mundos_carregados[target_mapa_id])

#         if hasattr(esper, "event_registry"):
#             esper.event_registry = self.master_event_registry

#         self._restaurar_snapshot_jogador()

#         mapa_db = db_session.query(MapaDB).filter(
#             MapaDB.id == target_mapa_id).first()
#         if mapa_db:
#             self._sincronizar_dados_estaticos_mapa(mapa_db)

#         return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

#     def _inicializar_novo_mundo(self, db_session: Session, save_db: SaveDB, usuario_id: int, target_mapa_id: int) -> tuple[bool, list[list[str]], dict, int]:
#         """Orquestra a criação e o povoamento inicial de uma cena completamente inédita."""
#         #novo_mundo = esper.new_context()
#         novo_mundo = esper.switch_world(self.mapa_id)
#         self.mundos_carregados[target_mapa_id] = novo_mundo

#         if hasattr(esper, "event_registry"):
#             esper.event_registry = self.master_event_registry

#         mapa_db = db_session.query(MapaDB).filter(
#             MapaDB.id == target_mapa_id).first()
#         if not mapa_db:
#             return False, [], {}, None

#         self._sincronizar_dados_estaticos_mapa(mapa_db)

#         # Hidratação do Herói (ID 1 Fixo) e Eventos Locais (Monstros/Baús)
#         self._hidratar_jogador(db_session, save_db, usuario_id, mapa_db)
#         self._hidratar_eventos_cenario(db_session, save_db, target_mapa_id)

#         return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

#     def _hidratar_jogador(self, db_session: Session, save_db: SaveDB, usuario_id: int, mapa_db: MapaDB):
#         """Decide se o herói nasce de um snapshot nômade, de um SaveDB delta ou de um New Game."""
#         if self.dados_salvaguarda_jogador:
#             self._restaurar_snapshot_jogador()
#             return

#         try:
#             esper.components_for_entity(1)
#         except KeyError:
#             esper.create_entity()

#         if save_db:
#             self._hidratar_jogador_via_save(save_db)
#         else:
#             self._hidratar_jogador_via_dominio(db_session, usuario_id, mapa_db)

#     def _hidratar_jogador_via_save(self, save_db: SaveDB):
#         """Reconstrói o herói a partir do snapshot JSON contido no SaveDB."""
#         snapshot_entidades = save_db.dados_sessao.get("entidades", {})
#         player_data = snapshot_entidades.get("1", {})

#         if player_data:
#             pos_d = player_data.get("PositionComponent", {
#                                     "x": 42, "y": 42, "direcao_olhar": "baixo"})
#             stats_d = player_data.get("StatsComponent", {})
#             inv_d = player_data.get("InventoryComponent", {"itens": {}})
#             eqp_d = player_data.get("EquipmentComponent", {
#                                     "arma": {}, "armadura": {}})

#             esper.add_component(1, PositionComponent(
#                 x=pos_d["x"], y=pos_d["y"], direcao_olhar=pos_d["direcao_olhar"]))
#             esper.add_component(1, RenderComponent(emoji="🧙"))
#             esper.add_component(1, InventoryComponent(
#                 itens=inv_d.get("itens", {})))

#             comp_eqp = EquipmentComponent()
#             comp_eqp.arma = eqp_d.get("arma")
#             comp_eqp.armadura = eqp_d.get("armadura")
#             esper.add_component(1, comp_eqp)

#             if stats_d:
#                 esper.add_component(1, StatsComponent(
#                     nome=stats_d.get("nome", "Herói"),
#                     hp=stats_d.get("hp", 50),
#                     max_hp=stats_d.get("max_hp", 50),
#                     mp=stats_d.get("mp", 10),
#                     max_mp=stats_d.get("max_mp", 10),
#                     ataque_base=stats_d.get("ataque_base", 10),
#                     defesa_base=stats_d.get("defesa_base", 5)
#                 ))

#     def _hidratar_jogador_via_dominio(self, db_session: Session, usuario_id: int, mapa_db: MapaDB):
#         """Gera os atributos lógicos base calculados para o início de uma nova campanha."""
#         p_db = GameController.obter_personagem_por_id(db_session, usuario_id)
#         if p_db:
#             p_logic = GameController.converter_para_dominio(p_db)
#             defesa_extra = getattr(p_logic.mao_esquerda, "defesa_extra", 0) if hasattr(
#                 p_logic, "mao_esquerda") and p_logic.mao_esquerda else 0
#             pos_inicial = mapa_db.configs.get(
#                 "pos_inicial", [42, 42]) if mapa_db.configs else [42, 42]

#             esper.add_component(1, PositionComponent(
#                 x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
#             esper.add_component(1, RenderComponent(
#                 emoji=str(p_logic.raca if hasattr(p_logic, 'raca') else "🧙")))
#             esper.add_component(1, InventoryComponent(itens={}))
#             esper.add_component(1, EquipmentComponent())
#             esper.add_component(1, StatsComponent(
#                 nome=p_logic.nome,
#                 classe='mago',
#                 hp=int(p_logic.pv_atual),
#                 max_hp=int(p_logic.max_hp),
#                 mp=int(p_logic.pm_atual),
#                 max_mp=int(p_logic.max_mp),
#                 ataque_base=int(p_logic.mod_atq_corpo or 0),
#                 defesa_base=int(defesa_extra)
#             ))

#     def _hidratar_eventos_cenario(self, db_session: Session, save_db: SaveDB, target_mapa_id: int):
#         """Varre as tabelas ou o delta delta para injetar os monstros e baús do novo mapa."""
#         eventos_db = db_session.query(EventoDB).filter(
#             EventoDB.mapa_id == target_mapa_id).all()
#         snapshot_entidades = save_db.dados_sessao.get(
#             "entidades", {}) if save_db else {}

#         for evt in eventos_db:
#             entidade_ecs_id = esper.create_entity()
#             id_virtual_do_banco = evt.id + 10000

#             parametros_base = evt.parametros if evt.parametros else {}
#             parametros_base["id_virtual_evento"] = id_virtual_do_banco

#             evt_salvo = snapshot_entidades.get(str(id_virtual_do_banco), {})

#             if evt_salvo:
#                 self._construir_evento_via_save(
#                     entidade_ecs_id, evt, parametros_base, evt_salvo)
#             else:
#                 self._construir_evento_via_template(
#                     entidade_ecs_id, evt, parametros_base)

#     def _construir_evento_via_save(self, ecs_id: int, evt: EventoDB, params: dict, salvo: dict):
#         """Injeta componentes em um monstro/baú recuperando seu estado dinâmico do Save."""
#         pos_d = salvo.get("PositionComponent", {
#                           "x": evt.pos_x, "y": evt.pos_y})
#         interact_d = salvo.get("InteractableComponent")
#         stats_d = salvo.get("StatsComponent", {})

#         esper.add_component(ecs_id, PositionComponent(
#             x=pos_d["x"], y=pos_d["y"]))
#         esper.add_component(ecs_id, RenderComponent(emoji=evt.emoji))
#         esper.add_component(ecs_id, InteractableComponent(
#             event_type=evt.event_type, parametros=params,
#         ))

#         if stats_d:
#             esper.add_component(ecs_id, StatsComponent(
#                 nome=stats_d.get("nome", evt.nome), classe='', hp=stats_d.get("hp", 10), max_hp=stats_d.get("max_hp", 10),
#                 mp=stats_d.get("mp", 0), max_mp=stats_d.get("max_mp", 0), ataque_base=stats_d.get("ataque_base", 2), defesa_base=stats_d.get("defesa_base", 2)
#             ))
#         self._adicionar_ia_se_necessario(ecs_id, params)

#     def _construir_evento_via_template(self, ecs_id: int, evt: EventoDB, params: dict):
#         """Injeta componentes em um monstro/baú usando as definições estruturais brutas do banco."""
#         esper.add_component(
#             ecs_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
#         esper.add_component(ecs_id, RenderComponent(emoji=evt.emoji))
#         esper.add_component(ecs_id, InteractableComponent(
#             event_type=evt.event_type, parametros=params
#         ))

#         if evt.event_type == "monstro":
#             val_dano = params.get("ação", {}).get(
#                 "mudar_hp", {}).get("valor", 2)
#             esper.add_component(ecs_id, StatsComponent(
#                 nome=evt.nome, classe='', hp=10, max_hp=10, mp=0, max_mp=0, ataque_base=val_dano, defesa_base=2
#             ))
#         self._adicionar_ia_se_necessario(ecs_id, params)

#     def _adicionar_ia_se_necessario(self, ecs_id: int, params: dict):
#         """Anexa o componente de inteligência artificial se mapeado nas configurações do evento."""
#         if "mover" in params:
#             esper.add_component(ecs_id, AIComponent(
#                 movement_type=params["mover"].get("direção", "aleatório"),
#                 action_on_touch=params.get("ação", {})
#             ))

#     def _processar_camada_objetos(self, mapa_db: MapaDB):
#         """Traduz as chaves de string 'y,x' da tabela para tuplas lógicas inteiras (y, x)."""
#         objetos_convertidos = {}
#         if mapa_db and mapa_db.objetos:
#             obj_raw = mapa_db.objetos if isinstance(
#                 mapa_db.objetos, dict) else {}
#             for coord_str, emoji in obj_raw.items():
#                 try:
#                     y_str, x_str = coord_str.split(",")
#                     objetos_convertidos[(int(y_str), int(x_str))] = emoji
#                 except Exception:
#                     pass
#         self.camada_objetos = objetos_convertidos

#     def _salvar_snapshot_jogador(self):
#         """Registra as informações dinâmicas do herói antes da transição."""
#         try:
#             self.dados_salvaguarda_jogador = {
#                 "PositionComponent": esper.component_for_entity(1, PositionComponent),
#                 "StatsComponent": esper.component_for_entity(1, StatsComponent),
#                 "InventoryComponent": esper.component_for_entity(1, InventoryComponent),
#                 "EquipmentComponent": esper.component_for_entity(1, EquipmentComponent),
#                 "RenderComponent": esper.component_for_entity(1, RenderComponent)
#             }
#         except KeyError:
#             pass

#     def _restaurar_snapshot_jogador(self):
#         """Sincroniza o snapshot do herói no ID 1 do mundo ativo atual eliminando dados órfãos."""
#         try:
#             componentes_antigos = list(esper.components_for_entity(1))
#             for comp_instance in componentes_antigos:
#                 esper.remove_component(1, comp_instance.__class__)
#         except KeyError:
#             esper.create_entity()

#         for comp_instance in self.dados_salvaguarda_jogador.values():
#             if comp_instance:
#                 esper.add_component(1, comp_instance)




import esper
import logging
from sqlalchemy.orm import Session

from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.plataforma_db import SaveDB
from app.controllers.game_controller import GameController
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, AIComponent, EquipmentComponent, InventoryComponent
)

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

esper.list_worlds

class GameEngineLoader:
    """
    Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos (esper.WorldContext).
    Integra o carregamento atômico entre Estados Iniciais (Base) e Estados Salvos (Delta).
    """

    def __init__(self):
        self.mapa_id = None
        self.nome_mapa = ""
        self.matriz_terrenos = []
        self.camada_objetos = {}
        self.altura = 0
        self.largura = 0

        # Infraestrutura de Cenas Isoladas (Mundos Esper)
        self.mundos_carregados = {}          # { mapa_id: objeto_esper_WorldContext }
        # Snapshot temporário para travessia de mapas
        self.dados_salvaguarda_jogador = {}

        self.master_event_registry = getattr(esper, "event_registry", {})

    def carregar_engine_do_banco(self, db_session: Session, usuario_id: int, cenario_id: int, 
                                slot_numero: int = 1, default_mapa_id: int = None) -> tuple[bool, list[list[str]], dict, int]:
        """
        Alterna ou inicializa o mundo do mapa alvo, sincronizando snapshots em RAM e persistência de SaveDB.
        """
        # ==========================================
        # STEP 1: RESOLUÇÃO DO ID DO MAPA ALVO
        # ==========================================
        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot_numero
        ).first()

        has_save = save_db is not None

        if default_mapa_id is not None:
            target_mapa_id = default_mapa_id
        elif has_save:
            target_mapa_id = save_db.dados_sessao.get("mapa_atual_id")
        else:
            primeiro_mapa = db_session.query(MapaDB).filter(
                MapaDB.cenario_id == cenario_id).first()
            target_mapa_id = primeiro_mapa.id if primeiro_mapa else None

        if not target_mapa_id:
            logging.error(
                "Falha fatal: Nenhum mapa_id pôde ser resolvido para o carregamento.")
            return False, [], {}, None

        # ==========================================
        # STEP 2: SNAPSHOT DO JOGADOR (SE JÁ HOUVER UMA CENA ATIVA)
        # ==========================================
        if self.mapa_id is not None and self.mapa_id != target_mapa_id:
            self._salvar_snapshot_jogador()

        self.mapa_id = target_mapa_id

        # ==========================================
        # STEP 3: TRANSIÇÃO DE CONTEXTO (MUNDO JÁ EXISTE EM RAM)
        # ==========================================
        if target_mapa_id in self.mundos_carregados:
            # 🔄 Restaura o contexto do mundo antigo congelado
            esper.switch_world(self.mundos_carregados[target_mapa_id])
        
            if hasattr(esper, "event_registry"):
                esper.event_registry = self.master_event_registry

            # 🧙 Transita o snapshot do jogador para a Entidade 1 deste mundo reativado
            self._restaurar_snapshot_jogador()

            # 🗺️ Recarrega as informações estruturais necessárias para a GamePlayScreen renderizar
            mapa_db = db_session.query(MapaDB).filter(MapaDB.id == target_mapa_id).first()
            if mapa_db:
                self.matriz_terrenos = mapa_db.mapa_em_si
                self.altura = len(self.matriz_terrenos)
                self.largura = len(self.matriz_terrenos[0]) if self.altura > 0 else 0
                self.nome_mapa = mapa_db.nome
            
                # Traduz as chaves dos objetos estáticos para tuplas de inteiros
                self._processar_camada_objetos(mapa_db)

                self.master_event_registry = esper.event_registry
            # 🛑 PARADA ATÔMICA: Evita que o código continue descendo e recrie ou limpe os eventos da RAM!
            return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

        # ==========================================
        # STEP 4: INSTANCIAÇÃO DE UM MUNDO INÉDITO EM RAM
        # ==========================================
        # novo_mundo = esper.new_context()

        esper.switch_world(str(self.mapa_id))
        self.mundos_carregados[target_mapa_id] = str(self.mapa_id)

        # 🌟 ADICIONE ESTAS LINHAS: Força o novo mundo a aceitar as escutas da tela
        if hasattr(esper, "event_registry"):
            esper.event_registry = self.master_event_registry

        mapa_db = db_session.query(MapaDB).filter(
            MapaDB.id == target_mapa_id).first()
        if not mapa_db:
            return False, [], {}, None

        self.nome_mapa = mapa_db.nome
        self.matriz_terrenos = mapa_db.mapa_em_si
        self.altura = len(self.matriz_terrenos)
        self.largura = len(self.matriz_terrenos[0]) if self.altura > 0 else 0

        # 🌟 ESTA LINHA: Usa o conversor de string para tuplas inteiras (y, x)
        self._processar_camada_objetos(mapa_db)

        # ==========================================
        # STEP 5: REIDRATAÇÃO DA ENTIDADE JOGADOR (ID 1 FIXO)
        # ==========================================
        if self.dados_salvaguarda_jogador:
            self._restaurar_snapshot_jogador()
        else:
            # Primeiro mapa da sessão (New Game ou Carregando Save)
            # Garante que a fenda da Entidade 1 exista e esteja registrada neste mundo novo
            try:
                esper.components_for_entity(1)
            except KeyError:
                esper.create_entity()

            if has_save:
                snapshot_entidades = save_db.dados_sessao.get("entidades", {})
                player_data = snapshot_entidades.get("1", {})

                if player_data:
                    pos_d = player_data.get("PositionComponent", {
                                            "x": 2, "y": 2, "direcao_olhar": "baixo"})
                    stats_d = player_data.get("StatsComponent", {})
                    inv_d = player_data.get(
                        "InventoryComponent", {"itens": {}})
                    eqp_d = player_data.get("EquipmentComponent", {
                                            "arma": {}, "armadura": {}})

                    esper.add_component(1, PositionComponent(
                        x=pos_d["x"], y=pos_d["y"], direcao_olhar=pos_d["direcao_olhar"]))
                    esper.add_component(1, RenderComponent(emoji="🧙"))
                    esper.add_component(1, InventoryComponent(
                        itens=inv_d.get("itens", {})))

                    comp_eqp = EquipmentComponent()
                    comp_eqp.arma = eqp_d.get("arma")
                    comp_eqp.armadura = eqp_d.get("armadura")
                    esper.add_component(1, comp_eqp)

                    if stats_d:
                        esper.add_component(1, StatsComponent(
                            nome=stats_d.get("nome", "Herói"),
                            classe='mago',
                            hp=stats_d.get("hp", 50),
                            max_hp=stats_d.get("max_hp", 50),
                            mp=stats_d.get("mp", 10),
                            max_mp=stats_d.get("max_mp", 10),
                            ataque_base=stats_d.get("ataque_base", 10),
                            defesa_base=stats_d.get("defesa_base", 5)
                        ))
            else:
                p_db = GameController.obter_personagem_por_id(db_session, usuario_id)

                if p_db:
                    p_logic = GameController.converter_para_dominio(p_db)
                    defesa_extra_calculada = 0
                    if hasattr(p_logic, "mao_esquerda") and p_logic.mao_esquerda:
                        defesa_extra_calculada = getattr(
                            p_logic.mao_esquerda.defesa, "defesa_extra", 0)

                    pos_inicial = mapa_db.configs.get(
                        "pos_inicial", [42, 42]) if mapa_db.configs else [42, 42]

                    esper.add_component(1, PositionComponent(
                        x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
                    esper.add_component(1, RenderComponent(
                        emoji=str(p_logic.raca if hasattr(p_logic, 'raca') else "🧙")))
                    esper.add_component(1, InventoryComponent(itens={}))
                    esper.add_component(1, EquipmentComponent())
                    esper.add_component(1, StatsComponent(
                        nome=p_logic.nome,
                        classe='mago',
                        hp=int(p_logic.pv_atual),
                        max_hp=int(p_logic.max_hp),
                        mp=int(p_logic.pm_atual),
                        max_mp=int(p_logic.max_mp),
                        ataque_base=int(p_logic.mod_atq_corpo or 0),
                        defesa_base=int(defesa_extra_calculada)
                    ))

        # ==========================================
        # STEP 6: HIDRATAÇÃO DOS EVENTOS DO CENÁRIO
        # ==========================================
        eventos_db = db_session.query(EventoDB).filter(
            EventoDB.mapa_id == target_mapa_id).all()
        
        snapshot_entidades = save_db.dados_sessao.get(
            "entidades", {}) if has_save else {}

        for evt in eventos_db:
            entidade_ecs_id = esper.create_entity()
            id_virtual_do_banco = evt.id + 10000
            parametros_base = evt.parametros if evt.parametros else {}
            parametros_base["id_virtual_evento"] = id_virtual_do_banco

            evt_salvo = snapshot_entidades.get(str(id_virtual_do_banco), {})

            if evt_salvo:
                pos_d = evt_salvo.get("PositionComponent", {
                                    "x": evt.pos_x, "y": evt.pos_y})
                interact_d = evt_salvo.get(
                    "InteractableComponent", {"is_active": True})
                stats_d = evt_salvo.get("StatsComponent", {})

                esper.add_component(entidade_ecs_id, PositionComponent(
                    x=pos_d["x"], y=pos_d["y"]))
                esper.add_component(
                    entidade_ecs_id, RenderComponent(emoji=evt.emoji))
                esper.add_component(entidade_ecs_id, InteractableComponent(
                    event_type=evt.event_type,
                    parametros=parametros_base,
                ))

                if stats_d:
                    esper.add_component(entidade_ecs_id, StatsComponent(
                        nome=stats_d.get("nome", evt.nome),
                        classe='',
                        hp=stats_d.get("hp", 10),
                        max_hp=stats_d.get("max_hp", 10),
                        mp=stats_d.get("mp", 0),
                        max_mp=stats_d.get("max_mp", 0),
                        ataque_base=stats_d.get("ataque_base", 2),
                        defesa_base=stats_d.get("defesa_base", 2)
                    ))
            else:
                esper.add_component(
                    entidade_ecs_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
                esper.add_component(
                    entidade_ecs_id, RenderComponent(emoji=evt.emoji))
                esper.add_component(entidade_ecs_id, InteractableComponent(
                    event_type=evt.event_type,
                    parametros=parametros_base
                ))

                if evt.event_type == "monstro":
                    val_dano = parametros_base.get("ação", {}).get(
                        "mudar_hp", {}).get("valor", 2)
                    esper.add_component(entidade_ecs_id, StatsComponent(
                        nome=evt.nome, classe='', hp=10, max_hp=10, mp=0, max_mp=0, ataque_base=val_dano, defesa_base=2
                    ))

            if "mover" in parametros_base:
                esper.add_component(entidade_ecs_id, AIComponent(
                    movement_type=parametros_base["mover"].get(
                        "direção", "aleatório"),
                    action_on_touch=parametros_base.get("ação", {})
                ))

        return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

    def _salvar_snapshot_jogador(self):
        """Fotografa os componentes da entidade 1."""
        try:
            self.dados_salvaguarda_jogador = {
                "PositionComponent": esper.component_for_entity(1, PositionComponent),
                "StatsComponent": esper.component_for_entity(1, StatsComponent),
                "InventoryComponent": esper.component_for_entity(1, InventoryComponent),
                "EquipmentComponent": esper.component_for_entity(1, EquipmentComponent),
                "RenderComponent": esper.component_for_entity(1, RenderComponent)
            }
        except KeyError:
            pass

    def _restaurar_snapshot_jogador(self):
        """Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói de forma blindada."""
        try:
            # Se a entidade 1 já existe no mundo carregado, limpa componentes velhos para evitar lixo
            componentes_antigos = list(esper.components_for_entity(1))
            for comp_instance in componentes_antigos:
                esper.remove_component(1, comp_instance.__class__)
        except KeyError:
            # Se a entidade 1 ainda não existia neste contexto, inicializa o slot dela
            esper.create_entity()

        # Alimenta os componentes atualizados por cima da assinatura 1 fixada
        for comp_instance in self.dados_salvaguarda_jogador.values():
            if comp_instance:
                esper.add_component(1, comp_instance)
            
    def _processar_camada_objetos(self, mapa_db):
        """🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de inteiros (y, x)."""
        objetos_convertidos = {}
        if mapa_db and mapa_db.objetos:
            obj_raw = mapa_db.objetos if isinstance(
                mapa_db.objetos, dict) else {}
            for coord_str, emoji in obj_raw.items():
                try:
                    y_str, x_str = coord_str.split(",")
                    objetos_convertidos[(int(y_str), int(x_str))] = emoji
                except Exception:
                    pass
        self.camada_objetos = objetos_convertidos