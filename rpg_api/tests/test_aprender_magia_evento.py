import pytest
import esper
from app.db.database import SessionLocal, engine, Base
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.entities.habilidades_magias import Magia
from app.core.engine.components import StatsComponent, HeroComponent, InventoryComponent
from app.core.engine.systems import EventSystem, InventarySystem
from app.core.engine.game_state import GameStateManager

@pytest.fixture(autouse=True)
def setup_world():
    esper.clear_database()
    Base.metadata.create_all(bind=engine)
    yield
    esper.clear_database()
    Base.metadata.drop_all(bind=engine)

def test_aprender_magia_evento_sucesso_e_falha():
    logs = []
    def log_cb(msg, notif=False):
        logs.append(msg)

    inv_sys = InventarySystem()
    game_state = GameStateManager()
    evt_sys = EventSystem(inv_sys, game_state, log_cb)


    # 1. Herói Mago com Bônus de Fogo +1 da Classe e Exuberância = 2
    raca = Raca("Humano")
    classe_mago = ClasseRPG("Aprendiz de Fogo", bonus_caminhos={"fogo": 1})
    mago = Personagem("Merlin", 1, raca, classe_mago, 1, 1, 1, 1, exub_base=2)

    # Cria entidade ID 1 no Esper com HeroComponent e StatsComponent
    if esper.entity_exists(1):
        esper.delete_entity(1)
    
    ent_id = esper.create_entity(
        HeroComponent(personagem=mago),
        StatsComponent("Merlin", "Aprendiz de Fogo", mago.pv_atual, mago.max_hp, mago.pm_atual, mago.max_mp, 2, 0),
        InventoryComponent(itens=[])
    )
    assert ent_id == 1

    # 2. Magia 1: Chama Simples (Exige Fogo 1, Exub 1) -> Válida para o Merlin!
    comando_sucesso = {
        "tipo": "aprender_magia",
        "dados": {
            "magia_nome": "Chama Simples",
            "custo_pm": 2,
            "requisito_caminhos": {"fogo": 1},
            "requisito_exuberancia": 1
        }
    }
    evt_sys._processar_comando_individual(comando_sucesso)

    assert len(mago.magias_conhecidas) == 1
    assert mago.magias_conhecidas[0].nome == "Chama Simples"
    assert any("Merlin aprendeu a magia 'Chama Simples'" in l for l in logs)

    # 3. Magia 2: Tempestade de Gelo (Exige Água 3) -> Merlin tem Água 0, deve Falhar!
    comando_falha = {
        "tipo": "aprender_magia",
        "dados": {
            "magia_nome": "Tempestade de Gelo",
            "custo_pm": 5,
            "requisito_caminhos": {"água": 3},
            "requisito_exuberancia": 2
        }
    }
    evt_sys._processar_comando_individual(comando_falha)

    assert len(mago.magias_conhecidas) == 1 # Não adicionou a segunda magia!
    assert any("Requisitos insuficientes" in l for l in logs)
