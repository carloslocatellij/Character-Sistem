"""
Tela de Gerenciamento de Equipe e Alistamento (Party Management Screen)

Permite ao jogador:
1. Organizar a formação da equipe (até 4 membros ativos e reservas).
2. Visualizar fichas detalhadas, equipamentos e magias de cada membro.
3. Transferir itens entre os inventários individuais dos personagens.
4. Recrutar novos aventureiros disponíveis para a jornada.

Segue o Padrão Ouro estilo Final Fantasy com Textual TUI.
"""
import os
import logging
from typing import Optional, List, Dict, Any

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, ListView, ListItem, Static, TabbedContent, TabPane, Select
from textual.containers import Vertical, Horizontal, Container
from textual import on
from textual.reactive import reactive
from textual.message import Message
from textual.widget import Widget

from app.db.database import SessionLocal
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, EquipeMembroDB

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


class PartyManagementScreen(ModalScreen[Optional[str]]):
    """
    Modal interativo para gestão completa da equipe de aventureiros.
    """

    CSS_PATH = "styles/party_styles.css"

    personagem_selecionado_id: reactive[Optional[int]] = reactive(None)

    class EquipeAtualizada(Message):
        """Mensagem emitida quando a composição da equipe é alterada."""
        def __init__(self, control: Widget, dados: dict) -> None:
            super().__init__()
            self._control = control
            self.dados = dados

        @property
        def control(self) -> Widget:
            return self._control

    def __init__(self, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None):
        super().__init__()
        self.usuario_id = usuario_id
        self.cenario_id = cenario_id
        self.origem_transfer_id: Optional[int] = None
        self.destino_transfer_id: Optional[int] = None
        self.item_transfer_selecionado: Optional[str] = None

    def compose(self) -> ComposeResult:
        with Vertical(id="party-dialog"):
            yield Label("👥 Gestão de Equipe & Alistamento de Aventureiros", id="party-main-title", classes="titulo-secao")

            with TabbedContent(initial="tab-formacao", id="party-tabs"):

                # ─── ABA 1: FORMAÇÃO DA EQUIPE ────────────────────────────
                with TabPane("👥 Formação da Equipe", id="tab-formacao"):
                    with Horizontal(classes="party-layout-horizontal"):

                        # Coluna Membros Ativos
                        with Vertical(classes="party-coluna"):
                            yield Label("⚔️ Membros Ativos (Máx 4):", classes="party-coluna-titulo")
                            yield ListView(id="list-membros-ativos", classes="party-lista")
                            yield Button("⬇ Mover para Reserva", id="btn-mover-reserva", variant="warning", classes="btn-acao-party", disabled=True)

                        # Coluna Membros Reserva
                        with Vertical(classes="party-coluna"):
                            yield Label("🛡️ Membros na Reserva:", classes="party-coluna-titulo")
                            yield ListView(id="list-membros-reserva", classes="party-lista")
                            yield Button("⬆ Alistar na Ativa", id="btn-mover-ativa", variant="success", classes="btn-acao-party", disabled=True)

                    # Painel Inferior: Ficha do Personagem Selecionado
                    with Horizontal(id="painel-detalhes-personagem"):
                        with Vertical(id="detalhes-ficha-col1"):
                            yield Label("Ficha do Aventureiro:", classes="label-destaque")
                            yield Static("Selecione um membro para visualizar sua ficha.", id="lbl-ficha-basica", classes="label-info")
                        with Vertical(id="detalhes-ficha-col2"):
                            yield Label("Equipamento & Magias:", classes="label-destaque")
                            yield Static("—", id="lbl-ficha-equipamentos", classes="label-info")

                # ─── ABA 2: TRANSFERÊNCIA DE ITENS ────────────────────────
                with TabPane("🎒 Transferir Itens", id="tab-transferencia"):
                    with Horizontal(classes="transfer-layout"):

                        # Doador (Origem)
                        with Vertical(classes="transfer-coluna"):
                            yield Label("1. Membro Doador (Origem):", classes="party-coluna-titulo")
                            yield Select([], prompt="Selecione o doador", id="select-doador")
                            yield ListView(id="list-itens-doador", classes="party-lista")

                        # Painel Central com Botões
                        with Vertical(classes="transfer-painel-meio"):
                            yield Label("Ação:", classes="party-coluna-titulo")
                            yield Button("➡ Transferir 1", id="btn-transferir-um", variant="primary", classes="transfer-btn", disabled=True)
                            yield Button("⏩ Transferir Tudo", id="btn-transferir-tudo", variant="warning", classes="transfer-btn", disabled=True)
                            yield Static("Selecione os dois membros e o item.", id="lbl-status-transfer", classes="label-info")

                        # Receptor (Destino)
                        with Vertical(classes="transfer-coluna"):
                            yield Label("2. Membro Receptor (Destino):", classes="party-coluna-titulo")
                            yield Select([], prompt="Selecione o receptor", id="select-receptor")
                            yield ListView(id="list-itens-receptor", classes="party-lista")

                # ─── ABA 3: RECRUTAMENTO / ALISTAMENTO ───────────────────
                with TabPane("🤝 Alistamento de Novos Membros", id="tab-recrutamento"):
                    with Vertical(classes="party-coluna"):
                        yield Label("Aventureiros Disponíveis para Recrutamento:", classes="party-coluna-titulo")
                        yield ListView(id="list-recrutaveis", classes="party-lista")
                        with Horizontal(id="painel-acoes-recrutamento"):
                            yield Button("✨ Alistar Personagem na Equipe", id="btn-recrutar-personagem", variant="success", disabled=True)

            with Horizontal(id="party-rodape-botoes"):
                yield Button("Voltar / Fechar (ESC)", id="btn-fechar-party", variant="error")

    def on_mount(self) -> None:
        self.call_after_refresh(self.carregar_dados)

    def carregar_dados(self) -> None:
        """Carrega e popula todas as listas da tela a partir do banco de dados."""
        db = SessionLocal()
        try:
            ctrl = GameController(db)
            GameController.garantir_dados_iniciais_completos(db)

            todos_chars = db.query(PersonagemDB).all()
            membros_equipe = db.query(EquipeMembroDB).filter(
                EquipeMembroDB.usuario_id == self.usuario_id,
                EquipeMembroDB.cenario_id == self.cenario_id
            ).all()

            mapa_membros = {m.personagem_id: m for m in membros_equipe}

            ativos: List[PersonagemDB] = []
            reservas: List[PersonagemDB] = []
            nao_alistados: List[PersonagemDB] = []

            for char in todos_chars:
                if char.id in mapa_membros:
                    m = mapa_membros[char.id]
                    if m.ativo == 1 and len(ativos) < 4:
                        ativos.append(char)
                    else:
                        reservas.append(char)
                else:
                    nao_alistados.append(char)

            if not ativos and not reservas:
                for idx, c in enumerate(todos_chars[:4]):
                    ctrl.alistar_personagem(c.id, slot=idx+1, usuario_id=self.usuario_id, cenario_id=self.cenario_id)
                    ativos.append(c)
                for c in todos_chars[4:]:
                    ctrl.alistar_personagem(c.id, slot=0, usuario_id=self.usuario_id, cenario_id=self.cenario_id)
                    reservas.append(c)
            else:
                for c in nao_alistados:
                    if c not in reservas and c not in ativos:
                        reservas.append(c)

            list_ativos = self.query_one("#list-membros-ativos", ListView)
            list_ativos.clear()
            for char in ativos:
                raca_nome = char.raca.nome if char.raca else "Humano"
                classe_nome = char.classe.nome if char.classe else "Aventureiro"
                emoji = getattr(char.raca, "emoji", "🧙")
                item_widget = ListItem(
                    Label(f"{emoji} [bold green]{char.nome}[/] (Nv {char.nivel} {classe_nome} {raca_nome}) — Slot {char.slot_equipe}"),
                    name=str(char.id)
                )
                list_ativos.append(item_widget)

            list_reservas = self.query_one("#list-membros-reserva", ListView)
            list_reservas.clear()
            for char in reservas:
                raca_nome = char.raca.nome if char.raca else "Humano"
                classe_nome = char.classe.nome if char.classe else "Aventureiro"
                emoji = getattr(char.raca, "emoji", "🧙")
                item_widget = ListItem(
                    Label(f"{emoji} [yellow]{char.nome}[/] (Nv {char.nivel} {classe_nome} {raca_nome}) — [dim]Reserva[/]"),
                    name=str(char.id)
                )
                list_reservas.append(item_widget)

            list_recrut = self.query_one("#list-recrutaveis", ListView)
            list_recrut.clear()
            for char in todos_chars:
                raca_nome = char.raca.nome if char.raca else "Humano"
                classe_nome = char.classe.nome if char.classe else "Aventureiro"
                status_membro = "⚔️ Ativo" if char in ativos else "🛡️ Reserva" if char in reservas else "➕ Disponível"
                item_widget = ListItem(
                    Label(f"[bold]{char.nome}[/] ({classe_nome} {raca_nome}) — Status: [cyan]{status_membro}[/]"),
                    name=str(char.id)
                )
                list_recrut.append(item_widget)

            opcoes_select = [(f"{c.nome} ({getattr(c.classe, 'nome', 'Char')})", c.id) for c in (ativos + reservas)]
            select_doador = self.query_one("#select-doador", Select)
            select_receptor = self.query_one("#select-receptor", Select)
            select_doador.set_options(opcoes_select)
            select_receptor.set_options(opcoes_select)
        finally:
            db.close()

    # ==========================================
    # SELEÇÃO E EXIBIÇÃO DE DETALHES DA FICHA
    # ==========================================

    @on(ListView.Highlighted, "#list-membros-ativos")
    def on_ativo_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            char_id = int(event.item.name)
            self.personagem_selecionado_id = char_id
            self.query_one("#btn-mover-reserva", Button).disabled = False
            self.query_one("#btn-mover-ativa", Button).disabled = True
            self._atualizar_painel_ficha(char_id)

    @on(ListView.Highlighted, "#list-membros-reserva")
    def on_reserva_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            char_id = int(event.item.name)
            self.personagem_selecionado_id = char_id
            self.query_one("#btn-mover-reserva", Button).disabled = True
            self.query_one("#btn-mover-ativa", Button).disabled = False
            self._atualizar_painel_ficha(char_id)

    @on(ListView.Highlighted, "#list-recrutaveis")
    def on_recrutavel_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            char_id = int(event.item.name)
            self.personagem_selecionado_id = char_id
            self.query_one("#btn-recrutar-personagem", Button).disabled = False
            self._atualizar_painel_ficha(char_id)

    def _atualizar_painel_ficha(self, char_id: int) -> None:
        db = SessionLocal()
        try:
            char = db.get(PersonagemDB, char_id)
            if not char:
                return

            ctrl = GameController(db)
            p_dom = ctrl.converter_para_dominio(char)
            raca_nome = p_dom.raca.nome if p_dom.raca else "Humano"
            classe_nome = p_dom.classe.nome if p_dom.classe else "Aventureiro"

            atr = p_dom.atributos_totais or {}
            forca = atr.get("forca", 0)
            agi = atr.get("agilidade", 0)
            res = atr.get("resistencia", 0)
            perc = atr.get("percepcao", 0)
            exu = atr.get("exuberancia", 0)

            txt_basico = (
                f"[bold cyan]{p_dom.nome}[/] | Raça: {raca_nome} | Classe: {classe_nome}\n"
                f"💟 HP: {p_dom.pv_atual}/{p_dom.max_hp} | 🔮 MP: {p_dom.pm_atual}/{p_dom.max_mp}\n"
                f"💪 FOR: {forca} | 🏃 AGI: {agi} | 🛡️ RES: {res} | 👁️ PER: {perc} | ✨ EXU: {exu}"
            )
            self.query_one("#lbl-ficha-basica", Static).update(txt_basico)

            arma = getattr(p_dom.mao_direita, "nome", "Nenhuma") if p_dom.mao_direita else "Nenhuma"
            armadura = getattr(p_dom.armadura, "nome", "Nenhuma") if p_dom.armadura else "Nenhuma"
            magias_nomes = ", ".join(m.nome for m in p_dom.magias_conhecidas) if p_dom.magias_conhecidas else "Nenhuma"
            itens_str = ", ".join(f"{it['nome']} (x{it['quantidade']})" for it in p_dom.inventario) if p_dom.inventario else "Vazio"

            txt_eqp = (
                f"🪓 Arma: [bold yellow]{arma}[/] | 🦺 Armadura: [bold yellow]{armadura}[/]\n"
                f"🪄 Magias: [bold magenta]{magias_nomes}[/]\n"
                f"🎒 Inventário: [dim]{itens_str}[/]"
            )
            self.query_one("#lbl-ficha-equipamentos", Static).update(txt_eqp)
        finally:
            db.close()

    # ==========================================
    # AÇÕES: MOVER ATIVO / RESERVA E RECRUTAR
    # ==========================================

    @on(Button.Pressed, "#btn-mover-reserva")
    def ao_mover_reserva(self, event: Button.Pressed) -> None:
        if not self.personagem_selecionado_id:
            return

        db = SessionLocal()
        try:
            ativos_count = db.query(EquipeMembroDB).filter(
                EquipeMembroDB.usuario_id == self.usuario_id,
                EquipeMembroDB.cenario_id == self.cenario_id,
                EquipeMembroDB.ativo == 1
            ).count()

            if ativos_count <= 1:
                self.notify("⚠️ A equipe ativa precisa ter no mínimo 1 integrante!", severity="warning")
                return

            ctrl = GameController(db)
            membro = db.query(EquipeMembroDB).filter(
                EquipeMembroDB.personagem_id == self.personagem_selecionado_id,
                EquipeMembroDB.usuario_id == self.usuario_id,
                EquipeMembroDB.cenario_id == self.cenario_id
            ).first()

            if membro:
                membro.ativo = 0
                membro.slot_posicao = 0
                p = db.get(PersonagemDB, self.personagem_selecionado_id)
                if p:
                    p.slot_equipe = 0
                db.commit()
        finally:
            db.close()

        self.carregar_dados()
        self.notify("Membro movido para a reserva com sucesso!", severity="information")

    @on(Button.Pressed, "#btn-mover-ativa")
    def ao_mover_ativa(self, event: Button.Pressed) -> None:
        if not self.personagem_selecionado_id:
            return

        db = SessionLocal()
        try:
            ativos_count = db.query(EquipeMembroDB).filter(
                EquipeMembroDB.usuario_id == self.usuario_id,
                EquipeMembroDB.cenario_id == self.cenario_id,
                EquipeMembroDB.ativo == 1
            ).count()

            if ativos_count >= 4:
                self.notify("⚠️ Limite atingido: A equipe já possui 4 membros ativos!", severity="warning")
                return

            ctrl = GameController(db)
            ctrl.alistar_personagem(self.personagem_selecionado_id, usuario_id=self.usuario_id, cenario_id=self.cenario_id)
        finally:
            db.close()

        self.carregar_dados()
        self.notify("Membro promovido para a equipe ativa!", severity="information")

    @on(Button.Pressed, "#btn-recrutar-personagem")
    def ao_recrutar(self, event: Button.Pressed) -> None:
        if not self.personagem_selecionado_id:
            return

        db = SessionLocal()
        try:
            ctrl = GameController(db)
            ctrl.alistar_personagem(self.personagem_selecionado_id, usuario_id=self.usuario_id, cenario_id=self.cenario_id)
        finally:
            db.close()

        self.carregar_dados()
        self.notify("Aventureiro alistado com sucesso!", severity="information")

    # ==========================================
    # TRANSFERÊNCIA DE ITENS ENTRE MEMBROS
    # ==========================================

    @on(Select.Changed, "#select-doador")
    def on_doador_changed(self, event: Select.Changed):
        self.origem_transfer_id = event.value
        self._carregar_itens_doador()
        self._verificar_botoes_transfer()

    @on(Select.Changed, "#select-receptor")
    def on_receptor_changed(self, event: Select.Changed):
        self.destino_transfer_id = event.value
        self._carregar_itens_receptor()
        self._verificar_botoes_transfer()

    def _carregar_itens_doador(self) -> None:
        list_doador = self.query_one("#list-itens-doador", ListView)
        list_doador.clear()
        if not self.origem_transfer_id:
            return

        db = SessionLocal()
        try:
            char = db.get(PersonagemDB, self.origem_transfer_id)
            if char and char.inventario:
                for it in char.inventario:
                    widget = ListItem(
                        Label(f"{it.get('emoji', '🧪')} {it['nome']} (x{it['quantidade']})"),
                        name=it['nome']
                    )
                    list_doador.append(widget)
        finally:
            db.close()

    def _carregar_itens_receptor(self) -> None:
        list_receptor = self.query_one("#list-itens-receptor", ListView)
        list_receptor.clear()
        if not self.destino_transfer_id:
            return

        db = SessionLocal()
        try:
            char = db.get(PersonagemDB, self.destino_transfer_id)
            if char and char.inventario:
                for it in char.inventario:
                    widget = ListItem(
                        Label(f"{it.get('emoji', '🧪')} {it['nome']} (x{it['quantidade']})"),
                        name=it['nome']
                    )
                    list_receptor.append(widget)
        finally:
            db.close()

    @on(ListView.Highlighted, "#list-itens-doador")
    def on_item_doador_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.item_transfer_selecionado = event.item.name
            self._verificar_botoes_transfer()

    def _verificar_botoes_transfer(self) -> None:
        pode_transferir = bool(
            self.origem_transfer_id and
            self.destino_transfer_id and
            self.origem_transfer_id != self.destino_transfer_id and
            self.item_transfer_selecionado
        )
        self.query_one("#btn-transferir-um", Button).disabled = not pode_transferir
        self.query_one("#btn-transferir-tudo", Button).disabled = not pode_transferir

    @on(Button.Pressed, "#btn-transferir-um")
    def ao_transferir_um(self, event: Button.Pressed) -> None:
        self._executar_transferencia(quantidade=1)

    @on(Button.Pressed, "#btn-transferir-tudo")
    def ao_transferir_tudo(self, event: Button.Pressed) -> None:
        db = SessionLocal()
        try:
            char = db.get(PersonagemDB, self.origem_transfer_id)
            qtd = 1
            if char and char.inventario:
                for it in char.inventario:
                    if it["nome"].lower() == self.item_transfer_selecionado.lower():
                        qtd = it["quantidade"]
                        break
        finally:
            db.close()

        self._executar_transferencia(quantidade=qtd)

    def _executar_transferencia(self, quantidade: int) -> None:
        if not self.origem_transfer_id or not self.destino_transfer_id or not self.item_transfer_selecionado:
            return

        db = SessionLocal()
        try:
            ctrl = GameController(db)
            sucesso = ctrl.transferir_item_entre_personagens_db(
                id_origem=self.origem_transfer_id,
                id_destino=self.destino_transfer_id,
                nome_item=self.item_transfer_selecionado,
                quantidade=quantidade
            )
        finally:
            db.close()

        if sucesso:
            self.notify(f"Transferido {quantidade}x {self.item_transfer_selecionado} com sucesso!", severity="information")
            self._carregar_itens_doador()
            self._carregar_itens_receptor()
            self._atualizar_painel_ficha(self.origem_transfer_id)
        else:
            self.notify("Falha ao transferir item!", severity="error")

    @on(Button.Pressed, "#btn-fechar-party")
    def ao_fechar(self, event: Button.Pressed) -> None:
        self.dismiss("fechou")
