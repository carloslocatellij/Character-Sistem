# rpg_api/tests/test_interaction_system.py
import inspect
import pytest
import esper
from app.core.engine.components import PositionComponent, PlayerControlComponent, InteractableComponent
from app.core.engine.systems import MovementSystem, InteractionSystem


def create_player_control(direcao="direita"):
    sig = inspect.signature(PlayerControlComponent.__init__).parameters
    kwargs = {}
    if "direcao_olhar" in sig:
        kwargs["direcao_olhar"] = direcao
    elif "direcao" in sig:
        kwargs["direcao"] = direcao
    elif "facing" in sig:
        kwargs["facing"] = direcao

    player_control = PlayerControlComponent(**kwargs) if kwargs else PlayerControlComponent()
    for attr in ("direcao_olhar", "direcao", "facing"):
        if hasattr(player_control, attr):
            setattr(player_control, attr, direcao)
            break

    return player_control


def build_interactable_component(event_type, parametros, on_interact):
    sig = inspect.signature(InteractableComponent.__init__).parameters
    kwargs = {}

    if "tipo_evento" in sig:
        kwargs["tipo_evento"] = event_type
    elif "event_type" in sig:
        kwargs["event_type"] = event_type
    elif "evento" in sig:
        kwargs["evento"] = event_type
    elif "tipo" in sig:
        kwargs["tipo"] = event_type

    if "parametros" in sig:
        kwargs["parametros"] = parametros
    elif "params" in sig:
        kwargs["params"] = parametros
    elif "parameters" in sig:
        kwargs["parameters"] = parametros
    elif "dados" in sig:
        kwargs["dados"] = parametros

    if "on_interact" in sig:
        kwargs["on_interact"] = on_interact
    elif "callback" in sig:
        kwargs["callback"] = on_interact
    elif "action" in sig:
        kwargs["action"] = on_interact
    elif "executar" in sig:
        kwargs["executar"] = on_interact

    return InteractableComponent(**kwargs)


def invoke_movement(system, entity, direcao):
    mover = getattr(system, "mover_entidade", None) or getattr(system, "move_entity", None) or getattr(system, "move", None)
    if mover is None:
        raise AttributeError("MovementSystem does not expose a movement method")
    return mover(entity, direcao)


def invoke_interaction(system, entity, direcao):
    interagir = getattr(system, "interagir", None) or getattr(system, "interact", None)
    if interagir is None:
        raise AttributeError("InteractionSystem does not expose an interaction method")

    try:
        return interagir(entity, direcao)
    except TypeError:
        return interagir(entity)


class MockMapLoader:
    """Um mock leve para simular as propriedades do GameEngineLoader sem acessar o BD."""

    def __init__(self):
        self.altura = 5
        self.largura = 5
        self.matriz_terrenos = [["  " for _ in range(5)] for _ in range(5)]
        self.matriz_terreno = self.matriz_terrenos
        self.terrenos = self.matriz_terrenos
        self.camada_objetos = {(2, 1): "🌳"}
        self.objetos = self.camada_objetos
        self.matriz_objetos = self.camada_objetos
        self.mapa_objetos = self.camada_objetos

        self.matriz_terrenos[2][1] = "🧱"

    def get_terrain_at(self, x, y):
        return self.matriz_terrenos[y][x]

    def get_terrain(self, x, y):
        return self.get_terrain_at(x, y)

    def get_tile_at(self, x, y):
        return self.get_terrain_at(x, y)

    def get_tile(self, x, y):
        return self.get_terrain_at(x, y)

    def get_terreno(self, x, y):
        return self.get_terrain_at(x, y)

    def get_object_at(self, x, y):
        return self.camada_objetos.get((x, y))

    def get_object(self, x, y):
        return self.get_object_at(x, y)

    def get_objeto(self, x, y):
        return self.get_object_at(x, y)

    def is_within_bounds(self, x, y):
        return 0 <= x < self.largura and 0 <= y < self.altura

    def esta_dentro_dos_limites(self, x, y):
        return self.is_within_bounds(x, y)

    def is_valid_position(self, x, y):
        return self.is_within_bounds(x, y)

    def posicao_valida(self, x, y):
        return self.is_within_bounds(x, y)

    def is_position_blocked(self, x, y):
        terrain = self.get_terrain_at(x, y)
        return terrain == "🧱" or (x, y) in self.camada_objetos

    def is_blocked(self, x, y):
        return self.is_position_blocked(x, y)

    def is_blocked_at(self, x, y):
        return self.is_position_blocked(x, y)

    def esta_bloqueada(self, x, y):
        return self.is_position_blocked(x, y)


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

    def mock_script_bau(player, params):
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