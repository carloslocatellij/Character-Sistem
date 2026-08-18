import esper
from typing import Optional
from textual.screen import Screen
from textual.widgets import Static, RichLog, Label, Input
from textual.containers import Container, ScrollableContainer
from textual.events import Key
from textual import on
from app.views.components.choice_box import ChoiceBox
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from app.core.engine.systems import (MovementSystem, InteractionSystem, AISystem,
                                     RenderSystem, InventarySystem, EventSystem,
                                     NetworkSystem, BattleSystem)
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.components import (PositionComponent, StatsComponent,
                                        InventoryComponent, EquipmentComponent
)
from app.core.engine.game_state import GameStateManager
from app.packages.stylewriter import ChatLog
import logging
logging.basicConfig(level=logging.INFO, filename='log.log', filemode='a')


class GamePlayScreen(Screen):
    CSS_PATH = 'styles/game_styles.css'
    
    def __init__(self, mapa_id: int = 1, personagem_id: int = 1):
        super().__init__()
        self.mapa_id = mapa_id
        self.personagem_id = personagem_id
        self.direcao_olhar = 'baixo'

        # Inicializa o Barramento e Carregador da Engine
        self.loader = GameEngineLoader()
        self.game_state = GameStateManager()
        self.mapa_matriz = None
        self.mapa_objetos = {}

        # Sistemas lógicos adaptados para Esper
        self.movimento_sys = None
        self.interacao_sys = None
        self.render_sys = RenderSystem()
        self.invSys = InventarySystem()
        self.network_sys = NetworkSystem()
        
        self.contador_de_ticks: int = 0
    

    BINDINGS = [('/', 'focus_in_command_bar', '')]

    def compose(self):
        with Container(id='game-layout'):
            # Tela do Mapa com suporte a Scroll total
            with ScrollableContainer(id='mapa-viewport', classes="scrollbar-hidden"):
                yield Static('Carregando cenário e banco...', id='tela-mapa', expand=True)
            
            # Tela de Status Dinâmica (Lê da Engine)
            with Container(id='tela-status'):
                yield Label('🧙‍♂️ Status', classes='titulo-secao')
                yield Label('Nome: [bold]...[/]', id='lbl-nome')
                yield Label('hp: -- / --', id='lbl-hp')
                yield Label('mp: -- / --', id='lbl-mp')
                yield Label('ATK: -- | DEF: --', id='lbl-combate')
                
            # Tela de Itens Dinâmica (Lê do Inventário engine)
            with Container(id='tela-itens'):
                yield Label('🎒 Itens', classes='titulo-secao')
                yield Static('Inventário Vazio', id='lbl-inventario')
                
            # Área de Interação Combinada: Histórico (Log) + Entrada de Texto (Terminal Input)
            with Container(id='area-interacao-container'):
                yield ChatLog(id='area-interacao') #markup=True)
                yield Input(placeholder='Digite um comando... (ex: /usar poção, /equipar espada_fogo)', id='terminal-prompt')

    
    def on_mount(self):
        self.log_mensagem(
            'CharSystem',
            estilo="slant"
            )
        
        try:
            with SessionLocal() as db_session:
                from sqlalchemy import select
                sql_coord_ini = select(MapaDB).where(
                    MapaDB.configs.contains('coordenadas_iniciais'))
                self.mapa_id = db_session.scalars(sql_coord_ini).first().id
                
                self.engine_manager = self.loader.carregar_engine_do_banco(
                    db_session,
                    usuario_id=1, # ID do jogador ativo
                    cenario_id=1,                  # ID do jogo/campanha escolhida
                    slot_numero=1,                  # Slot selecionado
                    default_mapa_id=self.mapa_id,
                    game_state=self.game_state,
                )
                
            self.mapa_matriz = self.loader.matriz_terrenos
            self.mapa_objetos = self.loader.camada_objetos
            self.mapa_id = self.loader.mapa_id
            
            self.movimento_sys = MovementSystem(self.loader)
            self.event_sys = EventSystem(self.invSys, self.game_state, self.log_mensagem)
            self.interacao_sys = InteractionSystem()
            self.ai_sys = AISystem(self.game_state)
            self.network_sys = NetworkSystem()
            self.render_sys = RenderSystem(self.game_state)

            # Registra os processadores no Esper para o mundo ativo
            for proc_inst in (self.movimento_sys, self.event_sys, self.interacao_sys, self.ai_sys, self.network_sys, self.render_sys):
                try:
                    esper.remove_processor(proc_inst.__class__)
                except KeyError:
                    pass
                esper.add_processor(proc_inst)
            
            # Registra o BattleSystem separadamente (sistema de combate)
            self.battle_sys = BattleSystem()
            try:
                esper.remove_processor(BattleSystem)
            except KeyError:
                pass
            esper.add_processor(self.battle_sys)
            
            esper.remove_handler('mudar_mapa', self.ao_mudar_de_mapa)
            esper.remove_handler('INTERACTION_SUCCESS', self.on_evento_interacao)
            esper.remove_handler('disparar_bifurcacao', self.disparar_bifurcacao_visual)
            esper.remove_handler('solicitar_iniciar_combate', self._ao_solicitar_combate)

            esper.set_handler('mudar_mapa', self.ao_mudar_de_mapa)
            esper.set_handler('INTERACTION_SUCCESS', self.on_evento_interacao)
            esper.set_handler('disparar_bifurcacao', self.disparar_bifurcacao_visual)
            esper.set_handler('solicitar_iniciar_combate', self._ao_solicitar_combate)
            
            self.game_loop()
            
            self.log_mensagem(
                '[bold green]>>> Engine Pronta!.[/]')
            self.atualizar_tudo()

        except Exception as e:
            self.log_mensagem(f'[bold red]❌ Erro crítico: {e}[/]')
    
    def on_unmount(self) -> None:
        """Limpa as escutas de eventos do Esper ao fechar a tela."""
        esper.remove_handler("mudar_mapa", self.ao_mudar_de_mapa)
        esper.remove_handler("INTERACTION_SUCCESS", self.on_evento_interacao)
        esper.remove_handler('disparar_bifurcacao', self.disparar_bifurcacao_visual)
        esper.remove_handler('solicitar_iniciar_combate', self._ao_solicitar_combate)
            

    def ao_mudar_de_mapa(self, dados_teleporte):
        '''
        O ponteiro central de transição. 
        Recebe: {"mapa_id": 3, "pos_x": 15, "pos_y": 15}
        '''
        mapa_alvo = dados_teleporte['mapa_id']
        nova_pos_x = dados_teleporte['pos_x']
        nova_pos_y = dados_teleporte['pos_y']

        with SessionLocal() as db_session:
            # 1. Recarrega a Engine do zero apontando para o novo mapa!
            try:
                self.engine_manager = self.loader.carregar_engine_do_banco(
                    db_session=db_session,
                    usuario_id=1,
                    cenario_id=1,
                    slot_numero=1,
                    default_mapa_id=mapa_alvo,
                    game_state=self.game_state,
                )
            except Exception as e:
                self.log_mensagem(f'Erro: {e}')
                self.log_mensagem(f'engine_manager: {self.engine_manager}') 

        # 2. Recarrega dados do mapa
        self.mapa_id = self.loader.mapa_id
        self.mapa_matriz = self.loader.matriz_terrenos
        self.mapa_objetos = self.loader.camada_objetos

        # 2.1 Re-instancia e registra os sistemas para o novo contexto de mundo
        try:
            self.movimento_sys = MovementSystem(self.loader)
            self.interacao_sys = InteractionSystem()
            self.ai_sys = AISystem(self.game_state)
            self.network_sys = NetworkSystem()
            self.render_sys = RenderSystem(self.game_state)
            self.event_sys = EventSystem(self.invSys, self.game_state, self.log_mensagem)
            self.battle_sys = BattleSystem()
            
            for proc_inst in (self.movimento_sys, self.event_sys, self.interacao_sys, self.ai_sys, self.network_sys, self.render_sys, self.battle_sys):
                try:
                    esper.remove_processor(proc_inst.__class__)
                except KeyError:
                    pass
                esper.add_processor(proc_inst)
        except Exception as e:
            self.log_mensagem(f'Erro ao Re-instaciar sistemas: {e}')

        # 3. Força o Jogador (ID 1) a posicionar-se na coordenada exata que o JSON mandou
        try:
            pos = esper.component_for_entity(1, PositionComponent)
            if pos:
                pos.x = nova_pos_x
                pos.y = nova_pos_y
        except Exception as e:
            self.log_mensagem(f'Erro ao posicionar jogador: {e}')
            
        esper.set_handler('mudar_mapa', self.ao_mudar_de_mapa)
        esper.set_handler('INTERACTION_SUCCESS', self.on_evento_interacao)
        esper.set_handler('disparar_bifurcacao', self.disparar_bifurcacao_visual)

        self.log_mensagem(
            f'[green]Mapa "[bold]{self.loader.nome_mapa}[/]" carregado com sucesso![/]')
        self.atualizar_tudo()
        
        esper.set_handler('ataque_monstro', self.ao_levar_ataque)

        # 4. Atualiza a tela para o jogador ver o novo cenário imediatamente
        self.atualizar_tudo()
            
    def log_mensagem(self, texto: str, estilo=None, velocidade: float = 0.01, notif=False):
        '''Injeta mensagens formatadas no painel lateral de logs.'''
        if notif:
            try:
                self.notify(texto, title='Noticia', severity='information')
            except Exception as e:
                logging.error(f'Erro ao notificar mensagem no log: {e}')
        else:
            try:
                self.query_one('#area-interacao', ChatLog).write(texto, estilo=estilo, velocidade=velocidade)
            except Exception as e:
                logging.error(f'Erro ao escrever mensagem no log: {e}')
            

    # ==========================================
    # GAME LOOP (Processamento via Esper)
    # ==========================================
    def game_loop(self):
        if not hasattr(self, "_game_timer"):
            self._game_timer = self.set_interval(0.01, self.game_tick)
        
        
    def game_tick(self):
        self.contador_de_ticks += 1
        
        if self.contador_de_ticks % 30 == 0:    
            tick_de_movimento = self.contador_de_ticks // 30
            
            # Utiliza os recursos de processamento nativos do Esper
            esper.process(tick_de_movimento)
            self.atualizar_tudo()


    def action_focus_in_command_bar(self):
            self.log_mensagem('[blue]Digite um comando.[/]')
            commandbox = self.query_one('#terminal-prompt', Input)
            commandbox.select_on_focus = False
            commandbox.value += "/"
            commandbox.cursor_position = len(commandbox.value) + 1
            commandbox.focus()
            

    # ==========================================
    # EVENTOS DA ENGINE
    # ==========================================
    def on_evento_interacao(self, payload: dict):
        '''Processador de Eventos Universal - Pipeline de 4 Etapas.'''
        if not self.is_mounted:  # Evita consultar widgets em telas inativas
            return
        self.event_sys.processar_evento_interacao(payload)
        self.atualizar_tudo()

    def ao_levar_ataque(self, dados_ataque):
        dano = dados_ataque.get('mudar_hp', {}).get('valor', 1)
        stats = esper.component_for_entity(1, StatsComponent)
        if stats:
            # Desconta o dano mitigado pela defesa real do personagem
            dano_real = max(0, dano - (stats.defesa_base // 3))
            stats.hp = max(0, stats.hp - dano_real)
            self.log_mensagem(
                f'[bold red]⚔️ O monstro atacou você! Sofreu {dano_real} de dano real (Defesa mitigou o resto).[/]')
            
            if stats.hp <= 0:
                self.log_mensagem(
                    '[bold background red]💀 VOCÊ MORREU! Fim de Jogo.[/]')
        
        self.atualizar_paineis_status()

    # ==========================================
    # COMBATE POR TURNOS — INTEGRAÇÃO
    # ==========================================

    def _ao_solicitar_combate(self, dados_inimigo: dict) -> None:
        """
        Handler disparado pelo EventSystem quando o comando 'iniciar_combate'
        é processado. Mapeia o herói do ECS para o domínio Personagem e
        empilha a BattleScreen sobre o GamePlayScreen.

        Suporta dois formatos de dados:
        - Dict único (retrocompatível): {'nome': ..., 'nivel': ...}
        - Dict com lista: {'inimigos': [{...}, {...}]}  → 1 a 4 inimigos
        """
        if not self.is_mounted:
            return

        heroi_dominio = self._obter_heroi_dominio()
        if heroi_dominio is None:
            self.log_mensagem('[bold red]❌ Erro: não foi possível carregar o herói para o combate.[/]')
            return

        # Detecta se é formato de lista ou único inimigo (retrocompatibilidade)
        if "inimigos" in dados_inimigo:
            inimigos_dados = dados_inimigo["inimigos"][:4]  # Máximo de 4
        else:
            inimigos_dados = [dados_inimigo]

        def _ao_concluir_combate(resultado: str | None = None):
            res = resultado if (resultado and isinstance(resultado, str)) else "venceu"
            esper.dispatch_event("combate_finalizado_gui", res)

        try:
            from app.views.battle_screen import BattleScreen
            self.app.push_screen(BattleScreen(heroi_dominio, inimigos_dados), _ao_concluir_combate)
        except Exception as erro_push:
            self.log_mensagem(f'[bold red]❌ Erro ao abrir a tela de combate: {erro_push}[/]')
            logging.error(f'_ao_solicitar_combate: {erro_push}')
            esper.dispatch_event("combate_finalizado_gui", "venceu")


    def _obter_heroi_dominio(self) -> Optional[object]:
        """
        Mapper: StatsComponent/ECS → objeto Personagem do domínio.
        Utiliza GameController.converter_para_dominio com os dados do personagem
        carregados do banco de dados, enriquecendo-os com o estado atual do ECS (HP, MP e equipamentos).
        Padrão Mapper conforme Regra 1.
        """
        try:
            from app.controllers.game_controller import GameController
            from app.models.personagens_db import PersonagemDB

            with SessionLocal() as db_session:
                personagem_db = db_session.query(PersonagemDB).filter_by(
                    id=self.personagem_id
                ).first()
                if personagem_db is None:
                    logging.error(f'_obter_heroi_dominio: PersonagemDB id={self.personagem_id} não encontrado.')
                    return None
                
                heroi_dominio = GameController.converter_para_dominio(personagem_db)
                if heroi_dominio:
                    stats = esper.component_for_entity(1, StatsComponent)
                    eqp = esper.component_for_entity(1, EquipmentComponent)
                    
                    # Sincroniza Equipamentos do ECS para o Domínio
                    if eqp:
                        from app.core.entities.equipamentos import Arma, Armadura, Escudo
                        
                        if eqp.arma:
                            nome = eqp.arma.get("nome", "Espada")
                            dano = eqp.arma.get("bonus_atk") or eqp.arma.get("dano", 3)
                            tipo_ataque = eqp.arma.get("tipo", "corpo")
                            heroi_dominio.mao_direita = Arma(nome=nome, dano=dano, tipo=tipo_ataque)
                        else:
                            heroi_dominio.mao_direita = None

                        arma_esquerda = None
                        armadura = None
                        
                        if hasattr(eqp, "escudo") and eqp.escudo:
                            nome = eqp.escudo.get("nome", "Escudo")
                            defesa = eqp.escudo.get("bonus_def") or eqp.escudo.get("defesa", 3)
                            arma_esquerda = Escudo(nome=nome, defesa_extra=defesa)
                        
                        if eqp.armadura:
                            nome = eqp.armadura.get("nome", "Armadura")
                            bonus = eqp.armadura.get("bonus_def") or eqp.armadura.get("defesa", 3)
                            if "escudo" in nome.lower():
                                arma_esquerda = Escudo(nome=nome, defesa_extra=bonus)
                            else:
                                armadura = Armadura(nome=nome, defesa=bonus)
                        
                        heroi_dominio.mao_esquerda = arma_esquerda
                        heroi_dominio.armadura = armadura
                        
                    # Recalcula atributos do domínio (inclusive max_hp e max_mp baseados em fórmulas)
                    heroi_dominio.atualizar_atributos_totais()
                    
                    # Sincroniza HP e Mana atuais salvando nos campos lógicos correspondentes
                    if stats:
                        heroi_dominio.pv_atual = min(stats.hp, heroi_dominio.max_hp)
                        heroi_dominio.pm_atual = min(stats.mp, heroi_dominio.max_mp)
                    
                    # Sincroniza magias conhecidas do HeroComponent (ECS) para o Domínio
                    from app.core.engine.components import HeroComponent
                    if esper.has_component(1, HeroComponent):
                        hero_comp = esper.component_for_entity(1, HeroComponent)
                        if hero_comp and hasattr(hero_comp, "personagem") and hero_comp.personagem:
                            for magia in hero_comp.personagem.magias_conhecidas:
                                if not any(m.nome == magia.nome for m in heroi_dominio.magias_conhecidas):
                                    heroi_dominio.magias_conhecidas.append(magia)
                    
                return heroi_dominio
        except Exception as erro_mapper:
            logging.error(f'_obter_heroi_dominio: {erro_mapper}')
            return None


    def disparar_bifurcacao_visual(self, dados):
        '''
        Chamado pelo interpretador de comandos quando atinge uma bifurcação.
        Instancia e exibe a caixa interativa na tela.
        '''
        pergunta = dados.get('pergunta', 'Pergunta:')
        opcoes = dados.get('opcoes', [])
        self.remover_choice_box_ativa()

        # Cria a nova caixa dinâmica
        try:
            caixa_escolha = ChoiceBox(
                mensagem=pergunta, opcoes=opcoes, id='box-evento-ativo')
        except Exception as e:
            self.log_mensagem(f'Erro na caixa: {e}')

        # Monta o widget dentro do container de interações ou painel lateral da UI
        def executar_montagem_segura(): # Interrompe o scroll automático do Textual!
            try:
                container = self.query_one('#area-interacao-container')
            except Exception as e:
                self.log_mensagem(f'[red]Erro ao montar a caixa:[/] {e}')

            area_texto = self.query_one('#area-interacao')
            area_texto.styles.height = '60%'
            
            self.query_one('#terminal-prompt').add_class('hidden')

            container.mount(caixa_escolha)
            sub_caixa_element = caixa_escolha.get_child_by_id("choice-box-card")
            caixa_element = sub_caixa_element.get_child_by_id("choice-radioset")
            caixa_element.focus()
            sub_caixa_element.trap_focus()

        self.call_next(executar_montagem_segura)

    def remover_choice_box_ativa(self):
        '''Remove o widget da tela de forma limpa.'''
        try:
            caixa = self.query_one('#box-evento-ativo', ChoiceBox)
            caixa.remove()
            input_chat = self.query_one('#terminal-prompt')
            area_texto = self.query_one('#area-interacao')
            area_texto.styles.height = '85%'
            self.query_one('#terminal-prompt').remove_class('hidden')
            input_chat.focus()
        except Exception:
            pass

    @on(ChoiceBox.Selected, '#box-evento-ativo')
    def ao_selecionar_opcao_evento(self, event: ChoiceBox.Selected):
        '''
        Nativo do Textual. Captura o sinal emitido pelo ChoiceBox 
        assim que o jogador confirma a opção.
        '''
        opcao_escolhida = event.text
        self.remover_choice_box_ativa()
        self.query_one('#terminal-prompt').focus()

        # Alimenta o motor de estados com a escolha e retoma o loop assíncrono
        self.event_sys.avancar_ramo_evento(opcao_escolhida)

    # ==========================================
    # INTERPRETADOR DE COMANDOS DO TERMINAL (SUBMIT INPUT)
    # ==========================================
    @on(Input.Submitted, '#terminal-prompt')
    def processar_comando_terminal(self, event: Input.Submitted):
        if event.value.startswith("/>"):
            texto = event.value.strip()
        else:
            texto = event.value.strip().lower()
            
        prompt = self.query_one('#terminal-prompt', Input)
        prompt.value = ''

        if not texto: return

        # 1. Separar o comando do argumento
        partes = texto.split(' ', 1)
        comando = partes[0]
        argumento = partes[1] if len(partes) > 1 else ''

        stats = esper.component_for_entity(1, StatsComponent) if esper.entity_exists(1) and esper.has_component(1, StatsComponent) else None
        inv = esper.component_for_entity(1, InventoryComponent) if esper.entity_exists(1) and esper.has_component(1, InventoryComponent) else None
        eqp = esper.component_for_entity(1, EquipmentComponent) if esper.entity_exists(1) and esper.has_component(1, EquipmentComponent) else None

        # 🥤 COMANDO: /usar
        if comando == '/usar':
            if argumento:
                from app.core.engine.item_system import aplicar_usar_item
                sucesso, msg = aplicar_usar_item(stats, inv, argumento)
                self.log_mensagem(msg)
            else:
                from app.views.inventario_screen import InventarioMenuScreen
                self.app.push_screen(InventarioMenuScreen(aba_inicial="tab-itens"), lambda res: self.atualizar_paineis_status())
            self.atualizar_paineis_status()

        # ⚔️ COMANDO: /equipar
        elif comando in ['/equipar', '/equipamentos', '/equip']:
            if argumento:
                from app.core.engine.item_system import aplicar_equipar_item
                sucesso, msg = aplicar_equipar_item(eqp, inv, argumento)
                self.log_mensagem(msg)
            else:
                from app.views.inventario_screen import InventarioMenuScreen
                self.app.push_screen(InventarioMenuScreen(aba_inicial="tab-equipamentos"), lambda res: self.atualizar_paineis_status())
            self.atualizar_paineis_status()

        elif comando in ['/inv', '/inventario', '/itens']:
            from app.views.inventario_screen import InventarioMenuScreen
            self.app.push_screen(InventarioMenuScreen(aba_inicial="tab-itens"), lambda res: self.atualizar_paineis_status())
            self.atualizar_paineis_status()

        elif comando in ['/party', '/equipe', '/recrutar', '/alistamento', '/formacao']:
            from app.views.party_management_screen import PartyManagementScreen
            self.app.push_screen(PartyManagementScreen(), lambda res: self.atualizar_paineis_status())
            self.atualizar_paineis_status()

        elif comando in ['/h', '/help', ]:
            self.log_mensagem(f'[yellow] /party -> "Gerencia equipe e alistamento de novos heróis" \n /usar <item consumível> -> "utiliza o item aplicando seus efeitos" \n /equipar <equipamento> -> "coloca o equipamento no personagem" \n /sair /q /quit -> "Sai do jogo"[/]')

        elif comando == "/>":
            codigo = argumento.strip()
            import sys
            try:
                log = self.query_one('#area-interacao', ChatLog)
                sys.stdout = log
                sys.stderr = log
                sys.stdin.readline = lambda: codigo
                result = exec(codigo)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                
                self.log_mensagem(f'[purple]>>> {sys.stdout.write(str(result))}[/]')
            except Exception as e:
                self.log_mensagem(f'[red]{e}[/]')

        elif comando == "/status":
            stats = esper.component_for_entity(1, StatsComponent)
            self.log_mensagem(f'{stats}')
            
        elif comando in ['/sair', '/q', '/exit', '/quit']:
            esper.switch_world('default')
            esper.clear_database()
            esper.clear_cache()
            for world in esper.list_worlds():
                if world != 'default':
                    esper.delete_world(world)
            self.app.pop_screen()
        else:
            self.log_mensagem(f'[red]Comando desconhecido: "{comando}". Tente /usar ou /equipar.[/]')
        
        self.atualizar_paineis_status()

    # ==========================================
    # INPUTS DE MOVIMENTAÇÃO
    # ==========================================
    def on_key(self, event: Key, ) -> None:
        key = event.key
        
        if event.key == "/" or event.key == '\\':
            self.action_focus_in_command_bar(event)
        
        if hasattr(self, 'event_sys') and self.event_sys.aguardando_escolha:
            if key in ('d', '/', 'm'):
                event.prevent_default()
                event.stop()
            return
        
        if key in ('up', 'down', 'left', 'right', 'w', 's', 'a', 'd', '/', 'm'):
            event.prevent_default()
            event.stop()

        if key in ('up', 'w'):
            self.direcao_olhar = 'cima'
            self.movimento_sys.mover_entidade(1, 'cima')
            self.centralizar_camera_no_jogador()
        elif key in ('down', 's'):
            self.direcao_olhar = 'baixo'
            self.movimento_sys.mover_entidade(1, 'baixo')
            self.centralizar_camera_no_jogador()
        elif key in ('left', 'a'):
            self.direcao_olhar = 'esquerda'
            self.movimento_sys.mover_entidade(1, 'esquerda')
            self.centralizar_camera_no_jogador()
        elif key in ('right', 'd'):
            self.direcao_olhar = 'direita'
            self.movimento_sys.mover_entidade(1, 'direita')
            self.centralizar_camera_no_jogador()
        elif key == 'enter':
            achou_evento = None
            prompt = self.query_one('#terminal-prompt')
            if self.focused == prompt and prompt.value == '':
                event.prevent_default()
                if self.interacao_sys:
                    achou_evento = self.interacao_sys.interagir(
                        1, self.direcao_olhar)
                    if not achou_evento:
                        self.log_mensagem(
                            '[gray]Não há nada para acionar aqui na sua frente.[/]')
                telamapa = self.query_one('#tela-mapa', Static)
                telamapa.focus()
            else:
                if self.interacao_sys:
                    achou_evento = self.interacao_sys.interagir(1, self.direcao_olhar)
                    if not achou_evento:
                        self.log_mensagem('[gray]Não há nada para acionar aqui na sua frente.[/]')
            self.atualizar_tudo()
            return
        
        self.atualizar_tudo()

    # ==========================================
    # REDESENHO DE TELAS E RECALCULO DE ATRIBUTOS
    # ==========================================
    def atualizar_tudo(self):
        self.atualizar_tela()
        self.atualizar_paineis_status()
        
    def atualizar_tela(self):
        '''Compila o frame atual do Esper e atualiza o Canvas Único na tela.'''
        self.centralizar_camera_no_jogador()
        frame_text = self.render_sys.renderizar_frame(
            self.mapa_matriz, self.mapa_objetos)
        self.query_one('#tela-mapa', Static).update(frame_text)

    def centralizar_camera_no_jogador(self):
        '''Busca a posição do jogador no Esper e move o viewport do ScrollableContainer.'''
        try:
            pos_player = esper.component_for_entity(1, PositionComponent)
            if pos_player:
                viewport = self.query_one('#mapa-viewport', ScrollableContainer)

                largura_tela_virtual = viewport.content_size.width
                altura_tela_virtual = viewport.content_size.height

                alvo_x = (pos_player.x * 2) - (largura_tela_virtual // 2)
                alvo_y = pos_player.y - (altura_tela_virtual // 2)

                viewport.scroll_to(x=max(0, alvo_x), y=max(0, alvo_y), animate=False)
        except Exception:
            pass
    
    @on(Input.Submitted, '#txt-chat')
    def ao_enviar_comando_chat(self, event: Input.Submitted):
        '''Processa a caixa de comandos rápidos de texto.'''
        texto = event.value.strip()
        if texto:
            self.log_mensagem(f'[bold white]Você:[/] {texto}')
            self.query_one('#txt-chat', Input).value = ''

    def atualizar_paineis_status(self):
        try:
            stats = esper.component_for_entity(1, StatsComponent)
            inv = esper.component_for_entity(1, InventoryComponent)
            eqp = esper.component_for_entity(1, EquipmentComponent)
        except KeyError:
            return

        if not stats: return

        bonus_atk = eqp.arma.get('bonus_atk', 0) if eqp and eqp.arma else 0
        bonus_def = eqp.armadura.get('bonus_def', 0) if eqp and eqp.armadura else 0
        
        atk_total = stats.ataque_base + bonus_atk
        def_total = stats.defesa_base + bonus_def

        # Atualiza Painel de Status
        self.query_one('#lbl-nome', Label).update(f'Nome: [bold green]{stats.nome}[/]')
        self.query_one('#lbl-hp', Label).update(f'hp: [bold red]{stats.hp} / {stats.max_hp}[/]')
        self.query_one('#lbl-mp', Label).update(f'mp: [bold blue]{stats.mp} / {stats.max_mp}[/]')
        self.query_one('#lbl-combate', Label).update(f'ATK: [yellow]{atk_total}[/] | DEF: [cyan]{def_total}[/]')

        # Atualiza Painel de Itens (Inventário)
        texto_inv = ''
        if inv:
            for nome_item, qtd in self.invSys._get_inventory_mapping(inv).items():
                if qtd > 0:
                    texto_inv += f'• {nome_item.capitalize()} (x{qtd})\n'
        self.query_one(
            '#lbl-inventario', Static).update(texto_inv if texto_inv else 'Inventário Vazio')

    def on_resume(self) -> None:
        """Chamado quando a tela de batalha é fechada e voltamos ao GamePlayScreen."""
        self.atualizar_paineis_status()
