# rpg_api/app/engine/components.py
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PositionComponent:
    """Onde a entidade está no mapa lógico."""
    x: int
    y: int

@dataclass
class RenderComponent:
    """Como a entidade se parece na interface."""
    emoji: str

@dataclass
class InteractableComponent:
    """O que acontece quando o jogador aperta Enter de frente para ela."""
    tipo_evento: str # Ex: 'bau', 'porta', 'npc'
    parametros: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlayerControlComponent:
    """Uma flag que indica que esta entidade é controlada pelo teclado."""
    pass