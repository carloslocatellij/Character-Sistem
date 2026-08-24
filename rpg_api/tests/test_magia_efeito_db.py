import pytest
from app.db.database import SessionLocal, engine, Base
from app.models.habilidades_magias_db import EfeitoDB, MagiaDB
from app.controllers.game_controller import GameController

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_criacao_e_mapeamento_efeito_e_magia_db():
    with SessionLocal() as db:
        # 1. Cria EfeitoDB
        efeito_db = EfeitoDB(
            nome="Queimadura Grave",
            duracao_turnos=3,
            tipo="dano_continuo",
            valor=4,
            configuracoes={"elemento": "fogo"}
        )
        db.add(efeito_db)
        db.commit()
        db.refresh(efeito_db)

        assert efeito_db.id is not None

        # 2. Cria MagiaDB associada ao EfeitoDB
        msg = GameController.criar_magia(
            db=db,
            nome="Bola de Fogo Suprema",
            custo_pm=5,
            requisito_caminhos={"fogo": 2},
            requisito_exuberancia=2,
            dano_base=10,
            cura_base=0,
            dano_area=True,
            tipo_execucao="combate",
            descricao="Lança uma enorme esfera de fogo.",
            propriedades_combate={"critico_ampliado": True},
            efeito_id=efeito_db.id
        )
        assert "salva com sucesso" in msg

        # 3. Busca MagiaDB e testa conversão para domínio
        magia_db = db.query(MagiaDB).filter_by(nome="Bola de Fogo Suprema").first()
        assert magia_db is not None
        assert magia_db.dano_area is True

        magia_dom = GameController.converter_magia_db_para_dominio(magia_db)
        assert magia_dom.nome == "Bola de Fogo Suprema"
        assert magia_dom.custo_pm == 5
        assert magia_dom.requisito_caminhos == {"fogo": 2}
        assert magia_dom.dano_area is True
        assert magia_dom.tipo_execucao == "combate"
        assert magia_dom.efeito_aplicado is not None
        assert magia_dom.efeito_aplicado.nome == "Queimadura Grave"
        assert magia_dom.efeito_aplicado.valor == 4
