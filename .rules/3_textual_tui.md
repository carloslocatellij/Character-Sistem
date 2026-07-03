# Regra 3: Interface Visual TUI (Textual Framework)

A interface gráfica de terminal (TUI) utiliza o framework `Textual`. Para manter a reatividade, evitar travamentos de tela e bugs de renderização, siga estas diretrizes:

## 1. Tratamento de Eventos Customizados e Mensagens

- **Propriedade `control` obrigatória:** Ao criar uma mensagem de evento customizada (que herde de `textual.message.Message`) e filtrá-la na TUI usando o decorador `@on` com um seletor (ex: `@on(ChoiceBox.Selected, "#input-id")`), você **deve obrigatoriamente** expor a propriedade `control` apontando para o Widget de origem. A ausência desta propriedade causará uma exceção crítica (`OnDecoratorError`) no loop interno de eventos do Textual.
  
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

## 2. Prevenção de Conflitos de Threads (Race Conditions)

- **Não use concorrência de threads nativas para mutações visuais:** O uso de `@work(thread=True)` para executar loops lógicos que alteram diretamente componentes ou estados da UI gera colisões de concorrência graves.
- **Solução Reativa Segura:**
  - Utilize os mecanismos de agendamento e Timers nativos do Textual (`set_interval`, `set_timer`) que rodam com segurança na thread principal (Main Event Loop).
  - Use `self.call_next(callback)` para garantir que alterações de foco e exibição ocorram somente após a conclusão do ciclo de layout atual.
  - Para chamadas assíncronas externas (como chamadas de rede/Supabase), use `async` do python de forma nativa e não-bloqueante no fluxo do loop do asyncio do Textual.

---

## 3. Gestão Dinâmica de CSS e Layouts

- **Separação Rígida:** Os estilos visuais devem ficar localizados nos arquivos `.css` correspondentes (ex: `rpg_api/app/views/styles/styles.css` e `game_styles.css`). Evite misturar atributos de design inline no código Python.
- **Redimensionamento sob Diálogos:** Quando caixas de escolhas interativas (`ChoiceBox`) ou menus forem abertos dinamicamente em cima de painéis rígidos, reajuste a propriedade CSS `.styles.height` do painel afetado para ceder espaço e evitar quebras de enquadramento da TUI. Restaure para o estado original (ex: `None`) ao finalizar o diálogo.
- **Foco e Interceptação de Teclas (Input Blocking):**
  - Enquanto o jogo estiver aguardando que o jogador responda a um diálogo ou faça uma escolha, capture as teclas direcionais (WASD ou setas) no método `on_key` da tela principal e **consuma o evento** (impeça que ele execute o movimento do personagem).
  - Garanta que o foco de teclado seja explicitamente direcionado ao novo elemento aberto (ex: `choice_box.focus()`) no ciclo adequado utilizando `call_next`.
