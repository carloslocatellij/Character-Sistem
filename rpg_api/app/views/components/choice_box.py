# app/views/components/choice_box.py
from textual.widget import Widget
from textual.widgets import Label, RadioSet, RadioButton, Button
from textual.containers import Vertical
from textual.message import Message

class ChoiceBox(Widget):
    """Widget customizado para exibir caixas de diálogo com escolhas dinâmicas em RPGs."""
    
    # 🛰️ MENSAGEM CUSTOMIZADA: Evento assíncrono disparado quando o jogador confirma
    class Selected(Message):
        def __init__(self, control: Widget, index: int, text: str) -> None:
            self.index = index      # Índice da opção (0, 1, 2...)
            self.text = text        # Texto da opção ("Sim", "Não"...)
            super().__init__()
            self._control = control

        @property
        def control(self) -> Widget:
            """O Textual lê esta propriedade para validar seletores por ID."""
            return self._control

    def __init__(self, mensagem: str, opcoes: list[str], **kwargs):
        super().__init__(**kwargs)
        self.mensagem_texto = mensagem
        self.opcoes_lista = opcoes

    def compose(self):
        """Monta a estrutura interna do widget."""
        with Vertical(id="choice-box-card"):
            yield Label(self.mensagem_texto, id="choice-label")
            
            with RadioSet(id="choice-radioset"):
                for idx, opcao in enumerate(self.opcoes_lista):
                    # Define a primeira opção como selecionada por padrão
                    yield RadioButton(opcao, value=(idx == 0))
            
            yield Button("Confirmar Escolha", variant="primary", id="choice-submit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Trata o clique ou Enter no botão de confirmação."""
        if event.button.id == "choice-submit":
            radioset = self.query_one("#choice-radioset", RadioSet)
            
            if radioset.pressed_button is not None:
                # Extrai os dados selecionados pelo jogador
                escolha_idx = radioset.pressed_index
                escolha_texto = str(radioset.pressed_button.label)
                
                # Dispara a mensagem para cima na hierarquia de telas
                self.post_message(self.Selected(self, escolha_idx, escolha_texto))
        
