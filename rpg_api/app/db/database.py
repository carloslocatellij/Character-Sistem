import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# 2. Lê a variável TEST_VERSION (converte para booleano)
# Se não encontrar a variável, assume "True" por segurança.
test_version_str = os.getenv("TEST_VERSION", "True").lower()
IS_TEST_ENV = test_version_str in ("true", "1", "t", "yes")

# 3. Define a URL do banco com base no ambiente
basedir = os.path.abspath(os.path.dirname(__file__))

if IS_TEST_ENV:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL_TEST", "sqlite:///" + os.path.join(basedir, "rpg_teste.db"))
    print("🔧 [DB] MODO DE TESTE ATIVADO: Usando banco de dados de teste.")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL_PROD", "sqlite:///" + os.path.join(basedir, "rpg_producao.db"))
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

def get_db():
    """Função utilitária para abrir e fechar a conexão com o banco corretamente."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()