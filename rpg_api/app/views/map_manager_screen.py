# app/screens/map_manager_screen.py
import os
import copy
from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Tree, Static, Label, Button, Input, Select, Switch
from textual.widgets import TabbedContent, TabPane
from textual.containers import Horizontal, Vertical, Container
from textual.message import Message
from textual import on
from textual.events import MouseDown, MouseUp, MouseMove
from app.core.entities.mapas import GestorDeMapas
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.equipamentos_db import ItemDB
from app.core.entities.emojis import CatalogoTiles, padronizar_largura_tile, dict_item_emoji, dict_emoji_efeito, dict_emoji_racas
from rich.text import Text
from app.views.tools.painting_tools import balde_de_tinta
from app.views.components.evento_form_screen import PropriedadesEventoFormScreen
from app.db.database import SessionLocal
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
from typing import Literal

CSS_PATH = "styles/styles.css"

Pincel = Literal['lapis', 'balde', 'borracha', 'mira']
Modo_de_Captura = Literal['config_ini', None]
Tipo_da_Camada = Literal['terreno', 'objeto', 'evento']

class MapaInterativo(Static):
    """Componente customizado que exibe o mapa e captura movimentos contínuos do mouse."""
    
    
    class Pintar(Message):
        """Mensagem enviada continuamente enquanto o mouse é arrastado."""
        def __init__(self, linha: int, coluna: int, inicio_de_traco: bool = False):
            self.linha = linha
            self.coluna = coluna
            # Esta flag ajuda o sistema a saber quando tirar a "foto" para o Desfazer
            self.inicio_de_traco = inicio_de_traco 
            super().__init__()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse_pressionado = False   # O nosso "sensor" de clique
        self.capture_mouse()
        self.release_mouse()

    def on_mouse_down(self, event: MouseDown) -> None:
        """Apertou o botão do mouse: começa o traço e captura o foco."""
        self.mouse_pressionado = True
        self.capture_mouse() 
        self.post_message(self.Pintar(event.y, event.x // 2, inicio_de_traco=True))

    def on_mouse_up(self, event: MouseUp) -> None:
        """Soltou o botão do mouse: termina o traço e liberta o foco."""
        self.mouse_pressionado = False
        if self.has_focus or self.mouse_pressionado == False: 
            self.release_mouse()

    def on_mouse_move(self, event: MouseMove) -> None:
        """Moveu o mouse: se estiver apertado, continua a pintar."""
        if self.mouse_pressionado:
            self.post_message(self.Pintar(event.y, event.x // 2, inicio_de_traco=False))
            
                    

class MapManagerScreen(Screen):
    """
    Tela principal do Gerenciador de Mapas.
    Responsável por exibir as ferramentas de edição, a paleta e o mapa em si.
    """
    CSS_PATH = CSS_PATH 
    
    
    def __init__(self):
        self.matriz_do_mapa_atual: list|None = None
        self.objetos_do_mapa_atual: dict = {} # Vai guardar dados no formato: {(linha, coluna): "🪑"}
        self.eventos_do_mapa_atual: dict = {} # Formato: {(linha, coluna): {"id": int, "nome": str, "emoji": str, ...}
        self.id_do_mapa_selecionado: int|None = None
        self.tem_alteracoes: bool = False
        self.historico_desfazer: list = []
        self.historico_refazer: list = []
        self.tile_selecionado: str = "🟫"
        self.camada_do_tile: Tipo_da_Camada = 'terreno'
        self.ferramenta_atual: Pincel = "lapis"  # Exemplo de pincel ativo
        self.modo_captura_coordenada: bool = False
        self.contexto_do_modo_de_captura_ativo: Modo_de_Captura = None
        self.buffer_de_dados_do_formulario: dict = {}
        self.dados_do_mapa_atual: dict|None = None
        super().__init__()
        
    BINDINGS = [
        ("ctrl+z", "desfazer_acao", "Desfazer"),
        ("ctrl+y", "refazer_acao", "Refazer"),
        ("ctrl+s", "salvar_mapa_no_banco", "Salvar"),
        ("ctrl+b", "selecionar_balde", "Balde de Tinta"),
        ("b", "selecionar_lapis", "Lápis Comum"),
                                                    ]

    def action_selecionar_balde(self) -> None:
        self.ferramenta_atual = "balde"
        self.query_one("#btn-balde").focus
        self.notify("Ferramenta atual: Balde de Tinta 🪣")

    def action_selecionar_lapis(self) -> None:
        self.ferramenta_atual = "lapis"
        self.query_one("#btn-lapis").focus
        self.notify("Ferramenta atual: Lápis ✏️")
    
    def action_desfazer_acao(self):
        self.desfazer_acao()
        
    def action_refazer_acao(self):
        self.refazer_acao()
    
    def action_salvar_mapa_no_banco(self):
        self.salvar_mapa_no_banco()
        

    def compose(self) -> ComposeResult:
        # 1. Nossa Barra Superior (Removido o Header nativo para não haver conflitos)
        with Horizontal(id="top-menu", ):
            yield Button("Menu", id="btn-menu")
            yield Button("Novo", id="btn-novo", variant="primary")
            yield Button("Salvar", id="btn-salvar", variant="success")
            #yield Button("Editar", id="btn-editar")
            yield Button("Opções", id="btn-opcoes")
            yield Button("X", id="btn-fechar", variant="error")

        # 2. O Layout Principal (Esquerda e Direita)
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                
                # --- A PALETA CLICÁVEL ---
                with Container(id="paleta-container"):
                    yield Label("🎨 Paleta", classes="titulo-secao")
                    yield Label(f"Selecionado: {self.tile_selecionado}", id="lbl-tile-atual")
                    yield Button("Balde 🧺", id="btn-balde", classes="btn-pequeno")
                    yield Button("Lápis ✏", id="btn-lapis", classes="btn-pequeno")
                    
                    with Horizontal(id="ferramentas-hist"):
                        yield Button("↩ Desfazer", id="btn-desfazer", classes="btn-pequeno")
                        yield Button("↪ Refazer", id="btn-refazer", classes="btn-pequeno")
                        # NOVO: Borracha para apagar objetos
                        yield Button("❌ Borracha", id="btn-borracha", classes="btn-pequeno", variant="error")
                    
                    # 🪄 O NOVO SISTEMA DE ABAS!
                    with TabbedContent(id="tabs-paleta"):
                        # ABA 1: TERRENOS E PAREDES
                        with TabPane("🌍 Terrenos", id="tab-terrenos"):
                            with Container(classes="grade-paleta"): # Note que mudei id="grade-paleta" para classes="grade-paleta" no seu CSS depois
                                for i, tile in enumerate(CatalogoTiles.TERRENOS):
                                    yield Button(padronizar_largura_tile(tile), classes="btn-paleta", id=f"tile-terr-{i}")
                        
                        # ABA 2: OBJETOS SOLTOS
                        with TabPane("📦 Objetos", id="tab-objetos"):
                            with Container(classes="grade-paleta"):
                                for i, tile in enumerate(CatalogoTiles.OBJETOS):
                                    yield Button(padronizar_largura_tile(tile), classes="btn-paleta", id=f"tile-obj-{i}")
                                    
                        # ABA 3: FUTURA ABA DE EVENTOS
                        with TabPane("⚡ Eventos", id="tab-eventos"):
                            with Container(classes="grade-paleta"):
                                for i, tile in enumerate(CatalogoTiles.EVENTOS):
                                    yield Button(tile, classes="btn-paleta", id=f"tile-evt-{i}")
                    
                with Container(id="arvore-container"):
                    yield Label("📂 Mapas", classes="titulo-secao")
                    yield Tree("Mundo")

            with Container(id="map-area"):
                yield Label("Mapa: Mundo", id="mapa-titulo")
                yield MapaInterativo("Matriz do Mapa aparecerá aqui...", id="mapa-view")
        yield Footer()


    def on_mount(self):
        """Executa automaticamente quando o Gerenciador de Mapas abre."""
        self.carregar_arvore_de_mapas()


    def carregar_arvore_de_mapas(self):
        """Busca os mapas no banco e monta a estrutura de árvore visual."""
        tree = self.query_one(Tree)
        tree.clear() # Limpa a árvore atual
        tree.root.label = "Meus Mapas"
        tree.root.expand()
        
        from app.db.database import SessionLocal
        with SessionLocal() as db:
            try:
                todos_mapas: list = db.query(MapaDB).all()
            except:
                todos_mapas = []
                
        from collections import defaultdict
        filhos_de: dict = defaultdict(list)
        
        for mapa in todos_mapas:
            arvore_pai_id = mapa.mapa_pai_id
            
            if arvore_pai_id == 0 or arvore_pai_id == "" or str(arvore_pai_id).lower() == "none":
                arvore_pai_id = None
                
            filhos_de[arvore_pai_id].append(mapa)
            
        def adicionar_ramos(pai_id_db, no_da_arvore):
            for mapa in filhos_de[pai_id_db]:
                # Adicionamos o nome na interface, e escondemos o ID no 'data' do nó
                novo_no = no_da_arvore.add(mapa.nome, data=mapa.id)
                novo_no.expand() # Mantém a árvore aberta
                # Chama a si mesma para ver se este mapa também tem filhos
                adicionar_ramos(mapa.id, novo_no)
        
        adicionar_ramos(None, tree.root)
        
    @on(Tree.NodeSelected)
    def ao_clicar_na_arvore(self, event: Tree.NodeSelected):
        """Dispara quando o utilizador clica num mapa na barra lateral."""
        id_mapa_clicado = event.node.data
        if id_mapa_clicado is None:
            return # Clicou na palavra "Meus Mapas" (A raiz visual), ignoramos.

        if self.tem_alteracoes:
            # Tem coisas não salvas! Guarda o ID que ele tentou abrir e chama o aviso.
            self.id_do_mapa_selecionado = id_mapa_clicado
            self.app.push_screen(ConfirmacaoSalvarScreen(), self.ao_responder_aviso)
        else:
            # Caminho livre, carrega direto!
            self.carregar_mapa_do_banco(id_mapa_clicado)


    def ao_responder_aviso(self, resposta: str):
        """Trata a resposta do utilizador no modal de confirmação."""
        if resposta == "cancelar":
            self.id_do_mapa_selecionado = None
            return # Não faz nada, o utilizador desistiu de trocar de mapa
            
        elif resposta == "salvar":
            self.salvar_mapa_no_banco()
            self.carregar_mapa_do_banco(self.id_do_mapa_selecionado)
            
        elif resposta == "descartar":
            self.tem_alteracoes = False # Esquece a sujeira
            self.carregar_mapa_do_banco(self.id_do_mapa_selecionado)


    def carregar_mapa_do_banco(self, mapa_id: int):
        from app.db.database import SessionLocal
        
        with SessionLocal() as db:
            # 1. Carrega o Mapa Base
            mapa_db_carregado = db.query(MapaDB).filter(MapaDB.id == mapa_id).first()
            if not mapa_db_carregado:
                return

            self.matriz_do_mapa_atual = mapa_db_carregado.mapa_em_si
            
            objetos_salvos = mapa_db_carregado.objetos if mapa_db_carregado.objetos else {}
            self.objetos_do_mapa_atual = self._desempacotar_objetos_do_banco(objetos_salvos)

            # ✅ NOVO: 2. Carrega os Eventos Relacionados
            eventos_db = db.query(EventoDB).filter(EventoDB.mapa_id == mapa_id).all()
            
            # Converte os objetos do SQLAlchemy de volta para uma lista de dicionários
            lista_eventos_para_memoria = []
            for evt in eventos_db:
                lista_eventos_para_memoria.append({
                    "id": evt.id,
                    "nome": evt.nome,
                    "emoji": evt.emoji,
                    "pos_y": evt.pos_y,
                    "pos_x": evt.pos_x,
                    "event_type": evt.event_type,
                    "parametros": evt.parametros if evt.parametros else {}
                })
            
            # Envia para a nossa função que já testámos com o Pytest!
            self._desempacotar_eventos_do_banco(lista_eventos_para_memoria)

            # 3. Atualiza os metadados da memória
            configs_salvas = mapa_db_carregado.configs if mapa_db_carregado.configs else {}
            self.dados_do_mapa_atual = {
                "id": mapa_db_carregado.id,
                "nome": mapa_db_carregado.nome,
                "tipo": mapa_db_carregado.tipo,
                "mapa_pai_id": mapa_db_carregado.mapa_pai_id,
                "largura": mapa_db_carregado.largura,
                "altura": mapa_db_carregado.altura,
                "configs": configs_salvas
            }
            
            self.tem_alteracoes = False
            self.id_do_mapa_selecionado = None
            
            # Desenha tudo na tela (Chão + Objetos + Eventos)
            try:
                self.exibir_mapa_na_tela()
            except Exception as e:
                raise(f"Erro ao exibir o mapa ao carregar: {e} ")
            self.notify(
                f"Mapa '{mapa_db_carregado.nome}' e eventos carregados!")

    
    def salvar_estado_historico(self):
        """Tira uma fotografia à matriz atual antes de a alterarmos."""
        # Limitamos o histórico a 10 passos para não consumir muita RAM
        if len(self.historico_desfazer) > 10:
            self.historico_desfazer.pop(0)
            
        snapshot = {
            "matriz": copy.deepcopy(self.matriz_do_mapa_atual),
            "objetos": copy.deepcopy(self.objetos_do_mapa_atual)
        }
        
        self.historico_desfazer.append(snapshot)
        self.historico_refazer.clear()


    @on(MapaInterativo.Pintar)
    def processar_pintura(self, event: MapaInterativo.Pintar):
        if self.matriz_do_mapa_atual is None:
            return
        linha, coluna = event.linha, event.coluna
        
        # Validação de Limites da Matriz
        if 0 <= linha < len(self.matriz_do_mapa_atual) and 0 <= coluna < len(self.matriz_do_mapa_atual[0]):
            if event.inicio_de_traco:
                self.salvar_estado_historico()
            
            # =========================================================================
            # FERRAMENTA BORRACHA / TERRENO / OBJETO (Seu código padrão bloco a bloco)
            # =========================================================================
            if self.ferramenta_atual == "borracha":
                if (linha, coluna) in self.objetos_do_mapa_atual:
                    del self.objetos_do_mapa_atual[(linha, coluna)]
                if (linha, coluna) in self.eventos_do_mapa_atual:
                    del self.eventos_do_mapa_atual[(linha, coluna)]
                    
            # =========================================================================
            # FERRAMENTA MODO CAPTURADOR DE COORDENADA
            # =========================================================================
            if self.modo_captura_coordenada or self.ferramenta_atual == "mira":
                logging.info(f"Modo de captura: coords: (x={coluna}, y={linha})")
                
                if event.inicio_de_traco:
                    self.query_one(
                        "#mapa-view", MapaInterativo).mouse_pressionado = False
                    self.modo_captura_coordenada = False
                    self.ferramenta_atual = "lapis"

                    # Passa o contexto ativo para a reabertura do formulário
                    try:
                        self._reabrir_formulario_enviando_coordenadas(
                            linha, coluna, self.contexto_do_modo_de_captura_ativo)
                    except Exception as e:
                        logging.info(f"Erro ao _reabrir_formulario_enviando_coordenadas: {e}")
                        raise ValueError(
                            f"Erro ao _reabrir_formulario_enviando_coordenadas: {e}")
                
                return
            
            # =========================================================================
            # FERRAMENTA BALDE DE TINTA
            # =========================================================================
            #TODO: A ferramenta balde não está preenchedo o fundo em caso de objetos
            if self.ferramenta_atual == "balde":
                # Executa APENAS no primeiro clique, ignorando o arrasto do mouse
                if event.inicio_de_traco:
                    # Desliga o sensor de clique contínuo para evitar reprocessamentos
                    self.query_one(
                        "#mapa-view", MapaInterativo).mouse_pressionado = False

                    # Dispara o algoritmo de Flood Fill iterativo
                    try:
                        balde_de_tinta(self.matriz_do_mapa_atual,
                            linha, coluna, self.tile_selecionado)
                    except Exception as e:
                        raise(f"Erro ao aplicar balde_de_tinta: {e}")
                    
                    # Atualiza o estado de modificação e renderiza a tela
                    self.tem_alteracoes = True
                    self.exibir_mapa_na_tela()
                return  

            
            # =========================================================================
            # FERRAMENTA LÁPIS 
            # =========================================================================
            if self.ferramenta_atual == "lapis":
                
                #tipo_pincel = CatalogoTiles.obter_tipo(self.tile_selecionado) 
                
                # =========================================================================
                # TRATAMENTO EXCLUSIVO PARA EVENTOS (Inalterado)
                # =========================================================================
                # TODO: Aqui ocorre o erro de confundir objetos por eventos, o .obter_tipo não sabe mais diferenciar já que a emojis iguais nos dois tipos.

                if self.camada_do_tile == "terreno":
                    if self.matriz_do_mapa_atual[linha][coluna] != self.tile_selecionado:
                        self.matriz_do_mapa_atual[linha][coluna] = self.tile_selecionado
                
                elif self.camada_do_tile == "evento":
                    if self.ferramenta_atual == 'balde':
                        self.ferramenta_atual = 'lapis'
                        
                    if event.inicio_de_traco:
                        self.query_one(
                            "#mapa-view", MapaInterativo).mouse_pressionado = False
                        evento_atual = self.eventos_do_mapa_atual.get((linha, coluna))
                        try:
                            self.app.push_screen(
                                PropriedadesEventoFormScreen(
                                    linha, coluna, self.tile_selecionado, evento_atual),
                                lambda dados: self.ao_terminar_configurar_evento(
                                    linha, coluna, dados)
                            )
                        except Exception as e:
                            raise(f"Erro em lançar o form de evento na pintura de evento: {e} ")
                        
                        self.salvar_estado_historico()
                    return
                
                else:
                    self.objetos_do_mapa_atual[(linha, coluna)
                                            ] = self.tile_selecionado

            self.tem_alteracoes = True
            self.exibir_mapa_na_tela()
  
    

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques na tela principal."""
        if event.button.id == "btn-fechar":
            self.dismiss()
        elif event.button.id == "btn-novo":
            self.app.push_screen(NovoMapaFormScreen(), self.ao_terminar_form_de_novo_mapa)
            
        elif event.button.id == "btn-salvar":
            self.salvar_mapa_no_banco()
        elif event.button.id == "btn-desfazer":
            self.desfazer_acao()
        elif event.button.id == "btn-refazer":
            self.refazer_acao()
        elif event.button.id == "btn-balde":
            self.action_selecionar_balde()
        elif event.button.id == "btn-lapis":
            self.action_selecionar_lapis()
        # (Junto aos botões desfazer/refazer)
        elif event.button.id == "btn-borracha":
            self.ferramenta_atual = "borracha"
            self.query_one("#lbl-tile-atual", Label).update("Selecionado: ❌ Borracha")
        
        if event.button.has_class("btn-paleta"):
            # ✅ DEPOIS: Passamos o texto do botão pelo nosso padronizador!
            tile_bruto = str(event.button.label)
            self.tile_selecionado = padronizar_largura_tile(tile_bruto)
            logging.info(f"btn:: {event.button.id}")
            self.query_one("#lbl-tile-atual", Label).update(f"Selecionado: {self.tile_selecionado}")
            return
            
        elif event.button.id == "btn-opcoes":
            if self.dados_do_mapa_atual is None:
                self.notify("Crie ou carregue um mapa primeiro!", severity="warning")
                return
            try:
                self.app.push_screen(
                    PropriedadesFormScreen(self.dados_do_mapa_atual), 
                    self.ao_terminar_propriedades)
            except Exception as e:
                logging.info(f"Erro ao lançar Form de Propriedades pelo botão: {e}")
                
        elif event.button.id == "btn-menu":
            # Abre o menu flutuante!
            self.app.push_screen(MenuAcoesScreen(), self.ao_escolher_acao_menu)

    @on(TabbedContent.TabActivated)
    def on_tab_pane_enabled(self, event: TabbedContent.TabActivated):
        logging.info(f"tab: {event.pane.id  }")
        aba_ativa_id = event.pane.id

        if aba_ativa_id == 'tab-terrenos':
            logging.info(f"tab: {aba_ativa_id}")
            self.camada_do_tile = 'terreno'
            if self.dados_do_mapa_atual:
                self.tile_selecionado = self.dados_do_mapa_atual.get(
                    'configs').get('tile_chao', "🟫")
            
        elif aba_ativa_id == 'tab-eventos':
            logging.info(f"tab: {aba_ativa_id}")
            self.camada_do_tile = 'evento'
            self.action_selecionar_lapis()
            
        else:
            logging.info(f"tab: {aba_ativa_id}")
            self.camada_do_tile = 'objeto'
            

    def ao_terminar_form_de_novo_mapa(self, dados_recebidos_do_form_novo_mapa: dict | None):
        """Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form."""
        if dados_recebidos_do_form_novo_mapa is None:
            return 
        
        self.dados_do_mapa_atual = dados_recebidos_do_form_novo_mapa
        self.objetos_do_mapa_atual.clear()
        
        # 2. PREPARAÇÃO DOS DADOS: Juntamos os tiles e as configurações num único pacote
        configs_completas = dados_recebidos_do_form_novo_mapa.get("configs", {})
        configs_completas["tile_parede"] = dados_recebidos_do_form_novo_mapa.get("tile_parede", "🔲")
        configs_completas["tile_chao"] = dados_recebidos_do_form_novo_mapa.get("tile_chao", "  ")
        
        try:
            # 3. Chama a lógica pura (O nosso core de geração) e injeta os dados reais
            self.matriz_do_mapa_atual = GestorDeMapas.gerar_mapa_rpg(
                tipo=dados_recebidos_do_form_novo_mapa["tipo"],
                largura=dados_recebidos_do_form_novo_mapa["largura"],
                altura=dados_recebidos_do_form_novo_mapa["altura"],
                configs=configs_completas 
            )
        except Exception as e:
            raise (f"Erro no processo de Gerar mapa pelo GestorDeMapas: {e}")
        
        # 4. Exibe o mapa na tela e avisa o utilizador!
        self.exibir_mapa_na_tela()
        self.notify(f"Mapa '{dados_recebidos_do_form_novo_mapa['nome']}' gerado com as novas regras!")
        
        
    def ao_terminar_propriedades(self, dados_de_propridades_alteradas: dict | None):
        """Callback acionado ao fechar a tela de Propriedades."""
        if dados_de_propridades_alteradas is None:
            return 
        
        logging.info(
            f"dados_de_propridades_alteradas: {dados_de_propridades_alteradas}")
        
        if dados_de_propridades_alteradas.get("acao_especial") == "ativar_capitura_de_posicao":
            self.modo_captura_coordenada = True
            self.ferramenta_atual = "mira"

            # 🌟 Registra o identificador do campo para a resposta saber onde se injetar
            self.contexto_do_modo_de_captura_ativo = dados_de_propridades_alteradas.get("id_alvo", 'config_ini')
            self.buffer_de_dados_do_formulario = dados_de_propridades_alteradas.get(
                "estado_formulario_atual", {})


        # Atualiza a memória com os novos dados
        self.dados_do_mapa_atual["nome"] = dados_de_propridades_alteradas["nome"]
        self.dados_do_mapa_atual["mapa_pai_id"] = dados_de_propridades_alteradas["mapa_pai_id"]
        if "coordenadas_iniciais" in dados_de_propridades_alteradas:
            self.dados_do_mapa_atual["configs"]["coordenadas_iniciais"] =  dados_de_propridades_alteradas["coordenadas_iniciais"]
        
        
        self.tem_alteracoes = True
        # Atualiza o título na tela
                
        self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.dados_do_mapa_atual['nome']}")
        self.notify("Propriedades atualizadas na memória! Lembre-se de Salvar.")
        
    
    def desfazer_acao(self):
        """Retrocede a matriz para o último estado guardado."""
        if not self.historico_desfazer:
            self.notify("Não há mais ações para desfazer!", severity="warning")
            return
            
        # 1. Guarda a foto atual no "Refazer" caso nos arrependamos do Desfazer
        snapshot_atual = {
            "matriz": copy.deepcopy(self.matriz_do_mapa_atual),
            "objetos": copy.deepcopy(self.objetos_do_mapa_atual)
        }
        self.historico_refazer.append(snapshot_atual)
        
        # 2. Puxa o snapshot do passado e restaura as duas camadas
        snapshot_passado = self.historico_desfazer.pop()
        self.matriz_do_mapa_atual = snapshot_passado["matriz"]
        self.objetos_do_mapa_atual = snapshot_passado["objetos"]
        
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()
        
        
    def ao_terminar_configurar_evento(self, linha: int, coluna: int, dados_evento: dict | None):
        """Callback acionado quando o usuário confirma os dados do evento no Modal."""
        if dados_evento is None:
            return # Usuário clicou em Cancelar, nada é alterado

        if dados_evento.get("acao_especial") == "ativar_capitura_de_posicao":
            self.modo_captura_coordenada = True
            self.ferramenta_atual = "mira"
                        
            # 🌟 Registra o identificador do campo para a resposta saber onde se injetar
            self.contexto_do_modo_de_captura_ativo = dados_evento.get("id_alvo")
            self.buffer_de_dados_do_formulario = dados_evento.get(
                "estado_formulario_atual", {})
            self.notify(
                f"Modo Mira Ativo: Selecione a coordenada para o campo [{self.contexto_do_modo_de_captura_ativo}]! 🎯")
            return
        
        # Usa a nossa função estruturada (que validamos no teste TDD anterior!)
        self.adicionar_evento_para_memoria(
            linha=linha,
            coluna=coluna,
            nome=dados_evento["nome"],
            emoji=dados_evento["emoji"],
            event_type=dados_evento["event_type"],
            parametros=dados_evento["parametros"],
            evento_id=dados_evento.get("id")
        )
        
        # Garante que o histórico do Desfazer registrou essa mudança
        self.salvar_estado_historico()
        
        # Atualiza o display e renderiza o novo emoji de evento por cima do mapa
        self.exibir_mapa_na_tela()
        self.notify(f"Evento '{dados_evento['nome']}' instanciado com sucesso!")
        
        
        
    def _reabrir_formulario_enviando_coordenadas(self, linha_coletada: int, coluna_coletada: int, id_alvo: str):
        """Monta o formulário de volta injetando a nova coordenada no escopo correto."""
        
        dados_para_reenvio_de_propriedades = self.dados_do_mapa_atual
        
        #dados_para_reenvio_de_propriedades['nome'] = self.dados_do_mapa_atual.get("nome"),
        dados_para_reenvio_de_propriedades ['mapa_pai_id']= self.dados_do_mapa_atual.get(
            'mapa_pai_id', None)
        
        dados_atuais = dict(
            coordenadas_iniciais=str(str(linha_coletada)+','+str(coluna_coletada)), 
            switch_coord_ini=True,
            )
        
        for key , value in dados_atuais.items():
            dados_para_reenvio_de_propriedades['configs'][key] = value
            
            
        if id_alvo == 'config_ini':
            form_screen = PropriedadesFormScreen(dados_para_reenvio_de_propriedades
            )
            self.app.push_screen(
                    form_screen,
                lambda dados_para_reenvio_de_propriedades: self.ao_terminar_propriedades(dados_para_reenvio_de_propriedades)
                )
        
        else:
            form_screen = PropriedadesEventoFormScreen(
                linha=linha_coletada, 
                coluna=coluna_coletada,
                tile=self.tile_selecionado,
                evento_atual=self.eventos_do_mapa_atual.get((linha_coletada, coluna_coletada))
            )
            # 🌟 Restaura a memória do formulário e passa a coordenada mapeada ao alvo correspondente
            form_screen.restaurar_valores_dos_campos(
                dados=self.buffer_de_dados_do_formulario, 
                linha_coletada=linha_coletada, 
                coluna_coletada=coluna_coletada,
                id_alvo=id_alvo
            )
            self.app.push_screen(
                form_screen,
                lambda dados: self.ao_terminar_configurar_evento(linha_coletada, coluna_coletada, dados)
            )
        
        # Limpa as flags e buffers de contexto
        self.buffer_de_dados_do_formulario = {}
        self.contexto_do_modo_de_captura_ativo = None
        
        


    def refazer_acao(self):
        """Avança Terrenos e Objetos para o estado do futuro."""
        if not self.historico_refazer:
            self.notify("Não há ações para refazer!", severity="warning")
            return

        # 1. Guarda o estado atual no Desfazer
        snapshot_atual = {
            "matriz": copy.deepcopy(self.matriz_do_mapa_atual),
            "objetos": copy.deepcopy(self.objetos_do_mapa_atual)
        }
        self.historico_desfazer.append(snapshot_atual)
        
        # 2. Puxa o snapshot do futuro e restaura
        snapshot_futuro = self.historico_refazer.pop()
        self.matriz_do_mapa_atual = snapshot_futuro["matriz"]
        self.objetos_do_mapa_atual = snapshot_futuro["objetos"]
        
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()

    def exibir_mapa_na_tela(self):
        """Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)."""
        if self.matriz_do_mapa_atual is None: return
        
        texto_mapa = Text(no_wrap=True)
        
        for linha_idx in range(len(self.matriz_do_mapa_atual)):
            for col_idx in range(len(self.matriz_do_mapa_atual[0])):
                
                # 1. Pega o terreno base da matriz
                tile_chao = self.matriz_do_mapa_atual[linha_idx][col_idx]
                # 2. Verifica se existe um objeto nesta coordenada
                tile_objeto = self.objetos_do_mapa_atual.get((linha_idx, col_idx))
                # ✅ NOVO: Verifica primeiro se há um evento lógico nesta coordenada
                dados_evento = self.eventos_do_mapa_atual.get((linha_idx, col_idx))
                
                # 3. Lógica de Renderização
                if dados_evento is not None:
                    # Desenha o Emoji do Evento (ex: 👾) com o background do chão correto
                    cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                    texto_mapa.append(dados_evento["emoji"], style=f"on {cor_bg}" if cor_bg else "")
                elif tile_objeto is not None:
                    # Desenha o objeto estático (cenário)
                    cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                    texto_mapa.append(tile_objeto, style=f"on {cor_bg}" if cor_bg else "")
                else:
                    # Desenha chão limpo
                    texto_mapa.append(tile_chao)
            
            # Quebra de linha no fim de cada linha da grelha
            texto_mapa.append("\n")
        
        self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.dados_do_mapa_atual['nome']}")
        self.query_one("#mapa-view", MapaInterativo).update(texto_mapa)
        

    def salvar_mapa_no_banco(self):
        """Salva o mapa atual, os objetos estáticos e os eventos dinâmicos no banco de dados."""
        from app.db.database import SessionLocal # Ajuste o import conforme o seu projeto
        
        mapa_id_atual = self.dados_do_mapa_atual.get("id") if self.dados_do_mapa_atual else None
        nome_mapa = self.dados_do_mapa_atual.get("nome") if self.dados_do_mapa_atual else None
        try:
            with SessionLocal() as db:
                # ==========================================
                # 1. SALVAR O MAPA BASE E OBJETOS (CENÁRIO)
                # ==========================================
                if mapa_id_atual is not None:
                    # MODO UPDATE
                    mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id_atual).first()
                    mapa_db.nome = nome_mapa
                    mapa_db.tipo = self.dados_do_mapa_atual.get("tipo")
                    mapa_db.mapa_pai_id = self.dados_do_mapa_atual.get("mapa_pai_id")
                    mapa_db.largura = self.dados_do_mapa_atual.get("largura")
                    mapa_db.altura = self.dados_do_mapa_atual.get("altura")
                    mapa_db.mapa_em_si = self.matriz_do_mapa_atual 
                    mapa_db.configs = self.dados_do_mapa_atual.get("configs", {})
                    mapa_db.objetos = self._empacotar_objetos_para_banco()
                    
                    acao_realizada = "atualizado"
                else:
                    # MODO INSERT
                    mapa_db = MapaDB(
                        nome=nome_mapa,
                        tipo=self.dados_do_mapa_atual.get("tipo"),
                        mapa_pai_id=self.dados_do_mapa_atual.get("mapa_pai_id"),
                        largura=self.dados_do_mapa_atual.get("largura"),
                        altura=self.dados_do_mapa_atual.get("altura"),
                        mapa_em_si=self.matriz_do_mapa_atual,
                        configs=self.dados_do_mapa_atual.get("configs", {}), 
                        objetos=self._empacotar_objetos_para_banco() 
                    )
                    db.add(mapa_db)
                    db.flush() # Força a geração do ID do mapa novo antes do commit
                    acao_realizada = "criado"

                # ==========================================
                # 2. SINCRONIZAR A CAMADA DE EVENTOS
                # ==========================================
                # Limpa os eventos antigos deste mapa para evitar duplicados ou fantasmas
                db.query(EventoDB).filter(EventoDB.mapa_id == mapa_db.id).delete()
                
                # Desempacota a memória e insere os novos registos
                lista_eventos = self._empacotar_eventos_para_banco()
                for dados_evt in lista_eventos:
                    novo_evento_db = EventoDB(
                        mapa_id=mapa_db.id,
                        nome=dados_evt["nome"],
                        emoji=dados_evt["emoji"],
                        pos_y=dados_evt["pos_y"],
                        pos_x=dados_evt["pos_x"],
                        event_type=dados_evt["event_type"],
                        parametros=dados_evt.get("parametros", {})
                    )
                    db.add(novo_evento_db)

                # ==========================================
                # 3. CONSOLIDAR TUDO
                # ==========================================
                db.commit()
                
                # Atualiza a memória com o novo ID (caso tenha sido um INSERT)
                self.dados_do_mapa_atual["id"] = mapa_db.id 
                self.tem_alteracoes = False
                
                self.notify(f"Mapa '{nome_mapa}' e seus eventos foram guardados com sucesso!", severity="success")

        except Exception as e:
            self.notify(f"Erro ao salvar no banco: {e}", severity="error")
    
    
    def ao_escolher_acao_menu(self, acao: str | None):
        """Callback após o utilizador clicar em algo no Menu Principal."""
        if acao is None: return
        
        if acao == "exportar" and self.matriz_do_mapa_atual is None:
            self.notify("Não há nenhum mapa carregado para exportar!", severity="warning")
            return
            
        # Pede o nome do ficheiro para a ação escolhida
        self.app.push_screen(ArquivoCSVScreen(acao), lambda nome_arq: self.processar_csv(acao, nome_arq))

    def processar_csv(self, acao: str, nome_arquivo: str | None):
        """Redireciona para importar ou exportar com base no nome do ficheiro."""
        if nome_arquivo is None: return # Utilizador cancelou
        
        if acao == "exportar":
            self.exportar_para_csv(nome_arquivo)
        elif acao == "importar":
            self.importar_de_csv(nome_arquivo)

    def exportar_para_csv(self, nome_arquivo: str):
        """Transforma a matriz atual em texto com vírgulas e guarda no disco."""
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                for linha in self.matriz_do_mapa_atual:
                    # Junta os elementos da linha com uma vírgula e adiciona quebra de linha
                    linha_csv = ",".join(linha)
                    f.write(linha_csv + "\n")
            
            self.notify(f"Mapa exportado com sucesso para '{nome_arquivo}'!", severity="success")
        except Exception as e:
            self.notify(f"Erro ao exportar: {e}", severity="error")

    def importar_de_csv(self, nome_arquivo: str):
        """Lê um ficheiro CSV do disco e transforma numa matriz para o nosso programa."""
        if not os.path.exists(nome_arquivo):
            self.notify(f"O ficheiro '{nome_arquivo}' não foi encontrado!", severity="error")
            return
            
        try:
            nova_matriz = []
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip() # Remove quebras de linha e espaços no final
                    if linha: # Ignora linhas vazias
                        # Separa pela vírgula para recriar a lista
                        elementos = linha.split(",")
                        nova_matriz.append(elementos)
            
            # Carrega a matriz para a memória do programa
            self.matriz_do_mapa_atual = nova_matriz
            
            # Atualiza os dados de controlo para fingir que é um mapa novo (ainda não salvo no banco)
            self.dados_do_mapa_atual = {
                "nome": nome_arquivo.replace(".csv", ""),
                "tipo": "importado",
                "largura": len(nova_matriz[0]) if nova_matriz else 0,
                "altura": len(nova_matriz),
                "mapa_pai_id": None
            }
            
            # Limpa o histórico e marca como alterado (para o utilizador ter de o salvar no banco depois)
            self.historico_desfazer.clear()
            self.historico_refazer.clear()
            self.tem_alteracoes = True
            
            self.exibir_mapa_na_tela()
            self.notify(f"Mapa importado de '{nome_arquivo}'!", severity="success")
            
        except Exception as e:
            self.notify(f"Erro ao importar: {e}", severity="error")
            
    
    # ==========================================
    # UTILITÁRIOS DE SERIALIZAÇÃO DE OBJETOS
    # ==========================================
    def _empacotar_objetos_para_banco(self) -> dict:
        """Transforma as chaves de tupla (1, 2) em texto '1,2' para poder salvar no Banco."""
        objetos_formatados = {}
        try:
            for (linha, coluna), emoji in self.objetos_do_mapa_atual.items():
                chave_texto = f"{linha},{coluna}"
                objetos_formatados[chave_texto] = emoji
        except Exception as e:
            logging.info(f"Erro ao _empacotar_objetos_para_banco: {e}")
            raise ValueError(f"Erro ao _empacotar_objetos_para_banco: {e}")
        return objetos_formatados

    def _desempacotar_objetos_do_banco(self, objetos_json: dict) -> dict:
        """Transforma o texto '1,2' do Banco de volta em tupla matemática (1, 2)."""
        objetos_na_memoria = {}
        if not objetos_json:
            return objetos_na_memoria  # Retorna vazio se não houver objetos

        try:
            for chave_texto, emoji in objetos_json.items():
                partes = chave_texto.split(",")
                linha = int(partes[0])
                coluna = int(partes[1])
                objetos_na_memoria[(linha, coluna)] = emoji
        except Exception as e:
            logging.info(f"Erro ao _desempacotar_objetos_do_banco: {e}")
            raise ValueError(f"Erro ao _desempacotar_objetos_do_banco: {e}")
        return objetos_na_memoria

    # ==========================================
    # MANIPULAÇÃO E SERIALIZAÇÃO DE EVENTOS
    # ==========================================
    def adicionar_evento_para_memoria(self, linha: int, coluna: int, nome: str,
                                      emoji: str, event_type: str, parametros: dict, evento_id: int = None) -> None:
        """Regista ou atualiza um evento numa coordenada específica."""
        dados_evento = {
            "nome": nome,
            "emoji": emoji,
            "event_type": event_type,
            "parametros": parametros
        }

        if evento_id is not None:
            # Só adicionamos o ID se ele vier do banco de dados (para fins de UPDATE futuro)
            dados_evento["id"] = evento_id

        self.eventos_do_mapa_atual[(linha, coluna)] = dados_evento
        self.tem_alteracoes = True

    def _empacotar_eventos_para_banco(self) -> list[dict]:
        """Transforma o dicionário de memória numa lista pronta para o SQLAlchemy."""
        lista_eventos = []
        try:
            for (linha, coluna), dados in self.eventos_do_mapa_atual.items():
                # Cria uma cópia para não alterar a memória original
                registo = dados.copy()
                registo["pos_y"] = linha
                registo["pos_x"] = coluna
                lista_eventos.append(registo)
        except Exception as e:
            logging.info(f"Erro ao _empacotar_eventos_para_banco: {e}")
            raise ValueError(f"Erro ao _empacotar_eventos_para_banco: {e}")
        return lista_eventos

    def _desempacotar_eventos_do_banco(self, lista_eventos_db: list[dict]):
        """Povoa a memória a partir da lista de eventos vindos do banco de dados."""
        self.eventos_do_mapa_atual.clear()  # Limpa a memória atual

        if not lista_eventos_db:
            return
        try:
            for evento in lista_eventos_db:
                linha = evento["pos_y"]
                coluna = evento["pos_x"]

                self.adicionar_evento_para_memoria(
                    linha=linha,
                    coluna=coluna,
                    nome=evento["nome"],
                    emoji=evento["emoji"],
                    event_type=evento["event_type"],
                    parametros=evento["parametros"],
                    evento_id=evento.get("id"))
        except Exception as e:
            logging.info(f"Erro ao _desempacotar_eventos_do_banco: {e}")
            raise ValueError(f"Erro ao _desempacotar_eventos_do_banco: {e}")




class NovoMapaFormScreen(ModalScreen[dict]):
    """
    Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.
    Retorna um dicionário com os dados preenchidos quando fechada.
    """
    CSS_PATH =  CSS_PATH

    def compose(self):
        with Vertical(id="form-caixa"):
            yield Label("✨ Gerar Novo Mapa", classes="titulo-secao")
            
            # --- CAMPOS GERAIS (Sempre visíveis) ---
            yield Input(placeholder="Nome do Mapa", id="input-nome")
            yield Select([], prompt="Mapa Pai (Opcional)", id="select-pai")
            yield Select((("Em branco", "Em branco") , ("Masmorra", "masmorra"), ("Vila", "vila"), ("Caverna", "caverna")), prompt="Tipo de Mapa", id="select-tipo", value="caverna")
            with Horizontal(classes="linha-dupla"):
                yield Input(placeholder="Largura (ex: 40)", id="input-largura")
                yield Input(placeholder="Altura (ex: 20)", id="input-altura")
                
            with Horizontal(classes="linha-dupla"):
                #yield Input(placeholder="Tile Parede", id="input-tile-parede", value="🔲")
                yield Select([("🔲", "🔲"), ("🧱", "🧱"), ("🌳", "🌳") , ("🟦", "🟦")], prompt="Tile Parede", id="input-tile-parede", value="🔲")
                yield Select([("  ", "  "), ("🟦", "🟦"), ("🟩", "🟩"), ("⬛", "⬛"), ("🟫", "🟫")], prompt="Tile Chão", id="input-tile-chao", value="  " )
                #yield Input(placeholder="Tile Chão", id="input-tile-chao", value="  ")
            # --- CAIXAS DE CONFIGURAÇÃO ESPECÍFICAS ---
            
            # 1. Configurações de Masmorra
            with Vertical(id="configs-masmorra", classes="caixa-config"):
                yield Label("⚙️ Configurações da Masmorra")
                yield Input(placeholder="Máx de Salas", id="input-max-salas", value="25")
                with Horizontal(classes="linha-dupla"):
                    yield Input(placeholder="Tam. Mínimo Sala", id="input-tam-min", value="3")
                    yield Input(placeholder="Tam. Máximo Sala", id="input-tam-max", value="15")
                    
            # 2. Configurações de Cavernas
            with Vertical(id="configs-caverna", classes="caixa-config"):
                yield Label("⚙️ Configurações da Caverna")
                yield Input(placeholder="Taxa de Preenchimento %", id="input-taxa-caverna", value="55")
                yield Input(placeholder="Iterações de Suavização", id="input-iteracoes", value="3")  

            # 3. Configurações de Vila (Inicialmente oculta)
            with Vertical(id="configs-vila", classes="caixa-config"):
                yield Label("⚙️ Configurações da Vila")
                yield Input(placeholder="Máx de Casas", id="input-max-casas", value="20")
                with Horizontal(classes="linha-dupla"):
                    yield Input(placeholder="Tam. Mínimo Casa", id="input-tam-min", value="4")
                    yield Input(placeholder="Tam. Máximo Casa", id="input-tam-max", value="10")
                #yield Input(placeholder="Taxa de Preenchimento %", id="input-taxa-vila", value="45")
                # Futuramente você pode adicionar mais configurações de vila aqui

            # --- BOTÕES DE AÇÃO ---
            with Horizontal(id="form-botoes"):
                yield Button("Cancelar", id="btn-cancelar", variant="error")
                yield Button("Gerar", id="btn-gerar", variant="success")

    def on_mount(self):
        """Executado quando a tela é carregada. Garante que apenas a caixa certa está visível."""
        self.atualizar_visibilidade_configs("masmorra")
        self.carregar_mapas_pai()
        
    def carregar_mapas_pai(self):
        """Busca os mapas no banco de dados e preenche o menu de seleção."""
        with SessionLocal() as db:
            try:
                mapas = db.query(MapaDB).all()
            except:
                mapas = []
            opcoes = [("Nenhum (Raiz)", 0)] + [(m.nome, m.id) for m in mapas]
            self.query_one("#select-pai", Select).set_options(opcoes)

    @on(Select.Changed, "#select-tipo")
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.value != Select.BLANK:
            self.atualizar_visibilidade_configs(str(event.value))

    def atualizar_visibilidade_configs(self, tipo_selecionado: str):
        """Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado."""
        self.query_one("#configs-masmorra").display = False
        self.query_one("#configs-vila").display = False
        self.query_one("#configs-caverna").display = False
        
        if tipo_selecionado == "masmorra":
            self.query_one("#configs-masmorra").display = True
        elif tipo_selecionado == "vila":
            self.query_one("#configs-vila").display = True
        elif tipo_selecionado == "caverna":
            self.query_one("#configs-caverna").display = True


    def on_button_pressed(self, event: Button.Pressed):
        """Captura os cliques dos botões."""
        if event.button.id == "btn-cancelar":
            self.dismiss(None) 
            
        elif event.button.id == "btn-gerar":
            nome = self.query_one("#input-nome").value
            tipo = self.query_one("#select-tipo").value
            mapa_pai_id = self.query_one("#select-pai").value
            if mapa_pai_id == Select.NULL or mapa_pai_id == Select.BLANK or mapa_pai_id == 0:
                mapa_pai_id = None
            if not nome or tipo == Select.BLANK or tipo == Select.NULL:
                self.notify("Preencha o nome e escolha um tipo!", severity="error")
                return

            dados_mapa = {
                "nome": nome,
                "tipo": str(tipo),
                "mapa_pai_id": mapa_pai_id ,
                "largura": int(self.query_one("#input-largura").value or 30),
                "altura": int(self.query_one("#input-altura").value or 30),
                "tile_parede": self.query_one("#input-tile-parede").value if self.query_one("#input-tile-parede").value else "🔲",
                "tile_chao": self.query_one("#input-tile-chao").value if self.query_one("#input-tile-chao").value else "  ",
                "configs": {}
            }
            
            # Adiciona as configurações dinâmicas dependendo do tipo
            if tipo == "masmorra":
                dados_mapa["configs"] = {
                    "max_salas": int(self.query_one("#input-max-salas").value),
                    "tam_min_sala": int(self.query_one("#input-tam-min").value),
                    "tam_max_sala": int(self.query_one("#input-tam-max").value)
                }
            elif tipo == "vila":
                dados_mapa["configs"] = {
                    "max_casas": int(self.query_one("#input-max-casas").value),
                    "tam_min_casa": int(self.query_one("#input-tam-min").value),
                    "tam_max_casa": int(self.query_one("#input-tam-max").value),
                    #"taxa_preenchimento": int(self.query_one("#input-taxa-vila").value)
                }
            elif tipo == "caverna":
                dados_mapa["configs"] = {
                    "taxa_preenchimento": int(self.query_one("#input-taxa-caverna").value),
                    "iteracoes": int(self.query_one("#input-iteracoes").value)
                }    
            
            
            self.dismiss(dados_mapa)
            

# ==============================================================================
# TELA 2: FORMULÁRIO DE PROPRIEDADES (NOVO)
# ==============================================================================
class PropriedadesFormScreen(ModalScreen[dict]):
    """Tela flutuante para editar as propriedades de um mapa que já está na memória."""

    def __init__(self, dados_atuais_recebidos_pelo_form: dict):
        super().__init__()
        # Recebe os dados do mapa atual para pré-preencher o formulário
        self.dados_de_propriedades_atuais = dados_atuais_recebidos_pelo_form
        self.mapa_pai_id = self.dados_de_propriedades_atuais.get('mapa_pai_id', None)
    
    def compose(self):
        with Vertical(id="prop-caixa"):
            yield Label("📝 Propriedades do Mapa", classes="titulo-secao")
            yield Label("Nome:")
            yield Input(value=self.dados_de_propriedades_atuais.get("nome", ""), id="prop-nome")
            
            yield Label("Mapa Pai:")
            yield Select([], id="prop-pai",)

            yield Horizontal(
                Static("Mapa Inicial:      ", classes="label"),         
                Switch(value=self.dados_de_propriedades_atuais.get(
                           'configs', {}).get("switch_coord_ini", False), id='switch_ini_world',
                       
                       tooltip='Mude para selecionar o local de início do jogo'),
                classes="container",)
            
            with Horizontal(id='cx-coordenadas_iniciais', classes="container"):
                yield Button("Indicar coordenada.", id='btn-indica-coord-ini', classes="label")
                yield Input(placeholder="coordenadas_iniciais: x , y",
                            value=self.dados_de_propriedades_atuais.get('configs',{}).get("coordenadas_iniciais", ""), id="coordenadas_iniciais", classes="label")
                
                        
            with Horizontal(id="prop-botoes"):
                yield Button("Cancelar", id="btn-prop-cancelar", variant="error")
                yield Button("Salvar Alterações", id="btn-prop-salvar", variant="primary")

    def on_mount(self):
        """Ao abrir, carrega os mapas do banco para o Select de Mapa Pai."""
        
        logging.info(f"dados_atuais_recebidos_pelo_form = {self.dados_de_propriedades_atuais}")
        
        switch_mapa_ini = self.query_one("#switch_ini_world").value 
        
        if switch_mapa_ini or self.dados_de_propriedades_atuais.get('configs', {}).get("coordenadas_iniciais"):
            self.query_one("#cx-coordenadas_iniciais").display = True
        else:
            self.query_one("#cx-coordenadas_iniciais").display = False
            
        from app.db.database import SessionLocal
            
        with SessionLocal() as db:
            mapas = db.query(MapaDB).all()
            opcoes = [("Nenhum (Raiz)", 0)] + [(m.nome, m.id) for m in mapas]
            
            select_pai = self.query_one("#prop-pai", Select)
            select_pai.set_options(opcoes)
            
            # Tenta marcar no Select o mapa pai que este mapa já possui
            pai_atual = self.dados_de_propriedades_atuais.get("mapa_pai_id", None)
            if pai_atual and pai_atual != '':
                select_pai.value = pai_atual
            else:
                select_pai.clear()
    
    @on(Switch.Changed, "#switch_ini_world")
    def on_switch_change(self, event: Switch.Changed ):
        
        if event.value: 
            self.query_one("#cx-coordenadas_iniciais").display = True
            self.notify(f"Mundo inicial setado. Deve haver apenas um.")
        else:
            self.query_one("#cx-coordenadas_iniciais").display = False
            
            self.query_one("#coordenadas_iniciais").value = ''
            self.dados_de_propriedades_atuais.get(
                'configs', {}).pop("coordenadas_iniciais")
            self.dados_de_propriedades_atuais.get(
                'configs', {}).pop("switch_ini_world")


    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-prop-cancelar":
            self.dismiss(None)
        
        elif event.button.id == "btn-indica-coord-ini":
            self.notify(f"Selecionar ponto de nascimento.")
            
            self.modo_captura_coordenada = True
            self.ferramenta_atual = "mira"

            # 🌟 Registra o identificador do campo para a resposta saber onde se injetar
            
            dados_requisicao = {
                "nome": self.query_one("#prop-nome").value or '',
                "mapa_pai_id": self.query_one("#prop-pai").value or None,
                "coordenadas_iniciais": self.query_one("#coordenadas_iniciais").value or '',
                "acao_especial": "ativar_capitura_de_posicao",
                "estado_formulario_atual": self._capturar_valores_campos_atuais()
            }
            
            self.contexto_do_modo_de_captura_ativo = dados_requisicao.get("id_alvo", 'config_ini')
            self.buffer_de_dados_do_formulario = dados_requisicao.get(
                "estado_formulario_atual", {})
            
            self.dismiss(dados_requisicao)

            
        elif event.button.id == "btn-prop-salvar":
            
            novo_nome = self.query_one("#prop-nome").value
            novo_pai = self.query_one("#prop-pai").value
            coordenadas_iniciais = self.query_one("#coordenadas_iniciais").value
            if novo_pai == Select.BLANK or novo_pai == Select.NULL or novo_pai ==  0:
                novo_pai = None

            # Retornamos apenas o que foi alterado
            dados_de_propridades_alteradas = {
                "nome": novo_nome or '',
                "mapa_pai_id": novo_pai or None,
                "coordenadas_iniciais": coordenadas_iniciais or ''
            }
            
            self.dismiss(dados_de_propridades_alteradas)
            
    def _capturar_valores_campos_atuais(self) -> dict:
        """Coleta o texto atual digitado nos campos para não perder o progresso."""
        return {
            # Exemplo de campo
            "nome": self.query_one("#prop-nome").value,
            "mapa_pai_id": self.query_one("#prop-pai").value,
            "coordenadas_iniciais": self.query_one("#coordenadas_iniciais").value
            # ... guarde o valor de todos os outros inputs do seu form aqui ...
        }


# PropriedadesEventoFormScreen e seus sub-modais foram movidos para:
# app/views/components/evento_form_screen.py
# O import está no topo deste arquivo.






# ==============================================================================
# TELA 3: AVISO DE ALTERAÇÕES NÃO SALVAS
# ==============================================================================
class ConfirmacaoSalvarScreen(ModalScreen[str]):
    """Tela que impede o utilizador de perder trabalho não salvo."""


    def compose(self):
        with Vertical(id="conf-caixa"):
            yield Label("⚠️ Atenção!", classes="titulo-secao", variant="warning")
            yield Label("O mapa atual tem alterações não salvas.")
            yield Label("O que deseja fazer?")

            with Horizontal(id="conf-botoes"):
                yield Button("Cancelar", id="btn-conf-cancelar")
                yield Button("Descartar", id="btn-conf-descartar", variant="error")
                yield Button("Salvar", id="btn-conf-salvar", variant="success")

    def on_button_pressed(self, event: Button.Pressed):
        # Retorna a ação escolhida como texto
        if event.button.id == "btn-conf-cancelar":
            self.dismiss("cancelar")
        elif event.button.id == "btn-conf-descartar":
            self.dismiss("descartar")
        elif event.button.id == "btn-conf-salvar":
            self.dismiss("salvar")
            
import os # Importante para verificar se o ficheiro existe na hora de importar

# ==============================================================================
# TELA 4: MENU PRINCIPAL (AÇÕES)
# ==============================================================================
class MenuAcoesScreen(ModalScreen[str]):
    """Tela de menu acionada pelo botão 'Menu' no topo."""


    def compose(self):
        with Vertical(id="menu-caixa"):
            yield Label("🛠️ Menu Principal", classes="titulo-secao")
            yield Button("📥 Importar CSV", id="btn-menu-importar", variant="primary")
            yield Button("📤 Exportar CSV", id="btn-menu-exportar", variant="success")
            yield Button("Voltar", id="btn-menu-voltar", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        # Retorna a ação escolhida (ou None se cancelar)
        if event.button.id == "btn-menu-voltar":
            self.dismiss(None)
        elif event.button.id == "btn-menu-importar":
            self.dismiss("importar")
        elif event.button.id == "btn-menu-exportar":
            self.dismiss("exportar")


# ==============================================================================
# TELA 5: FORMULÁRIO DE NOME DO FICHEIRO CSV
# ==============================================================================
class ArquivoCSVScreen(ModalScreen[str]):
    """Pede ao utilizador o caminho/nome do ficheiro CSV."""

    def __init__(self, acao: str):
        super().__init__()
        self.acao = acao # Guarda se estamos a importar ou a exportar

    def compose(self):
        with Vertical(id="csv-caixa"):
            titulo = "📤 Exportar para CSV" if self.acao == "exportar" else "📥 Importar de CSV"
            yield Label(titulo, classes="titulo-secao")
            yield Label("Digite o nome do ficheiro:")
            yield Input(placeholder="ex: mapa_caverna.csv", id="input-csv-nome")

            with Horizontal(id="csv-botoes"):
                yield Button("Cancelar", id="btn-csv-cancelar", variant="error")
                yield Button("Confirmar", id="btn-csv-confirmar", variant="primary")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-csv-cancelar":
            self.dismiss(None)
        elif event.button.id == "btn-csv-confirmar":
            nome_arquivo = self.query_one("#input-csv-nome").value
            if not nome_arquivo:
                self.notify("Por favor, digite um nome!", severity="error")
                return
            
            # Garante que termina com .csv
            if not nome_arquivo.endswith(".csv"):
                nome_arquivo += ".csv"
                
            self.dismiss(nome_arquivo)    
