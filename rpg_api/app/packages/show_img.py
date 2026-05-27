from textual.app import App, ComposeResult
from textual.widgets import Static
from rich_pixels import Pixels
from rich.console import Console
from PIL import Image

class VisualizadorImagem(App):
    
    
    def compose(self) -> ComposeResult:
        # Carrega a imagem e converte para ASCII (usando ansi)

        with Image.open('the_begin_1.jpg') as image:
            pixels = Pixels.from_image(image)
        
        # Cria um widget estático com a imagem renderizada em arte
        yield Static(pixels)

if __name__ == "__main__":
    app = VisualizadorImagem()
    app.run()
