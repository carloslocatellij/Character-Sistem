Markdown

# Guia de Instruções Arquiteturais: Motor TUI (Textual) + ECS (Esper)

Este guia serve como uma especificação técnica rígida e manual de instruções para Agentes de I.A. e Engenheiros de Software responsáveis pela manutenção, depuração e expansão deste motor de RPG baseado em Terminal. O sistema unifica o framework reativo **Textual** (camada visual TUI) ao motor de alto desempenho **Esper** (camada lógica ECS), persistido via **SQLAlchemy**.

---

## 1. Lógica Assíncrona de Interação e Pilha de Comandos

### O Problema Original
O uso de laços `for` síncronos e o bloqueio de loops assíncronos (`asyncio.run()`) dentro dos interpretadores de comandos quebravam o laço reativo principal do Textual, causando congelamento completo do terminal ou colisões de concorrência ao pausar para perguntas de NPCs ou Baús.

### Solução Arquitetural: Pilha de Comandos Não-Bloqueante
A execução de eventos baseados em scripts JSON estruturados (padrão RPG Maker) foi migrada para uma máquina de estados orientada a uma **Pilha de Comandos Linear (`pilha_de_comandos`)** dentro do `EventSystem`.

1. **Quebra Atômica:** O interpretador analisa um comando individual por vez.
2. **Interrupção Controlada:** Quando encontra um comando do tipo `bifurcacao_condicional`, o sistema renderiza as opções, mapeia os ramos válidos no dicionário `self.ramos_disponiveis` (por índice de texto e numérico), ativa a flag `self.aguardando_escolha = True` e **interrompe imediatamente o loop de execução** devolvendo o controle total da CPU para a TUI.
3. **Retoma Assíncrona:** Assim que o jogador submete a escolha, a interface invoca o método `avancar_ramo_evento(opcao_escolhida)`. Este método limpa o bloqueio, empilha o sub-ramo de ações correspondente no topo da pilha e reativa o loop executor central.

---

## 2. Implementação do Componente Customizado `ChoiceBox`

Para substituir inputs de chat de texto por caixas de diálogo interativas idênticas às de motores gráficos, foi desenvolvido o widget composto `ChoiceBox`.

### Tratamento do `OnDecoratorError` no Textual
O decorador `@on` do Textual exige que qualquer mensagem customizada filtrada por um seletor de ID (ex: `@on(ChoiceBox.Selected, "#box-evento-ativo")`) possua **obrigatoriamente** uma propriedade chamada `control` apontando para o próprio componente gerador do sinal. Sem isso, ocorre uma exceção fatal na inicialização do app.

```python
class ChoiceBox(Widget):
    class Selected(Message):
        def __init__(self, control: Widget, index: int, text: str) -> None:
            super().__init__()
            self._control = control
            self.index = index
            self.text = text

        @property
        def control(self) -> Widget:
            return self._control
```

Acoplamento Visual Responsivo na GamePlayScreen

Para embutir a ChoiceBox dinamicamente no painel de interações sem quebrar o enquadramento do layout fixo da TUI:

    Gerenciamento de Tamanho Dinâmico: Ao disparar a caixa de escolha, a propriedade .styles.height do painel de log (#area-interacao) é forçada temporariamente para um tamanho fixo curto (ex: "5"), liberando espaço para os botões de rádio. Ao encerrar o diálogo, define-se .styles.height = None para restaurar o layout CSS original (1fr).

    Ocultação e Foco: A barra de input padrão (#txt-chat) tem seu atributo .display definido como False e o foco do teclado é transferido explicitamente para a ChoiceBox via caixa_escolha.focus() encapsulado dentro de um agendamento seguro self.call_next().

    Bloqueio de Event Bubbling (Borbulhamento de Teclas): Para impedir que as setas direcionais do teclado alterem as opções do rádio e mexam o personagem no cenário simultaneamente, o método on_key na GamePlayScreen intercepta e consome os eventos caso o sistema esteja esperando uma resposta:
    Python

    if hasattr(self, "event_sys") and self.event_sys.aguardando_escolha:
        return

3. Gerenciamento de Cenas via Múltiplos Mundos (esper.WorldContext)
O Problema da Duplicação e Destruição de Estado

A abordagem inicial utilizando esper.clear_database() eliminava os vazamentos de monstros entre salas, mas gerava um efeito destrutivo severo: apagava o inventário do herói, removia seus equipamentos vigentes, reiniciava seus atributos lógicos calculados e deletava permanentemente todos os registros globais de Event Listeners (esper.event_registry), quebrando a comunicação assíncrona com a interface visual.
Solução de Engenharia: Persistência Congelada em RAM

O GameEngineLoader foi refatorado para utilizar isolamento completo de escopo usando o gerenciamento nativo de mundos do Esper. Cada mapa visitado gera ou recupera uma instância exclusiva de esper.WorldContext mantida na memória RAM no dicionário self.mundos_carregados.

```
                  ┌────────────────────────────────────────┐
                  │      GameEngineLoader (Central)        │
                  └────────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────┐                               ┌───────────────────────┐
│ Contexto: Mapa ID 1   │                               │ Contexto: Mapa ID 2   │
│ (esper.WorldContext)  │                               │ (esper.WorldContext)  │
├───────────────────────┤                               ├───────────────────────┤
│ • Monstros Locais     │                               │ • Monstros Locais     │
│ • Baús e Portas       │                               │ • Baús e Portas       │
│ ❌ Herói (ID 1 Removido)                               │ 🧙 Herói (ID 1 Ativo)  │
└───────────────────────┘                               └───────────────────────┘
```

    O Herói Nômade (ID 1 Fixo): O jogador é tratado como uma entidade transicional. Antes de trocar de cena, o método _salvar_snapshot_jogador() captura as instâncias puras de seus componentes (PositionComponent, StatsComponent, InventoryComponent, EquipmentComponent, RenderComponent) salvando-as num buffer temporário na RAM.

    Overwriting Limpo: Ao entrar em um novo mapa (seja inédito ou antigo), o loader aciona esper.switch_world(). No destino, se a Entidade 1 já existir de visitas passadas, seus componentes antigos são expurgados via .clear() para remover modificadores velhos de buffs ou debuffs locais, e os componentes atualizados do buffer nômade são re-injetados estritamente na assinatura de ID 1.

    Preservação de Progresso: Inimigos derrotados ou baús coletados no mapa anterior não são recriados nem destruídos; eles permanecem perfeitamente congelados no seu WorldContext original. Quando o herói retorna àquela sala através de uma porta, o mundo reativado exibe o cenário exatamente no estado em que foi deixado pelo jogador.

Unificação do Barramento de Eventos (master_event_registry)

Como a alternância de mundos substitui o dicionário interno de escutas do Esper por um limpo, os botões da interface visual paravam de funcionar ao cruzar portas. Para blindar o fluxo, o loader captura a referência mestre do barramento no __init__ e força cada novo mundo ou mundo recuperado a herdar esse barramento mestre:
Python

self.master_event_registry = getattr(esper, "event_registry", {})
# Durante a alternância de mundos:
if hasattr(esper, "event_registry"):
    esper.event_registry = self.master_event_registry

Conversão da Camada de Objetos Estáticos

O sistema de desenho de frames (RenderSystem) exige estritamente chaves baseadas em tuplas de inteiros representando as coordenadas (y, x). Como o banco de dados armazena os dicionários de objetos com chaves string estruturadas como "y,x", o método especializado privado _processar_camada_objetos realiza a tradução atômica em tempo de carregamento para evitar o desaparecimento visual de árvores, placas e decorações do cenário:
Python

```
def _processar_camada_objetos(self, mapa_db: MapaDB):
    objetos_convertidos = {}
    if mapa_db and mapa_db.objetos:
        obj_raw = mapa_db.objetos if isinstance(mapa_db.objetos, dict) else {}
        for coord_str, emoji in obj_raw.items():
            try:
                y_str, x_str = coord_str.split(",")
                objetos_convertidos[(int(y_str), int(x_str))] = emoji
            except Exception:
                pass
    self.camada_objetos = objetos_convertidos 
```

# Memória de Desenvolvimento: Sistema de RPG em Python
## Visão Geral do Projeto

- Desenvolvimento de um sistema profissional de criação de personagens e simulação de batalhas de RPG de mesa. O projeto segue os princípios de Clean Architecture (Arquitetura Limpa) e Domain-Driven Design (DDD), separando rigorosamente as regras de negócio (Domínio) do Banco de Dados e das Interfaces (CLI/Web).

## Stack Tecnológica Base

    Linguagem: Python 3.12+

    Testes Automatizados: pytest (com uso de monkeypatch para testes determinísticos de rolagens de dados).

    Banco de Dados (ORM): SQLAlchemy (SQLite temporário para testes e produção).

    Ambiente: python-dotenv (para chaveamento de banco de dados via .env).

    API Web: FastAPI (Próxima etapa).

## Estrutura de Diretórios Consolidada

rpg_api/
├── main_cli.py               # Interface de Linha de Comando e Tradutor (Mapper)
├── app/
│   ├── controllers/          # Controladores do jogo
│   │   └── game_controller.py
│   ├── core/                 # DOMÍNIO: Regras puras do jogo (Sem acesso a DB)
│   │   ├── engine/           # Sistema ECS (Entity-Component-System)
│   │   │   ├── components.py
│   │   │   ├── engine_loader.py
│   │   │   ├── event_bus.py
│   │   │   ├── game_state.py
│   │   │   ├── engine.py
│   │   │   └── systems.py
│   │   └── entities/         # Entidades de negócio
│   │       ├── emojis.py
│   │       ├── equipamentos.py
│   │       ├── habilidades_magias.py
│   │       ├── mapas.py
│   │       └── personagens.py
│   ├── db/                   # INFRA: Configuração de persistência
│   │   └── database.py       # Engine do SQLAlchemy e roteamento Teste/Prod
│   │   
│   ├── fastapi/              # API Web (Próxima etapa)
│   │   ├── main.py
│   │   └── routers/
│   │       └── personagens.py
│   ├── models/               # ESQUEMAS DO BANCO: Tabelas do Banco de Dados
│   │   ├── equipamentos_db.py
│   │   ├── eventos_db.py
│   │   ├── mapas_db.py
│   │   ├── personagens_db.py
│   │   ├── plataforma_db.py
│   │   └── schemas/          # Schemas Pydantic para FastAPI
│   │       └── rpg_schemas.py
│   ├── packages/             # Ferramentas e utilitários (Gerador de masmorras, Imagens)
│   │   ├── dungeon_gen.py
│   │   ├── resize.py
│   │   ├── show_img.py
│   │   └── stylewriter.py
│   └── views/                # Interfaces de Usuário Textual/Gráfica
│       ├── game_play_screen.py
│       ├── map_manager_screen.py
│       ├── simulador.py
│       ├── components/
│       │   └── choice_box.py
│       ├── styles/
│       │   ├── game_styles.css
│       │   └── styles.css
│       └── tools/
│           └── painting_tools.py
├── musics/                   # Controle de Áudio
│   └── audio_player.py
└── tests/                    # SUÍTE DE TESTES (TDD)
    ├── conftest.py
    ├── test_database.py
    ├── test_ecs_manager.py
    ├── test_editor_eventos.py
    ├── test_equipamentos.py
    ├── test_esper_integration.py
    ├── test_event_bus.py
    ├── test_game_controller.py
    ├── test_game_state_and_loader.py
    ├── test_habilidades_magias.py
    ├── test_interaction_system.py
    ├── test_logica_mapas.py
    ├── test_mainx_cli.py
    ├── test_personagens.py
    ├── test_personagens_db.py
    ├── test_renderizador.py
    └── test_simulador.py




## Passo a Passo da Implementação Realizada
### Fase 1: Núcleo de Domínio (Regras de Negócio)

    Sistema de Equipamentos: Criação de hierarquia base usando @dataclass (Item base para Arma, Armadura e Escudo).

    Sistema de Efeitos e Magias: * Criação de Efeito (dano/cura contínua, buffs/debuffs temporários).

        Criação de Magia e Habilidade. Implementado sistema de requisitos de magia baseado num dicionário de Caminhos Elementais (ex: {"fogo": 2}).

    Entidade Personagem: * Composição pura: Recebe objetos de Raca e ClasseRPG.

        Cálculo automático de hp, mp e Modificadores baseados nas fórmulas do MANUAL.md.

        Métodos de combate (atacar, receber_dano, lancar_magia) desenvolvidos com Design Orientado a Eventos (retornam dicionários com os resultados em vez de imprimir na tela).

        Controle rígido de exceções (ValueError) ao tentar aprender magias sem requisitos.

    Simulador de Combate: * Criação da classe SimuladorCombate responsável por gerir iniciativa e fluxo de turnos até a morte de uma das equipes.

        Geração de estatísticas por personagem (Dano causado, Abates, Taxa de Sobrevivência). Uso massivo de deepcopy para garantir simulações independentes.

### Fase 2: Banco de Dados e Infraestrutura

    Separação de Ambientes: Implementado app/db/database.py que lê TEST_VERSION do .env. Garante que testes automatizados usem banco de dados sqlite em memória sem sujar o banco de produção.

    Modelagem ORM: * Uso de colunas tipo JSON para armazenar de forma limpa os dicionários de bônus de atributos e caminhos de magia no SQLite.

        Criação do PersonagemDB com ForeignKeys obrigatórias para RacaDB e ClasseRPGDB.

        Resolução de AmbiguousForeignKeys na conexão de Equipamentos, especificando as FKs para mao_direita, mao_esquerda e armadura.

        Adoção de prática de salvar apenas "Status Base" no banco; cálculos derivados são responsabilidade exclusiva da classe do Domínio ao ser instanciada.

### Fase 3: Interface e Tradução (Adapter)

    CLI Interativa: Criação do main_cli.py para interação local, permitindo forjar raças, classes e personagens, e montar a Arena.

    Padrão Mapper: Implementada a função converter_para_dominio no CLI. Decisão arquitetural crucial: Extrai os dados puros das instâncias do Banco (SQLAlchemy) e injeta-os nos construtores das Entidades do Domínio (Personagem), garantindo isolamento entre camadas.

### Fase 4: Qualidade e Testes (TDD)

    Implementada suíte com 83+ testes.

    Uso do pytest rodando como módulo (python -m pytest) para evitar problemas de PYTHONPATH.

    Uso de monkeypatch para fixar resultados da função _rolar_d6 interna, permitindo testes precisos em regras de acerto e dano sem a interferência da aleatoriedade natural do RPG.

    Injeção e limpeza dinâmica de banco de dados (setup_module / teardown_module) para testes isolados de infraestrutura.


---

# 📜 Relatório de Desenvolvimento: RPG Game Maker (Textual + engine)

## 🎯 Objetivo Global

Desenvolver um **Motor de RPG e Criador de Jogos (Game Maker)** robusto e escalável para o terminal utilizando Python e o framework **Textual** e biblioteca python esper . O sistema suporta bases de dados para mapas, personagens, itens e eventos, utilizando uma arquitetura profissional onde a lógica do jogo (Engine) está completamente separada da interface gráfica (UI).

---

## 🚀 Fase 1: Descobertas e Prototipagem Visual (✅ Concluído)

Começamos por explorar as capacidades do framework Textual para manipulação de ecrãs em tempo real.

* **Space Ship Game:** Criámos um mini-jogo para entender o mapeamento de teclas (Bindings), a reatividade (`reactive`), a sobreposição de ecrãs e a utilização de temporizadores (`set_interval`) para criar um "Game Loop" simples.
* **Modelo Pokémon:** Explorámos a transição entre o mapa (Overworld) e ecrãs de batalha, introduzindo o padrão de **Event-Driven** e **Pilha de Ecrãs (Screen Stack)**.
* **Sistema de Grelha vs Objetos Livres:** Estabelecemos a diferença crucial entre renderizar um mapa estático (o chão/paredes) e renderizar entidades dinâmicas (jogadores/monstros).
* *Decisão:* O mapa é desenhado num bloco otimizado (`rich.text.Text`), enquanto as entidades são `Widgets` flutuantes (`position: absolute`) que se movem sobre ele.


---

## 🛠️ Fase 2: Integração de Dados e Resolução de Anomalias Visuais

Avançamos para a integração do sistema visual com a base de dados em desenvolvimento (`MapaDB`).

### ⚠️ Problemáticas Encontradas e Soluções:

1. **Desalinhamento do Mapa e Entidades:** (✅ Concluído)
* *Problema:* O mapa estava centrado no ecrã, mas as entidades nasciam no canto superior esquerdo do terminal, ignorando o mapa.
* *Solução:* Montar os widgets das entidades dinâmicas como **filhos diretos** do contentor do mapa (`#mapa-fundo`) e alterar o layout do contentor. Assim, o ponto lógico `(0,0)` das entidades passou a respeitar os limites do mapa.


2. **Rastos (Ghosting) de Emojis Complexos:** (✅ Concluído)
* *Problema:* Emojis compostos (como o Mago 🧙🏻‍♂️ com modificadores de cor e ZWJ) deixavam "lixo" visual (ex: ♂) ao moverem-se.
* *Solução:* Aumentar a largura (`width`) invisível do widget no CSS de 2 para 3, forçando o Textual a limpar uma área (bounding box) maior em cada atualização visual. 


3. **Efeito "Escadinha" e Bloqueio no Canto Superior:**
* *Problema:* Monstros ficavam empilhados uns abaixo dos outros ou bloqueados na coordenada `(0,0)`, atravessando paredes. (✅ Concluído)
* *Solução:* 1. Remover aninhamento (nesting) incorreto no ficheiro `styles.css`. (✅ Concluído)
2. Passar as coordenadas iniciais diretamente no `__init__` das entidades.(✅ Concluído)
3. Abandonar o uso de `offset` relativo e adotar propriedades absolutas (`top` e `left`). (✅ Concluído)


4. **Conflito de Threads (Race Conditions):** (✅ Concluído)
* *Problema:* O uso de `@work(thread=True)` causava falhas visuais ao alterar estados ao mesmo tempo que a interface tentava desenhar.
* *Solução:* Migração do motor de eventos para o sistema de *Timers* nativos do Textual (`set_interval`), tornando a execução segura e na thread principal.

---

## 🏗️ Fase 3: O Salto Arquitetural (✅ Concluído)

Percebemos que misturar a lógica de colisão e a física com os Widgets da interface estava a tornar o sistema frágil e pouco escalável. Decidimos refatorar o repositório baseando-nos nos Padrões de Indústria para Motores de Jogos.

### Decisões Arquiteturais Definidas (✅ Concluído):

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

1. **Implementar os Sistemas Lógicos (Systems):** (✅ Concluído)
* Criar o `MovementSystem`: Responsável por verificar colisões contra a grelha de terrenos e posições de outras entidades lógicas (sem depender de ecrãs).
* Criar o `InteractionSystem`: Que escutará a tecla "Enter" para despoletar comportamentos baseados no `InteractableComponent` (abrir um baú, iniciar diálogo).


2. **Sistema de Fila de Mensagens (Event Bus):** (✅ Concluído)
* Permitir que a Engine avise quando algo muda (ex: `"PLAYER_MOVED"`, `"ITEM_RECEIVED"`).
- `esper.set_handler(evento.nome, callback)`
- `esper.dispach(evento.nome)`


3. **Re-integração da Interface Visual (Textual):** (✅ Concluído)
* Construir a `GamePlayScreen` final, que fará uma assinatura ao *Event Bus* da Engine (esper).
* Decidir, com base na performance exigida, se usaremos *múltiplos Widgets absolutos* (como estávamos a tentar) ou se renderizaremos todo o mapa e entidades dinâmicas num *único frame de texto enriquecido (`rich.text.Text`)* atualizado a 60fps.