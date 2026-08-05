# Regra 3: Interface TUI (Textual)

Uso de `Textual`. Diretrizes para reatividade, prevenir travamentos e bugs:

## 1. Eventos Customizados

- **`control` obrigatório:** Mensagens evento (herdam `textual.message.Message`) filtradas com `@on` *devem* expor propriedade `control` apontando para Widget origem. Falta causa `OnDecoratorError`.

  ```python
  # Exemplo correto
  class CustomEvent(Message):
      def __init__(self, control: Widget, data: str) -> None:
          super().__init__()
          self._control = control
          self.data = data
      
      @property
      def control(self) -> Widget:
          return self._control
  ```

---

## 2. Prevenção Conflitos Threads

- **Sem threads nativas para mutações:** `@work(thread=True)` causa colisões.
- **Solução Reativa:**
  - Use Timers nativos (`set_interval`, `set_timer`) na thread principal.
  - Use `self.call_next(callback)` para alterações foco/exibição após layout.
  - Chamadas async externas (rede/Supabase): `async` nativo não-bloqueante no fluxo asyncio Textual.

---

## 3. Gestão CSS e Layouts

- **Separação Rígida:** Estilos em arquivos `.css` (`rpg_api/app/views/styles/styles.css`, `game_styles.css`). Zero design inline em Python.
- **Diálogos:** Abrir `ChoiceBox` sobre painéis: reajuste `.styles.height` do painel para ceder espaço. Restaure ao fechar.
- **Foco/Teclas (Input Blocking):**
  - Diálogo/escolha ativo: capture WASD/setas em `on_key` principal e **consuma evento** (bloqueia movimento).
  - Foque novo elemento (`choice_box.focus()`) via `call_next`.
