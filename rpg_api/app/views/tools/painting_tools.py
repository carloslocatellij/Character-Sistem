

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
