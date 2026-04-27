import sys
import io
import logging
# Configuração básica
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Select, Label, RichLog, DataTable
from textual.containers import Vertical, Horizontal, Center, Middle
from textual import on
from app.db.database import SessionLocal, engine, Base
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from app.controllers.game_controller import GameController, simular_arena
from app.core.emojis import dict_emoji_racas, dict_item_emoji
from musics.audio_player import music

# Garante que as tabelas existem
Base.metadata.create_all(bind=engine)

def action_start_stop_music():
        if music.active:
            music.stop()
        else:
            music.play()
            
            
# ==========================================           
# Funções de edição e salvamento
# ==========================================

map_entidades = {"Personagem": PersonagemDB, "Raça": RacaDB, "Classe": ClasseRPGDB, "Item": ItemDB}

def salvar_edicao(id_entity: int, dados: dict, modelo):
    modelo = map_entidades.get(modelo)
    with SessionLocal() as db:
        ctrl = GameController(db)
        ctrl.atualizar_elemento(modelo, id_entity, dados)


def salvar_novo(dados: dict, modelo):
    modelo = map_entidades.get(modelo)
    with SessionLocal() as db:
        novo_elemento = modelo(**dados)
        db.add(novo_elemento)
        db.commit()
        return novo_elemento


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
            self.app.push_screen(RacaFormScreen())
        elif event.button.id == "menu-create-classe":
            self.app.push_screen(ClasseFormScreen())
        elif event.button.id == "menu-create-person":
            self.app.push_screen(CharacterFormScreen())
        elif event.button.id == "menu-equip":
            self.app.push_screen(EquipScreen())
        elif event.button.id == "menu-create-item":
            self.app.push_screen(ItemFormScreen())
            
            
class ClasseFormScreen(Screen):
    def __init__(self, classe_id: int = None):
        super().__init__()
        self.caminhos_definidos = {}
        self.classe_id = classe_id 

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Nova Classe", id="title")
                
                yield Input(placeholder="Nome da Classe", id="inp-nome")
                
                yield Label("✨ Bônus de Caminhos (Ex: 'Fogo': 2, 'Água': 1):")
                
                with Horizontal():
                    yield Select([], prompt="Selecione um Caminho", id="sel-caminho")
                with Horizontal():
                    yield Input(placeholder="Pontos no Caminho", id="inp-caminho")
                
                yield Vertical(
                        Button("Adicionar", variant="success", id="btn-add-caminho"),
                        Label(f"Caminhos definidos: {self.caminhos_definidos}", id="caminhos-definidos"),
                        id="caminhos-add",
                    )
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
        if self.classe_id:
            db = SessionLocal()
            classe = db.query(ClasseRPGDB).get(self.classe_id)
            if classe:
                self.query_one("#inp-nome").value = classe.nome
                self.caminhos_definidos = classe.bonus_caminhos
                self.query_one("#caminhos-definidos").update(f"Caminhos definidos: {self.caminhos_definidos}")
                self.query_one("#inp-habilidades").value = ", ".join(classe.habilidades)
                caminhos = ["Fogo", "Água", "Terra", "Ar", "Luz", "Trevas"]
                self.query_one("#sel-caminho").set_options([(c, c) for c in caminhos])
            db.close()
        else:
            caminhos = ["Fogo", "Água", "Terra", "Ar", "Luz", "Trevas"]
            self.query_one("#sel-caminho").set_options([(c, c) for c in caminhos])
            self.caminhos_definidos = {}
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-add-caminho":
            caminho = self.query_one("#sel-caminho").value
            pontos = self.query_one("#inp-caminho").value
            if caminho and pontos:
                self.caminhos_definidos[caminho] = int(pontos)
                self.query_one("#caminhos-definidos").update(f"Caminhos definidos: {self.caminhos_definidos}")
                self.query_one("#inp-caminho").value = ""
        elif event.button.id == "btn-save":
            try:
                dados = dict(nome=self.query_one("#inp-nome").value,
                            bonus_caminhos=self.caminhos_definidos,
                            habilidades=[h.strip() for h in self.query_one("#inp-habilidades").value.split(",") if h.strip()])
                if self.classe_id:
                    salvar_edicao(self.classe_id, dados, "Classe")
                    self.notify("Classe criada e salva no banco de dados com sucesso!", title="Sucesso", severity="information")
                else:
                    salvar_novo(dados, "Classe")
                    
                self.app.pop_screen()
            except Exception as e:
                self.notify(f"Erro ao criar/atualizar! {e}", severity="error")
                

class RacaFormScreen(Screen):
    def __init__(self, raca_id: int = None):
        super().__init__()
        self.raca_id = raca_id  # Se for None, é Novo. Se tiver ID, é Edição
        
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
                yield Input(placeholder="Selecione um emoji", id="inp-emoji")
                yield Horizontal(
                    Button("Salvar", variant="success", id="btn-save"),
                    Button("Cancelar", variant="error", id="btn-cancel")
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()
        
    def on_mount(self):
        if self.raca_id:
            db = SessionLocal()
            raca = db.query(RacaDB).get(self.raca_id)
            if raca:
                print(raca.emoji)
                self.query_one("#inp-nome").value = raca.nome
                self.query_one("#inp-for").value = str(raca.bonus_atributos.get('forca', 0))
                self.query_one("#inp-agi").value = str(raca.bonus_atributos.get('agilidade', 0))
                self.query_one("#inp-res").value = str(raca.bonus_atributos.get('resistencia', 0))
                self.query_one("#inp-per").value = str(raca.bonus_atributos.get('percepcao', 0))
                self.query_one("#inp-exu").value = str(raca.bonus_atributos.get('exuberancia', 0))
                #logging.info(f"O valor do select antes: {self.query_one("#inp-emoji").value}")
                #logging.info(f"O emoji: [{raca.emoji}] ")
                self.query_one("#inp-emoji").value =  str(raca.emoji)
                #logging.info(f"O valor do select depois: {self.query_one("#inp-emoji").value}")
            db.close()
        
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            try:
                atributos = {
                    "forca": int(self.query_one("#inp-for").value),
                    "agilidade": int(self.query_one("#inp-agi").value),
                    "resistencia": int(self.query_one("#inp-res").value),
                    "percepcao": int(self.query_one("#inp-per").value),
                    "exuberancia": int(self.query_one("#inp-exu").value)
                            }
                dados = dict(nome=self.query_one("#inp-nome").value,
                            bonus_atributos=atributos,
                            emoji=self.query_one("#inp-emoji").value)
                if self.raca_id:
                    salvar_edicao(self.raca_id, dados, "Raça")
                    self.notify("Raça criada e salva no banco de dados com sucesso!", title="Sucesso", severity="information")
                else:
                    salvar_novo(dados, "Raça")
                self.app.pop_screen()
            except Exception as e:
                self.notify("Erro ao criar/atualizar! Verifique se preencheu todos os campos numéricos.", severity="error")
        


class CharacterFormScreen(Screen):
    def __init__(self, char_id: int = None):
        super().__init__()
        self.char_id = char_id  # Se for None, é Novo. Se tiver ID, é Edição
                
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Novo Herói" if not self.char_id else "🛠️  Editar o Herói", id="title")
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
        with SessionLocal() as db:
            if self.char_id:        # Lógica de Edição: Carregar dados existentes
                char = db.query(PersonagemDB).get(self.char_id)
                if char:
                    self.query_one("#inp-nome").value = char.nome
                    self.query_one("#inp-for").value = str(char.forca_base)
                    self.query_one("#inp-agi").value = str(char.agilidade_base)
                    self.query_one("#inp-res").value = str(char.resistencia_base)
                    self.query_one("#inp-per").value = str(char.percepcao_base)
                    self.query_one("#inp-exu").value = str(char.exuberancia_base)
                    racas = db.query(RacaDB).all()
                    classes = db.query(ClasseRPGDB).all()
                    self.query_one("#sel-raca").set_options([(r.nome, r.id) for r in racas])
                    self.query_one("#sel-classe").set_options([(c.nome, c.id) for c in classes])
                    self.query_one("#sel-raca").value = char.raca_id
                    self.query_one("#sel-classe").value = char.classe_id
            else:
                racas = db.query(RacaDB).all()
                classes = db.query(ClasseRPGDB).all()
                self.query_one("#sel-raca").set_options([(r.nome, r.id) for r in racas])
                self.query_one("#sel-classe").set_options([(c.nome, c.id) for c in classes])

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            dados = dict(nome=self.query_one("#inp-nome").value,
                    raca_id=self.query_one("#sel-raca").value,
                    classe_id=self.query_one("#sel-classe").value,
                    forca_base=int(self.query_one("#inp-for").value),
                    agilidade_base=int(self.query_one("#inp-agi").value),
                    resistencia_base=int(self.query_one("#inp-res").value),
                    percepcao_base=int(self.query_one("#inp-per").value),
                    exuberancia_base=int(self.query_one("#inp-exu").value))
            if self.char_id:
                try:
                    salvar_edicao(self.char_id, dados, "Personagem")
                    self.notify("Personagem editado com sucesso!", title="Sucesso", severity="information")
                except Exception as e:
                    self.notify("Erro ao editar! Verifique se preencheu todos os campos numéricos.", severity="error")
            else:
                try:
                    salvar_novo(dados, "Personagem")
                    self.notify("Personagem forjado com sucesso!", title="Sucesso", severity="information")
                except Exception as e:
                    self.notify("Erro ao criar! Verifique se preencheu todos os campos numéricos.", severity="error")
            self.app.pop_screen()

class ItemFormScreen(Screen):
    def __init__(self, item_id: int = None):
        super().__init__()
        self.item_id = item_id  
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="create-dialog"):
                yield Label("✨ Forjar Novo Item", id="title")
                yield Input(placeholder="Nome do Item", id="inp-nome")
                yield Select([
                    ("Arma", "Arma"), 
                    ("Escudo", "Escudo"), 
                    ("Armadura", "Armadura"), 
                    ("Acessório", "Acessório"),
                    ("Outro", "Outro")
                ], prompt="Selecione a Categoria", id="sel-categoria")
                yield Label("Efeitos e Bônus:")
                yield Input(placeholder="Dano", id="inp-dano", disabled=True)
                yield Input(placeholder="Defesa", id="inp-defesa", disabled=True)
                yield Select([
                    ("Corpo", "Corpo"), 
                    ('Distancia', 'Distancia'),('','')],
                    prompt="Tipo de Ataque (para Armas)", id="sel-tipo-ataque", disabled=True)
                yield Input(placeholder="Selecione um Emoji", id="inp-emoji", disabled=True)
                yield Horizontal(
                    Button("Salvar", variant="success", id="btn-save"),
                )
                yield Button("🔙 Voltar", variant="error", id="btn-cancel")
        yield Footer()
        
    def on_mount(self):
        if self.item_id:
            with SessionLocal() as db:
                item = db.query(ItemDB).get(self.item_id)
                if item:
                    self.query_one("#inp-nome").value = item.nome
                    self.query_one("#sel-categoria").value = item.categoria.capitalize()
                    self.query_one("#inp-dano").value = str(item.dano) 
                    self.query_one("#inp-defesa").value = str(item.defesa) if item.categoria != 'escudo' else str(item.defesa_extra) 
                    self.query_one("#sel-tipo-ataque").value = item.tipo_ataque.capitalize() if item.tipo_ataque else ""           

    @on(Select.Changed, "#sel-categoria")
    def on_select_changed(self, event: Select.Changed):
        categoria = event.value
        if categoria == "Arma":
            self.query_one("#inp-dano").disabled = False
            self.query_one("#inp-defesa").disabled = True
            self.query_one("#sel-tipo-ataque").disabled = False
            self.query_one("#inp-emoji").disabled = False
        elif categoria == "Escudo":
            self.query_one("#inp-dano").disabled = True
            self.query_one("#inp-defesa").disabled = False
            self.query_one("#sel-tipo-ataque").disabled = True
            self.query_one("#inp-emoji").disabled = False
        elif categoria == "Armadura":
            self.query_one("#inp-dano").disabled = True
            self.query_one("#inp-defesa").disabled = False
            self.query_one("#sel-tipo-ataque").disabled = True
            self.query_one("#inp-emoji").disabled = False            
        else:
            self.query_one("#inp-dano").disabled = True
            self.query_one("#inp-defesa").disabled = True
            self.query_one("#sel-tipo-ataque").disabled = True
            self.query_one("#inp-emoji").disabled = False
            #emojis = [(f'{name}: {emoji}', emoji) for name, emoji in dict_item_emoji.get('outros').items()]
            #self.query_one("#inp-emoji").set_options(emojis)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-save":
            try:
                dados = dict(
                    nome=self.query_one("#inp-nome").value,
                    categoria=self.query_one("#sel-categoria").value,
                    emoji=self.query_one("#inp-emoji").value,
                    dano=int(self.query_one("#inp-dano").value) if not self.query_one("#inp-dano").disabled else None,
                    tipo_ataque=self.query_one("#sel-tipo-ataque").value if not self.query_one("#sel-tipo-ataque").disabled else None,
                    defesa=int(self.query_one("#inp-defesa").value) if not self.query_one("#inp-defesa").disabled else None
                            )
                if self.item_id:
                    salvar_edicao(item_id, dados, "Item")
                    self.notify("Item forjado com sucesso!", title="Sucesso", severity="information")
                    self.app.pop_screen()
                else:
                    salvar_novo(dados, "Item")
                    
            except Exception as e:
                self.notify(f"Erro ao criar! {e}", severity="error")


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
# ECRÃ: SUBMENU DE PESQUISA E GERENCIAMENTO
# ==========================================
# class ManagementMenuScreen(Screen):
#     def __init__(self, element: int = None):
#         super().__init__()
#         self.element = element
#         self.model_map = {"Raça": RacaDB, "Classe": ClasseRPGDB, "Personagem": PersonagemDB, "Item": ItemDB}
        
#     def compose(self) -> ComposeResult:
#         yield Header()
#         with Horizontal():
#             with Vertical(id="side-panel"):
#                 yield Label("🔍 Pesquisa", id="title")
#                 yield Select([("Raça", 0), ("Classe", 1), ("Personagem",2), ("Item", 3)], prompt="Tipo de entidade", id="sel-entity")
#                 yield Input(placeholder="Filtrar por nome...", id="filter-input")
#                 yield Button("Editar Selecionado", variant="primary", id="btn-edit-sel")
#                 yield Button("Voltar ao Principal", variant="error", id="btn-back")
            
#             with Vertical(id="table-container"):
#                 yield DataTable(id="search-table")
#         yield Footer()

        
#     def mount_table(self):
#         self.table.clear()
#         table = self.query_one(DataTable)
#         table.cursor_type = "row"
#         if self.element == "Personagem":
#             table.add_columns(*[c.name for c in PersonagemDB.__table__.columns])
#         if self.element == "Raça":
#             table.add_columns(*[c.name for c in RacaDB.__table__.columns])
#         if self.element == "Classe":
#             table.add_columns(*[c.name for c in ClasseRPGDB.__table__.columns])
#         if self.element == "Item":
#             table.add_columns(*[c.name for c in ItemDB.__table__.columns])
#         else:
#             table.add_columns(*[c.name for c in PersonagemDB.__table__.columns])
#         return table

#     def on_mount(self):
#         self.table = self.mount_table()
#         self.refresh_table()

#     def refresh_table(self, filter_text: str = ""):
#         self.table.clear()
#         self.mount_table()
#         db = SessionLocal()

#         query = db.query(self.model_map.get(self.element, PersonagemDB)) if self.element else db.query(PersonagemDB)
#         if filter_text:
#             query = query.filter(self.model_map.get(self.element, PersonagemDB).nome.contains(filter_text))
        
#         for element in query.all():
#             if element:
#                 self.table.add_row(*[str(getattr(element, col.name)) for col in element.__table__.columns], key=str(element.id))
#         db.close()

#     def on_input_changed(self, event: Input.Changed):
#         if event.input.id == "filter-input":
#             self.refresh_table(event.value)

#     def on_select_changed(self, event: Select.Changed):
#         if event.select.id == "sel-entity":
#             self.element = event.value
#             self.refresh_table()

#     def on_button_pressed(self, event: Button.Pressed):
#         if event.button.id == "btn-back":
#             self.app.pop_screen()
        
#         elif event.button.id == "btn-edit-sel":
#             table = self.query_one(DataTable)
#             if table.cursor_row is not None:
#                 # 1. Recuperar dados da linha selecionada
#                 row_data = table.get_row_at(table.cursor_row)
#                 p_id = int(row_data[0]) # O ID está na primeira coluna
                
#                 # 2. Chamar o formulário reutilizável passando o ID
#                 # O callback garante que a tabela seja atualizada ao voltar
#                 self.app.push_screen(
#                     CharacterFormScreen(char_id=p_id), 
#                     callback=lambda _: self.refresh_table()
#                 )
                
#     def on_data_table_row_selected(self, event: DataTable.RowSelected):
#         """Permite editar ao pressionar Enter na linha."""
#         p_id = int(event.row_key.value) # Se usou chaves na criação da linha
#         self.app.push_screen(
#             CharacterFormScreen(char_id=p_id), 
#             callback=lambda _: self.refresh_table()
#         )

class ManagementMenuScreen(Screen):
    # Dicionário de configuração para mapear Tabelas -> Modelos -> Formulários
    # Nota: Assumindo que você criará RacaFormScreen, ClasseFormScreen etc.
    TABLE_MAP = {
        "personagens": {"model": PersonagemDB, "label": "Personagens"},
        "racas": {"model": RacaDB, "label": "Raças"},
        "classes": {"model": ClasseRPGDB, "label": "Classes"},
        "itens": {"model": ItemDB, "label": "Itens/Equipamentos"},
    }

    def compose(self):
        yield Header()
        with Horizontal():
            with Vertical(id="side-panel"):
                yield Label("📂 Tabelas do Sistema")
                yield Select(
                    [(v["label"], k) for k, v in self.TABLE_MAP.items()],
                    value="personagens",
                    id="table-selector"
                )
                yield Label("🔍 Pesquisa")
                yield Input(placeholder="Filtrar...", id="filter-input")
                yield Button("Editar Selecionado", variant="primary", id="btn-edit")
                yield Button("Voltar", variant="error", id="btn-back")
            
            with Vertical(id="table-container"):
                yield DataTable(id="universal-table")
        yield Footer()

    def on_mount(self):
        self.refresh_table_data()

    def on_select_changed(self, event: Select.Changed):
        """Disparado quando o usuário muda a tabela no seletor."""
        if event.select.id == "table-selector":
            self.refresh_table_data()

    def refresh_table_data(self, filter_text: str = ""):
        table_id = self.query_one("#table-selector").value
        model = self.TABLE_MAP[table_id]["model"]
        data_table = self.query_one("#universal-table")
        
        # Limpa TUDO, inclusive os cabeçalhos das colunas
        data_table.clear(columns=True)
        data_table.cursor_type = "row"

        db = SessionLocal()
        # 1. Definir Colunas Dinamicamente baseadas no Modelo
        if model == PersonagemDB:
            data_table.add_columns("ID", "Nome", "Nível", "Raça")
            query = db.query(PersonagemDB)
            if filter_text: query = query.filter(PersonagemDB.nome.contains(filter_text))
            for p in query.all():
                data_table.add_row(str(p.id), p.nome, str(p.nivel), p.raca.nome, key=str(p.id))
        
        elif model == RacaDB:
            data_table.add_columns("ID", "Nome", "Bónus")
            if filter_text: query = query.filter(RacaDB.nome.contains(filter_text))
            for r in db.query(RacaDB).all():
                data_table.add_row(str(r.id), r.nome, str(r.bonus_atributos), key=str(r.id))
        
        elif model == ItemDB:
            data_table.add_columns("ID", "Nome", "Tipo", "Dano/Def")
            for i in db.query(ItemDB).all():
                val = i.dano if i.categoria == "arma" else i.defesa
                data_table.add_row(str(i.id), i.nome, i.categoria, str(val), key=str(i.id))
                
        elif model == ClasseRPGDB:
            data_table.add_columns("ID", "Nome", "Bónus de Caminhos")
            for c in db.query(ClasseRPGDB).all():
                data_table.add_row(str(c.id), c.nome, str(c.bonus_caminhos), key=str(c.id))
        db.close()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Redireciona para o formulário correto baseado na tabela atual."""
        table_id = self.query_one("#table-selector").value
        if event.row_key:
            if hasattr(event.row_key, 'value'):
                item_id = int(event.row_key.value)
            else:
                item_id = int(event.row_key)
                
        
        # Lógica de roteamento para o formulário reutilizável correto
        if table_id == "personagens":
            self.app.push_screen(CharacterFormScreen(char_id=item_id), callback=lambda _: self.refresh_table_data())
        # Adicione elif para os outros formulários aqui...
        elif table_id == "racas":
            self.app.push_screen(RacaFormScreen(raca_id=item_id), callback=lambda _: self.refresh_table_data())
        elif table_id == "classes":
            self.app.push_screen(ClasseFormScreen(classe_id=item_id), callback=lambda _: self.refresh_table_data())
        elif table_id == "itens":
            self.app.push_screen(ItemFormScreen(item_id=item_id), callback=lambda _: self.refresh_table_data())

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-edit":
            # Dispara manualmente a seleção da linha atual
            table = self.query_one("#universal-table")
            if table.cursor_row is not None:
                row_key = table.get_row_at(table.cursor_row) # Pega o ID da primeira coluna
                self.on_data_table_row_selected(DataTable.RowSelected(table, event.button, row_key[0]))
                

# ==========================================
# ECRÃ PRINCIPAL (MENU APP)
# ==========================================
class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Center(), Middle():
            with Vertical(id="main-menu"):
                yield Label("🛡️  SIS-CHARLES RPG 🛡️", id="main-title")
                yield Button("✨ Criar", id="menu-create", variant="success")
                yield Button("🔍 Pesquisar/Editar", id="menu-search") 
                yield Button("⚔️  Entrar na Arena", id="menu-arena", variant="warning")
                yield Button("❌ Sair do Sistema", id="menu-quit", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "menu-create": self.app.push_screen(CreationScreen())
        elif btn_id == "menu-arena": self.app.push_screen(ArenaScreen())
        elif btn_id == "menu-search": self.app.push_screen(ManagementMenuScreen())
        elif btn_id == "menu-quit": self.app.exit()
        
       
# ==========================================
# CONFIGURAÇÃO DE ESTILOS E LANÇAMENTO
# ==========================================
class RPGApp(App):
    CSS_PATH = "app/views/styles.css"
    BINDINGS = [("d", "toggle_dark", "Mudar Tema Escuro/Claro"), ("q", "quit", "Sair"), ("m", "start_stop_music", "Música On/Off")]
    music.play()
    
    def on_mount(self):
        self.push_screen(MainScreen())
 
    def on_key(self, event):
        if event.key == "m":
            action_start_stop_music()


if __name__ == "__main__": 
    app = RPGApp()
    app.run()