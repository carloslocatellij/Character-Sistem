# rpg_api/tests/test_movement_system.py
import pytest
import esper
from app.core.engine.components import PositionComponent, PlayerControlComponent, InteractableComponent
from app.core.engine.systems import MovementSystem, InteractionSystem



class MockMapLoader:
    """Um mock leve para simular as propriedades do GameEngineLoader sem acessar o BD."""

    def __init__(self):
        self.altura = 5
        self.largura = 5
        self.matriz_terrenos = [["  " for _ in range(5)] for _ in range(5)]
        # Bloqueia a coordenada x=1, y=2 com uma parede lógica (matriz[y][x])
        self.matriz_terrenos[2][1] = "🧱"
        # Adiciona um objeto sólido estático na coordenada x=2, y=1 (matriz[y][x])
        self.camada_objetos = {(1, 2): "🌳"}


@pytest.fixture(autouse=True)
def setup_esper():
    """Reseta o mundo global do Esper antes de cada teste."""
    esper.clear_database()
    if esper.list_worlds():
        esper.switch_world(esper.list_worlds()[0])
    else:
        esper.switch_world(esper.World())


def test_deve_mover_entidade_para_posicao_valida():
    # 1. SETUP: Criar o jogador em (1, 0) livre de obstáculos
    player = esper.create_entity(
        PositionComponent(x=1, y=0),
        PlayerControlComponent()
    )
    map_loader = MockMapLoader()
    system = MovementSystem(map_loader)

    # 2. AÇÃO: Mover para a direita (X aumenta) -> nova posição esperada: (2, 0)
    sucesso = system.mover_entidade(player, "direita")

    # 3. VALIDAÇÃO: O movimento deve ser aceito e a posição alterada
    pos = esper.component_for_entity(player, PositionComponent)
    assert sucesso is True
    assert pos.x == 2
    assert pos.y == 0


def test_nao_deve_mover_para_cima_de_terreno_bloqueante():
    # 1. SETUP: Jogador em (1, 1). A coordenada (1, 2) é uma parede ("🧱")
    player = esper.create_entity(
        PositionComponent(x=1, y=1),
        PlayerControlComponent()
    )
    map_loader = MockMapLoader()
    system = MovementSystem(map_loader)

    # 2. AÇÃO: Tentar mover para "baixo" (Y aumenta) -> (1, 2), onde há a parede
    sucesso = system.mover_entidade(player, "baixo")

    # 3. VALIDAÇÃO: O movimento deve ser recusado e a posição mantida em (1, 1)
    pos = esper.component_for_entity(player, PositionComponent)
    assert sucesso is False
    assert pos.x == 1
    assert pos.y == 1


def test_nao_deve_mover_para_cima_de_objeto_solido():
    # 1. SETUP: Jogador em (1, 1). A coordenada (2, 1) tem uma árvore ("🌳")
    player = esper.create_entity(
        PositionComponent(x=1, y=1),
        PlayerControlComponent()
    )
    map_loader = MockMapLoader()
    system = MovementSystem(map_loader)

    # 2. AÇÃO: Tentar mover para a direita (X aumenta) -> (2, 1) onde está a árvore
    sucesso = system.mover_entidade(player, "direita")

    # 3. VALIDAÇÃO: Bloqueado pelo objeto estático
    pos = esper.component_for_entity(player, PositionComponent)
    assert sucesso is False
    assert pos.x == 1
    assert pos.y == 1



def test_deve_interagir_com_bau_na_frente_do_jogador():
    # 1. SETUP: Criar o jogador olhando para a DIREITA (X=1, Y=1)
    player = esper.create_entity(
        PositionComponent(x=1, y=1),
        PlayerControlComponent()
    )

    # Criar um baú exatamente à direita do jogador (X=2, Y=1)
    bau_chamado = {"executado": False}

    def mock_script_bau(player_id, params):
        bau_chamado["executado"] = True
        bau_chamado["recompensa"] = params.get("item")

    bau = esper.create_entity(
        PositionComponent(x=2, y=1),
        InteractableComponent(
            event_type="bau",
            parametros={"item": "Poção de Vida"},
            on_interact=mock_script_bau
        )
    )

    system = InteractionSystem()

    # 2. AÇÃO: Jogador tenta interagir olhando para a "direita"
    sucesso = system.interagir(player, "direita")

    # 3. VALIDAÇÃO: O sistema encontrou o baú e executou seu comportamento
    assert sucesso is True
    assert bau_chamado["executado"] is True
    assert bau_chamado["recompensa"] == "Poção de Vida"


def test_deve_retornar_false_se_nao_houver_nada_para_interagir():
    # 1. SETUP: Jogador isolado em (1, 1)
    player = esper.create_entity(
        PositionComponent(x=1, y=1),
        PlayerControlComponent()
    )
    system = InteractionSystem()

    # 2. AÇÃO: Tenta interagir para "cima" (onde está vazio)
    sucesso = system.interagir(player, "cima")

    # 3. VALIDAÇÃO: Nenhuma interação ocorreu
    assert sucesso is False
    
    



# import pytest
# from app.core.engine.components import PositionComponent, CollisionComponent, InteractableComponent
# from app.core.engine.systems import MovementSystem, InteractionSystem
# from app.core.engine.event_bus import EventBus

# # Matriz de teste (3x3)
# # 🔲 = Parede (Bloqueia)
# # 🟫 = Chão (Livre)
# MAPA_TESTE_MATRIZ = [
#     ["🔲", "🔲", "🔲"],
#     ["🔲", "🟫", "🟫"],
#     ["🔲", "🟫", "🔲"]
# ]
# TILES_BLOQUEANTES = ["🔲"]

# @pytest.fixture
# def mock_engine_manager():
#     """Simula o engine Manager com um Jogador e um Baú Mágico."""
#     class MockECS:
#         def __init__(self):
#             self.entidades = {
#                 # O Jogador (ID 1) está no (1,1) a olhar para a direita
#                 1: {"PositionComponent": PositionComponent(x=1, y=1, direcao_olhar="direita")},
                
#                 # O Baú (ID 2) está no (2,1) e é interagível
#                 2: {
#                     "PositionComponent": PositionComponent(x=2, y=1),
#                     "InteractableComponent": InteractableComponent(
#                         event_type="bau", 
#                         parametros={"item": "Espada de Fogo"}
#                     ), "CollisionComponent": CollisionComponent(solido=True)
#                 }
#             }
        
#         def get_component(self, entity_id, component_name):
#             return self.entidades.get(entity_id, {}).get(component_name)
            
#         def get_entities_with(self, *component_names):
#             result = []
#             for ent_id, comps in self.entidades.items():
#                 if all(c in comps for c in component_names):
#                     result.append(ent_id)
#             return result

#     return MockECS()


    

# def test_interacao_com_sucesso(mock_engine_manager):
#     """Garante que apertar Enter virado para o baú EMITE o evento no EventBus."""
#     bus = EventBus() # ✅ 1. Cria o mensageiro
#     system = InteractionSystem(engine_manager=mock_engine_manager, event_bus=bus) # ✅ 2. Injeta o mensageiro
    
#     # 3. Variável para capturar a mensagem que a Engine vai emitir
#     evento_capturado = {}
    
#     def ouvinte_de_teste(dados):
#         evento_capturado.update(dados)
        
#     # 4. Assina o canal 'bau' antes de interagir
#     bus.subscribe("bau", ouvinte_de_teste)
    
#     # 5. O Jogador (ID 1) tenta interagir
#     system.interact(entity_id=1)
    
#     # ✅ 6. Validação: O evento deve ter chegado ao nosso ouvinte!
#     assert evento_capturado != {}
#     assert evento_capturado["entity_id"] == 2
#     assert evento_capturado["parametros"]["item"] == "Espada de Fogo"



# def test_interacao_no_vazio_falha(mock_engine_manager):
#     """Garante que interagir a olhar para o nada não emite evento nenhum."""
#     bus = EventBus()
#     system = InteractionSystem(engine_manager=mock_engine_manager, event_bus=bus)
    
#     evento_capturado = {}
#     def ouvinte_de_teste(dados):
#         evento_capturado.update(dados)
        
#     bus.subscribe("bau", ouvinte_de_teste)
    
#     # Mudamos o olhar do jogador para cima (onde não há nada)
#     pos = mock_engine_manager.get_component(1, "PositionComponent")
#     pos.direcao_olhar = "cima"
    
#     system.interact(entity_id=1)
    
#     # O dicionário deve continuar vazio pois nenhum evento foi emitido na rádio
#     assert evento_capturado == {}