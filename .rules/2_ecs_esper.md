# Regra 2: Arquitetura ECS (Entity-Component-System) com Esper

O motor físico e lógico do jogo é regido por uma arquitetura ECS descentralizada usando a biblioteca `esper`. Todo desenvolvimento de mecânicas de mapa e combate deve seguir estritamente estes padrões.

## 1. Responsabilidades do ECS

1. **Entidades (Entities):**
   - São IDs numéricos gerados pelo Esper (`esper.create_entity()`).
   - Não possuem lógica ou variáveis internas além do seu ID. Representam qualquer objeto ou evento no jogo (jogador, monstros, baús, portas, decorações).

2. **Componentes (Components):**
   - Definidos em `rpg_api/app/core/engine/components.py`.
   - São **estruturas puras de dados** (geralmente usando `@dataclass`).
   - Não devem conter lógica complexa, inteligência artificial ou chamadas externas. Apenas armazenam o estado (ex: `PositionComponent` guarda `y` e `x`, `StatsComponent` guarda vida e atributos).

3. **Sistemas (Systems):**
   - Definidos em `rpg_api/app/core/engine/systems.py` (herdando de `esper.Processor`).
   - Contêm a lógica do jogo que opera sobre grupos de entidades com componentes específicos.
   - Devem processar as entidades em lotes eficientes no método `process(self, *args, **kwargs)`.

---

## 2. Isolamento Headless (Sem UI)

- O motor ECS deve rodar de forma **Headless** (desacoplada). Toda a lógica de colisão, inteligência artificial de monstros e acionamento de eventos ocorre puramente em memória RAM.
- A interface de usuário (TUI Textual) atua apenas como uma camada de visualização passiva e emissora de intenções de input do jogador.
- Não importe `Widget` ou componentes do Textual nos arquivos de componentes ou sistemas do Esper.

---

## 3. Gerenciamento de Cenas via Múltiplos Mundos (`WorldContext`)

Para evitar vazamentos de estado (como monstros e itens aparecendo em mapas errados) sem destruir dados globais e listeners de eventos da UI, o sistema usa múltiplos contextos de mundo do Esper:

- **Isolamento por Mapa:** Cada mapa do jogo visitado pelo jogador gera ou recupera uma instância dedicada de `esper.WorldContext` que é persistida no cache em RAM (`mundos_carregados`).
- **O Herói Nômade (ID 1 Fixo):**
  - O jogador sempre deve ter o ID de Entidade **1**.
  - Ao transicionar de mapa, um snapshot de seus componentes (`PositionComponent`, `StatsComponent`, `InventoryComponent`, `EquipmentComponent`, `RenderComponent`) deve ser salvo.
  - No novo mapa, o sistema muda de contexto (`esper.switch_world()`), destrói qualquer componente existente no ID 1 (limpeza física), e injeta os componentes do snapshot atualizados do herói na entidade ID 1.
- **Persistência do Barramento de Eventos:** Ao alternar mundos, garanta que os manipuladores de eventos da interface visual não sejam perdidos. O `master_event_registry` (barramento de eventos) deve ser repassado e herdado a cada novo `WorldContext` selecionado para evitar que botões e escutas da TUI parem de responder.
