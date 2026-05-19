import pytest
# Vamos importar o nosso futuro motor (que criaremos no próximo passo)
from app.core.motor_jogo import MotorRPG 

# Matriz de teste (3x3)
# 🔲 = Parede (Bloqueia)
# 🟫 = Chão (Livre)
MAPA_TESTE_MATRIZ = [
    ["🔲", "🔲", "🔲"],
    ["🔲", "🟫", "🟫"],
    ["🔲", "🟫", "🔲"]
]


@pytest.fixture
def motor_simples():
    """Cria um motor com jogador no (1, 1), um baú à direita e uma porta acima."""
    objetos_teste = {
        (1, 2): "📦", # Baú à direita do jogador
        (0, 1): "🚪"  # Porta acima do jogador
    }
    return MotorRPG(
        matriz_base=MAPA_TESTE_MATRIZ,
        dict_objetos={},
        dict_eventos={},
        posicao_inicial=(1, 1)
    )

@pytest.fixture
def motor_com_eventos():
    """Cria o motor com a separação correta entre Cenário e Eventos."""
    
    # 1. Camada de Objetos Visuais (Cenário)
    objetos_cenario = {
        (1, 2): "🪑"  # Cadeira à direita do jogador (linha 1, coluna 2)
    }
    
    # 2. Camada de Eventos Lógicos (Baseado no eventos_db.py)
    eventos_logicos = {
        (0, 1): { # Acima do jogador (linha 0, coluna 1)
            "id": 1,
            "nome": "Baú Escondido",
            "emoji": "📦",
            "tipo_evento": "bau",
            "parametros": {"item": "Espada Longa", "quantidade": 1}
        }
    }
    
    return MotorRPG(
        matriz_base=MAPA_TESTE_MATRIZ,
        dict_objetos=objetos_cenario,
        dict_eventos=eventos_logicos, # Injetamos a nova camada!
        posicao_inicial=(1, 1)
    )

def test_movimento_livre(motor_simples):
    """Garante que o jogador consegue mover-se para um chão vazio."""
    # Move para a direita (linha + 0, coluna + 1)
    sucesso = motor_simples.mover_personagem(d_linha=0, d_coluna=1)
    
    assert sucesso is True
    assert motor_simples.pos_jogador == (1, 2)
    assert motor_simples.direcao_olhar == "direita"
    

def test_colisao_com_parede(motor_simples):
    """Garante que o jogador NÃO atravessa paredes."""
    # Tenta mover para a esquerda (linha + 0, coluna - 1) que é uma parede 🔲
    sucesso = motor_simples.mover_personagem(d_linha=0, d_coluna=-1)
    
    assert sucesso is False
    assert motor_simples.pos_jogador == (1, 1) # Continua no mesmo lugar
    assert motor_simples.direcao_olhar == "esquerda" # Mas virou o rosto para a parede!

def test_limites_do_mapa(motor_simples):
    """Garante que o jogador não cai fora do mapa (IndexError)."""
    motor_simples.pos_jogador = (2, 1) # Coloca o jogador no limite inferior
    
    # Tenta descer mais um passo (linha + 1)
    sucesso = motor_simples.mover_personagem(d_linha=1, d_coluna=0)
    
    assert sucesso is False
    assert motor_simples.pos_jogador == (2, 1)
    
    
def test_interacao_com_objeto_cenario_falha(motor_com_eventos):
    """Garante que apertar Enter de frente para cenário (cadeira) não faz nada."""
    motor_com_eventos.direcao_olhar = "direita" # Vira para a Cadeira
    
    evento = motor_com_eventos.interagir()
    
    assert evento is None # O motor ignora a cadeira, pois não é um evento!
    

def test_colisao_com_cenario_e_eventos(motor_com_eventos):
    """Garante que tanto objetos quanto eventos bloqueiam a passagem do jogador."""
    # Tenta andar para a direita (bater na cadeira)
    assert motor_com_eventos.mover_personagem(0, 1) is False
    
    # Tenta andar para cima (bater no baú)
    assert motor_com_eventos.mover_personagem(-1, 0) is False