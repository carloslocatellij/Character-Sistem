import pytest
from app.db.database import Base, engine, SessionLocal
from app.models.equipamentos_db import ItemDB

# Esta rotina roda ANTES dos testes. Ela cria as tabelas no banco de teste.
def setup_module(module):
    #Base.metadata.create_all(bind=engine)
    pass

# Esta rotina roda DEPOIS dos testes. Ela limpa/apaga as tabelas para o próximo teste ser limpo.
def teardown_module(module):
    #Base.metadata.drop_all(bind=engine)
    pass

def test_salvar_e_recuperar_arma_no_banco():
    # 1. Abre a sessão com o banco
    db = SessionLocal()
    
    # 2. Cria um novo registro
    nova_arma = ItemDB(
        nome="Espada Longa de Aço",
        categoria="arma",
        peso=2.5,
        emoji="🗡️",
        dano=6,
        tipo_ataque="corpo"
    )
    
    # 3. Salva no banco (Commit)
    db.add(nova_arma)
    db.commit()
    
    # 4. Faz uma consulta (Query) para buscar a arma recém-criada
    arma_salva = db.query(ItemDB).filter(ItemDB.nome == "Espada Longa de Aço").first()
    
    # 5. Valida se os dados voltaram corretamente do banco SQLite
    assert arma_salva is not None
    assert arma_salva.id == 1
    assert arma_salva.dano == 6
    assert arma_salva.categoria == "arma"
    
    db.close()