import pytest
from app.db.database import Base, engine, SessionLocal
from app.models.equipamentos_db import ItemDB
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB 

# Esta rotina roda ANTES dos testes. Ela cria as tabelas no banco de teste.
def setup_module(module):
    Base.metadata.create_all(bind=engine)
    pass

# Esta rotina roda DEPOIS dos testes. Ela limpa/apaga as tabelas para o próximo teste ser limpo.
def teardown_module(module):
    Base.metadata.drop_all(bind=engine)
    pass

def test_salvar_e_recuperar_arma_no_banco():
    # 1. Abre a sessão com o banco
    with SessionLocal() as db:
        
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
        
# rpg_api/tests/test_database.py



def test_salvar_e_recuperar_evento_no_mapa():
    with SessionLocal() as db:
        # 1. Criamos um Mapa para servir de "Pai" do evento
        novo_mapa = MapaDB(
            nome="Caverna do Iniciante",
            tipo="caverna",
            altura=10,
            largura=10,
            mapa_em_si=[["  " for _ in range(10)] for _ in range(10)]
        )
        db.add(novo_mapa)
        db.commit()
        db.refresh(novo_mapa) # Atualiza para pegarmos o ID gerado (novo_mapa.id)

        # 2. Criamos o Evento (Ex: Um Baú)
        novo_evento = EventoDB(
            mapa_id=novo_mapa.id,
            nome="Baú de Madeira",
            emoji="📦",
            pos_x=5,
            pos_y=5,
            event_type="bau",
            # No engine, estes parâmetros vão alimentar o InteractableComponent
            parametros={"item_id": 1, "quantidade": 1, "mensagem": "Você encontrou uma Poção!"} 
        )
        db.add(novo_evento)
        db.commit()

        # 3. Consultamos o evento no banco
        evento_salvo = db.query(EventoDB).filter(EventoDB.nome == "Baú de Madeira").first()

        # 4. Asserções (Validações)
        assert evento_salvo is not None
        assert evento_salvo.mapa_id == novo_mapa.id
        assert evento_salvo.event_type == "bau"
        assert evento_salvo.parametros["item_id"] == 1