# O Criador de jogos de RPG

### Idealizado para ser uma ferramenta de gerenciamento de campanhas para mestres de RPG, está se tornando um Criador de jogos estilo Final Fantasy.


- Banco de dados para:
	- Personagens
	- Classes
	- Raças
	- Itens e Equipamentos
	- Mapas
	- Eventos
	
- Simulador de Combate

- Editor de mapas


- ### Jogar 
- Função de jogar (testar o jogo em funcionamento)


### Salvar / Carregar jogo:

- Suporte ao salvamento de Estados (todas as variáveis pertinentes ao tempo de execução que dizem o que está acontecendo no jogo): 
	- Qual mapa e em qual posição está o jogador
	- O status atual do personagem ( Nível, pv_atual, pm_atual, etc...)
	- Inventário atual do personagem
	- Equipamentos: Arma, armadura e escudo equipados no personagem.
	- Eventos que foram acionados e estados que sustentam a estrutura da história.
	- Outras variáveis de estado pertinentes ao jogo.


### Geração de múltiplos jogos independentes.

- O usuário poderá criar seus próprios  jogos completos:  O banco de dados deverá ter versionamento ou mecanismo semelhante para que cada usuário possa criar seus próprios jogos, escolher entre eles para jogar ou compartilhar com outros usuários.

##### Multiplayer:

[ ] Autenticação
[ ] Perfil do usuário
[ ] Comunidades
[ ] Tela de chats e interação de usuários
[ ] Compartinhamento de cenários
[ ] Jogo Multiplayer

#### Modo Jogo ROGUE LIKE:

[ ] Gerador de cenários procedural automático por árvores de mapas aninhados e com pontos de conexão por eventos de teleporte 
[ ] Gerador de eventos semi-aleatorios por categoria
[ ] Gerador de NPCs semi-aleatorios por categoria 
[ ] Sistema Conector de História

 

## Personagem
O que ele faz?

-> Move
-> Aciona coisas
-> Chama Menu *

---
### Mover - Cima / Baixo / Direita / Esquerda (teclas direcionais)
- Alguns elementos ou eventos serão acionados apenas com esta ação: O personagem se move sobre ou encosta no evento e ele **``dispara``**.

---

### Acionar - (tecla Enter)

- Base de todo mecanismo de funcionamento do jogo.
	- O acionar *chama* ou ``**Dispara**`` eventos que levam ao acionamento ou desencadeamento de **estados** possíveis que somados resultam no desenrolar do jogo.
##### -> Fundamental que o motor esteja sempre *escutando* estas ações.

- #### Conversas 
	- Um quadro de mensagem: De uma simples placa com o nome da cidade até um mecanismo completo de atribuição de valores, perguntas e respostas e escolhas que podem interferir completamente na dinâmica e até constituir mini-games.
	- ##### Compra / Venda (Lojas) São conversas aprimoradas, configuráveis e reutilizáveis.
	
- #### Acionamento de Eventos:
	- Acionamento padrão de eventos (reutilizáveis ou não): Pressionando a tecla Enter de frente para blocos de evento estes são acionados (baús, portas, NPCs, objetos em geral)
		- Estes eventos carregam em si a lógica de seu funcionamento.

- #### Acionamento Extra. (Pressionar e segurar tecla)
	- Em algumas situações ou condições segurar a tecla Enter por determinado tempo resulta numa mecânica ou interação diferente junto aos objetos ou eventos do cenário. Ex: Puxar / Empurrar, Segurar/ Soltar.  Isto permite o desenvolvimento de puzzles específicos.

---

### Menu - (tecla Tab)

Vai trazer as opções de salvar, carregar e também:

- #### [[Game Maker|Equipar Item]]
- #### Usar itens
- #### Usar Habilidades 
- #### Mudar a Equipe


## Eventos
O que eles fazem?

-> Move
-> São acionados

---
#### Mover - Cima / Baixo / Direita / Esquerda / Segue / Foge
- Eventos podem se mover se forem programados para isso, o disparo do movimento pode ser por meio de algum acionamento do personagem ou mudança no estado do jogo (mudança de mapa etc...)
- Podem seguir o personagem ou outro evento, fugir do personagem ou outro evento, seguir uma rota determinada (em ciclo ou não).
---

### Tecla '/'
- Vai para barra de comandos



# Sistema de jogo de RPG de mesa baseado em turnos

- Permite a criação de personagens para jogos de RPG com seus atributos, características, habilidades, raças e classes, etc...
- Permite a criação novas de raças com suas características próprias.
- Permite a criação de classes com suas características, atributos, habilidades próprias, etc ...
- Permite a criação de itens, equimapentos, armas e armaduras para equipar os personagens.
- Permite uma mecânica de batalha com as ações dos persongens na qual os atributos serão calculados e comparados para determinar o resultado.
- Permite simulações das batalhas.

## Sistema de Personagens
- A Raça e a Classe deverão ter propriedades que serão usadas para a composição do personagem.

### Raça
- A Raça tem nome e um dicionário de bonus de atributos a ser aplicados ao Personagem.
- A Raça tem representação por emojis.

### ClasseRPG
- A ClasseRPG tem nome, um dicionário de caminhos de magia "caminhos_magia", uma lista de habilidades e um dicionário de bonus_atributos que são aplicados ao personagem da classe.

### Personagem
- Personagem tem nome e nivel, é composto por ClasseRPG e Raça, têm um dicionário de atributos (
"forca": forca_base, "agilidade": agilidade_base, "resistencia": res_base, "percepcao": perc_base,    "exuberancia": exub_base). Além de ter mão_direta, mão_esquerda, armadura, itens de corpo e equipamentos. 
- O Personagem tem também uma lista de efeitos ativos.
- Boa parte do mecanismo de funcionamento do sistema vem dos métodos do Personagem, ou seja, um conjunto de ações (funções da class) que consistêm na forma que o sistema utiliza a class Personagem (atualizar_atributos_totais, _calcular_status_derivados, reset_status, calcular_defesa_esquiva, receber_dano, receber_dano_de_efeito e finalizar_turno) e também ações que podem ser usadas pelo sistema ou pelo usuário (atacar, lancar_magia, usar_item)

## Sistema de Magia, Habilidade e Efeitos:

### Habilidades
- Habilidades são um tipo de ação especial (sem ser atacar, andar, esquivar e se defender) que alguns personagens têm e podem executar durante o combate.
- Cada habilidade possui um nome, tipo, dano_base, efeitos, requisitos, area, alcance e se pode ser usada em aliados.

### Magias
- Magias são um tipo de habilidade (herda de Habilidade).
- Magia, além do que tem em habilidade, tem caminho e custo_mana.

### Efeitos
- Efeitos são eventos de status que uma habilidade ou magia podem apensar a um personagem. Em quanto durar o efeito o personagem fica sob as condições aplicadas pelo efeito. 
- Efeito tem nome, tipo, duração, área, dano_base, modificadores e podem ter uma função dinâmica para calculo de dano/recuperação.
- No início de cada turno de combate os resultados da aplicação de efeitos deve ser computados e aplicados.

#### Caminhos de Magia
No dicionário de Caminhos de Magias da ClasseRPG as chaves são os caminhos ("luz", "trevas", "fogo", "água", "ar" e "terra") e os valores são os pontos que o personagem tem no caminho (padrão=0).
- Os valores em pontos nos caminhos serão usados para verificar se o personagem pode possuir determinada magia: Na criação do objeto Personagem deve haver uma verificação para cada Magia ou Habilidade da Classe atribuida se as caracteristicas/atributos passados ao Personagem em questão atendem aos requistos da Magia/Habilidade, levantando uma Exessão em caso de não atendimento. 

## Sistema de Equipamentos
- O persongem também podera ser equipado com Itens, Armas, Armaduras e Escudo.
- Item terá nome, peso e uma representação visual por emoji
- Arma herda estas características de item, além de ter dano e tipo.
Armadura herda de item e tem a propriedade defesa.
Escudo herda de item e tem a propriedade defesa_extra.


## Sistema Simulação de Batalhas

### É um Simulador de Combate independente em Grupo. Neste simulador deverão ser passados os personagens aliados e os oponentes. A iniciativa será rolada para todos e o combate ira ocorrer nesta sequência até o final( todos os oponentes ou todos os aliados serem terem seus pontos de vida zerados ou a baixo de zero) 
- Contém um simulador que simula uma batalha individual e imprime os resultados dos acontecimentos de cada turno.
- Contém um simulador estatísco que recebe um número de batalhas (padrão = 100), realiza as simulações silenciosas, coleta resultados dos eventos por personagem (número de acertos, dano causa, cura causada, número de defesas, mortes causadas e batalhas sobrevividas), e o número de vitorias e derrotas de cada time.


## Criador de Mapas

### Um potente editor com gerador procedural para novos mapas: ('caverna', 'vila', 'masmorra'), atua em 3 camdas: (Terrenos, Objetos, Eventos). 

### Permite: Gerar, Importar de csv, Exportar para csv, Salvar no Banco de dados, Editar as camadas e Atribuir propriedades específicas como aninhamento de mapas 'mapa_pai'.
- [x] Mantem uma paleta de emojis por camada (Terreno, Objetos, Eventos).
- [x] Função de desenhar arrastando pincel no mapa.
- [x] Funções de Desfazer e Refazer.
- [x] Alterna entre 'pincel' e 'balde de tinta'.
- [x] Ao inserir evento abre Formulário de Configurações dos dados do evento - Eventos são salvos em EventDB e possuem um campo de ligação com o mapa 'mapa_id'.
- [ ] Tipo: Novo mapa em branco.
- [ ] Pincel de retangulo
- [ ] Pincel de circulo
- [ ] Pincel de linha
- [ ] Recortar e Colar



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


- Verificar em .specs/modelos_de_parametros_eventos.json

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
      "dados": {"texto": "[bold red]Aviso:[/] Você pisou em estacas escondidas e perdeu 15 de hp!"}
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