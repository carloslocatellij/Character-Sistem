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

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Inscreve uma função para ouvir um determinado tipo de evento."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        # Evita duplicar o mesmo listener para o mesmo evento
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Remove a inscrição de um escutador específico."""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)


    def publish(self, event_type: str, payload: Any = None) -> None:
        """Dispara um evento para todos os subscritores registados naquele tópico."""
        if event_type in self._listeners:
            # Fazemos uma cópia da lista para evitar erros se alguém se desinscrever durante o loop
            for callback in self._listeners[event_type][:]:
                try:
                    callback(payload)
                except Exception as e:
                    # Logs de salvaguarda para evitar que um erro na UI trave o loop interno da Engine
                    print(
                        f"[EventBus Error] Falha ao processar evento '{event_type}': {e}")