# Regra 4: Persistência de Dados e Banco de Dados (SQLAlchemy)

A persistência é gerenciada via SQLAlchemy ORM mapeada para SQLite (local) e preparada para transição futura para serviços cloud (como Supabase).

## 1. Separação de Ambientes (Produção vs. Teste)

- **Variável de Ambiente `TEST_VERSION`:** O sistema deve verificar a flag `TEST_VERSION` obtida do arquivo `.env` ou do ambiente do sistema operacional.
- **Roteamento de Conexão:**
  - Se `TEST_VERSION` for **verdadeira (True)**: Utilize um arquivo de banco SQLite isolado e descartável (`rpg_teste.db` ou banco em memória `:memory:`). Isso protege o banco de produção de alterações e sujeira causadas pela execução automatizada de testes (pytest).
  - Se `TEST_VERSION` for **falsa (False) ou nula**: Utilize o banco de produção do SQLite (`rpg_producao.db`) ou a URL de conexão definitiva.

---

## 2. Tipagem JSON no Banco de Dados

- Como o jogo lida com dados estruturados altamente flexíveis (ex: dicionário de bônus de atributos, caminhos elementais, inventários de mapa, layouts de terreno em emojis, propriedades JSON de eventos), utilize colunas do tipo **JSON** (ou tipos compatíveis convertidos para string/texto no SQLite) para armazenar estas propriedades de forma íntegra.
- Garanta que as propriedades JSON sejam serializadas/deserializadas corretamente ao transitar entre os modelos SQLAlchemy (ex: `PersonagemDB`, `MapaDB`, `EventoDB`) e as entidades de Domínio.

---

## 3. Chaves Estruturadas de Coordenadas de Objetos

- O banco armazena as chaves de mapas e posições de objetos estáticos como strings no formato `"y,x"` (ex: `"5,12": "🌲"`).
- O motor de renderização da TUI (`RenderSystem`) exige chaves baseadas em tuplas numéricas inteiras de coordenadas `(y, x)` para indexação veloz de frames.
- O mapeador e carregador do motor (`GameEngineLoader`) deve obrigatoriamente realizar a conversão atômica em tempo de carga destas coordenadas para tuplas de inteiros e tratar eventuais exceções decorrentes de formatos de string corrompidos.

---

## 4. Gerenciamento Assíncrono Futuro (Integração Cloud)

- Chamadas de banco de dados na nuvem (Supabase) não podem bloquear a thread principal do Textual.
- Qualquer integração ou persistência em nuvem deve ser implementada de forma **assíncrona (`async/await`)** utilizando `AsyncSession` do SQLAlchemy ou delegando as consultas síncronas para Workers assíncronos não-bloqueantes.
