import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 2. Lê a variável TEST_VERSION (converte para booleano)
# Se não encontrar a variável, assume "True" por segurança.
test_version_str = os.getenv("TEST_VERSION", "True").lower()
IS_TEST_ENV = test_version_str in ("true", "1", "t", "yes")

# 3. Define a URL do banco com base no ambiente
basedir = os.path.abspath(os.path.dirname(__file__))

if IS_TEST_ENV:
    engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,)
    print("🔧 [DB] MODO DE TESTE ATIVADO: Usando banco de dados de teste.")
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(basedir, "rpg_producao.db") or os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(basedir, "rpg_producao.db"))
    if "pytest" in sys.modules or "pytest" in sys.argv[0]:
        if "prod" in SQLALCHEMY_DATABASE_URL:
            engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,)
        print("🔧 [DB] MODO DE TESTE ATIVADO: Usando banco de dados de teste.")
        
    else:
        print("🚀 [DB] MODO DE PRODUÇÃO ATIVADO: Usando banco oficial.")    
        # 4. Cria o Motor (Engine) do banco de dados
        # O argumento connect_args={"check_same_thread": False} é necessário apenas para o SQLite trabalhar bem com o FastAPI.
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )

# 5. Fábrica de Sessões (Onde as transações do banco acontecem)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Classe Base da qual todos os nossos Modelos de Banco de Dados vão herdar
Base = declarative_base()

def garantir_schema_atualizado(engine_instancia=None):
    """
    Verifica e migra automaticamente colunas ausentes em bancos SQLite existentes.
    Garante que colunas recém-adicionadas (como personagens.inventario e personagens.slot_equipe)
    sejam criadas caso o arquivo de banco já existisse previamente sem elas.
    """
    target_engine = engine_instancia or engine
    Base.metadata.create_all(bind=target_engine)

    try:
        from sqlalchemy import text
        with target_engine.connect() as conn:
            # 1. Verifica colunas da tabela personagens
            res = conn.execute(text("PRAGMA table_info(personagens);")).fetchall()
            colunas_personagens = {r[1] for r in res}

            if colunas_personagens:
                if "inventario" not in colunas_personagens:
                    conn.execute(text("ALTER TABLE personagens ADD COLUMN inventario JSON DEFAULT '[]';"))
                if "slot_equipe" not in colunas_personagens:
                    conn.execute(text("ALTER TABLE personagens ADD COLUMN slot_equipe INTEGER DEFAULT 0;"))

            # 2. Verifica colunas da tabela magias
            res_magias = conn.execute(text("PRAGMA table_info(magias);")).fetchall()
            colunas_magias = {r[1] for r in res_magias}
            if colunas_magias:
                if "dano_area" not in colunas_magias:
                    conn.execute(text("ALTER TABLE magias ADD COLUMN dano_area BOOLEAN DEFAULT 0;"))
                if "tipo_execucao" not in colunas_magias:
                    conn.execute(text("ALTER TABLE magias ADD COLUMN tipo_execucao VARCHAR(50) DEFAULT 'combate';"))

            conn.commit()
    except Exception as erro_migracao:
        pass

# Executa a verificação e criação na inicialização
garantir_schema_atualizado(engine)

def get_db():
    """Função utilitária para abrir e fechar a conexão com o banco corretamente."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()