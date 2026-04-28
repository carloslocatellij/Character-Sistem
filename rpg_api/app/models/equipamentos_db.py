from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base

class ItemDB(Base):
    """Representa a tabela de Itens/Armas/Armaduras no Banco de Dados."""
    __tablename__ = "itens_equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    categoria = Column(String, nullable=False) # Ex: "arma", "armadura", "escudo", "comum"
    peso = Column(Float, default=0.0)
    emoji = Column(String, default="📦")
    
    # Atributos específicos (Podem ser nulos, pois uma poção não tem dano)
    dano = Column(Integer, nullable=True)         # Para Armas
    tipo_ataque = Column(String, nullable=True)   # "corpo" ou "distancia"
    defesa = Column(Integer, nullable=True)       # Para Armaduras
    defesa_extra = Column(Integer, nullable=True) # Para Escudos