# rpg_api/app/models/eventos_db.py

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class EventoDB(Base):
    __tablename__ = 'eventos'

    id = Column(Integer, primary_key=True, index=True)
    mapa_id = Column(Integer, ForeignKey("mapas.id", ondelete="CASCADE"), nullable=False)
    
    nome = Column(String, nullable=False)
    emoji = Column(String(2), nullable=False) # O caractere que será desenhado na interface
    
    # Coordenadas iniciais onde a Entity será instanciada pelo engine
    pos_x = Column(Integer, nullable=False)
    pos_y = Column(Integer, nullable=False)
    
    # Define o comportamento na Engine ('bau', 'npc_loja', 'npc_dialogo', 'porta', 'armadilha')
    event_type = Column(String, nullable=False) 
    
    # Armazena os dados específicos de cada tipo. 
    # Ex Lojas: {"produtos": [1, 5, 8], "dinheiro_npc": 500}
    # Ex Diálogo: {"texto": "Olá forasteiro!", "opcoes": [...]}
    parametros = Column(JSON, default=dict) 

    # Relacionamento de volta para o mapa
    mapa = relationship("MapaDB", back_populates="eventos")