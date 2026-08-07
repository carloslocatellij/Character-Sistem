# Graph Report - SisCharlesRpg  (2026-08-07)

## Corpus Check
- 103 files · ~318,444 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1640 nodes · 3346 edges · 110 communities (95 shown, 15 thin omitted)
- Extraction: 64% EXTRACTED · 36% INFERRED · 0% AMBIGUOUS · INFERRED: 1194 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f49ee06c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InventarioMenuScreen
- BarraStatusCombate
- InventoryComponent
- Arma
- GameController
- MagiaDB
- TestTurnoJogador
- BattleSystem
- ItemDB
- Criador jogos RPG
- EventSystem
- PersonagemDB
- DungeonGenerator
- PropriedadesEventoFormScreen
- CombatNetworkAdapter
- TestPropriedadesEventoFormScreen
- MapManagerScreen
- EntityFactory
- .criar_entidade_evento
- MapaInterativo
- Personagem
- TestMultiplosInimigos
- PropriedadesFormScreen
- TestSimuladorArena
- ChatLog
- Relatório: RPG Game Maker (Textual + engine)
- obter_pagina_ativa
- rpg_schemas.py
- TestMapearTipoEntidade
- CatalogoTiles
- TestValidacaoEntradas
- SimuladorCombate
- MockMapLoader
- RamoEditorScreen
- ManagementMenuScreen
- JogoAtaqueApp
- PositionComponent
- conftest.py
- ConfirmacaoSalvarScreen
- RTK Commands by Workflow
- TestGameControllerConsultas
- .processar_pintura
- test_editor_eventos.py
- NovoMapaFormScreen
- Regras de Implementação
- GameStateManager
- Graphify Rule
- GestorDeMapas
- SecondaryMap
- README.md
- GamePlayScreen
- TestInicializacaoCombate
- GameEngineLoader
- MensagemAnimada
- Magia
- EventoDB
- on
- BattleScreen
- TestResolucaoAcoes
- test_logica_mapas.py
- MODIFICADORES
- .log_mensagem
- .processar_comando_terminal
- CombatenteSprite
- test_esper_integration.py
- copilot-instructions.md
- .atualizar_tela
- .processar_csv
- .disparar_bifurcacao_visual
- TestCriarEntidadeJogadorDeSave
- .carregar_arvore_de_mapas
- test_magia_efeito_db.py
- Regra 5: Regras/Fórmulas Combate
- AISystem
- test_renderizador.py
- Regra 4: Persistência Dados (SQLAlchemy)
- Criador e Mantenedor de testes
- RTK - Rust Token Killer (Google Antigravity)
- VisualizadorImagem
- Regra 2: Arquitetura ECS + Esper
- Regra 3: Interface TUI (Textual)
- Regra 7: Testes/TDD
- TODO
- GameDev_Senior
- Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)
- Regra 6: Interpretador Eventos (EventSystem)
- get_db
- root
- AGENTS.md
- Debuger_senior.agent.md
- rules/graphify.md
- workflows/graphify.md
- Game_Screen.md
- Map_Maneger.md
- SPEC.md
- sischarlesrpg
- TestIAInimigo

## God Nodes (most connected - your core abstractions)
1. `GameController` - 86 edges
2. `GamePlayScreen` - 73 edges
3. `Personagem` - 71 edges
4. `InventoryComponent` - 62 edges
5. `MapManagerScreen` - 60 edges
6. `BattleSystem` - 55 edges
7. `StatsComponent` - 54 edges
8. `Raca` - 52 edges
9. `ClasseRPG` - 51 edges
10. `PersonagemDB` - 50 edges

## Surprising Connections (you probably didn't know these)
- `criar_e_salvar_mapa()` --calls--> `MapaDB`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/models/mapas_db.py
- `test_deve_atribuir_status_e_inventario_ao_jogador_no_esper()` --calls--> `GameEngineLoader`  [INFERRED]
  rpg_api/tests/test_esper_integration.py → rpg_api/app/core/engine/engine_loader.py
- `test_salvar_e_recuperar_arma_no_banco()` --calls--> `ItemDB`  [INFERRED]
  rpg_api/tests/test_database.py → rpg_api/app/models/equipamentos_db.py
- `GameController` --uses--> `Arma`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/core/entities/equipamentos.py
- `GameController` --uses--> `Armadura`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/core/entities/equipamentos.py

## Import Cycles
- None detected.

## Communities (110 total, 15 thin omitted)

### Community 0 - "InventarioMenuScreen"
Cohesion: 0.06
Nodes (39): Highlighted, aplicar_equipar_item(), aplicar_usar_item(), _eh_equipamento(), garantir_itens_padrao(), inv_adicionar_item(), inv_remover_item(), obter_equipamentos_inventario() (+31 more)

### Community 1 - "BarraStatusCombate"
Cohesion: 0.06
Nodes (23): BarraStatusCombate, on, Pressed, Static, Widget, Atualiza os valores e redesenha as barras., Tela de Combate por Turnos — BattleScreen Interface TUI do sistema de combate…, Atualiza a barra de HP do herói sempre que o valor reativo muda. (+15 more)

### Community 2 - "InventoryComponent"
Cohesion: 0.10
Nodes (31): Enum, EquipmentComponent, InventoryComponent, Guarda os atributos de combate e informações vitais do personagem., Armazena os itens que o personagem está carregando., Armazena o que está atualmente equipado no herói influenciando seus atributos., StatsComponent, entity_factory.py Fábrica de Entidades ECS (EntityFactory). Centraliza toda a… (+23 more)

### Community 3 - "Arma"
Cohesion: 0.11
Nodes (19): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+11 more)

### Community 4 - "GameController"
Cohesion: 0.07
Nodes (22): GameController, Session, Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda., Deve equipar uma armadura no corpo. (+14 more)

### Community 5 - "MagiaDB"
Cohesion: 0.08
Nodes (19): EfeitoDB, MagiaDB, Base, Tabela que armazena os metadados de Magias e Habilidades., Tabela que armazena os Efeitos Temporários (condições)., CharacterFormScreen, ClasseFormScreen, EquipScreen (+11 more)

### Community 6 - "TestTurnoJogador"
Cohesion: 0.10
Nodes (17): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, Testa os novos componentes ECS relacionados ao combate., CombatStateComponent deve inicializar com valores padrão corretos., BattleParticipantComponent deve aceitar tipo jogador/inimigo/rede., Testa a execução de ações do jogador via BattleSystem. (+9 more)

### Community 7 - "BattleSystem"
Cohesion: 0.10
Nodes (27): BattleSystem, O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista., Configura os combatentes com deepcopy e dispara o evento de início. O deepcopy…, ClasseRPG, Raca, AcaoConfirmada (+19 more)

### Community 8 - "ItemDB"
Cohesion: 0.08
Nodes (18): ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., Deve criar uma arma com dano e tipo de ataque., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Deve criar uma classe com múltiplos caminhos., Deve criar uma classe sem caminhos (bonus_caminhos vazio). (+10 more)

### Community 9 - "Criador jogos RPG"
Cohesion: 0.06
Nodes (35): Acionar - (tecla Enter), Caminhos Magia, ClasseRPG, Comandos Evento Mais Usados, Criador jogos RPG, Criador Mapas, Editor gerador procedural mapas: ('caverna', 'vila', 'masmorra'), 3 camadas: (Terrenos, Objetos, Eventos)., Efeitos (+27 more)

### Community 10 - "EventSystem"
Cohesion: 0.09
Nodes (15): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., fixture (+7 more)

### Community 11 - "PersonagemDB"
Cohesion: 0.10
Nodes (27): CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., ClasseRPGDB, PersonagemDB, Base, RacaDB (+19 more)

### Community 12 - "DungeonGenerator"
Cohesion: 0.09
Nodes (15): circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo., Verifica se este círculo se sobrepõe a outro., Gerador Procedimental Puro. Totalmente agnóstico: não possui dependências de… (+7 more)

### Community 13 - "PropriedadesEventoFormScreen"
Cohesion: 0.11
Nodes (13): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Sincroniza o item_requerido da página atual quando o Input muda., Callback do modal AdicionarSwitchScreen. (+5 more)

### Community 14 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 15 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 16 - "MapManagerScreen"
Cohesion: 0.11
Nodes (13): MapManagerScreen, Screen, Trata a resposta do utilizador no modal de confirmação., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Gerencia os cliques na tela principal., Retrocede a matriz para o último estado guardado., Avança Terrenos e Objetos para o estado do futuro., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo). (+5 more)

### Community 17 - "EntityFactory"
Cohesion: 0.11
Nodes (17): CollisionComponent, Fotografa os componentes da entidade 1., EntityFactory, _extrair_stats_salvos(), Any, Cria e hidrata entidades no esper de forma centralizada e tipada. Todos os…, Hidrata a entidade do jogador a partir de um objeto de domínio (novo jogo).…, Adiciona os componentes comuns a todas as entidades de evento:… (+9 more)

### Community 18 - ".criar_entidade_evento"
Cohesion: 0.11
Nodes (15): Ponto de entrada principal para criação de entidades de evento. Determina o…, _criar_entidade_vazia(), limpar_mundo_esper(), fixture, Verifica que toda entidade de evento recebe os componentes base., Verifica que Monstros recebem StatsComponent e MovimentComponent…, Verifica que a correção do bug IndexError está funcionando., Verifica que Itens são atravessáveis (CollisionComponent.solido=False). (+7 more)

### Community 19 - "MapaInterativo"
Cohesion: 0.13
Nodes (12): MouseDown, MouseMove, MouseUp, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado. (+4 more)

### Community 20 - "Personagem"
Cohesion: 0.11
Nodes (14): Personagem, Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Dano direto que ignora armadura (ex: veneno)., Realiza a mecânica completa de ataque contra um alvo., Adiciona um efeito à lista de ativos. (+6 more)

### Community 21 - "TestMultiplosInimigos"
Cohesion: 0.10
Nodes (19): battle_sys(), classe_guerreiro(), eventos_capturados(), heroi(), inimigo(), fixture, raca_humana(), Testes do Sistema de Combate por Turnos — BattleSystem Testa o motor de combate… (+11 more)

### Community 22 - "PropriedadesFormScreen"
Cohesion: 0.10
Nodes (11): ArquivoCSVScreen, MenuAcoesScreen, PropriedadesFormScreen, Pressed, Captura os cliques dos botões., Tela flutuante para editar as propriedades de um mapa que já está na memória., Ao abrir, carrega os mapas do banco para o Select de Mapa Pai., Coleta o texto atual digitado nos campos para não perder o progresso. (+3 more)

### Community 23 - "TestSimuladorArena"
Cohesion: 0.18
Nodes (7): criar_e_salvar_mapa(), simular_arena(), Testes da simulação de arena., Deve simular uma única batalha., Deve simular múltiplas batalhas e retornar estatísticas., Deve simular batalha com múltiplos personagens em cada equipe., TestSimuladorArena

### Community 24 - "ChatLog"
Cohesion: 0.14
Nodes (9): ChatLog, App, ComposeResult, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Captura o comando enviado pelo jogador e joga no nosso ChatLog., Widget customizado que se comporta como uma área de log com suporte a animações…, TestApp (+1 more)

### Community 25 - "Relatório: RPG Game Maker (Textual + engine)"
Cohesion: 0.09
Nodes (21): 1. Lógica Assíncrona, Pilha Comandos, 2. Componente `ChoiceBox`, Diretórios, Fase 1: Domínio, Fase 1: Prototipagem Visual, Fase 2: Banco/Infra, Fase 2: Integração/Anomalias, Fase 3: Arquitetura (ECS) (+13 more)

### Community 26 - "obter_pagina_ativa"
Cohesion: 0.13
Nodes (12): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), obter_pagina_ativa(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.… (+4 more)

### Community 27 - "rpg_schemas.py"
Cohesion: 0.22
Nodes (14): BaseModel, post, criar_personagem(), criar_raca(), listar_personagens(), listar_racas(), get, Session (+6 more)

### Community 28 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 29 - "CatalogoTiles"
Cohesion: 0.11
Nodes (11): CatalogoTiles, Registo central que define as categorias e propriedades visuais dos emojis., AdicionarComandoScreen, AdicionarSwitchScreen, AdicionarVariavelScreen, Pressed, Componente de Formulário de Eventos do Editor de Mapas. Contém todas as telas…, Modal simples para adicionar uma condição de Switch a uma página. (+3 more)

### Community 30 - "TestValidacaoEntradas"
Cohesion: 0.09
Nodes (14): Deve criar uma raça válida com todos os atributos., Verifica se todos os 5 atributos são salvos., Deve rejeitar atributos fora do intervalo 0-5., Testes de cenários práticos de uso., Testa que um item equipado em um personagem não afeta outro., Testes de tratamento de erros., Teste edge case: atributos com tipo errado., Testa se um item pode ser equipado em dois slots (não deveria). (+6 more)

### Community 31 - "SimuladorCombate"
Cohesion: 0.14
Nodes (13): Any, Corre X batalhas em silêncio e agrupa todas as estatísticas num mega relatório., Gere as simulações de batalhas em grupo e recolhe estatísticas., Calcula a ordem de combate baseada em 1d6 + Agilidade., Filtra apenas os combatentes que ainda têm Pontos de Vida., Executa uma única batalha até uma equipa ser derrotada. Devolve um relatório de…, SimuladorCombate, criar_lutadores() (+5 more)

### Community 33 - "RamoEditorScreen"
Cohesion: 0.15
Nodes (5): Modo_de_Captura, AcoesComandoScreen, RamoEditorScreen, Menu contextual ao clicar num comando da lista., Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou…

### Community 34 - "ManagementMenuScreen"
Cohesion: 0.21
Nodes (5): RowSelected, ManagementMenuScreen, Changed, on, Redireciona para o formulário correto baseado na tabela atual.

### Community 35 - "JogoAtaqueApp"
Cohesion: 0.12
Nodes (11): Combatente, JogoAtaqueApp, App, ComposeResult, Static, Remove os efeitos de piscar e restaura o emoji original., Subclasse de Static para gerenciar o X numérico de forma reativa., Sempre que x_pos mudar (via animação), atualiza o offset visual. (+3 more)

### Community 36 - "PositionComponent"
Cohesion: 0.10
Nodes (26): ActiveEffectsComponent, HeroComponent, InteractableComponent, PlayerControlComponent, PositionComponent, Dataclass pura que armazena e monitora em tempo de execução os efeitos…, Guarda a referência para a instância Personagem do domínio para o jogador., Uma flag que indica que esta entidade é controlada pelo teclado. (+18 more)

### Community 37 - "conftest.py"
Cohesion: 0.17
Nodes (15): classe_default(), item_arma(), item_armadura(), item_escudo(), personagem_default(), fixture, raca_default(), Fixture: Escudo de teste. (+7 more)

### Community 38 - "ConfirmacaoSalvarScreen"
Cohesion: 0.29
Nodes (4): NodeSelected, ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo., Dispara quando o utilizador clica num mapa na barra lateral.

### Community 39 - "RTK Commands by Workflow"
Cohesion: 0.13
Nodes (14): Analysis & Debug (70-90% savings), Build & Compile (80-90% savings), Files & Search (60-75% savings), Git (59-80% savings), GitHub (26-87% savings), Golden Rule, Infrastructure (85% savings), JavaScript/TypeScript Tooling (70-90% savings) (+6 more)

### Community 40 - "TestGameControllerConsultas"
Cohesion: 0.11
Nodes (11): Testes das funções de consulta., Deve retornar um personagem válido pelo ID., Deve retornar None para ID inexistente., Deve listar todas as raças cadastradas., Deve retornar lista vazia quando não há classes., Testes da conversão BD -> Domínio., Deve converter personagem sem equipamentos., Deve converter personagem com todos os equipamentos. (+3 more)

### Community 41 - ".processar_pintura"
Cohesion: 0.14
Nodes (7): Tira uma fotografia à matriz atual antes de a alterarmos., Callback acionado ao fechar a tela de Propriedades., Callback acionado quando o usuário confirma os dados do evento no Modal., Monta o formulário de volta injetando a nova coordenada no escopo correto., Regista ou atualiza um evento numa coordenada específica., balde_de_tinta(), Algoritmo iterativo de Flood Fill (Balde de Tinta). Varre e substitui células…

### Community 42 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 43 - "NovoMapaFormScreen"
Cohesion: 0.16
Nodes (8): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…, TabActivated

### Community 44 - "Regras de Implementação"
Cohesion: 0.17
Nodes (11): 1. Integração Textual + ECS (esper), 2. Gerenciamento de Foco e Visibilidade de Widgets, 3. Isolamento de Event Bubbling (Propagação de Eventos), 4. Agendamento Pró-Frame com `call_next()`, 5. Protocolo de Mensageria Customizada Externa, 6. Persistência e Backend, Competências Essenciais, Diretrizes do Sistema (+3 more)

### Community 45 - "GameStateManager"
Cohesion: 0.06
Nodes (27): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…, Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Base, Guarda o estado de execução de um jogo específico de um usuário. Desacoplado de…, SaveDB (+19 more)

### Community 46 - "Graphify Rule"
Cohesion: 0.22
Nodes (9): graphify-out/graph.json, GRAPH_REPORT.md, graphify CLI, graphify MCP, graphify-out Directory, Graphify Rule, graphify-out/wiki/index.md, Graphify Skill (+1 more)

### Community 47 - "GestorDeMapas"
Cohesion: 0.17
Nodes (7): GestorDeMapas, Any, Lê as configurações do RPG e aciona o gerador independente correspondente., Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form.

### Community 48 - "SecondaryMap"
Cohesion: 0.15
Nodes (10): ModalScreen, Pega o código hexadecimal da cor de fundo de um chão., Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap, Garante que os chãos devolvem as cores corretas para o motor de renderização. (+2 more)

### Community 49 - "README.md"
Cohesion: 0.18
Nodes (10): Apoie o projeto pela chave pix:, CharSistem é uma Engine de Criação de RPGs jogaveis de terminal feito em Python., Contexto do Projeto, Contexto do Projeto - Fase 2: Integração Cloud, Crie seus próprios mundos com cenários completos, personagens, magias, monstros., Este projeto tem potencial para se tornar um MMORPG de linha de comando!, Graficos totalmente feitos com emojis graças ao Textual: https://textual.textualize.io/, Jogue seu jogo e compartilhe com amigos. (+2 more)

### Community 50 - "GamePlayScreen"
Cohesion: 0.18
Nodes (6): GamePlayScreen, Screen, Limpa as escutas de eventos do Esper ao fechar a tela., O ponteiro central de transição. Recebe: {"mapa_id": 3, "pos_x": 15, "pos_y":…, Processador de Eventos Universal - Pipeline de 4 Etapas., Chamado quando a tela de batalha é fechada e voltamos ao GamePlayScreen.

### Community 51 - "TestInicializacaoCombate"
Cohesion: 0.20
Nodes (6): Testa o setup do combate via BattleSystem.iniciar_combate., Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.…, BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar., battle_sys.combate_ativo deve ser True após iniciar., Regra 5: Iniciativa = 1d6 + Agilidade. Com d6 fixo em 1, o personagem com maior…, TestInicializacaoCombate

### Community 52 - "GameEngineLoader"
Cohesion: 0.07
Nodes (26): NetworkPlayerComponent, Como a entidade se parece na interface., Identificador para jogadores que estão conectados via rede (multiplayer)., RenderComponent, GameEngineLoader, Any, Session, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos… (+18 more)

### Community 53 - "MensagemAnimada"
Cohesion: 0.27
Nodes (6): MensagemAnimada, Static, Processa a próxima mensagem da fila., Widget interno que gerencia a animação de uma única mensagem., Notificado quando uma mensagem termina de ser impressa., Avança um frame da animação a cada tique do timer.

### Community 54 - "Magia"
Cohesion: 0.16
Nodes (16): Efeito, Habilidade, Magia, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais ou Habilidade Mágica., criar_cobaia() (+8 more)

### Community 55 - "EventoDB"
Cohesion: 0.25
Nodes (4): EventoDB, Base, test_salvar_e_recuperar_arma_no_banco(), test_salvar_e_recuperar_evento_no_mapa()

### Community 56 - "on"
Cohesion: 0.39
Nodes (3): Changed, on, Sincroniza o self_switch da página atual quando o Select muda.

### Community 57 - "BattleScreen"
Cohesion: 0.07
Nodes (23): BattleScreen, Any, Screen, Tela de combate por turnos — suporta 1 a 4 inimigos. - Esta tela APENAS escuta…, Registra handlers do Esper, posiciona sprites e inicia o combate via…, Remove os handlers do Esper ao fechar a tela para evitar memory leaks., Habilita/desabilita o painel de ações conforme o estado do turno., Callback disparado pelo BattleSystem quando o combate é configurado. Inicializa… (+15 more)

### Community 58 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

### Community 59 - "test_logica_mapas.py"
Cohesion: 0.10
Nodes (17): padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., ComposeResult, fixture_db_session(), fixture, Garante que tuplas matemáticas viram strings JSON., Garante que strings JSON voltam a ser tuplas matemáticas. (+9 more)

### Community 60 - "MODIFICADORES"
Cohesion: 0.22
Nodes (8): 1 - PONTOS DE VIDA (hp MÁX.), 2 - PONTOS DE MANA, 3 - MODIFICADOR DE ATAQUE CORPO-A-CORPO, 4 - MODIFICADOR DE ATAQUE A DISTÂNCIA, ATAQUE, DEFESA / ESQUIVA, MODIFICADORES, **Não se importe com números quebrados

### Community 61 - ".log_mensagem"
Cohesion: 0.33
Nodes (3): Key, Injeta mensagens formatadas no painel lateral de logs., Handler disparado pelo EventSystem quando o comando 'iniciar_combate' é…

### Community 62 - ".processar_comando_terminal"
Cohesion: 0.33
Nodes (4): on, Submitted, Nativo do Textual. Captura o sinal emitido pelo ChoiceBox assim que o jogador…, Processa a caixa de comandos rápidos de texto.

### Community 63 - "CombatenteSprite"
Cohesion: 0.33
Nodes (3): CombatenteSprite, Widget de sprite do combatente com posição X animável via reactive. Seguindo o…, Sempre que x_pos mudar (via animação), atualiza o offset visual do sprite.

### Community 64 - "test_esper_integration.py"
Cohesion: 0.22
Nodes (6): fixture_db_session(), fixture, Garante que o método e'sperado pela tela limpa o mundo e popula as entidades., Cria um banco SQLite isolado em memória para cada teste., test_deve_atribuir_status_e_inventario_ao_jogador_no_esper(), test_deve_executar_carregar_engine_do_banco_com_esper()

### Community 65 - "copilot-instructions.md"
Cohesion: 0.25
Nodes (7): Conventions, Current Implementation Notes, Documentation References, Key Areas, Project Overview, Test and Development Commands, When to Use These Instructions

### Community 67 - ".processar_csv"
Cohesion: 0.25
Nodes (4): Callback após o utilizador clicar em algo no Menu Principal., Redireciona para importar ou exportar com base no nome do ficheiro., Transforma a matriz atual em texto com vírgulas e guarda no disco., Lê um ficheiro CSV do disco e transforma numa matriz para o nosso programa.

### Community 69 - "TestCriarEntidadeJogadorDeSave"
Cohesion: 0.38
Nodes (3): Hidrata a entidade do jogador a partir de dados do SaveDB. Args: entity_id:…, Verifica hidratação completa do Player a partir de dados do SaveDB., TestCriarEntidadeJogadorDeSave

### Community 72 - "Regra 5: Regras/Fórmulas Combate"
Cohesion: 0.29
Nodes (6): 1. Atributos Principais, 2. Fórmulas Status Derivados, 3. Teste Ataque/Defesa, 4. Dano/Absorção, 5. Simulação (Isolamento Arena), Regra 5: Regras/Fórmulas Combate

### Community 73 - "AISystem"
Cohesion: 0.18
Nodes (5): MovimentComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., AISystem, Processa movimento autônomo de monstros/NPCs a cada tick., Compatibilidade legado.

### Community 77 - "test_renderizador.py"
Cohesion: 0.33
Nodes (5): fixture, Garante o isolamento completo entre os testes limpando completamente todas as…, Garante que se não houver entidade no local, o objeto estático seja desenhado., restaurar_mundo_esper(), test_deve_renderizar_objeto_se_nao_houver_entidade()

### Community 78 - "Regra 4: Persistência Dados (SQLAlchemy)"
Cohesion: 0.33
Nodes (5): 1. Separação Ambientes (Prod vs. Teste), 2. Tipagem JSON, 3. Coordenadas, 4. Gerenciamento Assíncrono (Cloud), Regra 4: Persistência Dados (SQLAlchemy)

### Community 79 - "Criador e Mantenedor de testes"
Cohesion: 0.40
Nodes (4): Atendimento aos requisitos, Criador e Mantenedor de testes, Regras de trabalho, Verificação dos testes

### Community 80 - "RTK - Rust Token Killer (Google Antigravity)"
Cohesion: 0.40
Nodes (4): Meta Commands, RTK - Rust Token Killer (Google Antigravity), Rule, Why

### Community 81 - "VisualizadorImagem"
Cohesion: 0.40
Nodes (3): App, ComposeResult, VisualizadorImagem

### Community 83 - "Regra 2: Arquitetura ECS + Esper"
Cohesion: 0.40
Nodes (4): 1. Responsabilidades ECS, 2. Isolamento Headless, 3. Gerenciamento Cenas (WorldContext), Regra 2: Arquitetura ECS + Esper

### Community 84 - "Regra 3: Interface TUI (Textual)"
Cohesion: 0.40
Nodes (4): 1. Eventos Customizados, 2. Prevenção Conflitos Threads, 3. Gestão CSS e Layouts, Regra 3: Interface TUI (Textual)

### Community 85 - "Regra 7: Testes/TDD"
Cohesion: 0.40
Nodes (4): 1. Isolamento Dados Aleatórios, 2. Limpeza DB Teste, 3. Cobertura Mínima, Regra 7: Testes/TDD

### Community 86 - "TODO"
Cohesion: 0.40
Nodes (4): Fase atual;, Outras Fases, Próxima Fase, TODO

### Community 87 - "GameDev_Senior"
Cohesion: 0.50
Nodes (3): GameDev_Senior, Objetivo, Regras de trabalho

### Community 90 - "Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)"
Cohesion: 0.50
Nodes (3): 1. Separação de Camadas, 2. DDD + Mapper (Adapter), Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)

### Community 91 - "Regra 6: Interpretador Eventos (EventSystem)"
Cohesion: 0.50
Nodes (3): 1. Pipeline Execução, 2. Pilha Não-Bloqueante, Regra 6: Interpretador Eventos (EventSystem)

### Community 117 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

## Knowledge Gaps
- **125 isolated node(s):** `sischarlesrpg`, `Regras de Desenvolvimento do Projeto (SisCharlesRpg)`, `Diretrizes do Sistema`, `1. Integração Textual + ECS (esper)`, `2. Gerenciamento de Foco e Visibilidade de Widgets` (+120 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GameController` connect `GameController` to `ManagementMenuScreen`, `Arma`, `PositionComponent`, `MagiaDB`, `BattleSystem`, `ItemDB`, `TestGameControllerConsultas`, `AISystem`, `PersonagemDB`, `EventSystem`, `GestorDeMapas`, `GamePlayScreen`, `Personagem`, `GameEngineLoader`, `Magia`, `TestSimuladorArena`, `TestValidacaoEntradas`, `SimuladorCombate`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Why does `GamePlayScreen` connect `GamePlayScreen` to `InventarioMenuScreen`, `BarraStatusCombate`, `InventoryComponent`, `Arma`, `GameController`, `MagiaDB`, `TestTurnoJogador`, `BattleSystem`, `EventSystem`, `PersonagemDB`, `TestMultiplosInimigos`, `ChatLog`, `ManagementMenuScreen`, `PositionComponent`, `GameStateManager`, `TestInicializacaoCombate`, `GameEngineLoader`, `BattleScreen`, `TestResolucaoAcoes`, `.log_mensagem`, `.processar_comando_terminal`, `.atualizar_tela`, `.disparar_bifurcacao_visual`, `AISystem`, `TestIAInimigo`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `MapManagerScreen` connect `MapManagerScreen` to `ManagementMenuScreen`, `.processar_csv`, `MagiaDB`, `ConfirmacaoSalvarScreen`, `.carregar_arvore_de_mapas`, `ItemDB`, `.processar_pintura`, `test_editor_eventos.py`, `PersonagemDB`, `NovoMapaFormScreen`, `PropriedadesEventoFormScreen`, `GestorDeMapas`, `TestPropriedadesEventoFormScreen`, `MapaInterativo`, `PropriedadesFormScreen`, `EventoDB`, `test_logica_mapas.py`, `CatalogoTiles`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 72 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 72 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `InventoryComponent` (e.g. with `GameEngineLoader` and `EntityFactory`) actually correct?**
  _`InventoryComponent` has 51 INFERRED edges - model-reasoned connections that need verification._