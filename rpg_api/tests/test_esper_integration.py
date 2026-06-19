# rpg_api/tests/test_esper_integration.py
import pytest
import esper
from app.db.database import SessionLocal, Base, engine
from app.models.mapas_db import MapaDB, CenarioDB
from app.models.eventos_db import EventoDB
from app.models.plataforma_db import UsuarioDB
from app.models.personagens_db import PersonagemDB, ClasseRPGDB, RacaDB
from app.core.engine.components import PositionComponent, RenderComponent, InteractableComponent
from app.core.engine.components import StatsComponent, InventoryComponent, EquipmentComponent
from app.core.engine.engine_loader import GameEngineLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Esta rotina roda ANTES dos testes. Ela cria as tabelas no banco de teste.
def setup_module(module):
    Base.metadata.create_all(bind=engine)
    pass

# Esta rotina roda DEPOIS dos testes. Ela limpa/apaga as tabelas para o próximo teste ser limpo.
def teardown_module(module):
    Base.metadata.drop_all(bind=engine)
    pass


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria um banco SQLite isolado em memória para cada teste."""
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionTesting = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)

    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="dados_base")
def fixture_dados_base(db_session):
    """Povoa o banco com os templates base de um cenário (Mundo do Criador)."""
    # 1. Cria o Usuário Criador/Jogador
    usuario = UsuarioDB(username="mestre_rpg",
                        email="mestre@rpg.com", senha_hash="123")
    db_session.add(usuario)
    db_session.commit()

    # 2. Cria o Cenário/Jogo Independente
    cenario = CenarioDB(nome="Crônicas de Arton",
                        descricao="Campanha épica", criador_id=usuario.id)
    db_session.add(cenario)
    db_session.commit()

    # 3. Cria registros necessários de Raça e Classe exigidos pelo GameController relacional
    raca_db = RacaDB(nome="Humano", bonus_atributos={
                     "forca": 0, "agilidade": 0, "resistencia": 0, "percepcao": 0, "exuberancia": 0}, emoji="🧑")
    
    
    classe_db = ClasseRPGDB(
        nome="Mago", bonus_caminhos={}, habilidades=[])
    db_session.add(raca_db)
    db_session.add(classe_db)
    db_session.commit()

    # 4. Cria o Personagem Base na tabela real PersonagemDB usando as propriedades reais e chaves estrangeiras
    personagem = PersonagemDB(
        nome="Charles",
        nivel=1,
        raca_id=raca_db.id,
        classe_id=classe_db.id,
        usuario_id=usuario.id,
        cenario_id=cenario.id,
        forca_base=1,
        agilidade_base=2,
        resistencia_base=1,
        percepcao_base=1,
        exuberancia_base=1
    )
    db_session.add(personagem)
    db_session.commit()

    # 5. Cria o Mapa Base (Template)
    mapa = MapaDB(
        nome="Caverna do Esper",
        mapa_em_si=[["  ", "  "], ["  ", "  "]],
        objetos={})
    
    db_session.add(mapa)
    db_session.commit()

    # 6. Cria um Evento de Monstro Base (Template)
    evento_monstro = EventoDB(
        mapa_id=mapa.id,
        nome="Goblin",
        emoji="👹",
        pos_x=1,
        pos_y=0,
        event_type="monstro",
        parametros={}
    )
    db_session.add(evento_monstro)
    db_session.commit()


    return {
        "usuario_id": usuario.id,
        "cenario_id": cenario.id,
        "personagem": personagem,
        "mapa_id": mapa.id,
        "evento_id": evento_monstro.id 
    }


def test_deve_executar_carregar_engine_do_banco_com_esper(db_session, dados_base):
    """Garante que o método esperado pela tela limpa o mundo e popula as entidades."""

    mapa = dados_base.get('mapa_id')
    db = db_session
    
    # 2. AÇÃO: Executa o método esperado pela UI
    loader = GameEngineLoader()
    sucesso = loader.carregar_engine_do_banco(db, mapa)

    # 3. VALIDAÇÕES COERENTES COM O MOTOR COMPLETO
    assert sucesso is True
    assert loader.nome_mapa == "Caverna do Esper"

    # O Esper agora possui 2 entidades com posição (O Jogador injetado + o Goblin do banco)
    entidades = esper.get_components(PositionComponent)
    # Atualizado: Jogador (ID 1) + Goblin (Injetado depois)
    assert len(entidades) == 2

    # Para testar rigorosamente o Goblin do banco sem ser afetado pelo jogador fixo,
    # vamos varrer as entidades do Esper procurando quem possui o RenderComponent com o emoji "👹"
    achou_goblin = False
    for ent_id, (pos, ren) in esper.get_components(PositionComponent, RenderComponent):
        if ren.emoji == "👹":
            achou_goblin = True
            assert pos.x == 1
            assert pos.y == 0

    assert achou_goblin is True, "O Goblin vindo do banco de dados não foi encontrado no Esper ECS."


def test_deve_atribuir_status_e_inventario_ao_jogador_no_esper(db_session, dados_base):
    esper.switch_world(esper.list_worlds()[0])

    mapa_id = dados_base.get("mapa_id")

    loader = GameEngineLoader()
    loader.carregar_engine_do_banco(db_session, mapa_id)

    player_entity = None
    for ent_id, (stats,) in esper.get_components(StatsComponent):
        if stats.nome == "Charles":
            player_entity = ent_id
            break

    assert player_entity is not None
    stats = esper.component_for_entity(player_entity, StatsComponent)
    inv = esper.component_for_entity(player_entity, InventoryComponent)
    eqp = esper.component_for_entity(player_entity, EquipmentComponent)

    assert stats.nome == "Charles"
    assert stats.classe == "Mago"
    assert stats.ataque_base == 2
    assert isinstance(inv.itens, list)
    assert eqp.arma is None
