# Regra 5: Regras/Fórmulas Combate

Fórmulas status e fluxo combate RPG mesa.

## 1. Atributos Principais

5 atributos básicos (0-3+, evolui 5+):
- **Agilidade:** Precisão, velocidade, esquiva, iniciativa.
- **Força:** Carga, dano físico CC.
- **Resistência:** Saúde, redução dano, HP máx.
- **Percepção:** Sentidos, instintos, lógica, detecção.
- **Exuberância:** Magnetismo, potencial mágico, MP máx.

---

## 2. Fórmulas Status Derivados

Arredonde HP/Mana para **cima**, mods ataque/defesa para **baixo**.

1. **HP Máx:**
   $$HP = 7 + \left\lceil \frac{\text{Nível} \times (\text{Resistência} + 2)}{2} \right\rceil + (\text{Nível} + \text{Resistência}) \times 3$$

2. **Mod. Ataque CC:**
   $$\text{Mod. Ataque CC} = \text{Nível} \times \left( \text{Força} + \left\lceil \frac{\text{Agilidade}}{2} \right\rceil \right)$$

3. **Mod. Ataque Dist:**
   $$\text{Mod. Ataque Dist} = \text{Nível} \times \left( \text{Agilidade} + \left\lceil \frac{\text{Força}}{2} \right\rceil \right)$$

---

## 3. Teste Ataque/Defesa

- **Iniciativa:** $1d6 + \text{Agilidade}$. Desempate: Agilidade, depois cara/coroa determinístico.
- **Rolagem Ataque:**
  - $3d6$ básico.
  - Atributo chave (Força CC / Agilidade Dist) a cada 3 pts: $+1d6$ (arred. baixo):
    $$\text{Dados Rolados} = 3d6 + \left( \left\lfloor \frac{\text{Atributo}}{3} \right\rfloor \times 1d6 \right)$$
  - **Ataque Total:** Dados + Modificador.
- **Rolagem Defesa/Esquiva:**
  - $2d6$ básico.
  - Agilidade a cada 2 pts: $+1d6$ (arred. baixo).
  - **Defesa Total:** Dados + $(\text{Bônus de Escudo} + 1) \times \text{Agilidade}$.
- **Acerto:** Ataque > Defesa (Empate favorece Defesa).

---

## 4. Dano/Absorção

- **Dano Bruto:** $(\text{Atributo Chave}) \times 1d6 + \text{Dano Arma}$ (Chave: Força CC / Agilidade Dist).
- **Absorção:** $\text{Resistência} \times 1d6 + \text{Defesa Armadura}$.
- **Dano Líquido:** $\max(0, \text{Dano Bruto} - \text{Dano Absorvido})$ (subtrai HP alvo).

---

## 5. Simulação (Isolamento Arena)

- **Simulador:** Processa turnos alternados entre 2 times baseados iniciativa até um cair.
- **Deepcopy:** Antes simular (ex: 100 rodadas), simulador deve dar `deepcopy` total das instâncias personagens. Garante simulação inicia com HP/MP máx, sem efeitos acumulados anteriores.
