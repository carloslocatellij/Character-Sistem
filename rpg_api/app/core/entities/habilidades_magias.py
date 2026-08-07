from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from app.core.entities.emojis import dict_emoji_efeito

# ==========================================
# DOMÍNIO: EFEITOS, HABILIDADES E MAGIAS
# ==========================================


@dataclass
class Efeito:
    """Representa uma condição temporária aplicada a um personagem."""
    nome: str
    duracao_turnos: int
    tipo: str  # "dano_continuo", "cura_continua", "buff_atributo", "debuff_atributo", "sono", "atordoado", "lentidao", "louco", "protecao_elemental", "fraqueza_elemental"
    valor: int = 0
    atributo_alvo: Optional[str] = None # Qual atributo ele afeta (se for buff/debuff)
    configuracoes: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None

    def processar_efeito(self, alvo) -> dict:
        """Aplica o efeito no alvo a cada turno."""
        evento = {"nome": self.nome, "tipo": self.tipo, "valor": self.valor}
        
        if self.tipo == "dano_continuo":
            alvo.receber_dano_de_efeito(self.valor)
        elif self.tipo == "cura_continua":
            alvo.pv_atual = min(alvo.max_hp, alvo.pv_atual + self.valor)
        elif self.tipo == "sono":
            evento["pula_turno"] = True
            evento["mensagem"] = f"{alvo.nome} está dormindo!"
        elif self.tipo == "atordoado":
            evento["pula_turno"] = True
            evento["mensagem"] = f"{alvo.nome} está atordoado!"
        elif self.tipo == "louco":
            evento["alvo_aleatorio"] = True
            evento["mensagem"] = f"{alvo.nome} está confuso/louco!"
            
        self.duracao_turnos -= 1
        evento["turnos_restantes"] = self.duracao_turnos
        return evento
    
    def __str__(self) -> str:
        emoji_padrao = getattr(self, "emoji", "✨")
        return f"{dict_emoji_efeito.get(self.nome.lower(), emoji_padrao)}"

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
    """Representa um encanto dos Caminhos Elementais ou Habilidade Mágica."""
    nome: str
    custo_pm: int
    requisito_caminhos: Dict[str, int] = field(default_factory=dict) # Ex: {"fogo": 2, "ar": 1}
    dano_base: int = 0
    cura_base: int = 0
    dano_area: bool = False
    tipo_execucao: str = "combate"  # "combate", "fora_combate", "ambos"
    descricao: str = ""
    propriedades_combate: Dict[str, Any] = field(default_factory=dict) # Ex: {"critico_ampliado": True, "ignorar_defesa": True}
    efeito_aplicado: Optional[Efeito] = None
    requisito_exuberancia: int = 1
    id: Optional[int] = None