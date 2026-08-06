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
4.1. Validação Magias/Habilidades

    Modelar estas especificações abaixo no sistema: Será necessário criar tabelas para entidades magia e efeito;
    Magias podem causar efeitos: sono, veneno, lentidão, atordoado, regenerar.
    Efeitos são estados temporarios dos personagens ou monstros: Duram x turnos.
    A cada turno ativo o efeito pode: causar y de dano, curar y de hp, atributo fica y ponto a cima ou abaixo, deixa de atacar x turnos (dormindo), ataca aleatorio (louco), proteção ou fraqueza contra tipos de magia ou habilidades.
    Magias ou habilidade podem causar dano em área (> de 1 inimigo).
    Habilidades podem ter maior chance de crítico, ignorar bonus de defeza, contra-ataque, tentativa dupla ou tripla de ataque com taxas menores de acerto.
    Magias possuem requisitos (ex: `{"água": 2}`, Exuberância >= 2) para serem aprendidas/ adquiridas/ executadas.
    Regra Estrita: Ao ensinar magia, validar "Caminhos Magia Totais" (Base + Bônus Classe). Se requisitos não atingidos impede aprendizado/execução da magia/habilidade.

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
