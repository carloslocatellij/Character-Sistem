# Regra 6: Interpretador de Eventos (EventSystem)

Os eventos de mapa (NPCs, portas, baús, armadilhas, processos paralelos) seguem um modelo flexível baseado em páginas condicionais e comandos lineares estruturados em formato JSON, similar ao padrão RPG Maker.

## 1. Pipeline de Execução de Eventos

Quando uma interação ocorre (jogador aciona "Enter" ou anda sobre o evento), o interpretador deve executar as seguintes etapas:

1. **Filtro de Página (Loop Decrescente):**
   - Um evento possui uma lista de páginas (`paginas`).
   - O interpretador avalia as páginas de trás para frente (da maior `id_pagina` para a menor).
   - A primeira página que tiver **todas as suas condições atendidas** é a selecionada para execução.
   - Condições podem checar: `switches` globais, `variaveis` de estado do jogo, interruptor local (`self_switch` A, B, C, D) e itens requeridos no inventário.

2. **Validação de Gatilho (Trigger):**
   - Verifica se o gatilho da página casa com o estímulo físico ocorrido:
     - `enter` / `acao_jogador`: Jogador pressiona Enter virado para o evento.
     - `toque_jogador` / `andar_sobre`: Jogador anda sobre o bloco do evento.
     - `toque_evento`: O evento móvel encosta no jogador.
     - `processo_paralelo`: Roda continuamente em segundo plano sem travar a interface.
     - `processo_automatico`: Trava a movimentação e roda sozinho imediatamente ao carregar.

3. **Interpretação e Loop de Comandos:**
   - A lista de comandos da página selecionada é empilhada em uma pilha de execução linear (`pilha_de_comandos`).
   - Os comandos são executados de forma sequencial de cima para baixo.

---

## 2. Pilha de Comandos Não-Bloqueante e Interrupção

- **O Problema de Loops Síncronos:** O interpretador **não** deve rodar loops de bloqueio de CPU ou chamadas síncronas de espera, pois isso congela a interface TUI do Textual e causa colisões de concorrência.
- **Mecanismo de Pausa/Interrupção:**
  - Quando um comando exige input do usuário (como uma mensagem de diálogo com escolhas ou bifurcação condicional):
    1. O interpretador renderiza as opções visuais na tela.
    2. Registra os caminhos possíveis no estado interno.
    3. Ativa a flag `aguardando_escolha = True`.
    4. **Interrompe imediatamente o loop de comandos**, devolvendo o controle da CPU para a TUI do Textual.
- **Retomada de Fluxo:**
  - Quando o jogador responde ao diálogo (submetendo sua escolha na `ChoiceBox` ou prompt), a UI invoca o método do motor `avancar_ramo_evento(opcao_escolhida)`.
  - Este método limpa o bloqueio (`aguardando_escolha = False`), empilha as ações do sub-ramo de comandos correspondente à escolha no topo da pilha, e reativa o loop de execução da pilha.
