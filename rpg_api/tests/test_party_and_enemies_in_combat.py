"""
Testes de Integração de Múltiplos Aliados e Inimigos no Combate (BattleScreen & GamePlayScreen)

Valida que:
1. Quando o jogador possui equipe alistada na tabela equipe_membros, todos os membros ativos (até 4) entram no combate na BattleScreen.
2. Combates com múltiplos inimigos (1 a 4) são inicializados corretamente com seus respectivos status e sprites na BattleScreen.
3. A ArenaScreen permite iniciar combate interativo visual 4v4 a partir do menu.
"""
import os
import pytest
import esper
from textual.app import App
from textual.widgets import Button
from app.db.database import SessionLocal, Base, engine, garantir_schema_atualizado
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, EquipeMembroDB
from app.core.entities.personagens import Party, Personagem
from app.core.engine.systems import BattleSystem
from app.views.game_play_screen import GamePlayScreen
from app.views.battle_screen import BattleScreen, BarraStatusCombate, CombatenteSprite
from main_cli import RPGApp, ArenaScreen


@pytest.fixture(autouse=True)
def setup_teardown_db():
    garantir_schema_atualizado(engine)
    db = SessionLocal()
    try:
        GameController.garantir_dados_iniciais_completos(db)
        ctrl = GameController(db)
        chars = db.query(PersonagemDB).all()
        # Alista 4 membros na equipe ativa
        for idx, c in enumerate(chars[:4]):
            ctrl.alistar_personagem(c.id, slot=idx+1, usuario_id=1, cenario_id=1)
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
async def test_gameplay_carrega_equipe_completa_de_4_aliados_no_combate():
    """Valida que o GamePlayScreen carrega a equipe de 4 membros de equipe_membros ao solicitar combate."""
    screen = GamePlayScreen()
    screen.usuario_id = 1
    screen.cenario_id = 1

    party = screen._obter_party_dominio()
    assert party is not None
    assert len(party.membros) == 4
    nomes_membros = [m.nome for m in party.membros]
    assert "Artorias" in nomes_membros
    assert "Aerith" in nomes_membros
    assert "Locke" in nomes_membros
    assert "Vivi" in nomes_membros


@pytest.mark.anyio
async def test_gameplay_solicitar_combate_com_4_aliados_e_4_inimigos():
    """Valida que _ao_solicitar_combate com múltiplos inimigos instancia BattleScreen com 4v4."""
    if not esper.get_processor(BattleSystem):
        esper.add_processor(BattleSystem())

    screen = GamePlayScreen()
    screen.usuario_id = 1
    screen.cenario_id = 1

    from pathlib import Path
    dir_styles = Path(__file__).parent.parent / "app" / "views" / "styles"

    class DummyApp(App):
        CSS_PATH = [
            str(dir_styles / "styles.css"),
            str(dir_styles / "battle_styles.css"),
        ]
        def on_mount(self):
            self.push_screen(screen)

    app = DummyApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        dados_combate = {
            "inimigos": [
                {"nome": "Orc Chefe", "emoji": "👹", "pv_atual": 50, "forca": 4, "agilidade": 2},
                {"nome": "Goblin Atirador", "emoji": "👺", "pv_atual": 25, "forca": 2, "agilidade": 5},
                {"nome": "Xamã Orc", "emoji": "🧙‍♂️", "pv_atual": 30, "forca": 1, "agilidade": 3},
                {"nome": "Lobo Selvagem", "emoji": "🐺", "pv_atual": 35, "forca": 3, "agilidade": 4},
            ]
        }

        screen._ao_solicitar_combate(dados_combate)
        await pilot.pause()

        # BattleScreen deve ser a tela ativa no topo
        assert isinstance(app.screen, BattleScreen)
        battle = app.screen

        # 4 aliados e 4 inimigos carregados
        assert len(battle.aliados_dados) == 4
        assert len(battle.inimigos_dados) == 4

        # Valida que todas as 4 barras de aliados e 4 barras de inimigos existem
        for i in range(4):
            assert battle.query_one(f"#barra-aliado-{i}", BarraStatusCombate) is not None
            assert battle.query_one(f"#barra-inimigo-{i}", BarraStatusCombate) is not None
            assert battle.query_one(f"#sprite-aliado-{i}", CombatenteSprite) is not None
            assert battle.query_one(f"#sprite-inimigo-{i}", CombatenteSprite) is not None


@pytest.mark.anyio
async def test_arena_batalha_visual_interativa_4v4():
    """Valida que o botão de Batalha Visual na ArenaScreen abre BattleScreen com 4v4."""
    if not esper.get_processor(BattleSystem):
        esper.add_processor(BattleSystem())

    arena_screen = ArenaScreen()
    from pathlib import Path
    dir_styles = Path(__file__).parent.parent / "app" / "views" / "styles"

    class ArenaApp(App):
        CSS_PATH = [
            str(dir_styles / "styles.css"),
            str(dir_styles / "battle_styles.css"),
        ]
        def on_mount(self):
            self.push_screen(arena_screen)

    app = ArenaApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        db = SessionLocal()
        try:
            ids = [p.id for p in db.query(PersonagemDB).all()]
        finally:
            db.close()

        # Preenche IDs de aliados e oponentes
        inp_aliados = arena_screen.query_one("#inp-aliados")
        inp_aliados.value = f"{ids[0]}, {ids[1]}, {ids[2]}, {ids[3]}"

        inp_oponentes = arena_screen.query_one("#inp-oponentes")
        inp_oponentes.value = f"{ids[4]}, {ids[5]}"

        # Dispara ação de clique no botão de batalha visual
        btn_visual = arena_screen.query_one("#btn-batalha-visual")
        arena_screen.on_button_pressed(Button.Pressed(btn_visual))
        await pilot.pause()

        # BattleScreen deve ter sido empilhada
        assert isinstance(app.screen, BattleScreen)
        battle = app.screen
        assert len(battle.aliados_dados) == 4
        assert len(battle.inimigos_dados) == 2
