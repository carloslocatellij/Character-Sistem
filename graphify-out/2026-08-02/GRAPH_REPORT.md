# Graph Report - rpg_api  (2026-08-02)

## Corpus Check
- 67 files · ~293,416 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1362 nodes · 3268 edges · 70 communities (66 shown, 4 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 747 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dac7ccb6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- MockMapLoader
- .log_mensagem
- BattleScreen
- ItemFormScreen
- .criar_entidade_evento
- GameController
- TestPropriedadesEventoFormScreen
- StatsComponent
- PersonagemDB
- CatalogoTiles
- Arma
- GameEngineLoader
- AISystem
- test_battle_system.py
- TestGameControllerCriacoes
- DungeonGenerator
- PropriedadesFormScreen
- PositionComponent
- ._salvar_snapshot_jogador
- MapaInterativo
- CombatNetworkAdapter
- RenderComponent
- TestObterPaginaAtiva
- BattleSystem
- ChatLog
- InventarySystem
- TestMapearTipoEntidade
- routers/personagens.py
- TestCasosDeErroMainx
- Raca
- GameStateManager
- JogoAtaqueApp
- ItemDB
- PropriedadesEventoFormScreen
- ManagementMenuScreen
- MapManagerScreen
- .atacar
- AcaoConfirmada
- ConfirmacaoSalvarScreen
- .carregar_arvore_de_mapas
- NovoMapaFormScreen
- AdicionarComandoScreen
- TestGameControllerConversao
- RamoEditorScreen
- TestInicializacaoCombate
- TestIAInimigo
- Graphify Rule
- Personagem
- fixture_db_session
- SecondaryMap
- TestTurnoJogador
- TestResolucaoAcoes
- GamePlayScreen
- setup_esper
- fixture_db_session
- VisualizadorImagem
- Dungeon Table Scene
- limpar_mundo_esper
- restaurar_mundo_esper
- The Begin 1 Image

## God Nodes (most connected - your core abstractions)
1. `GameController` - 75 edges
2. `Personagem` - 73 edges
3. `GamePlayScreen` - 72 edges
4. `MapManagerScreen` - 62 edges
5. `PersonagemDB` - 61 edges
6. `StatsComponent` - 58 edges
7. `ItemDB` - 55 edges
8. `Raca` - 54 edges
9. `ClasseRPG` - 53 edges
10. `BattleSystem` - 52 edges

## Surprising Connections (you probably didn't know these)
- `ArenaScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `CharacterFormScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `ClasseFormScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `CreationScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py
- `EquipScreen` --uses--> `GameController`  [INFERRED]
  main_cli.py → app/controllers/game_controller.py

## Import Cycles
- None detected.

## Communities (70 total, 4 thin omitted)

### Community 1 - ".log_mensagem"
Cohesion: 0.06
Nodes (21): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+13 more)

### Community 2 - "BattleScreen"
Cohesion: 0.04
Nodes (36): BarraStatusCombate, BattleScreen, CombatenteSprite, EfeitoAtaque, on, Pressed, Screen, Static (+28 more)

### Community 3 - "ItemFormScreen"
Cohesion: 0.08
Nodes (15): CharacterFormScreen, ClasseFormScreen, CreationScreen, EquipScreen, ExplorerScreen, ItemFormScreen, ComposeResult, Pressed (+7 more)

### Community 4 - ".criar_entidade_evento"
Cohesion: 0.06
Nodes (22): Any, Session, Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo., Remove o jogador remoto do mundo atual usando o NetworkSystem., Atualiza a posição de um jogador remoto usando o NetworkSystem., Alterna ou inicializa o mundo do mapa alvo, sincronizando snapshots in RAM e… (+14 more)

### Community 5 - "GameController"
Cohesion: 0.06
Nodes (28): GameController, Session, Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda., Deve equipar uma armadura no corpo. (+20 more)

### Community 6 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 7 - "StatsComponent"
Cohesion: 0.12
Nodes (40): CollisionComponent, EquipmentComponent, InteractableComponent, InventoryComponent, MovimentComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., Guarda os atributos de combate e informações vitais do personagem., Armazena os itens que o personagem está carregando. (+32 more)

### Community 8 - "PersonagemDB"
Cohesion: 0.12
Nodes (25): simular_arena(), ClasseRPGDB, PersonagemDB, Base, RacaDB, Tabela que armazena as Classes/Profissões do jogo. Args: nome: str,…, Tabela central que armazena os Personagens dos jogadores., Tabela que armazena as Raças disponíveis no jogo. Args: nome: str,… (+17 more)

### Community 9 - "CatalogoTiles"
Cohesion: 0.09
Nodes (22): CatalogoTiles, padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…, Componente de Formulário de Eventos do Editor de Mapas. Contém todas as telas…, balde_de_tinta() (+14 more)

### Community 10 - "Arma"
Cohesion: 0.11
Nodes (20): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+12 more)

### Community 11 - "GameEngineLoader"
Cohesion: 0.08
Nodes (33): GameEngineLoader, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos…, Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem., NetworkSystem, Sistema responsável por sincronizar o estado de outros jogadores conectados…, EventoDB, Base, CenarioDB (+25 more)

### Community 12 - "AISystem"
Cohesion: 0.20
Nodes (3): AISystem, Processa movimento autônomo de monstros/NPCs a cada tick., Compatibilidade legado.

### Community 13 - "test_battle_system.py"
Cohesion: 0.07
Nodes (31): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, battle_sys(), classe_guerreiro(), eventos_capturados(), heroi() (+23 more)

### Community 14 - "TestGameControllerCriacoes"
Cohesion: 0.05
Nodes (25): Deve criar uma arma com dano e tipo de ataque., Deve criar uma raça válida com todos os atributos., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Verifica se todos os 5 atributos são salvos., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio)., Deve criar um personagem com todos os atributos válidos. (+17 more)

### Community 15 - "DungeonGenerator"
Cohesion: 0.08
Nodes (17): Any, Lê as configurações do RPG e aciona o gerador independente correspondente., circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo. (+9 more)

### Community 16 - "PropriedadesFormScreen"
Cohesion: 0.08
Nodes (14): GestorDeMapas, Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., ArquivoCSVScreen, MenuAcoesScreen, PropriedadesFormScreen, Pressed (+6 more)

### Community 17 - "PositionComponent"
Cohesion: 0.14
Nodes (19): PlayerControlComponent, PositionComponent, Uma flag que indica que esta entidade é controlada pelo teclado., Onde a entidade está no mapa lógico., InteractionSystem, MovementSystem, Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, Verifica se há um evento à frente do jogador. Se houver, publica as informações… (+11 more)

### Community 19 - "MapaInterativo"
Cohesion: 0.12
Nodes (13): ComposeResult, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado., Apertou o botão do mouse: começa o traço e captura o foco., Soltou o botão do mouse: termina o traço e liberta o foco. (+5 more)

### Community 20 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 21 - "RenderComponent"
Cohesion: 0.20
Nodes (11): NetworkPlayerComponent, Como a entidade se parece na interface., Identificador para jogadores que estão conectados via rede (multiplayer)., RenderComponent, Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em…, RenderSystem, test_fluxo_completo_engine_manager(), Testa se o Z-Index do RenderSystem respeita a ordem de prioridades: 1°… (+3 more)

### Community 22 - "TestObterPaginaAtiva"
Cohesion: 0.13
Nodes (14): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+6 more)

### Community 23 - "BattleSystem"
Cohesion: 0.11
Nodes (14): BattleSystem, IA simples para o primeiro inimigo da lista (alias de retrocompatibilidade).…, IA simples mas funcional para um inimigo específico: - Se tem mana e magias,…, Roteia a ação para o método correto da entidade Personagem do domínio., Encerra o combate e remove o CombatStateComponent da entidade do jogador., O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista. (+6 more)

### Community 24 - "ChatLog"
Cohesion: 0.10
Nodes (15): ChatLog, MensagemAnimada, App, ComposeResult, Static, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Processa a próxima mensagem da fila. (+7 more)

### Community 25 - "InventarySystem"
Cohesion: 0.11
Nodes (12): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+4 more)

### Community 26 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 27 - "routers/personagens.py"
Cohesion: 0.15
Nodes (18): get_db(), Função utilitária para abrir e fechar a conexão com o banco corretamente., get, root(), criar_personagem(), criar_raca(), listar_personagens(), listar_racas() (+10 more)

### Community 28 - "TestCasosDeErroMainx"
Cohesion: 0.33
Nodes (4): Testes de tratamento de erros., Teste edge case: atributos com tipo errado., Testa se um item pode ser equipado em dois slots (não deveria)., TestCasosDeErroMainx

### Community 29 - "Raca"
Cohesion: 0.10
Nodes (35): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais., ClasseRPG (+27 more)

### Community 30 - "GameStateManager"
Cohesion: 0.16
Nodes (7): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Testa se os seletores lógicos (Switches) persistem dinamicamente através do…, test_game_state_manager_salvamento_e_recuperacao_de_switches()

### Community 31 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 32 - "ItemDB"
Cohesion: 0.12
Nodes (17): ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., classe_default(), item_arma(), item_armadura(), item_escudo(), fixture (+9 more)

### Community 33 - "PropriedadesEventoFormScreen"
Cohesion: 0.06
Nodes (29): PropriedadesEventoFormScreen, Changed, on, Atualiza todos os widgets com os dados da página atual., Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.… (+21 more)

### Community 34 - "ManagementMenuScreen"
Cohesion: 0.29
Nodes (3): ManagementMenuScreen, Changed, on

### Community 35 - "MapManagerScreen"
Cohesion: 0.06
Nodes (24): MapManagerScreen, Screen, Trata a resposta do utilizador no modal de confirmação., Tira uma fotografia à matriz atual antes de a alterarmos., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Gerencia os cliques na tela principal., Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form., Callback acionado ao fechar a tela de Propriedades. (+16 more)

### Community 36 - ".atacar"
Cohesion: 0.31
Nodes (5): Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Realiza a mecânica completa de ataque contra um alvo.

### Community 37 - "AcaoConfirmada"
Cohesion: 0.25
Nodes (5): AcaoConfirmada, Any, Message, Widget, Mensagem interna emitida quando o jogador confirma sua ação. Segue o padrão da…

### Community 38 - "ConfirmacaoSalvarScreen"
Cohesion: 0.33
Nodes (4): ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo., Dispara quando o utilizador clica num mapa na barra lateral., NodeSelected

### Community 40 - "NovoMapaFormScreen"
Cohesion: 0.21
Nodes (7): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 41 - "AdicionarComandoScreen"
Cohesion: 0.12
Nodes (8): AdicionarComandoScreen, AdicionarSwitchScreen, AdicionarVariavelScreen, Pressed, Modal simples para adicionar uma condição de Switch a uma página., Modal simples para adicionar uma condição de Variável numérica a uma página., Sub-formulário para gerar comandos baseados no tipo selecionado., Serializa o estado atual do formulário de teleporte para não perder progresso.

### Community 42 - "TestGameControllerConversao"
Cohesion: 0.33
Nodes (4): Testes da conversão BD -> Domínio., Deve converter personagem sem equipamentos., Deve converter personagem com todos os equipamentos., TestGameControllerConversao

### Community 43 - "RamoEditorScreen"
Cohesion: 0.16
Nodes (5): AcoesComandoScreen, RamoEditorScreen, Menu contextual ao clicar num comando da lista., Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou…, Modo_de_Captura

### Community 44 - "TestInicializacaoCombate"
Cohesion: 0.20
Nodes (6): Testa o setup do combate via BattleSystem.iniciar_combate., Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.…, BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar., battle_sys.combate_ativo deve ser True após iniciar., Regra 5: Iniciativa = 1d6 + Agilidade. Com d6 fixo em 1, o personagem com maior…, TestInicializacaoCombate

### Community 45 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

### Community 46 - "Graphify Rule"
Cohesion: 0.22
Nodes (9): graphify-out/graph.json, GRAPH_REPORT.md, graphify CLI, graphify MCP, graphify-out Directory, Graphify Rule, graphify-out/wiki/index.md, Graphify Skill (+1 more)

### Community 47 - "Personagem"
Cohesion: 0.10
Nodes (15): Personagem, Dano direto que ignora armadura (ex: veneno)., Adiciona um efeito à lista de ativos., Roda no fim do turno: processa venenos, curas e reduz duração., Verifica se o personagem tem a Exuberância e os Pontos nos Caminhos exigidos., Tenta adicionar a magia à lista do personagem, levanta Exceção se não puder., Executa a magia conforme MANUAL.md (Teste Resistido)., Recalcula atributos E Caminhos de Magia. (+7 more)

### Community 48 - "fixture_db_session"
Cohesion: 0.67
Nodes (3): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste.

### Community 50 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, ModalScreen, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 53 - "TestTurnoJogador"
Cohesion: 0.25
Nodes (5): Testa a execução de ações do jogador via BattleSystem., executar_acao_jogador('ataque') deve disparar 'turno_calculado' com…, executar_acao_jogador deve ignorar quando combate_ativo=False., Quando o inimigo morre no turno do jogador, deve disparar 'combate_encerrado'., TestTurnoJogador

### Community 54 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

### Community 56 - "GamePlayScreen"
Cohesion: 0.14
Nodes (12): criar_e_salvar_mapa(), MapaDB, Base, GamePlayScreen, Screen, Limpa as escutas de eventos do Esper ao fechar a tela., action_start_stop_music(), ArenaScreen (+4 more)

### Community 57 - "setup_esper"
Cohesion: 0.67
Nodes (3): fixture, Reseta o mundo global do Esper antes de cada teste., setup_esper()

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
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GamePlayScreen` connect `GamePlayScreen` to `.log_mensagem`, `BattleScreen`, `ItemFormScreen`, `GameController`, `StatsComponent`, `PersonagemDB`, `Arma`, `GameEngineLoader`, `AISystem`, `test_battle_system.py`, `PositionComponent`, `RenderComponent`, `BattleSystem`, `ChatLog`, `InventarySystem`, `GameStateManager`, `ManagementMenuScreen`, `TestInicializacaoCombate`, `TestIAInimigo`, `TestTurnoJogador`, `TestResolucaoAcoes`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `GameController` connect `GameController` to `ItemDB`, `ManagementMenuScreen`, `ItemFormScreen`, `PersonagemDB`, `Arma`, `GameEngineLoader`, `TestGameControllerConversao`, `TestGameControllerCriacoes`, `Personagem`, `PropriedadesFormScreen`, `GamePlayScreen`, `TestCasosDeErroMainx`, `Raca`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `ItemDB`, `PropriedadesEventoFormScreen`, `ManagementMenuScreen`, `ItemFormScreen`, `ConfirmacaoSalvarScreen`, `.carregar_arvore_de_mapas`, `PersonagemDB`, `CatalogoTiles`, `TestPropriedadesEventoFormScreen`, `GameEngineLoader`, `PropriedadesFormScreen`, `MapaInterativo`, `GamePlayScreen`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `MapManagerScreen` (e.g. with `CatalogoTiles` and `GestorDeMapas`) actually correct?**
  _`MapManagerScreen` has 19 INFERRED edges - model-reasoned connections that need verification._