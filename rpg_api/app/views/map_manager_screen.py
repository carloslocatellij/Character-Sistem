# app/screens/map_manager_screen.py

import os
import copy
from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, Tree, Static, Label, Button, Input, Select
from textual.widgets import TabbedContent, TabPane
from textual.containers import Horizontal, Vertical, Container
from textual.message import Message
from textual import on
from textual.events import MouseDown, MouseUp, MouseMove
from app.core.mapas import GestorDeMapas
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from rich.text import Text

import rich.cells
from rich.cells import cell_len as rich_cell_len

def patched_cell_len(text: str) -> int:
    # Lógica robusta para emojis complexos do RPG
    if "\u200d" in text or "\ufe0f" in text:
        return 2
    # Fallback para a lógica original para manter compatibilidade com texto comum
    return rich_cell_len(text)

# Substituição global na biblioteca Rich
rich.cells.cell_len = patched_cell_len

CSS_PATH = "styles.css"

class CatalogoTiles:
    """Registo central que define as categorias e propriedades visuais dos emojis."""
    
    # Listas para construir as abas
    TERRENOS = ["  ", "🔳", "⬜",  "🟫", "🟩", "🔲", "🟦"]
    
    OBJETOS = [ "🌲", "🌳", "🌴", "🌵", "🍄", "🕸️",
                "🌻", "🌹", "🌷", "🔮", "🗿", "🏰", 
                "🚪", "🏘️ ", "🏚️ ", "🏯", "🕍",
                "💀", "⛺",  "⛲", "⌛", "🕋",
                "🛶", "🧊", "📦", "📖", "🪑", "🏴",
                "🌭", "🍔", "🍕", "🍺", "🍫", "♟️"]
    
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
        """Verifica de qual aba o pincel pertence."""
        tile_limpo = tile.strip()
        if tile_limpo in cls.TERRENOS:
            return "terreno"
        return "objeto" # Por padrão, trata tudo o resto (e a borracha) como objeto

    @classmethod
    def obter_cor_fundo(cls, tile: str) -> str:
        """Pega o código hexadecimal da cor de fundo de um chão."""
        tile_limpo = tile.strip()
        return cls.CORES_BG.get(tile_limpo, "")


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
        
        if eh_gnome_ou_linux and tile_limpo in emojis_rebeldes:

            return f"{tile_limpo} " 
        return tile_limpo

    return tile_limpo

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
        self.mouse_pressionado = False # O nosso "sensor" de clique
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
        super().__init__()
        self.mapa_atual_matriz = None
        # 🧠 NOVA MEMÓRIA PARA AS ENTIDADES/OBJETOS
        # Vai guardar dados no formato: {(linha, coluna): "🪑"}
        self.mapa_atual_objetos = {} 
        
        self.mapa_atual_dados = None
        self.tile_selecionado = "⬛"
        self.tem_alteracoes = False
        self.id_mapa_na_agulha = None
        self.historico_desfazer = []
        self.historico_refazer = []
        
# ==========================================
    # UTILITÁRIOS DE SERIALIZAÇÃO DE OBJETOS
    # ==========================================
    def _empacotar_objetos_para_banco(self) -> dict:
        """Transforma as chaves de tupla (1, 2) em texto '1,2' para poder salvar no Banco."""
        objetos_formatados = {}
        for (linha, coluna), emoji in self.mapa_atual_objetos.items():
            chave_texto = f"{linha},{coluna}"
            objetos_formatados[chave_texto] = emoji
        return objetos_formatados

    def _desempacotar_objetos_do_banco(self, objetos_json: dict) -> dict:
        """Transforma o texto '1,2' do Banco de volta em tupla matemática (1, 2)."""
        objetos_na_memoria = {}
        if not objetos_json:
            return objetos_na_memoria # Retorna vazio se não houver objetos
            
        for chave_texto, emoji in objetos_json.items():
            partes = chave_texto.split(",")
            linha = int(partes[0])
            coluna = int(partes[1])
            objetos_na_memoria[(linha, coluna)] = emoji
        return objetos_na_memoria

    def compose(self) -> ComposeResult:
        # 1. Nossa Barra Superior (Removido o Header nativo para não haver conflitos)
        with Horizontal(id="top-menu"):
            yield Button("Menu", id="btn-menu")
            yield Button("Novo", id="btn-novo", variant="primary")
            yield Button("Salvar", id="btn-salvar", variant="success")
            yield Button("Editar", id="btn-editar")
            yield Button("Opções", id="btn-opcoes")
            yield Button("X", id="btn-fechar", variant="error")

        # 2. O Layout Principal (Esquerda e Direita)
        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                
                # --- A NOVA PALETA CLICÁVEL ---
                with Container(id="paleta-container"):
                    yield Label("🎨 Paleta", classes="titulo-secao")
                    yield Label(f"Selecionado: {self.tile_selecionado}", id="lbl-tile-atual")
                    
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
                        with TabPane(f" Eventos {' '}", id="tab-eventos", disabled=True):
                            yield Label("Em breve: NPCs, Inimigos e Triggers...", id="aviso-eventos")
                    
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
        
        with SessionLocal() as db:
            try:
                todos_mapas = db.query(MapaDB).all()
            except:
                todos_mapas = []
                
        from collections import defaultdict
        filhos_de = defaultdict(list)
        
        for mapa in todos_mapas:
            pai_id = mapa.mapa_pai_id
            
            if pai_id == 0 or pai_id == "" or str(pai_id).lower() == "none":
                pai_id = None
                
            filhos_de[pai_id].append(mapa)
            
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
        mapa_id = event.node.data
        if mapa_id is None:
            return # Clicou na palavra "Meus Mapas" (A raiz visual), ignoramos.

        if self.tem_alteracoes:
            # Tem coisas não salvas! Guarda o ID que ele tentou abrir e chama o aviso.
            self.id_mapa_na_agulha = mapa_id
            self.app.push_screen(ConfirmacaoSalvarScreen(), self.ao_responder_aviso)
        else:
            # Caminho livre, carrega direto!
            self.carregar_mapa_do_banco(mapa_id)

    def ao_responder_aviso(self, resposta: str):
        """Trata a resposta do utilizador no modal de confirmação."""
        if resposta == "cancelar":
            self.id_mapa_na_agulha = None
            return # Não faz nada, o utilizador desistiu de trocar de mapa
            
        elif resposta == "salvar":
            self.salvar_mapa_no_banco()
            self.carregar_mapa_do_banco(self.id_mapa_na_agulha)
            
        elif resposta == "descartar":
            self.tem_alteracoes = False # Esquece a sujeira
            self.carregar_mapa_do_banco(self.id_mapa_na_agulha)


    def carregar_mapa_do_banco(self, mapa_id: int):
        with SessionLocal() as db:
            mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id).first()
            if not mapa_db:
                return

            self.mapa_atual_matriz = mapa_db.mapa_em_si
            
            # ✅ DEPOIS: Agora puxamos diretamente da nova coluna 'objetos'
            objetos_salvos = mapa_db.objetos if mapa_db.objetos else {}
            self.mapa_atual_objetos = self._desempacotar_objetos_do_banco(objetos_salvos)

            # E guardamos as configs originais para não as perdermos
            configs_salvas = mapa_db.configs if mapa_db.configs else {}

            self.mapa_atual_dados = {
                "id": mapa_db.id,
                "nome": mapa_db.nome,
                "tipo": mapa_db.tipo,
                "mapa_pai_id": mapa_db.mapa_pai_id,
                "largura": mapa_db.largura,
                "altura": mapa_db.altura,
                "configs": configs_salvas # Resgata as configurações de geração!
            }
            
            self.tem_alteracoes = False
            self.id_mapa_na_agulha = None
            
            self.exibir_mapa_na_tela()
            self.notify(f"Mapa '{mapa_db.nome}' carregado!")

    
    def salvar_estado_historico(self):
        """Tira uma fotografia à matriz atual antes de a alterarmos."""
        # Limitamos o histórico a 10 passos para não consumir muita RAM
        if len(self.historico_desfazer) > 10:
            self.historico_desfazer.pop(0)
            
        snapshot = {
            "matriz": copy.deepcopy(self.mapa_atual_matriz),
            "objetos": copy.deepcopy(self.mapa_atual_objetos)
        }
        
        self.historico_desfazer.append(snapshot)
        self.historico_refazer.clear()

    @on(MapaInterativo.Pintar)
    def processar_pintura(self, event: MapaInterativo.Pintar):
        if self.mapa_atual_matriz is None: return 
            
        linha, coluna = event.linha, event.coluna
        
        if 0 <= linha < len(self.mapa_atual_matriz) and 0 <= coluna < len(self.mapa_atual_matriz[0]):
            
            if event.inicio_de_traco:
                self.salvar_estado_historico()

            tipo_pincel = CatalogoTiles.obter_tipo(self.tile_selecionado)
            
            if self.tile_selecionado == "❌":
                # MODO BORRACHA: Apaga o objeto daquela coordenada (se existir)
                if (linha, coluna) in self.mapa_atual_objetos:
                    del self.mapa_atual_objetos[(linha, coluna)]
            elif tipo_pincel == "terreno":
                # MODO TERRENO: Atualiza apenas a matriz base
                if self.mapa_atual_matriz[linha][coluna] != self.tile_selecionado:
                    self.mapa_atual_matriz[linha][coluna] = self.tile_selecionado
            elif tipo_pincel == "objeto":
                # MODO OBJETO: Adiciona/Atualiza no dicionário de entidades
                self.mapa_atual_objetos[(linha, coluna)] = self.tile_selecionado

            self.tem_alteracoes = True
            self.exibir_mapa_na_tela()    
    

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques na tela principal."""
        if event.button.id == "btn-fechar":
            self.dismiss()
        elif event.button.id == "btn-novo":
            self.app.push_screen(NovoMapaFormScreen(), self.ao_terminar_form)
        elif event.button.id == "btn-salvar":
            self.salvar_mapa_no_banco()
        elif event.button.id == "btn-desfazer":
            self.desfazer_acao()
        elif event.button.id == "btn-refazer":
            self.refazer_acao()
        # (Junto aos botões desfazer/refazer)
        elif event.button.id == "btn-borracha":
            self.tile_selecionado = "❌"
            self.query_one("#lbl-tile-atual", Label).update("Selecionado: ❌ Borracha")
        
        if event.button.has_class("btn-paleta"):
            # ✅ DEPOIS: Passamos o texto do botão pelo nosso padronizador!
            tile_bruto = str(event.button.label)
            self.tile_selecionado = padronizar_largura_tile(tile_bruto)

            self.query_one("#lbl-tile-atual", Label).update(f"Selecionado: {self.tile_selecionado}")
            return
            
        elif event.button.id == "btn-opcoes":
            if self.mapa_atual_dados is None:
                self.notify("Crie ou carregue um mapa primeiro!", severity="warning")
                return
            
            self.app.push_screen(
                PropriedadesFormScreen(self.mapa_atual_dados), 
                self.ao_terminar_propriedades)
            
        elif event.button.id == "btn-menu":
            # Abre o menu flutuante!
            self.app.push_screen(MenuAcoesScreen(), self.ao_escolher_acao_menu)


    def ao_terminar_form(self, dados_do_form: dict | None):
        """Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form."""
        if dados_do_form is None:
            return 
        self.mapa_atual_dados = dados_do_form
        self.mapa_atual_objetos.clear()
        
        # 2. PREPARAÇÃO DOS DADOS: Juntamos os tiles e as configurações num único pacote
        configs_completas = dados_do_form.get("configs", {})
        configs_completas["tile_parede"] = dados_do_form.get("tile_parede", "🔲")
        configs_completas["tile_chao"] = dados_do_form.get("tile_chao", "  ")
        
        # 3. Chama a lógica pura (O nosso core de geração) e injeta os dados reais
        self.mapa_atual_matriz = GestorDeMapas.gerar_mapa_rpg(
            tipo=dados_do_form["tipo"],
            largura=dados_do_form["largura"],
            altura=dados_do_form["altura"],
            configs=configs_completas 
        )
        # 4. Exibe o mapa na tela e avisa o utilizador!
        self.exibir_mapa_na_tela()
        self.notify(f"Mapa '{dados_do_form['nome']}' gerado com as novas regras!")
        
        
    def ao_terminar_propriedades(self, alteracoes: dict | None):
        """Callback acionado ao fechar a tela de Propriedades."""
        if alteracoes is None:
            return 
            
        # Atualiza a memória com os novos dados
        self.mapa_atual_dados["nome"] = alteracoes["nome"]
        self.mapa_atual_dados["mapa_pai_id"] = alteracoes["mapa_pai_id"]
        self.tem_alteracoes = True
        # Atualiza o título na tela
        self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.mapa_atual_dados['nome']}")
        self.notify("Propriedades atualizadas na memória! Lembre-se de Salvar.")
    
    def desfazer_acao(self):
        """Retrocede a matriz para o último estado guardado."""
        if not self.historico_desfazer:
            self.notify("Não há mais ações para desfazer!", severity="warning")
            return
            
        # 1. Guarda a foto atual no "Refazer" caso nos arrependamos do Desfazer
        snapshot_atual = {
            "matriz": copy.deepcopy(self.mapa_atual_matriz),
            "objetos": copy.deepcopy(self.mapa_atual_objetos)
        }
        self.historico_refazer.append(snapshot_atual)
        
        # 2. Puxa o snapshot do passado e restaura as duas camadas
        snapshot_passado = self.historico_desfazer.pop()
        self.mapa_atual_matriz = snapshot_passado["matriz"]
        self.mapa_atual_objetos = snapshot_passado["objetos"]
        
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()

    def refazer_acao(self):
        """Avança Terrenos e Objetos para o estado do futuro."""
        if not self.historico_refazer:
            self.notify("Não há ações para refazer!", severity="warning")
            return

        # 1. Guarda o estado atual no Desfazer
        snapshot_atual = {
            "matriz": copy.deepcopy(self.mapa_atual_matriz),
            "objetos": copy.deepcopy(self.mapa_atual_objetos)
        }
        self.historico_desfazer.append(snapshot_atual)
        
        # 2. Puxa o snapshot do futuro e restaura
        snapshot_futuro = self.historico_refazer.pop()
        self.mapa_atual_matriz = snapshot_futuro["matriz"]
        self.mapa_atual_objetos = snapshot_futuro["objetos"]
        
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()

    def exibir_mapa_na_tela(self):
        """Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)."""
        if self.mapa_atual_matriz is None: return
        
        texto_mapa = Text(no_wrap=True)
        
        for linha_idx in range(len(self.mapa_atual_matriz)):
            for col_idx in range(len(self.mapa_atual_matriz[0])):
                
                # 1. Pega o terreno base da matriz
                tile_chao = self.mapa_atual_matriz[linha_idx][col_idx]
                
                # 2. Verifica se existe um objeto nesta coordenada
                tile_objeto = self.mapa_atual_objetos.get((linha_idx, col_idx))
                
                # 3. Lógica de Renderização
                if tile_objeto is not None:
                    # Desenha o Objeto, mas copia o background do terreno abaixo dele!
                    cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                    estilo = f"on {cor_bg}" if cor_bg else ""
                    texto_mapa.append(padronizar_largura_tile(tile_objeto), style=estilo)
                else:
                    # Não há objetos, desenha apenas o chão limpo
                    texto_mapa.append(tile_chao)
            
            # Quebra de linha no fim de cada linha da grelha
            texto_mapa.append("\n")
        
        self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.mapa_atual_dados['nome']}")
        self.query_one("#mapa-view", MapaInterativo).update(texto_mapa)

    def salvar_mapa_no_banco(self):
        """
        Guarda o mapa no banco de dados. 
        Verifica nomes duplicados e decide automaticamente entre criar um novo (Insert)
        ou atualizar um existente (Update).
        """
        # 1. Verificações de segurança base (O mapa existe na memória?)
        if self.mapa_atual_matriz is None or self.mapa_atual_dados is None:
            self.notify("Não há nenhum mapa gerado para salvar!", severity="warning")
            return

        nome_mapa = self.mapa_atual_dados.get("nome")
        
        # Pega o ID atual. O método '.get()' retorna 'None' se a chave "id" não existir.
        mapa_id_atual = self.mapa_atual_dados.get("id") 

        # 2. Abertura da comunicação com o Banco de Dados
        with SessionLocal() as db:
            
            # --- VALIDAÇÃO DE NOME ÚNICO ---
            # Busca no banco qualquer mapa que tenha exatamente este nome
            try:
                mapa_existente = db.query(MapaDB).filter(MapaDB.nome == nome_mapa).first()
            except:
                mapa_existente = None

            # Se achou um mapa com este nome, E o ID dele é diferente do nosso mapa atual
            if mapa_existente:
                mapa_id_existente = mapa_existente.id
                if mapa_id_existente != mapa_id_atual:
                    self.notify(f"Já existe um mapa chamado '{nome_mapa}'. Escolha outro nome em Opções!", severity="error")
                    return # Interrompe a função aqui, não salva nada

            # --- DECISÃO: UPDATE OU INSERT ---
            if mapa_id_atual is not None:
                # MODO UPDATE: O mapa já existe, vamos apenas atualizar os dados
                mapa_para_atualizar = db.query(MapaDB).filter(MapaDB.id == mapa_id_atual).first()
                
                if mapa_para_atualizar:
                    mapa_para_atualizar.nome = nome_mapa
                    mapa_para_atualizar.tipo = self.mapa_atual_dados.get("tipo")
                    mapa_para_atualizar.mapa_pai_id = self.mapa_atual_dados.get("mapa_pai_id")
                    mapa_para_atualizar.largura = self.mapa_atual_dados.get("largura")
                    mapa_para_atualizar.altura = self.mapa_atual_dados.get("altura")
                    mapa_para_atualizar.configs = self.mapa_atual_dados.get("configs", {})
                    mapa_para_atualizar.mapa_em_si = self.mapa_atual_matriz 
                    mapa_para_atualizar.objetos = self._empacotar_objetos_para_banco()
                    acao_realizada = "atualizado"
                else:
                    self.notify("Erro: Mapa original não foi encontrado no banco de dados.", severity="error")
                    return
            else:
                # MODO INSERT: O mapa é totalmente novo
                novo_mapa = MapaDB(
                    nome=nome_mapa,
                    tipo=self.mapa_atual_dados.get("tipo"),
                    mapa_pai_id=self.mapa_atual_dados.get("mapa_pai_id"),
                    largura=self.mapa_atual_dados.get("largura"),
                    altura=self.mapa_atual_dados.get("altura"),
                    mapa_em_si=self.mapa_atual_matriz,
                    configs=self.mapa_atual_dados.get("configs", {}),
                    objetos=self._empacotar_objetos_para_banco()
                )
                db.add(novo_mapa)
                acao_realizada = "criado"

            # 3. Gravar de facto no banco de dados (Efetivar a transação)
            db.commit()

            # --- PÓS-SALVAMENTO ---
            # Se acabámos de criar um mapa novo, o banco gerou um ID para ele.
            if acao_realizada == "criado":
                db.refresh(novo_mapa) # Pede ao banco para nos dar as informações geradas (o ID)
                self.mapa_atual_dados["id"] = novo_mapa.id # Guardamos na memória!

            # Limpa o alerta de alterações não salvas (o nosso "sensor de sujeira")
            self.tem_alteracoes = False 
            
            # Atualiza a árvore lateral para exibir o novo mapa ou a mudança de nome
            self.carregar_arvore_de_mapas()
            
            # Mostra a mensagem de sucesso verde
            self.notify(f"Mapa '{nome_mapa}' {acao_realizada} com sucesso!", severity="success")
    
    def ao_escolher_acao_menu(self, acao: str | None):
        """Callback após o utilizador clicar em algo no Menu Principal."""
        if acao is None: return
        
        if acao == "exportar" and self.mapa_atual_matriz is None:
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
                for linha in self.mapa_atual_matriz:
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
            self.mapa_atual_matriz = nova_matriz
            
            # Atualiza os dados de controlo para fingir que é um mapa novo (ainda não salvo no banco)
            self.mapa_atual_dados = {
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
            yield Select((("Masmorra", "masmorra"), ("Vila", "vila"), ("Caverna", "caverna")), prompt="Tipo de Mapa", id="select-tipo", value="caverna")
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



    def __init__(self, dados_atuais: dict):
        super().__init__()
        # Recebe os dados do mapa atual para pré-preencher o formulário
        self.dados_atuais = dados_atuais

    def compose(self):
        with Vertical(id="prop-caixa"):
            yield Label("📝 Propriedades do Mapa", classes="titulo-secao")
            yield Label("Nome:")
            yield Input(value=self.dados_atuais.get("nome", ""), id="prop-nome")
            
            yield Label("Mapa Pai:")
            yield Select([], id="prop-pai")

            with Horizontal(id="prop-botoes"):
                yield Button("Cancelar", id="btn-prop-cancelar", variant="error")
                yield Button("Salvar Alterações", id="btn-prop-salvar", variant="primary")

    def on_mount(self):
        """Ao abrir, carrega os mapas do banco para o Select de Mapa Pai."""
        with SessionLocal() as db:
            mapas = db.query(MapaDB).all()
            opcoes = [("Nenhum (Raiz)", 0)] + [(m.nome, m.id) for m in mapas]
            
            select_pai = self.query_one("#prop-pai", Select)
            select_pai.set_options(opcoes)
            
            # Tenta marcar no Select o mapa pai que este mapa já possui
            pai_atual = self.dados_atuais.get("mapa_pai_id")
            if pai_atual is not None:
                select_pai.value = pai_atual
            else:
                select_pai.clear()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-prop-cancelar":
            self.dismiss(None)
            
        elif event.button.id == "btn-prop-salvar":
            novo_nome = self.query_one("#prop-nome").value
            novo_pai = self.query_one("#prop-pai").value
            if novo_pai == Select.BLANK or novo_pai == Select.NULL or novo_pai ==  0:
                novo_pai.clear()

            # Retornamos apenas o que foi alterado
            alteracoes = {
                "nome": novo_nome,
                "mapa_pai_id": novo_pai
            }
            self.dismiss(alteracoes)


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