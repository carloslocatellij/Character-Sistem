Aqui está o relatório de memória do chat estruturado em formato Markdown. Este documento resume a nossa jornada desde os primeiros protótipos visuais até à adoção de uma arquitetura profissional de Motor de Jogos (Engine), servindo como guia para os próximos passos do desenvolvimento.

---

# 📜 Relatório de Desenvolvimento: RPG Game Maker (Textual + engine)

## 🎯 Objetivo Global

Desenvolver um **Motor de RPG e Criador de Jogos (Game Maker)** robusto e escalável para o terminal utilizando Python e o framework **Textual**. O sistema suporta bases de dados para mapas, personagens, itens e eventos, utilizando uma arquitetura profissional onde a lógica do jogo (Engine) está completamente separada da interface gráfica (UI).

---

## 🚀 Fase 1: Descobertas e Prototipagem Visual

Começámos por explorar as capacidades do framework Textual para manipulação de ecrãs em tempo real.

* **Space Ship Game:** Criámos um mini-jogo para entender o mapeamento de teclas (Bindings), a reatividade (`reactive`), a sobreposição de ecrãs e a utilização de temporizadores (`set_interval`) para criar um "Game Loop" simples.
* **Modelo Pokémon:** Explorámos a transição entre o mapa (Overworld) e ecrãs de batalha, introduzindo o padrão de **Event-Driven** e **Pilha de Ecrãs (Screen Stack)**.
* **Sistema de Grelha vs Objetos Livres:** Estabelecemos a diferença crucial entre renderizar um mapa estático (o chão/paredes) e renderizar entidades dinâmicas (jogadores/monstros).
* *Decisão:* O mapa é desenhado num bloco otimizado (`rich.text.Text`), enquanto as entidades são `Widgets` flutuantes (`position: absolute`) que se movem sobre ele.



---

## 🛠️ Fase 2: Integração de Dados e Resolução de Anomalias Visuais

Avançámos para a integração do sistema visual com a base de dados em desenvolvimento (`MapaDB`).

### ⚠️ Problemáticas Encontradas e Soluções:

1. **Desalinhamento do Mapa e Entidades:**
* *Problema:* O mapa estava centrado no ecrã, mas as entidades nasciam no canto superior esquerdo do terminal, ignorando o mapa.
* *Solução:* Montar os widgets das entidades dinâmicas como **filhos diretos** do contentor do mapa (`#mapa-fundo`) e alterar o layout do contentor. Assim, o ponto lógico `(0,0)` das entidades passou a respeitar os limites do mapa.


2. **Rastos (Ghosting) de Emojis Complexos:**
* *Problema:* Emojis compostos (como o Mago 🧙🏻‍♂️ com modificadores de cor e ZWJ) deixavam "lixo" visual (ex: ♂) ao moverem-se.
* *Solução:* Aumentar a largura (`width`) invisível do widget no CSS de 2 para 5, forçando o Textual a limpar uma área (bounding box) maior em cada atualização visual.


3. **Efeito "Escadinha" e Bloqueio no Canto Superior:**
* *Problema:* Monstros ficavam empilhados uns abaixo dos outros ou bloqueados na coordenada `(0,0)`, atravessando paredes.
* *Solução:* 1. Remover aninhamento (nesting) incorreto no ficheiro `styles.css`.
2. Passar as coordenadas iniciais diretamente no `__init__` das entidades.
3. Abandonar o uso de `offset` relativo e adotar propriedades absolutas (`top` e `left`).


4. **Conflito de Threads (Race Conditions):**
* *Problema:* O uso de `@work(thread=True)` causava falhas visuais ao alterar estados ao mesmo tempo que a interface tentava desenhar.
* *Solução:* Migração do motor de eventos para o sistema de *Timers* nativos do Textual (`set_interval`), tornando a execução segura e na thread principal.



---

## 🏗️ Fase 3: O Salto Arquitetural (Onde Estamos Agora)

Percebemos que misturar a lógica de colisão e a física com os Widgets da interface estava a tornar o sistema frágil e pouco escalável. Decidimos refatorar o repositório baseando-nos nos Padrões de Indústria para Motores de Jogos.

### Decisões Arquiteturais Definidas:

* **Arquitetura engine (Entity-Component-System):** Abandonámos a herança clássica. Agora, tudo é uma `Entidade` (ID numérico) que possui `Componentes` (sacolas de dados puros como `PositionComponent`, `InteractableComponent`) e é gerida por `Sistemas` lógicos.
* **Motor Headless (Desacoplado):** A Engine roda em memória independentemente do Textual. O Textual atua apenas como um "visualizador" passivo do estado da Engine.
* **TDD (Test-Driven Development):** Estamos a reconstruir a base funcional com testes unitários rigorosos para garantir que o motor não quebra à medida que adicionamos funcionalidades.

### Progresso Atual do TDD:

1. **Modelos de Base de Dados (✅ Concluído):** * Criado o `EventoDB` (para suportar NPCs, Lojas e Baús) interligado ao `MapaDB`.
* Resolvido erro do SQLAlchemy criando um ficheiro `__init__.py` para garantir o registo correto das classes no ORM.


2. **engine e Memória Lógica (✅ Concluído):**
* Criadas as classes `EngineManager`, `Components` e `GameEngine`.
* A Engine já consegue ler um mapa da base de dados, interpretar os seus eventos e instanciá-los como Entidades com Componentes na memória lógica. Testes aprovados.



---

## 🗺️ Próximos Passos (Roadmap)

Com a fundação lógica (Engine) estabelecida, o nosso foco prossegue na camada Headless antes de religar a camada visual:

1. **Implementar os Sistemas Lógicos (Systems):**
* Criar o `MovementSystem`: Responsável por verificar colisões contra a grelha de terrenos e posições de outras entidades lógicas (sem depender de ecrãs).
* Criar o `InteractionSystem`: Que escutará a tecla "Enter" para despoletar comportamentos baseados no `InteractableComponent` (abrir um baú, iniciar diálogo).


2. **Sistema de Fila de Mensagens (Event Bus):**
* Permitir que a Engine avise quando algo muda (ex: `"PLAYER_MOVED"`, `"ITEM_RECEIVED"`).


3. **Re-integração da Interface Visual (Textual):**
* Construir a `GamePlayScreen` final, que fará uma assinatura ao *Event Bus* da Engine.
* Decidir, com base na performance exigida, se usaremos *múltiplos Widgets absolutos* (como estávamos a tentar) ou se renderizaremos todo o mapa e entidades dinâmicas num *único frame de texto enriquecido (`rich.text.Text`)* atualizado a 60fps.