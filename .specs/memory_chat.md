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
├── .env                      # Variáveis de ambiente (TEST_VERSION, DATABASE_URLs)
├── main_cli.py               # Interface de Linha de Comando e Tradutor (Mapper)
├── pytest.ini                # Configuração do caminho de execução do Pytest
├── app/
│   ├── core/                 # DOMÍNIO: Regras puras do jogo (Sem acesso a DB)
│   │   ├── equipamentos.py   # Dataclasses de Item, Arma, Armadura, Escudo
│   │   ├── habilidades_magias.py # Dataclasses de Efeito, Habilidade, Magia
│   │   ├── personagens.py    # Entidades Raca, ClasseRPG, Personagem (Cálculos e Combate)
│   │   └── simulador.py      # Simulador de Batalhas únicas e estatísticas múltiplas
│   ├── db/                   # INFRA: Configuração de persistência
│   │   └── database.py       # Engine do SQLAlchemy e roteamento Teste/Prod
│   └── models/               # ESQUEMAS DO BANCO: Tabelas do Banco de Dados
│       ├── equipamentos_db.py# Modelos de itens (Single Table com coluna 'categoria')
│       └── personagens_db.py # Modelos RacaDB, ClasseRPGDB, PersonagemDB (Foreign Keys)
└── tests/                    # SUÍTE DE TESTES (TDD)
    ├── test_equipamentos.py
    ├── test_habilidades_magias.py
    ├── test_personagens.py
    ├── test_simulador.py
    ├── test_database.py
    └── test_personagens_db.py

## Passo a Passo da Implementação Realizada
### Fase 1: Núcleo de Domínio (Regras de Negócio)

    Sistema de Equipamentos: Criação de hierarquia base usando @dataclass (Item base para Arma, Armadura e Escudo).

    Sistema de Efeitos e Magias: * Criação de Efeito (dano/cura contínua, buffs/debuffs temporários).

        Criação de Magia e Habilidade. Implementado sistema de requisitos de magia baseado num dicionário de Caminhos Elementais (ex: {"fogo": 2}).

    Entidade Personagem: * Composição pura: Recebe objetos de Raca e ClasseRPG.

        Cálculo automático de PV, PM e Modificadores baseados nas fórmulas do MANUAL.md.

        Métodos de combate (atacar, receber_dano, lancar_magia) desenvolvidos com Design Orientado a Eventos (retornam dicionários com os resultados em vez de imprimir na tela).

        Controle rígido de exceções (ValueError) ao tentar aprender magias sem requisitos.

    Simulador de Combate: * Criação da classe SimuladorCombate responsável por gerir iniciativa e fluxo de turnos até a morte de uma das equipes.

        Geração de estatísticas por personagem (Dano causado, Abates, Taxa de Sobrevivência). Uso massivo de deepcopy para garantir simulações independentes.

### Fase 2: Banco de Dados e Infraestrutura

    Separação de Ambientes: Implementado app/db/database.py que lê TEST_VERSION do .env. Garante que testes automatizados usem rpg_teste.db sem sujar o banco de produção.

    Modelagem ORM: * Uso de colunas tipo JSON para armazenar de forma limpa os dicionários de bônus de atributos e caminhos de magia no SQLite.

        Criação do PersonagemDB com ForeignKeys obrigatórias para RacaDB e ClasseRPGDB.

        Resolução de AmbiguousForeignKeys na conexão de Equipamentos, especificando as FKs para mao_direita, mao_esquerda e armadura.

        Adoção de prática de salvar apenas "Status Base" no banco; cálculos derivados são responsabilidade exclusiva da classe do Domínio ao ser instanciada.

### Fase 3: Interface e Tradução (Adapter)

    CLI Interativa: Criação do main_cli.py para interação local, permitindo forjar raças, classes e personagens, e montar a Arena.

    Padrão Mapper: Implementada a função converter_para_dominio no CLI. Decisão arquitetural crucial: Extrai os dados puros das instâncias do Banco (SQLAlchemy) e injeta-os nos construtores das Entidades do Domínio (Personagem), garantindo isolamento entre camadas.

### Fase 4: Qualidade e Testes (TDD)

    Implementada suíte com 14+ testes.

    Uso do pytest rodando como módulo (python -m pytest) para evitar problemas de PYTHONPATH.

    Uso de monkeypatch para fixar resultados da função _rolar_d6 interna, permitindo testes precisos em regras de acerto e dano sem a interferência da aleatoriedade natural do RPG.

    Injeção e limpeza dinâmica de banco de dados (setup_module / teardown_module) para testes isolados de infraestrutura.