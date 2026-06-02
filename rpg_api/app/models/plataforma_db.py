# app/models/plataforma_db.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False) # Para o futuro sistema de login

    # Relacionamentos
    cenarios_criados = relationship("CenarioDB", back_populates="criador")
    personagens = relationship("PersonagemDB", back_populates="usuario")
    saves = relationship("SaveDB", back_populates="usuario")

    
class SaveDB(Base):
    """
    Guarda o estado de execução de um jogo específico de um usuário.
    Desacoplado de tabelas estáticas.
    """
    __tablename__ = "saves"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    cenario_id = Column(Integer, ForeignKey("cenarios.id", ondelete="CASCADE"), nullable=False)
    slot_numero = Column(Integer, default=1, nullable=False)
    dados_sessao = Column(JSON, nullable=False)
    
    usuario = relationship("UsuarioDB", back_populates="saves")
    cenario = relationship("CenarioDB", back_populates="saves") # Permite fazer save_db.cenario.nome se necessário

    # Restrição para garantir que um usuário só tenha 1 save por slot em cada cenário
    __table_args__ = (
        UniqueConstraint('usuario_id', 'cenario_id', 'slot_numero', name='_usuario_cenario_slot_uc'),
    )