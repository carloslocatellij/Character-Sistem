import pytest
import esper
from app.core.engine.engine_loader import GameEngineLoader
from app.core.engine.components import PositionComponent, RenderComponent

def test_fluxo_completo_engine_manager():
    esper.clear_database()
    manager = GameEngineLoader()
    
    # Criação de entidade
    ent_id = esper.create_entity()
    assert ent_id == 1
    
    # Anexar componentes
    esper.add_component(ent_id, PositionComponent(x=10, y=5))
    esper.add_component(ent_id, RenderComponent(emoji="👾"))
    
    # Recuperação
    pos = esper.get_component( PositionComponent)[0]
    render = esper.get_component( RenderComponent)[0]
    
    assert pos[1].x == 10
    assert render[1].emoji == "👾"
    
    # Filtragem por sistemas
    #lista = esper.has_components(PositionComponent, RenderComponent)
    #assert ent_id in lista
    assert esper.has_components(ent_id, PositionComponent, RenderComponent) is True