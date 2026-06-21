import esper
from textual.screen import Screen
from textual.widgets import Static, RichLog, Label, Input
from textual.containers import Container, ScrollableContainer
from textual.events import Key
from textual import on
from app.views.components.choice_box import ChoiceBox
from app.db.database import SessionLocal
from app.core.engine.systems import (MovementSystem, InteractionSystem, AISystem,
                                     RenderSystem, InventarySystem, EventSystem)
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.components import (PositionComponent, RenderComponent, 
                                        PlayerControlComponent, StatsComponent,
                                        InventoryComponent, EquipmentComponent                                       
)
from app.core.engine.game_state import GameStateManager
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


class GamePlayScreen(Screen):
    CSS_PATH = "styles/game_styles.css"
    
    def __init__(self, mapa_id: int, personagem_id: int = 1):
        super().__init__()
        self.mapa_id = mapa_id
        self.personagem_id = personagem_id
        self.direcao_olhar = "baixo"

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
        
        

    BINDINGS = [("/", "focus_in_command_bar", "")]

    def compose(self):
        with Container(id="game-layout"):
            # Tela do Mapa com suporte a Scroll total
            with ScrollableContainer(id="mapa-viewport", classes='scrollbar-hidden'):
                yield Static("Carregando cenário e banco...", id="tela-mapa", expand=True)
            
            # Tela de Status Dinâmica (Lê da Engine)
            with Container(id="tela-status"):
                yield Label("🧙‍♂️ Status", classes="titulo-secao")
                yield Label("Nome: [bold]...[/]", id="lbl-nome")
                yield Label("hp: -- / --", id="lbl-hp")
                yield Label("mp: -- / --", id="lbl-mp")
                yield Label("ATK: -- | DEF: --", id="lbl-combate")
                
            # Tela de Itens Dinâmica (Lê do Inventário engine)
            with Container(id="tela-itens"):
                yield Label("🎒 Itens", classes="titulo-secao")
                yield Static("Inventário Vazio", id="lbl-inventario")
                
            # Área de Interação Combinada: Histórico (Log) + Entrada de Texto (Terminal Input)
            with Container(id="area-interacao-container"):
                yield RichLog(id="area-interacao", markup=True)
                yield Input(placeholder="Digite um comando... (ex: /usar poção, /equipar espada_fogo)", id="terminal-prompt")

    
    def on_mount(self):
        self.log_mensagem(
            "[bold yellow]>>> Inicializando sistemas de campanha...[/]")
        
        try:
            with SessionLocal() as db_session:
                # Carregamento autêntico sem simulações!
                
                self.engine_manager = self.loader.carregar_engine_do_banco(
                    db_session,
                        usuario_id=1, # ID do jogador ativo
                        cenario_id=1,                  # ID do jogo/campanha escolhida
                        slot_numero=1,                  # Slot selecionado
                        default_mapa_id=1
                                            )
                
            self.mapa_matriz = self.loader.matriz_terrenos
            self.mapa_objetos = self.loader.camada_objetos
            self.mapa_id = self.loader.mapa_id
            
            # Inicia SISTEMAS:
            # # Inicia sistema de eventos
            # self.event_sys = EventSystem(
            #     self.invSys, self.game_state, self.log_mensagem, self.loader.event_bus)
            # # Interações com o Esper
            # self.interacao_sys = InteractionSystem(self.loader.event_bus)
            self.movimento_sys = MovementSystem(self.loader)
            
            self.event_sys = EventSystem(
                self.invSys, self.game_state, self.log_mensagem)
            self.interacao_sys = InteractionSystem()
            self.ai_sys = AISystem(self.movimento_sys)
            
            
            # self.loader.event_bus.subscribe(
            #     "mudar_mapa", self.ao_mudar_de_mapa)

            # self.loader.event_bus.subscribe(
            #     "INTERACTION_SUCCESS", self.on_evento_interacao)

            # self.log_mensagem(
            #     f"[green]Mapa '[bold]{self.loader.nome_mapa}[/]' carregado com sucesso![/]")
            # self.atualizar_tudo()

            # self.loader.event_bus.subscribe("ataque_monstro", self.ao_levar_ataque)
            
            # self.loader.event_bus.subscribe("disparar_bifurcacao",
            #                                 self.disparar_bifurcacao_visual)
            
            esper.remove_handler("mudar_mapa", self.ao_mudar_de_mapa)
            esper.remove_handler("INTERACTION_SUCCESS", self.on_evento_interacao)
            esper.remove_handler("disparar_bifurcacao", self.disparar_bifurcacao_visual)

            esper.set_handler("mudar_mapa", self.ao_mudar_de_mapa)
            esper.set_handler("INTERACTION_SUCCESS", self.on_evento_interacao)
            esper.set_handler("disparar_bifurcacao", self.disparar_bifurcacao_visual)
            
            self.set_interval(1.0, self.game_tick)
            
            self.log_mensagem(
                "[bold green]>>> Engine Pronta! Use setas para andar, ENTER para interagir ou use o Terminal de comandos abaixo.[/]")
            self.atualizar_tudo()

        except Exception as e:
            self.log_mensagem(f"[bold red]❌ Erro crítico: {e}[/]")
            

    def ao_mudar_de_mapa(self, dados_teleporte):
        """
        O ponteiro central de transição. 
        Recebe: {'mapa_id': 3, 'pos_x': 15, 'pos_y': 15}
        """
        
        mapa_alvo = dados_teleporte["mapa_id"]
        nova_pos_x = dados_teleporte["pos_x"]
        nova_pos_y = dados_teleporte["pos_y"]

        with SessionLocal() as db_session:
            # 1. Recarrega a Engine do zero apontando para o novo mapa!
            # Passamos o mapa_alvo como o default_mapa_id
            
            try:
                self.engine_manager = self.loader.carregar_engine_do_banco(
                    db_session=db_session,
                    usuario_id=1,
                    cenario_id=1,
                    slot_numero=1,
                    default_mapa_id=mapa_alvo
                )
            except Exception as e:
                self.log_mensagem(f"Erro: {e}")
                self.log_mensagem(f"engine_manager: {self.engine_manager}") 

        
        # 2. Recarrega dados do mapa
        self.mapa_id = self.loader.mapa_id
        self.mapa_matriz = self.loader.matriz_terrenos
        self.mapa_objetos = self.loader.camada_objetos

        # 2.1 Re-instancia os sistemas para a nova Engine limpa
        try:
            # Interações com o Esper
            # self.interacao_sys = InteractionSystem(self.loader.event_bus)
            # self.ai_sys = AISystem(self.loader,
            #                        self.movimento_sys, self.loader.event_bus)
            self.movimento_sys = MovementSystem(self.loader)
            self.interacao_sys = InteractionSystem()
            self.ai_sys = AISystem(self.movimento_sys)
            
        except Exception as e:
            self.log_mensagem(f"Erro ao Re-instaciar sistemas: {e}")

        # 3. Força o Jogador (ID 1) a posicionar-se na coordenada exata que o JSON mandou
        
        try:
            pos = esper.component_for_entity(1, PositionComponent)
            if pos:
                pos.x = nova_pos_x
                pos.y = nova_pos_y
                
        except Exception as e:
            self.log_mensagem(f"Erro ao posicionar jogador: {e}")

        # self.loader.event_bus.subscribe(
        #     "INTERACTION_SUCCESS", self.on_evento_interacao)
        # self.loader.event_bus.subscribe(
        #     "mudar_mapa", self.ao_mudar_de_mapa)
        esper.remove_handler("mudar_mapa", self.ao_mudar_de_mapa)
        esper.remove_handler("INTERACTION_SUCCESS", self.on_evento_interacao)
        esper.remove_handler("disparar_bifurcacao", self.disparar_bifurcacao_visual)

        esper.set_handler("mudar_mapa", self.ao_mudar_de_mapa)
        esper.set_handler("INTERACTION_SUCCESS", self.on_evento_interacao)
        esper.set_handler("disparar_bifurcacao", self.disparar_bifurcacao_visual)


        self.log_mensagem(
            f"[green]Mapa '[bold]{self.loader.nome_mapa}[/]' carregado com sucesso![/]")
        self.atualizar_tudo()
        
        esper.set_handler(
            "ataque_monstro", self.ao_levar_ataque)

        # self.loader.event_bus.subscribe(
        #     "ataque_monstro", self.ao_levar_ataque)

        self.set_interval(1.0, self.game_tick)

        # 4. Atualiza a tela para o jogador ver o novo cenário imediatamente
        self.atualizar_tudo()
            
    def log_mensagem(self, texto: str):
        """Injeta mensagens formatadas no painel lateral de logs."""
        try:
            self.query_one("#log-eventos", RichLog).write(texto)
        except Exception:
            pass
        try:
            self.query_one("#area-interacao", RichLog).write(texto)
        except Exception:
            pass

    def game_tick(self):
        if self.ai_sys:
            self.ai_sys.update()
            self.atualizar_tudo()


    def action_focus_in_command_bar(self):
            self.log_mensagem("[blue]Digite um comando.[/]")
            commandbox = self.query_one("#terminal-prompt", Input)
            commandbox.select_on_focus = False
            commandbox.value += '/'
            commandbox.cursor_position = len(commandbox.value) + 1
            commandbox.focus()
            

    # ==========================================
    # EVENTOS DA ENGINE
    # ==========================================
    
    def on_evento_interacao(self, payload: dict):
        """Processador de Eventos Universal - Pipeline de 4 Etapas."""
        self.event_sys.processar_evento_interacao(payload)
        self.atualizar_tudo()

    def ao_levar_ataque(self, dados_ataque):
        log = self.query_one("#area-interacao", RichLog)
        dano = dados_ataque.get("mudar_hp", {}).get("valor", 1)
        self.log_mensagem(f'dano: {dano} - dados ataque: {dados_ataque}')
        
        stats = esper.component_for_entity(1, StatsComponent)
        if stats:
            # Desconta o dano mitigado pela defesa real do personagem
            dano_real = max(0, dano - (stats.defesa_base // 3))
            stats.hp = max(0, stats.hp - dano_real)
            self.log_mensagem(
                f"[bold red]⚔️ O monstro atacou você! Sofreu {dano_real} de dano real (Defesa mitigou o resto).[/]")
            
            if stats.hp <= 0:
                self.log_mensagem(
                    "[bold background red]💀 VOCÊ MORREU! Fim de Jogo.[/]")
        
        self.atualizar_paineis_status()


    def disparar_bifurcacao_visual(self, dados):
        """
        Chamado pelo interpretador de comandos quando atinge uma bifurcação.
        Instancia e exibe a caixa interativa na tela.
        """
        pergunta = dados.get("pergunta", "Pergunta:")
        opcoes = dados.get("opcoes", [])
        # Remove uma ChoiceBox antiga caso ainda exista por segurança
        self.remover_choice_box_ativa()

        # Cria a nova caixa dinâmica
        try:
            caixa_escolha = ChoiceBox(
                mensagem=pergunta, opcoes=opcoes, id="box-evento-ativo")
        except Exception as e:
            self.log_mensagem(f"Erro na caixa: {e}")

        # Monta o widget dentro do container de interações ou
        # painel lateral da sua UI
        def executar_montagem_segura(): # Interrompe o scroll automático do Textual!
            try:
                container = self.query_one(
                    "#area-interacao-container")
            except Exception as e:
                self.log_mensagem(f"[red]Erro ao montar a caixa:[/] {e}")

            area_texto = self.query_one("#area-interacao")
            area_texto.styles.height = "60%"
            
            self.query_one("#terminal-prompt").add_class("hidden")

            container.mount(caixa_escolha)
            sub_caixa_element = caixa_escolha.get_child_by_id('choice-box-card')
            caixa_element = sub_caixa_element.get_child_by_id('choice-radioset')
            caixa_element.focus()
            sub_caixa_element.trap_focus()

        self.call_next(executar_montagem_segura)

    def remover_choice_box_ativa(self):
        """Remove o widget da tela de forma limpa."""
        try:
            caixa = self.query_one("#box-evento-ativo", ChoiceBox)
            caixa.remove()
            input_chat = self.query_one("#terminal-prompt")
            area_texto = self.query_one("#area-interacao")
            area_texto.styles.height = "85%"
            self.query_one("#terminal-prompt").remove_class("hidden")
            input_chat.focus()
        except Exception:
            pass

    @on(ChoiceBox.Selected, "#box-evento-ativo")
    def ao_selecionar_opcao_evento(self, event: ChoiceBox.Selected):
        """
        Nativo do Textual. Captura o sinal emitido pelo ChoiceBox 
        assim que o jogador confirma a opção.
        """
        # 1. Guarda a resposta limpa escolhida (texto ou índice)
        opcao_escolhida = event.text
        
        # 2. Desmolda o widget da interface para liberar espaço visual
        self.remover_choice_box_ativa()
        
        # Devolve o foco para o chat de comandos normais
        self.query_one("#terminal-prompt").focus()

        # 3. Alimenta o motor de estados com a escolha e retoma o loop assíncrono
        # (ramos_disponiveis foi mapeado previamente no processador usando strings ou índices)
        self.event_sys.avancar_ramo_evento(
            opcao_escolhida)

    # ==========================================
    # INTERPRETADOR DE COMANDOS DO TERMINAL (SUBMIT INPUT)
    # ==========================================
    @on(Input.Submitted, "#terminal-prompt")
    def processar_comando_terminal(self, event: Input.Submitted):
        
        if event.value.startswith('/>'):
            texto = event.value.strip()
        else:
            texto = event.value.strip().lower()
            
        log = self.query_one("#area-interacao", RichLog)
        prompt = self.query_one("#terminal-prompt", Input)
        
        # Limpa o input para o próximo comando
        prompt.value = ""

        if not texto: return

        # Mostra o comando ecoado no log
        self.log_mensagem(f"[dim]>>> {texto}[/]")

        # 1. Separar o comando do argumento. Ex: "/usar poção" -> comando="/usar", argumento="poção"
        partes = texto.split(" ", 1)
        comando = partes[0]
        argumento = partes[1] if len(partes) > 1 else ""

        stats = esper.component_for_entity(1, StatsComponent)
        inv = esper.component_for_entity(1, InventoryComponent)
        eqp = esper.component_for_entity(1, EquipmentComponent)

        # 🥤 COMANDO: /usar
        if comando == "/usar":
            if inv and self.invSys._inventory_has_item(inv, argumento):
                if argumento in ("poção", "potion"):
                    if self.invSys._inventory_remove_item(inv, argumento, 1):
                        stats.hp = min(stats.max_hp, stats.hp + 20)
                        self.log_mensagem(
                            f"[bold green]✨ Você tomou uma poção. Recuperou 20 hp![/]")
                    else:
                        self.log_mensagem(
                            f"[red]Erro ao usar '{argumento}'.[/]")
                else:
                    self.log_mensagem(
                        f"[orange]O item '{argumento}' não possui efeito de uso imediato.[/]")
            else:
                self.log_mensagem(
                    f"[red]Você não possui '{argumento}' no seu inventário.[/]")
            self.atualizar_paineis_status()
            
        # ⚔️ COMANDO: /equipar
        elif comando == "/equipar":
            if not argumento:
                self.log_mensagem(
                    "[orange]Use: /equipar <nome_da_arma_ou_armadura>[/]")
                return

            if inv and self.invSys._inventory_has_item(inv, argumento):
                if "espada" in argumento:
                    bonus = 5 if "longa" in argumento else 3
                    eqp.arma = {"nome": argumento, "bonus_atk": bonus}
                    self.log_mensagem(
                        f"[bold blue]⚔️ Equipado com sucesso: {argumento.upper()} (+{bonus} ATK).[/]")
                elif "armadura" in argumento or "escudo" in argumento:
                    bonus = 6 if "placas" in argumento else 3
                    eqp.armadura = {"nome": argumento, "bonus_def": bonus}
                    self.log_mensagem(
                        f"[bold blue]🛡️ Equipado com sucesso: {argumento.upper()} (+{bonus} DEF).[/]")
                else:
                    self.log_mensagem(
                        "[orange]Este item não pode ser equipado como arma ou armadura.[/]")
            else:
                self.log_mensagem(
                    f"[red]Você não possui o equipamento '{argumento}' no inventário.[/]")
            self.atualizar_paineis_status()
        
        elif comando in ["/h", "/help", ]:
            self.log_mensagem(f"[yellow] /usar <item consumível> -> 'utiliza o item aplicando seus efeitos' \n /equipar <equipamento> -> 'coloca o equipamento no personagem' \n /sair /q /quit -> 'Sai do jogo'[/]""")

        elif comando == '/>':
            # Interpretador de comandos python que redireciona para o log.add(element)
            codigo = argumento.strip()
            import sys
            try:
                sys.stdout = log
                sys.stderr = log
                sys.stdin.readline = lambda: codigo
                result = exec(codigo)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                
                self.log_mensagem(f"[purple]>>> {sys.stdout.write(str(result))}[/]")
            except Exception as e:
                self.log_mensagem(f"[red]{e}[/]")

        elif comando == '/status':
            stats = esper.component_for_entity(1, StatsComponent)
            self.log_mensagem(f"{stats}")
            
        # Força a interface a recalcular e redesenhar os novos valores obtidos
        elif comando in ["/sair", "/q", "/exit", "/quit"]:
            self.app.pop_screen()
        else:
            self.log_mensagem(
                f"[red]Comando desconhecido: '{comando}'. Tente /usar ou /equipar.[/]")
        
        #self.atualizar_paineis_status()

    # ==========================================
    # INPUTS DE MOVIMENTAÇÃO (MANTÉM O FOCO FORA DO PROMPT AO USAR SETAS)
    # ==========================================
    def on_key(self, event: Key, ) -> None:
        key = event.key
        moveu = False
        
        
        if event.key == '/' or event.key == "\\":
            self.action_focus_in_command_bar(event)
        
        if hasattr(self, "event_sys") and self.event_sys.aguardando_escolha:
            if key in ("d", "/", "m"):
                event.prevent_default()  # Interrompe o scroll automático do Textual!
                event.stop()
            return
        
        
        if key in ("up", "down", "left", "right", "w", "s", "a", "d", "/", "m"):
            event.prevent_default()  # Interrompe o scroll automático do Textual!
            event.stop()


        if key in ("up", "w"):
            self.direcao_olhar = "cima"
            moveu = self.movimento_sys.mover_entidade(1, "cima")
            self.centralizar_camera_no_jogador()
        elif key in ("down", "s"):
            self.direcao_olhar = "baixo"
            moveu = self.movimento_sys.mover_entidade(1, "baixo")
            self.centralizar_camera_no_jogador()
        elif key in ("left", "a"):
            self.direcao_olhar = "esquerda"
            moveu = self.movimento_sys.mover_entidade(1, "esquerda")
            self.centralizar_camera_no_jogador()
        elif key in ("right", "d"):
            self.direcao_olhar = "direita"
            moveu = self.movimento_sys.mover_entidade(1, "direita")
            self.centralizar_camera_no_jogador()
        elif key == "enter":
            # Se o foco estiver no prompt do terminal, deixa o submit do input agir e ignora o raio
            if self.focused == self.query_one("#terminal-prompt"):
                telamapa = self.query_one("#tela-mapa", Static)
                telamapa.focus()
            
            achou_evento = self.interacao_sys.interagir(1, self.direcao_olhar)
            
            if not achou_evento:
                self.log_mensagem(
                    "[gray]Não há nada para acionar aqui na sua frente.[/]")
            self.atualizar_tudo()
            return

        #sleep(0.01)
        self.atualizar_tudo()

    # ==========================================
    # REDESENHO DE TELAS E RECALCULO DE ATRIBUTOS + EQUIPAMENTOS
    # ==========================================
    
    # ANTERIOR AO ESPER
    def atualizar_tudo(self):
        self.atualizar_tela()
        self.atualizar_paineis_status()
        
    def atualizar_tela(self):
        """Compila o frame atual do Esper e atualiza o Canvas Único na tela."""
        
        self.centralizar_camera_no_jogador()
        
        frame_text = self.render_sys.renderizar_frame(
            self.mapa_matriz, self.mapa_objetos)
        self.query_one("#tela-mapa", Static).update(frame_text)

        # Centraliza a câmera no jogador de forma dinâmica

    def centralizar_camera_no_jogador(self):
        """Busca a posição do jogador no Esper e move o viewport do ScrollableContainer."""
        try:
            # O ID do jogador principal é 1
            pos_player = esper.component_for_entity(1, PositionComponent)
            if pos_player:
                # Pegamos o container de scroll
                viewport = self.query_one(
                    "#mapa-viewport", ScrollableContainer)

                # Coordenadas virtuais baseadas no tamanho das fontes do terminal
                # Multiplicamos o X por 2 porque cada coluna visual de emoji gasta 2 caracteres de largura
                largura_tela_virtual = viewport.content_size.width
                altura_tela_virtual = viewport.content_size.height

                # Centraliza a mira subtraindo metade do viewport visível
                alvo_x = (pos_player.x * 2) - (largura_tela_virtual // 2)
                alvo_y = pos_player.y - (altura_tela_virtual // 2)

                # Força a rolagem exata sem animações para evitar trepidação (flicker)
                viewport.scroll_to(x=max(0, alvo_x), y=max(
                    0, alvo_y), animate=False)
        except Exception:
            pass
    
    
    @on(Input.Submitted, "#txt-chat")
    def ao_enviar_comando_chat(self, event: Input.Submitted):
        """Processa a caixa de comandos rápidos de texto."""
        texto = event.value.strip()
        if texto:
            self.log_mensagem(f"[bold white]Você:[/] {texto}")
            self.query_one("#txt-chat", Input).value = ""


    def atualizar_paineis_status(self):
       # 🚀 BLINDAGEM CONTRA KEYERROR EM TRANSIÇÕES / FECHAMENTO:
        try:
            stats = esper.component_for_entity(1, StatsComponent)
            inv = esper.component_for_entity(1, InventoryComponent)
            eqp = esper.component_for_entity(1, EquipmentComponent)
        except KeyError:
            # Se o herói não foi instanciado no frame de encerramento do app, aborta o redesenho suavemente
            return

        if not stats: return

        # 🥊 MATEMÁTICA REAL DE EQUIPAMENTOS: Atributo Total = Base + Bónus do Equipamento
        bonus_atk = eqp.arma.get("bonus_atk", 0) if eqp and eqp.arma else 0
        bonus_def = eqp.armadura.get("bonus_def", 0) if eqp and eqp.armadura else 0
        
        atk_total = stats.ataque_base + bonus_atk
        def_total = stats.defesa_base + bonus_def

        # Atualiza Painel de Status
        self.query_one("#lbl-nome", Label).update(f"Nome: [bold green]{stats.nome}[/]")
        self.query_one("#lbl-hp", Label).update(f"hp: [bold red]{stats.hp} / {stats.max_hp}[/]")
        self.query_one("#lbl-mp", Label).update(f"mp: [bold blue]{stats.mp} / {stats.max_mp}[/]")
        self.query_one("#lbl-combate", Label).update(f"ATK: [yellow]{atk_total}[/] | DEF: [cyan]{def_total}[/]")

        # Atualiza Painel de Itens (Inventário)
        texto_inv = ""
        if inv:
            for nome_item, qtd in self.invSys._get_inventory_mapping(inv).items():
                if qtd > 0:
                    texto_inv += f"• {nome_item.capitalize()} (x{qtd})\n"
        self.query_one(
            "#lbl-inventario", Static).update(texto_inv if texto_inv else "Inventário Vazio")
