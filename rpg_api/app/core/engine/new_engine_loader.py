import esper
from typing import Any
from sqlalchemy.orm import Session
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.plataforma_db import SaveDB
from app.controllers.game_controller import GameController
from app.core.engine.new_components import (
    PositionComponent, RenderComponent,
    StatsComponent, EquipmentComponent, InventoryComponent,
    CollisionComponent, NetworkPlayerComponent
)
from app.core.engine.entity_factory import EntityFactory
import logging
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
                                slot_numero: int = 1, default_mapa_id: int = None,
                                game_state: Any = None) -> tuple[bool, list[list[str]], dict, int]:
        """
        Alterna ou inicializa o mundo do mapa alvo, sincronizando snapshots in RAM e persistência de SaveDB.
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

        if has_save and game_state is not None:
            dados = save_db.dados_sessao or {}
            game_state.switches = dados.get("switches", {})
            game_state.variables = dados.get("variables", {})

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
                    componentes_salvos = player_data.get("components", player_data)  # Retrocompatibilidade
                    pos_salva = componentes_salvos.get("PositionComponent", {
                        "x": 2, "y": 2, "direcao_olhar": "baixo"})
                    stats_salvo = componentes_salvos.get("StatsComponent", {})
                    inventario_salvo = componentes_salvos.get("InventoryComponent", {"itens": {}})
                    equipamento_salvo = componentes_salvos.get("EquipmentComponent", {
                        "arma": {}, "armadura": {}})

                    EntityFactory.criar_entidade_jogador_de_save(
                        entity_id=1,
                        pos_x=pos_salva["x"],
                        pos_y=pos_salva["y"],
                        direcao_olhar=pos_salva.get("direcao_olhar", "baixo"),
                        emoji="🧙",
                        stats_dict=stats_salvo,
                        inv_dict=inventario_salvo,
                        eqp_dict=equipamento_salvo,
                    )
            else:
                p_db = GameController.obter_personagem_por_id(db_session, usuario_id)

                if p_db:
                    p_logic = GameController.converter_para_dominio(p_db)
                    defesa_extra_calculada = 0
                    if hasattr(p_logic, "mao_esquerda") and p_logic.mao_esquerda:
                        defesa_extra_calculada = getattr(
                            p_logic.mao_esquerda.defesa, "defesa_extra", 0)

                    pos_inicial_str = mapa_db.configs.get(
                        "coordenadas_iniciais", "42,42") if mapa_db.configs else "42,42"
                    partes_pos_inicial = pos_inicial_str.split(",")
                    pos_x_inicial = int(partes_pos_inicial[1])
                    pos_y_inicial = int(partes_pos_inicial[0])

                    try:
                        EntityFactory.criar_entidade_jogador_novo(
                            entity_id=1,
                            pos_x=pos_x_inicial,
                            pos_y=pos_y_inicial,
                            personagem_dominio=p_logic,
                            defesa_extra_calculada=defesa_extra_calculada,
                        )
                    except KeyError:
                        esper.clear_database()
                        esper.create_entity()
                        EntityFactory.criar_entidade_jogador_novo(
                            entity_id=1,
                            pos_x=pos_x_inicial,
                            pos_y=pos_y_inicial,
                            personagem_dominio=p_logic,
                            defesa_extra_calculada=defesa_extra_calculada,
                        )

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

            # Dados persistidos no SaveDB para esta entidade (pode ser None)
            dados_salvos_do_evento = snapshot_entidades.get(str(id_virtual_do_banco)) or None

            # Delega toda a construção de componentes à EntityFactory
            EntityFactory.criar_entidade_evento(
                entity_id=entidade_ecs_id,
                event_type=evt.event_type,
                nome=evt.nome,
                emoji=evt.emoji,
                pos_x=evt.pos_x,
                pos_y=evt.pos_y,
                parametros_base=parametros_base,
                dados_salvos=dados_salvos_do_evento,
                game_state=game_state,
                world=esper,
            )

        return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

    def _salvar_snapshot_jogador(self):
        """Fotografa os componentes da entidade 1."""
        try:
            self.dados_salvaguarda_jogador = {
                "PositionComponent": esper.component_for_entity(1, PositionComponent),
                "StatsComponent": esper.component_for_entity(1, StatsComponent),
                "InventoryComponent": esper.component_for_entity(1, InventoryComponent),
                "EquipmentComponent": esper.component_for_entity(1, EquipmentComponent),
                "RenderComponent": esper.component_for_entity(1, RenderComponent),
                "CollisionComponent": esper.component_for_entity(1, CollisionComponent) if esper.has_component(1, CollisionComponent) else CollisionComponent(solido=True)
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

    # ==========================================
    # SUPORTE PARA MULTIPLAYER / REDE
    # ==========================================
    def obter_sistema_rede(self) -> any:
        """Busca o processador de rede (NetworkSystem) registrado no mundo ativo."""
        from app.core.engine.new_systems import NetworkSystem
        return esper.get_processor(NetworkSystem)

    def adicionar_jogador_rede(self, connection_id: str, username: str, x: int, y: int, emoji: str = "🧙") -> int:
        """Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem."""
        ns = self.obter_sistema_rede()
        if not ns:
            from app.core.engine.new_systems import NetworkSystem
            ns = NetworkSystem()
            esper.add_processor(ns)
        return ns.adicionar_jogador(connection_id, username, x, y, emoji)

    def remover_jogador_rede(self, connection_id: str):
        """Remove o jogador remoto do mundo atual usando o NetworkSystem."""
        ns = self.obter_sistema_rede()
        if ns:
            ns.remover_jogador(connection_id)

    def atualizar_jogador_rede(self, connection_id: str, x: int, y: int, direcao: str = "baixo"):
        """Atualiza a posição de um jogador remoto usando o NetworkSystem."""
        ns = self.obter_sistema_rede()
        if ns:
            ns.atualizar_jogador(connection_id, x, y, direcao)
