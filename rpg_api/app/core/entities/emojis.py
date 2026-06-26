import os
from rich.text import Text

class CatalogoTiles:
    """Registo central que define as categorias e propriedades visuais dos emojis."""
    
    # Listas para construir as abas
    TERRENOS = [ "🔳", "🔲", "⬜", "🟫", "🟩", "🟦", "🟧", "🈸", "🈴", "🔯" ]
    TERRENOS_BLOQUEANTES = ["⬛", "🔳", "🧱", "🔲", "🟦", "🟧"]
    
    OBJETOS = [ "🌲", "🌳", "🌴", "🌵", "🎄","🍄",
                "🌻", "🌹", "🌷", "🌾", "🌼", "🔮",
                "🌋", "🗻", "🏠", "🎪", "🏤", "🕍",
                "🏰", "🕌", "⛺",  "⛲", "⌛", "🕋",
                "🧱", "🛶", "🧊", "📦", "📖", "📚",
                "🏴", "🍖", "🍗", "🍕", "🍺", "🍞",
                "🎃", "🧪", "🪑", "☕", "🚪" , "🦴", 
                "💀", "📚", "📕", "📗", "📖", "🎋", 
                "🪔", "🔱", "🗿", "🔹", "🍒", "🍀", ]
    
    EVENTOS = ["🧙", "👨", "👩", "👦", "👧", "👳",
               "💂", "👷", "🤴", "🧝", "🧚", "👽",
               "💀", "🦝", "🐷", "🐻", "🦊", "🐥",
               "👾", "🚪", "📦", "🧷", "🕳 ", "🌾",
               "🏠", "🎪", "🏤", "🕍", "🏰", "🕌",
               "⛺", "🔑", "🍺", "🍷" , "🍗", "🍕",
               "🍎", "🍒", "📚", "📕", "📗", "📖",
               "🔔", "👑", "🛒", "🔮", "📜",  "  "]
    
    # Mapeamento de cores de fundo para os terrenos
    CORES_BG = {
        "⬛": "#221F1F",
        "🟫": "#B45428",
        "🟩": "#228B22",
        "🔳": "#808080",
        "🟦": "#0000FF"
    }
    
    
    @classmethod
    def obter_tipo(cls, tile: str) -> str:
        """Verifica se o pincel é um terreno, um objeto estático ou um evento lógico."""
        tile_limpo = tile.strip()
        if tile_limpo in cls.TERRENOS:
            return "terreno"
        if tile_limpo in cls.EVENTOS:
            return "evento" # <- NOVA CATEGORIA DETECTADA!
        return "objeto"

    @classmethod
    def obter_cor_fundo(cls, tile: str) -> str:
        """Pega o código hexadecimal da cor de fundo de um chão."""
        tile_limpo = tile.strip()
        return cls.CORES_BG.get(tile_limpo, "")

dict_item_emoji = {
    "armas": {"espada": "🗡️","espada longa": "🗡️","espada curta": "🗡️", "machado": "🪓", "arco": "🏹",
              "arco longo": "🏹", "arco curto": "🏹", "picareta": "⛏️",
              },
    "armaduras": {"armadura": "🦺", "armadura de placas": "🧥", "cota de malha": "🥼", "couro batido": "🦺",
                  "capa": "🧥", "luvas": "🧤", "elmo": "🧢", "botas": "👢", "cap": "🧢",},
    "escudos": {"escudo": "🛡️",  "escudo de ferro": "🛡️", "escudo de madeira": "🛡️",},
    "outros": {
        "bau": "💼",
        "bau de madeira": "📦",
            "bau de ouro": "🕋",
            "poção": "🧪",
            "poção de vida": "🌡 ",
            "poção de mana": "🧪",
            "chave" : "🗝️",
            "chave de ouro": "🗝️",
            "livro" : "📖",
            "livro de feitiços": "📕",
            "pergaminho": "📜",
            "tocha": "🔥", 
            "saco de moedas": "💰",
            "anel": "💍",
            "colar": "📿",
            "bracelete": "📿",
            "broche": "📿",
            "mochila": "👜",
            "cama": "🛏 "
    }
        }

dict_emoji_efeito = {
        "fogo": "🔥", "agua": "🌊", "terra": "🟤", "ar": "🌬️",
        "luz": "🌅", "trevas": "💫", "eter": "🌌", "sangue": "🩸",
        "raio": "⚡", "planta": "🌱", "metal": "🔩", 
        }

dict_emoji_racas = {
        "humano": "👨", 
        "orc": "🐷",
        "goblin": "👾",
        "elfo": "🧝",
        "anão": "🧔",
        "troll": "🤢",
        "zumbi": "🧟",
        "vampiro": "🧛",
        "golem": "🤖",
        "ogro": "👹",
        "gnomo": "👺",
        "draconio": "🐉",
        "anjo": "👼",
        "demonio": "😈",
        "fada": "🧚",
        "sereia": "🧜",
        "centauro": "🐎",
        "minotauro": "🐂",
        "esqueleto": "💀",
        "mumia": "🧟",
        "licantropo": "🐺",
        "elemental": "🌪️",
        "homenlagarto": "🦖",
        "octopus": "🐙", 
      }

def padronizar_largura_tile(tile_string: str) -> str:
    """
    Verifica a largura visual do caractere e adapta o preenchimento
    com base nas peculiaridades do emulador de terminal atual.
    """
    tile_limpo = tile_string.strip()
    eh_gnome_ou_linux = "VTE_VERSION" in os.environ or "GNOME_TERMINAL_SCREEN" in os.environ or os.name == "posix"

    # 2. Calcula a largura teórica pela biblioteca Rich
    largura_teorica = Text(tile_limpo).cell_len

    # 3. Estratégia de Ajuste Multiplataforma
    if largura_teorica == 1:
        return f"{tile_limpo} "
    elif largura_teorica == 2:
        emojis_rebeldes = ["🕸️", "🏘️", "🏚️", "🏯",] 
        
        # if eh_gnome_ou_linux and tile_limpo in emojis_rebeldes:
        #     return f"{tile_limpo} " 
        # return tile_limpo
        if tile_limpo in emojis_rebeldes:
            return f"{tile_limpo} " 

    return tile_limpo