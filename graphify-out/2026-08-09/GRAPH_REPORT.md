# Graph Report - rpg_api  (2026-08-09)

## Corpus Check
- 72 files · ~300,413 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1465 nodes · 3743 edges · 93 communities (76 shown, 17 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 865 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2c8af78d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StatsComponent
- InventoryComponent
- PersonagemDB
- ._animar_ataque
- MagiaDB
- Arma
- GamePlayScreen
- GameController
- MapManagerScreen
- GameEngineLoader
- TestGameControllerCriacoes
- EquipmentComponent
- CatalogoTiles
- Personagem
- DungeonGenerator
- CombatNetworkAdapter
- TestPropriedadesEventoFormScreen
- ChatLog
- .criar_entidade_evento
- fixture_db_session
- obter_pagina_ativa
- Magia
- MovementSystem
- TestMapearTipoEntidade
- routers/personagens.py
- MapaInterativo
- TestMultiplosInimigos
- SimuladorCombate
- ._executar_turno_inimigo_sincrono
- NetworkSystem
- JogoAtaqueApp
- GameStateManager
- SecondaryMap
- PropriedadesEventoFormScreen
- MapaDB
- .ao_clicar_na_arvore
- PropriedadesFormScreen
- Selected
- game_controller.py
- ManagementMenuScreen
- test_editor_eventos.py
- on
- NovoMapaFormScreen
- Raca
- restaurar_mundo_esper
- .processar_pintura
- AcaoConfirmada
- AdicionarComandoScreen
- ._escrever_log
- Any
- RamoEditorScreen
- ._obter_condicoes_pagina_atual
- VisualizadorImagem
- limpar_mundo_esper
- .exibir_mapa_na_tela
- .processar_csv
- BarraStatusCombate
- battle_screen.py
- .adicionar_evento_para_memoria
- ._calcular_posicoes_inimigos
- ._fechar_tela_combate
- RPGApp
- .carregar_arvore_de_mapas
- CombatenteSprite
- AcoesComandoScreen
- on
- .inimigo
- .process
- .ao_selecionar_opcao_evento
- .test_iniciar_combate_dispara_evento
- .test_iniciativa_considera_agilidade
- .__init__
- TestIAInimigo
- .test_resolver_ataque_retorna_resultado_valido
- .test_resolver_cura_retorna_sem_dano
- .processar_comando_terminal
- .atualizar_tela
- .on_unmount
- .watch_turno_liberado
- .test_iniciar_combate_ativa_flag_combate_ativo
- .test_acao_invalida_sem_combate_ativo
- .test_resolver_acao_invalida_usa_ataque_fallback
- .test_encerrar_combate_desativa_flag

## God Nodes (most connected - your core abstractions)
1. `GameController` - 93 edges
2. `Personagem` - 82 edges
3. `InventoryComponent` - 76 edges
4. `GamePlayScreen` - 75 edges
5. `StatsComponent` - 70 edges
6. `PersonagemDB` - 63 edges
7. `MapManagerScreen` - 63 edges
8. `Raca` - 62 edges
9. `ClasseRPG` - 61 edges
10. `ItemDB` - 60 edges

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

## Communities (93 total, 17 thin omitted)

### Community 0 - "StatsComponent"
Cohesion: 0.06
Nodes (55): BattleParticipantComponent, CombatStateComponent, HeroComponent, NetworkPlayerComponent, Guarda a referência para a instância Personagem do domínio para o jogador., Guarda os atributos de combate e informações vitais do personagem., Identificador para jogadores que estão conectados via rede (multiplayer)., Marca uma entidade como estando em combate ativo e armazena metadados do turno.… (+47 more)

### Community 1 - "InventoryComponent"
Cohesion: 0.09
Nodes (40): InventoryComponent, Armazena os itens que o personagem está carregando., aplicar_desequipar_item(), aplicar_equipar_item(), aplicar_usar_item(), _eh_equipamento(), garantir_itens_padrao(), inv_adicionar_item() (+32 more)

### Community 2 - "PersonagemDB"
Cohesion: 0.07
Nodes (53): simular_arena(), ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., ClasseRPGDB, PersonagemDB, Base, RacaDB (+45 more)

### Community 3 - "._animar_ataque"
Cohesion: 0.29
Nodes (4): Anima o sprite do atacante avançando sobre o alvo e recuando, ou lança projétil…, Remove o projétil e dispara o flash de impacto e o recuo do conjurador., Efeito visual de impacto: flash piscante na tela + emoji 💥 na arena + recuo do…, Faz a tela piscar 3x com a classe CSS de cor de impacto (efeito dramático…

### Community 4 - "MagiaDB"
Cohesion: 0.07
Nodes (24): EfeitoDB, MagiaDB, Base, Tabela que armazena os metadados de Magias e Habilidades., Tabela que armazena os Efeitos Temporários (condições)., ArenaScreen, CharacterFormScreen, ClasseFormScreen (+16 more)

### Community 5 - "Arma"
Cohesion: 0.13
Nodes (17): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+9 more)

### Community 6 - "GamePlayScreen"
Cohesion: 0.15
Nodes (9): GamePlayScreen, Screen, Limpa as escutas de eventos do Esper ao fechar a tela., O ponteiro central de transição. Recebe: {"mapa_id": 3, "pos_x": 15, "pos_y":…, Injeta mensagens formatadas no painel lateral de logs., Processador de Eventos Universal - Pipeline de 4 Etapas., Handler disparado pelo EventSystem quando o comando 'iniciar_combate' é…, Chamado quando a tela de batalha é fechada e voltamos ao GamePlayScreen. (+1 more)

### Community 7 - "GameController"
Cohesion: 0.05
Nodes (27): GameController, Session, Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda., Deve equipar uma armadura no corpo. (+19 more)

### Community 8 - "MapManagerScreen"
Cohesion: 0.13
Nodes (10): MapManagerScreen, Screen, Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Transforma as chaves de tupla (1, 2) em texto '1,2' para poder salvar no Banco., Transforma o dicionário de memória numa lista pronta para o SQLAlchemy., TabActivated, Garante que tuplas matemáticas viram strings JSON., Garante que strings JSON voltam a ser tuplas matemáticas. (+2 more)

### Community 9 - "GameEngineLoader"
Cohesion: 0.07
Nodes (24): GameEngineLoader, Any, Session, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos…, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo. (+16 more)

### Community 10 - "TestGameControllerCriacoes"
Cohesion: 0.06
Nodes (18): Deve criar uma arma com dano e tipo de ataque., Deve criar uma raça válida com todos os atributos., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Verifica se todos os 5 atributos são salvos., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio)., Deve criar um personagem com todos os atributos válidos. (+10 more)

### Community 11 - "EquipmentComponent"
Cohesion: 0.13
Nodes (42): ActiveEffectsComponent, CollisionComponent, EquipmentComponent, InteractableComponent, MovimentComponent, PositionComponent, Dataclass pura que armazena e monitora em tempo de execução os efeitos…, Como a entidade se parece na interface. (+34 more)

### Community 12 - "CatalogoTiles"
Cohesion: 0.09
Nodes (20): CatalogoTiles, padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…, AdicionarSwitchScreen, AdicionarVariavelScreen (+12 more)

### Community 13 - "Personagem"
Cohesion: 0.11
Nodes (14): Personagem, Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Dano direto que ignora armadura (ex: veneno)., Realiza a mecânica completa de ataque contra um alvo., Adiciona um efeito à lista de ativos. (+6 more)

### Community 14 - "DungeonGenerator"
Cohesion: 0.08
Nodes (17): Any, Lê as configurações do RPG e aciona o gerador independente correspondente., circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo. (+9 more)

### Community 15 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 16 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 17 - "ChatLog"
Cohesion: 0.10
Nodes (15): ChatLog, MensagemAnimada, App, ComposeResult, Static, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Processa a próxima mensagem da fila. (+7 more)

### Community 18 - ".criar_entidade_evento"
Cohesion: 0.12
Nodes (7): _extrair_stats_salvos(), Ponto de entrada principal para criação de entidades de evento. Determina o…, Entidades interativas (portas, alavancas, armadilhas) são sólidas, sem stats de…, Extrai o dicionário de StatsComponent de dados_salvos do SaveDB., _criar_entidade_vazia(), Verifica que a correção do bug IndexError está funcionando., Cria uma entidade em branco no esper e retorna seu ID.

### Community 19 - "fixture_db_session"
Cohesion: 0.40
Nodes (5): fixture_db_session(), fixture, Cria um banco SQLite isolado em memória para cada teste., Garante isolamento absoluto limpando a memória do Esper ECS., reset_esper_antes_de_cada_teste()

### Community 20 - "obter_pagina_ativa"
Cohesion: 0.07
Nodes (16): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+8 more)

### Community 21 - "Magia"
Cohesion: 0.12
Nodes (18): Efeito, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa um encanto dos Caminhos Elementais ou Habilidade Mágica., Testa que os efeitos temporários de magias (ex: veneno/dano contínuo) são…, Testa que magias com buffs de atributos são aplicadas ao próprio conjurador e…, Testa que ao expirar o efeito de buff, os atributos retornam ao normal sem… (+10 more)

### Community 22 - "MovementSystem"
Cohesion: 0.08
Nodes (20): PlayerControlComponent, Uma flag que indica que esta entidade é controlada pelo teclado., MovementSystem, Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, Verifica se há um evento à frente do jogador. Se houver, publica as informações…, Sistema lógico encarregado de validar a física e colisões de movimentos., build_interactable_component(), create_player_control() (+12 more)

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
Cohesion: 0.10
Nodes (16): classe_guerreiro(), eventos_capturados(), heroi(), inimigo(), fixture, raca_humana(), Testa o suporte a 1-4 inimigos no BattleSystem., Segundo inimigo para testes de grupo. (+8 more)

### Community 27 - "SimuladorCombate"
Cohesion: 0.19
Nodes (8): Interpretador genérico e atômico de comandos estruturados do JSON., Any, Corre X batalhas em silêncio e agrupa todas as estatísticas num mega relatório., Gere as simulações de batalhas em grupo e recolhe estatísticas., Calcula a ordem de combate baseada em 1d6 + Agilidade., Filtra apenas os combatentes que ainda têm Pontos de Vida., Executa uma única batalha até uma equipa ser derrotada. Devolve um relatório de…, SimuladorCombate

### Community 28 - "._executar_turno_inimigo_sincrono"
Cohesion: 0.14
Nodes (9): Cria a corrotina do turno do inimigo no event loop ativo., Calcula o turno da IA do inimigo sem bloquear o event loop do Textual. O delay…, Núcleo de execução do turno de todos os inimigos vivos (IA simples)., IA simples para o primeiro inimigo da lista (alias de retrocompatibilidade).…, IA simples mas funcional para um inimigo específico: - Se tem mana e magias,…, Roteia a ação para o método correto da entidade Personagem do domínio., Encerra o combate e remove o CombatStateComponent da entidade do jogador., Retorna a lista de dicts com o estado atual de cada inimigo (para eventos). (+1 more)

### Community 29 - "NetworkSystem"
Cohesion: 0.12
Nodes (8): NetworkSystem, Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em…, Sistema responsável por sincronizar o estado de outros jogadores conectados…, RenderSystem, Testa se o Z-Index do RenderSystem respeita a ordem de prioridades: 1°…, Garante que se não houver entidade no local, o objeto estático seja desenhado., test_deve_renderizar_objeto_se_nao_houver_entidade(), test_renderizacao_camadas_e_prioridade()

### Community 30 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 31 - "GameStateManager"
Cohesion: 0.13
Nodes (9): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Testa se os seletores lógicos (Switches) persistem dinamicamente através do…, test_game_state_manager_salvamento_e_recuperacao_de_switches(), Garante que jogadores de rede não corrompam o save-game persistido. (+1 more)

### Community 32 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, ModalScreen, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 33 - "PropriedadesEventoFormScreen"
Cohesion: 0.18
Nodes (6): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Serializa o estado atual dos inputs para não perder o progresso digitado., Preenche o formulário com o snapshot e injeta a nova coordenada no local exato.

### Community 34 - "MapaDB"
Cohesion: 0.12
Nodes (27): criar_e_salvar_mapa(), EventoDB, Base, CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., Base (+19 more)

### Community 35 - ".ao_clicar_na_arvore"
Cohesion: 0.25
Nodes (4): Dispara quando o utilizador clica num mapa na barra lateral., Trata a resposta do utilizador no modal de confirmação., Transforma o texto '1,2' do Banco de volta em tupla matemática (1, 2)., NodeSelected

### Community 36 - "PropriedadesFormScreen"
Cohesion: 0.06
Nodes (18): GestorDeMapas, Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., ArquivoCSVScreen, ConfirmacaoSalvarScreen, MenuAcoesScreen, PropriedadesFormScreen (+10 more)

### Community 37 - "Selected"
Cohesion: 0.13
Nodes (11): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+3 more)

### Community 38 - "game_controller.py"
Cohesion: 0.21
Nodes (8): Habilidade, Representa perícias ou golpes físicos especiais., criar_lutadores(), Testa se uma batalha decorre corretamente e se o vencedor é identificado., Garante que a recolha estatística após 10 batalhas soma os valores corretamente., Função utilitária para gerar lutadores para o teste., test_multiplas_simulacoes(), test_simulacao_unica()

### Community 39 - "ManagementMenuScreen"
Cohesion: 0.21
Nodes (5): ManagementMenuScreen, Changed, on, Redireciona para o formulário correto baseado na tabela atual., RowSelected

### Community 40 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 41 - "on"
Cohesion: 0.38
Nodes (3): Highlighted, on, Pressed

### Community 42 - "NovoMapaFormScreen"
Cohesion: 0.21
Nodes (6): NovoMapaFormScreen, Changed, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 43 - "Raca"
Cohesion: 0.14
Nodes (22): ClasseRPG, Raca, Mapper: dados do JSON do evento → objeto Personagem do domínio. Segue o padrão…, fixture, setup_world(), test_aprender_magia_evento_sucesso_e_falha(), test_aprender_magia_com_excecao(), test_batalha_usar_item_especifico() (+14 more)

### Community 44 - "restaurar_mundo_esper"
Cohesion: 0.67
Nodes (3): fixture, Garante o isolamento completo entre os testes limpando completamente todas as…, restaurar_mundo_esper()

### Community 45 - ".processar_pintura"
Cohesion: 0.24
Nodes (5): on, Tira uma fotografia à matriz atual antes de a alterarmos., Callback acionado ao fechar a tela de Propriedades., Callback acionado quando o usuário confirma os dados do evento no Modal., Monta o formulário de volta injetando a nova coordenada no escopo correto.

### Community 46 - "AcaoConfirmada"
Cohesion: 0.40
Nodes (4): AcaoConfirmada, Message, Widget, Mensagem interna emitida quando o jogador confirma sua ação. Segue o padrão da…

### Community 47 - "AdicionarComandoScreen"
Cohesion: 0.21
Nodes (4): AdicionarComandoScreen, Pressed, Sub-formulário para gerar comandos baseados no tipo selecionado., Serializa o estado atual do formulário de teleporte para não perder progresso.

### Community 48 - "._escrever_log"
Cohesion: 0.22
Nodes (5): Registra handlers do Esper, posiciona sprites e inicia o combate via…, Callback disparado pelo BattleSystem quando o combate é configurado. Inicializa…, Callback disparado pelo BattleSystem após calcular um turno. Atualiza os…, Escreve uma linha formatada no log de batalha., Formata e escreve o relatório narrativo de um turno no log.

### Community 49 - "Any"
Cohesion: 0.21
Nodes (7): Any, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa…, NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.…, Entidades pacíficas possuem HP defensivo mas não atacam ao tocar o jogador., Veículos possuem MovimentComponent com tipo especial e não atacam., Decorações de cenário podem ser atravessáveis (ex: vegetação baixa) ou sólidas…, Lê os dados de movimento da página ativa e adiciona o MovimentComponent.

### Community 51 - "._obter_condicoes_pagina_atual"
Cohesion: 0.22
Nodes (6): Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Callback do modal AdicionarSwitchScreen., Callback do modal AdicionarVariavelScreen., Remove um switch pelo índice da lista., Remove uma variável pelo índice da lista.

### Community 52 - "VisualizadorImagem"
Cohesion: 0.40
Nodes (3): App, ComposeResult, VisualizadorImagem

### Community 53 - "limpar_mundo_esper"
Cohesion: 0.67
Nodes (3): limpar_mundo_esper(), fixture, Garante isolamento total entre testes: reinicia o esper antes de cada um.

### Community 55 - ".exibir_mapa_na_tela"
Cohesion: 0.20
Nodes (4): Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form., Retrocede a matriz para o último estado guardado., Avança Terrenos e Objetos para o estado do futuro., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo).

### Community 65 - ".processar_csv"
Cohesion: 0.25
Nodes (4): Callback após o utilizador clicar em algo no Menu Principal., Redireciona para importar ou exportar com base no nome do ficheiro., Transforma a matriz atual em texto com vírgulas e guarda no disco., Lê um ficheiro CSV do disco e transforma numa matriz para o nosso programa.

### Community 66 - "BarraStatusCombate"
Cohesion: 0.22
Nodes (4): BarraStatusCombate, Atualiza os valores e redesenha as barras., Atualiza a barra de HP do herói sempre que o valor reativo muda., Widget composto de barra de status (nome + HP bar + MP bar) para um combatente.…

### Community 67 - "battle_screen.py"
Cohesion: 0.17
Nodes (8): EfeitoAtaque, Tela de Combate por Turnos — BattleScreen Interface TUI do sistema de combate…, Emoji de impacto que aparece brevemente na arena durante o ataque. Criado…, Cria um EfeitoAtaque dinâmico na arena e o remove após 0.5s. Posiciona o emoji…, Remove o widget de efeito de forma segura., Captura a ação selecionada pelo jogador no RadioSet e o alvo no TargetRadioSet.…, Modal de seleção de item usável durante a batalha., UsarItemBatalhaModal

### Community 69 - "._calcular_posicoes_inimigos"
Cohesion: 0.33
Nodes (3): Posiciona os sprites de inimigos de forma distribuída na arena antes da…, Calcula as posições X finais de N inimigos distribuídos na metade direita da…, Sprites entram animados a partir das bordas da arena.

### Community 70 - "._fechar_tela_combate"
Cohesion: 0.33
Nodes (3): Callback disparado quando o combate termina (vitória ou derrota)., Encerra a tela de combate e devolve o controle à tela principal., Sincroniza o status atual (HP/Mana) e equipamentos do herói da batalha de volta…

### Community 71 - "RPGApp"
Cohesion: 0.40
Nodes (3): action_start_stop_music(), App, RPGApp

### Community 73 - "CombatenteSprite"
Cohesion: 0.25
Nodes (4): CombatenteSprite, Static, Widget de sprite do combatente com posição X animável via reactive. Seguindo o…, Sempre que x_pos mudar (via animação), atualiza o offset visual do sprite.

### Community 74 - "AcoesComandoScreen"
Cohesion: 0.20
Nodes (3): AcoesComandoScreen, Menu contextual ao clicar num comando da lista., Modo_de_Captura

### Community 75 - "on"
Cohesion: 0.31
Nodes (4): Changed, on, Sincroniza o self_switch da página atual quando o Select muda., Sincroniza o item_requerido da página atual quando o Input muda.

### Community 78 - ".ao_selecionar_opcao_evento"
Cohesion: 0.33
Nodes (3): Chamado pelo interpretador de comandos quando atinge uma bifurcação. Instancia…, Remove o widget da tela de forma limpa., Nativo do Textual. Captura o sinal emitido pelo ChoiceBox assim que o jogador…

### Community 82 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

### Community 85 - ".processar_comando_terminal"
Cohesion: 0.50
Nodes (3): on, Submitted, Processa a caixa de comandos rápidos de texto.

## Knowledge Gaps
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameController` connect `GameController` to `StatsComponent`, `PersonagemDB`, `MapaDB`, `MagiaDB`, `Arma`, `game_controller.py`, `PropriedadesFormScreen`, `GamePlayScreen`, `GameEngineLoader`, `TestGameControllerCriacoes`, `Raca`, `ManagementMenuScreen`, `Personagem`, `RPGApp`, `Magia`, `MovementSystem`, `SimuladorCombate`, `NetworkSystem`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `.processar_csv`, `PersonagemDB`, `MapaDB`, `PropriedadesFormScreen`, `.adicionar_evento_para_memoria`, `.ao_clicar_na_arvore`, `PropriedadesEventoFormScreen`, `.carregar_arvore_de_mapas`, `MagiaDB`, `ManagementMenuScreen`, `RPGApp`, `CatalogoTiles`, `.processar_pintura`, `test_editor_eventos.py`, `TestPropriedadesEventoFormScreen`, `.exibir_mapa_na_tela`, `MapaInterativo`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `GamePlayScreen` connect `GamePlayScreen` to `StatsComponent`, `InventoryComponent`, `PersonagemDB`, `MagiaDB`, `Arma`, `GameController`, `GameEngineLoader`, `EquipmentComponent`, `ChatLog`, `MovementSystem`, `TestMultiplosInimigos`, `NetworkSystem`, `GameStateManager`, `MapaDB`, `Selected`, `ManagementMenuScreen`, `RPGApp`, `.ao_selecionar_opcao_evento`, `TestIAInimigo`, `.processar_comando_terminal`, `.atualizar_tela`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 50 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `InventoryComponent` (e.g. with `GameEngineLoader` and `EntityFactory`) actually correct?**
  _`InventoryComponent` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 46 INFERRED edges - model-reasoned connections that need verification._