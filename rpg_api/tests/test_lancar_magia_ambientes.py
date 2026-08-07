import pytest
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.entities.habilidades_magias import Magia, Efeito

def criar_cobaia(nome="Herói"):
    raca = Raca("Humano")
    classe = ClasseRPG("Mago", bonus_caminhos={"fogo": 2, "luz": 2})
    p = Personagem(nome, 1, raca, classe, 2, 2, 2, 2, exub_base=3)
    p.reset_status()
    return p

def test_lancar_magia_fora_combate_cura_e_pm():
    heroi = criar_cobaia()
    heroi.pv_atual = 5 # Ferido
    heroi.pm_atual = 10

    magia_cura = Magia(
        nome="Luz Curativa",
        custo_pm=3,
        requisito_caminhos={"luz": 1},
        cura_base=8,
        tipo_execucao="fora_combate"
    )

    resultado = heroi.lancar_magia_fora_combate(magia_cura, heroi)

    assert resultado["sucesso"] is True
    assert heroi.pm_atual == 7 # Gastou 3 PM
    assert heroi.pv_atual > 5 # Curou HP
    assert resultado["cura_realizada"] > 0

def test_bloqueio_magia_fora_combate_se_for_exclusiva_de_combate():
    heroi = criar_cobaia()
    heroi.pm_atual = 10

    magia_combate = Magia(
        nome="Explosão Arcana",
        custo_pm=4,
        requisito_caminhos={"fogo": 2},
        dano_base=10,
        tipo_execucao="combate"
    )

    resultado = heroi.lancar_magia_fora_combate(magia_combate, heroi)

    assert resultado["sucesso"] is False
    assert "só pode ser lançada em combate" in resultado["motivo"]
    assert heroi.pm_atual == 10 # Não gastou PM

def test_lancar_magia_combate_com_efeito(monkeypatch):
    atacante = criar_cobaia("Mago")
    alvo = criar_cobaia("Inimigo")
    atacante.pm_atual = 10

    monkeypatch.setattr(atacante, "_rolar_d6", lambda qtd: qtd * 6)
    monkeypatch.setattr(alvo, "_rolar_d6", lambda qtd: qtd * 1)

    queimadura = Efeito("Queimadura", duracao_turnos=2, tipo="dano_continuo", valor=3)
    magia_fogo = Magia(
        nome="Chama do Inferno",
        custo_pm=4,
        requisito_caminhos={"fogo": 2},
        dano_base=5,
        tipo_execucao="combate",
        efeito_aplicado=queimadura
    )

    resultado = atacante.lancar_magia(magia_fogo, alvo)

    assert resultado["sucesso"] is True
    assert atacante.pm_atual == 6
    assert len(alvo.efeitos_ativos) == 1
    assert alvo.efeitos_ativos[0].nome == "Queimadura"
