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

class GameEngineLoader:
    """
    Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos (esper.new_context()).
    Integra o carregamento atômico entre Estados Iniciais (Base) e Estados Salvos (Delta).
    """

    def __init__(self):
        self.mapa_id = None
        self.nome_mapa = ""
        self.matriz_terrenos = []
        self.camada_objetos = {}
        self.altura = 0
        self.largura = 0

        # 🆕 INFRAESTRUTURA DE CENAS ISOLADAS (MUNDOS ESPER):
        self.mundos_carregados = {}          # { mapa_id: objeto_esper_World }
        # Snapshot dos componentes do Herói (ID 1)
        self.dados_salvaguarda_jogador = {}
        
    def carregar_player(db_session):
        db = db_session
        p_db = GameController.obter_personagem_por_id(db, 1)
        if p_db:
            try:
                p_logic = GameController.converter_para_dominio(p_db)
                defesa_base = None
                if p_logic.mao_esquerda:
                    defesa_base = p_logic.mao_esquerda.defesa_extra
                stats_comp = StatsComponent(
                    nome=p_logic.nome,
                    classe=p_logic.classe.nome,
                    pv=p_logic.pv_atual,
                    pv_max=p_logic.pv_max,
                    pm=p_logic.pm_atual,
                    pm_max=p_logic.pm_max,
                    ataque_base=p_logic.mod_atq_corpo or 0,
                    defesa_base=defesa_base or 0
                )
            except Exception as e_conv:
                logging.info(
                    f"erro ao converter para personagem lógico, usando fallback parcial do BD: {e_conv} - {p_db}")
                
                
                

    def carregar_engine_do_banco(self, db_session: Session, usuario_id: int, cenario_id: int, slot_numero: int = 1, default_mapa_id: int = None) -> tuple[bool, list[list[str]], dict, int]:
        """
        Alterna ou inicializa o mundo do mapa alvo, respeitando snapshots em RAM e persistência de SaveDB.
        Retorna uma tupla: (sucesso_bool, matriz_terrenos, camada_objetos, mapa_atual_id)
        """
        # ==========================================
        # STEP 1: RESOLUÇÃO DO MAPA ATUAL (BASE VS DELTA)
        # ==========================================
        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot_numero
        ).first()

        has_save = save_db is not None

        # Define qual mapa abrir
        if default_mapa_id is not None:
            target_mapa_id = default_mapa_id
        elif has_save:
            target_mapa_id = save_db.dados_sessao.get("mapa_atual_id")
        else:
            # Caso limite: Se não houver save nem ID default, busca o primeiro mapa do cenário
            primeiro_mapa = db_session.query(MapaDB).filter(
                MapaDB.cenario_id == cenario_id).first()
            target_mapa_id = primeiro_mapa.id if primeiro_mapa else None

        if not target_mapa_id:
            logging.error(
                "Falha fatal: Nenhum mapa_id pôde ser resolvido para o carregamento.")
            return False, [], {}, None

        # ==========================================
        # STEP 2: SALVAGUARDA DO JOGADOR NO MUNDO ANTERIOR
        # ==========================================
        if self.mapa_id is not None and self.mapa_id != target_mapa_id:
            self._salvar_snapshot_jogador()

        self.mapa_id = target_mapa_id

        # ==========================================
        # STEP 3: SELEÇÃO E TRANSIÇÃO DE MUNDO (RAM PRIORITÁRIA)
        # ==========================================
        if target_mapa_id in self.mundos_carregados:
            # O mundo já foi inicializado nesta sessão. Alterna o contexto e re-injeta o jogador
            esper.switch_world(self.mundos_carregados[target_mapa_id])
            self._restaurar_snapshot_jogador()

            # Recarrega dados estáticos da matriz local na memória do loader
            mapa_db = db_session.query(MapaDB).filter(
                MapaDB.id == target_mapa_id).first()
            if mapa_db:
                self.matriz_terrenos = mapa_db.mapa_em_si
                self.camada_objetos = mapa_db.objetos if mapa_db.objetos else {}
                self.altura = len(self.matriz_terrenos)
                self.largura = len(
                    self.matriz_terrenos[0]) if self.altura > 0 else 0
                self.nome_mapa = mapa_db.nome
            return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

        # Cria um mundo Esper isolado inédito para este mapa e assume o contexto
        novo_mundo = esper.current_world
        self.mundos_carregados[target_mapa_id] = novo_mundo
        esper.switch_world(novo_mundo)

        # Carrega dados do template estrutural do mapa
        mapa_db = db_session.query(MapaDB).filter(
            MapaDB.id == target_mapa_id).first()
        if not mapa_db:
            return False, [], {}, None

        self.nome_mapa = mapa_db.nome
        self.matriz_terrenos = mapa_db.mapa_em_si
        self.camada_objetos = mapa_db.objetos if mapa_db.objetos else {}
        self.altura = len(self.matriz_terrenos)
        self.largura = len(self.matriz_terrenos[0]) if self.altura > 0 else 0

        # ==========================================
        # STEP 4: REIDRATAÇÃO OU NASCIMENTO DO JOGADOR (ID 1)
        # ==========================================
        player_id = esper.create_entity()  # No mundo limpo recém-criado, garante o ID 1

        if self.dados_salvaguarda_jogador:
            # Se o jogador já existia cruzando portas em tempo de execução, restaura-o intacto
            self._restaurar_snapshot_jogador()

        elif has_save:
            # 💾 REIDRATAÇÃO VIA DELTA (SAVE): Resgata o snapshot JSON do banco de dados
            snapshot_entidades = save_db.dados_sessao.get("entidades", {})
            player_data = snapshot_entidades.get("1", {})

            if player_data:
                pos_d = player_data.get("PositionComponent", {
                                        "x": 2, "y": 2, "direcao_olhar": "baixo"})
                stats_d = player_data.get("StatsComponent", {})
                inv_d = player_data.get("InventoryComponent", {"itens": {}})
                eqp_d = player_data.get("EquipmentComponent", {
                                        "arma": {}, "armadura": {}})

                esper.add_component(player_id, PositionComponent(
                    x=pos_d["x"], y=pos_d["y"], direcao_olhar=pos_d["direcao_olhar"]))
                esper.add_component(player_id, RenderComponent(emoji="🧙"))
                esper.add_component(player_id, InventoryComponent(
                    itens=inv_d.get("itens", {})))

                # Reconstrói os equipamentos acoplados
                comp_eqp = EquipmentComponent()
                comp_eqp.arma = eqp_d.get("arma")
                comp_eqp.armadura = eqp_d.get("armadura")
                esper.add_component(player_id, comp_eqp)

                if stats_d:
                    esper.add_component(player_id, StatsComponent(
                        nome=stats_d.get("nome", "Herói"),
                        pv=stats_d.get("pv_atual", 50),
                        pv_max=stats_d.get("pv_max", 50),
                        pm=stats_d.get("pm_atual", 10),
                        pm_max=stats_d.get("pm_max", 10),
                        ataque_base=stats_d.get("ataque_base", 10),
                        defesa_base=stats_d.get("defesa_base", 5)
                    ))
        else:
            # 📜 REIDRATAÇÃO VIA TEMPLATE DOMÍNIO (NEW GAME): Primeiro carregamento da história
            #controller = GameController()
            #p_db = GameController.obter_personagem_por_id(db, 1)
            #personagem_logico = controller.obter_personagem(usuario_id=usuario_id)
            personagem_logico = GameController.obter_personagem_por_id(
                db_session, 1)
            personagem_logico = GameController.converter_para_dominio(
                personagem_logico)
            
            # Define coordenadas iniciais seguras extraídas das configurações do mapa
            pos_inicial = mapa_db.configs.get(
                "pos_inicial", [2, 2]) if mapa_db.configs else [2, 2]

            esper.add_component(player_id, PositionComponent(
                x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
            esper.add_component(player_id, RenderComponent(
                emoji=str(personagem_logico.raca)))
            esper.add_component(player_id, InventoryComponent(itens={}))
            esper.add_component(player_id, EquipmentComponent())
            if personagem_logico.armadura:
                defesa = personagem_logico.armadura.defesa
            else:
                defesa = 0
            esper.add_component(player_id, StatsComponent(
                nome=personagem_logico.nome,
                classe="mago",
                pv=int(personagem_logico.pv_atual),
                pv_max=int(personagem_logico.pv_max),
                pm=int(personagem_logico.pm_atual),
                pm_max=int(personagem_logico.pm_max),
                ataque_base=int(
                    personagem_logico.mod_atq_corpo),
                defesa_base=int(defesa or 0)
            ))


        # ==========================================
        # STEP 5: RECONSTRUÇÃO DOS EVENTOS DO MAPA (BASE VS DELTA)
        # ==========================================
        eventos_db = db_session.query(EventoDB).filter(
            EventoDB.mapa_id == target_mapa_id).all()
        snapshot_entidades = save_db.dados_sessao.get(
            "entidades", {}) if has_save else {}

        for evt in eventos_db:
            # 💡 TRUQUE DO OFFSET: Mantém IDs de cenário altos (banco_id + 10000)
            # para casar perfeitamente com o GameStateManager e evitar colisões com o ID 1
            entidade_id = evt.id + 10000
            esper.create_entity()  # Reserva e avança o ponteiro interno de assinaturas do Esper

            parametros_base = evt.parametros if evt.parametros else {}

            # Se houver delta salvo para este monstro/baú específico, extrai dele; senão usa o template original
            evt_salvo = snapshot_entidades.get(str(entidade_id), {})

            if evt_salvo:
                pos_d = evt_salvo.get("PositionComponent", {
                                      "x": evt.pos_x, "y": evt.pos_y})
                interact_d = evt_salvo.get(
                    "InteractableComponent", {"is_active": True})
                stats_d = evt_salvo.get("StatsComponent", {})

                esper.add_component(entidade_id, PositionComponent(
                    x=pos_d["x"], y=pos_d["y"]))
                esper.add_component(
                    entidade_id, RenderComponent(emoji=evt.emoji))
                esper.add_component(entidade_id, InteractableComponent(
                    event_type=evt.tipo_evento,
                    parameters=parametros_base,
                    is_active=interact_d.get("is_active", True)
                ))

                if stats_d:
                    esper.add_component(entidade_id, StatsComponent(
                        nome=stats_d.get("nome", evt.nome),
                        pv=stats_d.get("pv_atual", 10),
                        pv_max=stats_d.get("pv_max", 10),
                        pm=stats_d.get("pm_atual", 0),
                        pm_max=stats_d.get("pm_max", 0),
                        ataque_base=stats_d.get("ataque_base", 2),
                        defesa_base=stats_d.get("defesa_base", 2)
                    ))
            else:
                # Inicialização padrão pura (Template do Banco)
                esper.add_component(
                    entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
                esper.add_component(
                    entidade_id, RenderComponent(emoji=evt.emoji))
                esper.add_component(entidade_id, InteractableComponent(
                    event_type=evt.tipo_evento,
                    parameters=parametros_base,
                    is_active=True
                ))

                if evt.tipo_evento == "monstro":
                    val_dano = parametros_base.get("ação", {}).get(
                        "mudar_pv", {}).get("valor", 2)
                    esper.add_component(entidade_id, StatsComponent(
                        nome=evt.nome, pv=10, pv_max=10, pm=0, pm_max=0, ataque_base=val_dano, defense_base=2
                    ))

            # Injeta IA se mapeado no JSON de comportamento
            if "mover" in parametros_base:
                esper.add_component(entidade_id, AIComponent(
                    movement_type=parametros_base["mover"].get(
                        "direção", "aleatório"),
                    action_on_touch=parametros_base.get("ação", {})
                ))

        return True, self.matriz_terrenos, self.camada_objetos, self.mapa_id

    def _salvar_snapshot_jogador(self):
        """Fotografa os componentes da entidade 1 e os remove do mundo antes da troca de mapa."""
        try:
            self.dados_salvaguarda_jogador = {
                "PositionComponent": esper.component_for_entity(1, PositionComponent),
                "StatsComponent": esper.component_for_entity(1, StatsComponent),
                "InventoryComponent": esper.component_for_entity(1, InventoryComponent),
                "EquipmentComponent": esper.component_for_entity(1, EquipmentComponent),
                "RenderComponent": esper.component_for_entity(1, RenderComponent)
            }
            # Remove o herói do mundo atual para que ele não fique "duplicado" congelado na cena velha
            esper.delete_entity(1)
        except KeyError:
            pass

    def _restaurar_snapshot_jogador(self):
        """Injeta as instâncias salvas de volta na assinatura de entidade 1 no mundo ativo."""
        # Força o Esper a criar/reservar a assinatura primária 1 no início do laço do novo mundo
        player_id = esper.create_entity()

        for comp_instance in self.dados_salvaguarda_jogador.values():
            if comp_instance:
                esper.add_component(player_id, comp_instance)



# class GameEngineLoader:
#     """
#     Gerencia carregamento, componentização e tradução de dados para entidades.
#     Args:
#         envent_bus = EventBus()
#         mapa_id = None
#         nome_mapa = ""
#         matriz_terrenos = []
#         camada_objetos = {}
#         altura = 0
#         largura = 0
#     Methods:
#         carregar_engine_do_banco(Session, mapa_id) -> bool
#     """
    
#     def __init__(self):
#         #self.event_bus = EventBus()
#         self.mapa_id = None
#         self.nome_mapa = ""
#         self.matriz_terrenos = []
#         self.camada_objetos = {}
#         self.altura = 0
#         self.largura = 0

#     def carregar_engine_do_banco(self, db: Session, mapa_id: int) -> bool:
#         """
#         Método assinado pela GamePlayScreen.
#         Limpa o contexto antigo do Esper, lê a BD e monta o novo estado em memória.
#         """
#         # 1. RESET CRUCIAL: Limpa todas as entidades antigas do mundo global do Esper
        
#         #esper.switch_world(esper.list_worlds()[0])
        
#         esper.clear_database()

#         mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id).first()
#         if not mapa_db:
#             return False

#         self.mapa_id = mapa_id
#         self.nome_mapa = mapa_db.nome
#         self.matriz_terrenos = mapa_db.mapa_em_si
#         self.altura = len(self.matriz_terrenos)
#         self.largura = len(self.matriz_terrenos[0]) if self.altura > 0 else 0

#         objetos_json = mapa_db.objetos or getattr(mapa_db, 'objetos', {}) or {}
#         self.camada_objetos = {}
#         for k, v in objetos_json.items():
#             try:
#                 partes = k.split(',')
#                 self.camada_objetos[(int(partes[0]), int(partes[1]))] = v
#             except Exception:
#                 continue

#         # 1. CARREGAR OS DADOS DO JOGADOR PRINCIPAL (ID 1) DO BANCO DE DADOS
        
#         stats_comp = StatsComponent(
#             nome="Charles",
#             classe="Mago",
#             pv=15,
#             pv_max=15,
#             pm=50,
#             pm_max=50,
#             ataque_base=15,
#             defesa_base=10
#         )

#         #controller = GameController()
#         try:
        #     # db.query(PersonagemDB).filter(PersonagemDB.id == 1).first()
        #     p_db = GameController.obter_personagem_por_id(db, 1)
        #     if p_db:
        #         # ⚔️ Tenta converter usando o GameController tradutor
        #         try:
        #             p_logic = GameController.converter_para_dominio(p_db)
        #             defesa_base = None
        #             if p_logic.mao_esquerda:
        #                 defesa_base = p_logic.mao_esquerda.defesa_extra
        #             stats_comp = StatsComponent(
        #                 nome=p_logic.nome,
        #                 classe=p_logic.classe.nome,
        #                 pv=p_logic.pv_atual,
        #                 pv_max=p_logic.pv_max,
        #                 pm=p_logic.pm_atual,
        #                 pm_max=p_logic.pm_max,
        #                 ataque_base=p_logic.mod_atq_corpo or 0,
        #                 defesa_base=defesa_base or 0
        #             )
        #         except Exception as e_conv:
        #             logging.info(
        #                 f"erro ao converter para personagem lógico, usando fallback parcial do BD: {e_conv} - {p_db}")
        #             # Caso a conversão falhe por falta de raça/classe populada no mock, usa os dados crus do BD
        #             stats_comp = StatsComponent(
        #                 nome=getattr(p_db, 'nome', "Charles"),
        #                 classe="Mago",
        #                 pv=getattr(p_db, 'pv', 100),
        #                 pv_max=getattr(p_db, 'pv_max', 100),
        #                 pm=getattr(p_db, 'mp', 50),
        #                 pm_max=getattr(p_db, 'pm_max', 50),
        #                 ataque_base=getattr(p_db, 'ataque', 15),
        #                 defesa_base=getattr(p_db, 'defesa', 10)
        #             )
        # except Exception as e_bd:
        #     logging.info(f"erro ao acessar ou alimentar comp status: {e_bd}")

#         # Tenta obter posição inicial das configs do mapa ou usa fallback seguro
#         configs = getattr(mapa_db, 'configs', {}) or {}
#         pos_inicial = configs.get("pos_inicial", [45, 45])
#         px, py = pos_inicial[0], pos_inicial[1]

#         # Itens iniciais para garantir o funcionamento dos comandos do Chat (/inventario, /equipar)
#         itens_iniciais = [
#             {"id": 101, "nome": "poção",
#                 "tipo": "consumivel", "bonus": 50},
#             {"id": 201, "nome": "espada longa", "tipo": "arma", "bonus_atk": 8},
#             {"id": 301, "nome": "armadura de couro",
#                 "tipo": "armadura", "bonus_def": 4}
#         ]

#         # Cria rigidamente a entidade do jogador (ID 1) no Esper com todos os componentes acoplados
#         esper.create_entity(
#             PositionComponent(x=px, y=py),
#             RenderComponent(emoji=p_db.raca.emoji or "🦀"),
#             PlayerControlComponent(),
#             stats_comp,
#             InventoryComponent(itens=itens_iniciais),
#             EquipmentComponent()
#         )


#         # 2. Carrega o resto das entidades do mapa (Monstros/Baús)
#         eventos_bd = getattr(mapa_db, 'eventos', [])
#         for evento_db in eventos_bd:
#             entidade = esper.create_entity()
#             esper.add_component(entidade, PositionComponent(
#                 x=evento_db.pos_x, y=evento_db.pos_y))
#             esper.add_component(
#                 entidade, RenderComponent(emoji=evento_db.emoji))

#             # Interpreta os parâmetros para determinar se é um monstro com IA
#             parametros = evento_db.parametros or {}
#             if "mover" in parametros:
#                 direcao = parametros["mover"].get("direção", "aleatório")
#                 esper.add_component(entidade, AIComponent(
#                     tipo_movimento=direcao,
#                     action_on_touch={
#                         "quando": "tocar_heroi",
#                         "tipo": "ataque",
#                         "dano": parametros.get("ataque", {}).get("dano", 1)
#                     }
#                 ))

#             # Todos os eventos continuam com InteractableComponent para triggers adicionais
#             esper.add_component(entidade, InteractableComponent(
#                 tipo_evento=evento_db.tipo_evento, parametros=parametros
#             ))

#         return True




# from app.core.engine.manager import EngineManager
# from app.core.engine.components import (
#     PositionComponent, CollisionComponent, InteractableComponent, 
#     RenderComponent, StatsComponent, InventoryComponent, EquipmentComponent, AIComponent
# )
# from app.models.mapas_db import MapaDB
# from app.models.eventos_db import EventoDB
# from app.models.plataforma_db import SaveDB
# from app.controllers.game_controller import GameController



# def carregar_engine_do_banco(
#     db_session, 
    # usuario_id: int, 
    # cenario_id: int, 
    # slot_numero: int = 1, 
#     default_mapa_id: int = None
# ) -> tuple[EngineManager, list[list[str]], dict, int]:
#     """
#     Carrega a infraestrutura do jogo interpretando o estado atual (Base + Delta).
#     Isolado por Usuário, Cenário e Slot de Salvamento.
    
#     Retorna: (engine_manager, mapa_em_si, objetos_cenario, mapa_atual_id)
#     """
#     engine = EngineManager()

#     # ==========================================
#     # STEP 1: CONFERIR SE EXISTE JOGO SALVO (DELTA)
#     # ==========================================
#     save_db = db_session.query(SaveDB).filter(
#         SaveDB.usuario_id == usuario_id,
#         SaveDB.cenario_id == cenario_id,
#         SaveDB.slot_numero == slot_numero
#     ).first()

#     has_save = save_db is not None
#     dados_sessao = save_db.dados_sessao if has_save else {}

#     # Define qual mapa carregar (O salvo ou o padrão do cenário)
#     if has_save:
#         mapa_id = dados_sessao.get("mapa_atual_id")
#     else:
#         # Se for um novo jogo e não passamos mapa padrão, pegamos o primeiro mapa cadastrado do cenário
#         if default_mapa_id:
#             mapa_id = default_mapa_id
#         else:
#             primeiro_mapa = db_session.query(MapaDB).filter(MapaDB.cenario_id == cenario_id).first()
#             if not primeiro_mapa:
#                 raise ValueError(f"Erro: O Cenário {cenario_id} não possui nenhum mapa cadastrado no editor.")
#             mapa_id = primeiro_mapa.id

#     # ==========================================
#     # STEP 2: CARREGAR OS DADOS BASE DO CENÁRIO (TEMPLATES)
#     # ==========================================
#     mapa_db = db_session.query(MapaDB).filter(MapaDB.id == mapa_id, MapaDB.cenario_id == cenario_id).first()
#     if not mapa_db:
#         raise ValueError(f"Erro Crítico: Mapa {mapa_id} não pertence ao Cenário {cenario_id}.")

#     eventos_db = db_session.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()

#     # ==========================================
#     # STEP 3: RECONSTRUÇÃO DO JOGADOR (ID 1)
#     # ==========================================
#     # ISSO ESTÁ ERRADO MAS PARA FUNCIONAR POR ENQUANTO - ESTÁ PASSANDO O ID DO USUÁRIO PARA PEGAR O PERSONAGEM (Mesmo id só por agora)
#     # TODO - AJUSTAR PARA PASSAR O ID DO PERSONAGEM SELECIONADO PELO USUÁRIO (Isso ainda necessita de uma forma de acontecer).
#     player_id = 1 # Garantimos fixo na arquitetura do motor
#     engine.entities[player_id] = {} # Força a criação da assinatura da entidade principal

#     # Puxamos o orquestrador para calcular a vida matemática base do herói
    
    
#     controller = GameController(db_session)
#     conversor = GameController.converter_para_dominio 
     
#     personagem_logico = controller.obter_personagem_por_id(player_id) # Vinculado ao ID do usuário jogador
#     personagem_logico = conversor(personagem_logico) if personagem_logico else None

#     if not personagem_logico:
#         raise ValueError(f"Nenhum personagem ativo encontrado para o Usuário {usuario_id}.")

#     if not has_save:
#         # 🆕 NOVO JOGO: Posição inicial vem das configs do editor de mapas
#         configs = mapa_db.configs if mapa_db.configs else {}
#         pos_inicial = configs.get("pos_inicial", [40, 40])
        
#         engine.add_component(player_id, PositionComponent(x=pos_inicial[0], y=pos_inicial[1], direcao_olhar="baixo"))
        
#         engine.add_component(player_id, StatsComponent(
#                 nome=personagem_logico.nome,    
#                 pv=personagem_logico.pv_atual,
#                 pv_max=personagem_logico.pv_max,
#                 pm=personagem_logico.pm_atual,
#                 pm_max=personagem_logico.pm_max,
#                 ataque_base=int(personagem_logico.mod_atq_corpo), # Garante tipo numérico inteiro
#                 #defesa_base= int(personagem_logico.armadura.defesa) if hasattr(personagem_logico, 'armadura') else 0
#                 defesa_base= 0
                
#         ))
        
#         engine.add_component(player_id, InventoryComponent(itens={'espada longa': 1}))
#         engine.add_component(player_id, EquipmentComponent())
        
#     else:
#         # 💾 CARREGAR JOGO (DELTA): Restaura exatamente o snapshot do arquivo de save
#         save_player = dados_sessao["entidades"].get(str(player_id), {})
        
#         engine.add_component(player_id, PositionComponent(
#             x=save_player["pos_x"], 
#             y=save_player["pos_y"], 
#             direcao_olhar=save_player.get("direcao", "baixo")
#         ))
        
#         saved_stats = save_player.get("stats", {})
        
#         engine.add_component(player_id, StatsComponent(
#             nome=saved_stats.get("nome", personagem_logico.nome),
#             pv=saved_stats.get("pv_atual", personagem_logico.pv_atual),
#             pv_max=saved_stats.get("pv_max", personagem_logico.pv_max),
#             pm=saved_stats.get("pm_atual", personagem_logico.pm_atual),
#             pm_max=saved_stats.get("pm_max", personagem_logico.pm_max),
#             ataque_base=saved_stats.get("ataque_base", int(personagem_logico.ataque)),
#             defesa_base=saved_stats.get("defesa_base", int(personagem_logico.defesa))
#         ))
        
#         engine.add_component(player_id, InventoryComponent(itens=save_player.get("inventario", {})))
        
#         saved_eqp = save_player.get("equipamento", {})
#         engine.add_component(player_id, EquipmentComponent(
#             arma=saved_eqp.get("arma"),
#             armadura=saved_eqp.get("armadura")
#         ))

#     engine.add_component(player_id, CollisionComponent(solido=True))
#     engine.add_component(player_id, RenderComponent(emoji=save_player.get("render_emoji", "🧙‍♂️") if has_save else "🧙‍♂️"))

#     # ==========================================
#     # STEP 4: RECONSTRUÇÃO DOS EVENTOS (MONSTROS / BAÚS)
#     # ==========================================
#     # Usamos o ID do banco do evento como ID no ECS para um mapeamento Delta indestrutível!
#     for evt in eventos_db:
#         entidade_id = evt.id + 100000
#         engine.entities[entidade_id] = {} # Cria assinatura lúdica

#         parametros_base = evt.parametros if evt.parametros else {}
        
#         # Se existe um save, conferimos se este monstro/baú tem dados guardados da sua última posição
#         save_entidade = dados_sessao.get("entidades", {}).get(str(entidade_id)) if has_save else None

#         if save_entidade:
#             # 💾 DELTA: O monstro andou ou sofreu dano! Carrega o estado alterado do Save
#             engine.add_component(entidade_id, PositionComponent(
#                 x=save_entidade["pos_x"], 
#                 y=save_entidade["pos_y"], 
#                 direcao_olhar=save_entidade.get("direcao", "baixo")
#             ))
#             engine.add_component(entidade_id, RenderComponent(emoji=save_entidade.get("render_emoji", evt.emoji)))
            
#             is_active_atual = save_entidade.get("is_active", True)
            
#             if "stats" in save_entidade:
#                 s_stats = save_entidade["stats"]
#                 engine.add_component(entidade_id, StatsComponent(
#                     nome=s_stats["nome"], pv=s_stats["pv_atual"], pv_max=s_stats["pv_max"],
#                     pm=s_stats["pm_atual"], pm_max=s_stats["pm_max"], 
#                     ataque_base=s_stats["ataque_base"], defesa_base=s_stats["defesa_base"]
#                 ))
#         else:
#             # 🆕 BASE: Sem modificações salvas para este evento. Carrega o padrão do editor
#             engine.add_component(entidade_id, PositionComponent(x=evt.pos_x, y=evt.pos_y))
#             engine.add_component(entidade_id, RenderComponent(emoji=evt.emoji))
#             is_active_atual = True
            
#             # Se for um monstro com atributos base definidos no JSON de parâmetros
#             if "ação" in parametros_base and "mudar_pv" in parametros_base["ação"]:
#                 val_dano = parametros_base["ação"]["mudar_pv"].get("valor", 2)
#                 engine.add_component(entidade_id, StatsComponent(
#                     nome="Monstro", pv=10, pv_max=10, pm=0, pm_max=0, ataque_base=val_dano, defesa_base=2
#                 ))

#         # Componentes de infraestrutura mecânica (mantêm a inteligência do JSON)
#         solido = parametros_base.get("atravessavel", True)
#         engine.add_component(entidade_id, CollisionComponent(solido=solido))
#         engine.add_component(entidade_id, InteractableComponent(
#             tipo_evento=evt.tipo_evento,
#             parametros=parametros_base,
#             is_active=is_active_atual
#         ))

#         if "mover" in parametros_base:
#             engine.add_component(entidade_id, AIComponent(
#                 tipo_movimento=parametros_base["mover"].get("direção", "aleatório"),
#                 action_on_touch=parametros_base.get("ação", {})
#             ))

#     # ==========================================
#     # STEP 5: OBJETOS ESTÁTICOS DO CENÁRIO
#     # ==========================================
#     objetos_cenario = {}
#     if mapa_db.objetos:
#         obj_dict = mapa_db.objetos if isinstance(mapa_db.objetos, dict) else {}
#         for coordenada_str, emoji in obj_dict.items():
#             try:
#                 y_str, x_str = coordenada_str.split(",")
#                 objetos_cenario[(int(y_str), int(x_str))] = emoji
#             except ValueError:
#                 continue

#     return engine, mapa_db.mapa_em_si, objetos_cenario, mapa_id
