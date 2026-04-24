import sys
import io
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Select, Label, RichLog, DataTable
from textual.containers import Vertical, Horizontal, Center, Middle

from app.db.database import SessionLocal, engine, Base
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from app.controllers.game_controller import GameController, simular_arena
from app.core.emojis import dict_emoji_racas
from musics.audio_player import music

# Garante que as tabelas existem
Base.metadata.create_all(bind=engine)

# ==========================================
# ECRÃ 1: CRIAR PERSONAGEM
# ==========================================

class CreationScreen(Screen):
    def compose(self):
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("🛡️ Escolha o que Criar 🛡️", id="main-title")
                yield Button("🧝 Criar Raça", id="menu-create-raca", variant="success")
                yield Button("🤺 Criar Classe", id="menu-create-classe", variant="primary")
                yield Button("👤 Criar Personagem", id="menu-create-person", variant="success")
                yield Button("💍 Criar Item", id="menu-create-item", variant="primary")
                yield Button("🗡️ Equipar Personagem", id="menu-equip", variant="success")
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
                
        yield Footer()
        
    def _on_mount(self, event):
        return super()._on_mount(event)
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "menu-create-raca":
            self.app.push_screen(CreateRacaScreen())
        elif event.button.id == "menu-create-classe":
            self.app.push_screen(CreateClasseScreen())
        elif event.button.id == "menu-create-person":
            self.app.push_screen(CreateCharacterScreen())
        elif event.button.id == "menu-equip":
            self.app.push_screen(EquipScreen())
            
            
class CreateClasseScreen(Screen):
    def __init__(self):
        super().__init__()
        self.caminhos_definidos = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Nova Classe", id="title")
                
                yield Input(placeholder="Nome da Classe", id="inp-nome")
                
                yield Vertical(
                    Label("✨ Bônus de Caminhos (Ex: 'Fogo': 2, 'Água': 1):"),
                    Select([], prompt="Selecione um Caminho", id="sel-caminho"),
                    Input(placeholder="Pontos no Caminho", id="inp-caminho"),
                    Button("Adicionar", variant="success", id="btn-add-caminho"),
                )
                yield Label(f"Caminhos definidos: {self.caminhos_definidos}", id="caminhos-definidos")
                yield Vertical(
                    Label("Habilidades (Ex: 'Ataque Furtivo, Magia Arcana'):"),
                    Input(placeholder="Habilidades (Ex: 'Ataque Furtivo, Magia Arcana')", id="inp-habilidades")
                )
                yield Horizontal(
                    Button("Salvar", variant="success", id="btn-save"),
                    Button("Cancelar", variant="error", id="btn-cancel")
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()
        
    def on_mount(self):
        caminhos = ["Fogo", "Água", "Terra", "Ar", "Luz", "Trevas"]
        self.query_one("#sel-caminho").set_options([(c, c) for c in caminhos])
        self.caminhos_definidos = {}
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-add-caminho":
            caminho = self.query_one("#sel-caminho").value
            pontos = self.query_one("#inp-caminho").value
            if caminho and pontos:
                self.caminhos_definidos[caminho] = int(pontos)
                self.query_one("#caminhos-definidos").update(f"Caminhos definidos: {self.caminhos_definidos}")
                self.query_one("#inp-caminho").value = ""
        elif event.button.id == "btn-save":
            try:
                db = SessionLocal()
                nova_classe = ClasseRPGDB(
                    nome=self.query_one("#inp-nome").value,
                    bonus_caminhos=self.caminhos_definidos,
                    habilidades=[h.strip() for h in self.query_one("#inp-habilidades").value.split(",") if h.strip()]
                )
                db.add(nova_classe)
                db.commit()
                db.close()
                self.notify("Classe criada e salva no banco de dados com sucesso!", title="Sucesso", severity="information")
                self.app.pop_screen()
            except Exception as e:
                self.notify(f"Erro ao criar! {e}", severity="error")
        elif event.button.id == "btn-cancel":
            self.app.pop_screen()
                

class CreateRacaScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Nova Raça", id="title")
                
                yield Input(placeholder="Nome da Raça", id="inp-nome")
                yield Horizontal(
                 Input(placeholder="Força", id="inp-for"),
                 Input(placeholder="Agilidade", id="inp-agi"),
                 Input(placeholder="Resistência", id="inp-res"),
                 Input(placeholder="Percepção", id="inp-per"),
                 Input(placeholder="Exuberância", id="inp-exu"),
                 id="attr-inputs"
                )
                yield Select([], prompt="Selecione um emoji", id="sel-emoji")
                yield Horizontal(
                    Button("Salvar", variant="success", id="btn-save"),
                    Button("Cancelar", variant="error", id="btn-cancel")
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()
        
    def on_mount(self):
        emojis = [(f'{name}: {emoji}', emoji) for name, emoji in dict_emoji_racas.items()]
        self.query_one("#sel-emoji").set_options(emojis)
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            try:
                db = SessionLocal()
                atributos = {
                    "forca": int(self.query_one("#inp-for").value),
                    "agilidade": int(self.query_one("#inp-agi").value),
                    "resistencia": int(self.query_one("#inp-res").value),
                    "percepcao": int(self.query_one("#inp-per").value),
                    "exuberancia": int(self.query_one("#inp-exu").value)
                }
                nova_raca = RacaDB(
                    nome=self.query_one("#inp-nome").value,
                    bonus_atributos=atributos,
                    emoji=self.query_one("#sel-emoji").value
                )
                db.add(nova_raca)
                db.commit()
                db.close()
                self.notify("Raça criada e salva no banco de dados com sucesso!", title="Sucesso", severity="information")
                self.app.pop_screen()
            except Exception as e:
                self.notify("Erro ao criar! Verifique se preencheu todos os campos numéricos.", severity="error")
        



class CreateCharacterScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Novo Herói", id="title")
                yield Input(placeholder="Nome do Personagem", id="inp-nome")
                yield Select([], prompt="Selecione a Raça", id="sel-raca")
                yield Select([], prompt="Selecione a Classe", id="sel-classe")
                yield Label("Atributos Base (0 a 5):")
                yield Horizontal(
                    Input(placeholder="For", id="inp-for"),
                    Input(placeholder="Agi", id="inp-agi"),
                    Input(placeholder="Res", id="inp-res"),
                    Input(placeholder="Per", id="inp-per"),
                    Input(placeholder="Exu", id="inp-exu"),
                    id="attr-inputs"
                )
                yield Horizontal(
                    Button("Salvar", variant="success", id="btn-save"),
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()

    def on_mount(self):
        db = SessionLocal()
        racas = db.query(RacaDB).all()
        classes = db.query(ClasseRPGDB).all()
        self.query_one("#sel-raca").set_options([(r.nome, r.id) for r in racas])
        self.query_one("#sel-classe").set_options([(c.nome, c.id) for c in classes])
        db.close()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            try:
                db = SessionLocal()
                novo_char = PersonagemDB(
                    nome=self.query_one("#inp-nome").value,
                    raca_id=self.query_one("#sel-raca").value,
                    classe_id=self.query_one("#sel-classe").value,
                    forca_base=int(self.query_one("#inp-for").value),
                    agilidade_base=int(self.query_one("#inp-agi").value),
                    resistencia_base=int(self.query_one("#inp-res").value),
                    percepcao_base=int(self.query_one("#inp-per").value),
                    exuberancia_base=int(self.query_one("#inp-exu").value)
                )
                db.add(novo_char)
                db.commit()
                db.close()
                self.notify("Personagem forjado com sucesso!", title="Sucesso", severity="information")
                self.app.pop_screen()
            except Exception as e:
                self.notify("Erro ao criar! Verifique se preencheu todos os campos numéricos.", severity="error")

# ==========================================
# ECRÃ 2: EQUIPAR PERSONAGEM
# ==========================================
class EquipScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="equip-dialog"):
                yield Label("🗡️ Armaria e Equipamentos", id="title")
                yield Select([], prompt="Selecione o Personagem", id="sel-char")
                yield Select([], prompt="Selecione o Item", id="sel-item")
                yield Select([
                    ("Mão Direita (Arma)", "direita"), 
                    ("Mão Esquerda (Escudo/Arma)", "esquerda"), 
                    ("Corpo (Armadura)", "armadura")
                ], prompt="Selecione o Slot", id="sel-slot")
                
                yield Horizontal(
                    Button("Equipar", variant="success", id="btn-equip"),
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()

    def on_mount(self):
        db = SessionLocal()
        chars = db.query(PersonagemDB).all()
        itens = db.query(ItemDB).all()
        self.query_one("#sel-char").set_options([(p.nome, p.id) for p in chars])
        self.query_one("#sel-item").set_options([(f"{i.nome} ({i.categoria})", i.id) for i in itens])
        db.close()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-equip":
            char_id = self.query_one("#sel-char").value
            item_id = self.query_one("#sel-item").value
            slot = self.query_one("#sel-slot").value
            
            if not all([char_id, item_id, slot]):
                self.notify("Preencha todos os campos!", severity="warning")
                return

            db = SessionLocal()
            ctrl = GameController(db)
            try:
                msg = ctrl.equipar_item(char_id, item_id, slot)
                self.notify(msg, title="Sucesso")
                self.app.pop_screen()
            except Exception as e:
                self.notify(str(e), severity="error")
            finally:
                db.close()

# ==========================================
# ECRÃ 3: ARENA DE SIMULAÇÃO
# ==========================================
class ArenaScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="arena-sidebar"):
                yield Label("⚔️ Configurar Batalha", id="title")
                yield DataTable(id="char-table")
                yield Input(placeholder="IDs Aliados (Ex: 1, 2)", id="inp-aliados")
                yield Input(placeholder="IDs Oponentes (Ex: 3, 4)", id="inp-oponentes")
                yield Input(placeholder="Quantidade de Batalhas", value="1", id="inp-qtd")
                yield Horizontal(
                    Button("Simular", variant="warning", id="btn-simular"),
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
            with Vertical(id="arena-log-container"):
                yield RichLog(id="arena-log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Nome", "Lvl", "Raça", "Classe")
        db = SessionLocal()
        for p in db.query(PersonagemDB).all():
            table.add_row(str(p.id), p.nome, str(p.nivel), p.raca.nome, p.classe.nome)
        db.close()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return
            
        aliados_str = self.query_one("#inp-aliados").value
        oponentes_str = self.query_one("#inp-oponentes").value
        qtd = int(self.query_one("#inp-qtd").value)
        
        if not aliados_str or not oponentes_str:
            self.notify("Preencha os IDs dos lutadores!", severity="error")
            return

        aliados = [int(x.strip()) for x in aliados_str.split(",")]
        oponentes = [int(x.strip()) for x in oponentes_str.split(",")]
        
        db = SessionLocal()
        ctrl = GameController(db)
        log_widget = self.query_one(RichLog)
        log_widget.clear()

        # Magia do Python: Redireciona o "print" do controlador para o nosso RichLog da interface
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            resultado = simular_arena(db, aliados, oponentes, qtd)
        except Exception as e:
            log_widget.write(f"[red]Erro na simulação: {e}[/red]")
            return
        finally:
            sys.stdout = old_stdout # Restaura o print normal
            db.close()

        # Escreve o texto capturado no painel visual
        log_widget.write(new_stdout.getvalue())

        # Exibe o resumo no final se forem múltiplas batalhas
        if qtd > 1:
            log_widget.write("\n[bold yellow]📊 ESTATÍSTICAS FINAIS[/bold yellow]")
            log_widget.write(f"Vitórias Aliados: {resultado['vitorias_aliados']}")
            log_widget.write(f"Vitórias Oponentes: {resultado['vitorias_oponentes']}")

# ==========================================
# ECRÃ PRINCIPAL (MENU APP)
# ==========================================
class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="main-menu"):
                yield Label("🛡️  SIS-CHARLES RPG 🛡️", id="main-title")
                yield Button("✨ Criação", id="menu-create", variant="success")
                yield Button("⚔️  Entrar na Arena", id="menu-arena", variant="warning")
                yield Button("❌ Sair do Sistema", id="menu-quit", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "menu-create": self.app.push_screen(CreationScreen())
        elif btn_id == "menu-arena": self.app.push_screen(ArenaScreen())
        elif btn_id == "menu-quit": self.app.exit()

# ==========================================
# CONFIGURAÇÃO DE ESTILOS E LANÇAMENTO
# ==========================================
class RPGApp(App):
    CSS = """
    Screen { align: center middle; background: $background; }
    
    #main-menu { width: 45; padding: 2; border: tall $accent; background: $surface; }
    #main-title { width: 100%; text-align: center; text-style: bold; margin-bottom: 2; color: $secondary; }
    Button { width: 100%; margin-bottom: 1; }
    
    #create-dialog, #equip-dialog { width: 60; padding: 2; border: tall $primary; background: $surface; }
    #title { width: 100%; text-align: center; text-style: bold; margin-bottom: 1; color: $warning; }
    
    #attr-inputs > Input { width: 1fr; margin-right: 1; }
    
    #arena-sidebar { width: 45; padding: 1; border-right: vkey $accent; background: $surface; height: 100%; }
    #arena-log-container { width: 1fr; padding: 1; height: 100%; }
    #char-table { height: 1fr; margin-bottom: 1; border: round $primary; }
    """
    
    BINDINGS = [("d", "toggle_dark", "Mudar Tema Escuro/Claro"), ("q", "quit", "Sair")]

    def on_mount(self):
        self.push_screen(MainScreen())

if __name__ == "__main__":
    #music = Playback()
    #music.load_file('musics/Animals_House_Of_The_Rising_Sun1.wav')
    #music.loop_at_end(True)
    
    music.play()
    
    app = RPGApp()
    app.run()