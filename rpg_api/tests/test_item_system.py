import pytest
import esper
from app.db.database import Base, engine, SessionLocal
from app.models.equipamentos_db import ItemDB
from app.core.engine.components import StatsComponent, InventoryComponent, EquipmentComponent
from app.core.engine.item_system import (
    garantir_itens_padrao,
    obter_todos_itens_db,
    obter_itens_usaveis,
    obter_equipamentos_inventario,
    aplicar_usar_item,
    aplicar_equipar_item,
    aplicar_desequipar_item,
)
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.engine.systems import BattleSystem


@pytest.fixture(autouse=True)
def setup_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_garantir_itens_padrao_popula_banco():
    with SessionLocal() as db:
        itens = garantir_itens_padrao(db)
        assert len(itens) >= 5
        nomes = [i.nome for i in itens]
        assert "Poção de Cura" in nomes
        assert "Espada Longa" in nomes
        assert "Armadura de Aço" in nomes


def test_usar_item_recupera_hp():
    stats = StatsComponent(
        nome="Heroi", classe="Guerreiro", hp=10, max_hp=50, mp=10, max_mp=20,
        ataque_base=5, defesa_base=2
    )
    inv = InventoryComponent(itens={"Poção de Cura": 2})

    sucesso, msg = aplicar_usar_item(stats, inv, "Poção de Cura")
    assert sucesso is True
    assert stats.hp == 30
    assert inv.itens.get("Poção de Cura", 0) == 1
    assert "Recuperou 20 HP" in msg


def test_usar_item_recupera_mp():
    stats = StatsComponent(
        nome="Mago", classe="Mago", hp=50, max_hp=50, mp=5, max_mp=30,
        ataque_base=2, defesa_base=1
    )
    inv = InventoryComponent(itens={"Poção de Mana": 1})

    sucesso, msg = aplicar_usar_item(stats, inv, "Poção de Mana")
    assert sucesso is True
    assert stats.mp == 20
    assert "Poção de Mana" not in inv.itens
    assert "Recuperou 15 MP" in msg


def test_equipar_e_desequipar_item():
    eqp = EquipmentComponent()
    inv = InventoryComponent(itens={"Espada Longa": 1, "Armadura de Aço": 1})

    # Equipar arma
    sucesso_arma, msg_arma = aplicar_equipar_item(eqp, inv, "Espada Longa")
    assert sucesso_arma is True
    assert eqp.arma is not None
    assert eqp.arma["nome"] == "Espada Longa"
    assert "Espada Longa" not in inv.itens

    # Equipar armadura
    sucesso_arm, msg_arm = aplicar_equipar_item(eqp, inv, "Armadura de Aço")
    assert sucesso_arm is True
    assert eqp.armadura is not None
    assert eqp.armadura["nome"] == "Armadura de Aço"
    assert "Armadura de Aço" not in inv.itens

    # Desequipar arma
    sucesso_des, msg_des = aplicar_desequipar_item(eqp, inv, "arma")
    assert sucesso_des is True
    assert eqp.arma is None
    assert inv.itens.get("Espada Longa") == 1


def test_trocar_equipamento_devolve_anterior_ao_inventario():
    eqp = EquipmentComponent(arma={"nome": "Espada Curta", "bonus_atk": 2, "tipo": "corpo"})
    inv = InventoryComponent(itens={"Espada Longa": 1})

    sucesso, msg = aplicar_equipar_item(eqp, inv, "Espada Longa")
    assert sucesso is True
    assert eqp.arma["nome"] == "Espada Longa"
    # A espada antiga deve ter voltado para o inventário
    assert inv.itens.get("Espada Curta") == 1
    assert "Espada Longa" not in inv.itens


def test_batalha_usar_item_especifico():
    esper.clear_database()
    heroi = Personagem(
        nome="Heroi", nivel=1, raca=Raca("Humano", {}, "🧙"),
        classe_rpg=ClasseRPG("Guerreiro", {}, []),
        forca_base=5, agilidade_base=3, res_base=4, perc_base=2, exub_base=1
    )
    inimigo = Personagem(
        nome="Goblin", nivel=1, raca=Raca("Goblin", {}, "👹"),
        classe_rpg=ClasseRPG("Monstro", {}, []),
        forca_base=1, agilidade_base=1, res_base=1, perc_base=1, exub_base=1
    )

    heroi.pv_atual = 10
    heroi.pm_atual = 5

    try:
        esper.components_for_entity(1)
    except KeyError:
        esper.create_entity()

    inv = InventoryComponent(itens={"Poção de Mana": 2, "Poção de Cura": 1})
    esper.add_component(1, inv)

    battle_sys = BattleSystem()
    battle_sys.iniciar_combate(heroi, [inimigo])

    # Executa a ação de usar "Poção de Mana" na batalha
    battle_sys.executar_acao_jogador("item", nome_item="Poção de Mana")

    assert battle_sys.heroi.pm_atual == min(heroi.max_mp, 20)
    assert inv.itens.get("Poção de Mana") == 1
