# rpg_api/tests/test_engine_multiplayer.py
import pytest
import esper
from app.db.database import Base, engine
from app.models.mapas_db import MapaDB, CenarioDB
from app.models.eventos_db import EventoDB
from app.models.plataforma_db import UsuarioDB
from app.models.personagens_db import PersonagemDB, ClasseRPGDB, RacaDB
from app.core.engine.components import (
    PositionComponent, RenderComponent, InteractableComponent,
    StatsComponent, InventoryComponent, EquipmentComponent,
    CollisionComponent, NetworkPlayerComponent
)
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.systems import (
    MovementSystem, AISystem, RenderSystem, EventSystem, InventarySystem, NetworkSystem
)
from app.core.engine.game_state import GameStateManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria um banco SQLite isolado em memória para cada teste."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    usuario = UsuarioDB(username="mestre_rpg", email="mestre@rpg.com", senha_hash="123")
    db_session.add(usuario)
    db_session.commit()

    # 2. Cria o Cenário/Jogo Independente
    cenario = CenarioDB(nome="Crônicas de Arton", descricao="Campanha multiplayer", criador_id=usuario.id)
    db_session.add(cenario)
    db_session.commit()

    # 3. Cria registros de Raça e Classe
    raca_db = RacaDB(nome="Humano", bonus_atributos={
                     "forca": 0, "agilidade": 0, "resistencia": 0, "percepcao": 0, "exuberancia": 0}, emoji="🧑")
    classe_db = ClasseRPGDB(nome="Mago", bonus_caminhos={}, habilidades=[])
    db_session.add(raca_db)
    db_session.add(classe_db)
    db_session.commit()

    # 4. Cria o Personagem
    personagem = PersonagemDB(
        nome="Charles", nivel=1, raca_id=raca_db.id, classe_id=classe_db.id,
        usuario_id=usuario.id, cenario_id=cenario.id, forca_base=1, agilidade_base=2,
        resistencia_base=1, percepcao_base=1, exuberancia_base=1
    )
    db_session.add(personagem)
    db_session.commit()

    # 5. Cria o Mapa Base (Template) - 5x5
    mapa = MapaDB(
        nome="Arena Multiplayer",
        mapa_em_si=[["  "] * 5 for _ in range(5)],
        objetos={}
    )
    db_session.add(mapa)
    db_session.commit()

    # 6. Goblin
    evento_monstro = EventoDB(
        mapa_id=mapa.id, nome="Goblin", emoji="👹", pos_x=1, pos_y=0, event_type="monstro",
        parametros={"paginas": [{"gatilho": "acao_jogador", "movimento": {"tipo": "direcional", "roteiro": ["esquerda"]}}]}
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


def test_deve_carregar_nova_engine_com_suporte_a_processors(db_session, dados_base):
    """Garante que a nova engine carrega corretamente no novo loader."""
    mapa_id = dados_base.get('mapa_id')
    loader = GameEngineLoader()
    sucesso, matriz, objs, active_map_id = loader.carregar_engine_do_banco(
        db_session, usuario_id=dados_base["usuario_id"], default_mapa_id=mapa_id, slot_numero=1, cenario_id=dados_base.get('cenario_id')
    )

    assert sucesso is True
    assert loader.nome_mapa == "Arena Multiplayer"
    assert active_map_id == mapa_id

    # Registra processadores
    mov_sys = MovementSystem(loader)
    ai_sys = AISystem(mov_sys)
    net_sys = NetworkSystem()
    render_sys = RenderSystem()
    
    esper.add_processor(mov_sys)
    esper.add_processor(ai_sys)
    esper.add_processor(net_sys)
    esper.add_processor(render_sys)

    assert esper.get_processor(NetworkSystem) is net_sys
    assert esper.get_processor(RenderSystem) is render_sys


def test_deve_adicionar_e_atualizar_jogador_rede(db_session, dados_base):
    """Verifica se jogadores remotos podem ser adicionados, atualizados e removidos da rede."""
    mapa_id = dados_base.get('mapa_id')
    loader = GameEngineLoader()
    loader.carregar_engine_do_banco(
        db_session, usuario_id=dados_base["usuario_id"], default_mapa_id=mapa_id, slot_numero=1, cenario_id=dados_base.get('cenario_id')
    )

    # Adiciona jogador remoto
    connection_id = "conn_12345"
    username = "Pernalonga"
    ent_id = loader.adicionar_jogador_rede(connection_id, username, x=3, y=3, emoji="🐰")
    
    assert ent_id is not None
    assert esper.entity_exists(ent_id)
    assert esper.has_component(ent_id, NetworkPlayerComponent)
    assert esper.has_component(ent_id, PositionComponent)
    assert esper.has_component(ent_id, RenderComponent)

    # Verifica posição
    pos = esper.component_for_entity(ent_id, PositionComponent)
    assert pos.x == 3
    assert pos.y == 3

    # Atualiza posição
    loader.atualizar_jogador_rede(connection_id, x=4, y=3, direcao="direita")
    assert pos.x == 4
    assert pos.y == 3
    assert pos.direcao_olhar == "direita"

    # Remove jogador remoto
    loader.remover_jogador_rede(connection_id)
    assert not esper.entity_exists(ent_id)


def test_jogador_rede_deve_bloquear_movimento(db_session, dados_base):
    """Verifica se um jogador remoto bloqueia a movimentação física."""
    mapa_id = dados_base.get('mapa_id')
    loader = GameEngineLoader()
    loader.carregar_engine_do_banco(
        db_session, usuario_id=dados_base["usuario_id"], default_mapa_id=mapa_id, slot_numero=1, cenario_id=dados_base.get('cenario_id')
    )

    mov_sys = MovementSystem(loader)
    esper.add_processor(mov_sys)

    # Jogador principal está em (2, 2) inicialmente se carregado de coords_iniciais (pelo loader vem de configuracao_iniciais ou 42,42)
    # Vamos setar a posição do jogador principal para (2, 2) explicitamente
    pos_player = esper.component_for_entity(1, PositionComponent)
    pos_player.x = 2
    pos_player.y = 2

    # Adiciona jogador remoto ao lado (3, 2)
    connection_id = "conn_block"
    loader.adicionar_jogador_rede(connection_id, "Obstaculo", x=3, y=2, emoji="🛡️")

    # Tenta mover para a direita (onde está o jogador remoto)
    moveu = mov_sys.mover_entidade(1, "direita")
    assert moveu is False
    assert pos_player.x == 2  # Não mudou de posição

    # Tenta mover para baixo (vazio)
    moveu = mov_sys.mover_entidade(1, "baixo")
    assert moveu is True
    assert pos_player.x == 2
    assert pos_player.y == 3


def test_deve_excluir_jogadores_rede_do_save_local(db_session, dados_base):
    """Garante que jogadores de rede não corrompam o save-game persistido."""
    mapa_id = dados_base.get('mapa_id')
    loader = GameEngineLoader()
    loader.carregar_engine_do_banco(
        db_session, usuario_id=dados_base["usuario_id"], default_mapa_id=mapa_id, slot_numero=1, cenario_id=dados_base.get('cenario_id')
    )

    # Adiciona jogador remoto
    loader.adicionar_jogador_rede("conn_save_test", "RemotePlayer", x=1, y=1, emoji="🎮")

    # Salva sessão
    game_state = GameStateManager()
    save_id = game_state.salvar_sessao_no_banco(
        db_session, usuario_id=dados_base["usuario_id"], cenario_id=dados_base["cenario_id"], mapa_atual_id=mapa_id, slot=2
    )
    assert save_id is not None

    # Recupera o save
    dados_carregados = game_state.carregar_sessao_do_banco(
        db_session, usuario_id=dados_base["usuario_id"], cenario_id=dados_base["cenario_id"], slot=2
    )
    assert dados_carregados is not None
    entidades_salvas = dados_carregados.get("entidades", {})

    # Procura se o jogador remoto foi salvo
    remote_saved = False
    for ent_id_str, ent_data in entidades_salvas.items():
        components = ent_data.get("components", {})
        stats = components.get("StatsComponent")
        if stats and stats.get("nome") == "RemotePlayer":
            remote_saved = True

    assert remote_saved is False, "O jogador remoto da rede foi indevidamente salvo no banco de dados local."
