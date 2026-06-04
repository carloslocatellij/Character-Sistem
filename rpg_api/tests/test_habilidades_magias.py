import pytest # Necessário para testar exceções
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.entities.habilidades_magias import Efeito, Magia, Habilidade

def criar_cobaia():
    raca = Raca("Humano")
    classe = ClasseRPG("Guerreiro")
    return Personagem("Cobaia", 1, raca, classe, 2, 2, 2, 2, 3) # Exuberância = 3

def test_aprender_magia_com_excecao():
    raca = Raca("Humano")
    # Este mago ganha +1 em Fogo, mas +0 em Água
    classe = ClasseRPG("Mago Aprendiz", bonus_caminhos={"fogo": 1})
    
    # Exuberância inicial = 2
    mago = Personagem("Harry", 1, raca, classe, 1, 1, 1, 1, exub_base=2)
    
    # Magia 1: Fácil (Exige Exub 1 e Fogo 1)
    magia_fogo = Magia("Chama Menor", custo_pm=2, requisito_caminhos={"fogo": 1}, requisito_exuberancia=1)
    
    # Magia 2: Impossível (Exige Água 2)
    magia_agua = Magia("Tsunami", custo_pm=10, requisito_caminhos={"água": 2}, requisito_exuberancia=2)

    # Teste de Sucesso
    mago.aprender_magia(magia_fogo)
    assert len(mago.magias_conhecidas) == 1
    
    # Teste de Falha (Deve levantar a Exceção ValueError)
    with pytest.raises(ValueError) as erro:
        mago.aprender_magia(magia_agua)
    
    assert "não atende aos requisitos" in str(erro.value)
    assert len(mago.magias_conhecidas) == 1 # Não adicionou a segunda magia

def test_efeito_dano_continuo():
    alvo = criar_cobaia()
    alvo.pv_atual = 20
    
    veneno = Efeito(nome="Veneno", duracao_turnos=2, tipo="dano_continuo", valor=3)
    alvo.aplicar_efeito(veneno)
    
    assert len(alvo.efeitos_ativos) == 1
    
    # Simula Fim do Turn 1
    relatorio1 = alvo.finalizar_turno()
    assert alvo.pv_atual == 17 # Sofreu 3 de dano direto
    assert len(alvo.efeitos_ativos) == 1 # Efeito continua (1 turno restante)
    
    # Simula Fim do Turn 2
    relatorio2 = alvo.finalizar_turno()
    assert alvo.pv_atual == 14
    assert len(alvo.efeitos_ativos) == 0 # Veneno acabou

def test_efeito_buff_atributo():
    heroi = criar_cobaia()
    forca_original = heroi.atributos_totais["forca"]
    mod_ataque_original = heroi.mod_atq_corpo
    
    furia = Efeito(nome="Fúria", duracao_turnos=1, tipo="buff_atributo", valor=2, atributo_alvo="forca")
    heroi.aplicar_efeito(furia)
    
    # Garante que aplicou na hora
    assert heroi.atributos_totais["forca"] == forca_original + 2
    assert heroi.mod_atq_corpo > mod_ataque_original # O modificador automático subiu!
    
    # Passa 1 turno, efeito acaba e volta ao normal
    heroi.finalizar_turno()
    assert heroi.atributos_totais["forca"] == forca_original

def test_lancamento_de_magia(monkeypatch):
    mago = criar_cobaia()
    alvo = criar_cobaia()
    mago.pm_atual = 10
    
    # Magia de Fogo que dá 5 de dano e aplica Queimadura (1 de dano por 2 turnos)
    queimadura = Efeito("Chamas", 2, "dano_continuo", 1)
    bola_de_fogo = Magia("Bola de Fogo", custo_pm=4, dano_base=5, efeito_aplicado=queimadura, requisito_exuberancia=2)
    
    # Congela rolagem para sempre acertar (Atacante tira alto, alvo tira baixo)
    monkeypatch.setattr(mago, "_rolar_d6", lambda qtd: qtd * 6)
    monkeypatch.setattr(alvo, "_rolar_d6", lambda qtd: qtd * 1)
    
    resultado = mago.lancar_magia(bola_de_fogo, alvo)
    
    assert resultado["sucesso"] is True
    assert mago.pm_atual == 6 # Gastou 4
    assert resultado["dano_causado"] > 0
    assert len(alvo.efeitos_ativos) == 1
    assert alvo.efeitos_ativos[0].nome == "Chamas"