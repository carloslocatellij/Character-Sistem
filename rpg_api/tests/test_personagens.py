from app.core.entities.personagens import Raca, ClasseRPG, Personagem
from app.core.entities.equipamentos import Arma, Armadura
from app.core.entities.habilidades_magias import Magia

def test_criacao_raca_e_classe():
    """Garante que dicionários e listas vazias sejam tratados corretamente pelas dataclasses."""
    raca_orc = Raca(nome="orco", bonus_atributos={"forca": 2, "agilidade": -1}, emoji="🧟")
    classe_guerreiro = ClasseRPG(nome="warrior", habilidades=["Fúria"])
    
    assert raca_orc.nome == "orco"
    assert raca_orc.bonus_atributos["forca"] == 2
    assert classe_guerreiro.habilidades[0] == "Fúria"

def test_calculo_atributos_totais_personagem():
    """Testa se o Personagem soma corretamente os atributos base + raça + classe."""
    raca_elfo = Raca(nome="elven", bonus_atributos={"agilidade": 2, "percepcao": 1, "exuberancia": 2})
    classe_mago = ClasseRPG(nome="magee")
    
    # Herói com tudo zero na base, para isolar e testar os bônus
    heroi = Personagem(
        nome="Galadriel", nivel=1, raca=raca_elfo, classe_rpg=classe_mago,
        forca_base=0, agilidade_base=0, res_base=0, perc_base=0, exub_base=0
    )
    
    assert heroi.atributos_totais["forca"] == 0
    assert heroi.atributos_totais["agilidade"] == 2
    assert heroi.atributos_totais["percepcao"] == 1
    assert heroi.atributos_totais["exuberancia"] == 2

def test_formulas_status_derivados():
    """Testa a integridade das fórmulas matemáticas de PV e PM do MANUAL.md."""
    raca_humano = Raca(nome="human", bonus_atributos={})
    classe_comum = ClasseRPG(nome="Camponês")
    
    # Nivel 1, Todos atributos = 2
    heroi = Personagem(
        nome="Arthur", nivel=1, raca=raca_humano, classe_rpg=classe_comum,
        forca_base=2, agilidade_base=2, res_base=2, perc_base=2, exub_base=2
    )
    
    #pv = int(7+ (ceil(self.nivel * ceil((res+2) / 2) + ceil((self.nivel + res) *3))))
    assert heroi.pv_max == 18
    assert heroi.pv_atual == 18
    
    # atq = int(self.nivel * ceil(forca + (agi / 2))) deve ser 3)
    assert heroi.mod_atq_corpo == 3

def test_equipamento_inventario():
    """Garante que a agregação com a camada de equipamentos funciona."""
    raca = Raca(nome="human")
    classe = ClasseRPG(nome="warrior")
    heroi = Personagem("Arthur", 1, raca, classe, 2, 2, 2, 2, 2)
    
    espada = Arma(nome="Excalibur", dano=10)
    armadura = Armadura(nome="Placas Metálicas", defesa=5)
    
    heroi.mao_direita = espada
    heroi.armadura = armadura
    
    assert heroi.mao_direita.nome == "Excalibur"
    assert heroi.armadura.defesa == 5
    
    
def test_receber_dano():
    """Testa se o cálculo de dano reduz a vida e se o bloqueio funciona."""
    raca = Raca("human")
    classe = ClasseRPG("warrior")
    
    # Criamos um alvo com PV alto e 0 de resistência para isolar a armadura no teste
    alvo = Personagem("Alvo", 1, raca, classe, 1, 1, 0, 1, 1)
    alvo.pv_atual = 50 
    alvo.armadura = Armadura("Ferro", defesa=5)
    
    # Se ele recebe 10 de dano bruto, a armadura(5) bloqueia 5. Dano real = 5.
    evento = alvo.receber_dano(10)
    
    assert evento["dano_recebido"] == 5
    assert evento["dano_bloqueado"] == 5
    assert alvo.pv_atual == 45 # 50 - 5
    assert evento["morreu"] is False

def test_sistema_de_magia_mana():
    """Testa o gasto de PM ao lançar magias com a nova assinatura de objetos."""
    raca = Raca("elven")
    classe = ClasseRPG("magee")
    mago = Personagem("Gandalf", 1, raca, classe, 1, 1, 1, 3, 4) # Exuberância 3
    alvo = Personagem("orco", 1, raca, classe, 1, 0, 0, 1, 1)
    
    mago.pm_atual = 10
    
    # Criamos os objetos Magia como a nova arquitetura exige
    magia_fogo = Magia(nome="Bola de Fogo", custo_pm=6)
    magia_raio = Magia(nome="Raio", custo_pm=5)
    
    # Teste 1: Sucesso ao lançar magia
    evento = mago.lancar_magia(magia_fogo, alvo)
    assert evento["sucesso"] is True
    assert mago.pm_atual == 4
    
    # Teste 2: Falha por falta de mana (magee só tem 4 PM agora, o Raio custa 5)
    evento_falha = mago.lancar_magia(magia_raio, alvo)
    assert evento_falha["sucesso"] is False
    assert mago.pm_atual == 4 # Mana não foi gasta

def test_ataque_integracao_basica(monkeypatch):
    """Teste de integração entre atacante e alvo. Usa monkeypatch para congelar os dados."""
    raca = Raca("human")
    classe = ClasseRPG("warrior")
    
    atacante = Personagem("Atacante", 1, raca, classe, 2, 2, 2, 2, 2)
    alvo = Personagem("Alvo", 1, raca, classe, 2, 2, 2, 2, 2)
    
    # Equipando o atacante
    atacante.mao_direita = Arma("Espada", dano=5, tipo="corpo")
    
    # Congelamos a rolagem de dados para sempre retornar "3" 
    # (assim o teste não falha aleatoriamente)
    monkeypatch.setattr(atacante, "_rolar_d6", lambda qtd: qtd * 3)
    monkeypatch.setattr(alvo, "_rolar_d6", lambda qtd: qtd * 3)
    
    # O atacante rola 3 dados (3*3 = 9) + Mod(12) = 21
    # O alvo defende com 1 dado (1*3 = 3) + Agi(2) = 5
    # Ataque (21) > Defesa (5) -> Acerta!
    
    resultado = atacante.atacar(alvo)
    
    assert resultado["acertou"] is True
    assert resultado["atacante"] == "Atacante"
    assert "dano_causado" in resultado