# Regra 5: Regras e Fórmulas de Combate

Esta regra estabelece as fórmulas matemáticas de cálculo de status e o fluxo mecânico do combate do RPG de mesa.

## 1. Atributos Principais

O personagem possui 5 atributos básicos (escala inicial de 0 a 3, podendo evoluir até 5 ou mais):
- **Agilidade:** Precisão, velocidade, esquiva, iniciativa.
- **Força:** Carga, dano físico corpo-a-corpo.
- **Resistência:** Saúde, redução de dano físico/mágico, HP máximo.
- **Percepção:** Sentidos, instintos, lógica, detecção.
- **Exuberância:** Magnetismo, potencial mágico, MP máximo.

---

## 2. Fórmulas de Status Derivados

Sempre arredonde os valores de HP e Mana para **cima**, e os valores de modificadores de ataque/defesa para **baixo**.

1. **Pontos de Vida Máximos (HP Máx):**
   $$HP = 7 + \left\lceil \frac{\text{Nível} \times (\text{Resistência} + 2)}{2} \right\rceil + (\text{Nível} + \text{Resistência}) \times 3$$

2. **Modificador de Ataque Corpo-a-Corpo:**
   $$\text{Mod. Ataque CC} = \text{Nível} \times \left( \text{Força} + \left\lceil \frac{\text{Agilidade}}{2} \right\rceil \right)$$

3. **Modificador de Ataque à Distância:**
   $$\text{Mod. Ataque Dist} = \text{Nível} \times \left( \text{Agilidade} + \left\lceil \frac{\text{Força}}{2} \right\rceil \right)$$

---

## 3. Mecânica de Teste de Ataque e Defesa

- **Iniciativa (Ordem dos Turnos):** Rola-se $1d6 + \text{Agilidade}$. Desempates usam a maior Agilidade base; se persistir, decide-se via cara ou coroa/par ou ímpar determinístico.
- **Rolagem de Ataque:** 
  - Rola-se $3d6$ básico.
  - Para cada 3 pontos no atributo chave (Força para Corpo-a-Corpo; Agilidade para Distância), adiciona-se $+1d6$ na rolagem (arredondado para baixo):
    $$\text{Dados Rolados} = 3d6 + \left( \left\lfloor \frac{\text{Atributo}}{3} \right\rfloor \times 1d6 \right)$$
  - **Ataque Total =** Somatório dos dados rolados + Modificador de Ataque correspondente.
- **Rolagem de Defesa / Esquiva:**
  - Rola-se $2d6$ básico.
  - Para cada 2 pontos de Agilidade, adiciona-se $+1d6$ (arredondado para baixo).
  - **Defesa Total =** Dados rolados + $(\text{Bônus de Escudo} + 1) \times \text{Agilidade}$.
- **Resolução de Acerto:** O ataque acerta se o Ataque Total for **maior** que a Defesa Total do alvo. Empates favorecem a Defesa.

---

## 4. Cálculo de Dano e Absorção

- **Dano Bruto Causado:**
  $$\text{Dano Bruto} = (\text{Atributo Chave}) \times 1d6 + \text{Dano da Arma}$$
  *(Atributo Chave: Força para CC; Agilidade para Distância)*
- **Absorção de Dano:**
  $$\text{Dano Absorvido} = \text{Resistência} \times 1d6 + \text{Defesa da Armadura}$$
- **Dano Líquido Recebido:**
  $$\text{Dano Sofrido} = \max(0, \text{Dano Bruto} - \text{Dano Absorvido})$$
  *(Este valor é subtraído diretamente dos Pontos de Vida atuais do alvo).*

---

## 5. Simulação de Combate (Isolamento de Arena)

- **Simulador de Batalha:** Aceita dois times de personagens e processa turnos alternados de combate baseado em iniciativa até que uma equipe inteira caia.
- **Uso Estrito de Deepcopy:** Antes de iniciar qualquer simulação (especialmente simulações estatísticas em loop, ex: 100 rodadas), o simulador deve realizar obrigatoriamente um `deepcopy` de todas as instâncias de personagens originais. Isso garante que cada simulação inicie com HP e MP máximos e limpos de ferimentos ou efeitos acumulados do combate anterior.
