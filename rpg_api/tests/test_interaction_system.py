import pytest
from app.core.engine.components import PositionComponent, CollisionComponent, InteractableComponent
from app.core.engine.systems import MovementSystem, InteractionSystem
from app.core.engine.event_bus import EventBus

# Matriz de teste (3x3)
# 🔲 = Parede (Bloqueia)
# 🟫 = Chão (Livre)
MAPA_TESTE_MATRIZ = [
    ["🔲", "🔲", "🔲"],
    ["🔲", "🟫", "🟫"],
    ["🔲", "🟫", "🔲"]
]
TILES_BLOQUEANTES = ["🔲"]

@pytest.fixture
def mock_ecs_manager():
    """Simula o ECS Manager com um Jogador e um Baú Mágico."""
    class MockECS:
        def __init__(self):
            self.entidades = {
                # O Jogador (ID 1) está no (1,1) a olhar para a direita
                1: {"Position": PositionComponent(x=1, y=1, direcao_olhar="direita")},
                
                # O Baú (ID 2) está no (2,1) e é interagível
                2: {
                    "Position": PositionComponent(x=2, y=1),
                    "Interactable": InteractableComponent(
                        event_type="bau", 
                        parameters={"item": "Espada de Fogo"}
                    ), "Collision": CollisionComponent(is_solid=True)
                }
            }
        
        def get_component(self, entity_id, component_name):
            return self.entidades.get(entity_id, {}).get(component_name)
            
        def get_entities_with(self, *component_names):
            result = []
            for ent_id, comps in self.entidades.items():
                if all(c in comps for c in component_names):
                    result.append(ent_id)
            return result

    return MockECS()


def test_mover_para_chao_livre(mock_ecs_manager):
    system = MovementSystem(ecs_manager=mock_ecs_manager, mapa_matriz=MAPA_TESTE_MATRIZ, tiles_bloqueio=TILES_BLOQUEANTES)
    
    # Tenta mover o Jogador (ID 1) para baixo (dy=1, dx=0)
    sucesso = system.move_entity(entity_id=1, dx=0, dy=1)
    
    posicao = mock_ecs_manager.get_component(1, "Position")
    assert sucesso is True
    assert posicao.y == 2
    assert posicao.x == 1
    assert posicao.direcao_olhar == "baixo"

def test_colisao_com_parede_do_mapa(mock_ecs_manager):
    system = MovementSystem(ecs_manager=mock_ecs_manager, mapa_matriz=MAPA_TESTE_MATRIZ, tiles_bloqueio=TILES_BLOQUEANTES)
    
    # Tenta mover o Jogador (ID 1) para a esquerda contra a parede (dx=-1, dy=0)
    sucesso = system.move_entity(entity_id=1, dx=-1, dy=0)
    
    posicao = mock_ecs_manager.get_component(1, "Position")
    assert sucesso is False
    assert posicao.x == 1 # Não andou
    assert posicao.direcao_olhar == "esquerda" # Mas virou o rosto!

def test_colisao_com_entidade_solida(mock_ecs_manager):
    system = MovementSystem(ecs_manager=mock_ecs_manager, mapa_matriz=MAPA_TESTE_MATRIZ, tiles_bloqueio=TILES_BLOQUEANTES)
    
    # Tenta mover o Jogador (ID 1) para a direita contra o NPC (dx=1, dy=0)
    sucesso = system.move_entity(entity_id=1, dx=1, dy=0)
    
    posicao = mock_ecs_manager.get_component(1, "Position")
    assert sucesso is False
    assert posicao.x == 1 # Bloqueado pelo NPC
    assert posicao.direcao_olhar == "direita"

def test_interacao_com_sucesso(mock_ecs_manager):
    """Garante que apertar Enter virado para o baú EMITE o evento no EventBus."""
    bus = EventBus() # ✅ 1. Cria o mensageiro
    system = InteractionSystem(ecs_manager=mock_ecs_manager, event_bus=bus) # ✅ 2. Injeta o mensageiro
    
    # 3. Variável para capturar a mensagem que a Engine vai emitir
    evento_capturado = {}
    
    def ouvinte_de_teste(dados):
        evento_capturado.update(dados)
        
    # 4. Assina o canal 'bau' antes de interagir
    bus.subscribe("bau", ouvinte_de_teste)
    
    # 5. O Jogador (ID 1) tenta interagir
    system.interact(entity_id=1)
    
    # ✅ 6. Validação: O evento deve ter chegado ao nosso ouvinte!
    assert evento_capturado != {}
    assert evento_capturado["entity_id"] == 2
    assert evento_capturado["parameters"]["item"] == "Espada de Fogo"


def test_interacao_no_vazio_falha(mock_ecs_manager):
    """Garante que interagir a olhar para o nada não emite evento nenhum."""
    bus = EventBus()
    system = InteractionSystem(ecs_manager=mock_ecs_manager, event_bus=bus)
    
    evento_capturado = {}
    def ouvinte_de_teste(dados):
        evento_capturado.update(dados)
        
    bus.subscribe("bau", ouvinte_de_teste)
    
    # Mudamos o olhar do jogador para cima (onde não há nada)
    pos = mock_ecs_manager.get_component(1, "Position")
    pos.direcao_olhar = "cima"
    
    system.interact(entity_id=1)
    
    # O dicionário deve continuar vazio pois nenhum evento foi emitido na rádio
    assert evento_capturado == {}