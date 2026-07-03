# Especificação Técnica: Sistema de RPG de Mesa
1. Visão Geral

Este projeto é um motor (engine) online para criação de jogos de RPG por meio da geração de Cenários completos compartilhaveis. Desenvolvido em Python, o sistema adota princípios de Arquitetura Limpa (Clean Architecture) e Domain-Driven Design (DDD) Test-Driven Design (TDD), garantindo total desacoplamento entre as regras do jogo, a persistência de dados (Banco de Dados) e a interface do utilizador.

- Criação de Mapas aninhados
- Criação de Personagens (Raças, Classes, Itens, Habilidades)
- Simulação de batalhas de RPG de mesa baseado em turnos
- Jogar

2. Arquitetura do Sistema

O sistema é dividido nas seguintes camadas independentes:

    Domínio (core): Contém as regras puras do RPG (Classes, Fórmulas, Simulador). Não possui dependências externas.

    Persistência (models / db): Gerencia o banco de dados relacional utilizando SQLAlchemy (ORM).

    Interface (CLI / API): Interage com o utilizador e utiliza Padrões de Mapeamento (Adapters) para traduzir dados do banco para o domínio.

3. Entidades de Domínio
3.1. Raça

Representa a espécie do personagem.

    Propriedades: nome, emoji (representação visual).

    Mecânica: Possui um dicionário bonus_atributos (ex: {"forca": 2, "agilidade": -1}) que modifica permanentemente os atributos base do personagem.

3.2. ClasseRPG

Representa o treinamento/profissão do personagem.

    Propriedades: nome, lista de habilidades, dicionário bonus_atributos.

    Caminhos Mágicos: Possui um dicionário bonus_caminhos (ex: {"fogo": 1, "trevas": 2}) que dita a aptidão do personagem para aprender feitiços específicos.

3.3. Equipamentos (Herança)

Sistema baseado em herança a partir de uma classe base Item.

    Item: Possui nome, peso e emoji.

    Arma (herda Item): Adiciona dano numérico e tipo ("corpo" ou "distancia").

    Armadura (herda Item): Adiciona pontuação de defesa.

    Escudo (herda Item): Adiciona pontuação de defesa_extra.


3.4. Personagem (Entidade Central)

Entidade acionadora do jogo. Utiliza composição para agregar Raça e Classe.

    Atributos Base vs Totais: Armazena os atributos puros (0 a 5: Força, Agilidade, Resistência, Percepção, Exuberância) e calcula os "Atributos Totais" somando os bônus da Raça e Classe.

    Status Derivados: Calcula automaticamente (e recalcula quando sofre alterações) os Pontos de Vida (hp), Pontos de Mana (mp) e Modificadores de Ataque utilizando fórmulas matemáticas pré-definidas.

    Inventário e Slots: Possui campos específicos para equipamentos equipados: mao_direita, mao_esquerda e armadura, além de listas para inventário geral.

    Estado: Controla listas dinâmicas de efeitos_ativos (venenos, buffs) processados a cada turno e magias_conhecidas.


3.5. Mapas (A base do ambiente de jogo)

Entidade composta pela camada de terreno, camada de objetos e conjuntos de eventos ligados a cada mapa, Os mapas podem ser aninhados pelo campo 'mapa_pai'.

    Existem terrenos que permitem caminhar (chão) e outros bloqueam a passagem (paredes, água, etc).

    A camada de objetos bloqueia a passagem. Um truque de background faz parecer que está a cima da camada de terrenos.

    Eventos ficam no EventosDB e são instancidos juntos com o mapa, sobrepostos a ele e são acionaveis por meio de seus parametros. Assim como os objetos, eles aparentam estar acima da camada de terrenos.


3.6. Eventos (Centro da Mecânica do Jogo)

Entidades representadas por emojis posicionados no mapa mas com parametros que são passados ao motor de eventos EventSystem quando são acionados.

    Os parametros permitem uma criação e programação visual completa do evento como uma entidade única do jogo.

    Enventos classicos são:
        - teleporte (portas, entradas, cidades, entrada de cavernas): muda de mapa.
        - baús: eventos que modificam o inventário do personagem
        - Npcs: disparam mensagens, escolha de opções dadas, mudam variáveis, etc...

    Exemplos de possibilidades podem ser vistas no arquivo `modelo_de_parametros_eventos.json`

    


4. Regras de Negócio e Mecânicas
4.1. Validação de Magias e Habilidades

    As Magias possuem requisitos em formato de dicionário (ex: exige {"água": 2} e Exuberância >= 2).

    Regra Estrita: Ao tentar ensinar uma magia a um personagem, o sistema deve validar os seus "Caminhos de Magia Totais" (Base + Bônus da Classe). Se os requisitos não forem atingidos, o sistema deve levantar uma Exceção (ValueError) e impedir o aprendizado.

4.2. Fluxo de Combate

    Iniciativa: Ordenada por 1d6 + Agilidade (com desempates automáticos).

    Ataque: O atacante rola 3d6 + Modificador de Ataque contra a rolagem de Defesa do alvo (1d6 + Agilidade + Bônus de Escudo).

    Dano: Se acertar, o dano bruto é calculado rolando 1d6 por ponto do atributo base (Força/Agilidade) somado ao dano da arma.

    Absorção: O alvo reduz o dano bruto rolando 1d6 por ponto de Resistência e somando a defesa da Armadura.

5. Simulação de Batalhas

O módulo de simulação é estritamente isolado e aceita duas equipes (listas de instâncias de Personagem).

    Batalha Única (Arena): Simula turno a turno, selecionando alvos aleatoriamente entre os vivos. Retorna um dicionário de eventos relatando o vencedor e o log do combate.

    Simulador Estatístico (Múltiplas Batalhas): Recebe o número N de batalhas (Padrão: 100). Executa simulações silenciosas.

    Mecânica de Isolamento: O simulador deve usar deepcopy nos personagens originais antes de cada rodada para garantir que eles entrem na arena com hp e mp máximos, evitando o acúmulo irreal de ferimentos entre simulações independentes.

    Relatório: Agrupa estatísticas por personagem (Tentativas, Acertos, Dano Causado, Abates e Taxa de Sobrevivência).

6. Persistência e Banco de Dados (ORM)

    SQLAlchemy: Utilizado para mapeamento relacional.

    Separação de Ambientes: O sistema obedece a uma variável de ambiente (TEST_VERSION). Se verdadeira, utiliza bancos SQLite isolados para testes (rpg_teste.db), protegendo dados de produção.

    Tipagem JSON: Dicionários e listas do Domínio (como bônus e requisitos) são salvos em colunas tipo JSON.

    Isolamento de Dados Derivados: O banco de dados armazena apenas os Atributos Base. Cálculos de vida, mana e ataque má


