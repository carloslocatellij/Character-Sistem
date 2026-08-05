# Graph Report - rpg_api  (2026-08-01)

## Corpus Check
- 67 files · ~293,044 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1357 nodes · 3256 edges · 75 communities (71 shown, 4 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 746 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dac7ccb6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Arma
- GamePlayScreen
- BattleScreen
- ItemFormScreen
- .criar_entidade_evento
- GameController
- TestPropriedadesEventoFormScreen
- StatsComponent
- PersonagemDB
- CatalogoTiles
- Personagem
- MapaDB
- PositionComponent
- test_battle_system.py
- TestGameControllerCriacoes
- DungeonGenerator
- PropriedadesFormScreen
- MovementSystem
- GameEngineLoader
- MapaInterativo
- CombatNetworkAdapter
- ._escrever_log
- TestObterPaginaAtiva
- BattleSystem
- ChatLog
- InventarySystem
- TestMapearTipoEntidade
- routers/personagens.py
- TestValidacaoEntradas
- Raca
- GameStateManager
- JogoAtaqueApp
- ItemDB
- PropriedadesEventoFormScreen
- ManagementMenuScreen
- MapManagerScreen
- ._obter_condicoes_pagina_atual
- Any
- test_editor_eventos.py
- .carregar_arvore_de_mapas
- NovoMapaFormScreen
- AdicionarComandoScreen
- on
- RamoEditorScreen
- TestInicializacaoCombate
- TestIAInimigo
- Graphify Rule
- .atacar
- test_esper_integration.py
- .criar_entidade_jogador_de_save
- SecondaryMap
- ConfirmacaoSalvarScreen
- AISystem
- TestTurnoJogador
- TestResolucaoAcoes
- fixture_db_session
- .test_usar_item_com_sucesso
- .test_usar_item_sem_sucesso
- TestGameControllerConversao
- TestEquipamentoMainx
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

## Communities (75 total, 4 thin omitted)

### Community 0 - "Arma"
Cohesion: 0.13
Nodes (18): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+10 more)

### Community 1 - "GamePlayScreen"
Cohesion: 0.06
Nodes (27): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+19 more)

### Community 2 - "BattleScreen"
Cohesion: 0.05
Nodes (31): AcaoConfirmada, BarraStatusCombate, BattleScreen, CombatenteSprite, EfeitoAtaque, Any, Message, Screen (+23 more)

### Community 3 - "ItemFormScreen"
Cohesion: 0.08
Nodes (15): ArenaScreen, CharacterFormScreen, ClasseFormScreen, CreationScreen, EquipScreen, ExplorerScreen, ItemFormScreen, MainScreen (+7 more)

### Community 4 - ".criar_entidade_evento"
Cohesion: 0.13
Nodes (7): Ponto de entrada principal para criação de entidades de evento. Determina o…, Itens são atravessáveis — o jogador pode andar sobre eles para coletar.…, _criar_entidade_vazia(), Verifica que Monstros recebem StatsComponent e MovimentComponent…, Verifica que a correção do bug IndexError está funcionando., Cria uma entidade em branco no esper e retorna seu ID., TestCriarEntidadeMonstro

### Community 5 - "GameController"
Cohesion: 0.06
Nodes (25): GameController, Session, Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda., Deve equipar uma armadura no corpo. (+17 more)

### Community 6 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 7 - "StatsComponent"
Cohesion: 0.18
Nodes (34): CollisionComponent, EquipmentComponent, InteractableComponent, InventoryComponent, MovimentComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., Guarda os atributos de combate e informações vitais do personagem., Armazena os itens que o personagem está carregando. (+26 more)

### Community 8 - "PersonagemDB"
Cohesion: 0.11
Nodes (26): simular_arena(), ClasseRPGDB, PersonagemDB, Base, RacaDB, Tabela que armazena as Classes/Profissões do jogo. Args: nome: str,…, Tabela central que armazena os Personagens dos jogadores., Tabela que armazena as Raças disponíveis no jogo. Args: nome: str,… (+18 more)

### Community 9 - "CatalogoTiles"
Cohesion: 0.09
Nodes (22): CatalogoTiles, padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…, Componente de Formulário de Eventos do Editor de Mapas. Contém todas as telas…, balde_de_tinta() (+14 more)

### Community 10 - "Personagem"
Cohesion: 0.08
Nodes (21): Personagem, Dano direto que ignora armadura (ex: veneno)., Adiciona um efeito à lista de ativos., Roda no fim do turno: processa venenos, curas e reduz duração., Verifica se o personagem tem a Exuberância e os Pontos nos Caminhos exigidos., Tenta adicionar a magia à lista do personagem, levanta Exceção se não puder., Executa a magia conforme MANUAL.md (Teste Resistido)., Recalcula atributos E Caminhos de Magia. (+13 more)

### Community 11 - "MapaDB"
Cohesion: 0.15
Nodes (20): criar_e_salvar_mapa(), EventoDB, Base, CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., Base (+12 more)

### Community 12 - "PositionComponent"
Cohesion: 0.17
Nodes (15): NetworkPlayerComponent, PositionComponent, Como a entidade se parece na interface., Onde a entidade está no mapa lógico., Identificador para jogadores que estão conectados via rede (multiplayer)., RenderComponent, NetworkSystem, Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em… (+7 more)

### Community 13 - "test_battle_system.py"
Cohesion: 0.07
Nodes (31): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, battle_sys(), classe_guerreiro(), eventos_capturados(), heroi() (+23 more)

### Community 14 - "TestGameControllerCriacoes"
Cohesion: 0.08
Nodes (18): Deve criar uma arma com dano e tipo de ataque., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio)., Deve criar um personagem com todos os atributos válidos., Testes das funções de criação no GameController., TestGameControllerCriacoes (+10 more)

### Community 15 - "DungeonGenerator"
Cohesion: 0.08
Nodes (17): Any, Lê as configurações do RPG e aciona o gerador independente correspondente., circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo. (+9 more)

### Community 16 - "PropriedadesFormScreen"
Cohesion: 0.08
Nodes (14): GestorDeMapas, Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., ArquivoCSVScreen, MenuAcoesScreen, PropriedadesFormScreen, Pressed (+6 more)

### Community 17 - "MovementSystem"
Cohesion: 0.07
Nodes (21): PlayerControlComponent, Uma flag que indica que esta entidade é controlada pelo teclado., InteractionSystem, MovementSystem, Verifica se há um evento à frente do jogador. Se houver, publica as informações…, Sistema lógico encarregado de validar a física e colisões de movimentos., Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, build_interactable_component() (+13 more)

### Community 18 - "GameEngineLoader"
Cohesion: 0.10
Nodes (15): GameEngineLoader, Any, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos…, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo., Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem., Remove o jogador remoto do mundo atual usando o NetworkSystem. (+7 more)

### Community 19 - "MapaInterativo"
Cohesion: 0.12
Nodes (13): ComposeResult, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado., Apertou o botão do mouse: começa o traço e captura o foco., Soltou o botão do mouse: termina o traço e liberta o foco. (+5 more)

### Community 20 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 21 - "._escrever_log"
Cohesion: 0.11
Nodes (10): on, Pressed, Atualiza os valores e redesenha as barras., Atualiza a barra de HP do herói sempre que o valor reativo muda., Callback disparado pelo BattleSystem quando o combate é configurado. Inicializa…, Callback disparado pelo BattleSystem após calcular um turno. Atualiza os…, Callback disparado quando o combate termina (vitória ou derrota)., Captura a ação selecionada pelo jogador no RadioSet e o alvo no TargetRadioSet.… (+2 more)

### Community 22 - "TestObterPaginaAtiva"
Cohesion: 0.13
Nodes (14): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+6 more)

### Community 23 - "BattleSystem"
Cohesion: 0.11
Nodes (14): BattleSystem, Roteia a ação para o método correto da entidade Personagem do domínio., Encerra o combate e remove o CombatStateComponent da entidade do jogador., O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista., Configura os combatentes com deepcopy e dispara o evento de início. O deepcopy…, Retorna a lista de dicts com o estado atual de cada inimigo (para eventos). (+6 more)

### Community 24 - "ChatLog"
Cohesion: 0.10
Nodes (15): ChatLog, MensagemAnimada, App, ComposeResult, Static, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Processa a próxima mensagem da fila. (+7 more)

### Community 25 - "InventarySystem"
Cohesion: 0.12
Nodes (11): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+3 more)

### Community 26 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 27 - "routers/personagens.py"
Cohesion: 0.15
Nodes (18): get_db(), Função utilitária para abrir e fechar a conexão com o banco corretamente., get, root(), criar_personagem(), criar_raca(), listar_personagens(), listar_racas() (+10 more)

### Community 28 - "TestValidacaoEntradas"
Cohesion: 0.14
Nodes (8): Deve criar uma raça válida com todos os atributos., Verifica se todos os 5 atributos são salvos., Deve rejeitar atributos fora do intervalo 0-5., Teste edge case: atributos com tipo errado., Deve lidar com nome vazio., Deve aceitar emojis especiais., Testes de validação de entrada do usuário., TestValidacaoEntradas

### Community 29 - "Raca"
Cohesion: 0.13
Nodes (28): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais., ClasseRPG (+20 more)

### Community 30 - "GameStateManager"
Cohesion: 0.14
Nodes (9): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Testa se os seletores lógicos (Switches) persistem dinamicamente através do…, test_game_state_manager_salvamento_e_recuperacao_de_switches(), Garante que jogadores de rede não corrompam o save-game persistido. (+1 more)

### Community 31 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 32 - "ItemDB"
Cohesion: 0.14
Nodes (16): ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., classe_default(), item_arma(), item_armadura(), item_escudo(), fixture (+8 more)

### Community 33 - "PropriedadesEventoFormScreen"
Cohesion: 0.18
Nodes (6): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Serializa o estado atual dos inputs para não perder o progresso digitado., Preenche o formulário com o snapshot e injeta a nova coordenada no local exato.

### Community 34 - "ManagementMenuScreen"
Cohesion: 0.21
Nodes (5): ManagementMenuScreen, Changed, on, Redireciona para o formulário correto baseado na tabela atual., RowSelected

### Community 35 - "MapManagerScreen"
Cohesion: 0.06
Nodes (24): MapManagerScreen, Screen, Trata a resposta do utilizador no modal de confirmação., Tira uma fotografia à matriz atual antes de a alterarmos., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Gerencia os cliques na tela principal., Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form., Callback acionado ao fechar a tela de Propriedades. (+16 more)

### Community 36 - "._obter_condicoes_pagina_atual"
Cohesion: 0.23
Nodes (6): Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Callback do modal AdicionarSwitchScreen., Callback do modal AdicionarVariavelScreen., Remove um switch pelo índice da lista., Remove uma variável pelo índice da lista.

### Community 37 - "Any"
Cohesion: 0.13
Nodes (11): _extrair_stats_salvos(), Any, Adiciona os componentes comuns a todas as entidades de evento:…, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa…, NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.…, Entidades pacíficas possuem HP defensivo mas não atacam ao tocar o jogador., Entidades interativas (portas, alavancas, armadilhas) são sólidas, sem stats de…, Veículos possuem MovimentComponent com tipo especial e não atacam. (+3 more)

### Community 38 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 40 - "NovoMapaFormScreen"
Cohesion: 0.21
Nodes (7): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 41 - "AdicionarComandoScreen"
Cohesion: 0.13
Nodes (8): AdicionarComandoScreen, AdicionarSwitchScreen, AdicionarVariavelScreen, Pressed, Modal simples para adicionar uma condição de Switch a uma página., Modal simples para adicionar uma condição de Variável numérica a uma página., Sub-formulário para gerar comandos baseados no tipo selecionado., Serializa o estado atual do formulário de teleporte para não perder progresso.

### Community 42 - "on"
Cohesion: 0.31
Nodes (4): Changed, on, Sincroniza o self_switch da página atual quando o Select muda., Sincroniza o item_requerido da página atual quando o Input muda.

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

### Community 47 - ".atacar"
Cohesion: 0.31
Nodes (5): Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Realiza a mecânica completa de ataque contra um alvo.

### Community 48 - "test_esper_integration.py"
Cohesion: 0.20
Nodes (8): fixture_dados_base(), fixture_db_session(), fixture, Garante que o método e'sperado pela tela limpa o mundo e popula as entidades., Cria um banco SQLite isolado em memória para cada teste., Povoa o banco com os templates base de um cenário (Mundo do Criador)., test_deve_atribuir_status_e_inventario_ao_jogador_no_esper(), test_deve_executar_carregar_engine_do_banco_com_esper()

### Community 49 - ".criar_entidade_jogador_de_save"
Cohesion: 0.20
Nodes (4): Session, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Alterna ou inicializa o mundo do mapa alvo, sincronizando snapshots in RAM e…, Hidrata a entidade do jogador a partir de dados do SaveDB. Args: entity_id:…

### Community 50 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, ModalScreen, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 51 - "ConfirmacaoSalvarScreen"
Cohesion: 0.29
Nodes (4): ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo., Dispara quando o utilizador clica num mapa na barra lateral., NodeSelected

### Community 52 - "AISystem"
Cohesion: 0.32
Nodes (5): AISystem, Processa movimento autônomo de monstros/NPCs a cada tick., Compatibilidade legado., Garante que a nova engine carrega corretamente no novo loader., test_deve_carregar_nova_engine_com_suporte_a_processors()

### Community 53 - "TestTurnoJogador"
Cohesion: 0.25
Nodes (5): Testa a execução de ações do jogador via BattleSystem., executar_acao_jogador('ataque') deve disparar 'turno_calculado' com…, executar_acao_jogador deve ignorar quando combate_ativo=False., Quando o inimigo morre no turno do jogador, deve disparar 'combate_encerrado'., TestTurnoJogador

### Community 54 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

### Community 55 - "fixture_db_session"
Cohesion: 0.40
Nodes (5): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste., Garante isolamento absoluto limpando a memória do Esper ECS., reset_esper_antes_de_cada_teste()

### Community 58 - "TestGameControllerConversao"
Cohesion: 0.33
Nodes (4): Testes da conversão BD -> Domínio., Deve converter personagem sem equipamentos., Deve converter personagem com todos os equipamentos., TestGameControllerConversao

### Community 59 - "TestEquipamentoMainx"
Cohesion: 0.33
Nodes (4): Testes de lógica de equipamento do mainx_cli., Deve equipar itens em todos os slots sequencialmente., Deve lidar com tentativa de equipar em slot inválido., TestEquipamentoMainx

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

- **Why does `GamePlayScreen` connect `GamePlayScreen` to `Arma`, `BattleScreen`, `ItemFormScreen`, `GameController`, `StatsComponent`, `PersonagemDB`, `MapaDB`, `PositionComponent`, `test_battle_system.py`, `MovementSystem`, `GameEngineLoader`, `BattleSystem`, `ChatLog`, `InventarySystem`, `GameStateManager`, `ManagementMenuScreen`, `TestInicializacaoCombate`, `TestIAInimigo`, `AISystem`, `TestTurnoJogador`, `TestResolucaoAcoes`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `CatalogoTiles` connect `CatalogoTiles` to `PropriedadesEventoFormScreen`, `MapManagerScreen`, `NovoMapaFormScreen`, `AdicionarComandoScreen`, `RamoEditorScreen`, `PositionComponent`, `PropriedadesFormScreen`, `MovementSystem`, `SecondaryMap`, `ConfirmacaoSalvarScreen`, `AISystem`, `BattleSystem`, `InventarySystem`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `ItemDB`, `PropriedadesEventoFormScreen`, `ManagementMenuScreen`, `ItemFormScreen`, `test_editor_eventos.py`, `.carregar_arvore_de_mapas`, `PersonagemDB`, `CatalogoTiles`, `TestPropriedadesEventoFormScreen`, `MapaDB`, `PropriedadesFormScreen`, `ConfirmacaoSalvarScreen`, `MapaInterativo`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `MapManagerScreen` (e.g. with `CatalogoTiles` and `GestorDeMapas`) actually correct?**
  _`MapManagerScreen` has 19 INFERRED edges - model-reasoned connections that need verification._