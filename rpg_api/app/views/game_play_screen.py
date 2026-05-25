# app/views/game_play_screen.py
from textual.screen import Screen
from textual.widgets import Static, RichLog, Label, Input
from textual.containers import Container, ScrollableContainer
from textual.events import Key
from textual import on

from app.db.database import SessionLocal
from app.core.emojis import CatalogoTiles
from app.core.engine.event_bus import EventBus
from app.core.engine.systems import MovementSystem, InteractionSystem, AISystem
from app.core.engine.render import RenderSystem
from app.core.engine.engine_loader import carregar_engine_do_banco

class GamePlayScreen(Screen):
    CSS_PATH = "game_styles.tcss"
    
    def __init__(self, mapa_id: int, personagem_id: int = 1): # Recebe mapa e herói reais
        super().__init__()
        self.mapa_id = mapa_id
        self.personagem_id = personagem_id
        self.event_bus = EventBus()
        
        self.engine_manager = None
        self.mapa_matriz = None
        self.mapa_objetos = {}
        
        self.movimento_sys = None
        self.interacao_sys = None
        self.ai_sys = None
        self.render_sys = None

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
        log = self.query_one("#area-interacao", RichLog)
        log.write("[bold yellow]>>> Inicializando sistemas de campanha...[/]")
        
        try:
            with SessionLocal() as db:
                # Carregamento autêntico sem simulações!
                self.engine_manager, self.mapa_matriz, self.mapa_objetos = carregar_engine_do_banco(
                    self.mapa_id, self.personagem_id, db
                )
            
            self.movimento_sys = MovementSystem(self.engine_manager, self.mapa_matriz, CatalogoTiles.TERRENOS_BLOQUEANTES, self.mapa_objetos)
            self.interacao_sys = InteractionSystem(self.engine_manager, self.event_bus)
            self.render_sys = RenderSystem(self.engine_manager)
            self.ai_sys = AISystem(self.engine_manager, self.movimento_sys, self.event_bus)

            # Assina eventos globais da rádio lúdica
            self.event_bus.subscribe("bau", self.ao_recolher_bau)
            self.event_bus.subscribe("ataque_monstro", self.ao_levar_ataque)

            # Batimento dos monstros autónomos a cada 1 segundo
            self.set_interval(1.0, self.game_tick)

            log.write("[bold green]>>> Engine Pronta! Use setas para andar, ENTER para interagir ou use o Terminal de comandos abaixo.[/]")
            self.atualizar_tudo()

        except Exception as e:
            log.write(f"[bold red]❌ Erro crítico: {e}[/]")

    def game_tick(self):
        if self.ai_sys:
            self.ai_sys.update()
            self.atualizar_visual_do_jogo()

    # ==========================================
    # EVENTOS DA ENGINE
    # ==========================================
    def ao_recolher_bau(self, dados):
        log = self.query_one("#area-interacao", RichLog)
        params = dados["parameters"]
        item_nome = params.get("item", "Moeda Antiga")
        qtd = params.get("quantidade", 1)
        
        # Injeta o item coletado no Inventário Lógico da Engine!
        inv = self.engine_manager.get_component(1, "InventoryComponent")
        if inv:
            inv.itens[item_nome] = inv.itens.get(item_nome, 0) + qtd
            
        log.write(f"[bold cyan]🎁 Você abriu um baú e coletou: [yellow]{item_nome} x{qtd}[/yellow]! (Digite /equipar ou /usar no terminal para usufruir)[/]")
        self.atualizar_paineis_status()

    def ao_levar_ataque(self, dados_ataque):
        log = self.query_one("#area-interacao", RichLog)
        dano = dados_ataque.get("mudar_hp", {}).get("valor", 1)
        
        stats = self.engine_manager.get_component(1, "StatsComponent")
        if stats:
            # Desconta o dano mitigado pela defesa real do personagem
            dano_real = max(1, dano - (stats.defesa_base // 3))
            stats.hp = max(0, stats.hp - dano_real)
            log.write(f"[bold red]⚔️ O monstro atacou você! Sofreu {dano_real} de dano real (Defesa mitigou o resto).[/]")
            
            if stats.hp <= 0:
                log.write("[bold background red]💀 VOCÊ MORREU! Fim de Jogo.[/]")
        
        self.atualizar_paineis_status()

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

        log.write(f"[dim]>>> {texto}[/]") # Mostra o comando ecoado no log

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
        
        else:
            log.write(f"[red]Comando desconhecido: '{comando}'. Tente /usar ou /equipar.[/]")

        # Força a interface a recalcular e redesenhar os novos valores obtidos
        self.atualizar_paineis_status()

    # ==========================================
    # INPUTS DE MOVIMENTAÇÃO (MANTÉM O FOCO FORA DO PROMPT AO USAR SETAS)
    # ==========================================
    def on_key(self, event: Key) -> None:
        chave = event.key
        moveu = False

        if chave == "up": moveu = self.movimento_sys.move_entity(1, 0, -1)
        elif chave == "down": moveu = self.movimento_sys.move_entity(1, 0, 1)
        elif chave == "left": moveu = self.movimento_sys.move_entity(1, -1, 0)
        elif chave == "right": moveu = self.movimento_sys.move_entity(1, 1, 0)
        elif chave == "enter":
            # Se o foco estiver no prompt do terminal, deixa o submit do input agir e ignora o raio
            if self.focused == self.query_one("#terminal-prompt"):
                return
            self.interacao_sys.interact(1)
            return

        if moveu:
            self.atualizar_visual_do_jogo()

    # ==========================================
    # REDESENHO DE TELAS E RECALCULO DE ATRIBUTOS + EQUIPAMENTOS
    # ==========================================
    def atualizar_tudo(self):
        self.atualizar_visual_do_jogo()
        self.atualizar_paineis_status()

    def atualizar_visual_do_jogo(self):
        buffer_renderizado = self.render_sys.renderizar_frame(self.mapa_matriz, self.mapa_objetos)
        self.query_one("#tela-mapa", Static).update(buffer_renderizado)
        
        # Faz o scroll da câmara acompanhar o jogador no viewport
        viewport = self.query_one("#mapa-viewport", ScrollableContainer)
        pos_jogador = self.engine_manager.get_component(1, "PositionComponent")
        if pos_jogador and viewport.size.width > 0:
            alvo_x = (pos_jogador.x * 2) - (viewport.size.width // 2)
            alvo_y = pos_jogador.y - (viewport.size.height // 2)
            viewport.scroll_to(x=max(0, alvo_x), y=max(0, alvo_y), animate=False)

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

# from textual.screen import Screen
# from textual.widgets import Static, RichLog, Label
# from textual.containers import Container, ScrollableContainer
# from textual.events import Key

# from app.db.database import SessionLocal # Conexão autêntica com o banco
# from app.core.emojis import CatalogoTiles
# from app.core.engine.event_bus import EventBus
# from app.core.engine.systems import MovementSystem, InteractionSystem, AISystem
# from app.core.engine.render import RenderSystem
# from app.core.engine.engine_loader import carregar_engine_do_banco  # ✅ NOSSO CARREGADOR REAL!

# class GamePlayScreen(Screen):
#     from app.core.engine.systems import AISystem
# # ...
#     CSS_PATH = "game_styles.css"
    
#     def __init__(self, mapa_id: int):
#         super().__init__()
#         self.mapa_id = mapa_id
#         self.event_bus = EventBus()
        
#         # Referências da Engine Real
#         self.engine_manager = None
#         self.mapa_matriz = None
#         self.mapa_objetos = {}
        
#         # Sistemas Ativos
#         self.movimento_sys = None
#         self.interacao_sys = None
#         self.render_sys = None
#         self.ai_sys = None  

#     def compose(self):
#          with Container(id="game-layout"):
#             with ScrollableContainer(id="mapa-viewport"):
#                 # O parâmetro expand=True diz ao Static para abraçar todo o texto gerado
#                 yield Static("Carregando Cenário Lógico...", id="tela-mapa", expand=True)
            
#             with Container(id="tela-status"):
#                 yield Label("🐱‍👤 Status", classes="titulo-secao")
#                 yield Label("Jogador: [bold green]Mago[/]", id="lbl-nome")
#                 yield Label("Pv: 10 / Pm: 5", id="lbl-pv-pm")
#                 yield Label("Atk: 13 | Def: 9", id="lbl-status-combate")
                
#             with Container(id="tela-itens"):
#                 yield Label("🎒 Itens", classes="titulo-secao")
#                 yield Static("- 3x Poção de Vida\n- 1x Chave de Bronze", id="lbl-inventario")
                
#             # Área de interação (Terminal de mensagens)
#             yield RichLog(id="area-interacao", markup=True)

#     def on_mount(self):
#         log = self.query_one("#area-interacao", RichLog)
#         log.write("[bold green]>>> Lendo registros de campanha do Banco de Dados...[/]")
        
#         try:
#             # 🔌 CONEXÃO DE PRODUÇÃO: Puxa o mapa e eventos criados no editor!
#             with SessionLocal() as db:
#                 self.engine_manager, self.mapa_matriz, self.mapa_objetos = carregar_engine_do_banco(
#                     self.mapa_id, db
#                 )
            
#             # Instanciação dos sistemas apontando para o engine real e para a paleta global
#             self.movimento_sys = MovementSystem(
#                 self.engine_manager, self.mapa_matriz, 
#                 tiles_bloqueio=CatalogoTiles.TERRENOS_BLOQUEANTES, dict_objetos=self.mapa_objetos
#             )
#             self.interacao_sys = InteractionSystem(self.engine_manager, self.event_bus)
#             self.render_sys = RenderSystem(self.engine_manager)

#             self.ai_sys = AISystem(self.engine_manager, self.movimento_sys, self.event_bus)
            
#             # Escuta os disparos lógicos da Engine
#             self.event_bus.subscribe("bau", self.ao_encontrar_tesouro)
#             self.event_bus.subscribe("npc_dialogo", self.ao_conversar_com_npc)

#             log.write("[bold gold]>>> Sucesso! Engine carregada. Divirta-se![/]")
            
#             self.set_interval(0.2, self.game_tick)
#             self.event_bus.subscribe("ataque_monstro", self.ao_sofrer_ataque)
            
#             self.atualizar_visual_do_jogo()

#         except Exception as e:
#             log.write(f"[bold red]❌ Erro ao inicializar engine do banco: {e}[/]")

#     def ao_encontrar_tesouro(self, dados):
#         log = self.query_one("#area-interacao", RichLog)
#         item = dados["parameters"].get("item", "Ouro")
#         log.write(f"[bold cyan]>>> [Interação] Você abriu o baú e pegou: {item}![/]")

#     def ao_conversar_com_npc(self, dados):
#         log = self.query_one("#area-interacao", RichLog)
#         fala = dados["parameters"].get("texto", "...")
#         log.write(f"[bold green]>>> NPC diz: \"{fala}\"[/]")

#     def on_key(self, event: Key) -> None:
#         chave = event.key
#         moveu = False

#         if chave == "up": moveu = self.movimento_sys.move_entity(1, 0, -1)
#         elif chave == "down": moveu = self.movimento_sys.move_entity(1, 0, 1)
#         elif chave == "left": moveu = self.movimento_sys.move_entity(1, -1, 0)
#         elif chave == "right": moveu = self.movimento_sys.move_entity(1, 1, 0)
#         elif chave == "enter":
#             self.interacao_sys.interact(1)
#             return

#         if moveu:
#             self.atualizar_visual_do_jogo()

#     def atualizar_visual_do_jogo(self):
#         """Renderiza o mapa e move a câmara (scroll) para seguir o jogador."""
#         buffer_renderizado = self.render_sys.renderizar_frame(self.mapa_matriz, self.mapa_objetos)
        
#         # Atualiza a string do mapa
#         mapa_widget = self.query_one("#tela-mapa", Static)
#         mapa_widget.update(buffer_renderizado)
        
#         # ✅ CORREÇÃO: Puxamos a Janela (Viewport) para calcular a câmara
#         viewport = self.query_one("#mapa-viewport", ScrollableContainer)
        
#         pos_jogador = self.engine_manager.get_component(1, "PositionComponent")
        
#         if pos_jogador:
#             # Usamos o tamanho do Viewport para centrar
#             largura_tela = viewport.size.width
#             altura_tela = viewport.size.height
            
#             # Como emojis ocupam 2 espaços visuais, X é multiplicado por 2
#             pos_x_visual = pos_jogador.x * 2
#             pos_y_visual = pos_jogador.y
            
#             # Subtraímos metade do viewport para manter o jogador no centro
#             alvo_x = pos_x_visual - (largura_tela // 2)
#             alvo_y = pos_y_visual - (altura_tela // 2)
            
#             alvo_x = max(0, alvo_x)
#             alvo_y = max(0, alvo_y)
            
#             # Fazemos o scroll na Janela (Viewport)
#             viewport.scroll_to(x=alvo_x, y=alvo_y, animate=False)
    
#     def game_tick(self):
#         """O batimento cardíaco da Engine. Faz o mundo mover-se independentemente do jogador."""
#         if self.ai_sys:
#             self.ai_sys.update()
#             # Atualiza o visual para vermos os monstros andarem!
#             self.atualizar_visual_do_jogo()

#     def ao_sofrer_ataque(self, dados_ataque):
#         log = self.query_one("#area-interacao", RichLog)
#         alvo = dados_ataque.get("alvo", "desconhecido")
#         dano = dados_ataque.get("mudar_hp", {}).get("valor", 0)
#         log.write(f"[bold red]⚔️ Um monstro bateu no {alvo}! Sofreu {dano} de dano![/]")