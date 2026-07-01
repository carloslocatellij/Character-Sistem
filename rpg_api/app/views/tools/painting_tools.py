
from textual.events import MouseDown, MouseUp, MouseMove
from textual.message import Message
from textual.widgets import Static

class MapaInterativo(Static):
    """Componente customizado que exibe o mapa e captura movimentos contínuos do mouse."""

    class Pintar(Message):
        """Mensagem enviada continuamente enquanto o mouse é arrastado."""

        def __init__(self, linha: int, coluna: int, inicio_de_traco: bool = False):
            self.linha = linha
            self.coluna = coluna
            # Esta flag ajuda o sistema a saber quando tirar a "foto" para o Desfazer
            self.inicio_de_traco = inicio_de_traco
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse_pressionado = False   # O nosso "sensor" de clique
        self.capture_mouse()
        self.release_mouse()

    def on_mouse_down(self, event: MouseDown) -> None:
        """Apertou o botão do mouse: começa o traço e captura o foco."""
        self.mouse_pressionado = True
        self.capture_mouse()
        self.post_message(self.Pintar(
            event.y, event.x // 2, inicio_de_traco=True))

    def on_mouse_up(self, event: MouseUp) -> None:
        """Soltou o botão do mouse: termina o traço e liberta o foco."""
        self.mouse_pressionado = False
        if self.has_focus or self.mouse_pressionado == False:
            self.release_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        """Moveu o mouse: se estiver apertado, continua a pintar."""
        if self.mouse_pressionado:
            self.post_message(self.Pintar(
                event.y, event.x // 2, inicio_de_traco=False))
            

def balde_de_tinta(matriz_terrenos: list[list[str]], y_inicial: int, x_inicial: int, tile_novo: str) -> None:
    """
        Algoritmo iterativo de Flood Fill (Balde de Tinta).
        Varre e substitui células idênticas conectadas em 4 direções.
        """
    matriz = matriz_terrenos  # Adapte para a variável real da sua matriz (ex: self.loader.matriz_terrenos)
    altura = len(matriz)
    largura = len(matriz[0]) if altura > 0 else 0

    # Proteção de Limites
    if not (0 <= y_inicial < altura and 0 <= x_inicial < largura):
        return

    tile_antigo = matriz[y_inicial][x_inicial]

    # Evita loops infinitos caso o usuário clique com o mesmo tile já existente na célula
    if tile_antigo == tile_novo:
        return

    # Inicializa a pilha com a coordenada do clique inicial
    pilha = [(y_inicial, x_inicial)]

    while pilha:
        y, x = pilha.pop()

        # Se a célula atual contém o tile antigo, pinta e adiciona os vizinhos
        if matriz[y][x] == tile_antigo:
            matriz[y][x] = tile_novo

            # Adiciona vizinhos ortogonais válidos (Cima, Baixo, Esquerda, Direita)
            if y > 0:
                pilha.append((y - 1, x))
            if y < altura - 1:
                pilha.append((y + 1, x))
            if x > 0:
                pilha.append((y, x - 1))
            if x < largura - 1:
                pilha.append((y, x + 1))


def desenha_retangulo():
    pass

def desenha_circulo():
    pass