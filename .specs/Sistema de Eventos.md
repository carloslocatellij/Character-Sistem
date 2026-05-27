

### Tipos de Eventos Principais

- **Eventos de Mapa:** São aqueles posicionados diretamente na grade do seu mapa. Podem ser personagens, portas, itens escondidos ou eventos invisíveis de tele transporte (mudança de mapa).
- **Eventos Comuns:** Ficam salvos no "Banco de Dados" do jogo. São úteis para criar lógicas que se repetem em vários lugares (como um sistema de descanso na pousada, ou habilidades de batalha que chamam um evento). 

### Estrutura de um Evento

1. **Estados:** Um evento pode ter várias páginas de condições. O jogo sempre lê da maior página para a menor (da página 3 para a página 1). A primeira página que tiver sua condição atendida é a que roda.

2. **Condições:** O que precisa acontecer para aquela página do evento funcionar (ex: ter completado uma _Quest_, ou a variável "X" estar no valor 10).

3. **Acionamento:** Como o jogador interage com ele:
    - _Ação do Jogador:_ Aperta a tecla de confirmação virado para o evento.
    - _Toque do Evento:_ O evento encosta no personagem ou o personagem encosta no evento.
    - _Toque do Jogador:_ Idem ao Toque do Evento, mas para quando o herói anda em cima do evento.
    - _Processo Paralelo:_ Roda em segundo plano infinitamente enquanto a página estiver ativa. Ideal para climas (chuva) ou monitoramento constante (Checar se o HP do jogador chegou a zero).
    - _Processo Automático:_ Trava a tela e roda sozinho. Excelente para cenas de história (Cutscenes).

#### Comandos de Evento Mais Usados

- **Mensagem:** Exibe textos, imagens e rostos de personagens na tela.

- **Controle de Variáveis/Interruptores (Switches):** Usados na memória do jogo para registrar escolhas e progresso do jogador.

- **Bifurcação Condicional (Conditional Branch):** Cria caminhos alternativos no diálogo. _"Se o jogador tiver o item Chave, abra a porta; se não, diga que está trancada"_.

- **Mover Evento:** Controla a movimentação de NPCs ou do herói para criar sequências de animação e cinemáticas. 