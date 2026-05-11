from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from app.db.database import Base

class MapaDB(Base):
    __tablename__ = 'mapas'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=True, default='') # 'masmorra', 'caverna', 'cidade'
    altura = Column(Integer)
    largura = Column(Integer)
    tile_parede = Column(String(1), default="🔳")
    tile_chao = Column(String(1), default="  ")
    configs = Column(JSON, default=dict) # Parâmetros usados na geração
    aleatorio = Column(Boolean, default=True)
    # Auto-relacionamento: Um mapa pode ser "pai" de outro (ex: níveis de uma dungeon)
    mapa_pai_id = Column(Integer, nullable=True)
    # A matriz do mapa guardada como JSON (Lista de Listas)
    mapa_em_si = Column(JSON, nullable=False)
    objetos = Column(JSON, nullable=True , default=dict)