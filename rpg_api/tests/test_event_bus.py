import pytest
from app.core.engine.event_bus import EventBus

def test_event_bus_assinatura_e_emissao():
    """Garante que um ouvinte recebe os dados corretos quando um evento é emitido."""
    bus = EventBus()
    
    # Variável externa para capturar o que o callback recebe
    mensagens_recebidas = []
    
    # 1. Definimos o 'Ouvinte' (Callback)
    def ao_abrir_bau(dados_evento):
        mensagens_recebidas.append(dados_evento)

    # 2. O Ouvinte assina o canal "bau"
    bus.subscribe("bau", ao_abrir_bau)
    
    # 3. A Engine (em outro lugar) emite o evento
    bus.emit("bau", {"item": "Poção de Vida", "quantidade": 2})
    
    # Verificações
    assert len(mensagens_recebidas) == 1
    assert mensagens_recebidas[0]["item"] == "Poção de Vida"
    assert mensagens_recebidas[0]["quantidade"] == 2

def test_event_bus_multiplos_ouvintes():
    """Garante que múltiplos sistemas podem ouvir o mesmo evento."""
    bus = EventBus()
    contador = {"audio": 0, "ui": 0}
    
    def tocar_som(dados): contador["audio"] += 1
    def mostrar_texto(dados): contador["ui"] += 1
        
    bus.subscribe("dano_sofrido", tocar_som)
    bus.subscribe("dano_sofrido", mostrar_texto)
    
    bus.emit("dano_sofrido", {"valor": 10})
    
    assert contador["audio"] == 1
    assert contador["ui"] == 1