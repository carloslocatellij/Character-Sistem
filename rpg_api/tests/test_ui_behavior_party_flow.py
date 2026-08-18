"""
Testes de Comportamento e Interface de Usuário (Item 4 da Regra 7 - TDD / Textual Pilot)

Valida o fluxo ponta a ponta da interface de usuário da aplicação RPGApp,
a navegação entre telas, a gestão de equipes, a transferência de itens e comandos in-game,
garantindo integridade de banco de dados e ausência de OperationalError (como colunas ausentes).
"""
import os
import pytest
from textual.app import App
from textual.widgets import ListView, Input
from app.db.database import SessionLocal, Base, engine, garantir_schema_atualizado
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, EquipeMembroDB
from main_cli import RPGApp, MainScreen
from app.views.party_management_screen import PartyManagementScreen
from app.views.game_play_screen import GamePlayScreen


@pytest.fixture(autouse=True)
def setup_teardown_db():
    """Garante schema atualizado com todas as colunas e seed antes de rodar os testes."""
    garantir_schema_atualizado(engine)
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
async def test_ui_behavior_navegacao_menu_principal_para_party():
    """
    Item 4 Regra 7: Teste de Comportamento de UI do Menu Principal para Gestão de Equipe.
    Arrange: Inicia o aplicativo principal RPGApp.
    Act: Simula o clique do usuário no botão de Gestão de Equipe '#menu-equipe'.
    Assert: Verifica que a PartyManagementScreen foi empilhada e carregou dados sem erro.
    """
    app = RPGApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        # 1. Arrange: Verifica que a tela inicial é a MainScreen
        assert isinstance(app.screen, MainScreen)

        # 2. Act: Clica no botão de Gerenciar Equipe no Menu Principal
        await pilot.click("#menu-equipe")
        await pilot.pause()

        # 3. Assert: A tela ativa deve ser a PartyManagementScreen
        assert isinstance(app.screen, PartyManagementScreen)
        assert app.screen.query_one("#party-dialog") is not None

        # Verifica se os membros ativos e reservas foram carregados das colunas do banco
        list_ativos = app.screen.query_one("#list-membros-ativos")
        assert list_ativos is not None
        assert len(list_ativos.children) >= 1

        # Fecha o modal clicando em voltar
        await pilot.click("#btn-fechar-party")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)


@pytest.mark.anyio
async def test_ui_behavior_movimentacao_membros_party_screen():
    """
    Item 4 Regra 7: Simula interação com teclas e botões dentro da PartyManagementScreen.
    Arrange: Abre a PartyManagementScreen.
    Act: Seleciona membro ativo, clica para mover para reserva, depois promove de volta.
    Assert: Verifica mudança de estados dos botões e transição de listas.
    """
    screen = PartyManagementScreen()

    class TestApp(App):
        CSS_PATH = os.path.abspath("rpg_api/app/views/styles/party_styles.css")
        def on_mount(self):
            self.push_screen(screen)

    test_app = TestApp()

    async with test_app.run_test() as pilot:
        await pilot.pause()

        list_ativos = screen.query_one("#list-membros-ativos", ListView)
        if list_ativos.children:
            # 1. Destaca o primeiro item ativo
            primeiro_ativo = list_ativos.children[0]
            screen.on_ativo_highlighted(ListView.Highlighted(list_ativos, primeiro_ativo))
            await pilot.pause()

            btn_reserva = screen.query_one("#btn-mover-reserva")
            assert btn_reserva.disabled is False

            # Clica no botão mover reserva
            await pilot.click("#btn-mover-reserva")
            await pilot.pause()

            # Verifica que a lista de reservas possui o membro
            list_reservas = screen.query_one("#list-membros-reserva", ListView)
            assert len(list_reservas.children) >= 1

            # Seleciona o membro na reserva
            primeiro_reserva = list_reservas.children[0]
            screen.on_reserva_highlighted(ListView.Highlighted(list_reservas, primeiro_reserva))
            await pilot.pause()

            btn_ativa = screen.query_one("#btn-mover-ativa")
            assert btn_ativa.disabled is False

            # Clica para retornar à ativa
            await pilot.click("#btn-mover-ativa")
            await pilot.pause()


@pytest.mark.anyio
async def test_ui_behavior_comando_party_em_gameplay():
    """
    Item 4 Regra 7: Testa abertura da tela de equipe a partir do comando /party no terminal de gameplay.
    Arrange: Inicia GamePlayScreen em app de teste.
    Act: Submete o comando '/party' no prompt do terminal.
    Assert: Verifica que o modal PartyManagementScreen foi aberto sobre a tela de jogo sem erros de SQL.
    """
    screen = GamePlayScreen()

    class GameplayTestApp(App):
        CSS_PATH = [
            os.path.abspath("rpg_api/app/views/styles/styles.css"),
            os.path.abspath("rpg_api/app/views/styles/party_styles.css"),
        ]
        def on_mount(self):
            self.push_screen(screen)

    app = GameplayTestApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        # Localiza e submete o comando no prompt
        prompt = screen.query_one("#terminal-prompt", Input)
        prompt.value = "/party"
        screen.processar_comando_terminal(Input.Submitted(prompt, value="/party"))
        await pilot.pause()

        # Verifica se PartyManagementScreen está ativa no topo da pilha
        assert isinstance(app.screen, PartyManagementScreen)
        assert app.screen.query_one("#party-dialog") is not None
