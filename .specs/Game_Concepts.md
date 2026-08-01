# Criador jogos RPG

### Ferramenta gerenciamento campanhas mestres RPG, tornando-se Criador jogos estilo Final Fantasy.

- Banco dados:
	- Personagens
	- Classes
	- Raças
	- Itens Equipamentos
	- Mapas
	- Eventos
	
- Simulador Combate

- Editor mapas


- ### Jogar 
- Função jogar (testar jogo funcionamento)


### Salvar / Carregar jogo:

- Suporte salvamento Estados (variáveis tempo execução jogo): 
	- Mapa posição jogador
	- Status atual personagem (Nível, pv_atual, pm_atual, etc...)
	- Inventário atual personagem
	- Equipamentos: Arma, armadura, escudo equipados personagem.
	- Eventos acionados, estados sustentam história.
	- Outras variáveis estado jogo.


### Geração múltiplos jogos independentes.

- Usuário criará jogos completos: Banco dados deve ter versionamento/mecanismo para criar, escolher, compartilhar jogos.

##### Multiplayer:

[ ] Autenticação
[ ] Perfil usuário
[ ] Comunidades
[ ] Tela chats interação usuários
[ ] Compartilhamento cenários
[ ] Jogo Multiplayer

#### Modo Jogo ROGUE LIKE:

[ ] Gerador cenários procedural automático por árvores mapas aninhados, pontos conexão eventos teleporte 
[ ] Gerador eventos semi-aleatórios categoria
[ ] Gerador NPCs semi-aleatórios categoria 
[ ] Sistema Conector História


## Personagem
O que faz?

-> Move
-> Aciona coisas
-> Chama Menu *

---
### Mover - Cima / Baixo / Direita / Esquerda (teclas direcionais)
- Elementos/eventos acionados nesta ação: Personagem move sobre/encosta evento, **dispara**.

---

### Acionar - (tecla Enter)

- Base mecanismo funcionamento jogo.
	- Acionar chama/**Dispara** eventos desencadeando **estados** que resultam desenrolar jogo.
##### -> Motor deve estar escutando ações.

- #### Conversas 
	- Quadro mensagem: Desde placa nome cidade até mecanismo atribuição valores, perguntas, escolhas que interferem dinâmica/constituem mini-games.
	- ##### Compra / Venda (Lojas): Conversas aprimoradas, configuráveis, reutilizáveis.
	
- #### Acionamento Eventos:
	- Acionamento padrão (reutilizáveis): Pressionar Enter frente blocos evento (baús, portas, NPCs, objetos).
		- Eventos carregam lógica funcionamento.

- #### Acionamento Extra. (Pressionar segurar tecla)
	- Segurar Enter tempo resulta mecânica/interação diferente (ex: Puxar/Empurrar, Segurar/Soltar). Permite desenvolvimento puzzles.

---

### Menu - (tecla Tab)

Opções salvar, carregar:

- #### [[Game Maker|Equipar Item]]
- #### Usar itens
- #### Usar Habilidades 
- #### Mudar Equipe


## Eventos
O que fazem?

-> Move
-> Acionados

---
#### Mover - Cima / Baixo / Direita / Esquerda / Segue / Foge
- Eventos movem se programados; disparo movimento por acionamento personagem ou mudança estado jogo (mudança mapa).
- Seguir personagem/outro evento, fugir, seguir rota (ciclo).
---

### Tecla '/'
- Barra comandos



# Sistema jogo RPG mesa baseado turnos

- Criação personagens RPG (atributos, características, habilidades, raças, classes).
- Criação raças características próprias.
- Criação classes características, atributos, habilidades próprias.
- Criação itens, equipamentos, armas, armaduras.
- Mecânica batalha (ações personagens, cálculo/comparação atributos para resultado).
- Simulações batalhas.

## Sistema Personagens
- Raça, Classe propriedades composição personagem.

### Raça
- Nome, dicionário bônus atributos aplicado Personagem.
- Representação emojis.

### ClasseRPG
- Nome, dicionário caminhos_magia, lista habilidades, dicionário bônus_atributos.

### Personagem
- Nome, nível, ClasseRPG, Raça, dicionário atributos (forca, agilidade, resistencia, percepcao, exuberancia). Mão_direta, mão_esquerda, armadura, itens corpo, equipamentos. 
- Lista efeitos ativos.
- Funcionamento: Métodos Personagem (atualizar_atributos_totais, _calcular_status_derivados, reset_status, calcular_defesa_esquiva, receber_dano, receber_dano_de_efeito, finalizar_turno), ações (atacar, lancar_magia, usar_item).

## Sistema Magia, Habilidade, Efeitos:

### Habilidades
- Ação especial (não atacar, andar, esquivar, defender).
- Nome, tipo, dano_base, efeitos, requisitos, area, alcance, uso aliados.

### Magias
- Tipo habilidade (herda Habilidade).
- Caminho, custo_mana.

### Efeitos
- Eventos status habilidades/magias. Duração: personagem sob condições aplicadas. 
- Nome, tipo, duração, área, dano_base, modificadores, função cálculo dano/recuperação.
- Início turno combate: computar/aplicar efeitos.

#### Caminhos Magia
- Caminhos ("luz", "trevas", "fogo", "água", "ar", "terra"). Valores: pontos (padrão=0).
- Pontos verificam posse magia: Na criação Personagem, verificar se atributos atendem requisitos Magia/Habilidade. Exceção caso contrário.

## Sistema Equipamentos
- Itens, Armas, Armaduras, Escudo.
- Item: nome, peso, emoji.
- Arma (herda item): dano, tipo.
- Armadura (herda item): defesa.
- Escudo (herda item): defesa_extra.


## Sistema Simulação Batalhas

### Simulador Combate independente Grupo. Aliados, oponentes. Iniciativa rolada; combate ocorre sequência até final (pontos vida zerados/abaixo zero). 
- Simulador batalha individual, resultados cada turno.
- Simulador estatístico (padrão 100 batalhas): simulações silenciosas, coleta resultados (acertos, dano, cura, defesas, mortes, batalhas sobrevividas), vitórias/derrotas time.


## Criador Mapas

### Editor gerador procedural mapas: ('caverna', 'vila', 'masmorra'), 3 camadas: (Terrenos, Objetos, Eventos). 

### Permite: Gerar, Importar/Exportar csv, Salvar Banco dados, Editar camadas, Atribuir propriedades (mapa_pai).
- [x] Paleta emojis camada (Terreno, Objetos, Eventos).
- [x] Desenhar pincel mapa.
- [x] Desfazer/Refazer.
- [x] Alterna pincel/balde tinta.
- [x] Inserir evento: Formulário Configurações - Eventos salvos EventDB (campo ligação mapa_id).
- [ ] Tipo: Novo mapa branco.
- [ ] Pincel retangulo
- [ ] Pincel circulo
- [ ] Pincel linha
- [ ] Recortar/Colar



### Tipos Eventos Principais

- **Eventos Mapa:** Posicionados grade mapa. Personagens, portas, itens escondidos, eventos invisíveis teletransporte (mudança mapa).
- **Eventos Comuns:** Salvos "Banco Dados" jogo. Lógicas repetidas (descanso pousada, habilidades batalha). 

### Estrutura Evento

1. **Estados:** Várias páginas condições. Jogo lê decrescente (página 3 para 1). Roda primeira página condição atendida.

2. **Condições:** Funcionamento página (ex: Quest, variável X valor 10).

3. **Acionamento:** Interação jogador:
    - _Ação Jogador:_ Aperta tecla confirmação frente evento.
    - _Toque Evento:_ Evento encosta personagem/personagem encosta evento.
    - _Toque Jogador:_ Herói anda sobre evento.
    - _Processo Paralelo:_ Roda plano fundo infinito. Climas (chuva), monitoramento constante (HP zero).
    - _Processo Automático:_ Trava tela, roda sozinho. Cenas história (Cutscenes).

#### Comandos Evento Mais Usados

- **Mensagem:** Exibe textos, imagens, rostos tela.

- **Controle Variáveis/Interruptores (Switches):** Memória jogo registrar escolhas, progresso.

- **Bifurcação Condicional (Conditional Branch):** Caminhos diálogo. _"Se tiver item Chave, abra porta; se não, diga trancada"_.

- **Mover Evento:** Movimentação NPCs/herói animações, cinemáticas. 



# Transformar motor lógico ferramenta profissional estilo RPG Maker: migrar payload (mistura estados/comandos) para Arquitetura Homogênea Baseada Páginas Condicionais, Comandos Lineares Sequenciais.

Arquitetura clássica RPG: evento possui Lista Páginas avaliada decrescente (maior para menor). Cada página possui Condições, Gatilhos, lista sequencial Comandos genéricos.

Abaixo modelo estendido, padronizado, escalável payload JSON:

🌐 Modelo Payload Universal Estendido (JSON)

Este payload representa evento banco dados (parametros). Engloba casos uso (Baú Switch Local, NPC Missão, Armadilha Toque, Quebra-Cabeças Empurrar, Processos Paralelos).
JSON


- Verificar em .specs/modelos_de_parametros_eventos.json

## 🪵 Extensão Extra: Payloads Especiais Gatilhos Puzzles

Suporte mecânicas (empurrar objetos, armadilhas automáticas, processos paralelos clima), padronizamos formatos página eventos específicos:

A) Puzzle Empurrar / Puxar Bloco (segurar_confirmacao)
JSON

{
  "id_pagina": 1,
  "condicoes": {},
  "configuracao_visual": {"emoji": "🪨", "atravessavel": false, "movimento": {"direcao": "parado"}},
  "gatilho": "segurar_confirmacao",
  "comandos": [
    {
      "tipo": "mover_evento",
      "dados": {
        "alvo": "proprio",
        "direcao": "olhar_jogador", 
        "passos": 1,
        "ignorar_bloqueio": false
      }
    }
  ]
}

B) Armadilha Oculta Chão (toque_jogador)
JSON

{
  "id_pagina": 1,
  "condicoes": {},
  "configuracao_visual": {"emoji": "🟩", "atravessavel": true},
  "gatilho": "toque_jogador",
  "comandos": [
    {
      "tipo": "efeito_sonoro",
      "dados": {"arquivo": "spikes.wav", "volume": 80}
    },
    {
      "tipo": "mudar_render",
      "dados": {"alvo": "proprio", "novo_emoji": "💀"}
    },
    {
      "tipo": "mudar_status_heroi",
      "dados": {"parametro": "hp", "operacao": "sub", "valor": 15}
    },
    {
      "tipo": "mensagem",
      "dados": {"texto": "[bold red]Aviso:[/] Pisou estacas escondidas, perdeu 15 hp!"}
    }
  ]
}

C) Processo Paralelo (processo_paralelo - Dano Veneno / Clima)
JSON

{
  "id_pagina": 1,
  "condicoes": {
    "switches": [{"nome": "heroi_envenenado", "valor": true}]
  },
  "configuracao_visual": {"emoji": "", "atravessavel": true},
  "gatilho": "processo_paralelo",
  "comandos": [
    {
      "tipo": "mudar_status_heroi",
      "dados": {"parametro": "hp", "operacao": "sub", "valor": 2}
    },
    {
      "tipo": "esperar",
      "dados": {"ciclos_ticks": 5}
    }
  ]
}

⚙️ Especificação Técnica Interpretador Payloads

Quando interação dispara, motor lógico processa payload seguindo pipeline técnico:

[Interação/Gatilho Detectado]
              │
              ▼
    ┌───────────────────┐
    │  Pipeline Passo 1 │ ───> Executa loop decrescente páginas (Page 3 -> 2 -> 1).
    │  Filtro Página    │ ───> Confere Switches, Variáveis GameStateManager.
    └───────────────────┘
              │
              ▼ (Primeira página válida)
    ┌───────────────────┐
    │  Pipeline Passo 2 │ ───> Avalia Gatilho página casa estímulo físico
    │ Validação Gatilho │      (ex: gatilho "toque_jogador", herói pisou bloco).
    └───────────────────┘
              │
              ▼ (Gatilho Correspondente)
    ┌───────────────────┐
    │  Pipeline Passo 3 │ ───> Interpretador linear lê array 'comandos' cima baixo.
    │  Loop Comandos    │ ───> Desvia sub-rotinas baseadas chave "tipo".
    └───────────────────┘
              │
              ▼
    ┌───────────────────┐
    │  Pipeline Passo 4 │ ───> Modifica componentes EngineManager, emite eventos
    │  Mutação Tela     │      EventBus, força redesenho quadros Textual.
    └───────────────────┘

1. Estrutura Dicionário Condições (condicoes)

    switches: Lista objetos contendo nome, estado booleano esperado GameStateManager.

    variaveis: Suporta operações relacionais numéricas (maior_ou_igual, menor_ou_igual, igual, diferente).

    self_switch: Interruptores locais atómicos (A, B, C, D). Evento lembra interagiu consigo (ex: mudar emoji baú fechado para aberto) sem poluir tabela global switches.

    item_requerido: Verifica InventoryComponent herói (ID 1) string informada existe quantidade > 0 antes abrir página.

2. Dicionário Comandos Padronizados (comandos)

Em vez funções soltas, comando nó imperativo dicionário interno dados:

    mensagem: Injeta texto formatado log interface.

    bifurcacao_condicional: Pausa execução sequencial, renderiza opções prompt, desvia ponteiro sub-bloco ramo escolhido.

    mudar_inventario / mudar_status_heroi: Altera valores numéricos InventoryComponent, StatsComponent anexados entidade memória RAM.

    controle_self_switch: Altera estado interno evento: próxima renderização, página superior ativada.
