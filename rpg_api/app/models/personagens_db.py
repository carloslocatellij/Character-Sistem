from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class RacaDB(Base):
    """Tabela que armazena as Raças disponíveis no jogo."""
    __tablename__ = "racas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    bonus_atributos = Column(JSON, default=dict)
    emoji = Column(String, default="👤")

    # Relacionamento reverso: permite acessar todos os personagens desta raça (ex: raca.personagens)
    personagens = relationship("PersonagemDB", back_populates="raca")


class ClasseRPGDB(Base):
    """Tabela que armazena as Classes/Profissões do jogo."""
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
    cenario_id = Column(Integer, ForeignKey("cenarios.id"))

    # ==========================================
    # CHAVES ESTRANGEIRAS (FOREIGN KEYS)
    # ==========================================
    # Estas colunas guardam apenas o "ID" da raça e da classe
    raca_id = Column(Integer, ForeignKey("racas.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes_rpg.id"), nullable=False)

    # ==========================================
    # RELACIONAMENTOS (ORM)
    # ==========================================
    # O SQLAlchemy usa isso para carregar o objeto inteiro automaticamente!
    raca = relationship("RacaDB", back_populates="personagens")
    classe = relationship("ClasseRPGDB", back_populates="personagens")

    # ==========================================
    # ATRIBUTOS BASE (Status puros, sem modificadores)
    # ==========================================
    forca_base = Column(Integer, default=1)
    agilidade_base = Column(Integer, default=1)
    resistencia_base = Column(Integer, default=1)
    percepcao_base = Column(Integer, default=1)
    exuberancia_base = Column(Integer, default=1)
    
    
    # ==========================================
    # NOVO: EQUIPAMENTOS (CHAVES ESTRANGEIRAS)
    # ==========================================
    # nullable=True porque o personagem pode não ter nada equipado nesses slots
    mao_direita_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)
    mao_esquerda_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)
    armadura_id = Column(Integer, ForeignKey("itens_equipamentos.id"), nullable=True)

    # ==========================================
    # NOVO: RELACIONAMENTOS DOS EQUIPAMENTOS
    # ==========================================
    # Usamos foreign_keys para o SQLAlchemy saber exatamente qual ID carregar em qual slot
    mao_direita = relationship("ItemDB", foreign_keys=[mao_direita_id])
    mao_esquerda = relationship("ItemDB", foreign_keys=[mao_esquerda_id])
    armadura_equipada = relationship("ItemDB", foreign_keys=[armadura_id])

    # Nota: Não salvamos "pv_atual", "modificador_ataque" ou "caminhos_magia" totais no banco de dados.
    # Em uma Arquitetura Limpa, o banco guarda os DADOS BASE. Os cálculos são feitos
    # pela nossa classe de Domínio (`app.core.personagens.Personagem`) quando carregamos o jogo!