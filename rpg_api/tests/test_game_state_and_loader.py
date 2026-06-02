# rpg_api/tests/test_game_state_and_loader.py
import pytest
import esper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.plataforma_db import UsuarioDB, SaveDB
from app.models.mapas_db import MapaDB, CenarioDB
from app.models.eventos_db import EventoDB
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB

from app.core.engine.game_state import GameStateManager
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.components import PositionComponent, StatsComponent

# ==============================================================================
# 🧼 FIXTURES DE INFRAESTRUTURA E RESET DO ESPER
# ==============================================================================


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


@pytest.fixture(autouse=True)
def reset_esper_antes_de_cada_teste():
    """Garante isolamento absoluto limpando a memória do Esper ECS."""
    esper.clear_database()
    if esper.list_worlds():
        esper.switch_world(esper.list_worlds()[0])
    else:
        esper.switch_world(esper.World())


@pytest.fixture(name="dados_base")
def fixture_dados_base(db_session):
    """Povoa o banco com os templates base de um cenário (Mundo do Criador)."""
    # 1. Cria Raça e Classe obrigatórias para os relacionamentos de PersonagemDB
    raca = RacaDB(nome="Humano", bonus_atributos={}, emoji="🧍")
    classe = ClasseRPGDB(nome="Mago", bonus_caminhos={}, habilidades={})
    db_session.add_all([raca, classe])
    db_session.commit()

    # 2. Cria a infraestrutura do Cenário e do Mapa
    usuario = UsuarioDB(username="charles_admin",
                        email="admin@rpg.com", senha_hash="123")
    db_session.add(usuario)
    db_session.commit()

    cenario = CenarioDB(nome="Aventura de Teste",
                        criador_id=usuario.id, descricao="Cenário para testes unitários")
    db_session.add(cenario)
    db_session.commit()
    # 2. Cria o Personagem ID 1 (Jogador principal)
    
    jogador_db = PersonagemDB(
        id=1, nome="Charles", nivel=1, raca_id=raca.id, classe_id=classe.id,
        usuario_id=usuario.id, cenario_id=cenario.id, forca_base=5, agilidade_base=5, resistencia_base=5,
        percepcao_base=5, exuberancia_base=5
    )
    db_session.add(jogador_db)
    db_session.commit()
   

    mapa = MapaDB(nome="Masmorra Central", altura=2, largura=2, tile_parede="🧱",
                  tile_chao="🪵", mapa_em_si=[["  " for _ in range(10)] for _ in range(10)], objetos={}, cenario_id=cenario.id)
    db_session.add(mapa)
    db_session.commit()


    # 4. Adiciona um Evento (Monstro) associado a esse mapa
    evento_monstro = EventoDB(
        mapa_id=mapa.id, nome="Orc Soldado", emoji="🧌",
        pos_x=1, pos_y=1, tipo_evento="monstro", parametros={}
    )
    db_session.add(evento_monstro)
    db_session.commit()


    return {
        "usuario_id": usuario.id,
        "cenario_id": cenario.id,
        "mapa_id": mapa.id,
        "evento_id": evento_monstro.id
    }


# ==============================================================================
# ⚔️ SUÍTE DE TESTES UNITÁRIOS DO GAME STATE & LOADER
# ==============================================================================
def test_deve_inicializar_engine_loader_e_popular_mundo_com_esper(db_session, dados_base):
    """Garante que o GameEngineLoader consegue ler o cenário do banco e montar o Esper."""
    loader = GameEngineLoader()
    sucesso = loader.carregar_engine_do_banco(
        db_session, dados_base["mapa_id"])

    assert sucesso is True
    assert loader.nome_mapa == "Masmorra Central"

    esper.create_entity()  # Força a criação de uma entidade para validar o mundo

    # Deve conter 2 entidades: Jogador (Injetado) + Orc Soldado (Banco)
    position_components = list(esper.get_components(PositionComponent))
    assert len(position_components) == 2

    # Valida se o herói nasceu com a árvore de componentes correta
    stats_components = list(esper.get_components(StatsComponent))
    player_entities = [entity for entity, stats in stats_components if stats[0].nome == "Charles"]
    assert len(player_entities) == 1

    player_entity = player_entities[0]
    assert esper.entity_exists(player_entity) is True

    pos_player = esper.component_for_entity(player_entity, PositionComponent)
    stats_player = esper.component_for_entity(player_entity, StatsComponent)

    # Posição inicial segura do fallback
    assert pos_player.x == 2 and pos_player.y == 2
    assert stats_player.nome == "Charles"


def test_game_state_manager_salvamento_e_recuperacao_de_switches(db_session, dados_base):
    """Testa se os seletores lógicos (Switches) persistem dinamicamente através do GameStateManager."""
    gsm = GameStateManager()
    gsm.set_switch("porta_aberta", True)
    gsm.set_variable("ouro_acumulado", 250)

    # Cria e salva o registro na tabela 'saves' (Slot 1)
    save_id = gsm.salvar_sessao_no_banco(
        db_session, dados_base["usuario_id"], dados_base["cenario_id"], dados_base["mapa_id"], slot=1)
    assert save_id is not None

    # Instancia um novo gerenciador zerado para simular o fechamento e reabertura do jogo
    novo_gsm = GameStateManager()
    dados_carregados = novo_gsm.carregar_sessao_do_banco(
        db_session, dados_base["usuario_id"], dados_base["cenario_id"], slot=1)

    assert dados_carregados is not None
    assert novo_gsm.get_switch("porta_aberta") is True
    assert novo_gsm.get_variable("ouro_acumulado") == 250
