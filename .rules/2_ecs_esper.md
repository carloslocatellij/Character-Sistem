# Regra 2: Arquitetura ECS + Esper

Motor lógico segue arquitetura ECS descentralizada (biblioteca `esper`).

## 1. Responsabilidades ECS

1. **Entidades:** IDs numéricos (`esper.create_entity()`). Sem lógica/variáveis internas. Representam qualquer objeto/evento (jogador, monstro, baú, etc.).
2. **Componentes:** Em `rpg_api/app/core/engine/components.py`. **Dados puros** (`@dataclass`). Sem lógica/IA/chamadas externas. Apenas estado (ex: `PositionComponent` com `x`, `y`).
3. **Sistemas:** Em `rpg_api/app/core/engine/systems.py` (herda `esper.Processor`). Lógica que opera sobre grupos entidades com componentes específicos. Processa em lotes em `process()`.

---

## 2. Isolamento Headless

- Motor ECS deve ser **Headless** (desacoplado). Lógica (colisão, IA, eventos) apenas em RAM.
- TUI (Textual) atua como visualização passiva + emissora intenções input.
- Não importe `Widget` ou componentes Textual em componentes/sistemas Esper.

---

## 3. Gerenciamento Cenas (WorldContext)

Evita vazamentos estado, sem destruir dados globais/listeners UI.

- **Isolamento Mapa:** Cada mapa visitado recupera `esper.WorldContext` persistido no cache RAM (`mundos_carregados`).
- **Herói Nômade (ID 1 Fixo):**
  - Jogador ID **1**.
  - Transição mapa: salva snapshot componentes (pos, stats, inventário, etc.).
  - Novo mapa: muda contexto (`esper.switch_world()`), limpa componentes antigos ID 1, injeta novos.
- **Persistência Barramento Eventos:** Ao alternar mundos, garante que manipuladores interface não sejam perdidos. `master_event_registry` repassado para cada novo `WorldContext` para evitar que UI pare de responder.
