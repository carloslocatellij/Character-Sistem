from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive  # Importante para observar variáveis

# Estilos CSS
CSS = """
Screen {
    align: center middle;
    background: #1e1e1e;
}

Screen.flash-red {
    background: #8b0000;
}

#arena {
    width: 60;
    height: 15;
    border: heavy white;
    background: #2d2d2d;
}

.combatente {
    width: 5;
    height: 1;
    content-align: center middle;
    text-style: bold;
    position: absolute; 
}

.tomando-dano {
    background: yellow;
    color: black;
}
"""


class Combatente(Static):
    """Subclasse de Static para gerenciar o X numérico de forma reativa."""
    # Declaramos o x_pos como reativo. Mudar esse número dispara o watch_x_pos automaticamente.
    x_pos = reactive(0.0)

    def watch_x_pos(self, novo_x: float) -> None:
        """Sempre que x_pos mudar (via animação), atualiza o offset visual."""
        # Mantemos o Y sempre fixo em 5 e atualizamos apenas o X de forma limpa
        self.styles.offset = (int(novo_x), 5)


class JogoAtaqueApp(App):
    CSS = CSS
    BINDINGS = [("space", "atacar", "Atacar!")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Static(id="arena"):
                # Usamos nossa nova classe Combatente em vez do Static puro
                yield Combatente("🧙", id="atacante", classes="combatente")
                yield Combatente("👹", id="alvo", classes="combatente")
        yield Footer()

    def on_mount(self) -> None:
        """Configura a posição inicial baseada nos números puros."""
        atacante = self.query_one("#atacante")
        alvo = self.query_one("#alvo")

        # Define os valores iniciais numéricos
        atacante.x_pos = 5.0
        alvo.x_pos = 45.0

    def action_atacar(self) -> None:
        """Ação disparada ao apertar ESPAÇO."""
        atacante = self.query_one("#atacante")

        # Agora animamos a propriedade pura 'x_pos' (um float padrão)
        # O Textual aceita floats nativamente sem disparar AssertionError
        atacante.animate(
            "x_pos",
            value=40.0,
            duration=0.15,
            on_complete=self.aplicar_dano
        )

    def aplicar_dano(self) -> None:
        """Callback executado assim que o atacante encosta no alvo."""
        atacante = self.query_one("#atacante")
        alvo = self.query_one("#alvo")
        screen = self.screen

        alvo.update("💥")
        screen.add_class("flash-red")
        alvo.add_class("tomando-dano")

        # Mantém o efeito visual na tela por 0.2 segundos
        self.set_timer(0.2, self.resetar_impacto)

        # Anima a volta numérica do mago para o X=5 original
        atacante.animate(
            "x_pos",
            value=5.0,
            duration=0.2
        )

    def resetar_impacto(self) -> None:
        """Remove os efeitos de piscar e restaura o emoji original."""
        alvo = self.query_one("#alvo")
        screen = self.screen

        screen.remove_class("flash-red")
        alvo.remove_class("tomando-dano")
        alvo.update("👹")


if __name__ == "__main__":
    app = JogoAtaqueApp()
    app.run()
