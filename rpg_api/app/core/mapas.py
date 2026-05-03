from typing import List, Dict, Any
from app.modules.dungeon_gen import DungeonGenerator

class GestorDeMapas:
    """
    Adapter que conecta o submódulo independente 'dungeon_gen' 
    com o ecossistema e as entidades do nosso sistema de RPG.
    """
    
    @staticmethod
    def gerar_mapa_rpg(tipo: str, largura: int, altura: int, configs: Dict[str, Any]) -> List[List[str]]:
        """
        Lê as configurações do RPG e aciona o gerador independente correspondente.
        """
        # Extrai configurações seguras com valores padrão
        tile_chao = configs.get("tile_chao", "  ")
        tile_parede = configs.get("tile_parede", "🔳")
        
        # Inicializa o gerador agnóstico
        gerador = DungeonGenerator(
            largura=largura, 
            altura=altura, 
            tile_chao=tile_chao, 
            tile_parede=tile_parede
        )
        
        if tipo.lower() == "masmorra":
            max_salas = configs.get("max_salas", 15)
            tam_min = configs.get("tam_min_sala", 4)
            tam_max = configs.get("tam_max_sala", 10)
            
            matriz = gerador.gerar_bsp_dungeon(max_salas, tam_min, tam_max)
            # Futuramente podemos adicionar injetores de monstros e baús aqui:
            # matriz = GestorDeMapas._espalhar_monstros(matriz, configs)
            return matriz
            
        elif tipo.lower() == "vila":
            max_casas = configs.get("max_casas", 15)
            tam_min = configs.get("tam_min_casa", 3)
            tam_max = configs.get("tam_max_casa", 6)
            
            matriz = gerador.generate_village(max_casas, tam_min, tam_max)
            return matriz
        
        elif tipo.lower() == "caverna":
            taxa_preenchimento = configs.get("taxa_preenchimento", 55)
            suavisações = configs.get("iteracoes", 3)
            
            matriz = gerador.generate_caves(taxa_preenchimento, suavisações)
            return matriz
        
        return gerador.mapa # Retorna um mapa em branco/cheio se o tipo for desconhecido

    @staticmethod
    def exportar_csv(matriz: List[List[str]]) -> str:
        """Converte a matriz do mapa num formato string CSV."""
        return "\n".join([",".join(linha) for linha in matriz])

    @staticmethod
    def importar_csv(conteudo_csv: str) -> List[List[str]]:
        """Reconstrói a matriz do mapa a partir de uma string CSV."""
        linhas = conteudo_csv.strip().split("\n")
        return [linha.split(",") for linha in linhas]