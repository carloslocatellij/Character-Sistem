import esper
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, ListView, ListItem, Static, TabbedContent, TabPane
from textual.containers import Vertical, Horizontal
from textual import on

from app.core.engine.components import StatsComponent, InventoryComponent, EquipmentComponent
from app.core.engine.item_system import (
    obter_itens_usaveis,
    obter_equipamentos_inventario,
    aplicar_usar_item,
    aplicar_equipar_item,
    aplicar_desequipar_item,
)

class InventarioMenuScreen(ModalScreen[str]):
    """
    Menu interativo com abas para visualização, uso e troca de equipamentos do personagem.
    """

    CSS_PATH = "styles/styles.css"

    def __init__(self, aba_inicial: str = "tab-itens", entity_id: int = 1):
        super().__init__()
        self.aba_inicial = aba_inicial if aba_inicial in ["tab-itens", "tab-equipamentos"] else "tab-itens"
        self.entity_id = entity_id
        self.item_usavel_selecionado = None
        self.equipamento_selecionado = None

    def compose(self) -> ComposeResult:
        with Vertical(id="inv-dialog"):
            yield Label("🎒 Gerenciamento de Inventário e Equipamentos", id="inv-main-title", classes="titulo-secao")

            with TabbedContent(initial=self.aba_inicial, id="inv-tabs"):
                with TabPane("🧪 Itens Usáveis", id="tab-itens"):
                    with Horizontal(classes="inv-pane-layout"):
                        with Vertical(classes="inv-lista-container"):
                            yield Label("Itens Consumíveis:", classes="subtitulo")
                            yield ListView(id="list-itens-usaveis")
                        with Vertical(classes="inv-detalhes-container"):
                            yield Label("Detalhes do Item:", classes="subtitulo")
                            yield Static("Selecione um item da lista.", id="lbl-item-detalhe")
                            yield Button("✨ Usar Item", id="btn-usar-item", variant="success", disabled=True)

                with TabPane("⚔️ Equipamentos", id="tab-equipamentos"):
                    with Vertical(classes="inv-pane-layout"):
                        with Vertical(id="painel-equipados-atuais"):
                            yield Label("🛡️ Equipados Atualmente:", classes="subtitulo")
                            with Horizontal(classes="linha-slot-eqp"):
                                yield Static("🗡️ Arma: (Nenhuma)", id="lbl-slot-arma")
                                yield Button("Desequipar", id="btn-deseqp-arma", variant="warning", classes="btn-compacto")
                            with Horizontal(classes="linha-slot-eqp"):
                                yield Static("🦺 Armadura: (Nenhuma)", id="lbl-slot-armadura")
                                yield Button("Desequipar", id="btn-deseqp-armadura", variant="warning", classes="btn-compacto")
                            with Horizontal(classes="linha-slot-eqp"):
                                yield Static("🛡️ Escudo: (Nenhum)", id="lbl-slot-escudo")
                                yield Button("Desequipar", id="btn-deseqp-escudo", variant="warning", classes="btn-compacto")

                        with Horizontal(classes="inv-eqp-lista-layout"):
                            with Vertical(classes="inv-lista-container"):
                                yield Label("Equipamentos no Inventário:", classes="subtitulo")
                                yield ListView(id="list-equipamentos")
                            with Vertical(classes="inv-detalhes-container"):
                                yield Label("Ação:", classes="subtitulo")
                                yield Static("Selecione um equipamento do inventário.", id="lbl-eqp-detalhe")
                                yield Button("⚔️ Equipar Item", id="btn-equipar-item", variant="primary", disabled=True)

            with Horizontal(id="inv-rodape-botoes"):
                yield Button("Voltar / Fechar (ESC)", id="btn-fechar-inv", variant="error")

    def _obter_componentes(self):
        stats = None
        inv = None
        eqp = None

        if esper.entity_exists(self.entity_id):
            if esper.has_component(self.entity_id, StatsComponent):
                stats = esper.component_for_entity(self.entity_id, StatsComponent)
            if esper.has_component(self.entity_id, InventoryComponent):
                inv = esper.component_for_entity(self.entity_id, InventoryComponent)
            if esper.has_component(self.entity_id, EquipmentComponent):
                eqp = esper.component_for_entity(self.entity_id, EquipmentComponent)

        if inv is None:
            for ent, comp in esper.get_component(InventoryComponent):
                inv = comp
                self.entity_id = ent
                break
        if stats is None and inv is not None:
            if esper.has_component(self.entity_id, StatsComponent):
                stats = esper.component_for_entity(self.entity_id, StatsComponent)
            else:
                for ent, comp in esper.get_component(StatsComponent):
                    stats = comp
                    break
        if eqp is None and inv is not None:
            if esper.has_component(self.entity_id, EquipmentComponent):
                eqp = esper.component_for_entity(self.entity_id, EquipmentComponent)
            else:
                for ent, comp in esper.get_component(EquipmentComponent):
                    eqp = comp
                    break

        return stats, inv, eqp

    def on_mount(self) -> None:
        self.call_after_refresh(self.atualizar_tudo)

    def atualizar_tudo(self) -> None:
        stats, inv, eqp = self._obter_componentes()

        # 1. Atualiza lista de itens usáveis
        list_usaveis = self.query_one("#list-itens-usaveis", ListView)
        list_usaveis.clear()
        itens_usaveis = obter_itens_usaveis(inv) if inv else []
        for item in itens_usaveis:
            item_widget = ListItem(
                Label(f"{item['emoji']} {item['nome']} (x{item['quantidade']}) — {item['descricao']}"),
                name=item['nome']
            )
            list_usaveis.append(item_widget)

        if not itens_usaveis:
            self.query_one("#lbl-item-detalhe", Static).update("Você não possui itens usáveis no inventário.")
            self.query_one("#btn-usar-item", Button).disabled = True
            self.item_usavel_selecionado = None
        else:
            self.query_one("#lbl-item-detalhe", Static).update("Selecione um item da lista.")
            self.query_one("#btn-usar-item", Button).disabled = True

        # 2. Atualiza os slots equipados atualmente
        lbl_arma = self.query_one("#lbl-slot-arma", Static)
        btn_arma = self.query_one("#btn-deseqp-arma", Button)
        if eqp and eqp.arma:
            lbl_arma.update(f"🗡️ Arma: {eqp.arma.get('nome')} (+{eqp.arma.get('bonus_atk', 0)} ATK)")
            btn_arma.disabled = False
        else:
            lbl_arma.update("🗡️ Arma: (Nenhuma)")
            btn_arma.disabled = True

        lbl_armadura = self.query_one("#lbl-slot-armadura", Static)
        btn_armadura = self.query_one("#btn-deseqp-armadura", Button)
        if eqp and eqp.armadura:
            lbl_armadura.update(f"🦺 Armadura: {eqp.armadura.get('nome')} (+{eqp.armadura.get('bonus_def', 0)} DEF)")
            btn_armadura.disabled = False
        else:
            lbl_armadura.update("🦺 Armadura: (Nenhuma)")
            btn_armadura.disabled = True

        lbl_escudo = self.query_one("#lbl-slot-escudo", Static)
        btn_escudo = self.query_one("#btn-deseqp-escudo", Button)
        if eqp and hasattr(eqp, "escudo") and eqp.escudo:
            lbl_escudo.update(f"🛡️ Escudo: {eqp.escudo.get('nome')} (+{eqp.escudo.get('bonus_def', 0)} DEF)")
            btn_escudo.disabled = False
        else:
            lbl_escudo.update("🛡️ Escudo: (Nenhum)")
            btn_escudo.disabled = True

        # 3. Atualiza lista de equipamentos do inventário
        list_eqp = self.query_one("#list-equipamentos", ListView)
        list_eqp.clear()
        equipamentos = obter_equipamentos_inventario(inv) if inv else []
        for eq in equipamentos:
            eq_widget = ListItem(
                Label(f"{eq['emoji']} {eq['nome']} (x{eq['quantidade']}) [{eq['categoria'].upper()}] — {eq['descricao']}"),
                name=eq['nome']
            )
            list_eqp.append(eq_widget)

        if not equipamentos:
            self.query_one("#lbl-eqp-detalhe", Static).update("Você não possui equipamentos no inventário.")
            self.query_one("#btn-equipar-item", Button).disabled = True
            self.equipamento_selecionado = None
        else:
            self.query_one("#lbl-eqp-detalhe", Static).update("Selecione um equipamento do inventário.")
            self.query_one("#btn-equipar-item", Button).disabled = True

    @on(ListView.Selected, "#list-itens-usaveis")
    @on(ListView.Highlighted, "#list-itens-usaveis")
    def on_item_usavel_selecionado(self, event: ListView.Selected | ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.item_usavel_selecionado = event.item.name
            self.query_one("#lbl-item-detalhe", Static).update(f"Item selecionado: [bold yellow]{self.item_usavel_selecionado}[/]")
            self.query_one("#btn-usar-item", Button).disabled = False

    @on(ListView.Selected, "#list-equipamentos")
    @on(ListView.Highlighted, "#list-equipamentos")
    def on_equipamento_selecionado(self, event: ListView.Selected | ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.equipamento_selecionado = event.item.name
            self.query_one("#lbl-eqp-detalhe", Static).update(f"Equipamento selecionado: [bold cyan]{self.equipamento_selecionado}[/]")
            self.query_one("#btn-equipar-item", Button).disabled = False

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        stats, inv, eqp = self._obter_componentes()

        if button_id == "btn-fechar-inv":
            self.dismiss(None)
        elif button_id == "btn-usar-item":
            if self.item_usavel_selecionado and stats and inv:
                sucesso, msg = aplicar_usar_item(stats, inv, self.item_usavel_selecionado)
                self.app.notify(msg, title="Item Usado")
                self.atualizar_tudo()
        elif button_id == "btn-equipar-item":
            if self.equipamento_selecionado and eqp and inv:
                sucesso, msg = aplicar_equipar_item(eqp, inv, self.equipamento_selecionado)
                self.app.notify(msg, title="Equipamento")
                self.atualizar_tudo()
        elif button_id == "btn-deseqp-arma":
            if eqp and inv:
                sucesso, msg = aplicar_desequipar_item(eqp, inv, "arma")
                self.app.notify(msg, title="Desequipado")
                self.atualizar_tudo()
        elif button_id == "btn-deseqp-armadura":
            if eqp and inv:
                sucesso, msg = aplicar_desequipar_item(eqp, inv, "armadura")
                self.app.notify(msg, title="Desequipado")
                self.atualizar_tudo()
        elif button_id == "btn-deseqp-escudo":
            if eqp and inv:
                sucesso, msg = aplicar_desequipar_item(eqp, inv, "escudo")
                self.app.notify(msg, title="Desequipado")
                self.atualizar_tudo()
