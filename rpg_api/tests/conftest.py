# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.database import Base
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB


@pytest.fixture(scope="function")
def test_db():
    """Cria um banco de dados SQLite em memória para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def raca_default(test_db):
    """Fixture: Raça padrão para testes."""
    raca = RacaDB(
        nome="Élfo",
        bonus_atributos={
            "forca": 1,
            "agilidade": 3,
            "resistencia": 2,
            "percepcao": 3,
            "exuberancia": 1
        },
        emoji="🧝"
    )
    test_db.add(raca)
    test_db.commit()
    return raca


@pytest.fixture
def classe_default(test_db):
    """Fixture: Classe padrão para testes."""
    classe = ClasseRPGDB(
        nome="Arqueiro",
        bonus_caminhos={"ar": 2, "fogo": 1},
        habilidades=["Tiro Preciso", "Visão Aguçada"]
    )
    test_db.add(classe)
    test_db.commit()
    return classe


@pytest.fixture
def personagem_default(test_db, raca_default, classe_default):
    """Fixture: Personagem padrão para testes."""
    personagem = PersonagemDB(
        nome="Legolas",
        raca_id=raca_default.id,
        classe_id=classe_default.id,
        usuario_id=1, cenario_id=1,
        forca_base=2,
        agilidade_base=5,
        resistencia_base=3,
        percepcao_base=4,
        exuberancia_base=2,
        nivel=1
    )
    test_db.add(personagem)
    test_db.commit()
    return personagem


@pytest.fixture
def item_arma(test_db):
    """Fixture: Arma de teste."""
    arma = ItemDB(
        nome="Arco Élfico",
        categoria="arma",
        dano=8,
        tipo_ataque="Distancia",
        emoji="🏹",
        defesa=0,
        defesa_extra=None
    )
    test_db.add(arma)
    test_db.commit()
    return arma


@pytest.fixture
def item_escudo(test_db):
    """Fixture: Escudo de teste."""
    escudo = ItemDB(
        nome="Escudo de Madeira",
        categoria="escudo",
        dano=0,
        tipo_ataque=None,
        emoji="🛡️",
        defesa=0,
        defesa_extra=5
    )
    test_db.add(escudo)
    test_db.commit()
    return escudo


@pytest.fixture
def item_armadura(test_db):
    """Fixture: Armadura de teste."""
    armadura = ItemDB(
        nome="Túnica de Couro",
        categoria="armadura",
        dano=0,
        tipo_ataque=None,
        emoji="🧥",
        defesa=3,
        defesa_extra=None
    )
    test_db.add(armadura)
    test_db.commit()
    return armadura