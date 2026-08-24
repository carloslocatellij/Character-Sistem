# TODO

### Fase atual;

[x] O resultado do combate (venceu/ perdeu/ fugiu/ inimigo fugiu) deve poder se ligar a mudanças parâmetros como atribuição/mudança de variáveis, switches.     

[X] A parte de itens/equipamentos:
        + As referencias a itens ou equipamentos nos eventos devem ser listas para os itens da tabela ItensDB.
        + Os comandos /usar e /equipar devem mostrar um menu com abas para os itens e equipamentos do personagem onde ele pode usar, equipar/desequipar.
        + na batalha o usar item deve mostra um menu com os itens usaveis e estes devem fazer seu efeito próprio quando usados

[ ] O sistema de Magias e Habilidades descrito nas especificações:      
 Modelar estas especificações abaixo no sistema: Será necessário criar tabelas para entidades magia e efeito;
    Magias podem causar efeitos: sono, veneno, lentidão, atordoado, regenerar.
    Efeitos são estados temporarios dos personagens ou monstros: Duram x turnos.
    A cada turno ativo o efeito pode: causar y de dano, curar y de hp, atributo fica y ponto a cima ou abaixo, deixa de atacar x turnos (dormindo), ataca aleatorio (louco), proteção ou fraqueza contra tipos de magia ou habilidades.
    Magias ou habilidade podem causar dano em área (> de 1 inimigo).
    Habilidades podem ter maior chance de crítico, ignorar bonus de defeza, contra-ataque, tentativa dupla ou tripla de ataque com taxas menores de acerto.
    Magias possuem requisitos (ex: `{"água": 2}`, Exuberância >= 2) para serem aprendidas/ adquiridas/ executadas.
    Regra Estrita: Ao ensinar magia, validar "Caminhos Magia Totais" (Base + Bônus Classe). Se requisitos não atingidos impede aprendizado/execução da magia/habilidade.

[ ] Adicionar membro na equipe (A Equipe é o personagem do jogador + 3 personagens totalizando 4 personagem por jogador) - Nas batalhas cada personagem pode atacar em sua vez.


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