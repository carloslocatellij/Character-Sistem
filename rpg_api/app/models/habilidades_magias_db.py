from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class EfeitoDB(Base):
    """Tabela que armazena os Efeitos Temporários (condições)."""
    __tablename__ = "efeitos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    duracao_turnos = Column(Integer, default=1)
    tipo = Column(String, nullable=False)  # "dano_continuo", "cura_continua", "buff_atributo", "debuff_atributo", "sono", "atordoado", "lentidao", "louco", "protecao_elemental", "fraqueza_elemental"
    valor = Column(Integer, default=0)
    atributo_alvo = Column(String, nullable=True)
    configuracoes = Column(JSON, default=dict)


class MagiaDB(Base):
    """Tabela que armazena os metadados de Magias e Habilidades."""
    __tablename__ = "magias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    descricao = Column(String, default="")
    tipo_execucao = Column(String, default="combate")  # "combate", "fora_combate", "ambos"
    custo_pm = Column(Integer, default=1)
    requisito_caminhos = Column(JSON, default=dict)  # Ex: {"fogo": 2}
    requisito_exuberancia = Column(Integer, default=1)
    dano_base = Column(Integer, default=0)
    cura_base = Column(Integer, default=0)
    dano_area = Column(Boolean, default=False)
    propriedades_combate = Column(JSON, default=dict)  # critico_ampliado, ignorar_defesa, contra_ataque, etc.

    efeito_id = Column(Integer, ForeignKey("efeitos.id", ondelete="SET NULL"), nullable=True)
    efeito = relationship("EfeitoDB")
