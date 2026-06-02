import esper
from textual.screen import Screen
from textual.widgets import Static, RichLog, Label, Input
from textual.containers import Container, ScrollableContainer
from textual.events import Key
from textual import on

from app.db.database import SessionLocal
from app.core.engine.systems import MovementSystem, InteractionSystem, AISystem, RenderSystem
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.components import PositionComponent, RenderComponent, PlayerControlComponent


class GamePlayScreen(Screen):
    CSS_PATH = "styles/game_styles.css"
    
    def __init__(self, mapa_id: int, personagem_id: int = 1):
        super().__init__()
        self.mapa_id = mapa_id
        self.personagem_id = personagem_id
        self.direcao_olhar = "baixo"

        # Inicializa o Barramento e Carregador da Engine
        self.loader = GameEngineLoader()
        self.mapa_matriz = None
        self.mapa_objetos = {}

        # Sistemas lógicos adaptados para Esper
        self.movimento_sys = None
        self.interacao_sys = None
        self.render_sys = RenderSystem()

    def compose(self):
        with Container(id="game-layout"):
            # Tela do Mapa com suporte a Scroll total
            with ScrollableContainer(id="mapa-viewport", classes='scrollbar-hidden'):
                yield Static("Carregando cenário e banco...", id="tela-mapa", expand=True)
            
            # Tela de Status Dinâmica (Lê da Engine)
            with Container(id="tela-status"):
                yield Label("🧙‍♂️ Status", classes="titulo-secao")
                yield Label("Nome: [bold]...[/]", id="lbl-nome")
                yield Label("PV: -- / --", id="lbl-pv")
                yield Label("PM: -- / --", id="lbl-pm")
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
            with SessionLocal() as db:
                # Carregamento autêntico sem simulações!
                
                self.engine_manager = self.loader.carregar_engine_do_banco(
                        #usuario_id=self.personagem_id, # ID do jogador ativo
                        #cenario_id=1,                  # ID do jogo/campanha escolhida
                        #slot_numero=1                  # Slot selecionado
                        db,
                        mapa_id=1
                                            )
                
            self.mapa_matriz = self.loader.matriz_terrenos
            self.mapa_objetos = self.loader.camada_objetos
            self.mapa_id = self.loader.mapa_id
            
            # TODO: teste pratico mostrou que o engine_load cria a entidade; limpar
            if not esper.entity_exists(1):
                esper.create_entity(
                    PositionComponent(x=9, y=9),
                    RenderComponent(emoji="🐱"),
                    PlayerControlComponent()
                )

            self.movimento_sys = MovementSystem(self.loader)
            
            # Interações com o Esper
            self.interacao_sys = InteractionSystem(self.loader.event_bus)
            
            self.ai_sys = AISystem(self.loader,
                                   self.movimento_sys, self.interacao_sys)

            self.loader.event_bus.subscribe(
                "INTERACTION_SUCCESS", self.on_evento_interacao)

            self.log_mensagem(
                f"[green]Mapa '[bold]{self.loader.nome_mapa}[/]' carregado com sucesso![/]")
            self.atualizar_tudo()


            # Assina eventos globais da rádio lúdica
            self.loader.event_bus.subscribe("bau", self.ao_recolher_bau)
            self.loader.event_bus.subscribe("ataque_monstro", self.ao_levar_ataque)

            # Batimento dos monstros autónomos a cada 1 segundo
            self.set_interval(1.0, self.game_tick)

            self.log_mensagem(
                "[bold green]>>> Engine Pronta! Use setas para andar, ENTER para interagir ou use o Terminal de comandos abaixo.[/]")
            self.atualizar_tudo()

        except Exception as e:
            self.log_mensagem(f"[bold red]❌ Erro crítico: {e}[/]")
            
    def log_mensagem(self, texto: str):
        """Injeta mensagens formatadas no painel lateral de logs."""
        try:
            self.query_one("#log-eventos", RichLog).write(texto)
        except Exception:
            pass

    def game_tick(self):
        if self.ai_sys:
            self.ai_sys.update()
            self.atualizar_tudo()


    # ==========================================
    # EVENTOS DA ENGINE
    # ==========================================
    
    def on_evento_interacao(self, payload: dict):
        """Callback acionado via Event Bus quando o InteractionSystem processa algo."""
        tipo = payload.get("tipo", "evento")
        params = payload.get("parametros", {})

        if tipo == "bau":
            self.log_mensagem(
                f"[yellow]📦 {params.get('mensagem', 'Você abriu um baú!')}[/]")
        elif tipo == "npc_dialogo":
            self.log_mensagem(f"[cyan]💬 NPC: {params.get('texto', 'Olá!')}[/]")
        else:
            self.log_mensagem(f"[white]✨ Evento ativado: {tipo}[/]")
            

    # ANTES DO ESPER
    # def ao_recolher_bau(self, dados):
    #     log = self.query_one("#area-interacao", RichLog)
    #     params = dados["parametros"]
    #     item_nome = params.get("item", "Moeda Antiga")
    #     qtd = params.get("quantidade", 1)
        
    #     # Injeta o item coletado no Inventário Lógico da Engine!
    #     inv = self.engine_manager.get_component(1, "InventoryComponent")
    #     if inv:
    #         inv.itens[item_nome] = inv.itens.get(item_nome, 0) + qtd
            
    #     self.log_mensagem(
    #         f"[bold cyan]🎁 Você abriu um baú e coletou: [yellow]{item_nome} x{qtd}[/yellow]! (Digite /equipar ou /usar no terminal para usufruir)[/]")
    #     self.atualizar_paineis_status()


    # def ao_levar_ataque(self, dados_ataque):
    #     log = self.query_one("#area-interacao", RichLog)
    #     dano = dados_ataque.get("mudar_hp", {}).get("valor", 1)
        
    #     stats = self.engine_manager.get_component(1, "StatsComponent")
    #     if stats:
    #         # Desconta o dano mitigado pela defesa real do personagem
    #         dano_real = max(1, dano - (stats.defesa_base // 3))
    #         stats.hp = max(0, stats.hp - dano_real)
    #         self.log_mensagem(
    #             f"[bold red]⚔️ O monstro atacou você! Sofreu {dano_real} de dano real (Defesa mitigou o resto).[/]")
            
    #         if stats.hp <= 0:
    #             self.log_mensagem(
    #                 "[bold background red]💀 VOCÊ MORREU! Fim de Jogo.[/]")
        
    #     self.atualizar_paineis_status()


    # ==========================================
    # INTERPRETADOR DE COMANDOS DO TERMINAL (SUBMIT INPUT)
    # ==========================================
    @on(Input.Submitted, "#terminal-prompt")
    def processar_comando_terminal(self, event: Input.Submitted):
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

        stats = self.engine_manager.get_component(1, "StatsComponent")
        inv = self.engine_manager.get_component(1, "InventoryComponent")
        eqp = self.engine_manager.get_component(1, "EquipmentComponent")

        # 🥤 COMANDO: /usar
        if comando == "/usar":
            if not argumento:
                log.write("[orange]Use: /usar <nome_do_item>[/]")
                return
            
            if inv and inv.itens.get(argumento, 0) > 0:
                if argumento == "poção" or argumento == "potion":
                    inv.itens[argumento] -= 1
                    stats.hp = min(stats.max_hp, stats.hp + 20) # Cura 20 de vida
                    log.write(f"[bold green]✨ Você tomou uma poção. Recuperou 20 PV![/]")
                else:
                    log.write(f"[orange]O item '{argumento}' não possui efeito de uso imediato.[/]")
            else:
                log.write(f"[red]Você não possui '{argumento}' no seu inventário.[/]")

        # ⚔️ COMANDO: /equipar
        elif comando == "/equipar":
            if not argumento:
                log.write("[orange]Use: /equipar <nome_da_arma_ou_armadura>[/]")
                return
                
            if inv and inv.itens.get(argumento, 0) > 0:
                # Simula um banco de dados de itens simples para conferir os bónus lógicos
                if "espada" in argumento:
                    bonus = 5 if "longa" in argumento else 3
                    eqp.arma = {"nome": argumento, "bonus_atk": bonus}
                    log.write(f"[bold blue]⚔️ Equipado com sucesso: {argumento.upper()} (+{bonus} ATK).[/]")
                elif "armadura" in argumento or "escudo" in argumento:
                    bonus = 6 if "placas" in argumento else 3
                    eqp.armadura = {"nome": argumento, "bonus_def": bonus}
                    log.write(f"[bold blue]🛡️ Equipado com sucesso: {argumento.upper()} (+{bonus} DEF).[/]")
                else:
                    log.write("[orange]Este item não pode ser equipado como arma ou armadura.[/]")
            else:
                log.write(f"[red]Você não possui o equipamento '{argumento}' no inventário.[/]")
        

        # Força a interface a recalcular e redesenhar os novos valores obtidos
        elif comando in ["/sair", "/q", "/exit", "/quit"]:
            self.app.pop_screen()
        else:
            log.write(f"[red]Comando desconhecido: '{comando}'. Tente /usar ou /equipar.[/]")
        
        #self.atualizar_paineis_status()

    # ==========================================
    # INPUTS DE MOVIMENTAÇÃO (MANTÉM O FOCO FORA DO PROMPT AO USAR SETAS)
    # ==========================================
    def on_key(self, event: Key) -> None:
        key = event.key
        moveu = False
        
        if key in ("up", "down", "left", "right", "w", "s", "a", "d"):
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
                return
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
        #self.atualizar_paineis_status()
        
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
    
    

    # ANTERIOR AO ESPER
    # def atualizar_visual_do_jogo(self):
    #     buffer_renderizado = self.render_sys.renderizar_frame(self.mapa_matriz, self.mapa_objetos)
    #     self.query_one("#tela-mapa", Static).update(buffer_renderizado)
        
    #     # Faz o scroll da câmara acompanhar o jogador no viewport
    #     viewport = self.query_one("#mapa-viewport", ScrollableContainer)
    #     pos_jogador = self.engine_manager.get_component(1, "PositionComponent")
    #     if pos_jogador and viewport.size.width > 0:
    #         alvo_x = (pos_jogador.x * 2) - (viewport.size.width // 2)
    #         alvo_y = pos_jogador.y - (viewport.size.height // 2)
    #         viewport.scroll_to(x=max(0, alvo_x), y=max(0, alvo_y), animate=False)
            
    @on(Input.Submitted, "#txt-chat")
    def ao_enviar_comando_chat(self, event: Input.Submitted):
        """Processa a caixa de comandos rápidos de texto."""
        texto = event.value.strip()
        if texto:
            self.log_mensagem(f"[bold white]Você:[/] {texto}")
            self.query_one("#txt-chat", Input).value = ""


    def atualizar_paineis_status(self):
        stats = self.engine_manager.get_component(1, "StatsComponent")
        inv = self.engine_manager.get_component(1, "InventoryComponent")
        eqp = self.engine_manager.get_component(1, "EquipmentComponent")

        if not stats: return

        # 🥊 MATEMÁTICA REAL DE EQUIPAMENTOS: Atributo Total = Base + Bónus do Equipamento
        bonus_atk = eqp.arma.get("bonus_atk", 0) if eqp and eqp.arma else 0
        bonus_def = eqp.armadura.get("bonus_def", 0) if eqp and eqp.armadura else 0
        
        atk_total = stats.ataque_base + bonus_atk
        def_total = stats.defesa_base + bonus_def

        # Atualiza Painel de Status
        self.query_one("#lbl-nome", Label).update(f"Nome: [bold green]{stats.nome}[/]")
        self.query_one("#lbl-pv", Label).update(f"PV: [bold red]{stats.hp} / {stats.max_hp}[/]")
        self.query_one("#lbl-pm", Label).update(f"PM: [bold blue]{stats.mp} / {stats.max_mp}[/]")
        self.query_one("#lbl-combate", Label).update(f"ATK: [yellow]{atk_total}[/] | DEF: [cyan]{def_total}[/]")

        # Atualiza Painel de Itens (Inventário)
        texto_inv = ""
        if inv and inv.itens:
            for nome_item, qtd in inv.itens.items():
                if qtd > 0:
                    texto_inv += f"• {nome_item.capitalize()} (x{qtd})\n"
        self.query_one("#lbl-inventario", Static).update(texto_inv if texto_inv else "Inventário Vazio")
