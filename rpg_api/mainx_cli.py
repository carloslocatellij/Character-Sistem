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

# Garante que as tabelas existem
Base.metadata.create_all(bind=engine)

# ==========================================
# ECRÃ 1: CRIAR PERSONAGEM
# ==========================================
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
                    Button("Cancelar", variant="error", id="btn-cancel")
                )
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
                    Button("Cancelar", variant="error", id="btn-cancel")
                )
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
                    Button("Voltar", variant="error", id="btn-cancel")
                )
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
                yield Label("🛡️ SIS-CHARLES RPG 🛡️", id="main-title")
                yield Button("👤 Criar Personagem", id="menu-create", variant="primary")
                yield Button("🗡️ Equipar Personagem", id="menu-equip", variant="primary")
                yield Button("⚔️ Entrar na Arena", id="menu-arena", variant="warning")
                yield Button("❌ Sair do Sistema", id="menu-quit", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "menu-create": self.app.push_screen(CreateCharacterScreen())
        elif btn_id == "menu-equip": self.app.push_screen(EquipScreen())
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
    app = RPGApp()
    app.run()