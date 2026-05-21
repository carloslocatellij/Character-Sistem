
class CatalogoTiles:
    """Registo central que define as categorias e propriedades visuais dos emojis."""
    
    # Listas para construir as abas
    TERRENOS = ["  ", "⬛", "🔲", "⬜", "🟫", "🟩", "🟦", "🟧", "🈸", "🈴", "🔯" ]
    TERRENOS_BLOQUEANTES = ["🔳", "🧱", "🔲", "🟦", "🟧"]
    
    OBJETOS = [ "🌲", "🌳", "🌴", "🌵", "🎄","🍄",
                "🌻", "🌹", "🌷","🌾" ,"🔮", "🌋", 
                "🗻", "🏠", "🎪", "🏤", "🕍", "🏰",
                "🕌", "⛺",  "⛲", "⌛", "🕋", "🧱",
                "🛶", "🧊", "📦", "📖", "📚", "🏴",
                "🍖", "🍗", "🍕", "🍺", "🍞", "🎃",
                "🧪", "🪑", "☕", "🚪" , "🦴", "💀",
                "🔱", "🗿", "🔹", "🍒", "🍀"]
    
    EVENTOS = ["📦", "🧙‍♂️", "👾", "🚪", "🧷"]
    
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
                  "capa": "🧥", "luvas": "🧤", "elmo": "🪖", "botas": "👢", "cap": "🧢",},
    "escudos": {"escudo": "🛡️",  "escudo de ferro": "🛡️", "escudo de madeira": "🛡️",},
    "outros": {
            "bau": "💼", 
            "bau de ferro": "💼",
            "bau de madeira": "💼",
            "bau de ouro": "💼",
            "poção": "🧪",
            "poção de vida": "🧪",
            "poção de mana": "🧪",
            "chave" : "🗝️",
            "chave de ouro": "🗝️",
            "livro" : "📖",
            "livro de feitiços": "📖",
            "pergaminho": "📜",
            "amuleto": "🪬",
            "tocha": "🔥", 
            "moeda": "🪙",
            "saco de moedas": "💰",
            "corda": "🪢",  
            "anel": "💍",
            "colar": "📿",
            "bracelete": "📿",
            "broche": "📿",
            "mochila": "👜",
    }
        }

dict_emoji_efeito = {
        "fogo": "🔥", "agua": "🌊", "terra": "🪨", "ar": "🌬️",
        "luz": "🌅", "trevas": "🪯", "eter": "🌌", "sangue": "🩸",
        "raio": "⚡", "planta": "🌱", "metal": "🔩", 
        }

dict_emoji_racas = {
        "humano": "👨‍🦱", 
        "orc": "🧌",
        "goblin": "👾",
        "elfo": "🧝",
        "anão": "🧔🏽",
        "troll": "🧟",
        "zumbi": "🧟‍♂️",
        "vampiro": "🧛",
        "golem": "🤖",
        "ogro": "👹",
        "gnomo": "👺",
        "draconio": "🐉",
        "anjo": "👼",
        "demonio": "😈",
        "fada": "🧚",
        "sereia": "🧜‍♀️",
        "centauro": "🐎",
        "minotauro": "🐂",
        "esqueleto": "💀",
        "mumia": "🧟‍♀️",
        "licantropo": "🐺",
        "elemental": "🌪️",
        "homenlagarto": "🦖",
        "octopus": "🐙", 
      }

