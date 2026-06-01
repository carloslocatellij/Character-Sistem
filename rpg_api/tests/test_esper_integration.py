# rpg_api/tests/test_esper_integration.py
import pytest
import esper
from app.db.database import SessionLocal, Base, engine
from app.models import MapaDB, EventoDB
from app.core.engine.components import PositionComponent, RenderComponent, InteractableComponent
from app.core.engine.engine_loader import GameEngineLoader


# Esta rotina roda ANTES dos testes. Ela cria as tabelas no banco de teste.
def setup_module(module):
    Base.metadata.create_all(bind=engine)
    pass

# Esta rotina roda DEPOIS dos testes. Ela limpa/apaga as tabelas para o próximo teste ser limpo.


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)
    pass


def test_deve_carregar_mapa_do_bd_e_popular_o_mundo_esper():
    """
    Garante que o GameEngineLoader consegue ler o banco de dados
    e instanciar corretamente as entidades no contexto global do Esper.
    """
    # 1. Limpa o mundo global do Esper para isolar o teste
    esper.switch_world(esper.list_worlds()[0])

    with SessionLocal() as db:
        # 2. SETUP: Criar cenário de teste no Banco de Dados
        novo_mapa = MapaDB(
            nome="Masmorra do Esper",
            tipo="caverna",
            altura=2,
            largura=2,
            mapa_em_si=[["  ", "  "], ["  ", "  "]],
            objetos={"1,1": "🧱"},
            cenario_id=1
        )
        db.add(novo_mapa)
        db.commit()
        db.refresh(novo_mapa)

        evento_bau = EventoDB(
            mapa_id=novo_mapa.id,
            nome="Baú Secreto",
            emoji="📦",
            pos_x=0,
            pos_y=1,
            tipo_evento="bau",
            parametros={"recompensa": "Espada de Bronze"}
        )
        db.add(evento_bau)
        db.commit()

        # 3. AÇÃO: Instanciar o carregador e carregar o mapa
        loader = GameEngineLoader()
        sucesso = loader.carregar_mapa(db, novo_mapa.id)

        # 4. VALIDAÇÕES:
        assert sucesso is True
        assert loader.altura == 2
        assert loader.camada_objetos[(1, 1)] == "🧱"

        # 5. ASSERÇÕES NO ESPER: O Esper registou a entidade?
        # Procuramos todas as entidades que contêm o PositionComponent
        entidades_com_posicao = esper.get_components(PositionComponent)
        assert len(entidades_com_posicao) == 1

        # Desempacotamos o ID da entidade e a instância do componente
        entidade_id, pos = entidades_com_posicao[0]
        
        # Recuperamos os outros componentes acoplados a esse mesmo ID no Esper
        ren = esper.component_for_entity(entidade_id, RenderComponent)
        interact = esper.component_for_entity(entidade_id, InteractableComponent)
        
        assert pos[0].x == 0 and pos[0].y == 1
        assert ren.emoji == "📦"
        assert interact.event_type == "bau"
        assert interact.parameters["recompensa"] == "Espada de Bronze"