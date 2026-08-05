
==========================================
|[menu]|[editar]|[opçoes]				X|
==========================================
|Paleta_____| ->, O, #, Ev! 		  	 |
|			|----------------------------|
|# @ $ * +	| Mapa: Mundo				 |
|% X ~ ^ ;	|----------------------------|
|% X ~ ^ ;	|							 |
|& ? ! Q .	|							 |
|___________|							 |
|Mapas______|							 |
|			|							 |
|Mundo		|							 |
||\			|			mundo_db		 |
|\_Cidade1	|							 |
|| \_loja1	|							 |
|| \_loja2	|							 |
|| \_casa1	|							 |
||			|							 |
| \_Caverna1|							 |
|			|							 |
++++++++++++++++++++++++++++++++++++++++++

Menus:
Menu  -> Novo, Salvar, Importar_csv, Exportar_csv, Sair
Editar-> Recorta, Cola, Propriedades
Opções-> Paleta, Eventos, Musica, Dados

[x] Novo: abre formulário criação mapas.
[x] Salvar: salva mapa banco dados.
[x] Importar/Exportar: csv importa/exporta.
[x] Sair: sai, igual 'X'.
Recortar: recorta área quadrada mapa para colar.
Colar: cola parte mapa transferência.
[x] Propriedades: acessa/altera propriedades mapa.
[x] Paleta: fornece opções tiles edição.
Eventos: permite tile especial dispara eventos programados.
Musica: gerencia músicas.
[x] Dados: formulário Pesquisa/Edição dados sistema.
---

Paleta permite seleção tiles para mapa.

[x] Mapas: árvore mapas criados, aninhados mapa_pai, selecionáveis edição.


#===========================================
#  GESTOR DE MAPAS NÍVEL 2
#===========================================

Composição mapa via emojis traz problema:
Emojis: chão, parede, objetos (nem chão, nem parede). "  " (espaço duplo) = fundo.
Objeto tem fundo transparente, compatível apenas com "  " (fundo terminal).
Exemplo:
🟫🟫🟫
🟫🪑🟫 
🟫🟫🟫

Solução:
1 - Dividir emojis em categorias: Terreno, Objetos, Eventos. Estabelecer atribuição.
2 - Tratar sobreposição objeto/chão:
[x] Sobreposição tratada via mapeamento cor tile anterior + preenchimento background emoji.

===============

Antes implementação, reavaliar confrontando objetivos:
Jogabilidade com "char" (personagem).
Futuro: motor execução recursos tipo jogo, tela atualiza movimento, acesso menu, interação eventos.
Implicações? Arquitetura ideal game engines?
[x] Arquitetura ECS: Event Component System
[x] Máquina Estados: Interação eventos mapa verificando 'tile' frente.
