import pytest
import esper

def test_deve_inscrever_e_notificar_subscritores():
    # 1. SETUP
    resultado_evento = {"recebido": False, "dados": None}

    def escutador_de_teste(payload):
        resultado_evento["recebido"] = True
        resultado_evento["dados"] = payload

    # Inscreve o escutador no tópico "MENSAGEM_ALERTA"
    esper.set_handler("MENSAGEM_ALERTA", escutador_de_teste)

    # 2. AÇÃO
    # Publica um payload no tópico específico
    esper.dispatch_event("MENSAGEM_ALERTA", {
                         "texto": "Um monstro aproximou-se!"})

    # 3. VALIDAÇÃO
    assert resultado_evento["recebido"] is True
    assert resultado_evento["dados"]["texto"] == "Um monstro aproximou-se!"


def test_nao_deve_notificar_topicos_diferentes():
    # 1. SETUP
    resultado_evento = {"recebido": False}

    def escutador_de_teste(payload):
        resultado_evento["recebido"] = True

    esper.set_handler("DIALOGO_NPC", escutador_de_teste)

    # 2. AÇÃO: Publica num tópico completamente diferente
    esper.dispatch_event("MOVIMENTO_JOGADOR", {"x": 5, "y": 10})

    # 3. VALIDAÇÃO: O escutador de DIALOGO_NPC não pode ter sido ativado
    assert resultado_evento["recebido"] is False
