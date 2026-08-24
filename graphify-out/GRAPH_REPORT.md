# Graph Report - Character-Sistem  (2026-08-18)

## Corpus Check
- 108 files · ~329,586 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1867 nodes · 3936 edges · 117 communities (104 shown, 13 thin omitted)
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 1434 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4cb59980`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- GameController
- MovementSystem
- TestGameControllerCriacoes
- GameStateManager
- MapManagerScreen
- PersonagemDB
- Magia
- Personagem
- BattleSystem
- PartyManagementScreen
- Criador jogos RPG
- EquipmentComponent
- NetworkSystem
- DungeonGenerator
- Party
- Raca
- EventSystem
- ChatLog
- Arma
- PropriedadesEventoFormScreen
- CombatNetworkAdapter
- ._processar_proximo_turno
- TestPropriedadesEventoFormScreen
- _criar_entidade_vazia
- rpg_schemas.py
- MapaInterativo
- MagiaDB
- EntityFactory
- TestMultiplosInimigos
- PositionComponent
- BattleScreen
- test_logica_mapas.py
- .exibir_mapa_na_tela
- CatalogoTiles
- GameEngineLoader
- ConfirmacaoSalvarScreen
- Relatório: RPG Game Maker (Textual + engine)
- TestMapearTipoEntidade
- CombatenteSprite
- aplicar_usar_item
- TestBattleSystem4v4Party
- JogoAtaqueApp
- on
- UsarItemBatalhaModal
- SimuladorCombate
- GamePlayScreen
- ArquivoCSVScreen
- conftest.py
- DummyBattleApp
- RTK Commands by Workflow
- InventarioMenuScreen
- test_editor_eventos.py
- DummyPartyApp
- aplicar_equipar_item
- Regras de Implementação
- TestObterPaginaAtiva
- README.md
- avaliar_condicoes
- ._executar_turno_inimigo_sincrono
- on
- ManagementMenuScreen
- TestInicializacaoCombate
- TestIAInimigo
- MODIFICADORES
- TestGameControllerConsultas
- .on_button_pressed
- NovoMapaFormScreen
- test_esper_integration.py
- copilot-instructions.md
- EventoDB
- ._calcular_posicoes_aliados
- .processar_csv
- PropriedadesFormScreen
- DummyPlayback
- RamoEditorScreen
- TestResolucaoAcoes
- GestorDeMapas
- .salvar_mapa_no_banco
- Regra 5: Regras/Fórmulas Combate
- test_renderizador.py
- Regra 3: Interface TUI (Textual)
- Regra 4: Persistência Dados (SQLAlchemy)
- Regra 7: Testes/TDD
- Criador e Mantenedor de testes
- RTK - Rust Token Killer (Google Antigravity)
- VisualizadorImagem
- .__init__
- Regra 2: Arquitetura ECS + Esper
- TODO
- GameDev_Senior
- .carregar_arvore_de_mapas
- test_party_and_enemies_in_combat.py
- Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)
- Regra 6: Interpretador Eventos (EventSystem)
- root
- test_aprender_magia_evento.py
- AGENTS.md
- Debuger_senior.agent.md
- rules/graphify.md
- workflows/graphify.md
- Game_Screen.md
- Map_Maneger.md
- SPEC.md
- sischarlesrpg

## God Nodes (most connected - your core abstractions)
1. `GameController` - 115 edges
2. `Personagem` - 92 edges
3. `GamePlayScreen` - 79 edges
4. `BattleSystem` - 69 edges
5. `BattleScreen` - 66 edges
6. `InventoryComponent` - 62 edges
7. `Raca` - 61 edges
8. `ClasseRPG` - 60 edges
9. `PersonagemDB` - 60 edges
10. `MapManagerScreen` - 60 edges

## Surprising Connections (you probably didn't know these)
- `criar_e_salvar_mapa()` --calls--> `MapaDB`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/models/mapas_db.py
- `build_interactable_component()` --calls--> `InteractableComponent`  [INFERRED]
  rpg_api/tests/test_interaction_system.py → rpg_api/app/core/engine/components.py
- `test_deve_atribuir_status_e_inventario_ao_jogador_no_esper()` --calls--> `GameEngineLoader`  [INFERRED]
  rpg_api/tests/test_esper_integration.py → rpg_api/app/core/engine/engine_loader.py
- `test_garantir_itens_padrao_popula_banco()` --calls--> `garantir_itens_padrao()`  [INFERRED]
  rpg_api/tests/test_item_system.py → rpg_api/app/core/engine/item_system.py
- `test_salvar_e_recuperar_arma_no_banco()` --calls--> `ItemDB`  [INFERRED]
  rpg_api/tests/test_database.py → rpg_api/app/models/equipamentos_db.py

## Import Cycles
- None detected.

## Communities (117 total, 13 thin omitted)

### Community 0 - "GameController"
Cohesion: 0.04
Nodes (36): criar_e_salvar_mapa(), GameController, Session, Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Alista um personagem para a equipe do jogador. - Se for especificado um slot…, Remove um personagem da equipe ativa/alistamento., Carrega a equipe ativa (Party de domínio) do banco de dados. Retorna a… (+28 more)

### Community 1 - "MovementSystem"
Cohesion: 0.07
Nodes (22): PlayerControlComponent, Uma flag que indica que esta entidade é controlada pelo teclado., MovementSystem, Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, Processa movimento autônomo de monstros/NPCs a cada tick., Compatibilidade legado., Verifica se há um evento à frente do jogador. Se houver, publica as informações…, Sistema lógico encarregado de validar a física e colisões de movimentos. (+14 more)

### Community 2 - "TestGameControllerCriacoes"
Cohesion: 0.06
Nodes (23): Deve criar uma arma com dano e tipo de ataque., Deve criar uma raça válida com todos os atributos., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Deve listar todas as raças cadastradas., Verifica se todos os 5 atributos são salvos., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio). (+15 more)

### Community 3 - "GameStateManager"
Cohesion: 0.06
Nodes (29): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Base, Guarda o estado de execução de um jogo específico de um usuário. Desacoplado de…, SaveDB (+21 more)

### Community 4 - "MapManagerScreen"
Cohesion: 0.07
Nodes (30): RowSelected, ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., EfeitoDB, Tabela que armazena os Efeitos Temporários (condições)., MapaDB, MapManagerScreen (+22 more)

### Community 5 - "PersonagemDB"
Cohesion: 0.08
Nodes (33): CenarioDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., ClasseRPGDB, EquipeMembroDB, PersonagemDB, Base, RacaDB (+25 more)

### Community 6 - "Magia"
Cohesion: 0.08
Nodes (26): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais ou Habilidade Mágica., Testa a integração do inventário e status dos jogadores no combate. (+18 more)

### Community 7 - "Personagem"
Cohesion: 0.08
Nodes (18): Personagem, Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Dano direto que ignora armadura (ex: veneno)., Realiza a mecânica completa de ataque contra um alvo., Adiciona um efeito à lista de ativos. (+10 more)

### Community 8 - "BattleSystem"
Cohesion: 0.08
Nodes (27): InventoryComponent, Guarda os atributos de combate e informações vitais do personagem., Armazena os itens que o personagem está carregando., StatsComponent, BattleSystem, Processamento sob demanda., Motor lógico puro de combate por turnos multi-personagens (estilo Final…, AcaoConfirmada (+19 more)

### Community 9 - "PartyManagementScreen"
Cohesion: 0.11
Nodes (13): EquipeAtualizada, PartyManagementScreen, Changed, ComposeResult, Highlighted, Message, on, Pressed (+5 more)

### Community 10 - "Criador jogos RPG"
Cohesion: 0.06
Nodes (35): Acionar - (tecla Enter), Caminhos Magia, ClasseRPG, Comandos Evento Mais Usados, Criador jogos RPG, Criador Mapas, Editor gerador procedural mapas: ('caverna', 'vila', 'masmorra'), 3 camadas: (Terrenos, Objetos, Eventos)., Efeitos (+27 more)

### Community 11 - "EquipmentComponent"
Cohesion: 0.13
Nodes (17): Enum, ActiveEffectsComponent, EquipmentComponent, InteractableComponent, MovimentComponent, Dataclass pura que armazena e monitora em tempo de execução os efeitos…, Define o comportamento autônomo (NPCs, Monstros, Pets)., Armazena o que está atualmente equipado no herói influenciando seus atributos. (+9 more)

### Community 12 - "NetworkSystem"
Cohesion: 0.09
Nodes (20): BattleParticipantComponent, CombatStateComponent, HeroComponent, NetworkPlayerComponent, Guarda a referência para a instância Personagem do domínio para o jogador., Identificador para jogadores que estão conectados via rede (multiplayer)., Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o… (+12 more)

### Community 13 - "DungeonGenerator"
Cohesion: 0.08
Nodes (18): Any, Lê as configurações do RPG e aciona o gerador independente correspondente., circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo. (+10 more)

### Community 14 - "Party"
Cohesion: 0.07
Nodes (14): Party, Adiciona uma quantidade de item ao inventário individual do personagem., Remove uma quantidade de item do inventário individual do personagem., Entidade de Domínio: Representa o grupo/equipe de até 4 personagens aliados.…, Alista um novo personagem na equipe. Se o grupo ativo tiver menos de 4 membros,…, Move um membro das reservas para a equipe ativa (máx 4)., Move um membro da equipe ativa para as reservas., Troca a ordem de dois membros dentro da equipe ativa. (+6 more)

### Community 15 - "Raca"
Cohesion: 0.10
Nodes (28): ClasseRPG, Raca, test_aprender_magia_evento_sucesso_e_falha(), party_4_aliados(), battle_sys(), eventos_capturados(), inimigos_4(), party_4_aliados() (+20 more)

### Community 16 - "EventSystem"
Cohesion: 0.10
Nodes (14): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+6 more)

### Community 17 - "ChatLog"
Cohesion: 0.06
Nodes (30): garantir_schema_atualizado(), get_db(), Verifica e migra automaticamente colunas ausentes em bancos SQLite existentes.…, Função utilitária para abrir e fechar a conexão com o banco corretamente., ChatLog, MensagemAnimada, App, ComposeResult (+22 more)

### Community 18 - "Arma"
Cohesion: 0.10
Nodes (19): Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base., Herda de Item. Adiciona propriedades de defesa extra. (+11 more)

### Community 19 - "PropriedadesEventoFormScreen"
Cohesion: 0.12
Nodes (12): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Callback do modal AdicionarSwitchScreen., Callback do modal AdicionarVariavelScreen. (+4 more)

### Community 20 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 21 - "._processar_proximo_turno"
Cohesion: 0.11
Nodes (15): Any, Retorna a visão ordenada da linha do tempo/fila de turnos., Avança o ponteiro da fila de turnos para o próximo combatente vivo. Se todos…, Executa a ação escolhida pelo jogador para o aliado cujo turno está ativo., Dispara o evento turno_calculado com estado consolidado para a UI., Roteia a ação para os métodos do Domínio Personagem com suporte a magias em…, Encerra o combate, remove marcadores ECS e emite o evento de término., Alias de retrocompatibilidade: retorna o primeiro aliado (líder da equipe). (+7 more)

### Community 22 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 23 - "_criar_entidade_vazia"
Cohesion: 0.11
Nodes (14): _criar_entidade_vazia(), limpar_mundo_esper(), fixture, Verifica que toda entidade de evento recebe os componentes base., Verifica que Monstros recebem StatsComponent e MovimentComponent…, Verifica que a correção do bug IndexError está funcionando., Verifica que NPCs não recebem StatsComponent de combate., Verifica que Itens são atravessáveis (CollisionComponent.solido=False). (+6 more)

### Community 24 - "rpg_schemas.py"
Cohesion: 0.22
Nodes (14): BaseModel, post, criar_personagem(), criar_raca(), listar_personagens(), listar_racas(), get, Session (+6 more)

### Community 25 - "MapaInterativo"
Cohesion: 0.09
Nodes (17): ModalScreen, MouseDown, MouseMove, MouseUp, Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap (+9 more)

### Community 26 - "MagiaDB"
Cohesion: 0.09
Nodes (17): MagiaDB, Base, Tabela que armazena os metadados de Magias e Habilidades., fixture, setup_db(), test_criacao_e_mapeamento_efeito_e_magia_db(), Testes de lógica de equipamento do mainx_cli., Deve equipar itens em todos os slots sequencialmente. (+9 more)

### Community 27 - "EntityFactory"
Cohesion: 0.15
Nodes (15): EntityFactory, _extrair_stats_salvos(), Any, Cria e hidrata entidades no esper de forma centralizada e tipada. Todos os…, Ponto de entrada principal para criação de entidades de evento. Determina o…, Adiciona os componentes comuns a todas as entidades de evento:…, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa…, NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.… (+7 more)

### Community 28 - "TestMultiplosInimigos"
Cohesion: 0.10
Nodes (19): battle_sys(), classe_guerreiro(), eventos_capturados(), heroi(), inimigo(), fixture, raca_humana(), Testes do Sistema de Combate por Turnos — BattleSystem Testa o motor de combate… (+11 more)

### Community 29 - "PositionComponent"
Cohesion: 0.13
Nodes (14): CollisionComponent, PositionComponent, Como a entidade se parece na interface., Onde a entidade está no mapa lógico., RenderComponent, Hidrata a entidade do jogador a partir de dados do SaveDB. Args: entity_id:…, Hidrata a entidade do jogador a partir de um objeto de domínio (novo jogo).…, test_fluxo_completo_engine_manager() (+6 more)

### Community 30 - "BattleScreen"
Cohesion: 0.12
Nodes (10): BattleScreen, Screen, Atualiza os valores e redesenha as barras., Tela de combate por turnos multi-aliados (1-4) vs multi-inimigos (1-4). Segue o…, Registra handlers do Esper e inicializa o motor de combate., Inicializa os dados visuais do combate 4v4 e anima entrada., Atualiza o combatente ativo da vez, destacando sua barra e liberando/bloqueando…, Processa o resultado do turno, atualiza barras, escreve logs e anima. (+2 more)

### Community 31 - "test_logica_mapas.py"
Cohesion: 0.09
Nodes (19): padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., ComposeResult, fixture_db_session(), fixture, Garante que tuplas matemáticas viram strings JSON., Garante que strings JSON voltam a ser tuplas matemáticas. (+11 more)

### Community 32 - ".exibir_mapa_na_tela"
Cohesion: 0.11
Nodes (10): Pega o código hexadecimal da cor de fundo de um chão., Tira uma fotografia à matriz atual antes de a alterarmos., Callback acionado ao fechar a tela de Propriedades., Callback acionado quando o usuário confirma os dados do evento no Modal., Monta o formulário de volta injetando a nova coordenada no escopo correto., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., balde_de_tinta() (+2 more)

### Community 33 - "CatalogoTiles"
Cohesion: 0.11
Nodes (11): CatalogoTiles, Registo central que define as categorias e propriedades visuais dos emojis., AdicionarComandoScreen, AdicionarSwitchScreen, AdicionarVariavelScreen, Pressed, Componente de Formulário de Eventos do Editor de Mapas. Contém todas as telas…, Modal simples para adicionar uma condição de Switch a uma página. (+3 more)

### Community 34 - "GameEngineLoader"
Cohesion: 0.12
Nodes (12): GameEngineLoader, Any, Session, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos…, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Busca o processador de rede (NetworkSystem) registrado no mundo ativo. (+4 more)

### Community 35 - "ConfirmacaoSalvarScreen"
Cohesion: 0.12
Nodes (8): NodeSelected, ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo., Dispara quando o utilizador clica num mapa na barra lateral., Trata a resposta do utilizador no modal de confirmação., Transforma o texto '1,2' do Banco de volta em tupla matemática (1, 2)., Regista ou atualiza um evento numa coordenada específica., Povoa a memória a partir da lista de eventos vindos do banco de dados.

### Community 36 - "Relatório: RPG Game Maker (Textual + engine)"
Cohesion: 0.09
Nodes (21): 1. Lógica Assíncrona, Pilha Comandos, 2. Componente `ChoiceBox`, Diretórios, Fase 1: Domínio, Fase 1: Prototipagem Visual, Fase 2: Banco/Infra, Fase 2: Integração/Anomalias, Fase 3: Arquitetura (ECS) (+13 more)

### Community 37 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 38 - "CombatenteSprite"
Cohesion: 0.13
Nodes (7): CombatenteSprite, EfeitoAtaque, Static, Tela de Combate por Turnos — BattleScreen (Padrão Ouro Final Fantasy) Interface…, Widget de sprite do combatente com posições X e Y animáveis via reactive., Emoji de impacto ou projétil que aparece brevemente na arena., Anima ataque físico ou magia para o combatente da vez.

### Community 39 - "aplicar_usar_item"
Cohesion: 0.19
Nodes (19): aplicar_usar_item(), _eh_equipamento(), garantir_itens_padrao(), inv_remover_item(), obter_equipamentos_inventario(), obter_itens_usaveis(), obter_mapeamento_inventario(), obter_todos_itens_db() (+11 more)

### Community 40 - "TestBattleSystem4v4Party"
Cohesion: 0.11
Nodes (10): Valida que cada personagem (aliado ou inimigo) possui seu próprio turno…, Valida que magia em área atinge todos os 4 inimigos de uma única vez., Valida que suporte/cura pode ser direcionado a outro membro da equipe., Valida uso de item do inventário individual do combatente da vez., Se um combatente morre antes de agir na rodada, o turno deve ignorá-lo…, Ao abater os 4 inimigos, dispara 'combate_encerrado' com vencedor='jogador'., Ao abater os 4 aliados, dispara 'combate_encerrado' com vencedor='inimigo'., Inimigo seleciona alvo vivo entre os aliados disponíveis. (+2 more)

### Community 41 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 42 - "on"
Cohesion: 0.33
Nodes (3): Changed, on, TabActivated

### Community 43 - "UsarItemBatalhaModal"
Cohesion: 0.16
Nodes (9): Highlighted, on, Pressed, Modal para escolha de itens usáveis pelo combatente ativo., UsarItemBatalhaModal, Message, Pressed, Trata o clique ou Enter no botão de confirmação. (+1 more)

### Community 44 - "SimuladorCombate"
Cohesion: 0.14
Nodes (11): Any, Corre X batalhas em silêncio e agrupa todas as estatísticas num mega relatório., Gere as simulações de batalhas em grupo e recolhe estatísticas., Calcula a ordem de combate baseada em 1d6 + Agilidade., Filtra apenas os combatentes que ainda têm Pontos de Vida., Executa uma única batalha até uma equipa ser derrotada. Devolve um relatório de…, SimuladorCombate, Testa se uma batalha decorre corretamente e se o vencedor é identificado. (+3 more)

### Community 45 - "GamePlayScreen"
Cohesion: 0.06
Nodes (27): Key, ChoiceBox, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs., GamePlayScreen, on (+19 more)

### Community 46 - "ArquivoCSVScreen"
Cohesion: 0.13
Nodes (7): ArquivoCSVScreen, MenuAcoesScreen, Pressed, Captura os cliques dos botões., Tela de menu acionada pelo botão 'Menu' no topo., Pede ao utilizador o caminho/nome do ficheiro CSV., # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não…

### Community 47 - "conftest.py"
Cohesion: 0.17
Nodes (15): classe_default(), item_arma(), item_armadura(), item_escudo(), personagem_default(), fixture, raca_default(), Fixture: Escudo de teste. (+7 more)

### Community 48 - "DummyBattleApp"
Cohesion: 0.17
Nodes (13): DummyBattleApp, inimigos_4(), isolamento_esper(), anyio, App, fixture, Valida que o aliado cujo turno está ativo recebe destaque visual e atualiza a…, App de teste Textual para rodar BattleScreen com pilot. (+5 more)

### Community 49 - "RTK Commands by Workflow"
Cohesion: 0.13
Nodes (14): Analysis & Debug (70-90% savings), Build & Compile (80-90% savings), Files & Search (60-75% savings), Git (59-80% savings), GitHub (26-87% savings), Golden Rule, Infrastructure (85% savings), JavaScript/TypeScript Tooling (70-90% savings) (+6 more)

### Community 50 - "InventarioMenuScreen"
Cohesion: 0.19
Nodes (6): InventarioMenuScreen, ComposeResult, Highlighted, on, Pressed, Menu interativo com abas para visualização, uso e troca de equipamentos do…

### Community 51 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 52 - "DummyPartyApp"
Cohesion: 0.19
Nodes (11): DummyPartyApp, anyio, App, fixture, Valida que a tela carrega e popula membros ativos, reservas e recrutáveis., Valida transições de membros entre equipe ativa e reserva., Valida a função do GameController de transferência de itens entre personagens., setup_db() (+3 more)

### Community 53 - "aplicar_equipar_item"
Cohesion: 0.18
Nodes (11): aplicar_desequipar_item(), aplicar_equipar_item(), inv_adicionar_item(), Equipa um item do inventário no slot correspondente do EquipmentComponent., Desequipa o item do slot ("arma", "armadura", "escudo") e o devolve ao…, Adiciona uma quantidade de item ao componente de inventário (case-insensitive)., fixture, setup_teardown_db() (+3 more)

### Community 54 - "Regras de Implementação"
Cohesion: 0.17
Nodes (11): 1. Integração Textual + ECS (esper), 2. Gerenciamento de Foco e Visibilidade de Widgets, 3. Isolamento de Event Bubbling (Propagação de Eventos), 4. Agendamento Pró-Frame com `call_next()`, 5. Protocolo de Mensageria Customizada Externa, 6. Persistência e Backend, Competências Essenciais, Diretrizes do Sistema (+3 more)

### Community 55 - "TestObterPaginaAtiva"
Cohesion: 0.24
Nodes (6): obter_pagina_ativa(), Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.…, Verifica a varredura decrescente de páginas (Regra 6)., Por varredura decrescente, sem switches, a última página é sempre retornada., Entradas que não são dict devem ser ignoradas na varredura., TestObterPaginaAtiva

### Community 56 - "README.md"
Cohesion: 0.18
Nodes (10): Apoie o projeto pela chave pix:, CharSistem é uma Engine de Criação de RPGs jogaveis de terminal feito em Python., Contexto do Projeto, Contexto do Projeto - Fase 2: Integração Cloud, Crie seus próprios mundos com cenários completos, personagens, magias, monstros., Este projeto tem potencial para se tornar um MMORPG de linha de comando!, Graficos totalmente feitos com emojis graças ao Textual: https://textual.textualize.io/, Jogue seu jogo e compartilhe com amigos. (+2 more)

### Community 57 - "avaliar_condicoes"
Cohesion: 0.27
Nodes (8): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Obtém o ID virtual estável do banco de dados para a entidade de evento (evt.id…, Avalia se todas as condições declaradas em uma página de evento são atendidas.

### Community 58 - "._executar_turno_inimigo_sincrono"
Cohesion: 0.22
Nodes (5): Cria a corrotina do turno do inimigo no event loop ativo., Pausa dramática de 0.8s para leitura do turno anterior antes do inimigo agir., Processa a ação de IA para o inimigo ativo da fila de turnos., Alias de retrocompatibilidade para o primeiro inimigo., IA adaptativa para o inimigo ativo.

### Community 59 - "on"
Cohesion: 0.31
Nodes (4): Changed, on, Sincroniza o self_switch da página atual quando o Select muda., Sincroniza o item_requerido da página atual quando o Input muda.

### Community 60 - "ManagementMenuScreen"
Cohesion: 0.29
Nodes (3): ManagementMenuScreen, Changed, on

### Community 61 - "TestInicializacaoCombate"
Cohesion: 0.20
Nodes (6): Testa o setup do combate via BattleSystem.iniciar_combate., Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.…, BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar., battle_sys.combate_ativo deve ser True após iniciar., Regra 5: Iniciativa = 1d6 + Agilidade. Com d6 fixo em 1, o personagem com maior…, TestInicializacaoCombate

### Community 62 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

### Community 63 - "MODIFICADORES"
Cohesion: 0.22
Nodes (8): 1 - PONTOS DE VIDA (hp MÁX.), 2 - PONTOS DE MANA, 3 - MODIFICADOR DE ATAQUE CORPO-A-CORPO, 4 - MODIFICADOR DE ATAQUE A DISTÂNCIA, ATAQUE, DEFESA / ESQUIVA, MODIFICADORES, **Não se importe com números quebrados

### Community 64 - "TestGameControllerConsultas"
Cohesion: 0.25
Nodes (5): Testes das funções de consulta., Deve retornar um personagem válido pelo ID., Deve retornar None para ID inexistente., Deve retornar lista vazia quando não há classes., TestGameControllerConsultas

### Community 65 - ".on_button_pressed"
Cohesion: 0.22
Nodes (3): Gerencia os cliques na tela principal., Retrocede a matriz para o último estado guardado., Avança Terrenos e Objetos para o estado do futuro.

### Community 66 - "NovoMapaFormScreen"
Cohesion: 0.28
Nodes (5): NovoMapaFormScreen, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 67 - "test_esper_integration.py"
Cohesion: 0.22
Nodes (6): fixture_db_session(), fixture, Garante que o método e'sperado pela tela limpa o mundo e popula as entidades., Cria um banco SQLite isolado em memória para cada teste., test_deve_atribuir_status_e_inventario_ao_jogador_no_esper(), test_deve_executar_carregar_engine_do_banco_com_esper()

### Community 68 - "copilot-instructions.md"
Cohesion: 0.25
Nodes (7): Conventions, Current Implementation Notes, Documentation References, Key Areas, Project Overview, Test and Development Commands, When to Use These Instructions

### Community 69 - "EventoDB"
Cohesion: 0.25
Nodes (4): EventoDB, Base, test_salvar_e_recuperar_arma_no_banco(), test_salvar_e_recuperar_evento_no_mapa()

### Community 70 - "._calcular_posicoes_aliados"
Cohesion: 0.29
Nodes (4): Retorna coordenadas (x, y) balanceadas para até 4 aliados no lado esquerdo.…, Retorna coordenadas (x, y) balanceadas para até 4 inimigos no lado direito.…, Posiciona sprites em suas coordenadas de formação antes da animação., Faz os sprites deslizarem suavemente para a formação de combate.

### Community 71 - ".processar_csv"
Cohesion: 0.25
Nodes (4): Callback após o utilizador clicar em algo no Menu Principal., Redireciona para importar ou exportar com base no nome do ficheiro., Transforma a matriz atual em texto com vírgulas e guarda no disco., Lê um ficheiro CSV do disco e transforma numa matriz para o nosso programa.

### Community 72 - "PropriedadesFormScreen"
Cohesion: 0.29
Nodes (4): PropriedadesFormScreen, Tela flutuante para editar as propriedades de um mapa que já está na memória., Ao abrir, carrega os mapas do banco para o Select de Mapa Pai., Coleta o texto atual digitado nos campos para não perder o progresso.

### Community 74 - "RamoEditorScreen"
Cohesion: 0.15
Nodes (5): Modo_de_Captura, AcoesComandoScreen, RamoEditorScreen, Menu contextual ao clicar num comando da lista., Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou…

### Community 75 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

### Community 76 - "GestorDeMapas"
Cohesion: 0.29
Nodes (4): GestorDeMapas, Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV.

### Community 77 - ".salvar_mapa_no_banco"
Cohesion: 0.29
Nodes (3): Salva o mapa atual, os objetos estáticos e os eventos dinâmicos no banco de…, Transforma as chaves de tupla (1, 2) em texto '1,2' para poder salvar no Banco., Transforma o dicionário de memória numa lista pronta para o SQLAlchemy.

### Community 78 - "Regra 5: Regras/Fórmulas Combate"
Cohesion: 0.29
Nodes (6): 1. Atributos Principais, 2. Fórmulas Status Derivados, 3. Teste Ataque/Defesa, 4. Dano/Absorção, 5. Simulação (Isolamento Arena), Regra 5: Regras/Fórmulas Combate

### Community 79 - "test_renderizador.py"
Cohesion: 0.33
Nodes (5): fixture, Garante o isolamento completo entre os testes limpando completamente todas as…, Garante que se não houver entidade no local, o objeto estático seja desenhado., restaurar_mundo_esper(), test_deve_renderizar_objeto_se_nao_houver_entidade()

### Community 80 - "Regra 3: Interface TUI (Textual)"
Cohesion: 0.33
Nodes (5): 1. Eventos Customizados, 2. Prevenção Conflitos Threads, 3. Gestão CSS e Layouts, 4. Responsividade e Eventos de Estado, Regra 3: Interface TUI (Textual)

### Community 81 - "Regra 4: Persistência Dados (SQLAlchemy)"
Cohesion: 0.33
Nodes (5): 1. Separação Ambientes (Prod vs. Teste), 2. Tipagem JSON, 3. Coordenadas, 4. Gerenciamento Assíncrono (Cloud), Regra 4: Persistência Dados (SQLAlchemy)

### Community 82 - "Regra 7: Testes/TDD"
Cohesion: 0.33
Nodes (5): 1. Isolamento Dados Aleatórios, 2. Limpeza DB Teste, 3. Cobertura Mínima, 4. Testes de Behavior e User Interface:, Regra 7: Testes/TDD

### Community 83 - "Criador e Mantenedor de testes"
Cohesion: 0.40
Nodes (4): Atendimento aos requisitos, Criador e Mantenedor de testes, Regras de trabalho, Verificação dos testes

### Community 84 - "RTK - Rust Token Killer (Google Antigravity)"
Cohesion: 0.40
Nodes (4): Meta Commands, RTK - Rust Token Killer (Google Antigravity), Rule, Why

### Community 85 - "VisualizadorImagem"
Cohesion: 0.40
Nodes (3): App, ComposeResult, VisualizadorImagem

### Community 87 - "Regra 2: Arquitetura ECS + Esper"
Cohesion: 0.40
Nodes (4): 1. Responsabilidades ECS, 2. Isolamento Headless, 3. Gerenciamento Cenas (WorldContext), Regra 2: Arquitetura ECS + Esper

### Community 88 - "TODO"
Cohesion: 0.40
Nodes (4): Fase atual;, Outras Fases, Próxima Fase, TODO

### Community 89 - "GameDev_Senior"
Cohesion: 0.50
Nodes (3): GameDev_Senior, Objetivo, Regras de trabalho

### Community 91 - "test_party_and_enemies_in_combat.py"
Cohesion: 0.50
Nodes (3): Testes de Integração de Múltiplos Aliados e Inimigos no Combate (BattleScreen &…, Valida que o botão de Batalha Visual na ArenaScreen abre BattleScreen com 4v4., test_arena_batalha_visual_interativa_4v4()

### Community 92 - "Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)"
Cohesion: 0.50
Nodes (3): 1. Separação de Camadas, 2. DDD + Mapper (Adapter), Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)

### Community 93 - "Regra 6: Interpretador Eventos (EventSystem)"
Cohesion: 0.50
Nodes (3): 1. Pipeline Execução, 2. Pilha Não-Bloqueante, Regra 6: Interpretador Eventos (EventSystem)

## Knowledge Gaps
- **120 isolated node(s):** `sischarlesrpg`, `Regras de Desenvolvimento do Projeto (SisCharlesRpg)`, `Diretrizes do Sistema`, `1. Integração Textual + ECS (esper)`, `2. Gerenciamento de Foco e Visibilidade de Widgets` (+115 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameController` connect `GameController` to `MovementSystem`, `TestGameControllerCriacoes`, `MapManagerScreen`, `PersonagemDB`, `Magia`, `Personagem`, `BattleSystem`, `PartyManagementScreen`, `NetworkSystem`, `Party`, `Raca`, `EventSystem`, `Arma`, `MagiaDB`, `GameEngineLoader`, `SimuladorCombate`, `GamePlayScreen`, `DummyPartyApp`, `ManagementMenuScreen`, `TestGameControllerConsultas`, `GestorDeMapas`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `GamePlayScreen` connect `GamePlayScreen` to `GameController`, `MovementSystem`, `GameStateManager`, `MapManagerScreen`, `PersonagemDB`, `Magia`, `BattleSystem`, `PartyManagementScreen`, `EquipmentComponent`, `NetworkSystem`, `Party`, `EventSystem`, `ChatLog`, `Arma`, `TestMultiplosInimigos`, `PositionComponent`, `BattleScreen`, `GameEngineLoader`, `InventarioMenuScreen`, `ManagementMenuScreen`, `TestInicializacaoCombate`, `TestIAInimigo`, `TestResolucaoAcoes`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `.exibir_mapa_na_tela`, `.on_button_pressed`, `CatalogoTiles`, `ConfirmacaoSalvarScreen`, `EventoDB`, `.processar_csv`, `on`, `GestorDeMapas`, `.salvar_mapa_no_banco`, `ArquivoCSVScreen`, `DungeonGenerator`, `PropriedadesEventoFormScreen`, `test_editor_eventos.py`, `TestPropriedadesEventoFormScreen`, `MapaInterativo`, `.carregar_arvore_de_mapas`, `ManagementMenuScreen`, `test_logica_mapas.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 92 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 92 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `BattleSystem` (e.g. with `GameController` and `BattleParticipantComponent`) actually correct?**
  _`BattleSystem` has 47 INFERRED edges - model-reasoned connections that need verification._