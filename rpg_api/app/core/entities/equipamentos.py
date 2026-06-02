from dataclasses import dataclass
from typing import Optional
from app.core.entities.emojis import dict_item_emoji

# ==========================================
# DOMÍNIO: SISTEMA DE EQUIPAMENTOS
# ==========================================

@dataclass
class Item:
    """Classe base para todos os itens do jogo."""
    nome: str
    peso: float = 0.0
    emoji: str = "📦"
    
    def __str__(self) -> str:
      return f"{dict_item_emoji['outros'].get(self.nome.lower(), self.emoji)}"

@dataclass
class Arma(Item):
    """Herda de Item. Adiciona propriedades de ataque."""
    dano: int = 0
    tipo: str = "corpo" # "corpo" ou "distancia"
    emoji: str = "🗡️"
    
    def __str__(self) -> str:
      return f"{dict_item_emoji['armas'].get(self.nome.lower(), self.emoji)}"

@dataclass
class Armadura(Item):
    """Herda de Item. Adiciona propriedades de defesa base."""
    defesa: int = 0
    emoji: str = "🦺"
    
    def __str__(self) -> str:
      return f"{dict_item_emoji['armaduras'].get(self.nome.lower(), self.emoji)}"

@dataclass
class Escudo(Item):
    """Herda de Item. Adiciona propriedades de defesa extra."""
    defesa_extra: int = 0
    emoji: str = "🛡️"
    
    def __str__(self) -> str:
      return f"{dict_item_emoji['escudos'].get(self.nome.lower(), self.emoji)}"
