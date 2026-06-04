import pytest
from app.core.entities.emojis import  CatalogoTiles, padronizar_largura_tile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.models.mapas_db import MapaDB

# ==============================================================================
# 🧼 FIXTURE DE INFRAESTRUTURA ISOLADA (SQLite em Memória)
# ==============================================================================


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria um banco SQLite isolado em memória para cada teste de mapas."""
    # 1. Cria a conexão isolada em memória
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False})

    # 2. Força o SQLAlchemy a mapear e CRIAR as tabelas (incluindo a tabela 'mapas')
    Base.metadata.create_all(bind=engine)

    SessionTesting = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    session = SessionTesting()

    try:
        yield session
    finally:
        session.close()
        # 3. Limpa tudo ao final da rodada do teste
        Base.metadata.drop_all(bind=engine)


# ==============================================================================
# ⚔️ O TESTE ADAPTADO E CORRIGIDO
# ==============================================================================
def test_deve_listar_mapas_cadastrados_no_banco(db_session):
    """Garante que a consulta base do banco retorna os mapas para o gerenciador."""

    # 1. SETUP: Registra o mapa de testes dentro do banco isolado da fixture
    mapa_teste = MapaDB(
        nome="Masmorra de Validação",
        tipo="caverna",
        altura=4,
        largura=4,
        mapa_em_si=[["  " for _ in range(4)] for _ in range(4)],
        objetos={}
    )
    db_session.add(mapa_teste)
    db_session.commit()
    db_session.refresh(mapa_teste)

    # 2. AÇÃO: Simula a query exata que o Gerenciador de Mapas usa na UI
    lista_mapas = db_session.query(MapaDB).all()

    # 3. VALIDAÇÃO: O banco precisa retornar o registro de forma íntegra
    assert len(lista_mapas) > 0
    nomes_mapas = [m.nome for m in lista_mapas]
    assert "Masmorra de Validação" in nomes_mapas

# ==========================================
# 1. TESTES DO CATÁLOGO E PADRONIZAÇÃO VISUAL
# ==========================================
def test_padronizar_largura_tile():
    """Garante que caracteres magros ganham espaço e emojis largos ficam iguais."""
    # Caractere normal (tamanho 1) deve ganhar um espaço
    assert padronizar_largura_tile('🏘️') == "🏘️ "
    assert padronizar_largura_tile("🕸️") == "🕸️ "
    
    # Emoji padrão (tamanho 2) deve retornar intacto
    assert padronizar_largura_tile("🌳") == "🌳"
    assert padronizar_largura_tile("⬛") == "⬛"

def test_catalogo_tiles_tipos():
    """Garante que o sistema diferencia corretamente chãos de objetos."""
    # Terrenos conhecidos
    assert CatalogoTiles.obter_tipo("🟫") == "terreno"
    assert CatalogoTiles.obter_tipo("🔲") == "terreno"
    
    # Objetos conhecidos e desconhecidos (Borracha, Letras)
    assert CatalogoTiles.obter_tipo("🪑") == "objeto"
    assert CatalogoTiles.obter_tipo("❌") == "objeto"
    assert CatalogoTiles.obter_tipo("🏚️ ") == "objeto" # Tudo o que não é terreno, é objeto

def test_catalogo_cores_fundo():
    """Garante que os chãos devolvem as cores corretas para o motor de renderização."""
    assert CatalogoTiles.obter_cor_fundo("🟫") == "#B45428"
    assert CatalogoTiles.obter_cor_fundo("⬛") == "#221F1F"
    
    # Objetos ou tiles inexistentes não devem ter cor de fundo padrão
    assert CatalogoTiles.obter_cor_fundo("🪑") == ""
    
# ==========================================
# 2. TESTES DE SERIALIZAÇÃO DE OBJETOS
# ==========================================
from app.views.map_manager_screen import MapManagerScreen

def test_empacotar_objetos_para_banco():
    """Garante que tuplas matemáticas viram strings JSON."""
    # Instanciamos a tela apenas para usar as suas funções internas
    tela = MapManagerScreen()
    
    # Simulamos o utilizador a colocar dois objetos no mapa
    tela.mapa_atual_objetos = {
        (5, 10): "🪑",
        (0, 0): "💀"
    }
    
    resultado = tela._empacotar_objetos_para_banco()
    
    # A tupla (5, 10) deve ter virado a string "5,10"
    assert resultado == {"5,10": "🪑", "0,0": "💀"}
    assert type(list(resultado.keys())[0]) == str

def test_desempacotar_objetos_do_banco():
    """Garante que strings JSON voltam a ser tuplas matemáticas."""
    tela = MapManagerScreen()
    
    dados_do_banco = {
        "3,4": "🍄",
        "15,20": "⛺"
    }
    
    resultado = tela._desempacotar_objetos_do_banco(dados_do_banco)
    
    # O texto deve ter virado tupla novamente
    assert resultado == {(3, 4): "🍄", (15, 20): "⛺"}
    
    # Testa se o sistema lida bem com dicionários vazios ou nulos (mapas novos)
    assert tela._desempacotar_objetos_do_banco({}) == {}
    assert tela._desempacotar_objetos_do_banco(None) == {}
    
    