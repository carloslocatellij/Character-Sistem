# rpg_api/tests/test_renderizador.py
import pytest
import esper
from app.core.engine.render import RenderSystem
from app.core.engine.components import PositionComponent, RenderComponent


@pytest.fixture(autouse=True)
def restaurar_mundo_esper():
    """
    Garante o isolamento completo entre os testes limpando 
    completamente todas as entidades e componentes da memória do Esper.
    """
    # 🧼 Limpa a base de dados interna do mundo atual do Esper
    esper.clear_database()

    # Se o seu sistema inicializar múltiplos mundos, garante o reset do mundo principal
    if esper.list_worlds():
        esper.switch_world(esper.list_worlds()[0])
    else:
        esper.switch_world(esper.World())


def test_renderizacao_camadas_e_prioridade():
    """
    Testa se o Z-Index do RenderSystem respeita a ordem de prioridades:
    1° Entidades do Esper ECS -> 2° Objetos Estáticos -> 3° Terreno Base
    """
    # 1. SETUP: Matriz base 1x1 com chão comum ("  ")
    mapa_matriz = [["  "]]

    # Objeto de cenário posicionado na coordenada (Y=0, X=0)
    dict_objetos = {(0, 0): "🌳"}

    # Criamos uma Entidade dinâmica no Esper exatamente em cima do objeto e do chão (X=0, Y=0)
    esper.create_entity(
        PositionComponent(x=0, y=0),
        RenderComponent(emoji="🧙🏻‍♂️")
    )

    # 2. AÇÃO: Instancia o renderizador
    renderer = RenderSystem()
    frame_resultado = renderer.renderizar_frame(mapa_matriz, dict_objetos)

    # Convertemos o buffer do Rich Text para string crua para validar os caracteres
    texto_cru = frame_resultado.plain

    # 3. VALIDAÇÃO: Como a entidade tem prioridade máxima no Z-Index,
    # o emoji do mago "🧙🏻‍♂️" deve sobressair e ser renderizado, ocultando a árvore e o chão.
    assert "🧙🏻‍♂️" in texto_cru
    assert "🌳" not in texto_cru
    assert "  " not in texto_cru


def test_deve_renderizar_objeto_se_nao_houver_entidade():
    """Garante que se não houver entidade no local, o objeto estático seja desenhado."""
    # 1. SETUP: Desta vez o Esper nascerá vazio devido à fixture autouse
    mapa_matriz = [["  "]]
    dict_objetos = {(0, 0): "🌳"}

    # 2. AÇÃO: Renderiza sem criar entidades no Esper
    renderer = RenderSystem()
    frame_resultado = renderer.renderizar_frame(mapa_matriz, dict_objetos)

    # 3. VALIDAÇÃO: Como o Esper está limpo, o Z-Index cai para a 2ª prioridade (Objetos de cenário)
    texto_cru = frame_resultado.plain
    assert "🌳" in texto_cru
    assert "🧙🏻‍♂️" not in texto_cru
