import pytest
from rich.text import Text
from app.core.engine.components import PositionComponent, RenderComponent
from app.core.engine.render import RenderSystem

# Cenário de Teste: Mapa 2x2 de Grama (🟩)
MAPA_BASE_TESTE = [
    ["🟩", "🟩"],
    ["🟩", "🟩"]
]
# Uma árvore estática no (0, 1)
OBJETOS_TESTE = {(0, 1): "🌲"}

@pytest.fixture
def mock_engine_com_jogador():
    class MockECS:
        def __init__(self):
            # O jogador está na linha 1, coluna 0 (y=1, x=0)
            self.entidades = {
                1: {"PositionComponent": PositionComponent(x=0, y=1),
                    "RenderComponent": RenderComponent(emoji='🧙')
                    }
            }
        def get_component(self, ent_id, comp_name):
            return self.entidades.get(ent_id, {}).get(comp_name)
        def get_entities_with(self, *names):
            return [1] # Retorna o ID do jogador
    return MockECS()

def test_renderizacao_camadas_e_prioridade(mock_engine_com_jogador):
    """Garante que o renderizador sobrepõe Chão -> Objeto -> Jogador na ordem certa."""
    # O emoji do jogador será "🧙"
    renderer = RenderSystem(engine_manager=mock_engine_com_jogador)
    
    # Executa a renderização lógica
    texto_renderizado = renderer.renderizar_frame(
        mapa_matriz=MAPA_BASE_TESTE,
        dict_objetos=OBJETOS_TESTE
    )
    
    # Convertemos para string pura para checar os caracteres
    string_pura = texto_renderizado.plain
    
    # Linha 0 deve ter: Grama (🟩) e depois Árvore (🌲)
    # Linha 1 deve ter: Jogador (🧙‍♂️) e depois Grama (🟩)
    linhas = string_pura.strip().split("\n")
    
    assert "🟩" in linhas[0]
    assert "🌲" in list(linhas[0])[1] # Verifica o segundo caractere visual
    assert "🧙" in linhas[1]