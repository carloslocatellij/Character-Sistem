# Graph Report - SisCharlesRpg  (2026-08-05)

## Corpus Check
- 101 files · ~315,889 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1606 nodes · 3170 edges · 119 communities (105 shown, 14 thin omitted)
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 1082 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `97cb99bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InventoryComponent
- GamePlayScreen
- BattleScreen
- Raca
- GameController
- ItemFormScreen
- TestInicializacaoCombate
- EquipmentComponent
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
- MapaDB
- ChatLog
- Relatório: RPG Game Maker (Textual + engine)
- RenderComponent
- rpg_schemas.py
- TestMapearTipoEntidade
- AdicionarComandoScreen
- TestValidacaoEntradas
- SimuladorCombate
- MockMapLoader
- RamoEditorScreen
- ManagementMenuScreen
- JogoAtaqueApp
- MovementSystem
- conftest.py
- ConfirmacaoSalvarScreen
- RTK Commands by Workflow
- Selected
- .processar_pintura
- test_editor_eventos.py
- NovoMapaFormScreen
- Regras de Implementação
- GameStateManager
- Graphify Rule
- GestorDeMapas
- SecondaryMap
- README.md
- .obter_cor_fundo
- TestGameControllerConsultas
- GameEngineLoader
- avaliar_condicoes
- Efeito
- .ao_enviar_comando_chat
- on
- StatsComponent
- test_game_state_and_loader.py
- test_logica_mapas.py
- MODIFICADORES
- .obter_sistema_rede
- .carregar_engine_do_banco
- .atacar
- test_esper_integration.py
- copilot-instructions.md
- .atualizar
- .processar_csv
- TestTurnoJogador
- TestCriarEntidadeJogadorDeSave
- SaveDB
- CatalogoTiles
- Regra 5: Regras/Fórmulas Combate
- .processar_movimento_autonomo
- ._fechar_tela_combate
- .ao_confirmar_acao
- ._escrever_log
- test_renderizador.py
- Regra 4: Persistência Dados (SQLAlchemy)
- Criador e Mantenedor de testes
- RTK - Rust Token Killer (Google Antigravity)
- VisualizadorImagem
- RPGApp
- Regra 2: Arquitetura ECS + Esper
- Regra 3: Interface TUI (Textual)
- Regra 7: Testes/TDD
- TODO
- GameDev_Senior
- opencode.json
- .carregar_arvore_de_mapas
- Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)
- Regra 6: Interpretador Eventos (EventSystem)
- graphify.js
- .interagir
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
- TestResolucaoAcoes

## God Nodes (most connected - your core abstractions)
1. `GamePlayScreen` - 71 edges
2. `GameController` - 70 edges
3. `Personagem` - 67 edges
4. `InventoryComponent` - 60 edges
5. `MapManagerScreen` - 59 edges
6. `StatsComponent` - 52 edges
7. `BattleSystem` - 50 edges
8. `Raca` - 49 edges
9. `ClasseRPG` - 48 edges
10. `PersonagemDB` - 48 edges

## Surprising Connections (you probably didn't know these)
- `build_interactable_component()` --calls--> `InteractableComponent`  [INFERRED]
  rpg_api/tests/test_interaction_system.py → rpg_api/app/core/engine/components.py
- `test_deve_atribuir_status_e_inventario_ao_jogador_no_esper()` --calls--> `GameEngineLoader`  [INFERRED]
  rpg_api/tests/test_esper_integration.py → rpg_api/app/core/engine/engine_loader.py
- `GameController` --uses--> `Arma`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/core/entities/equipamentos.py
- `GameController` --uses--> `Armadura`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/core/entities/equipamentos.py
- `GameController` --uses--> `Escudo`  [INFERRED]
  rpg_api/app/controllers/game_controller.py → rpg_api/app/core/entities/equipamentos.py

## Import Cycles
- None detected.

## Communities (119 total, 14 thin omitted)

### Community 0 - "InventoryComponent"
Cohesion: 0.05
Nodes (49): Highlighted, InventoryComponent, Armazena os itens que o personagem está carregando., aplicar_desequipar_item(), aplicar_equipar_item(), aplicar_usar_item(), _eh_equipamento(), garantir_itens_padrao() (+41 more)

### Community 1 - "GamePlayScreen"
Cohesion: 0.07
Nodes (21): Key, NetworkPlayerComponent, Identificador para jogadores que estão conectados via rede (multiplayer)., AISystem, InteractionSystem, NetworkSystem, Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em…, Sistema responsável por sincronizar o estado de outros jogadores conectados… (+13 more)

### Community 2 - "BattleScreen"
Cohesion: 0.09
Nodes (16): BattleScreen, Any, Screen, Tela de combate por turnos — suporta 1 a 4 inimigos. Princípio fundamental…, Registra handlers do Esper, posiciona sprites e inicia o combate via…, Remove os handlers do Esper ao fechar a tela para evitar memory leaks., Habilita/desabilita o painel de ações conforme o estado do turno., Posiciona os sprites de inimigos de forma distribuída na arena antes da… (+8 more)

### Community 3 - "Raca"
Cohesion: 0.07
Nodes (39): Converte um modelo do SQLAlchemy para a Entidade pura do RPG., Arma, Armadura, Escudo, Item, Classe base para todos os itens do jogo., Herda de Item. Adiciona propriedades de ataque., Herda de Item. Adiciona propriedades de defesa base. (+31 more)

### Community 4 - "GameController"
Cohesion: 0.06
Nodes (24): GameController, Session, Método genérico para listar registros (RacaDB, ClasseRPGDB, etc), Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'., EquipScreen, Testes das funções de equipamento., Deve equipar uma arma na mão direita., Deve equipar um escudo na mão esquerda. (+16 more)

### Community 5 - "ItemFormScreen"
Cohesion: 0.09
Nodes (14): ArenaScreen, CharacterFormScreen, ClasseFormScreen, CreationScreen, ExplorerScreen, ItemFormScreen, MainScreen, ComposeResult (+6 more)

### Community 6 - "TestInicializacaoCombate"
Cohesion: 0.09
Nodes (18): BattleParticipantComponent, CombatStateComponent, Marca uma entidade como estando em combate ativo e armazena metadados do turno.…, Liga um identificador de participante ao contexto de uma batalha. Permite que o…, Testa os novos componentes ECS relacionados ao combate., CombatStateComponent deve inicializar com valores padrão corretos., BattleParticipantComponent deve aceitar tipo jogador/inimigo/rede., Testa o setup do combate via BattleSystem.iniciar_combate. (+10 more)

### Community 7 - "EquipmentComponent"
Cohesion: 0.15
Nodes (29): Enum, CollisionComponent, EquipmentComponent, InteractableComponent, MovimentComponent, PositionComponent, Define o comportamento autônomo (NPCs, Monstros, Pets)., Armazena o que está atualmente equipado no herói influenciando seus atributos. (+21 more)

### Community 8 - "ItemDB"
Cohesion: 0.06
Nodes (22): ItemDB, Base, Representa a tabela de Itens/Armas/Armaduras no Banco de Dados., test_salvar_e_recuperar_arma_no_banco(), Deve criar uma arma com dano e tipo de ataque., Deve criar um escudo com defesa_extra., Deve criar uma armadura com defesa., Deve criar uma classe com múltiplos caminhos. (+14 more)

### Community 9 - "Criador jogos RPG"
Cohesion: 0.06
Nodes (35): Acionar - (tecla Enter), Caminhos Magia, ClasseRPG, Comandos Evento Mais Usados, Criador jogos RPG, Criador Mapas, Editor gerador procedural mapas: ('caverna', 'vila', 'masmorra'), 3 camadas: (Terrenos, Objetos, Eventos)., Efeitos (+27 more)

### Community 10 - "EventSystem"
Cohesion: 0.11
Nodes (12): EventSystem, InventarySystem, Gerencia estoques de baús e o inventário do personagem., Sistema processador de eventos universais., Callback disparado pelo esper event_handler assim que o jogador interage com um…, Loop executor não-bloqueante que processa a pilha até o fim ou até uma…, Interpretador genérico e atômico de comandos estruturados do JSON., Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'. (+4 more)

### Community 11 - "PersonagemDB"
Cohesion: 0.11
Nodes (22): simular_arena(), ClasseRPGDB, PersonagemDB, Base, RacaDB, Tabela que armazena as Classes/Profissões do jogo. Args: nome: str,…, Tabela central que armazena os Personagens dos jogadores., Tabela que armazena as Raças disponíveis no jogo. Args: nome: str,… (+14 more)

### Community 12 - "DungeonGenerator"
Cohesion: 0.09
Nodes (15): circle, DungeonGenerator, Retorna as coordenadas do centro do retângulo., Verifica se este retângulo se sobrepõe a outro., Representa um círculo, usado para criar poços ou lagos., Retorna as coordenadas do centro do retângulo., Verifica se este círculo se sobrepõe a outro., Gerador Procedimental Puro. Totalmente agnóstico: não possui dependências de… (+7 more)

### Community 13 - "PropriedadesEventoFormScreen"
Cohesion: 0.12
Nodes (12): PropriedadesEventoFormScreen, Atualiza todos os widgets com os dados da página atual., Retorna o dict de condições da página atual, criando se não existir., Popula os widgets de condições com os dados da página atual., Renderiza a lista de comandos da página atual., Formulário principal que gerencia o JSON do evento com páginas e comandos.…, Callback do modal AdicionarSwitchScreen., Callback do modal AdicionarVariavelScreen. (+4 more)

### Community 14 - "CombatNetworkAdapter"
Cohesion: 0.09
Nodes (17): AcaoCombateRede, CombatNetworkAdapter, Any, Adapter de rede para combate multiplayer (PvP). Este módulo define os contratos…, Registra o callback que será invocado quando uma ação do oponente chegar pela…, [STUB] Conecta ao servidor de combate PvP. TODO: Implementar com:…, [STUB] Encerra a conexão com o servidor de combate. TODO: Implementar com:…, [STUB] Envia a ação do turno para o oponente via rede. TODO: Implementar com:… (+9 more)

### Community 15 - "TestPropriedadesEventoFormScreen"
Cohesion: 0.07
Nodes (15): Testa a lógica de estado da classe de formulário sem montar a TUI. O __init__…, Garante que um evento novo inicia com exatamente 1 página padrão., Garante que o ID do evento existente é preservado nos dados., Testa a lógica de adicionar uma nova página diretamente na lista., Garante que a proteção de página única funciona (lista permanece com 1 item)., Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes' na página…, Testa o callback ao_adicionar_switch(): garante que um switch é inserido…, Garante que passar None (usuário cancelou o modal) não altera as condições. (+7 more)

### Community 16 - "MapManagerScreen"
Cohesion: 0.10
Nodes (15): MapManagerScreen, Screen, Trata a resposta do utilizador no modal de confirmação., Tela principal do Gerenciador de Mapas. Responsável por exibir as ferramentas…, Gerencia os cliques na tela principal., Retrocede a matriz para o último estado guardado., Avança Terrenos e Objetos para o estado do futuro., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo). (+7 more)

### Community 17 - "EntityFactory"
Cohesion: 0.12
Nodes (15): EntityFactory, _extrair_stats_salvos(), Any, Cria e hidrata entidades no esper de forma centralizada e tipada. Todos os…, Hidrata a entidade do jogador a partir de um objeto de domínio (novo jogo).…, Adiciona os componentes comuns a todas as entidades de evento:…, Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa…, NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.… (+7 more)

### Community 18 - ".criar_entidade_evento"
Cohesion: 0.15
Nodes (6): Ponto de entrada principal para criação de entidades de evento. Determina o…, _criar_entidade_vazia(), Verifica que Monstros recebem StatsComponent e MovimentComponent…, Verifica que a correção do bug IndexError está funcionando., Cria uma entidade em branco no esper e retorna seu ID., TestCriarEntidadeMonstro

### Community 19 - "MapaInterativo"
Cohesion: 0.13
Nodes (12): MouseDown, MouseMove, MouseUp, MapaInterativo, Pintar, Message, Static, Mensagem enviada continuamente enquanto o mouse é arrastado. (+4 more)

### Community 20 - "Personagem"
Cohesion: 0.13
Nodes (13): Habilidade, Magia, Representa perícias ou golpes físicos especiais., Representa um encanto dos Caminhos Elementais., Personagem, Dano direto que ignora armadura (ex: veneno)., Adiciona um efeito à lista de ativos., Roda no fim do turno: processa venenos, curas e reduz duração. (+5 more)

### Community 21 - "TestMultiplosInimigos"
Cohesion: 0.10
Nodes (19): battle_sys(), classe_guerreiro(), eventos_capturados(), heroi(), inimigo(), fixture, raca_humana(), Testes do Sistema de Combate por Turnos — BattleSystem Testa o motor de combate… (+11 more)

### Community 22 - "PropriedadesFormScreen"
Cohesion: 0.10
Nodes (11): ArquivoCSVScreen, MenuAcoesScreen, PropriedadesFormScreen, Pressed, Captura os cliques dos botões., Tela flutuante para editar as propriedades de um mapa que já está na memória., Ao abrir, carrega os mapas do banco para o Select de Mapa Pai., Coleta o texto atual digitado nos campos para não perder o progresso. (+3 more)

### Community 23 - "MapaDB"
Cohesion: 0.13
Nodes (17): criar_e_salvar_mapa(), EventoDB, Base, CenarioDB, MapaDB, Base, Representa um jogo/campanha completo e independente criado por um usuário., test_salvar_e_recuperar_evento_no_mapa() (+9 more)

### Community 24 - "ChatLog"
Cohesion: 0.10
Nodes (15): ChatLog, MensagemAnimada, App, ComposeResult, Static, Submitted, Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso., Processa a próxima mensagem da fila. (+7 more)

### Community 25 - "Relatório: RPG Game Maker (Textual + engine)"
Cohesion: 0.09
Nodes (21): 1. Lógica Assíncrona, Pilha Comandos, 2. Componente `ChoiceBox`, Diretórios, Fase 1: Domínio, Fase 1: Prototipagem Visual, Fase 2: Banco/Infra, Fase 2: Integração/Anomalias, Fase 3: Arquitetura (ECS) (+13 more)

### Community 26 - "RenderComponent"
Cohesion: 0.12
Nodes (12): Como a entidade se parece na interface., RenderComponent, obter_pagina_ativa(), Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.…, Processa movimento autônomo de monstros/NPCs a cada tick., test_fluxo_completo_engine_manager(), Verifica a varredura decrescente de páginas (Regra 6)., Por varredura decrescente, sem switches, a última página é sempre retornada. (+4 more)

### Community 27 - "rpg_schemas.py"
Cohesion: 0.22
Nodes (14): BaseModel, post, criar_personagem(), criar_raca(), listar_personagens(), listar_racas(), get, Session (+6 more)

### Community 28 - "TestMapearTipoEntidade"
Cohesion: 0.17
Nodes (5): mapear_tipo_entidade(), Converte a string ``event_type`` do banco de dados no enum TipoEntidade.…, Garante que strings com espaços ou maiúsculas são toleradas., Verifica que strings do banco de dados são mapeadas corretamente., TestMapearTipoEntidade

### Community 29 - "AdicionarComandoScreen"
Cohesion: 0.12
Nodes (9): AdicionarComandoScreen, AdicionarSwitchScreen, AdicionarVariavelScreen, Pressed, Componente de Formulário de Eventos do Editor de Mapas. Contém todas as telas…, Modal simples para adicionar uma condição de Switch a uma página., Modal simples para adicionar uma condição de Variável numérica a uma página., Sub-formulário para gerar comandos baseados no tipo selecionado. (+1 more)

### Community 30 - "TestValidacaoEntradas"
Cohesion: 0.10
Nodes (12): Deve criar uma raça válida com todos os atributos., Deve listar todas as raças cadastradas., Verifica se todos os 5 atributos são salvos., Deve rejeitar atributos fora do intervalo 0-5., Testes de tratamento de erros., Teste edge case: atributos com tipo errado., Testa se um item pode ser equipado em dois slots (não deveria)., Deve lidar com nome vazio. (+4 more)

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

### Community 36 - "MovementSystem"
Cohesion: 0.18
Nodes (14): PlayerControlComponent, Uma flag que indica que esta entidade é controlada pelo teclado., MovementSystem, Sistema lógico encarregado de validar a física e colisões de movimentos., build_interactable_component(), create_player_control(), fixture, Reseta o mundo global do Esper antes de cada teste. (+6 more)

### Community 37 - "conftest.py"
Cohesion: 0.17
Nodes (15): classe_default(), item_arma(), item_armadura(), item_escudo(), personagem_default(), fixture, raca_default(), Fixture: Escudo de teste. (+7 more)

### Community 38 - "ConfirmacaoSalvarScreen"
Cohesion: 0.29
Nodes (4): NodeSelected, ConfirmacaoSalvarScreen, Tela que impede o utilizador de perder trabalho não salvo., Dispara quando o utilizador clica num mapa na barra lateral.

### Community 39 - "RTK Commands by Workflow"
Cohesion: 0.13
Nodes (14): Analysis & Debug (70-90% savings), Build & Compile (80-90% savings), Files & Search (60-75% savings), Git (59-80% savings), GitHub (26-87% savings), Golden Rule, Infrastructure (85% savings), JavaScript/TypeScript Tooling (70-90% savings) (+6 more)

### Community 40 - "Selected"
Cohesion: 0.17
Nodes (9): ChoiceBox, Message, Pressed, Widget, O Textual lê esta propriedade para validar seletores por ID., Monta a estrutura interna do widget., Trata o clique ou Enter no botão de confirmação., Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs. (+1 more)

### Community 41 - ".processar_pintura"
Cohesion: 0.16
Nodes (6): Tira uma fotografia à matriz atual antes de a alterarmos., Callback acionado ao fechar a tela de Propriedades., Callback acionado quando o usuário confirma os dados do evento no Modal., Monta o formulário de volta injetando a nova coordenada no escopo correto., balde_de_tinta(), Algoritmo iterativo de Flood Fill (Balde de Tinta). Varre e substitui células…

### Community 42 - "test_editor_eventos.py"
Cohesion: 0.16
Nodes (13): editor_vazio(), form_evento_existente(), form_novo_evento(), fixture, Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas…, Instância limpa do MapManagerScreen para testar lógica de dados., Instância do formulário de evento para um tile novo (sem dados existentes)., Instância do formulário com dados pré-existentes de um evento salvo no banco. (+5 more)

### Community 43 - "NovoMapaFormScreen"
Cohesion: 0.21
Nodes (7): NovoMapaFormScreen, Changed, on, Executado quando a tela é carregada. Garante que apenas a caixa certa está…, Busca os mapas no banco de dados e preenche o menu de seleção., Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado., Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.…

### Community 44 - "Regras de Implementação"
Cohesion: 0.17
Nodes (11): 1. Integração Textual + ECS (esper), 2. Gerenciamento de Foco e Visibilidade de Widgets, 3. Isolamento de Event Bubbling (Propagação de Eventos), 4. Agendamento Pró-Frame com `call_next()`, 5. Protocolo de Mensageria Customizada Externa, 6. Persistência e Backend, Competências Essenciais, Diretrizes do Sistema (+3 more)

### Community 45 - "GameStateManager"
Cohesion: 0.21
Nodes (4): GameStateManager, any, Gerenciador de Estado Global e Persistência de Sessão (Saves). Adaptado para…, Busca a sessão persistida no BD e restaura os dicionários de controle da…

### Community 46 - "Graphify Rule"
Cohesion: 0.22
Nodes (9): graphify-out/graph.json, GRAPH_REPORT.md, graphify CLI, graphify MCP, graphify-out Directory, Graphify Rule, graphify-out/wiki/index.md, Graphify Skill (+1 more)

### Community 47 - "GestorDeMapas"
Cohesion: 0.17
Nodes (7): GestorDeMapas, Any, Lê as configurações do RPG e aciona o gerador independente correspondente., Adapter que conecta o submódulo independente 'dungeon_gen' com o ecossistema e…, Converte a matriz do mapa num formato string CSV., Reconstrói a matriz do mapa a partir de uma string CSV., Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form.

### Community 48 - "SecondaryMap"
Cohesion: 0.24
Nodes (6): ModalScreen, Um mostrador de mapa para coisas como pegar coordenada., Executa automaticamente quando o Gerenciador de Mapas abre., Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)., Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2)., SecondaryMap

### Community 49 - "README.md"
Cohesion: 0.18
Nodes (10): Apoie o projeto pela chave pix:, CharSistem é uma Engine de Criação de RPGs jogaveis de terminal feito em Python., Contexto do Projeto, Contexto do Projeto - Fase 2: Integração Cloud, Crie seus próprios mundos com cenários completos, personagens, magias, monstros., Este projeto tem potencial para se tornar um MMORPG de linha de comando!, Graficos totalmente feitos com emojis graças ao Textual: https://textual.textualize.io/, Jogue seu jogo e compartilhe com amigos. (+2 more)

### Community 50 - ".obter_cor_fundo"
Cohesion: 0.17
Nodes (9): padronizar_largura_tile(), Verifica a largura visual do caractere e adapta o preenchimento com base nas…, Pega o código hexadecimal da cor de fundo de um chão., ComposeResult, Garante que caracteres magros ganham espaço e emojis largos ficam iguais., Garante que os chãos devolvem as cores corretas para o motor de renderização., test_catalogo_cores_fundo(), test_padronizar_largura_tile() (+1 more)

### Community 51 - "TestGameControllerConsultas"
Cohesion: 0.25
Nodes (5): Testes das funções de consulta., Deve retornar um personagem válido pelo ID., Deve retornar None para ID inexistente., Deve retornar lista vazia quando não há classes., TestGameControllerConsultas

### Community 52 - "GameEngineLoader"
Cohesion: 0.20
Nodes (8): GameEngineLoader, Gerencia o ciclo de vida do motor ECS utilizando contextos isolados de mundos…, Verifica se jogadores remotos podem ser adicionados, atualizados e removidos da…, Verifica se um jogador remoto bloqueia a movimentação física., Garante que jogadores de rede não corrompam o save-game persistido., test_deve_adicionar_e_atualizar_jogador_rede(), test_deve_excluir_jogadores_rede_do_save_local(), test_jogador_rede_deve_bloquear_movimento()

### Community 53 - "avaliar_condicoes"
Cohesion: 0.27
Nodes (8): avaliar_condicoes(), _checar_item_inventario(), obter_id_referencia_evento(), Any, event_evaluator.py Centraliza a lógica de avaliação de condições e filtragem de…, Verifica se o componente de inventário possui o item especificado pelo nome., Obtém o ID virtual estável do banco de dados para a entidade de evento (evt.id…, Avalia se todas as condições declaradas em uma página de evento são atendidas.

### Community 54 - "Efeito"
Cohesion: 0.31
Nodes (7): Efeito, Representa uma condição temporária aplicada a um personagem., Aplica o efeito no alvo a cada turno., criar_cobaia(), test_efeito_buff_atributo(), test_efeito_dano_continuo(), test_lancamento_de_magia()

### Community 55 - ".ao_enviar_comando_chat"
Cohesion: 0.20
Nodes (6): on, Submitted, Chamado pelo interpretador de comandos quando atinge uma bifurcação. Instancia…, Remove o widget da tela de forma limpa., Nativo do Textual. Captura o sinal emitido pelo ChoiceBox assim que o jogador…, Processa a caixa de comandos rápidos de texto.

### Community 56 - "on"
Cohesion: 0.31
Nodes (4): Changed, on, Sincroniza o self_switch da página atual quando o Select muda., Sincroniza o item_requerido da página atual quando o Input muda.

### Community 57 - "StatsComponent"
Cohesion: 0.08
Nodes (22): Guarda os atributos de combate e informações vitais do personagem., StatsComponent, BattleSystem, O BattleSystem não precisa de processamento periódico — opera sob demanda., Motor lógico puro de combate por turnos. Opera exclusivamente sobre objetos…, Alias de retrocompatibilidade: retorna o primeiro inimigo da lista., Configura os combatentes com deepcopy e dispara o evento de início. O deepcopy…, AcaoConfirmada (+14 more)

### Community 58 - "test_game_state_and_loader.py"
Cohesion: 0.22
Nodes (9): fixture_db_session(), fixture, Garante que o GameEngineLoader consegue ler o cenário do banco e montar o Esper., Testa se os seletores lógicos (Switches) persistem dinamicamente através do…, Cria um banco SQLite isolado em memória para cada teste., Garante isolamento absoluto limpando a memória do Esper ECS., reset_esper_antes_de_cada_teste(), test_deve_inicializar_engine_loader_e_popular_mundo_com_esper() (+1 more)

### Community 59 - "test_logica_mapas.py"
Cohesion: 0.20
Nodes (9): fixture_db_session(), fixture, Garante que tuplas matemáticas viram strings JSON., Garante que strings JSON voltam a ser tuplas matemáticas., Cria um banco SQLite isolado em memória para cada teste de mapas., Garante que a consulta base do banco retorna os mapas para o gerenciador., test_desempacotar_objetos_do_banco(), test_deve_listar_mapas_cadastrados_no_banco() (+1 more)

### Community 60 - "MODIFICADORES"
Cohesion: 0.22
Nodes (8): 1 - PONTOS DE VIDA (hp MÁX.), 2 - PONTOS DE MANA, 3 - MODIFICADOR DE ATAQUE CORPO-A-CORPO, 4 - MODIFICADOR DE ATAQUE A DISTÂNCIA, ATAQUE, DEFESA / ESQUIVA, MODIFICADORES, **Não se importe com números quebrados

### Community 61 - ".obter_sistema_rede"
Cohesion: 0.22
Nodes (5): Any, Busca o processador de rede (NetworkSystem) registrado no mundo ativo., Spawna ou atualiza um jogador remoto no mundo atual utilizando o NetworkSystem., Remove o jogador remoto do mundo atual usando o NetworkSystem., Atualiza a posição de um jogador remoto usando o NetworkSystem.

### Community 62 - ".carregar_engine_do_banco"
Cohesion: 0.22
Nodes (5): Session, Fotografa os componentes da entidade 1., Garante que a entidade 1 do mundo atual herde as estatísticas nômades do herói…, 🌟 Traduz o dicionário de objetos com chaves string 'y,x' para tuplas de…, Alterna ou inicializa o mundo do mapa alvo, sincronizando snapshots in RAM e…

### Community 63 - ".atacar"
Cohesion: 0.31
Nodes (5): Any, Utilitário interno para rolagens de dados (Domain Service embutido)., 1d6 + Agilidade + Defesa do Escudo (se houver)., Processa a absorção de dano (1d6 por Res + Armadura)., Realiza a mecânica completa de ataque contra um alvo.

### Community 64 - "test_esper_integration.py"
Cohesion: 0.22
Nodes (6): fixture_db_session(), fixture, Garante que o método e'sperado pela tela limpa o mundo e popula as entidades., Cria um banco SQLite isolado em memória para cada teste., test_deve_atribuir_status_e_inventario_ao_jogador_no_esper(), test_deve_executar_carregar_engine_do_banco_com_esper()

### Community 65 - "copilot-instructions.md"
Cohesion: 0.25
Nodes (7): Conventions, Current Implementation Notes, Documentation References, Key Areas, Project Overview, Test and Development Commands, When to Use These Instructions

### Community 66 - ".atualizar"
Cohesion: 0.25
Nodes (3): Atualiza os valores e redesenha as barras., Atualiza a barra de HP do herói sempre que o valor reativo muda., Callback disparado pelo BattleSystem quando o combate é configurado. Inicializa…

### Community 67 - ".processar_csv"
Cohesion: 0.25
Nodes (4): Callback após o utilizador clicar em algo no Menu Principal., Redireciona para importar ou exportar com base no nome do ficheiro., Transforma a matriz atual em texto com vírgulas e guarda no disco., Lê um ficheiro CSV do disco e transforma numa matriz para o nosso programa.

### Community 68 - "TestTurnoJogador"
Cohesion: 0.25
Nodes (5): Testa a execução de ações do jogador via BattleSystem., executar_acao_jogador('ataque') deve disparar 'turno_calculado' com…, executar_acao_jogador deve ignorar quando combate_ativo=False., Quando o inimigo morre no turno do jogador, deve disparar 'combate_encerrado'., TestTurnoJogador

### Community 69 - "TestCriarEntidadeJogadorDeSave"
Cohesion: 0.38
Nodes (3): Hidrata a entidade do jogador a partir de dados do SaveDB. Args: entity_id:…, Verifica hidratação completa do Player a partir de dados do SaveDB., TestCriarEntidadeJogadorDeSave

### Community 70 - "SaveDB"
Cohesion: 0.33
Nodes (5): Captura o estado dos seletores e gera um snapshot das entidades vivas no Esper…, Base, Guarda o estado de execução de um jogo específico de um usuário. Desacoplado de…, SaveDB, UsuarioDB

### Community 71 - "CatalogoTiles"
Cohesion: 0.29
Nodes (5): CatalogoTiles, Verifica se o pincel é um terreno, um objeto estático ou um evento lógico., Registo central que define as categorias e propriedades visuais dos emojis., Garante que o sistema diferencia corretamente chãos de objetos., test_catalogo_tiles_tipos()

### Community 72 - "Regra 5: Regras/Fórmulas Combate"
Cohesion: 0.29
Nodes (6): 1. Atributos Principais, 2. Fórmulas Status Derivados, 3. Teste Ataque/Defesa, 4. Dano/Absorção, 5. Simulação (Isolamento Arena), Regra 5: Regras/Fórmulas Combate

### Community 73 - ".processar_movimento_autonomo"
Cohesion: 0.33
Nodes (3): Calcula a nova posição de uma entidade e aplica se for válida. Retorna True se…, Compatibilidade legado., invoke_movement()

### Community 74 - "._fechar_tela_combate"
Cohesion: 0.33
Nodes (3): Callback disparado quando o combate termina (vitória ou derrota)., Encerra a tela de combate e devolve o controle à tela principal., Sincroniza o status atual (HP/Mana) e equipamentos do herói da batalha de volta…

### Community 75 - ".ao_confirmar_acao"
Cohesion: 0.40
Nodes (3): on, Pressed, Captura a ação selecionada pelo jogador no RadioSet e o alvo no TargetRadioSet.…

### Community 76 - "._escrever_log"
Cohesion: 0.40
Nodes (3): Callback disparado pelo BattleSystem após calcular um turno. Atualiza os…, Escreve uma linha formatada no log de batalha., Formata e escreve o relatório narrativo de um turno no log.

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

### Community 82 - "RPGApp"
Cohesion: 0.40
Nodes (3): action_start_stop_music(), App, RPGApp

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

### Community 88 - "opencode.json"
Cohesion: 0.50
Nodes (3): plugin, $schema, .opencode/plugins/graphify.js

### Community 90 - "Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)"
Cohesion: 0.50
Nodes (3): 1. Separação de Camadas, 2. DDD + Mapper (Adapter), Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)

### Community 91 - "Regra 6: Interpretador Eventos (EventSystem)"
Cohesion: 0.50
Nodes (3): 1. Pipeline Execução, 2. Pilha Não-Bloqueante, Regra 6: Interpretador Eventos (EventSystem)

### Community 117 - "TestIAInimigo"
Cohesion: 0.20
Nodes (6): Testa o comportamento de tomada de decisão da IA do inimigo., Com HP > 30%, a IA deve preferir atacar (sem chance de cura)., Com HP < 30% e random < 0.4, a IA deve tentar se curar., O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'., Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com…, TestIAInimigo

### Community 118 - "TestResolucaoAcoes"
Cohesion: 0.25
Nodes (5): Testa o mapeamento de ações para métodos do Personagem de domínio., _resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e…, Ação desconhecida deve cair no fallback de ataque desarmado., Ação 'cura' da IA deve retornar dano_causado=0., TestResolucaoAcoes

## Knowledge Gaps
- **127 isolated node(s):** `$schema`, `.opencode/plugins/graphify.js`, `sischarlesrpg`, `Regras de Desenvolvimento do Projeto (SisCharlesRpg)`, `Diretrizes do Sistema` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GamePlayScreen` connect `GamePlayScreen` to `InventoryComponent`, `BattleScreen`, `Raca`, `GameController`, `ItemFormScreen`, `TestInicializacaoCombate`, `EquipmentComponent`, `EventSystem`, `PersonagemDB`, `TestMultiplosInimigos`, `MapaDB`, `ChatLog`, `ManagementMenuScreen`, `MovementSystem`, `Selected`, `GameStateManager`, `GameEngineLoader`, `.ao_enviar_comando_chat`, `StatsComponent`, `TestTurnoJogador`, `RPGApp`, `TestIAInimigo`, `TestResolucaoAcoes`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `GameController` connect `GameController` to `GamePlayScreen`, `ManagementMenuScreen`, `Raca`, `ItemFormScreen`, `ItemDB`, `PersonagemDB`, `GestorDeMapas`, `RPGApp`, `TestGameControllerConsultas`, `Personagem`, `GameEngineLoader`, `MapaDB`, `TestValidacaoEntradas`, `SimuladorCombate`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `CatalogoTiles` connect `CatalogoTiles` to `GamePlayScreen`, `RamoEditorScreen`, `MovementSystem`, `ConfirmacaoSalvarScreen`, `EventSystem`, `NovoMapaFormScreen`, `PropriedadesEventoFormScreen`, `MapManagerScreen`, `SecondaryMap`, `.obter_cor_fundo`, `PropriedadesFormScreen`, `StatsComponent`, `AdicionarComandoScreen`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `GamePlayScreen` (e.g. with `GameController` and `EquipmentComponent`) actually correct?**
  _`GamePlayScreen` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `GameController` (e.g. with `Arma` and `Armadura`) actually correct?**
  _`GameController` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `Personagem` (e.g. with `GameController` and `AISystem`) actually correct?**
  _`Personagem` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `InventoryComponent` (e.g. with `GameEngineLoader` and `EntityFactory`) actually correct?**
  _`InventoryComponent` has 49 INFERRED edges - model-reasoned connections that need verification._