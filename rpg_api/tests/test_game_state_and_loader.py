# rpg_api/tests/test_game_state_and_loader.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.plataforma_db import UsuarioDB, SaveDB
from app.models.mapas_db import MapaDB, CenarioDB
from app.models.eventos_db import EventoDB
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB

from app.core.engine.game_state import GameStateManager
from app.core.engine.engine_loader import carregar_engine_do_banco
from app.core.engine.manager import EngineManager
from app.core.personagens import Personagem

# ==========================================
# INFRAESTRUTURA DE BANCO DE DADOS EM MEMÓRIA
# ==========================================
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
    cenario = CenarioDB(nome="Crônicas de Arton", descricao="Campanha épica", criador_id=usuario.id)
    db_session.add(cenario)
    db_session.commit()

    # 3. Cria registros necessários de Raça e Classe exigidos pelo GameController relacional
    raca_db = RacaDB(nome="Humano", bonus_atributos={"forca": 0, "agilidade": 0, "resistencia": 0, "percepcao": 0, "exuberancia": 0}, emoji="🧑")
    classe_db = ClasseRPGDB(nome="Guerreiro", bonus_caminhos={}, habilidades=[])
    db_session.add(raca_db)
    db_session.add(classe_db)
    db_session.commit()

    # 4. Cria o Personagem Base na tabela real PersonagemDB usando as propriedades reais e chaves estrangeiras
    personagem = PersonagemDB(
        nome="Ragnar",
        nivel=1,
        raca_id=raca_db.id,
        classe_id=classe_db.id,
        forca_base=15,
        agilidade_base=12,
        resistencia_base=14,
        percepcao_base=10,
        exuberancia_base=10,
        usuario_id=usuario.id
    )
    db_session.add(personagem)
    db_session.commit()

    # 5. Cria o Mapa Base (Template)
    mapa = MapaDB(
        nome="Vila Inicial",
        largura=5, altura=5,
        mapa_em_si=[["🟩" for _ in range(5)] for _ in range(5)],
        objetos={},
        configs={"pos_inicial": [2, 2]},
        cenario_id=cenario.id
    )
    db_session.add(mapa)
    db_session.commit()

    # 6. Cria um Evento de Monstro Base (Template)
    evento_monstro = EventoDB(
        mapa_id=mapa.id,
        nome="Slime",
        emoji="👾",
        pos_x=4, pos_y=4,
        tipo_evento="monstro",
        parametros={"mover": {"direção": "aleatório"}, "ação": {"quando": "tocar_heroi", "mudar_hp": {"valor": 2}}}
    )
    db_session.add(evento_monstro)
    db_session.commit()

    return {
        "usuario_id": usuario.nome,
        "cenario_id": cenario.id,
        "mapa_id": mapa.id,
        "evento_id": evento_monstro.nome 
    }


# ==========================================
# SUÍTE DE TESTES DE INTEGRAÇÃO
# ==========================================

def test_inicializacao_novo_jogo_sem_save(db_session, dados_base, monkeypatch):
    """Garante que se não houver save, o motor carrega o estado original do editor (Base)."""
    
    # Conseguimos capturar a instanciação real de Personagem e acoplar dinamicamente 
    # as propriedades temporárias de compatibilidade lidas pelo engine_loader
    original_init = Personagem.__init__
    
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Acopla propriedades dinâmicas avaliando os métodos reais do seu domínio
        self.ataque = self.mod_atq_corpo
        if self.armadura:
            self.defesa = self.armadura.defesa
        else:
            self.defesa = 0

    monkeypatch.setattr(Personagem, "__init__", patched_init)

    # Executa o carregamento real usando a EngineManager
    engine, mapa_matriz, objetos, mapa_id = carregar_engine_do_banco(
        db_session=db_session,
        usuario_id=dados_base["usuario_id"],
        cenario_id=dados_base["cenario_id"],
        slot_numero=1
    )

    from app.core.engine.components import PositionComponent
    engine.add_component(dados_base["usuario_id"], PositionComponent(x=2, y=2))
    
    # Verificações de Consistência
    assert mapa_id == dados_base["mapa_id"]
    assert len(mapa_matriz) == 5
    
    # O Jogador (ID 1) deve herdar as coordenadas padrão do cenário (2, 2)
    pos_jogador = engine.get_component(dados_base["usuario_id"], "PositionComponent")
    assert pos_jogador.x == 2
    assert pos_jogador.y == 2
    
    # O Monstro deve iniciar na sua respectiva coordenada de spawn (4, 4)
    pos_monstro = engine.get_component(dados_base["evento_id"], "PositionComponent")
    assert pos_monstro.x == 4
    assert pos_monstro.y == 4


def test_salvamento_e_carregamento_com_delta(db_session, dados_base, monkeypatch):
    """Garante o ciclo base+delta: move entidades, salva no BD, limpa a memória e reverte as posições modificadas."""
    
    original_init = Personagem.__init__
    
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.ataque = self.mod_atq_corpo
        if self.armadura:
            self.defesa = self.armadura.defesa
        else:
            self.defesa = 0
 

    monkeypatch.setattr(Personagem, "__init__", patched_init)

    # 1. Realiza o carregamento inicial limpo da infraestrutura do mapa
    engine, _, _, _ = carregar_engine_do_banco(db_session, dados_base["usuario_id"], dados_base["cenario_id"], slot_numero=1)
    gsm = GameStateManager()

    from app.core.engine.components import PositionComponent, StatsComponent, InventoryComponent, EquipmentComponent
    engine.add_component(1, PositionComponent(x=2, y=2))
    engine.add_component(1, StatsComponent(nome="Ragnar", hp=45, max_hp=45, mp=12, max_mp=12, ataque_base=15, defesa_base=10))
    engine.add_component(1, InventoryComponent(itens={}))
    engine.add_component(1, EquipmentComponent())
    
    # 2. APLICA MODIFICAÇÕES DINÂMICAS DE TEMPO DE EXECUÇÃO
    pos_jogador = engine.get_component(1, "PositionComponent")
    pos_jogador.x = 0; pos_jogador.y = 0 
    
    engine.add_component(2, PositionComponent(x=2, y=2))
    
    pos_monstro = engine.get_component(dados_base["evento_id"], "PositionComponent")
    pos_monstro.x = 1; pos_monstro.y = 1 
    
    # Atualiza componentes vitais do motor geométrico
    stats_jogador = engine.get_component(1, "StatsComponent")
    stats_jogador.hp = 30 
    
    inv_jogador = engine.get_component(1, "InventoryComponent")
    inv_jogador.itens["espada_lendaria"] = 1 

    gsm.set_switch("missao_concluida", True)
    gsm.set_variable("nome_aliado", "Carlos")

    # 3. SALVA O SNAPSHOT CORRENTE DIRETAMENTE NA TABELA SAVEDB
    gsm.salvar_sessao_no_banco(
        ecs_manager=engine,
        db_session=db_session,
        usuario_id=dados_base["usuario_id"],
        cenario_id=dados_base["cenario_id"],
        mapa_atual_id=dados_base["mapa_id"],
        slot=1
    )

    # Certifica-se de que o registro JSON estruturado foi guardado no SQLite relacional
    save_no_banco = db_session.query(SaveDB).filter(SaveDB.usuario_id == dados_base["usuario_id"]).first()
    assert save_no_banco is not None
    assert save_no_banco.dados_sessao["switches"]["missao_concluida"] is True
    assert save_no_banco.dados_sessao["variables"]["nome_aliado"] == "Carlos"

    # ==========================================
    # 4. SIMULAÇÃO DE RESET: RECARREGA A SESSÃO SALVA DO BANCO (LOAD)
    # ==========================================
    novo_gsm = GameStateManager()
    dados_carregados = novo_gsm.carregar_sessao_do_banco(db_session, dados_base["usuario_id"], dados_base["cenario_id"], slot=1)
    
    assert dados_carregados is not None
    assert novo_gsm.get_switch("missao_concluida") is True
    assert novo_gsm.get_variable("nome_aliado") == "Carlos"

    # Executa um novo carregar_engine_do_banco que deve preferir os dados do Delta
    novo_engine, _, _, _ = carregar_engine_do_banco(
        db_session, dados_base["usuario_id"], dados_base["cenario_id"], slot_numero=1
    )

    # 5. AS VALIDAÇÕES FINAIS (Garantia de persistência mutável)
    pos_jogador_carregado = novo_engine.get_component(1, "PositionComponent")
    assert pos_jogador_carregado.x == 0
    assert pos_jogador_carregado.y == 0  # Prevaleceu a coordenada salva (0,0) sobre o template (2,2)

    pos_monstro_carregado = novo_engine.get_component(dados_base["evento_id"], "PositionComponent")
    assert pos_monstro_carregado.x == 1
    assert pos_monstro_carregado.y == 1  # Prevaleceu a coordenada salva (1,1) sobre o template (4,4)

    stats_jogador_carregado = novo_engine.get_component(1, "StatsComponent")
    assert stats_jogador_carregado.hp == 30  

    inv_jogador_carregado = novo_engine.get_component(1, "InventoryComponent")
    assert inv_jogador_carregado.itens.get("espada_lendaria") == 1
