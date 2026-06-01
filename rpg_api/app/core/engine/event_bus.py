# rpg_api/app/core/engine/event_bus.py
from typing import Callable, Dict, List, Any


class EventBus:
    """
    Barramento de Eventos Centralizado (Padrão Pub/Sub).
    Permite desacoplar a lógica do motor (Esper ECS) da camada visual (Textual).
    """

    def __init__(self):
        # Dicionário mapeando NomeDoTopico -> Lista de Callbacks
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, tipo_evento: str, callback: Callable[[Any], None]) -> None:
        """Inscreve uma função para ouvir um determinado tipo de evento."""
        if tipo_evento not in self._listeners:
            self._listeners[tipo_evento] = []

        # Evita duplicar o mesmo listener para o mesmo evento
        if callback not in self._listeners[tipo_evento]:
            self._listeners[tipo_evento].append(callback)

    def unsubscribe(self, tipo_evento: str, callback: Callable[[Any], None]) -> None:
        """Remove a inscrição de um escutador específico."""
        if tipo_evento in self._listeners and callback in self._listeners[tipo_evento]:
            self._listeners[tipo_evento].remove(callback)

    def publish(self, tipo_evento: str, payload: Any = None) -> None:
        """Dispara um evento para todos os subscritores registados naquele tópico."""
        if tipo_evento in self._listeners:
            # Fazemos uma cópia da lista para evitar erros se alguém se desinscrever durante o loop
            for callback in self._listeners[tipo_evento][:]:
                try:
                    callback(payload)
                except Exception as e:
                    # Logs de salvaguarda para evitar que um erro na UI trave o loop interno da Engine
                    print(
                        f"[EventBus Error] Falha ao processar evento '{tipo_evento}': {e}")
                    
                    
# class EventBus:
#     """
#     Sistema de Mensageria (Pub/Sub) para desacoplar a Engine da Interface.
#     """
#     def __init__(self):
#         # Dicionário que guarda: {"tipo_do_evento": [lista_de_funcoes_callback]}
#         self._listeners = {}

#     def subscribe(self, tipo_evento: str, callback):
#         """Inscreve uma função para escutar um tipo específico de evento."""
#         if tipo_evento not in self._listeners:
#             self._listeners[tipo_evento] = []
        
#         # Evita inscrever a mesma função duas vezes
#         if callback not in self._listeners[tipo_evento]:
#             self._listeners[tipo_evento].append(callback)

#     def emit(self, tipo_evento: str, event_data: dict = None):
#         """Grita para todos os ouvintes que o evento aconteceu, passando os dados."""
#         if event_data is None:
#             event_data = {}
            
#         if tipo_evento in self._listeners:
#             for callback in self._listeners[tipo_evento]:
#                 callback(event_data)