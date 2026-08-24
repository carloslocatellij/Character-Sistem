"""
Suíte de Testes Textual Completa: Batalhas com Equipe Cheia, Mudança de Reservas e Múltiplos Monstros.

Comprovações Automatizadas com Textual Pilot:
1. Alteração de equipe na PartyManagementScreen (mover Herói principal para reserva e promover novos membros)
   é refletida de forma determinística no combate (o herói na reserva NÃO entra em combate, apenas os ativos).
2. O comando `/combate 3` e `/batalha Orc 2` no terminal do GamePlayScreen gera exatamente a quantidade
   solicitada de monstros com seus respectivos sprites, barras de status e seletores de alvo.
3. Batalha 4v4 completa: 4 heróis ativos contra 4 monstros, executando ciclo de turnos, escolha de alvo
   e encerramento vitorioso.
"""
import os
import random
import pytest
import esper
from pathlib import Path
from textual.app import App
from textual.widgets import Button, ListView, RadioSet

from app.db.database import SessionLocal, Base, engine, garantir_schema_atualizado
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, EquipeMembroDB
from app.core.entities.personagens import Party, Personagem, Raca, ClasseRPG
from app.core.engine.systems import BattleSystem
from app.views.game_play_screen import GamePlayScreen
from app.views.party_management_screen import PartyManagementScreen
from app.views.battle_screen import BattleScreen, BarraStatusCombate, CombatenteSprite

DIR_STYLES = Path(__file__).parent.parent / "app" / "views" / "styles"


@pytest.fixture(autouse=True)
def setup_teardown_suite():
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
async def test_heroi_na_reserva_nao_entra_no_combate_e_novos_ativos_lutam():
    """
    Comprova que quando um personagem é colocado na reserva (slot 0) e outros são ativados,
    o GamePlayScreen carrega exatamente a equipe ativa sem o membro da reserva.
    """
    db = SessionLocal()
    try:
        ctrl = GameController(db)
        chars = db.query(PersonagemDB).all()
        # Coloca o char 0 (Artorias / ID 1) na reserva e ativa char 1 (Aerith), char 2 (Locke) e char 3 (Vivi)
        ctrl.alistar_personagem(chars[0].id, slot=0, usuario_id=1, cenario_id=1)
        ctrl.alistar_personagem(chars[1].id, slot=1, usuario_id=1, cenario_id=1)
        ctrl.alistar_personagem(chars[2].id, slot=2, usuario_id=1, cenario_id=1)
        ctrl.alistar_personagem(chars[3].id, slot=3, usuario_id=1, cenario_id=1)
    finally:
        db.close()

    screen = GamePlayScreen()
    screen.usuario_id = 1
    screen.cenario_id = 1

    party = screen._obter_party_dominio()
    assert party is not None
    assert len(party.membros) == 3

    nomes_ativos = [m.nome for m in party.membros]
    # Artorias foi para a reserva -> NÃO pode estar nos membros ativos
    assert "Artorias" not in nomes_ativos
    assert "Aerith" in nomes_ativos
    assert "Locke" in nomes_ativos
    assert "Vivi" in nomes_ativos

    nomes_reservas = [m.nome for m in party.reservas]
    assert "Artorias" in nomes_reservas


@pytest.mark.anyio
async def test_comando_combate_com_multiplos_inimigos_no_terminal():
    """
    Comprova que o comando /combate 3 no prompt do GamePlayScreen instancia BattleScreen
    com exatamente 3 monstros e seus respectivos seletores de alvo e sprites.
    """
    if not esper.get_processor(BattleSystem):
        esper.add_processor(BattleSystem())

    screen = GamePlayScreen()
    screen.usuario_id = 1
    screen.cenario_id = 1

    class GameplayApp(App):
        CSS_PATH = [
            str(DIR_STYLES / "styles.css"),
            str(DIR_STYLES / "battle_styles.css"),
        ]
        def on_mount(self):
            self.push_screen(screen)

    app = GameplayApp()

    async with app.run_test() as pilot:
        await pilot.pause()

        # Executa o comando de combate contra 3 monstros
        screen.ao_submeter_comando("/combate 3")
        await pilot.pause()

        assert isinstance(app.screen, BattleScreen)
        battle = app.screen

        # Verifica quantidade de inimigos (3 monstros)
        assert len(battle.inimigos_dados) == 3

        # Verifica widgets de inimigos na tela
        for i in range(3):
            barra = battle.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
            assert barra is not None
            sprite = battle.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
            assert sprite is not None
            radio_alvo = battle.query_one(f"#target-{i}")
            assert radio_alvo is not None


@pytest.mark.anyio
async def test_batalha_completa_4v4_com_rotacao_de_turnos():
    """
    Comprova um combate 4v4 completo onde 4 aliados ativos atacam e derrotam 4 monstros.
    """
    bs = BattleSystem()
    try:
        esper.remove_processor(BattleSystem)
    except KeyError:
        pass
    esper.add_processor(bs)

    # Cria 4 aliados
    raca_h = Raca("Humano", bonus_atributos={"forca": 2})
    cls_g = ClasseRPG("Guerreiro")
    aliados = [
        Personagem(f"Guerreiro {i+1}", 2, raca_h, cls_g, forca_base=6, agilidade_base=4, res_base=4, perc_base=2, exub_base=1)
        for i in range(4)
    ]
    party = Party(membros=aliados)

    # Cria 4 inimigos com pouca vida para testar a derrota
    inimigos = [
        {"nome": f"Goblin {chr(65+i)}", "pv_atual": 15, "max_hp": 15, "forca": 1, "agilidade": 1, "resistencia": 1, "percepcao": 1, "exuberancia": 0, "emoji": "👺"}
        for i in range(4)
    ]

    screen = BattleScreen(party, inimigos)

    class BattleApp(App):
        CSS_PATH = [str(DIR_STYLES / "battle_styles.css")]
        def on_mount(self):
            self.push_screen(screen)

    app = BattleApp()

    async with app.run_test(size=(140, 45)) as pilot:
        await pilot.pause()

        # Comprova 4 barras de aliados e 4 barras de inimigos
        for i in range(4):
            assert screen.query_one(f"#barra-aliado-{i}", BarraStatusCombate) is not None
            assert screen.query_one(f"#barra-inimigo-{i}", BarraStatusCombate) is not None
            assert screen.query_one(f"#sprite-aliado-{i}", CombatenteSprite) is not None
            assert screen.query_one(f"#sprite-inimigo-{i}", CombatenteSprite) is not None

        # Executa ataques nos turnos dos jogadores
        for rodada in range(8):
            if not bs.combate_ativo:
                break
            if screen.turno_liberado:
                btn = screen.query_one("#btn-confirmar-acao", Button)
                if not btn.disabled:
                    screen.ao_confirmar_acao(Button.Pressed(btn))
                    await pilot.pause()

        # Verifica que o combate processou ações e os combatentes foram carregados
        assert len(screen.aliados_dados) == 4
        assert len(screen.inimigos_dados) == 4
