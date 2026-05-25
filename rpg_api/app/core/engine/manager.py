# app/core/engine/manager.py

class EngineManeger:
    """
    O Gestor engine Definitivo. Controla a criação de entidades e o ciclo
    de vida dos componentes anexados a elas.
    """
    def __init__(self):
        self._next_entity_id = 1
        # Estrutura: { entity_id: { "NomeDoComponente": instancia_do_componente } }
        self.entities = {}

    def create_entity(self) -> int:
        """Cria uma nova assinatura de entidade única no motor."""
        entity_id = self._next_entity_id
        self.entities[entity_id] = {}
        self._next_entity_id += 1
        return entity_id

    def add_component(self, entity_id: int, component):
        """Anexa um componente a uma entidade existente."""
        if entity_id in self.entities:
            comp_name = component.__class__.__name__
            self.entities[entity_id][comp_name] = component

    def get_component(self, entity_id: int, component_name: str):
        """Resgata um componente específico de uma entidade."""
        return self.entities.get(entity_id, {}).get(component_name)

    def get_entities_with(self, *component_names) -> list[int]:
        """Retorna uma lista de IDs de entidades que possuem TODOS os componentes pedidos."""
        matching_entities = []
        for entity_id, components in self.entities.items():
            if all(comp_name in components for comp_name in component_names):
                matching_entities.append(entity_id)
        return matching_entities

    def remove_entity(self, entity_id: int):
        """Apaga a entidade e todos os seus componentes da memória lúdica."""
        if entity_id in self.entities:
            del self.entities[entity_id]