
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List

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
    """Guarda os atributos de combate e informações vitais do personagem."""
    nome: str
    classe: str
    hp: int
    max_hp: int
    mp: int
    max_mp: int
    ataque_base: int
    defesa_base: int
    

@dataclass
class InventoryComponent:
    """Armazena os itens que o personagem está carregando."""
    # Lista de dicionários representando os itens: [{"id": 1, "nome": "Poção", "tipo": "consumivel", "bonus": 0}]
    itens: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EquipmentComponent:
    """Armazena o que está atualmente equipado no herói influenciando seus atributos."""
    arma: Optional[Dict[str, Any]
                   # Ex: {"nome": "Espada de Ferro", "bonus_atk": 10}
                   ] = None
    # Ex: {"nome": "Cota de Malha", "bonus_def": 5}
    armadura: Optional[Dict[str, Any]] = None
