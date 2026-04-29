from app.core.personagens import Personagem, Raca, ClasseRPG
from app.core.equipamentos import Arma
from app.core.simulador import SimuladorCombate

def criar_lutadores():
    """Função utilitária para gerar lutadores para o teste."""
    raca = Raca("Humano")
    classe = ClasseRPG("warrior")
    
    # Herói muito forte
    heroi = Personagem("Aragorn", 1, raca, classe, 5, 5, 5, 2, 2)
    heroi.mao_direita = Arma("Espada Épica", dano=10, tipo="corpo")
    
    # Vilão muito fraco
    vilao = Personagem("Goblin Fraco", 1, raca, classe, 1, 1, 1, 1, 1)
    vilao.mao_direita = Arma("Faca", dano=1, tipo="corpo")
    
    return [heroi], [vilao]

def test_simulacao_unica(monkeypatch):
    """Testa se uma batalha decorre corretamente e se o vencedor é identificado."""
    aliados, oponentes = criar_lutadores()
    
    # Forçar o dado a dar sempre 6 para testar sem surpresas
    monkeypatch.setattr(Personagem, "_rolar_d6", lambda self, qtd: qtd * 6)
    
    simulador = SimuladorCombate(aliados, oponentes)
    relatorio = simulador.simular_batalha(silencioso=True)
    
    # Aragorn é muito mais forte, deve vencer na primeira ronda
    assert relatorio["vencedor"] == "Aliados"
    assert relatorio["estatisticas"]["Aragorn"]["acertos"] > 0
    assert relatorio["estatisticas"]["Aragorn"]["abates"] == 1
    assert relatorio["estatisticas"]["Goblin Fraco"]["abates"] == 0

def test_multiplas_simulacoes(monkeypatch):
    """Garante que a recolha estatística após 10 batalhas soma os valores corretamente."""
    aliados, oponentes = criar_lutadores()
    
    # Forçar o dado a dar sempre 6
    monkeypatch.setattr(Personagem, "_rolar_d6", lambda self, qtd: qtd * 6)
    
    simulador = SimuladorCombate(aliados, oponentes)
    # Correr apenas 10 simulações para o teste ser rápido
    relatorio = simulador.simular_multiplas_batalhas(num_simulacoes=10)
    
    assert relatorio["num_simulacoes"] == 10
    assert relatorio["vitorias_aliados"] == 10 # O herói forte deve ganhar todas
    assert relatorio["vitorias_oponentes"] == 0
    
    # Verifica a sobrevivência
    detalhes = relatorio["detalhes"]
    assert detalhes["Aragorn"]["sobreviveu"] == 10
    assert detalhes["Goblin Fraco"]["sobreviveu"] == 0