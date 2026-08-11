# Graph Report - rpg_api  (2026-08-09)

## Corpus Check
- 72 files · ~300,805 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1470 nodes · 3765 edges · 73 communities (71 shown, 2 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 876 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c8af78d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BattleSystem
- InventoryComponent
- PersonagemDB
- BattleScreen
- main_cli.py
- Arma
- GamePlayScreen
- GameController
- EventoDB
- .carregar_engine_do_banco
- TestGameControllerCriacoes
- CollisionComponent
- CatalogoTiles
- Personagem
- DungeonGenerator
- CombatNetworkAdapter
- TestPropriedadesEventoFormScreen
- ChatLog
- EntityFactory
- fixture_db_session
- systems.py
- Magia
- PositionComponent
- TestMapearTipoEntidade
- routers/personagens.py
- MapaInterativo
- TestMultiplosInimigos
- EventSystem
- StatsComponent
- RenderComponent
- JogoAtaqueApp
- GameStateManager
- SecondaryMap
- PropriedadesEventoFormScreen
- ItemDB
- GestorDeMapas
- PropriedadesFormScreen
- Selected
- MockMapLoader
- ManagementMenuScreen
- MensagemAnimada
- simular_arena
- NovoMapaFormScreen
- Raca
- restaurar_mundo_esper
- .log_mensagem
- fixture_db_session
- AdicionarComandoScreen
- setup_esper
- fixture_db_session
- RamoEditorScreen
- ._obter_condicoes_pagina_atual
- VisualizadorImagem
- limpar_mundo_esper
- MapManagerScreen
- ArquivoCSVScreen
- BarraStatusCombate
- RPGApp
- AcoesComandoScreen
- on
- .ao_enviar_comando_chat
- TestInicializacaoCombate
- TestIAInimigo

## God Nodes (most connected - your core abstractions)
1. `GameController` - 94 edges
2. `Personagem` - 82 edges
3. `InventoryComponent` - 76 edges
4. `GamePlayScreen` - 75 edges
5. `StatsComponent` - 70 edges
6. `PersonagemDB` - 64 edges
7. `MapManagerScreen` - 63 edges
8. `Raca` - 62 edges
9. `ClasseRPG` - 61 edges
10. `ItemDB` - 61 edges

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

## Communities (73 total, 2 thin omitted)

### Community 0 - "BattleSystem"
Cohesion: 0.05
Nodes (42): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, BattleSystem, O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista. (+34 more)

### Community 1 - "InventoryComponent"
Cohesion: 0.06
Nodes (51): InventoryComponent, Armazena os itens que o personagem está carregando., aplicar_desequipar_item(), aplicar_equipar_item(), aplicar_usar_item(), _eh_equipamento(), garantir_itens_padrao(), inv_adicionar_item() (+43 more)

### Community 2 - "PersonagemDB"
Cohesion: 0.09
Nodes (44): MagiaDB, Tabela que armazena os metadados de Magias e Habilidades., ClasseRPGDB, PersonagemDB, Base, RacaDB, Tabela que armazena as Classes/Profissões do jogo. Args: nome: str,…, Tabela central que armazena os Personagens dos jogadores. (+36 more)

### Community 3 - "BattleScreen"
Cohesion: 0.07
Nodes (21): AcaoConfirmada, BattleScreen, CombatenteSprite, Message, Screen, Tela de combate por turnos — suporta 1 a 4 inimigos. - Esta tela APENAS escuta…, Mensagem interna emitida quando o jogador confirma sua ação. Segue o padrão da…, Registra handlers do Esper, posiciona sprites e inicia o combate via… (+13 more)

### Community 4 - "main_cli.py"
Cohesion: 0.07
Nodes (21): EfeitoDB, Base, Tabela que armazena os Efeitos Temporários (condições)., ArenaScreen, CharacterFormScreen, ClasseFormScreen, CreationScreen, EquipScreen (+13 more)

### Community 5 - "Arma"
Cohesion: 0.08
Nodes (30): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+22 more)

### Community 6 - "GamePlayScreen"
Cohesion: 0.17
Nodes (7): GamePlayScreen, Screen, Limpa as escutas de eventos do Esper ao fechar a tela., Processador de Eventos Universal - Pipeline de 4 Etapas., Compila o frame atual do Esper e atualiza o Canvas Único na tela., Busca a posição do jogador no Esper e move o viewport do ScrollableContainer., Chamado quando a tela de batalha é fechada e voltamos ao GamePlayScreen.

### Community 7 - "GameController"
Cohesion: 0.05
Nodes (24): GameController, Session, Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda., Deve equipar uma armadura no corpo. (+16 more)

### Community 8 - "EventoDB"
Cohesion: 0.22
Nodes (5): EventoDB, Base, Salva o mapa atual, os objetos estáticos e os eventos dinâmicos no banco de…, Transforma as chaves de tupla (1, 2) em texto '1,2' para poder salvar no Banco., Transforma o dicionário de memória numa lista pronta para o SQLAlchemy.

### Community 9 - ".carregar_engine_do_banco"
Cohesion: 0.11
Nodes (10): Any, Session, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo., Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem., Remove o jogador remoto do mundo atual usando o NetworkSystem. (+2 more)

### Community 10 - "TestGameControllerCriacoes"
Cohesion: 0.06
Nodes (19): Deve criar uma arma com dano e tipo de ataque., Deve criar uma raça válida com todos os atributos., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Deve listar todas as raças cadastradas., Verifica se todos os 5 atributos são salvos., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio). (+11 more)

### Community 11 - "CollisionComponent"
Cohesion: 0.15
Nodes (19): CollisionComponent, InteractableComponent, MovimentComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., entity_factory.py Fábrica de Entidades ECS (EntityFactory). Centraliza toda a…, Hidrata a entidade do jogador a partir de dados do SaveDB. Args: entity_id:…, Tipos canônicos de entidade reconhecidos pelo motor de jogo., TipoEntidade (+11 more)

### Community 12 - "CatalogoTiles"
Cohesion: 0.07
Nodes (26): CatalogoTiles, padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…, AdicionarSwitchScreen, AdicionarVariavelScreen (+18 more)

### Community 13 - "Personagem"
Cohesion: 0.11
Nodes (14): Personagem, Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Dano direto que ignora armadura (ex: veneno)., Realiza a mecânica completa de ataque contra um alvo., Adiciona um efeito à lista de ativos. (+6 more)

### Community 14 - "DungeonGenerator"
Cohesion: 0.09
Nodes (15): circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo., Verifica se este círculo se sobrepõe a outro., Gerador Procedimental Puro. Totalmente agnóstico: não possui dependências de… (+7 more)

### Community 15 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 16 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.05
Nodes (28): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados. (+20 more)

### Community 17 - "ChatLog"
Cohesion: 0.14
Nodes (9): ChatLog, App, ComposeResult, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Captura o comando enviado pelo jogador e joga no nosso ChatLog., Widget customizado que se comporta como uma área de log com suporte a animações…, TestApp (+1 more)

### Community 18 - "EntityFactory"
Cohesion: 0.07
Nodes (27): EntityFactory, _extrair_stats_salvos(), Any, Cria e hidrata entidades no esper de forma centralizada e tipada. Todos os…, Ponto de entrada principal para criação de entidades de evento. Determina o…, Hidrata a entidade do jogador a partir de um objeto de domínio (novo jogo).…, Adiciona os componentes comuns a todas as entidades de evento:…, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa… (+19 more)

### Community 19 - "fixture_db_session"
Cohesion: 0.40
Nodes (5): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste., Garante isolamento absoluto limpando a memória do Esper ECS., reset_esper_antes_de_cada_teste()

### Community 20 - "systems.py"
Cohesion: 0.13
Nodes (14): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+6 more)

### Community 21 - "Magia"
Cohesion: 0.09
Nodes (25): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais ou Habilidade Mágica., Testa a integração do inventário e status dos jogadores no combate. (+17 more)

### Community 22 - "PositionComponent"
Cohesion: 0.08
Nodes (28): HeroComponent, PlayerControlComponent, PositionComponent, Guarda a referência para a instância Personagem do domínio para o jogador., Uma flag que indica que esta entidade é controlada pelo teclado., Onde a entidade está no mapa lógico., AISystem, InteractionSystem (+20 more)

### Community 23 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 24 - "routers/personagens.py"
Cohesion: 0.15
Nodes (18): get_db(), Função utilitária para abrir e fechar a conexão com o banco corretamente., get, root(), criar_personagem(), criar_raca(), listar_personagens(), listar_racas() (+10 more)

### Community 25 - "MapaInterativo"
Cohesion: 0.12
Nodes (13): ComposeResult, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado., Apertou o botão do mouse: começa o traço e captura o foco., Soltou o botão do mouse: termina o traço e liberta o foco. (+5 more)

### Community 26 - "TestMultiplosInimigos"
Cohesion: 0.17
Nodes (7): Testa o suporte a 1-4 inimigos no BattleSystem., Segundo inimigo para testes de grupo., BattleSystem deve aceitar lista de 2 inimigos., _snapshot_inimigos deve retornar lista com hp, hp_max, vivo e index., O evento turno_calculado deve incluir o campo 'inimigos' com snapshot completo., Todos os inimigos com HP 0 deve encerrar com vitória do jogador., TestMultiplosInimigos

### Community 27 - "EventSystem"
Cohesion: 0.11
Nodes (12): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+4 more)

### Community 28 - "StatsComponent"
Cohesion: 0.11
Nodes (27): ActiveEffectsComponent, EquipmentComponent, NetworkPlayerComponent, Dataclass pura que armazena e monitora em tempo de execução os efeitos…, Guarda os atributos de combate e informações vitais do personagem., Armazena o que está atualmente equipado no herói influenciando seus atributos., Identificador para jogadores que estão conectados via rede (multiplayer)., StatsComponent (+19 more)

### Community 29 - "RenderComponent"
Cohesion: 0.31
Nodes (8): Como a entidade se parece na interface., RenderComponent, Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em…, RenderSystem, Testa se o Z-Index do RenderSystem respeita a ordem de prioridades: 1°…, Garante que se não houver entidade no local, o objeto estático seja desenhado., test_deve_renderizar_objeto_se_nao_houver_entidade(), test_renderizacao_camadas_e_prioridade()

### Community 30 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 31 - "GameStateManager"
Cohesion: 0.15
Nodes (7): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Testa se os seletores lógicos (Switches) persistem dinamicamente através do…, test_game_state_manager_salvamento_e_recuperacao_de_switches()

### Community 32 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, ModalScreen, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 33 - "PropriedadesEventoFormScreen"
Cohesion: 0.18
Nodes (6): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Serializa o estado atual dos inputs para não perder o progresso digitado., Preenche o formulário com o snapshot e injeta a nova coordenada no local exato.

### Community 34 - "ItemDB"
Cohesion: 0.09
Nodes (29): criar_e_salvar_mapa(), ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário. (+21 more)

### Community 35 - "GestorDeMapas"
Cohesion: 0.12
Nodes (10): GestorDeMapas, Any, Lê as configurações do RPG e aciona o gerador independente correspondente., Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo. (+2 more)

### Community 36 - "PropriedadesFormScreen"
Cohesion: 0.13
Nodes (8): MenuAcoesScreen, PropriedadesFormScreen, Pressed, Tela flutuante para editar as propriedades de um mapa que já está na memória., Ao abrir, carrega os mapas do banco para o Select de Mapa Pai., Coleta o texto atual digitado nos campos para não perder o progresso., Tela de menu acionada pelo botão 'Menu' no topo., Gerencia os cliques na tela principal.

### Community 37 - "Selected"
Cohesion: 0.16
Nodes (9): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+1 more)

### Community 39 - "ManagementMenuScreen"
Cohesion: 0.29
Nodes (3): ManagementMenuScreen, Changed, on

### Community 40 - "MensagemAnimada"
Cohesion: 0.27
Nodes (6): MensagemAnimada, Static, Processa a próxima mensagem da fila., Widget interno que gerencia a animação de uma única mensagem., Notificado quando uma mensagem termina de ser impressa., Avança um frame da animação a cada tique do timer.

### Community 41 - "simular_arena"
Cohesion: 0.25
Nodes (4): simular_arena(), Deve simular uma única batalha., Deve simular múltiplas batalhas e retornar estatísticas., Deve simular batalha com múltiplos personagens em cada equipe.

### Community 42 - "NovoMapaFormScreen"
Cohesion: 0.14
Nodes (9): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Captura os cliques dos botões., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.… (+1 more)

### Community 43 - "Raca"
Cohesion: 0.12
Nodes (25): ClasseRPG, Raca, EfeitoAtaque, Tela de Combate por Turnos — BattleScreen Interface TUI do sistema de combate…, Emoji de impacto que aparece brevemente na arena durante o ataque. Criado…, Mapper: dados do JSON do evento → objeto Personagem do domínio. Segue o padrão…, fixture, setup_world() (+17 more)

### Community 44 - "restaurar_mundo_esper"
Cohesion: 0.67
Nodes (3): fixture, Garante o isolamento completo entre os testes limpando completamente todas as…, restaurar_mundo_esper()

### Community 45 - ".log_mensagem"
Cohesion: 0.33
Nodes (3): Injeta mensagens formatadas no painel lateral de logs., Handler disparado pelo EventSystem quando o comando 'iniciar_combate' é…, Key

### Community 46 - "fixture_db_session"
Cohesion: 0.67
Nodes (3): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste.

### Community 47 - "AdicionarComandoScreen"
Cohesion: 0.24
Nodes (4): AdicionarComandoScreen, Pressed, Sub-formulário para gerar comandos baseados no tipo selecionado., Serializa o estado atual do formulário de teleporte para não perder progresso.

### Community 48 - "setup_esper"
Cohesion: 0.67
Nodes (3): fixture, Reseta o mundo global do Esper antes de cada teste., setup_esper()

### Community 49 - "fixture_db_session"
Cohesion: 0.67
Nodes (3): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste.

### Community 51 - "._obter_condicoes_pagina_atual"
Cohesion: 0.22
Nodes (6): Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Callback do modal AdicionarSwitchScreen., Callback do modal AdicionarVariavelScreen., Remove um switch pelo índice da lista., Remove uma variável pelo índice da lista.

### Community 52 - "VisualizadorImagem"
Cohesion: 0.40
Nodes (3): App, ComposeResult, VisualizadorImagem

### Community 53 - "limpar_mundo_esper"
Cohesion: 0.67
Nodes (3): limpar_mundo_esper(), fixture, Garante isolamento total entre testes: reinicia o esper antes de cada um.

### Community 55 - "MapManagerScreen"
Cohesion: 0.09
Nodes (18): MapManagerScreen, Screen, Executa automaticamente quando o Gerenciador de Mapas abre., Busca os mapas no banco e monta a estrutura de árvore visual., Trata a resposta do utilizador no modal de confirmação., Tira uma fotografia à matriz atual antes de a alterarmos., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form. (+10 more)

### Community 65 - "ArquivoCSVScreen"
Cohesion: 0.17
Nodes (5): ArquivoCSVScreen, Pede ao utilizador o caminho/nome do ficheiro CSV., Callback após o utilizador clicar em algo no Menu Principal., Redireciona para importar ou exportar com base no nome do ficheiro., Transforma a matriz atual em texto com vírgulas e guarda no disco.

### Community 66 - "BarraStatusCombate"
Cohesion: 0.06
Nodes (19): BarraStatusCombate, Any, Highlighted, on, Pressed, Widget, Atualiza os valores e redesenha as barras., Atualiza a barra de HP do herói sempre que o valor reativo muda. (+11 more)

### Community 71 - "RPGApp"
Cohesion: 0.40
Nodes (3): action_start_stop_music(), App, RPGApp

### Community 74 - "AcoesComandoScreen"
Cohesion: 0.20
Nodes (3): AcoesComandoScreen, Menu contextual ao clicar num comando da lista., Modo_de_Captura

### Community 75 - "on"
Cohesion: 0.31
Nodes (4): Changed, on, Sincroniza o self_switch da página atual quando o Select muda., Sincroniza o item_requerido da página atual quando o Input muda.

### Community 78 - ".ao_enviar_comando_chat"
Cohesion: 0.20
Nodes (6): on, Submitted, Chamado pelo interpretador de comandos quando atinge uma bifurcação. Instancia…, Remove o widget da tela de forma limpa., Nativo do Textual. Captura o sinal emitido pelo ChoiceBox assim que o jogador…, Processa a caixa de comandos rápidos de texto.

### Community 79 - "TestInicializacaoCombate"
Cohesion: 0.20
Nodes (6): Testa o setup do combate via BattleSystem.iniciar_combate., Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.…, BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar., battle_sys.combate_ativo deve ser True após iniciar., Regra 5: Iniciativa = 1d6 + Agilidade. Com d6 fixo em 1, o personagem com maior…, TestInicializacaoCombate

### Community 82 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameController` connect `GameController` to `BattleSystem`, `PersonagemDB`, `main_cli.py`, `Arma`, `GamePlayScreen`, `TestGameControllerCriacoes`, `Personagem`, `systems.py`, `Magia`, `PositionComponent`, `EventSystem`, `StatsComponent`, `RenderComponent`, `ItemDB`, `GestorDeMapas`, `ManagementMenuScreen`, `simular_arena`, `Raca`, `RPGApp`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `ArquivoCSVScreen`, `ItemDB`, `GestorDeMapas`, `PropriedadesFormScreen`, `PropriedadesEventoFormScreen`, `main_cli.py`, `ManagementMenuScreen`, `EventoDB`, `RPGApp`, `NovoMapaFormScreen`, `CatalogoTiles`, `TestPropriedadesEventoFormScreen`, `MapaInterativo`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `GamePlayScreen` connect `GamePlayScreen` to `BattleSystem`, `InventoryComponent`, `PersonagemDB`, `BattleScreen`, `main_cli.py`, `Arma`, `GameController`, `ChatLog`, `Magia`, `PositionComponent`, `TestMultiplosInimigos`, `EventSystem`, `StatsComponent`, `RenderComponent`, `GameStateManager`, `ItemDB`, `Selected`, `ManagementMenuScreen`, `.log_mensagem`, `RPGApp`, `.ao_enviar_comando_chat`, `TestInicializacaoCombate`, `TestIAInimigo`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `InventoryComponent` (e.g. with `GameEngineLoader` and `EntityFactory`) actually correct?**
  _`InventoryComponent` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 46 INFERRED edges - model-reasoned connections that need verification._