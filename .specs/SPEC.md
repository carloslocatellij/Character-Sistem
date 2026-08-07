# Especificação Técnica: Sistema de RPG de Mesa
1. Visão Geral

Projeto motor RPG online para criação de jogos por geração de Cenários compartilháveis. Python, Arquitetura Limpa, DDD, TDD. Garante desacoplamento entre regras, persistência dados, interface.

- Criação Mapas aninhados
- Criação Personagens (Raças, Classes, Itens, Habilidades)
- Simulação batalhas RPG turno
- Jogar

2. Arquitetura Sistema

Camadas independentes:

    Domínio (core): Regras puras RPG (Classes, Fórmulas, Simulador). Sem dependências externas.

    Persistência (models / db): Gerencia BD relacional via SQLAlchemy (ORM).

    Interface (CLI / API): Interage utilizador, usa Padrões Mapeamento (Adapters) traduzir dados banco para domínio.

3. Entidades Domínio
3.1. Raça

Representa espécie personagem.

    Propriedades: nome, emoji (visual).

    Mecânica: Dicionário `bonus_atributos` (ex: `{"forca": 2, "agilidade": -1}`) modifica atributos base personagem.

3.2. ClasseRPG

Representa treinamento/profissão personagem.

    Propriedades: nome, lista habilidades, dicionário `bonus_atributos`.

    Caminhos Mágicos: Dicionário `bonus_caminhos` (ex: `{"fogo": 1, "trevas": 2}`) dita aptidão para aprender feitiços.

3.3. Equipamentos (Herança)

Herança a partir classe base `Item`.

    Item: nome, peso, emoji.

    Arma (herda Item): Dano numérico, tipo ("corpo" ou "distancia").

    Armadura (herda Item): Defesa.

    Escudo (herda Item): Defesa extra.


3.4. Personagem (Entidade Central)

Entidade acionadora jogo. Composição agrega Raça e Classe.

    Atributos Base vs Totais: Armazena atributos puros (0 a 5: Força, Agilidade, Resistência, Percepção, Exuberância). Calcula "Atributos Totais" somando bônus Raça e Classe.

    Status Derivados: Calcula automaticamente (e recalcula alterações) Pontos Vida (hp), Pontos Mana (mp), Modificadores Ataque via fórmulas pré-definidas.

    Inventário/Slots: Campos equipamentos (`mao_direita`, `mao_esquerda`, `armadura`), listas inventário geral.

    Estado: Listas dinâmicas `efeitos_ativos` (venenos, buffs) processados cada turno, `magias_conhecidas`.


3.5. Mapas (Base ambiente jogo)

Composta camada terreno, camada objetos, eventos. Mapas aninhados campo `mapa_pai`.

    Terrenos: transitáveis (chão), bloqueio (paredes, água).

    Camada objetos: bloqueia passagem. Truque background para efeito visual.

    Eventos: em `EventosDB`, instanciados com mapa, sobrepostos, acionáveis via parâmetros.

3.6. Eventos (Centro Mecânica Jogo)

Emojis posicionados no mapa, parâmetros passados ao `EventSystem` ao acionar.

    Parâmetros permitem criação/programação visual evento como entidade única.

    Eventos clássicos:
        - teleporte (portas, cidades, cavernas): muda mapa.
        - baús: modifica inventário personagem.
        - Npcs: dispara mensagens, escolhas, muda variáveis.

    Exemplos em `modelo_de_parametros_eventos.json`.


4. Regras Negócio e Mecânicas

4.1. Sistema de Aquisição e Lançamento de Magias/Habilidades:

    Modelagem da persistência: utilizar tabelas com colunas JSON para modificadores e efeitos temporários criar tabelas para magias e para efeitos; A entidade ClasseRPGDB que compõe o Personagem recebe Magias na coluna habilidades.
    Magias podem causar efeitos: sono, veneno, lentidão, atordoado, regenerar.
    Efeitos são estados temporarios dos personagens ou monstros: Duram x turnos.
    A cada turno ativo o efeito pode: causar y de dano, curar y de hp, atributo fica y ponto a cima ou abaixo, deixa de atacar x turnos (dormindo), ataca aleatorio (louco), proteção ou fraqueza contra tipos de magia ou habilidades.
    Magias ou habilidade podem causar dano em área (> de 1 inimigo).
    Habilidades podem ter maior chance de crítico, ignorar bonus de defeza, contra-ataque, tentativa dupla ou tripla de ataque com taxas menores de acerto.
    Magias possuem requisitos (ex: `{"água": 2}`, Exuberância >= 2) para serem aprendidas/ adquiridas/ executadas.
    Regra Estrita: Ao ensinar magia, validar "Caminhos Magia Totais" (Base + Bônus Classe). Se requisitos não atingidos impede aprendizado/execução da magia/habilidade.
    1. **Modelagem de Persistência (SQLAlchemy):**
   - **`EfeitoDB` (Tabela `efeitos`):** Estados temporários (sono, veneno, lentidão, atordoado, regenerar) durando $x$ turnos. O campo `configuracoes` (JSON) define o comportamento do "tick" por turno: causar/curar $y$ de dano/HP, alterar atributos temporariamente, deixar de atacar por $x$ turnos (sono), atacar de forma aleatória (louco) ou conferir proteção/fraqueza elemental.
   - **`MagiaDB` (Tabela `magias`):** Metadados de magias e habilidades. Inclui flags de `dano_area` (alvos múltiplos), as propriedades de combate (taxa de crítico ampliada, ignorar bônus de defesa, contra-ataque, chance de ataques múltiplos com penalidade de acerto) e o campo JSON de `requisitos`.

2. **Lógica em Memória (Esper ECS):**
   - **`ActiveEffectsComponent`:** Dataclass pura que armazena e monitora em tempo de execução os efeitos aplicados nas entidades e seus turnos de duração restantes.
   - **Sistemas de Combate e Atualização:** Processam os "ticks" dos efeitos ativos e aplicam suas respectivas alterações lógicas na RAM a cada turno da rodada.

3. **Validação Estrita de Requisitos:**
   - Crie uma rotina de verificação matemática impeditiva que valida se o personagem atende aos pré-requisitos lógicos e de atributos do JSON da magia:
     $$\text{Caminhos Totais} = \text{Caminhos Base (Personagem)} + \text{Bônus da Classe}$$
   - Caso os "Caminhos Magia Totais" ou os atributos requeridos do herói (ex: Exuberância $\ge 2$) sejam insuficientes, impeça o aprendizado ou a execução de forma absoluta.


4.2. Fluxo Combate

    Iniciativa: `1d6 + Agilidade` (desempates automáticos).

    Ataque: Atacante rola `3d6 + Modificador Ataque` vs Defesa alvo (`1d6 + Agilidade + Bônus Escudo`).

    Dano: Se acertar, dano bruto `1d6` por ponto atributo base (Força/Agilidade) + dano arma.

    Absorção: Alvo reduz dano bruto rolando `1d6` por ponto Resistência + defesa Armadura.


5. Simulação Batalhas

Módulo estritamente isolado, aceita duas equipes (listas `Personagem`).

    Batalha Única (Arena): Simula turno a turno, alvos aleatórios entre vivos. Retorna dicionário eventos, vencedor, log combate.

    Simulador Estatístico (Múltiplas Batalhas): Recebe N batalhas (Padrão: 100). Executa simulações silenciosas.

    Mecânica Isolamento: Simulador usa `deepcopy` personagens originais antes cada rodada, garante hp/mp máximos, evita acúmulo ferimentos entre simulações.

    Relatório: Agrupa estatísticas personagem (Tentativas, Acertos, Dano Causado, Abates, Taxa Sobrevivência).

6. Persistência e Banco Dados (ORM)

    SQLAlchemy: Mapeamento relacional.

    Separação Ambientes: Variável `TEST_VERSION`. Se verdadeira, usa bancos SQLite isolados para testes (`rpg_teste.db`), protege dados produção.

    Tipagem JSON: Dicionários/listas Domínio (bônus, requisitos) salvos colunas JSON.

    Isolamento Dados Derivados: Banco armazena apenas Atributos Base. Cálculos vida, mana, ataque má.
