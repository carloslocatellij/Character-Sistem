import pytest
from rpg_api._legacy.manager import EngineManager
from app.core.engine.components import PositionComponent, RenderComponent

def test_fluxo_completo_engine_manager():
    manager = EngineManager()
    
    # Criação de entidade
    ent_id = manager.create_entity()
    assert ent_id == 1
    
    # Anexar componentes
    manager.add_component(ent_id, PositionComponent(x=10, y=5))
    manager.add_component(ent_id, RenderComponent(emoji="👾"))
    
    # Recuperação
    pos = manager.get_component(ent_id, "PositionComponent")
    render = manager.get_component(ent_id, "RenderComponent")
    
    assert pos.x == 10
    assert render.emoji == "👾"
    
    # Filtragem por sistemas
    lista = manager.get_entities_with("PositionComponent", "RenderComponent")
    assert ent_id in lista