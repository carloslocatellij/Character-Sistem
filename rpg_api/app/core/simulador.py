import random
from copy import deepcopy
from typing import List, Dict, Any, Tuple
from app.core.personagens import Personagem

# ==========================================
# DOMÍNIO: SIMULADOR DE COMBATE
# ==========================================

class SimuladorCombate:
    """Gere as simulações de batalhas em grupo e recolhe estatísticas."""
    
    def __init__(self, equipa_aliada: List[Personagem], equipa_oponente: List[Personagem]):
        self.equipa_aliada_base = equipa_aliada
        self.equipa_oponente_base = equipa_oponente

    def _rolar_iniciativa(self, combatentes: List[Personagem]) -> Tuple[List[Personagem], List[Dict]]:
        """Calcula a ordem de combate baseada em 1d6 + Agilidade."""
        iniciativas = []
        for p in combatentes:
            rolagem = p._rolar_d6(1) + p.atributos_totais["agilidade"]
            iniciativas.append({
                "personagem": p,
                "resultado": rolagem,
                "agilidade": p.atributos_totais["agilidade"],
                "rolagem": rolagem - p.atributos_totais["agilidade"],  # a rolagem pura
                "desempate": random.random() # Evita empates absolutos
            })
            
        # Ordena: Maior Resultado -> Maior Agilidade -> Desempate aleatório
        iniciativas.sort(key=lambda x: (x["resultado"], x["agilidade"], x["desempate"]), reverse=True)
        ordem = [item["personagem"] for item in iniciativas]
        detalhes_iniciativa = [{"nome": item["personagem"].nome, "rolagem": item["rolagem"], "agilidade": item["agilidade"], "total": item["resultado"]} for item in iniciativas]
        return ordem, detalhes_iniciativa

    def _obter_vivos(self, equipa: List[Personagem]) -> List[Personagem]:
        """Filtra apenas os combatentes que ainda têm Pontos de Vida."""
        return [p for p in equipa if p.pv_atual > 0]

    def simular_batalha(self, silencioso: bool = True) -> Dict[str, Any]:
        """
        Executa uma única batalha até uma equipa ser derrotada.
        Devolve um relatório de tudo o que aconteceu.
        """
        # Fazemos cópias frescas dos personagens para não alterar os originais
        aliados = deepcopy(self.equipa_aliada_base)
        oponentes = deepcopy(self.equipa_oponente_base)
        
        ordem_turnos, detalhes_iniciativa = self._rolar_iniciativa(aliados + oponentes)
        
        # Dicionário para guardar estatísticas desta partida
        estatisticas = {p.nome: {"dano_causado": 0, "abates": 0, "tentativas": 0, "acertos": 0} for p in ordem_turnos}
        vencedor = None
        rodada = 0
        
        if not silencioso:
            print("========================================\n🎲 ROLAGEM DE INICIATIVA 🎲\n========================================")
            for det in detalhes_iniciativa:
                print(f"⏩ {det['nome']} rolou {det['rolagem']} de iniciativa.")
            print()
        
        while True:
            rodada += 1
            if not silencioso:
                print(f"=============== RODADA {rodada} ===============")
            
            for atacante in ordem_turnos:
                if atacante.pv_atual <= 0:
                    continue # Mortos não atacam
                    
                aliados_vivos = self._obter_vivos(aliados)
                oponentes_vivos = self._obter_vivos(oponentes)
                
                # Verificação de Vitória
                if not aliados_vivos:
                    vencedor = "Oponentes"
                    break
                if not oponentes_vivos:
                    vencedor = "Aliados"
                    break
                    
                # Escolher alvo aleatório (se for aliado ataca oponente, e vice-versa)
                is_aliado = any(a.nome == atacante.nome for a in aliados)
                inimigos = oponentes_vivos if is_aliado else aliados_vivos
                alvo = random.choice(inimigos)
                
                # Executar ataque
                resultado = atacante.atacar(alvo)
                
                # Recolher Dados para a Estatística
                estatisticas[atacante.nome]["tentativas"] += 1
                if resultado["acertou"]:
                    estatisticas[atacante.nome]["acertos"] += 1
                    estatisticas[atacante.nome]["dano_causado"] += resultado["dano_causado"]
                    if resultado.get("alvo_morreu", False):
                        estatisticas[atacante.nome]["abates"] += 1
                        
                
                if not silencioso:
                    print(f"⚔️ {atacante.nome} ataca {alvo.nome} com {resultado['arma_nome']}!")
                    print(f"   Ataque: {resultado['ataque_total']} vs Defesa: {resultado['defesa_alvo']}")
                    if resultado["acertou"]:
                        print("   💫 Acertou o golpe!")
                        print(f"   🛡️ {alvo.nome} tentou absorver! Bloqueou {resultado['defesa_total']} ({resultado['absorcao_dados']} Resistência, {resultado['bonus_armadura']} Armadura).")
                        print(f"   💥 {alvo.nome} sofreu {resultado['dano_causado']} de dano! PV restante: {resultado['pv_restante']:.1f}")
                        if resultado.get("alvo_morreu", False) and not silencioso: print(f"💀 {atacante.nome} eliminou {alvo.nome}!")
                    else:
                        print("   🔴 O ataque falhou ou foi esquivado!")
                    print("----------------------------------------")
                
                # Processar efeitos no fim do turno
                atacante.finalizar_turno()
                
            if vencedor:
                break
                
        if not silencioso:
            print(f"\n🏆 FIM DE COMBATE! Vencedor: {vencedor}\n")
            print("📊 ESTATÍSTICAS DA BATALHA:")
            if len(estatisticas) > 0:
                for nome, stats in estatisticas.items():
                    print(f" - {nome}: {stats['dano_causado']} Dano, {stats['abates']} Abates")
            
        return {"vencedor": vencedor, "estatisticas": estatisticas, "sobreviventes": self._obter_vivos(aliados + oponentes)}

    def simular_multiplas_batalhas(self, num_simulacoes: int = 100) -> Dict[str, Any]:
        """Corre X batalhas em silêncio e agrupa todas as estatísticas num mega relatório."""
        vitorias_aliados = 0
        vitorias_oponentes = 0
        
        # Cria a base das estatísticas totais
        todos_personagens = self.equipa_aliada_base + self.equipa_oponente_base
        stats_totais = {
            p.nome: {"dano_total": 0, "abates": 0, "tentativas": 0, "acertos": 0, "sobreviveu": 0} 
            for p in todos_personagens
        }
        
        for _ in range(num_simulacoes):
            relatorio = self.simular_batalha(silencioso=True)
            
            if relatorio["vencedor"] == "Aliados":
                vitorias_aliados += 1
            else:
                vitorias_oponentes += 1
                
            # Somar resultados parciais ao total
            if len(relatorio.get("estatisticas")) > 0:
                for nome, stats in relatorio["estatisticas"].items():
                    stats_totais[nome]["dano_total"] += stats["dano_causado"]
                    stats_totais[nome]["abates"] += stats["abates"]
                    stats_totais[nome]["tentativas"] += stats["tentativas"]
                    stats_totais[nome]["acertos"] += stats["acertos"]
                    
                # Contar quem ficou de pé
                for sobrevivente in relatorio["sobreviventes"]:
                    stats_totais[sobrevivente.nome]["sobreviveu"] += 1
                
        return {
            "num_simulacoes": num_simulacoes,
            "vitorias_aliados": vitorias_aliados,
            "vitorias_oponentes": vitorias_oponentes,
            "detalhes": stats_totais
        }