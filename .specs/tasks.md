# TODO

### Fase atual;

[x] O resultado do combate (venceu/ perdeu/ fugiu/ inimigo fugiu) deve poder se ligar a mudanças parâmetros como atribuição/mudança de variáveis, switches.     

[ ] A parte de itens/equipamentos está em estagio experimental:
        - adicionar por eventos recebe qualquer valor digitado ao invés de itens do banco de dados.
        - os comandos /usar e /equipar foram escritos apenas para itens de exemplo ('poção', 'espada longa')
        - na batalha, o comando usar item, apenas tenta usar uma poção do inventário.
        ---
        + As referencias a itens ou equipamentos nos eventos devem ser listas para os itens da tabela ItensDB.
        + Os comandos /usar e /equipar devem mostrar um menu com abas para os itens e equipamentos do personagem onde ele pode usar, equipar/desequipar.
        + na batalha o usar item deve mostra um menu com os itens usaveis e estes devem fazer seu efeito próprio quando usados

[ ] Adicionar membro na equipe (A Equipe é o personagem do jogador + 3 personagens totalizando 4 personagem por jogador) - Nas batalhas cada personagem pode atacar em sua vez.

[ ] O sistema de Magias e Habilidades descrito nas especificações:

[ ] É necessário uma opção de loop lógico que desencadeia o funcionamento de loop nas interações com eventos.

[ ] Implementar sistema de mostrar imagens por meio dos parâmetros de eventos

[ ] Implementar sistema de tocar sons/musicas por meio dos parâmetros dos eventos

[ ] Implementar sistema de usar barco por meio dos parâmetros dos eventos

### Próxima Fase

[ ] Tabela de progressão de niveis por XP

[ ] Sistema de aquisição e avanço de habilidades/magias por nível de classe.

[ ] Sistema que permite o usuário criar suas próprias habilidades/ magias


### Outras Fases

[Pendente] Estrutura Servidor/Cliente - MVP rede local 2 jogadores.

[Pendente] API Web (FastAPI).

[Pendente] app/schemas (Pydantic) - validação requisições.

[Pendente] app/routers - endpoints (POST /personagens, POST /simulacao).
 
[Pendente] Autenticação.
 
[Pendente] Estrutura comunidades web.

[Pendente] Modulo Rogue Like - Geração procedural de aventuras