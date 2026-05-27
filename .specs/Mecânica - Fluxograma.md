
## Personagem
O que ele faz?

-> Move
-> Aciona coisas
-> Chama Menu *

---
### Mover - Cima / Baixo / Direita / Esquerda (teclas direcionais)
- Alguns elementos ou eventos serão acionados apenas com esta ação: O personagem se move sobre ou encosta no evento e ele **``dispara``**.

---

### Acionar - (tecla Enter)

- Base de todo mecanismo de funcionamento do jogo.
	- O acionar *chama* ou ``**Dispara**`` eventos que levam ao acionamento ou desencadeamento de **estados** possíveis que somados resultam no desenrolar do jogo.
##### -> Fundamental que o motor esteja sempre *escutando* estas ações.

- #### Conversas 
	- Um quadro de mensagem: De uma simples placa com o nome da cidade até um mecanismo completo de atribuição de valores, perguntas e respostas e escolhas que podem interferir completamente na dinâmica e até constituir mini-games.
	- ##### Compra / Venda (Lojas) São conversas aprimoradas, configuráveis e reutilizáveis.
	
- #### Acionamento de Eventos:
	- Acionamento padrão de eventos (reutilizáveis ou não): Pressionando a tecla Enter de frente para blocos de evento estes são acionados (baús, portas, NPCs, objetos em geral)
		- Estes eventos carregam em si a lógica de seu funcionamento.

- #### Acionamento Extra. (Pressionar e segurar tecla)
	- Em algumas situações ou condições segurar a tecla Enter por determinado tempo resulta numa mecânica ou interação diferente junto aos objetos ou eventos do cenário. Ex: Puxar / Empurrar, Segurar/ Soltar.  Isto permite o desenvolvimento de puzzles específicos.

---

### Menu - (tecla Tab)

Vai trazer as opções de salvar, carregar e também:

- #### [[Game Maker|Equipar Item]]
- #### Usar itens
- #### Usar Habilidades 
- #### Mudar a Equipe


## Eventos
O que eles fazem?

-> Move
-> São acionados

---
#### Mover - Cima / Baixo / Direita / Esquerda / Segue / Foge
- Eventos podem se mover se forem programados para isso, o disparo do movimento pode ser por meio de algum acionamento do personagem ou mudança no estado do jogo (mudança de mapa etc...)
- Podem seguir o personagem ou outro evento, fugir do personagem ou outro evento, seguir uma rota determinada (em ciclo ou não).
---
