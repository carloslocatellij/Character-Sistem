# Guia: Motor TUI (Textual) + ECS (Esper)

Guia: especificação técnica, manual instruções. Agentes, engenheiros manutenção, depuração, expansão motor RPG Terminal. Sistema unifica framework **Textual** (TUI) motor **Esper** (ECS), persistência **SQLAlchemy**.

---

## 1. Lógica Assíncrona, Pilha Comandos

### Problema
Laços `for` síncronos, bloqueio `asyncio.run()` interpretadores comandos quebravam laço reativo Textual. Causava congelamento terminal, colisões concorrência ao pausar NPCs/Baús.

### Solução: Pilha Comandos Não-Bloqueante
Execução eventos JSON (RPG Maker) migrada máquina estados, **Pilha Comandos Linear (`pilha_de_comandos`)** dentro `EventSystem`.

1. **Quebra Atômica:** Analisa comando individual.
2. **Interrupção Controlada:** Comando `bifurcacao_condicional` renderiza opções, mapeia ramos `self.ramos_disponiveis` (índice texto/numérico), ativa flag `self.aguardando_escolha = True`, **interrompe loop execução**, devolve CPU TUI.
3. **Retoma Assíncrona:** Jogador escolhe, interface invoca `avancar_ramo_evento(opcao_escolhida)`. Método limpa bloqueio, empilha sub-ramo, reativa loop central.

---

## 2. Componente `ChoiceBox`

Substitui inputs chat texto caixas diálogo interativas (motores gráficos).

### `OnDecoratorError` (Textual)
Decorador `@on` exige mensagem filtrada ID (ex: `@on(ChoiceBox.Selected, "#box-evento-ativo")`) propriedade `control` apontando componente gerador. Falta causa exceção fatal.

```python
class ChoiceBox(Widget):
    class Selected(Message):
        def __init__(self, control: Widget, index: int, text: str) -> None:
            super().__init__()
            self._control = control
            self.index = index
            self.text = text

        @property
        def control(self) -> Widget:
            return self._control
```

Acoplamento Visual: GamePlayScreen

1. **Tamanho Dinâmico:** Ao disparar escolha, `.styles.height` painel log (#area-interacao) forçado tamanho fixo curto (ex: "5"), espaço botões rádio. Encerrar: define `.styles.height = None` (restaura 1fr).
2. **Ocultação/Foco:** Input padrão (#txt-chat) `.display = False`, foco teclado transferido ChoiceBox via `caixa_escolha.focus()` encapsulado `self.call_next()`.
3. **Bloqueio Event Bubbling:** Método `on_key` GamePlayScreen consome eventos se sistema espera resposta:
```python
    if hasattr(self, "event_sys") and self.event_sys.aguardando_escolha:
        return
```

3. Múltiplos Mundos (esper.WorldContext)

Problema: Duplicação, destruição estado. `esper.clear_database()` eliminava vazamentos monstros, mas destruía inventário herói, equipamentos, atributos, registros globais Event Listeners (`esper.event_registry`), quebrava comunicação interface.

Solução: Persistência Congelada RAM
GameEngineLoader refatorado, isolamento escopo usando mundos nativos Esper. Cada mapa recupera/gera instância `esper.WorldContext` única em `self.mundos_carregados`.

[Diagrama: Loader Central -> Contextos Mapa ID 1, Mapa ID 2]

1. **Herói Nômade (ID 1 Fixo):** Entidade transicional. Antes trocar cena, `_salvar_snapshot_jogador()` captura instâncias puras componentes (Position, Stats, Inventory, Equipment, Render), salva buffer RAM.
2. **Overwriting Limpo:** Entrar novo mapa, loader aciona `esper.switch_world()`. Destino, se Entidade 1 existir, limpa componentes (`.clear()`), re-injeta componentes buffer nômade assinatura ID 1.
3. **Preservação Progresso:** Inimigos/Baús não recriados/destruídos; congelados em `WorldContext` original. Retorno exibe cenário estado anterior.

Unificação Barramento Eventos (master_event_registry)
Alternância mundos limpa `esper.event_registry`, botões interface paravam. Loader captura referência mestre `__init__`, força novo/recuperado mundo herdar:

```python
self.master_event_registry = getattr(esper, "event_registry", {})
# Durante alternância:
if hasattr(esper, "event_registry"):
    esper.event_registry = self.master_event_registry
```

Conversão Camada Objetos Estáticos
`RenderSystem` exige chaves tuplas inteiros (y, x). Banco armazena dicionários chaves string "y,x". `_processar_camada_objetos` realiza tradução atômica carregamento:

```python
def _processar_camada_objetos(self, mapa_db: MapaDB):
    objetos_convertidos = {}
    if mapa_db and mapa_db.objetos:
        obj_raw = mapa_db.objetos if isinstance(mapa_db.objetos, dict) else {}
        for coord_str, emoji in obj_raw.items():
            try:
                y_str, x_str = coord_str.split(",")
                objetos_convertidos[(int(y_str), int(x_str))] = emoji
            except Exception:
                pass
    self.camada_objetos = objetos_convertidos
```

# Memória: Sistema RPG Python
## Visão Geral
Criação personagens, simulação batalhas RPG mesa. Princípios Clean Architecture, DDD, separando Domínio, DB, Interfaces.

## Stack
- Linguagem: Python 3.12+
- Testes: pytest (monkeypatch rolagens dados)
- DB: SQLAlchemy (SQLite)
- Ambiente: python-dotenv
- API: FastAPI

## Diretórios
rpg_api/
- `main_cli.py` (CLI, Mapper)
- `app/core/` (DOMÍNIO: ECS, components, engine, event_bus)
- `app/db/` (INFRA: Persistência)
- `app/models/` (DB Tables)
- `app/views/` (Textual)

## Passo a Passo Implementação
### Fase 1: Domínio
- Equipamentos: hierarquia @dataclass.
- Magias/Efeitos: Dano/Cura, buffs/debuffs, requisitos Caminhos Elementais.
- Personagem: Composição (Raca, ClasseRPG). Cálculo hp/mp/modificadores. Métodos combate (Design Orientado a Eventos).
- SimuladorCombate: Iniciativa, turnos. Estatísticas.

### Fase 2: Banco/Infra
- Ambientes: `TEST_VERSION` .env.
- ORM: JSON colunas (bônus, magia). PersonagemDB FKs (RacaDB, ClasseRPGDB). Prática: salvar "Status Base".

### Fase 3: Interface/Adapter
- CLI: `main_cli.py`. Padrão Mapper (`converter_para_dominio`).

### Fase 4: Qualidade
- 83+ testes.
- `pytest` módulo.
- monkeypatch (rolagens d6).
- setup/teardown DB.

---

# Relatório: RPG Game Maker (Textual + engine)
## Objetivo
Motor RPG/Criador Jogos, terminal, Python, Textual, Esper. Lógica (Engine) separada interface (UI).

## Fase 1: Prototipagem Visual
- **Space Ship:** Teclas, reatividade, Game Loop.
- **Modelo Pokémon:** Padrão Event-Driven, Screen Stack.
- **Render:** Mapa (bloco estático `rich.text.Text`), entidades (Widgets flutuantes).

## Fase 2: Integração/Anomalias
1. **Desalinhamento:** Entidades montadas filhos `mapa-fundo`, ponto (0,0) respeita limites mapa.
2. **Rastos Emojis:** Largura (`width`) CSS 2 para 3, limpa `bounding box` maior.
3. **Escadinha/Bloqueio:** Limpeza `styles.css`, coordenadas iniciais `__init__`, propriedades absolutas (top/left).
4. **Race Conditions:** `@work(thread=True)` substituído por `Timers` nativos (thread principal).

## Fase 3: Arquitetura (ECS)
- ECS: Entidade (ID), Componentes (dados), Sistemas (lógica).
- Engine Headless: Independente Textual.
- TDD: Testes rigorosos.

## Roadmap
1. Sistemas Lógicos: `MovementSystem` (colisões), `InteractionSystem` (Enter).
2. Event Bus: Fila mensagens Engine -> Interface.
3. Re-integração: `GamePlayScreen` assina Event Bus Engine.
