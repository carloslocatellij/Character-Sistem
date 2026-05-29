from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class CenarioDB(Base):
    """Representa um jogo/campanha completo e independente criado por um usuário."""
    __tablename__ = "cenarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)
    criador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos
    criador = relationship("UsuarioDB", back_populates="cenarios_criados")
    mapas = relationship("MapaDB", back_populates="cenario") # Garanta que MapaDB tenha a FK cenario_id
    saves = relationship("SaveDB", back_populates="cenario")
    

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
    cenario_id = Column(Integer, ForeignKey("cenarios.id"))
    
    cenario = relationship("CenarioDB", back_populates="mapas")
    eventos = relationship("EventoDB", back_populates="mapa", cascade="all, delete-orphan")