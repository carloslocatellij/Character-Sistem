
# CharSistem é um sistema de Criação de RPGs jogaveis de terminal feito em Python.
## Crie seus próprios mundos com cenários completos, personagens, magias, monstros.
## Jogue seu jogo e compartilhe com amigos.
### Graficos totalmente feitos com emojis graças ao Textual: https://textual.textualize.io/
### Motor ECS https://esper.readthedocs.io/

- O usuário pode, até o momento, criar personagens informando seu Nome, Nivel, Classe, Raça e os atributos, também uma lista de habilidades, caminhos de magia (água, ar, fogo, terra, trevas e luz). Criar e equipar itens, simular batalhas.

- Agora temos um editor de mapas que pode gerar masmorras, cavernas e cidades aleatórias e preencher com emojis de várias coisas.

- A Jogabilidade já está em fase de testes ( Você pode andar pelo mapa de "id 1" e interagir com eventos )

- Consulte o contexto de desenvolvimento em `.specs/*.md`

- Consulte o MANUAL.md em caso de dúvidas.

Para usar a versão CLI:

1 - Instale o git.

2 - Em seu computador escolha uma pasta para o jogo e faça: 
`git clone https://github.com/carloslocatellij/Character-Sistem`

3 - Instale o python. (Não vou ensinar).

4 - Isole e Baixe as requerimentos:
- crie um ambiente virtural (opicional) com:
`python -m venv .venv`
- ative o ambiente com:
windos `.\.venv\Scripts\activate` linux `source .venv/bin/activate`

4.1 - Baixe e instale:
`pip install -r requirements.txt`

5 - Na pasta do projeto rode:
`python ./rpg_api/main_cli.py`


# Contexto do Projeto
- **Framework Principal:** Textual (TUI)
- **Gerenciador de Estado:** Python esper (ECS)
- **Persistência:** SQLAlchemy + Supabase
- **Padrão de Código:** Componentização estrita. O Textual gerencia a View; o esper gerencia o estado/lógica.

# Contexto do Projeto - Fase 2: Integração Cloud
- **Status Atual:** Módulos TUI (Textual) e Motor (esper ECS) operando localmente com testes robustos.
- **Próximo Objetivo:** Migrar persistência local/em memória para o Supabase de forma assíncrona.
- **Restrição Arquitetural Crítica:** Chamadas de rede da API do Supabase NÃO podem bloquear o loop de eventos principal do Textual (`asyncio`).
- **Padrão de Integração:** O Supabase deve ser injetado via SQLAlchemy (AsyncSession) ou client assíncrono dentro dos Systems do `esper` ou em threads gerenciadas por Workers do Textual.


##### Obs.
Testado no Gnome Terminal v.3.52 e Windows Terminal 

### Este projeto tem potencial para se tornar um MMORPG de linha de comando!
Caso tenha sujestões ou deseje participar fique a vontade para me contactar por meio das redes da bios.

##### Apoie o projeto pela chave pix:
3679f002-4e36-4fa3-ac40-5067b2750a9a