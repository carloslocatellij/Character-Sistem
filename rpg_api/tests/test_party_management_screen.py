import pytest
import os
import random
from textual.app import App
from app.db.database import SessionLocal, Base, engine
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, EquipeMembroDB
from app.views.party_management_screen import PartyManagementScreen

from pathlib import Path

DIR_STYLES = Path(__file__).parent.parent / "app" / "views" / "styles"

class DummyPartyApp(App):
    CSS_PATH = str(DIR_STYLES / "party_styles.css")
    def __init__(self, screen_to_test):
        super().__init__()
        self.screen_to_test = screen_to_test

    def on_mount(self):
        self.push_screen(self.screen_to_test)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        GameController.garantir_dados_iniciais_completos(db)
    finally:
        db.close()
    yield
    db = SessionLocal()
    try:
        db.query(EquipeMembroDB).delete()
        db.query(PersonagemDB).delete()
        db.commit()
    except Exception:
        pass
    finally:
        db.close()


@pytest.mark.anyio
async def test_party_management_screen_renderiza_listas():
    """Valida que a tela carrega e popula membros ativos, reservas e recrutáveis."""
    screen = PartyManagementScreen()
    app = DummyPartyApp(screen)

    async with app.run_test() as pilot:
        await pilot.pause()

        list_ativos = screen.query_one("#list-membros-ativos")
        assert list_ativos is not None
        assert len(list_ativos.children) >= 1

        list_reservas = screen.query_one("#list-membros-reserva")
        assert list_reservas is not None

        list_recrutaveis = screen.query_one("#list-recrutaveis")
        assert list_recrutaveis is not None
        assert len(list_recrutaveis.children) >= 4


@pytest.mark.anyio
async def test_party_management_mover_para_reserva_e_ativa():
    """Valida transições de membros entre equipe ativa e reserva."""
    screen = PartyManagementScreen()
    app = DummyPartyApp(screen)

    async with app.run_test() as pilot:
        await pilot.pause()

        list_ativos = screen.query_one("#list-membros-ativos")
        if list_ativos.children:
            list_ativos.index = 0
            await pilot.pause()

            btn_reserva = screen.query_one("#btn-mover-reserva")
            assert btn_reserva.disabled is False

            btn_reserva.press()
            await pilot.pause()

            list_reservas = screen.query_one("#list-membros-reserva")
            assert len(list_reservas.children) >= 1


@pytest.mark.anyio
async def test_transferir_item_entre_personagens_db():
    """Valida a função do GameController de transferência de itens entre personagens."""
    db = SessionLocal()
    try:
        ctrl = GameController(db)
        chars = db.query(PersonagemDB).all()
        p1 = chars[0]
        p2 = chars[1]

        # Adiciona poção para p1
        ctrl.adicionar_item_personagem_db(p1.id, "Super Poção", 3, "consumivel")

        # Transfere 2 poções de p1 para p2
        sucesso = ctrl.transferir_item_entre_personagens_db(p1.id, p2.id, "Super Poção", 2)
        assert sucesso is True

        db.refresh(p1)
        db.refresh(p2)

        inv1 = {i["nome"]: i["quantidade"] for i in p1.inventario}
        inv2 = {i["nome"]: i["quantidade"] for i in p2.inventario}

        assert inv1.get("Super Poção") == 1
        assert inv2.get("Super Poção") == 2
    finally:
        db.close()
