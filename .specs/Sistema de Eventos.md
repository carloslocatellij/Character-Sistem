

### Tipos de Eventos Principais

- **Eventos de Mapa:** São aqueles posicionados diretamente na grade do seu mapa. Podem ser personagens, portas, itens escondidos ou eventos invisíveis de tele transporte (mudança de mapa).
- **Eventos Comuns:** Ficam salvos no "Banco de Dados" do jogo. São úteis para criar lógicas que se repetem em vários lugares (como um sistema de descanso na pousada, ou habilidades de batalha que chamam um evento). 

### Estrutura de um Evento

1. **Estados:** Um evento pode ter várias páginas de condições. O jogo sempre lê da maior página para a menor (da página 3 para a página 1). A primeira página que tiver sua condição atendida é a que roda.

2. **Condições:** O que precisa acontecer para aquela página do evento funcionar (ex: ter completado uma _Quest_, ou a variável "X" estar no valor 10).

3. **Acionamento:** Como o jogador interage com ele:
    - _Ação do Jogador:_ Aperta a tecla de confirmação virado para o evento.
    - _Toque do Evento:_ O evento encosta no personagem ou o personagem encosta no evento.
    - _Toque do Jogador:_ Idem ao Toque do Evento, mas para quando o herói anda em cima do evento.
    - _Processo Paralelo:_ Roda em segundo plano infinitamente enquanto a página estiver ativa. Ideal para climas (chuva) ou monitoramento constante (Checar se o HP do jogador chegou a zero).
    - _Processo Automático:_ Trava a tela e roda sozinho. Excelente para cenas de história (Cutscenes).

#### Comandos de Evento Mais Usados

- **Mensagem:** Exibe textos, imagens e rostos de personagens na tela.

- **Controle de Variáveis/Interruptores (Switches):** Usados na memória do jogo para registrar escolhas e progresso do jogador.

- **Bifurcação Condicional (Conditional Branch):** Cria caminhos alternativos no diálogo. _"Se o jogador tiver o item Chave, abra a porta; se não, diga que está trancada"_.

- **Mover Evento:** Controla a movimentação de NPCs ou do herói para criar sequências de animação e cinemáticas. 



# Para transformar o  motor lógico numa ferramenta profissional no estilo RPG Maker, precisamos de migrar o modelo atual de payloads (que mistura estados locais e comandos de forma direta) para uma Arquitetura Homogenea Baseada em Páginas Condicionais e Comandos Lineares Sequenciais.

Na arquitetura clássica de RPGs, um evento não possui propriedades estáticas de "tipo". Em vez disso, ele possui uma Lista de Páginas avaliada de forma decrescente (da maior para a menor). Cada página possui as suas próprias Condições, Gatilhos e uma lista sequencial de Comandos estruturados de forma genérica.

Abaixo está o modelo estendido, padronizado e escalável de payload JSON que o EngineManager e o engine_loader.py devem interpretar na interação.
🌐 O Modelo de Payload Universal Estendido (JSON)

Este payload representa um único evento no banco de dados (parametros). Ele engloba múltiplos casos de uso (Baú reutilizável com Switch Local, NPC com Missão e Bifurcação, Armadilha por Toque, Quebra-Cabeças de Empurrar, e Processos Paralelos).
JSON

{
  "evento_id_base": 42,
  "nome": "Guarda de Riverwood",
  "paginas": [
    {
      "id_pagina": 3,
      "condicoes": {
        "switches": [
          {"nome": "dragao_derrotado", "valor": true}
        ],
        "variaveis": [
          {"nome": "reputacao", "operador": "maior_ou_igual", "valor": 15}
        ],
        "self_switch": "A",
        "item_requerido": null
      },
      "configuracao_visual": {
        "emoji": "🛡️",
        "atravessavel": false,
        "movimento": {
          "direcao": "aleatorio",
          "ciclos": "infinito",
          "frequencia_s": 2.0
        }
      },
      "gatilho": "acao_jogador",
      "comandos": [
        {
          "tipo": "mensagem",
          "dados": {
            "faceset": "guarda_feliz.png",
            "texto": "Saudações, herói de Arton! A cidade estará eternamente grata pelo seu feito."
          }
        },
        {
          "tipo": "mudar_inventario",
          "dados": {
            "item": "ouro",
            "operacao": "add",
            "quantidade": 500
          }
        }
      ]
    },
    {
      "id_pagina": 2,
      "condicoes": {
        "switches": [
          {"nome": "missao_guarda_ativa", "valor": true}
        ],
        "variaveis": [],
        "self_switch": null,
        "item_requerido": "pocao_cura"
      },
      "configuracao_visual": {
        "emoji": "💂",
        "atravessavel": false,
        "movimento": {"direcao": "parado", "ciclos": "estatico"}
      },
      "gatilho": "acao_jogador",
      "comandos": [
        {
          "tipo": "mensagem",
          "dados": {
            "texto": "Ah, você trouxe a poção de cura para os feridos! Pode entregá-la?"
          }
        },
        {
          "tipo": "bifurcacao_condicional",
          "dados": {
            "pergunta": "Entregar a poção?",
            "opcoes": ["Sim, aqui está", "Não agora"],
            "ramos": {
              "Sim, aqui está": [
                {
                  "tipo": "mudar_inventario",
                  "dados": {"item": "pocao_cura", "operacao": "sub", "quantidade": 1}
                },
                {
                  "tipo": "controle_switch",
                  "dados": {"nome": "dragao_derrotado", "valor": true}
                },
                {
                  "tipo": "controle_self_switch",
                  "dados": {"letra": "A", "valor": true}
                },
                {
                  "tipo": "mensagem",
                  "dados": {"texto": "Obrigado! Pegue esta recompensa."}
                }
              ],
              "Não agora": [
                {
                  "tipo": "mensagem",
                  "dados": {"texto": "Por favor, apresse-se. Eles precisam de ajuda."}
                }
              ]
            }
          }
        }
      ]
    },
    {
      "id_pagina": 1,
      "condicoes": {},
      "configuracao_visual": {
        "emoji": "💂",
        "atravessavel": false,
        "movimento": {"direcao": "parado", "ciclos": "estatico"}
      },
      "gatilho": "acao_jogador",
      "comandos": [
        {
          "tipo": "mensagem",
          "dados": {
            "texto": "Pare! O caminho à frente está bloqueado por monstros selvagens. Você aceita nos ajudar?"
          }
        },
        {
          "tipo": "bifurcacao_condicional",
          "dados": {
            "pergunta": "Aceitar missão?",
            "opcoes": ["Sim", "Não"],
            "ramos": {
              "Sim": [
                {
                  "tipo": "controle_switch",
                  "dados": {"nome": "missao_guarda_ativa", "valor": true}
                },
                {
                  "tipo": "mensagem",
                  "dados": {"texto": "Excelente! Encontre uma poção de cura e traga-me o quanto antes."}
                }
              ],
              "Não": [
                {
                  "tipo": "mensagem",
                  "dados": {"texto": "Volte quando estiver mais corajoso."}
                }
              ]
            }
          }
        }
      ]
    }
  ]
}

## 🪵 Extensão Extra: Payloads Especiais de Gatilhos e Puzzles

Para suportar as mecânicas levantadas no fluxograma (como empurrar objetos segurando botões, armadilhas automáticas no chão ou processos paralelos de clima), padronizamos os seguintes formatos de páginas para eventos específicos:

A) Puzzle de Empurrar / Puxar Bloco (segurar_confirmacao)
JSON

{
  "id_pagina": 1,
  "condicoes": {},
  "configuracao_visual": {"emoji": "🪨", "atravessavel": false, "movimento": {"direcao": "parado"}},
  "gatilho": "segurar_confirmacao",
  "comandos": [
    {
      "tipo": "mover_evento",
      "dados": {
        "alvo": "proprio",
        "direcao": "olhar_jogador", 
        "passos": 1,
        "ignorar_bloqueio": false
      }
    }
  ]
}

B) Armadilha Oculta de Chão (toque_jogador)
JSON

{
  "id_pagina": 1,
  "condicoes": {},
  "configuracao_visual": {"emoji": "🟩", "atravessavel": true},
  "gatilho": "toque_jogador",
  "comandos": [
    {
      "tipo": "efeito_sonoro",
      "dados": {"arquivo": "spikes.wav", "volume": 80}
    },
    {
      "tipo": "mudar_render",
      "dados": {"alvo": "proprio", "novo_emoji": "💀"}
    },
    {
      "tipo": "mudar_status_heroi",
      "dados": {"parametro": "hp", "operacao": "sub", "valor": 15}
    },
    {
      "tipo": "mensagem",
      "dados": {"texto": "[bold red]Aviso:[/] Você pisou em estacas escondidas e perdeu 15 de PV!"}
    }
  ]
}

C) Processo Paralelo (processo_paralelo - Dano por Veneno / Clima)
JSON

{
  "id_pagina": 1,
  "condicoes": {
    "switches": [{"nome": "heroi_envenenado", "valor": true}]
  },
  "configuracao_visual": {"emoji": "", "atravessavel": true},
  "gatilho": "processo_paralelo",
  "comandos": [
    {
      "tipo": "mudar_status_heroi",
      "dados": {"parametro": "hp", "operacao": "sub", "valor": 2}
    },
    {
      "tipo": "esperar",
      "dados": {"ciclos_ticks": 5}
    }
  ]
}

⚙️ Especificação Técnica do Interpretador de Payloads

Quando a interação dispara, o motor lógico do jogo deve processar o payload seguindo estritamente este pipeline técnico de quatro etapas:

[Interação/Gatilho Detectado]
              │
              ▼
    ┌───────────────────┐
    │  Pipeline Passo 1 │ ───> Executa loop decrescente de páginas (ex: Page 3 -> 2 -> 1).
    │  Filtro de Página │ ───> Confere se Switches e Variáveis no GameStateManager coincidem.
    └───────────────────┘
              │
              ▼ (Primeira página válida encontrada)
    ┌───────────────────┐
    │  Pipeline Passo 2 │ ───> Avalia se o Gatilho da página casa com o estímulo físico
    │ Validação Gatilho │      (ex: se o gatilho é "toque_jogador" e o herói pisou no bloco).
    └───────────────────┘
              │
              ▼ (Gatilho Correspondente)
    ┌───────────────────┐
    │  Pipeline Passo 3 │ ───> O interpretador linear lê o array de 'comandos' de cima a baixo.
    │  Loop de Comandos │ ───> Desvia para sub-rotinas baseadas na chave "tipo".
    └───────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  Pipeline Passo 4 │ ───> Modifica os componentes no EngineManager, emite eventos globais
    │  Mutação de Tela  │      no EventBus e força o redesenho visual dos quadros no Textual.
    └───────────────────┘

1. Estrutura do Dicionário de Condições (condicoes)

    switches: Lista de objetos contendo nome e o estado booleano esperado no seu GameStateManager.

    variaveis: Suporta operações relacionais numéricas (maior_ou_igual, menor_ou_igual, igual, diferente).

    self_switch: Interruptores locais atómicos (A, B, C, D). Permite que o evento lembre que já interagiu consigo mesmo (ex: mudar o emoji de baú fechado para baú aberto permanentemente) sem poluir a tabela global de switches da campanha.

    item_requerido: Verifica no InventoryComponent do herói (ID 1) se a string informada existe com quantidade maior que zero antes de abrir a página.

2. Dicionário de Comandos Padronizados (comandos)

Em vez de funções soltas, cada comando é um nó imperativo com um dicionário interno de dados:

    mensagem: Injeta texto formatado diretamente no log da interface lúdica.

    bifurcacao_condicional: Pausa a execução sequencial, renderiza opções no prompt e desvia o ponteiro para o sub-bloco do ramo escolhido pelo usuário.

    mudar_inventario / mudar_status_heroi: Altera diretamente os valores numéricos contidos nos componentes InventoryComponent e StatsComponent anexados à entidade da memória RAM.

    controle_self_switch: Altera o estado interno do próprio evento para que, no próximo ciclo de renderização, a página superior seja ativada.