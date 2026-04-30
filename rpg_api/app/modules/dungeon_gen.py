import random
from typing import List, Tuple

class Rect:
    """Representa um retângulo, usado para criar salas e construções."""
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self) -> Tuple[int, int]:
        """Retorna as coordenadas do centro do retângulo."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersect(self, other: 'Rect') -> bool:
        """Verifica se este retângulo se sobrepõe a outro."""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class DungeonGenerator:
    """
    Gerador Procedimental Puro. 
    Totalmente agnóstico: não possui dependências de banco de dados ou frameworks externos.
    """
    def __init__(self, largura: int, altura: int, tile_chao: str = ".", tile_parede: str = "#"):
        self.largura = largura
        self.altura = altura
        self.tile_chao = tile_chao
        self.tile_parede = tile_parede
        # Inicializa o mapa preenchido com paredes
        self.mapa = [[self.tile_parede for _ in range(self.largura)] for _ in range(self.altura)]
        self.salas: List[Rect] = []

    def criar_sala(self, sala: Rect):
        """Escava uma sala na matriz do mapa."""
        for x in range(sala.x1 + 1, sala.x2):
            for y in range(sala.y1 + 1, sala.y2):
                if 0 < x < self.largura - 1 and 0 < y < self.altura - 1:
                    self.mapa[y][x] = self.tile_chao

    def criar_tunel_horizontal(self, x1: int, x2: int, y: int):
        """Escava um túnel horizontal."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 < x < self.largura - 1 and 0 < y < self.altura - 1:
                self.mapa[y][x] = self.tile_chao

    def criar_tunel_vertical(self, y1: int, y2: int, x: int):
        """Escava um túnel vertical."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 < x < self.largura - 1 and 0 < y < self.altura - 1:
                self.mapa[y][x] = self.tile_chao

    def gerar_bsp_dungeon(self, max_salas: int, tam_min_sala: int, tam_max_sala: int) -> List[List[str]]:
        """
        Algoritmo principal que gera a masmorra completa ligando as salas.
        Retorna a matriz pronta.
        """
        for _ in range(max_salas):
            w = random.randint(tam_min_sala, tam_max_sala)
            h = random.randint(tam_min_sala, tam_max_sala)
            x = random.randint(1, self.largura - w - 1)
            y = random.randint(1, self.altura - h - 1)

            nova_sala = Rect(x, y, w, h)
            
            # Verifica se sobrepõe outras salas
            sobrepoe = any(nova_sala.intersect(outra_sala) for outra_sala in self.salas)
            
            if not sobrepoe:
                self.criar_sala(nova_sala)
                if len(self.salas) > 0:
                    (novo_x, novo_y) = nova_sala.center()
                    (antigo_x, antigo_y) = self.salas[-1].center()

                    if random.randint(0, 1) == 1:
                        self.criar_tunel_horizontal(antigo_x, novo_x, antigo_y)
                        self.criar_tunel_vertical(antigo_y, novo_y, novo_x)
                    else:
                        self.criar_tunel_vertical(antigo_y, novo_y, antigo_x)
                        self.criar_tunel_horizontal(antigo_x, novo_x, novo_y)

                self.salas.append(nova_sala)

        return self.mapa