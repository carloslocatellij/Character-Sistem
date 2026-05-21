# rpg_api/app/engine/components.py
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PositionComponent:
    """Onde a entidade está no mapa lógico."""
    x: int
    y: int
    direcao_olhar: str = "baixo"

@dataclass
class CollisionComponent:
    is_solid: bool = True # Se for False, a entidade é "atravessável" (ex: um trigger de armadilha no chão)

@dataclass
class RenderComponent:
    """Como a entidade se parece na interface."""
    emoji: str

@dataclass
class InteractableComponent:
    """Define que a entidade pode receber uma ação (tecla Enter)."""
    event_type: str          # Ex: 'bau', 'npc_dialogo', 'porta'
    parameters: dict         # Ex: {'item': 'pocao', 'quantidade': 1}
    is_active: bool = True   # Permite desligar a interação (ex: um baú já aberto)

@dataclass
class PlayerControlComponent:
    """Uma flag que indica que esta entidade é controlada pelo teclado."""
    pass