import pytest
import esper
import os
import random
from textual.app import App, ComposeResult
from app.core.entities.personagens import Personagem, Raca, ClasseRPG, Party
from app.core.entities.habilidades_magias import Magia
from app.core.engine.systems import BattleSystem
from app.views.battle_screen import BattleScreen, BarraStatusCombate, CombatenteSprite, UsarMagiaBatalhaModal, UsarItemBatalhaModal

class DummyBattleApp(App):
    """App de teste Textual para rodar BattleScreen com pilot."""
    CSS_PATH = os.path.abspath("rpg_api/app/views/styles/battle_styles.css")
    def __init__(self, screen_to_test):
        super().__init__()
        self.screen_to_test = screen_to_test

    def on_mount(self):
        self.push_screen(self.screen_to_test)

@pytest.fixture
def party_4_aliados():
    raca_hum = Raca("Humano", bonus_atributos={"forca": 1})
    raca_elfo = Raca("Elfo", bonus_atributos={"destreza": 2})

    cls_g = ClasseRPG("Guerreiro")
    cls_c = ClasseRPG("Clérigo", bonus_caminhos={"luz": 2})
    cls_l = ClasseRPG("Ladino")
    cls_m = ClasseRPG("Mago", bonus_caminhos={"fogo": 2})

    p1 = Personagem("Artorias", 2, raca_hum, cls_g, 4, 2, 3, 2, 2)
    p2 = Personagem("Aerith", 2, raca_elfo, cls_c, 2, 3, 2, 3, 4)
    p3 = Personagem("Locke", 2, raca_hum, cls_l, 2, 5, 2, 4, 2)
    p4 = Personagem("Vivi", 2, raca_hum, cls_m, 1, 1, 2, 3, 4)

    for p in [p1, p2, p3, p4]:
        p.reset_status()

    p1.adicionar_item_inventario("Poção de Vida", 2)
    p2.aprender_magia(Magia("Cura Sagrada", custo_pm=3, cura_base=10))

    party = Party()
    for p in [p1, p2, p3, p4]:
        party.adicionar_membro(p)
    return party

@pytest.fixture
def inimigos_4():
    return [
        {"nome": "Orc Chefe", "raca": "Monstro", "classe": "Monstro", "emoji": "👹", "pv_atual": 40, "forca": 3, "agilidade": 2, "resistencia": 2, "percepcao": 1, "exuberancia": 0},
        {"nome": "Goblin", "raca": "Monstro", "classe": "Monstro", "emoji": "👺", "pv_atual": 25, "forca": 2, "agilidade": 4, "resistencia": 1, "percepcao": 1, "exuberancia": 0},
        {"nome": "Esqueleto", "raca": "Monstro", "classe": "Monstro", "emoji": "💀", "pv_atual": 20, "forca": 2, "agilidade": 1, "resistencia": 1, "percepcao": 1, "exuberancia": 0},
        {"nome": "Xamã", "raca": "Monstro", "classe": "Monstro", "emoji": "🧙‍♂️", "pv_atual": 30, "forca": 1, "agilidade": 3, "resistencia": 2, "percepcao": 2, "exuberancia": 1},
    ]


@pytest.fixture
def isolamento_esper():
    world_nome = f"teste_screen_{random.randint(1000, 999999)}"
    esper.switch_world(world_nome)
    yield
    try:
        esper.switch_world("default")
        esper.delete_world(world_nome)
    except Exception:
        pass


@pytest.mark.anyio
async def test_battle_screen_renderiza_4_aliados_e_4_inimigos(party_4_aliados, inimigos_4, isolamento_esper):
    """Valida composição da TUI: timeline, 4 barras de aliados, 4 barras de inimigos e sprites."""
    bs = BattleSystem()
    esper.add_processor(bs)

    screen = BattleScreen(party_4_aliados, inimigos_4)
    app = DummyBattleApp(screen)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Verifica Timeline
        timeline_lbl = screen.query_one("#lbl-timeline-turnos")
        assert timeline_lbl is not None

        # Verifica 4 barras de aliados
        for i in range(4):
            barra_aliado = screen.query_one(f"#barra-aliado-{i}", BarraStatusCombate)
            assert barra_aliado is not None
            sprite_aliado = screen.query_one(f"#sprite-aliado-{i}", CombatenteSprite)
            assert sprite_aliado is not None

        # Verifica 4 barras de inimigos
        for i in range(4):
            barra_inimigo = screen.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
            assert barra_inimigo is not None
            sprite_inimigo = screen.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
            assert sprite_inimigo is not None

        # Verifica Painel de Ações
        assert screen.query_one("#btn-confirmar-acao") is not None
        assert screen.query_one("#action-radioset") is not None


@pytest.mark.anyio
async def test_battle_screen_destaca_combatente_ativo(party_4_aliados, inimigos_4, isolamento_esper):
    """Valida que o aliado cujo turno está ativo recebe destaque visual e atualiza a UI."""
    bs = BattleSystem()
    esper.add_processor(bs)

    screen = BattleScreen(party_4_aliados, inimigos_4)
    app = DummyBattleApp(screen)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Dispara evento simulado de turno de Locke (índice 2)
        esper.dispatch_event("turno_iniciado", {
            "turno": 1,
            "rodada": 1,
            "combatente_ativo": party_4_aliados.membros[2],
            "tipo": "aliado",
            "indice_time": 2,
            "e_aliado": True,
            "aliados": bs._snapshot_aliados(),
            "inimigos": bs._snapshot_inimigos(),
            "fila_turnos": bs._snapshot_fila_turnos(),
        })
        await pilot.pause()

        barra_locke = screen.query_one("#barra-aliado-2", BarraStatusCombate)
        assert "combatente-ativo" in barra_locke.classes
        assert screen.turno_liberado is True

        lbl_turno = screen.query_one("#action-turn-label")
        assert "Locke" in str(lbl_turno.render())


@pytest.mark.anyio
async def test_modal_magia_e_item_batalha(party_4_aliados, isolamento_esper):
    """Valida abertura e listagem nos modais contextuais."""
    magias = [Magia("Cura Sagrada", custo_pm=3, cura_base=12)]
    modal_magia = UsarMagiaBatalhaModal(magias)

    app_magia = DummyBattleApp(modal_magia)
    async with app_magia.run_test() as pilot:
        await pilot.pause()
        assert modal_magia.query_one("#list-magias-batalha") is not None

    itens = [{"nome": "Poção de Vida", "quantidade": 2, "emoji": "🧪", "descricao": "Cura 20 HP"}]
    modal_item = UsarItemBatalhaModal(itens)

    app_item = DummyBattleApp(modal_item)
    async with app_item.run_test() as pilot:
        await pilot.pause()
        assert modal_item.query_one("#list-itens-batalha") is not None
