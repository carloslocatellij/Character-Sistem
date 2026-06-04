from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class RacaDB(Base):
    """Tabela que armazena as Raças disponíveis no jogo.
        Args: 
            nome: str,
            bonus_atributos: json
            emoji: str 
    """
    __tablename__ = "racas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    bonus_atributos = Column(JSON, default=dict)
    emoji = Column(String, default="👤")

    # Relacionamento reverso: permite acessar todos os personagens desta raça (ex: raca.personagens)
    personagens = relationship("PersonagemDB", back_populates="raca")


class ClasseRPGDB(Base):
    """Tabela que armazena as Classes/Profissões do jogo.
        Args: 
            nome: str,
            bonus_caminhos: json
            habilidades: json 
    
    """
    __tablename__ = "classes_rpg"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    
    # Armazenando dicionários e listas no banco
    bonus_caminhos = Column(JSON, default=dict)
    habilidades = Column(JSON, default=list)    # Ex: ["Ataque Furtivo"]
    personagens = relationship("PersonagemDB", back_populates="classe")


class PersonagemDB(Base):
    """Tabela central que armazena os Personagens dos jogadores."""
    __tablename__ = "personagens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    nivel = Column(Integer, default=1)
    raca_id = Column(Integer, ForeignKey("racas.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes_rpg.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"))
    cenario_id = Column(Integer, ForeignKey("cenarios.id", ondelete="CASCADE"))

    # ATRIBUTOS BASE (Status puros, sem modificadores)
    forca_base = Column(Integer, default=1)
    agilidade_base = Column(Integer, default=1)
    resistencia_base = Column(Integer, default=1)
    percepcao_base = Column(Integer, default=1)
    exuberancia_base = Column(Integer, default=1)
    
    # EQUIPAMENTOS (CHAVES ESTRANGEIRAS)
    mao_direita_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)
    mao_esquerda_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)
    armadura_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)
    
    # RELACIONAMENTOS (ORM)
    raca = relationship("RacaDB", back_populates="personagens")
    classe = relationship("ClasseRPGDB", back_populates="personagens")
    usuario = relationship("UsuarioDB", back_populates="personagens")
    cenario = relationship("CenarioDB", back_populates="personagens")


    # RELACIONAMENTOS DOS EQUIPAMENTOS
    # Usamos foreign_keys para o SQLAlchemy saber exatamente qual ID carregar em qual slot
    mao_direita = relationship("ItemDB", foreign_keys=[mao_direita_id])
    mao_esquerda = relationship("ItemDB", foreign_keys=[mao_esquerda_id])
    armadura_equipada = relationship("ItemDB", foreign_keys=[armadura_id])

    # Nota: Não salvamos "pv_atual", "modificador_ataque" ou "caminhos_magia" junto do personagem mas sim na tabela save.