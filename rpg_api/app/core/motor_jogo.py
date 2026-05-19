class MotorRPG:
    """
    O cérebro do jogo. Gerencia o estado atual do mapa, colisões e eventos.
    """
    def __init__(self, matriz_base: list[list[str]], dict_objetos: dict, dict_eventos: dict, posicao_inicial: tuple[int, int]):
        self.matriz_base = matriz_base
        
        # Separação estrita de entidades (ECS)
        self.objetos = dict_objetos   # Camada visual
        self.eventos = dict_eventos   # Camada lógica
        
        self.pos_jogador = posicao_inicial
        self.direcao_olhar = "baixo"
        
        self.tiles_bloqueantes = ["🔲", "🟦"]

    def mover_personagem(self, d_linha: int, d_coluna: int) -> bool:
        """
        Tenta mover o personagem. 
        Retorna True se moveu com sucesso, False se colidiu.
        """
        # 1. Atualiza a direção para onde o personagem está a olhar
        self._atualizar_direcao(d_linha, d_coluna)

        linha_atual, col_atual = self.pos_jogador
        nova_linha = linha_atual + d_linha
        nova_coluna = col_atual + d_coluna

        # 2. Verifica a colisão (A Física do Jogo)
        if self._pode_caminhar(nova_linha, nova_coluna):
            self.pos_jogador = (nova_linha, nova_coluna)
            return True
        
        return False
    

    def _atualizar_direcao(self, d_linha: int, d_coluna: int):
        if d_linha == -1: self.direcao_olhar = "cima"
        elif d_linha == 1: self.direcao_olhar = "baixo"
        elif d_coluna == -1: self.direcao_olhar = "esquerda"
        elif d_coluna == 1: self.direcao_olhar = "direita"

    def _pode_caminhar(self, linha: int, coluna: int) -> bool:
        """Verifica colisões com Paredes, Objetos de Cenário e Eventos."""
        # 1. Limites do Mapa
        if not (0 <= linha < len(self.matriz_base) and 0 <= coluna < len(self.matriz_base[0])):
            return False
            
        # 2. Colisão com Matriz Base (Paredes/Água)
        if self.matriz_base[linha][coluna].strip() in self.tiles_bloqueantes:
            return False
            
        # 3. Colisão com Objetos de Cenário (Cadeiras, Árvores)
        if (linha, coluna) in self.objetos:
            return False
            
        # 4. Colisão com Eventos Físicos (Baús, NPCs)
        # Nota: Futuramente, podemos adicionar uma propriedade 'atravessavel: True' 
        # aos eventos no banco de dados para coisas como 'armadilhas de chão'.
        if (linha, coluna) in self.eventos:
            return False

        return True

    def _obter_coordenada_frente(self) -> tuple[int, int]:
        linha, coluna = self.pos_jogador
        if self.direcao_olhar == "cima": return (linha - 1, coluna)
        elif self.direcao_olhar == "baixo": return (linha + 1, coluna)
        elif self.direcao_olhar == "esquerda": return (linha, coluna - 1)
        elif self.direcao_olhar == "direita": return (linha, coluna + 1)
        return (linha, coluna)

    def interagir(self) -> dict | None:
        """
        Executa a ação 'Enter'. 
        Devolve os dados do Evento se houver um na frente do jogador.
        """
        coordenada_alvo = self._obter_coordenada_frente()
        
        # O motor olha EXCLUSIVAMENTE para a camada de eventos!
        evento_alvo = self.eventos.get(coordenada_alvo)
        
        if evento_alvo:
            # Retornamos o dicionário completo que veio do banco de dados!
            return evento_alvo
            
        return None