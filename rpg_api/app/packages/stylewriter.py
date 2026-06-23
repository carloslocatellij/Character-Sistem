import asyncio
from pyfiglet import figlet_format, FontNotFound
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Header, Footer, Input, Static
import esper
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


class MensagemAnimada(Static):
    """Widget interno que gerencia a animação de uma única mensagem."""

    def __init__(self, texto: str, estilo_figlet: str | None, velocidade: float, _id, **kwargs):
        self._id = _id
        super().__init__(**kwargs)
        self.texto_original = texto
        self.estilo_figlet = estilo_figlet
        self.velocidade = velocidade

        # Variáveis de controle da animação
        self.texto_final = ""
        self.linhas_figlet = []
        self.max_colunas = 0
        self.passo_atual = 0

    def on_mount(self) -> None:
        # 1. Processa o texto inicial (Pyfiglet ou Puro)
        if self.estilo_figlet:
            try:
                self.texto_final = figlet_format(
                    self.texto_original, font=self.estilo_figlet)
            except FontNotFound:
                self.texto_final = self.texto_original
        else:
            self.texto_final = self.texto_original

        # 2. Configura a estratégia de animação baseada no tipo de texto
        if "\n" not in self.texto_final.strip():
            # Texto Puro: avança de 1 em 1 caractere
            self.max_colunas = len(self.texto_final)
        else:
            # Texto Pyfiglet: quebra em linhas e descobre a maior coluna
            self.linhas_figlet = self.texto_final.splitlines()
            if self.linhas_figlet:
                self.max_colunas = max(len(linha)
                                       for linha in self.linhas_figlet)

        # 3. Inicia o Timer nativo do Textual para atualizar a tela no intervalo correto
        if self.max_colunas > 0:
            self.timer_animacao = self.set_interval(
                self.velocidade, self.avancar_animacao)
        else:
            self.update(self.texto_final)
            if self.parent and hasattr(self.parent, "on_mensagem_terminada"):
                self.parent.on_mensagem_terminada()
            
    def avancar_animacao(self) -> None:
        """Avança um frame da animação a cada tique do timer."""
        self.passo_atual += 1

        # Condição de parada: a animação chegou ao fim
        if self.passo_atual > self.max_colunas:
            self.timer_animacao.stop()
            if self.parent and hasattr(self.parent, "on_mensagem_terminada"):
                self.parent.on_mensagem_terminada()
            return self.timer_animacao

        if not self.linhas_figlet:
            # Renderiza texto puro progressivamente
            self.update(self.texto_final[:self.passo_atual])
        else:
            # Renderiza colunas do Pyfiglet progressivamente
            frame_atual = [linha[:self.passo_atual]
                           for linha in self.linhas_figlet]
            self.update("\n".join(frame_atual))

        # Força o chat a rolar para baixo enquanto o texto cresce
        if self.parent:
            self.parent.scroll_end()


class ChatLog(VerticalScroll):
    """Widget customizado que se comporta como uma área de log com suporte a animações Rich."""

    DEFAULT_CSS = """
    ChatLog {
        background: $surface;
    }
    MensagemAnimada {
        height: auto;
    }
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._id = kwargs.get("id", "area-interacao")
        self.fila_mensagens = []
        self.mensagem_ativa = None

    def escrever(self, texto: str, estilo: str | None = None, velocidade: float = 0.01) -> None:
        """Adiciona uma nova mensagem à fila e inicia a reprodução se ocioso."""
        self.fila_mensagens.append((texto, estilo, velocidade))
        self.processar_fila()

    def processar_fila(self) -> None:
        """Processa a próxima mensagem da fila."""
        if self.mensagem_ativa is not None or not self.fila_mensagens:
            return

        texto, estilo, velocidade = self.fila_mensagens.pop(0)
        try:
            nova_mensagem = MensagemAnimada(
                texto=texto,
                estilo_figlet=estilo,
                velocidade=velocidade,
                expand=True,
                _id=self._id,
            )
        except Exception as e:
            logging.error(f"Erro ao criar MensagemAnimada: {e}")
            nova_mensagem = Static(texto)  # Fallback simples sem animação

        self.mensagem_ativa = nova_mensagem
        self.mount(nova_mensagem)

        if not hasattr(nova_mensagem, "max_colunas") or nova_mensagem.max_colunas <= 0:
            self.on_mensagem_terminada()

    def on_mensagem_terminada(self) -> None:
        """Notificado quando uma mensagem termina de ser impressa."""
        self.mensagem_ativa = None
        self.scroll_end()
        self.processar_fila()


#Daqui para baixo é só para testes.

class TestApp(App):

    def compose(self) -> ComposeResult:
        yield Header()
        yield ChatLog(id="log-eventos")
        yield Input(placeholder="Digite seu comando aqui e aperte Enter...", id="entrada-usuario")
        yield Footer()

    async def on_mount(self) -> None:
        log = self.query_one("#log-eventos", ChatLog)

        # Exemplo 1: Imprimindo título estilizado com Pyfiglet (ajustado velocidade para o timer)
        log.escrever("RPG API v1.0", estilo="slant", velocidade=0.2)
        log.escrever("Desenvolvida por CharlesDev",
                     estilo="slant", velocidade=0.1)

        await asyncio.sleep(1.5)  # Pausa dramática para a animação rodar

        # Exemplo 2: Imprimindo texto normal com formatação de cores Rich
        log.escrever(
            "[bold yellow]Sistema:[/] Conexão estabelecida com sucesso.", velocidade=0.03)
        log.escrever(
            "Você acorda em uma taverna escura. O cheiro de hidromel paira no ar...", velocidade=0.02)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Captura o comando enviado pelo jogador e joga no nosso ChatLog."""
        log = self.query_one("#log-eventos", ChatLog)
        input_campo = self.query_one("#entrada-usuario", Input)

        if event.value.strip():
            log.escrever(f"[bold cyan]> {event.value}[/]", velocidade=0.01)
            input_campo.value = ""

            # Resposta simulada do jogo
            await asyncio.sleep(1)
            log.escrever(
                "[bold red]Comando desconhecido.[/] Tente novamente.", velocidade=0.02)


if __name__ == '__main__':
    app = TestApp()
    app.run()

