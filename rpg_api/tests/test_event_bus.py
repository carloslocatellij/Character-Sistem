# rpg_api/tests/test_event_bus.py
import pytest
from app.core.engine.event_bus import EventBus


def test_deve_inscrever_e_notificar_subscritores():
    # 1. SETUP
    bus = EventBus()
    resultado_evento = {"recebido": False, "dados": None}

    def escutador_de_teste(payload):
        resultado_evento["recebido"] = True
        resultado_evento["dados"] = payload

    # Inscreve o escutador no tópico "MENSAGEM_ALERTA"
    bus.subscribe("MENSAGEM_ALERTA", escutador_de_teste)

    # 2. AÇÃO
    # Publica um payload no tópico específico
    bus.publish("MENSAGEM_ALERTA", {"texto": "Um monstro aproximou-se!"})

    # 3. VALIDAÇÃO
    assert resultado_evento["recebido"] is True
    assert resultado_evento["dados"]["texto"] == "Um monstro aproximou-se!"


def test_nao_deve_notificar_topicos_diferentes():
    # 1. SETUP
    bus = EventBus()
    resultado_evento = {"recebido": False}

    def escutador_de_teste(payload):
        resultado_evento["recebido"] = True

    bus.subscribe("DIALOGO_NPC", escutador_de_teste)

    # 2. AÇÃO: Publica num tópico completamente diferente
    bus.publish("MOVIMENTO_JOGADOR", {"x": 5, "y": 10})

    # 3. VALIDAÇÃO: O escutador de DIALOGO_NPC não pode ter sido ativado
    assert resultado_evento["recebido"] is False

# import pytest
# from app.core.engine.event_bus import EventBus

# def test_event_bus_assinatura_e_emissao():
#     """Garante que um ouvinte recebe os dados corretos quando um evento é emitido."""
#     bus = EventBus()
    
#     # Variável externa para capturar o que o callback recebe
#     mensagens_recebidas = []
    
#     # 1. Definimos o 'Ouvinte' (Callback)
#     def ao_abrir_bau(dados_evento):
#         mensagens_recebidas.append(dados_evento)

#     # 2. O Ouvinte assina o canal "bau"
#     bus.subscribe("bau", ao_abrir_bau)
    
#     # 3. A Engine (em outro lugar) emite o evento
#     bus.emit("bau", {"item": "Poção de Vida", "quantidade": 2})
    
#     # Verificações
#     assert len(mensagens_recebidas) == 1
#     assert mensagens_recebidas[0]["item"] == "Poção de Vida"
#     assert mensagens_recebidas[0]["quantidade"] == 2

# def test_event_bus_multiplos_ouvintes():
#     """Garante que múltiplos sistemas podem ouvir o mesmo evento."""
#     bus = EventBus()
#     contador = {"audio": 0, "ui": 0}
    
#     def tocar_som(dados): contador["audio"] += 1
#     def mostrar_texto(dados): contador["ui"] += 1
        
#     bus.subscribe("dano_sofrido", tocar_som)
#     bus.subscribe("dano_sofrido", mostrar_texto)
    
#     bus.emit("dano_sofrido", {"valor": 10})
    
#     assert contador["audio"] == 1
#     assert contador["ui"] == 1