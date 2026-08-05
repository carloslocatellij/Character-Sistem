# Graph Report - rpg_api  (2026-08-02)

## Corpus Check
- 70 files · ~296,140 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1414 nodes · 3442 edges · 62 communities (60 shown, 2 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 756 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dac7ccb6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UsarItemBatalhaModal
- GamePlayScreen
- BattleScreen
- ItemFormScreen
- .criar_entidade_evento
- GameController
- TestPropriedadesEventoFormScreen
- StatsComponent
- PersonagemDB
- CatalogoTiles
- Raca
- PositionComponent
- AISystem
- BattleSystem
- TestGameControllerCriacoes
- DungeonGenerator
- PropriedadesFormScreen
- MovementSystem
- .carregar_engine_do_banco
- MapaInterativo
- CombatNetworkAdapter
- test_editor_eventos.py
- TestObterPaginaAtiva
- InventoryComponent
- ChatLog
- EventSystem
- TestMapearTipoEntidade
- routers/personagens.py
- rpg_schemas.py
- SimuladorCombate
- GameStateManager
- JogoAtaqueApp
- fixture
- PropriedadesEventoFormScreen
- ManagementMenuScreen
- MapManagerScreen
- GestorDeMapas
- .carregar_arvore_de_mapas
- NovoMapaFormScreen
- TestInicializacaoCombate
- Graphify Rule
- Personagem
- MapaDB
- SecondaryMap
- TestTurnoJogador
- TestResolucaoAcoes
- fixture_db_session
- VisualizadorImagem
- Dungeon Table Scene
- limpar_mundo_esper
- restaurar_mundo_esper
- The Begin 1 Image

## God Nodes (most connected - your core abstractions)
1. `Personagem` - 76 edges
2. `GameController` - 75 edges
3. `GamePlayScreen` - 73 edges
4. `InventoryComponent` - 72 edges
5. `StatsComponent` - 65 edges
6. `MapManagerScreen` - 62 edges
7. `PersonagemDB` - 61 edges
8. `ItemDB` - 59 edges
9. `Raca` - 57 edges
10. `ClasseRPG` - 56 edges

## Surprising Connections (you probably didn't know these)
- `CharacterFormScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `ClasseFormScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `CreationScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `EquipScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `ExplorerScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py

## Import Cycles
- None detected.

## Communities (62 total, 2 thin omitted)

### Community 0 - "UsarItemBatalhaModal"
Cohesion: 0.10
Nodes (14): CombatenteSprite, EfeitoAtaque, on, Pressed, Static, Tela de Combate por Turnos — BattleScreen Interface TUI do sistema de combate…, Widget de sprite do combatente com posição X animável via reactive. Seguindo o…, Sempre que x_pos mudar (via animação), atualiza o offset visual do sprite. (+6 more)

### Community 1 - "GamePlayScreen"
Cohesion: 0.06
Nodes (27): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+19 more)

### Community 2 - "BattleScreen"
Cohesion: 0.05
Nodes (29): AcaoConfirmada, BarraStatusCombate, BattleScreen, Any, Message, Screen, Widget, Atualiza os valores e redesenha as barras. (+21 more)

### Community 3 - "ItemFormScreen"
Cohesion: 0.08
Nodes (14): CharacterFormScreen, ClasseFormScreen, CreationScreen, EquipScreen, ExplorerScreen, ItemFormScreen, MainScreen, ComposeResult (+6 more)

### Community 4 - ".criar_entidade_evento"
Cohesion: 0.08
Nodes (16): _extrair_stats_salvos(), Any, Ponto de entrada principal para criação de entidades de evento. Determina o…, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa…, NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.…, Entidades pacíficas possuem HP defensivo mas não atacam ao tocar o jogador., Entidades interativas (portas, alavancas, armadilhas) são sólidas, sem stats de…, Veículos possuem MovimentComponent com tipo especial e não atacam. (+8 more)

### Community 5 - "GameController"
Cohesion: 0.05
Nodes (29): GameController, Session, Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., ArenaScreen, Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda. (+21 more)

### Community 6 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 7 - "StatsComponent"
Cohesion: 0.13
Nodes (35): CollisionComponent, EquipmentComponent, InteractableComponent, MovimentComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., Guarda os atributos de combate e informações vitais do personagem., Armazena o que está atualmente equipado no herói influenciando seus atributos., StatsComponent (+27 more)

### Community 8 - "PersonagemDB"
Cohesion: 0.08
Nodes (42): criar_e_salvar_mapa(), simular_arena(), ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., ClasseRPGDB, PersonagemDB, Base (+34 more)

### Community 9 - "CatalogoTiles"
Cohesion: 0.07
Nodes (28): CatalogoTiles, padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…, AcoesComandoScreen, AdicionarSwitchScreen (+20 more)

### Community 10 - "Raca"
Cohesion: 0.08
Nodes (40): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+32 more)

### Community 11 - "PositionComponent"
Cohesion: 0.10
Nodes (30): NetworkPlayerComponent, PositionComponent, Como a entidade se parece na interface., Onde a entidade está no mapa lógico., Identificador para jogadores que estão conectados via rede (multiplayer)., RenderComponent, GameEngineLoader, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos… (+22 more)

### Community 12 - "AISystem"
Cohesion: 0.47
Nodes (3): AISystem, Processa movimento autônomo de monstros/NPCs a cada tick., Compatibilidade legado.

### Community 13 - "BattleSystem"
Cohesion: 0.05
Nodes (42): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, BattleSystem, O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista. (+34 more)

### Community 14 - "TestGameControllerCriacoes"
Cohesion: 0.06
Nodes (18): Deve criar uma arma com dano e tipo de ataque., Deve criar uma raça válida com todos os atributos., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Verifica se todos os 5 atributos são salvos., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio)., Deve criar um personagem com todos os atributos válidos. (+10 more)

### Community 15 - "DungeonGenerator"
Cohesion: 0.09
Nodes (15): circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo., Verifica se este círculo se sobrepõe a outro., Gerador Procedimental Puro. Totalmente agnóstico: não possui dependências de… (+7 more)

### Community 16 - "PropriedadesFormScreen"
Cohesion: 0.09
Nodes (11): ArquivoCSVScreen, MenuAcoesScreen, PropriedadesFormScreen, Pressed, Tela flutuante para editar as propriedades de um mapa que já está na memória., Ao abrir, carrega os mapas do banco para o Select de Mapa Pai., Coleta o texto atual digitado nos campos para não perder o progresso., Tela de menu acionada pelo botão 'Menu' no topo. (+3 more)

### Community 17 - "MovementSystem"
Cohesion: 0.07
Nodes (21): PlayerControlComponent, Uma flag que indica que esta entidade é controlada pelo teclado., InteractionSystem, MovementSystem, Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, Verifica se há um evento à frente do jogador. Se houver, publica as informações…, Sistema lógico encarregado de validar a física e colisões de movimentos., build_interactable_component() (+13 more)

### Community 18 - ".carregar_engine_do_banco"
Cohesion: 0.11
Nodes (10): Any, Session, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo., Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem., Remove o jogador remoto do mundo atual usando o NetworkSystem. (+2 more)

### Community 19 - "MapaInterativo"
Cohesion: 0.12
Nodes (13): ComposeResult, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado., Apertou o botão do mouse: começa o traço e captura o foco., Soltou o botão do mouse: termina o traço e liberta o foco. (+5 more)

### Community 20 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 21 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 22 - "TestObterPaginaAtiva"
Cohesion: 0.13
Nodes (14): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+6 more)

### Community 23 - "InventoryComponent"
Cohesion: 0.06
Nodes (46): InventoryComponent, Armazena os itens que o personagem está carregando., aplicar_desequipar_item(), aplicar_equipar_item(), aplicar_usar_item(), garantir_itens_padrao(), inv_adicionar_item(), inv_remover_item() (+38 more)

### Community 24 - "ChatLog"
Cohesion: 0.10
Nodes (15): ChatLog, MensagemAnimada, App, ComposeResult, Static, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Processa a próxima mensagem da fila. (+7 more)

### Community 25 - "EventSystem"
Cohesion: 0.11
Nodes (12): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+4 more)

### Community 26 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 27 - "routers/personagens.py"
Cohesion: 0.22
Nodes (11): get_db(), Função utilitária para abrir e fechar a conexão com o banco corretamente., get, root(), criar_personagem(), criar_raca(), listar_personagens(), listar_racas() (+3 more)

### Community 28 - "rpg_schemas.py"
Cohesion: 0.43
Nodes (7): ClasseRPGCreate, ClasseRPGResponse, PersonagemCreate, PersonagemResponse, RacaCreate, RacaResponse, BaseModel

### Community 29 - "SimuladorCombate"
Cohesion: 0.19
Nodes (9): Any, Corre X batalhas em silêncio e agrupa todas as estatísticas num mega relatório., Gere as simulações de batalhas em grupo e recolhe estatísticas., Calcula a ordem de combate baseada em 1d6 + Agilidade., Filtra apenas os combatentes que ainda têm Pontos de Vida., Executa uma única batalha até uma equipa ser derrotada. Devolve um relatório de…, SimuladorCombate, Garante que a recolha estatística após 10 batalhas soma os valores corretamente. (+1 more)

### Community 30 - "GameStateManager"
Cohesion: 0.14
Nodes (10): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Base, Guarda o estado de execução de um jogo específico de um usuário. Desacoplado de…, SaveDB (+2 more)

### Community 31 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 32 - "fixture"
Cohesion: 0.13
Nodes (15): classe_default(), item_arma(), item_armadura(), item_escudo(), personagem_default(), fixture, raca_default(), Fixture: Escudo de teste. (+7 more)

### Community 33 - "PropriedadesEventoFormScreen"
Cohesion: 0.05
Nodes (23): AdicionarComandoScreen, PropriedadesEventoFormScreen, Changed, on, Pressed, RamoEditorScreen, Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou…, Atualiza todos os widgets com os dados da página atual. (+15 more)

### Community 34 - "ManagementMenuScreen"
Cohesion: 0.21
Nodes (5): ManagementMenuScreen, Changed, on, Redireciona para o formulário correto baseado na tabela atual., RowSelected

### Community 35 - "MapManagerScreen"
Cohesion: 0.07
Nodes (22): MapManagerScreen, Screen, Trata a resposta do utilizador no modal de confirmação., Tira uma fotografia à matriz atual antes de a alterarmos., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form., Callback acionado ao fechar a tela de Propriedades., Retrocede a matriz para o último estado guardado. (+14 more)

### Community 38 - "GestorDeMapas"
Cohesion: 0.12
Nodes (10): GestorDeMapas, Any, Lê as configurações do RPG e aciona o gerador independente correspondente., Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo. (+2 more)

### Community 40 - "NovoMapaFormScreen"
Cohesion: 0.17
Nodes (8): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Captura os cliques dos botões., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 44 - "TestInicializacaoCombate"
Cohesion: 0.20
Nodes (6): Testa o setup do combate via BattleSystem.iniciar_combate., Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.…, BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar., battle_sys.combate_ativo deve ser True após iniciar., Regra 5: Iniciativa = 1d6 + Agilidade. Com d6 fixo em 1, o personagem com maior…, TestInicializacaoCombate

### Community 46 - "Graphify Rule"
Cohesion: 0.22
Nodes (9): graphify-out/graph.json, GRAPH_REPORT.md, graphify CLI, graphify MCP, graphify-out Directory, Graphify Rule, graphify-out/wiki/index.md, Graphify Skill (+1 more)

### Community 47 - "Personagem"
Cohesion: 0.08
Nodes (25): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais., Personagem (+17 more)

### Community 48 - "MapaDB"
Cohesion: 0.13
Nodes (22): EventoDB, Base, CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., UsuarioDB, test_salvar_e_recuperar_evento_no_mapa() (+14 more)

### Community 50 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, ModalScreen, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 53 - "TestTurnoJogador"
Cohesion: 0.25
Nodes (5): Testa a execução de ações do jogador via BattleSystem., executar_acao_jogador('ataque') deve disparar 'turno_calculado' com…, executar_acao_jogador deve ignorar quando combate_ativo=False., Quando o inimigo morre no turno do jogador, deve disparar 'combate_encerrado'., TestTurnoJogador

### Community 54 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

### Community 58 - "fixture_db_session"
Cohesion: 0.67
Nodes (3): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste.

### Community 60 - "VisualizadorImagem"
Cohesion: 0.40
Nodes (3): App, ComposeResult, VisualizadorImagem

### Community 61 - "Dungeon Table Scene"
Cohesion: 0.40
Nodes (4): Dungeon Table Scene, Hourglass, Open Grimoire with Magic Symbols, Glowing Runic Sword

### Community 63 - "limpar_mundo_esper"
Cohesion: 0.67
Nodes (3): limpar_mundo_esper(), fixture, Garante isolamento total entre testes: reinicia o esper antes de cada um.

### Community 66 - "restaurar_mundo_esper"
Cohesion: 0.67
Nodes (3): fixture, Garante o isolamento completo entre os testes limpando completamente todas as…, restaurar_mundo_esper()

## Knowledge Gaps
- **11 isolated node(s):** `graphify-out Directory`, `graphify-out/graph.json`, `graphify CLI`, `graphify MCP`, `graphify-out/wiki/index.md` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GamePlayScreen` connect `GamePlayScreen` to `BattleScreen`, `ItemFormScreen`, `GameController`, `StatsComponent`, `PersonagemDB`, `Raca`, `PositionComponent`, `AISystem`, `BattleSystem`, `MovementSystem`, `InventoryComponent`, `ChatLog`, `EventSystem`, `GameStateManager`, `ManagementMenuScreen`, `TestInicializacaoCombate`, `MapaDB`, `TestTurnoJogador`, `TestResolucaoAcoes`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `PropriedadesEventoFormScreen`, `ManagementMenuScreen`, `ItemFormScreen`, `GameController`, `GestorDeMapas`, `.carregar_arvore_de_mapas`, `PersonagemDB`, `CatalogoTiles`, `TestPropriedadesEventoFormScreen`, `MapaDB`, `PropriedadesFormScreen`, `MapaInterativo`, `test_editor_eventos.py`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `GameController` connect `GameController` to `GamePlayScreen`, `ManagementMenuScreen`, `ItemFormScreen`, `GestorDeMapas`, `PersonagemDB`, `Raca`, `PositionComponent`, `TestGameControllerCriacoes`, `Personagem`, `MapaDB`, `SimuladorCombate`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `InventoryComponent` (e.g. with `GameEngineLoader` and `EntityFactory`) actually correct?**
  _`InventoryComponent` has 39 INFERRED edges - model-reasoned connections that need verification._