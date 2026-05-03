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

    def intersect(self, other: 'Rect', casa=False) -> bool:
        """Verifica se este retângulo se sobrepõe a outro."""
        if not casa:
            return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                        self.y1 <= other.y2 and self.y2 >= other.y1)
        else:
            return (self.x1 <= other.x2 + 1 and self.x2 >= other.x1 - 1 and
                        self.y1 <= other.y2 + 1 and self.y2 >= other.y1 - 1)
            
class circle:
    """Representa um círculo, usado para criar poços ou lagos."""
    def __init__(self, x: int, y: int, r: int):
        self.x = x
        self.y = y
        self.r = r
        
    def center(self) -> Tuple[int, int]:
        """Retorna as coordenadas do centro do retângulo."""
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersect(self, other: 'circle') -> bool:
        """Verifica se este círculo se sobrepõe a outro."""
        distance_squared = (self.x - other.x) ** 2 + (self.y - other.y) ** 2
        radius_sum_squared = (self.r + other.r) ** 2
        return distance_squared < radius_sum_squared
    

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
        self.casas: List[Rect] = []

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
                
    def criar_casa(self, casa):
        """Cria uma casa com paredes e um chão, além de uma porta aleatória."""
        for x in range(casa.x1 , casa.x2 + 1):
            for y in range(casa.y1 , casa.y2 + 1):
                self.mapa[y][x] = self.tile_parede

        for x in range(casa.x1 + 1, casa.x2):
            for y in range(casa.y1 + 1, casa.y2):
                self.mapa[y][x] = self.tile_chao

        north_door = (casa.y1, random.choice(range(casa.x1 +1, casa.x2 -1)))
        south_door = (casa.y2, random.choice(range(casa.x1 +1, casa.x2 -1)))
        west_door =  (random.choice(range(casa.y1 +1, casa.y2 -1)), casa.x1)
        east_door =  (random.choice(range(casa.y1 +1, casa.y2 -1)), casa.x2)

        choice_door = random.choice([north_door, south_door, west_door, east_door])
        self.mapa[choice_door[0]][choice_door[1]] = '🚪'

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
    
    def generate_caves(self, fill_percent=55, smoothing_iterations=3):
        for y in range(self.altura):
            for x in range(self.largura):
                if x == 0 or x == self.largura - 1 or y == 0 or y == self.altura - 1:
                    self.mapa[y][x] = self.tile_parede
                else:
                    self.mapa[y][x] = self.tile_chao if random.randint(0, 100) < fill_percent else self.tile_parede


        for _ in range(smoothing_iterations):
            new_mapa = [row[:] for row in self.mapa]
            for y in range(1, self.altura - 1):
                for x in range(1, self.largura - 1):
                    neighbors = 0
                    for ny in range(y - 1, y + 2):
                        for nx in range(x - 1, x + 2):
                            if nx == x and ny == y: continue
                            if self.mapa[ny][nx] ==  self.tile_parede:
                                neighbors += 1
                    if neighbors > 4:
                        new_mapa[y][x] = self.tile_parede
                    elif neighbors < 4:
                        new_mapa[y][x] = self.tile_chao
            self.mapa = new_mapa
        return self.mapa
            
            

    def generate_village(self, max_casas, casa_min_size, casa_max_size):
        for y in range(self.altura):
              for x in range(self.largura):
                  if x == 0 or x == self.largura - 1 or y == 0 or y == self.altura - 1:
                      self.mapa[y][x] = self.tile_parede
                  else:
                    self.mapa[y][x] = self.tile_chao

        for r in range(max_casas):
            w = random.randint(casa_min_size, casa_max_size)
            h = random.randint(casa_min_size, casa_max_size)
            x = random.randint(2, self.largura - w - 3)
            y = random.randint(2, self.altura - h - 3)

            new_casa = Rect(x, y, w, h)
            failed = False
            for other_casa in self.casas:
                if new_casa.intersect(other_casa, casa=True):
                    failed = True
                    break
            
            if not failed:
                self.criar_casa(new_casa)
                (new_x, new_y) = new_casa.center()
                self.casas.append(new_casa)
        return self.mapa