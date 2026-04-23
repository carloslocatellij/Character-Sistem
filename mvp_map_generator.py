import random

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
      

class DungeonGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [['🔳' for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.houses = []

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.grid[y][x] = '⬛'


    def create_house(self, house):

        for x in range(house.x1 , house.x2 + 1):
            for y in range(house.y1 , house.y2 + 1):
                self.grid[y][x] = '🔳'

        for x in range(house.x1 + 1, house.x2):
            for y in range(house.y1 + 1, house.y2):
                self.grid[y][x] = '⬛'

        north_door = (house.y1, random.choice(range(house.x1 +1, house.x2 -1)))
        south_door = (house.y2, random.choice(range(house.x1 +1, house.x2 -1)))
        west_door =  (random.choice(range(house.y1 +1, house.y2 -1)), house.x1)
        east_door =  (random.choice(range(house.y1 +1, house.y2 -1)), house.x2)

        choice_door = random.choice([north_door, south_door, west_door, east_door])
        self.grid[choice_door[0]][choice_door[1]] = '🚪'



    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = '⬛'

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = '⬛'


    def generate(self, max_rooms, room_min_size, room_max_size):
        for r in range(max_rooms):
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            x = random.randint(0, self.width - w - 1)
            y = random.randint(0, self.height - h - 1)

            new_room = Rect(x, y, w, h)
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()

                if len(self.rooms) > 0:
                    (prev_x, prev_y) = self.rooms[-1].center()
                    if random.randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.rooms.append(new_room)


    def generate_caves(self, fill_percent=45, smoothing_iterations=5):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.grid[y][x] = '🔳'
                else:
                    self.grid[y][x] = '🔳' if random.randint(0, 100) < fill_percent else '⬛'


        for _ in range(smoothing_iterations):
            new_grid = [row[:] for row in self.grid]
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    neighbors = 0
                    for ny in range(y - 1, y + 2):
                        for nx in range(x - 1, x + 2):
                            if nx == x and ny == y: continue
                            if self.grid[ny][nx] == '🔳':
                                neighbors += 1
                    if neighbors > 4:
                        new_grid[y][x] = '🔳'
                    elif neighbors < 4:
                        new_grid[y][x] = '⬛'
            self.grid = new_grid


    def generete_village(self, max_houses, house_min_size, house_max_size):
        for y in range(self.height):
              for x in range(self.width):
                  if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                      self.grid[y][x] = '🔳'
                  else:
                    self.grid[y][x] = '⬛'

        for r in range(max_houses):
            w = random.randint(house_min_size, house_max_size)
            h = random.randint(house_min_size, house_max_size)
            x = random.randint(2, self.width - w - 3)
            y = random.randint(2, self.height - h - 3)

            new_house = Rect(x, y, w, h)
            failed = False
            for other_house in self.houses:
                if new_house.intersect(other_house):
                    failed = True
                    break
            
            if not failed:
                self.create_house(new_house)
                (new_x, new_y) = new_house.center()
                self.houses.append(new_house)


    def place_entities(self, entities_dict):
        """Recebe um dict como {'👾': 5, '💰': 3} e espalha no mapa."""
        walkable_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '⬛':
                    walkable_cells.append((x, y))
                    

        random.shuffle(walkable_cells)

        for char, count in entities_dict.items():
            for _ in range(count):
                if not walkable_cells: break
                x, y = walkable_cells.pop()
                self.grid[y][x] = char

    def display(self):
        for row in self.grid:
            print(''.join(row))
            
# Configurações da Masmorra
MAP_WIDTH = 35
MAP_HEIGHT = 35
MAX_ROOMS = 18
ROOM_MIN_SIZE = 4
ROOM_MAX_SIZE = 9

entities = {
    '👾': 15,
    '💰': 12,
    '🚪': 2  # Saída
}


dungeon = DungeonGenerator(MAP_WIDTH, MAP_HEIGHT)
dungeon.generate(MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
dungeon.place_entities(entities)
dungeon.display()

# Configurações da Caverna
MAP_WIDTH = 35
MAP_HEIGHT = 25

dungeon = DungeonGenerator(MAP_WIDTH, MAP_HEIGHT)
dungeon.generate_caves(fill_percent=40, smoothing_iterations=2)

# Adicionando Inimigos (👾) e Itens (💰)
entities = {
    '👾': 5,
    '💰': 2,
    '🚪': 1  # Saída
}

dungeon.place_entities(entities)
dungeon.display()

# Configuração de Cidade
MAP_WIDTH = 35
MAP_HEIGHT = 35
MAX_HOUSES, HOUSE_MIN_SIZE, HOUSE_MAX_SIZE = 22, 3, 7

dungeon = DungeonGenerator(MAP_WIDTH, MAP_HEIGHT)
dungeon.generete_village(MAX_HOUSES, HOUSE_MIN_SIZE, HOUSE_MAX_SIZE)

# Adicionando Inimigos (👾) e Itens (💰)
entities = {
    '👾': 5,
    '💰': 2,
    '🍖': 1  # Saída
}

#dungeon.place_entities(entities)
dungeon.display()