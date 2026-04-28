
from dataclasses import dataclass, field # Add field here
from typing import Dict
from typing import Optional
from app.core.emojis import dict_emoji_efeito

# ==========================================
# DOMÍNIO: EFEITOS, HABILIDADES E MAGIAS
# ==========================================

@dataclass
class Efeito:
    """Representa uma condição temporária aplicada a um personagem."""
    nome: str
    duracao_turnos: int
    tipo: str  # "dano_continuo", "cura_continua", "buff_atributo", "debuff_atributo"
    valor: int
    atributo_alvo: Optional[str] = None # Qual atributo ele afeta (se for buff/debuff)
    
    def processar_efeito(self, alvo) -> dict:
        """Aplica o efeito no alvo a cada turno."""
        evento = {"nome": self.nome, "tipo": self.tipo, "valor": self.valor}
        
        if self.tipo == "dano_continuo":
            alvo.receber_dano_de_efeito(self.valor)
        elif self.tipo == "cura_continua":
            alvo.pv_atual = min(alvo.pv_max, alvo.pv_atual + self.valor)
            
        self.duracao_turnos -= 1
        evento["turnos_restantes"] = self.duracao_turnos
        return evento
    
    def __str__(self) -> str:
      return f"{dict_emoji_efeito.get(self.nome.lower(), self.emoji)}"

@dataclass
class Habilidade:
    """Representa perícias ou golpes físicos especiais."""
    nome: str
    requisito_atributo: str  # Ex: "forca"
    requisito_valor: int     # Ex: 3 (exige Força 3 para usar/aprender)
    dano_extra: int = 0
    efeito_aplicado: Optional[Efeito] = None

@dataclass
class Magia:
    """Representa um encanto dos Caminhos Elementais."""
    nome: str
    custo_pm: int
    requisito_caminhos: Dict[str, int] = field(default_factory=dict) # Ex: {"fogo": 2, "ar": 1}
    dano_base: int = 0
    efeito_aplicado: Optional[Efeito] = None
    requisito_exuberancia: int = 1