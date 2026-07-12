from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
import time

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
    event_type: str  # 'bau', 'porta', 'npc_dialogo', etc.
    parametros: Dict[str, Any] = field(default_factory=dict)
    seguravel: bool = False
    # Callback opcional que a Engine executará passando a entidade que interagiu e os parâmetros
    on_interact: Optional[Callable[[int, Dict[str, Any]], None]] = None

@dataclass
class PlayerControlComponent:
    """Uma flag que indica que esta entidade é controlada pelo teclado."""
    pass

@dataclass
class MovimentComponent:
    """Define o comportamento autônomo (NPCs, Monstros, Pets)."""
    movement_type: str  # Ex: "aleatorio", "patrulha", "seguir"
    roteiro: list
    ciclos: int
    action_on_touch: dict    # O que faz se esbarrar em alguém
    roteiro_idx: int = 0

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
    arma: Optional[Dict[str, Any]] = None
    armadura: Optional[Dict[str, Any]] = None
    escudo: Optional[Dict[str, Any]] = None

@dataclass
class NetworkPlayerComponent:
    """Identificador para jogadores que estão conectados via rede (multiplayer)."""
    username: str
    connection_id: str
    latency_ms: int = 0


# ==========================================
# COMPONENTES DE COMBATE POR TURNOS
# ==========================================

@dataclass
class CombatStateComponent:
    """
    Marca uma entidade como estando em combate ativo e armazena metadados do turno.
    Apenas a entidade do jogador (ID 1) deverá ter este componente enquanto houver
    uma batalha em andamento. Remova-o ao encerrar o combate.
    """
    em_combate: bool = True
    turno_atual: int = 0
    iniciativa_jogador: int = 0
    iniciativa_inimigo: int = 0
    # Fase atual: "aguardando_acao" | "calculando_ia" | "executando_turno_jogador" | "encerrado"
    fase_turno: str = "aguardando_acao"
    timestamp_inicio: float = field(default_factory=time.time)


@dataclass
class BattleParticipantComponent:
    """
    Liga um identificador de participante ao contexto de uma batalha.
    Permite que o BattleSystem saiba quais entidades ECS são combatentes ativos
    e quais dados de domínio (Personagem) usar para os cálculos.
    """
    personagem_id: str                    # Identificador único do participante (ex: "heroi_1", "inimigo_goblin")
    tipo: str                             # "jogador" | "inimigo" | "rede"
    nivel: int = 1
    emoji_sprite: str = "👹"
    nome_display: str = "Inimigo"
    xp_recompensa: int = 10
    drops_possiveis: List[Dict[str, Any]] = field(default_factory=list)
