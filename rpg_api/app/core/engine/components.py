# rpg_api/app/engine/components.py
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class PositionComponent:
    """Onde a entidade está no mapa lógico."""
    x: int
    y: int
    direcao_olhar: str = "baixo"

@dataclass
class CollisionComponent:
    solido: bool = True # Se for False, a entidade é "atravessável" (ex: um trigger de armadilha no chão)

@dataclass
class RenderComponent:
    """Como a entidade se parece na interface."""
    emoji: str

# @dataclass
# class InteractableComponent:
#     """Define que a entidade pode receber uma ação (tecla Enter)."""
#     tipo_evento: str          # Ex: 'bau', 'npc_dialogo', 'porta'
#     parametros: dict         # Ex: {'item': 'pocao', 'quantidade': 1}
#     is_active: bool = True   # Permite desligar a interação (ex: um baú já aberto)


@dataclass
class InteractableComponent:
    tipo_evento: str  # 'bau', 'porta', 'npc_dialogo', etc.
    parametros: Dict[str, Any] = field(default_factory=dict)
    seguravel: bool = False
    # Callback opcional que a Engine executará passando a entidade que interagiu e os parâmetros
    on_interact: Optional[Callable[[int, Dict[str, Any]], None]] = None

@dataclass
class PlayerControlComponent:
    """Uma flag que indica que esta entidade é controlada pelo teclado."""
    pass

@dataclass
class AIComponent:
    """Define o comportamento autônomo (NPCs, Monstros, Pets)."""
    tipo_movimento: str       # Ex: "aleatório", "patrulha", "seguir"
    action_on_touch: dict    # O que faz se esbarrar em alguém

@dataclass
class StatsComponent:
    """Guarda a matemática pura dos atributos vitais de combate."""
    nome: str
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    ataque_base: int
    defesa_base: int

@dataclass
class InventoryComponent:
    """Guarda os itens que a entidade carrega. Ex: {'poção': 3, 'espada_ferro': 1}"""
    itens: dict[str, int] = field(default_factory=dict)

@dataclass
class EquipmentComponent:
    """Mapeia o que a entidade tem atualmente equipado no corpo."""
    arma: dict | None = None      # Ex: {'nome': 'Espada Longa', 'bonus_atk': 5}
    armadura: dict | None = None  # Ex: {'nome': 'Armadura de Placas', 'bonus_def': 7}