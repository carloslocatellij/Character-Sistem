# Regra 4: Persistência Dados (SQLAlchemy)

Gerenciado via SQLAlchemy ORM (SQLite), preparado para nuvem (Supabase).

## 1. Separação Ambientes (Prod vs. Teste)

- **Variável `TEST_VERSION`:**
  - `TEST_VERSION=True`: Usa SQLite isolado (`rpg_teste.db` ou `:memory:`). Protege banco prod de testes (pytest).
  - `TEST_VERSION=False/null`: Usa `rpg_producao.db`.

---

## 2. Tipagem JSON

- Dados flexíveis (bônus, inventário, layouts, eventos) em colunas **JSON**.
- Garanta serialização/deserialização correta entre modelos SQLAlchemy (`PersonagemDB`, `MapaDB`, `EventoDB`) e entidades Domínio.

---

## 3. Coordenadas

- Banco armazena chaves de posições como strings `"y,x"` (ex: `"5,12": "🌲"`).
- Render (`RenderSystem`) exige tuplas `(y, x)` (ints).
- `GameEngineLoader` deve converter atômico strings para tuplas tuplas ints no carregamento. Tratar erros formato.

---

## 4. Gerenciamento Assíncrono (Cloud)

- Chamadas DB nuvem (Supabase) não podem bloquear thread principal Textual.
- Persistência nuvem deve ser **assíncrona (`async/await`)** (usando `AsyncSession` ou Workers assíncronos).
