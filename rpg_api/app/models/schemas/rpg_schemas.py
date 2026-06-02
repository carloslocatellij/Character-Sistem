from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional

# ==========================================
# SCHEMAS DE RAÇA
# ==========================================
class RacaCreate(BaseModel):
    nome: str
    bonus_atributos: Dict[str, int]
    emoji: Optional[str] = "👤"

class RacaResponse(RacaCreate):
    id: int
    
    # Configuração do Pydantic V2 para ler dados do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# SCHEMAS DE CLASSE
# ==========================================
class ClasseRPGCreate(BaseModel):
    nome: str
    bonus_caminhos: Dict[str, int] = {}
    habilidades: List[str] = []
    bonus_atributos: Dict[str, int] = {}

class ClasseRPGResponse(ClasseRPGCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# SCHEMAS DE PERSONAGEM
# ==========================================
class PersonagemCreate(BaseModel):
    nome: str
    raca_id: int
    classe_id: int
    forca_base: int
    agilidade_base: int
    resistencia_base: int
    percepcao_base: int
    exuberancia_base: int

class PersonagemResponse(BaseModel):
    id: int
    nome: str
    nivel: int
    raca: RacaResponse
    classe: ClasseRPGResponse
    # Trazemos as FKs de equipamentos como opcionais por enquanto
    mao_direita_id: Optional[int] = None
    mao_esquerda_id: Optional[int] = None
    armadura_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)