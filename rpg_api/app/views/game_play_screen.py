# # app/views/game_play_screen.py (ou rpg_api/game_play_screen.py)

# from textual.screen import Screen
# from textual.widgets import Static, RichLog, Label
# from textual.containers import Container
# from textual import on
# from textual.events import Key

# # Imports do nosso ecossistema robusto
# from app.core.engine.event_bus import EventBus
# from app.core.engine.systems import MovementSystem, InteractionSystem
# from app.core.engine.render import RenderSystem
# from app.core.engine.components import PositionComponent, CollisionComponent, InteractableComponent
# from app.core.emojis import CatalogoTiles


# # app/views/game_play_screen.py
from textual.screen import Screen
from textual.widgets import Static, RichLog, Label
from textual.containers import Container
from textual.events import Key

from app.db.database import SessionLocal # Conexão autêntica com o banco
from app.core.emojis import CatalogoTiles
from app.core.engine.event_bus import EventBus
from app.core.engine.systems import MovementSystem, InteractionSystem
from app.core.engine.render import RenderSystem
from app.core.engine.engine_loader import carregar_engine_do_banco  # ✅ NOSSO CARREGADOR REAL!

class GamePlayScreen(Screen):
    CSS_PATH = "game_styles.css"
    
    def __init__(self, mapa_id: int):
        super().__init__()
        self.mapa_id = mapa_id
        self.event_bus = EventBus()
        
        # Referências da Engine Real
        self.engine_manager = None
        self.mapa_matriz = None
        self.mapa_objetos = {}
        
        # Sistemas Ativos
        self.movimento_sys = None
        self.interacao_sys = None
        self.render_sys = None

    def compose(self):
         with Container(id="game-layout"):
            yield Static("Carregando Cenário Lógico...", id="tela-mapa")
            
            with Container(id="tela-status"):
                yield Label("🐱‍👤 Status", classes="titulo-secao")
                yield Label("Jogador: [bold green]Mago[/]", id="lbl-nome")
                yield Label("Pv: 10 / Pm: 5", id="lbl-pv-pm")
                yield Label("Atk: 13 | Def: 9", id="lbl-status-combate")
                
            with Container(id="tela-itens"):
                yield Label("🎒 Itens", classes="titulo-secao")
                yield Static("- 3x Poção de Vida\n- 1x Chave de Bronze", id="lbl-inventario")
                
            # Área de interação (Terminal de mensagens)
            yield RichLog(id="area-interacao", markup=True)

    def on_mount(self):
        log = self.query_one("#area-interacao", RichLog)
        log.write("[bold green]>>> Lendo registros de campanha do Banco de Dados...[/]")
        
        try:
            # 🔌 CONEXÃO DE PRODUÇÃO: Puxa o mapa e eventos criados no editor!
            with SessionLocal() as db:
                self.engine_manager, self.mapa_matriz, self.mapa_objetos = carregar_engine_do_banco(
                    self.mapa_id, db
                )
            
            # Instanciação dos sistemas apontando para o ECS real e para a paleta global
            self.movimento_sys = MovementSystem(
                self.engine_manager, self.mapa_matriz, 
                tiles_bloqueio=CatalogoTiles.TERRENOS_BLOQUEANTES, dict_objetos=self.mapa_objetos
            )
            self.interacao_sys = InteractionSystem(self.engine_manager, self.event_bus)
            self.render_sys = RenderSystem(self.engine_manager)

            # Escuta os disparos lógicos da Engine
            self.event_bus.subscribe("bau", self.ao_encontrar_tesouro)
            self.event_bus.subscribe("npc_dialogo", self.ao_conversar_com_npc)

            log.write("[bold gold]>>> Sucesso! Engine carregada. Divirta-se![/]")
            self.atualizar_visual_do_jogo()

        except Exception as e:
            log.write(f"[bold red]❌ Erro ao inicializar engine do banco: {e}[/]")

    def ao_encontrar_tesouro(self, dados):
        log = self.query_one("#area-interacao", RichLog)
        item = dados["parameters"].get("item", "Ouro")
        log.write(f"[bold cyan]>>> [Interação] Você abriu o baú e pegou: {item}![/]")

    def ao_conversar_com_npc(self, dados):
        log = self.query_one("#area-interacao", RichLog)
        fala = dados["parameters"].get("texto", "...")
        log.write(f"[bold green]>>> NPC diz: \"{fala}\"[/]")

    def on_key(self, event: Key) -> None:
        chave = event.key
        moveu = False

        if chave == "up": moveu = self.movimento_sys.move_entity(1, 0, -1)
        elif chave == "down": moveu = self.movimento_sys.move_entity(1, 0, 1)
        elif chave == "left": moveu = self.movimento_sys.move_entity(1, -1, 0)
        elif chave == "right": moveu = self.movimento_sys.move_entity(1, 1, 0)
        elif chave == "enter":
            self.interacao_sys.interact(1)
            return

        if moveu:
            self.atualizar_visual_do_jogo()

    def atualizar_visual_do_jogo(self):
        buffer_renderizado = self.render_sys.renderizar_frame(self.mapa_matriz, self.mapa_objetos)
        self.query_one("#tela-mapa", Static).update(buffer_renderizado)



# class GamePlayScreen(Screen):
#     """A Interface ativa do jogo conectada à Engine Headless por Eventos."""
    
#     CSS_PATH = "game_styles.css"
    
#     def __init__(self, mapa_id: int):
#         super().__init__()
#         self.mapa_id = mapa_id
        
#         # Inicializa a infraestrutura lógica (Engine)
#         self.event_bus = EventBus()
#         self.engine_manager = None # No mundo real, você usará o seu ECSManager real carregado aqui
        
#         # Dados do mapa que virão do Banco de Dados
#         self.mapa_matriz = None
#         self.mapa_objetos = {}
        
#         # Sistemas lógicos
#         self.movimento_sys = None
#         self.interacao_sys = None
#         self.render_sys = None

#     def compose(self):
#         with Container(id="game-layout"):
#             yield Static("Carregando Cenário Lógico...", id="tela-mapa")
            
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
#         """Prepara o estado inicial do jogo, carrega dados e assina canais."""
#         log = self.query_one("#area-interacao", RichLog)
#         log.write("[bold yellow]>>> Sistema Inicializado.[/]")
        
#         # 1. SIMULAÇÃO DE CARREGAMENTO DO BANCO (Substitua pela sua query real do Banco)
#         # Vamos fingir que puxamos um mapa do banco de dados para o teste em tela
#         self.mapa_matriz = [
#             ["🔲", "🔲", "🔲", "🔲","🔲", "🔲", "🔲"],
#             ["🔲", "🟩", "🟩", "🟩", "🟩", "🟩", "🔲"],
#             ["🔲", "🟩", "🟩", "🟩", "🟩", "🟩", "🔲"],
#             ["🔲", "🟩", "🟩", "🟩", "🟩", "🟩", "🔲"],
#             ["🔲", "🟩", "🟩", "🟩", "🟩", "🟩", "🔲"],
#             ["🔲", "🟩", "🟩", "🟩", "🟩", "🟩", "🔲"],
#             ["🔲", "🔲", "🔲", "🔲", "🔲", "🔲", "🔲"]
#         ]
#         self.mapa_objetos = {(2, 2): "🌲"}
        
#         self.movimento_sys = MovementSystem(
#             self.engine_manager, 
#             self.mapa_matriz,
#             tiles_bloqueio=CatalogoTiles.TERRENOS_BLOQUEANTES, # ✅ O Motor recebe a lista de bloqueios dinamicamente!
#             dict_objetos=self.mapa_objetos
#         )
        
        
#         # 2. INSTANCIAÇÃO DO MOCK DO ECS MANAGER REAL (Integre com o seu MotorDeComponentes definitivo)
#         class MotorDeComponentes:
#             def __init__(self):
#                 self.entidades = {
#                     1: {"Position": PositionComponent(x=1, y=1, direcao_olhar="baixo")}, # Jogador
#                     2: { # Um baú de tesouro instanciado como evento lógico
#                         "Position": PositionComponent(x=3, y=2),
#                         "Collision": CollisionComponent(is_solid=True),
#                         "Interactable": InteractableComponent(event_type="bau", parameters={"item": "Cajado Arcano"})
#                     }
#                 }
#                 # Gambiarra para o Componente de Evento ter emoji (conforme o eventos_db.py)
#                 self.entidades[2]["Interactable"].emoji = "📦"
                
#             def get_component(self, e_id, name): return self.entidades.get(e_id, {}).get(name)
#             def get_entities_with(self, *names):
#                 return [e_id for e_id, comps in self.entidades.items() if all(n in comps for n in names)]

#         self.engine_manager = MotorDeComponentes()

#         self.interacao_sys = InteractionSystem(self.engine_manager, self.event_bus)


#         # 3. INSTANCIAÇÃO DOS SISTEMAS
#         self.movimento_sys = MovementSystem(self.engine_manager, self.mapa_matriz, tiles_bloqueio=CatalogoTiles.TERRENOS_BLOQUEANTES, # ✅ O Motor recebe a lista de bloqueios dinamicamente!
#             dict_objetos=self.mapa_objetos)
#         self.interacao_sys = InteractionSystem(self.engine_manager, self.event_bus)
#         self.render_sys = RenderSystem(self.engine_manager, emoji_jogador="🧙")

#         # 4. ASSINATURA DOS CANAIS DO EVENT BUS (A Interface escuta a Engine)
#         self.event_bus.subscribe("bau", self.ao_interagir_com_bau)
#         self.event_bus.subscribe("audio_trigger", self.tocar_efeito_sonoro)

#         # Desenha o primeiro frame do jogo na tela
#         self.atualizar_tela_mapa()

#     # ==========================================
#     # ASSINANTES (LISTENERS) DO EVENT BUS
#     # ==========================================
#     def ao_interagir_com_bau(self, dados_evento):
#         """Disparado via Event Bus quando a física/lógica aprova o Enter."""
#         item = dados_evento["parameters"].get("item", "Lixo")
#         log = self.query_one("#area-interacao", RichLog)
#         log.write(f"[bold cyan]>>> Você abriu um baú antigo e encontrou: [yellow]{item}[/]![/]")

#     def tocar_efeito_sonoro(self, dados):
#         # Gancho limpo para integrar o seu player de áudio (audio_player.py) sem sujar a engine!
#         pass

#     # ==========================================
#     # CONTROLADOR DE ENTRADAS (INPUT HANDLING)
#     # ==========================================
#     def on_key(self, event: Key) -> None:
#         """Capta as teclas pressionadas e encaminha a intenção para a Engine."""
#         chave = event.key
#         moveu = False

#         if chave == "up":
#             moveu = self.movimento_sys.move_entity(entity_id=1, dx=0, dy=-1)
#         elif chave == "down":
#             moveu = self.movimento_sys.move_entity(entity_id=1, dx=0, dy=1)
#         elif chave == "left":
#             moveu = self.movimento_sys.move_entity(entity_id=1, dx=-1, dy=0)
#         elif chave == "right":
#             moveu = self.movimento_sys.move_entity(entity_id=1, dx=1, dy=0)
#         elif chave == "enter":
#             # Dispara o raio de interação. Se bater no baú, o Event Bus vai gritar e chamar o método acima!
#             self.interacao_sys.interact(entity_id=1)
#             return

#         # Se o jogador se moveu com sucesso (aprovado pela física de colisão), atualiza o mapa visual
#         if moveu:
#             self.atualizar_tela_mapa()

#     def atualizar_tela_mapa(self):
#         """Pede ao Render System o frame atualizado e injeta no widget correspondente."""
#         buffer_visual = self.render_sys.renderizar_frame(self.mapa_matriz, self.mapa_objetos)
#         self.query_one("#tela-mapa", Static).update(buffer_visual)

