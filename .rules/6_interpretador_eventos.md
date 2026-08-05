# Regra 6: Interpretador Eventos (EventSystem)

Eventos mapa (NPCs, portas, etc.) seguem modelo flexível (páginas condicionais + comandos JSON).

## 1. Pipeline Execução

1. **Filtro Página (Loop Decrescente):**
   - Evalua páginas de trás para frente (maior `id_pagina` -> menor).
   - Primeira página com **todas condições atendidas** executa.
   - Condições: `switches` globais, `variaveis`, `self_switch` (A, B, C, D), itens inventário.

2. **Validação Gatilho (Trigger):**
   - Verifica casamento gatilho com estímulo físico:
     - `acao_jogador` (Enter virado).
     - `toque_jogador` (anda sobre).
     - `toque_evento` (evento encosta).
     - `processo_paralelo` (fundo, não trava).
     - `processo_automatico` (trava mov, roda imediato).

3. **Interpretação/Loop Comandos:**
   - Lista comandos página em `pilha_de_comandos`.
   - Execução sequencial.

---

## 2. Pilha Não-Bloqueante

- **Proibido loops bloqueantes/espera:** Congela TUI Textual, causa colisão.
- **Pausa/Interrupção:**
  - Comando exige input (diálogo/escolha): renderiza escolhas, registra caminhos, ativa `aguardando_escolha = True`, **interrompe loop**, devolve controle para Textual.
- **Retomada:**
  - Jogador escolhe: UI invoca `avancar_ramo_evento(opcao_escolhida)`.
  - Limpa `aguardando_escolha = False`, empilha sub-ramo comandos, reativa loop pilha.
