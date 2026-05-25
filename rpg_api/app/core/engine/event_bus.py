# app/core/engine/event_bus.py

class EventBus:
    """
    Sistema de Mensageria (Pub/Sub) para desacoplar a Engine da Interface.
    """
    def __init__(self):
        # Dicionário que guarda: {"tipo_do_evento": [lista_de_funcoes_callback]}
        self._listeners = {}

    def subscribe(self, event_type: str, callback):
        """Inscreve uma função para escutar um tipo específico de evento."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        # Evita inscrever a mesma função duas vezes
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def emit(self, event_type: str, event_data: dict = None):
        """Grita para todos os ouvintes que o evento aconteceu, passando os dados."""
        if event_data is None:
            event_data = {}
            
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(event_data)