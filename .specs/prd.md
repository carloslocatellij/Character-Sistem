
# Sistema de jogo de RPG de mesa baseado em turnos

- Permite a criação de personagens para jogos de RPG com seus atributos, características, habilidades, raças e classes, etc...
- Permite a criação novas de raças com suas características próprias.
- Permite a criação de classes com suas características, atributos, habilidades próprias, etc ...
- Permite a criação de itens, equimapentos, armas e armaduras para equipar os personagens.
- Permite uma mecânica de batalha com as ações dos persongens na qual os atributos serão calculados e comparados para determinar o resultado.
- Permite simulações das batalhas.

## Sistema de Personagens
- A Raça e a Classe deverão ter propriedades que serão usadas para a composição do personagem.

### Raça
- A Raça tem nome e um dicionário de bonus de atributos a ser aplicados ao Personagem.
- A Raça tem representação por emojis.

### ClasseRPG
- A ClasseRPG tem nome, um dicionário de caminhos de magia "caminhos_magia", uma lista de habilidades e um dicionário de bonus_atributos que são aplicados ao personagem da classe.

### Personagem
- Personagem tem nome e nivel, é composto por ClasseRPG e Raça, têm um dicionário de atributos (
"forca": forca_base, "agilidade": agilidade_base, "resistencia": res_base, "percepcao": perc_base,    "exuberancia": exub_base). Além de ter mão_direta, mão_esquerda, armadura, itens de corpo e equipamentos. 
- O Personagem tem também uma lista de efeitos ativos.
- Boa parte do mecanismo de funcionamento do sistema vem dos métodos do Personagem, ou seja, um conjunto de ações (funções da class) que consistêm na forma que o sistema utiliza a class Personagem (atualizar_atributos_totais, _calcular_status_derivados, reset_status, calcular_defesa_esquiva, receber_dano, receber_dano_de_efeito e finalizar_turno) e também ações que podem ser usadas pelo sistema ou pelo usuário (atacar, lancar_magia, usar_item)

## Sistema de Magia, Habilidade e Efeitos:

### Habilidades
- Habilidades são um tipo de ação especial (sem ser atacar, andar, esquivar e se defender) que alguns personagens têm e podem executar durante o combate.
- Cada habilidade possui um nome, tipo, dano_base, efeitos, requisitos, area, alcance e se pode ser usada em aliados.

### Magias
- Magias são um tipo de habilidade (herda de Habilidade).
- Magia, além do que tem em habilidade, tem caminho e custo_mana.

### Efeitos
- Efeitos são eventos de status que uma habilidade ou magia podem apensar a um personagem. Em quanto durar o efeito o personagem fica sob as condições aplicadas pelo efeito. 
- Efeito tem nome, tipo, duração, área, dano_base, modificadores e podem ter uma função dinâmica para calculo de dano/recuperação.
- No início de cada turno de combate os resultados da aplicação de efeitos deve ser computados e aplicados.

#### Caminhos de Magia
No dicionário de Caminhos de Magias da ClasseRPG as chaves são os caminhos ("luz", "trevas", "fogo", "água", "ar" e "terra") e os valores são os pontos que o personagem tem no caminho (padrão=0).
- Os valores em pontos nos caminhos serão usados para verificar se o personagem pode possuir determinada magia: Na criação do objeto Personagem deve haver uma verificação para cada Magia ou Habilidade da Classe atribuida se as caracteristicas/atributos passados ao Personagem em questão atendem aos requistos da Magia/Habilidade, levantando uma Exessão em caso de não atendimento. 

## Sistema de Equipamentos
- O persongem também podera ser equipado com Itens, Armas, Armaduras e Escudo.
- Item terá nome, peso e uma representação visual por emoji
- Arma herda estas características de item, além de ter dano e tipo.
Armadura herda de item e tem a propriedade defesa.
Escudo herda de item e tem a propriedade defesa_extra.


## Sistema Simulação de Batalhas

### É um Simulador de Combate independente em Grupo. Neste simulador deverão ser passados os personagens aliados e os oponentes. A iniciativa será rolada para todos e o combate ira ocorrer nesta sequência até o final( todos os oponentes ou todos os aliados serem terem seus pontos de vida zerados ou a baixo de zero) 
- Contém um simulador que simula uma batalha individual e imprime os resultados dos acontecimentos de cada turno.
- Contém um simulador estatísco que recebe um número de batalhas (padrão = 100), realiza as simulações silenciosas, coleta resultados dos eventos por personagem (número de acertos, dano causa, cura causada, número de defesas, mortes causadas e batalhas sobrevividas), e o número de vitorias e derrotas de cada time.

