# rpg_api/app/models/__init__.py

# Importar todos os modelos aqui garante que o SQLAlchemy os registre 
# no Base.metadata antes de tentar resolver os relacionamentos (relationships)
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.personagens_db import PersonagemDB
from app.models.equipamentos_db import ItemDB