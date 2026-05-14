import asyncio
import random
from typing import Dict, Tuple, Any
from rich.text import Text

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Footer, Header
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding
from textual import work, on

# Importações do ecossistema existente da aplicação
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
# Importamos o catálogo existente para aproveitar as cores de fundo dos terrenos
from app.views.map_manager_screen import CatalogoTiles


# ==============================================================================
# 1. MENSAGENS E COMPONENTES VISUAIS DA CAMADA DE EVENTOS
# ==============================================================================

class AtualizacaoCamadaEventos(Message):
    """Pacote de dados enviado pelo motor interno para atualizar as entidades no ecrã."""
    def __init__(self, estado_entidades: Dict[str, Dict[str, Any]]):
        super().__init__()
        self.estado_entidades = estado_entidades


class WidgetEntidade(Static):
    """Representação visual de um ator na camada de eventos (Jogador, Monstro, etc.)."""
    linha = reactive(0)
    coluna = reactive(0)
    emoji = reactive("")

    def watch_linha(self, _) -> None:
        self._atualizar_posicao_visual()

    def watch_coluna(self, _) -> None:
        self._atualizar_posicao_visual()

    def watch_emoji(self, novo_emoji: str) -> None:
        self.update(novo_emoji)

    def _atualizar_posicao_visual(self) -> None:
        """Sincroniza a coordenada matricial lógica com o offset visual do terminal."""
        # Multiplica a coluna por 2 para compensar a largura dos caracteres no terminal
        self.styles.offset = (self.coluna * 2, self.linha)


# ==============================================================================
# 2. ECRÄ PRINCIPAL DO JOGO (INTERAÇÃO E RENDERIZAÇÃO)
# ==============================================================================

class GamePlayScreen(Screen):
    """
    Ecrã de jogo que integra o mapa carregado da base de dados, desenha o fundo
    estático e processa as atualizações programáticas da camada de eventos.
    """

    CSS_PATH = "app/views/styles.css"

    BINDINGS = [
        Binding("w,up", "processar_movimento('cima')", "Mover Cima"),
        Binding("s,down", "processar_movimento('baixo')", "Mover Baixo"),
        Binding("a,left", "processar_movimento('esquerda')", "Mover Esquerda"),
        Binding("d,right", "processar_movimento('direita')", "Mover Direita"),
        Binding("q", "app.pop_screen", "Sair do Mapa")
    ]

    def __init__(self, mapa_id: int):
        super().__init__()
        self.mapa_id = mapa_id
        
        # Estruturas de dados do Cenário (Estático)
        self.matriz_terrenos = []
        self.camada_objetos: Dict[Tuple[int, int], str] = {}
        self.altura_mapa = 0
        self.largura_mapa = 0
        self.nome_mapa = ""
        
        # Estrutura do Motor Lógico (Estado Dinâmico da Camada de Eventos)
        self.motor_rodando = False
        self.estado_dinamico: Dict[str, Dict[str, Any]] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        # O contentor principal onde desenhamos o texto base do mapa
        yield Static(id="mapa-fundo")
        yield Footer()

    def on_mount(self) -> None:
        """Carrega os dados e inicializa os ciclos lógicos mal o ecrã é montado."""
        sucesso = self._carregar_mapa_da_base_de_dados()
        if not sucesso:
            self.notify("Erro: Não foi possível carregar o mapa especificado.", severity="error")
            self.app.pop_screen()
            return

        self._renderizar_camadas_estaticas()
        self._inicializar_camada_eventos()
        self.motor_rodando = True
        self.iniciar_motor_de_eventos()

    def _desempacotar_objetos(self, objetos_json: dict) -> Dict[Tuple[int, int], str]:
        """Converte as chaves de texto gravadas na BD de volta para tuplas lógicas."""
        objetos_memoria = {}
        if not objetos_json:
            return objetos_memoria
        for chave_texto, emoji in objetos_json.items():
            partes = chave_texto.split(",")
            objetos_memoria[(int(partes[0]), int(partes[1]))] = emoji
        return objetos_memoria

    def _carregar_mapa_da_base_de_dados(self) -> bool:
        """Abre uma sessão com a base de dados e extrai as camadas do mapa."""
        with SessionLocal() as db:
            mapa_db = db.query(MapaDB).filter(MapaDB.id == self.mapa_id).first()
            if not mapa_db or not mapa_db.mapa_em_si:
                return False

            self.nome_mapa = mapa_db.nome
            self.matriz_terrenos = mapa_db.mapa_em_si
            self.altura_mapa = len(self.matriz_terrenos)
            self.largura_mapa = len(self.matriz_terrenos[0]) if self.altura_mapa > 0 else 0
            
            # Desempacota a camada de objetos que atuará como obstáculo
            objetos_bd = mapa_db.objetos if mapa_db.objetos else {}
            self.camada_objetos = self._desempacotar_objetos(objetos_bd)
            return True

    def _renderizar_camadas_estaticas(self) -> None:
        """
        Mescla a camada de terrenos e a camada de objetos num único elemento Text
        de alta performance, aplicando as cores de fundo adequadas.
        """
        texto_mapa = Text(no_wrap=True)
        
        for l in range(self.altura_mapa):
            for c in range(self.largura_mapa):
                chao = self.matriz_terrenos[l][c]
                objeto = self.camada_objetos.get((l, c))
                
                if objeto is not None:
                    # Renderiza o objeto mantendo a cor de fundo do terreno subjacente
                    cor_bg = CatalogoTiles.obter_cor_fundo(chao)
                    estilo = f"on {cor_bg}" if cor_bg else ""
                    texto_mapa.append(objeto, style=estilo)
                else:
                    texto_mapa.append(chao)
            texto_mapa.append("\n")
            
        self.title = f"A Explorar: {self.nome_mapa}"
        self.query_one("#mapa-fundo", Static).update(texto_mapa)

    def _inicializar_camada_eventos(self) -> None:
        """Posiciona as entidades iniciais em coordenadas livres do mapa."""
        # Encontra coordenadas seguras para o jogador e para o monstro
        linha_j, col_j = self._obter_coordenada_livre()
        linha_m, col_m = self._obter_coordenada_livre()

        # Define o estado global da camada de eventos
        self.estado_dinamico = {
            "jogador": {"linha": linha_j, "coluna": col_j, "emoji": "🧙🏻‍♂️", "solido": True},
            "monstro_1": {"linha": linha_m, "coluna": col_m, "emoji": "👾", "solido": True}
        }
        mapa_container = self.query_one("#mapa-fundo", Static)
        
        # Injeta programaticamente os widgets correspondentes no ecrã
        for ent_id, dados in self.estado_dinamico.items():
            widget = WidgetEntidade(id=ent_id)
            widget.linha = dados["linha"]
            widget.coluna = dados["coluna"]
            widget.emoji = dados["emoji"]
            mapa_container.mount(widget)

    def _obter_coordenada_livre(self) -> Tuple[int, int]:
        """Procura uma coordenada que não contenha paredes lógicas nem objetos sólidos."""
        paredes_bloqueantes = ["🔳", "🧱", "🔲"]
        for _ in range(100):
            l = random.randint(1, self.altura_mapa - 2)
            c = random.randint(1, self.largura_mapa - 2)
            
            terreno_valido = self.matriz_terrenos[l][c] not in paredes_bloqueantes
            sem_objetos = (l, c) not in self.camada_objetos
            
            if terreno_valido and sem_objetos:
                return l, c
        return 2, 2 # Coordenada de salvaguarda

    # ==========================================================================
    # 3. MOTOR INTERNO DE EVENTOS E VERIFICAÇÃO DE COLISÕES
    # ==========================================================================

    def _posicao_valida_para_movimento(self, nova_linha: int, nova_coluna: int, id_ator: str) -> bool:
        """
        Garante que a entidade não sai do mapa, não colide com objetos da BD
        e não se sobrepõe a outras entidades dinâmicas.
        """
        # 1. Limites do mapa
        if not (0 <= nova_linha < self.altura_mapa and 0 <= nova_coluna < self.largura_mapa):
            return False

        # 2. Camada de Terrenos (Paredes fecham a passagem)
        tiles_bloqueantes = ["🔳", "🧱", "🔲"]
        if self.matriz_terrenos[nova_linha][nova_coluna] in tiles_bloqueantes:
            return False

        # 3. Camada de Objetos (Qualquer objeto estático atua como colisão sólida)
        if (nova_linha, nova_coluna) in self.camada_objetos:
            return False

        # 4. Camada de Eventos (Evita sobreposição entre monstros e jogador)
        for ent_id, dados in self.estado_dinamico.items():
            if ent_id != id_ator and dados.get("solido", True):
                if dados["linha"] == nova_linha and dados["coluna"] == nova_coluna:
                    return False

        return True

    def action_processar_movimento(self, direcao: str) -> None:
        """Capta a intenção do utilizador e solicita validação ao motor lógico."""
        jogador = self.estado_dinamico.get("jogador")
        if not jogador:
            return

        nl, nc = jogador["linha"], jogador["coluna"]
        if direcao == "cima": nl -= 1
        elif direcao == "baixo": nl += 1
        elif direcao == "esquerda": nc -= 1
        elif direcao == "direita": nc += 1

        if self._posicao_valida_para_movimento(nl, nc, "jogador"):
            jogador["linha"] = nl
            jogador["coluna"] = nc
            # Atualiza imediatamente o widget local do jogador
            self._sincronizar_widget("jogador", jogador)

    @work(thread=True)
    def iniciar_motor_de_eventos(self) -> None:
        """
        Processo independente que rege o mundo de jogo (IA dos monstros).
        Emite atualizações contínuas para o loop de eventos principal do Textual.
        """
        import time
        while self.motor_rodando:
            time.sleep(0.8)  # Ciclo de IA: o monstro move-se a cada 0.8 segundos
            
            monstro = self.estado_dinamico.get("monstro_1")
            if monstro:
                direcao = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                nl = monstro["linha"] + direcao[0]
                nc = monstro["coluna"] + direcao[1]

                # O motor central valida a física antes de aplicar o estado
                if self._posicao_valida_para_movimento(nl, nc, "monstro_1"):
                    monstro["linha"] = nl
                    monstro["coluna"] = nc
                    
                    # Envia a mensagem de forma thread-safe para atualizar a interface
                    self.post_message(AtualizacaoCamadaEventos(self.estado_dinamico))

    @on(AtualizacaoCamadaEventos)
    def ao_receber_atualizacao(self, pacote: AtualizacaoCamadaEventos) -> None:
        """Consome programaticamente as alterações de estado originadas pelo motor."""
        for ent_id, dados in pacote.estado_entidades.items():
            self._sincronizar_widget(ent_id, dados)

    def _sincronizar_widget(self, ent_id: str, dados: dict) -> None:
        """Procura o widget dinâmico correspondente e injeta os novos valores reativos."""
        try:
            widget = self.query_one(f"#{ent_id}", WidgetEntidade)
            widget.linha = dados["linha"]
            widget.coluna = dados["coluna"]
            widget.emoji = dados["emoji"]
        except Exception:
            # Se a entidade não existir na tela (ex: monstro invocado agora), cria e monta no mapa
            novo_widget = WidgetEntidade(id=ent_id)
            novo_widget.linha = dados["linha"]
            novo_widget.coluna = dados["coluna"]
            novo_widget.emoji = dados["emoji"]
            self.query_one("#mapa-fundo", Static).mount(novo_widget)

    def on_unmount(self) -> None:
        """Garante a terminação limpa da thread do motor ao encerrar o ecrã."""
        self.motor_rodando = False


# ==============================================================================
# INICIALIZADOR DE TESTE RÁPIDO
# ==============================================================================
if __name__ == "__main__":
    class JogoTesteApp(App):
        def on_mount(self) -> None:
            # Puxa o mapa com ID 1 (ou adapte para um ID existente na sua BD oficial)
            self.push_screen(GamePlayScreen(mapa_id=2))

    app = JogoTesteApp()
    app.run()