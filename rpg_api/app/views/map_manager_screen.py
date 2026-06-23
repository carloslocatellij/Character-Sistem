# app/screens/map_manager_screen.py
import os
import copy
import json
from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, Tree, Static, Label, Button, Input, Select, ListView, ListItem
from textual.widgets import TabbedContent, TabPane
from textual.containers import Horizontal, Vertical, Container
from textual.message import Message
from textual import on
from textual.events import MouseDown, MouseUp, MouseMove
from app.core.entities.mapas import GestorDeMapas
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from app.models.eventos_db import EventoDB
from app.models.equipamentos_db import ItemDB
from app.core.entities.emojis import CatalogoTiles, padronizar_largura_tile, dict_item_emoji, dict_emoji_efeito, dict_emoji_racas
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

CSS_PATH = "styles/styles.css"


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
        # 🧠 NOVA MEMÓRIA PARA OBJETOS
        # Vai guardar dados no formato: {(linha, coluna): "🪑"}
        self.mapa_atual_objetos = {}
        # 🧠 NOVA MEMÓRIA PARA ENTIDADES/EVENTOS LÓGICOS
        # Formato: {(linha, coluna): {"id": int, "nome": str, "emoji": str, ...}
        self.mapa_atual_eventos = {}
        
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
    
    # ==========================================
    # MANIPULAÇÃO E SERIALIZAÇÃO DE EVENTOS
    # ==========================================
    def adicionar_evento_memoria(self, linha: int, coluna: int, nome: str, emoji: str, event_type: str, parametros: dict, evento_id: int = None):
        """Regista ou atualiza um evento numa coordenada específica."""
        dados_evento = {
            "nome": nome,
            "emoji": emoji,
            "event_type": event_type,
            "parametros": parametros
        }
        # Só adicionamos o ID se ele vier do banco de dados (para fins de UPDATE futuro)
        if evento_id is not None:
            dados_evento["id"] = evento_id
            
        self.mapa_atual_eventos[(linha, coluna)] = dados_evento
        self.tem_alteracoes = True

    def _empacotar_eventos_para_banco(self) -> list[dict]:
        """Transforma o dicionário de memória numa lista pronta para o SQLAlchemy."""
        lista_eventos = []
        for (linha, coluna), dados in self.mapa_atual_eventos.items():
            # Cria uma cópia para não alterar a memória original
            registo = dados.copy() 
            registo["pos_y"] = linha
            registo["pos_x"] = coluna
            lista_eventos.append(registo)
        return lista_eventos

    def _desempacotar_eventos_do_banco(self, lista_eventos_db: list[dict]):
        """Povoa a memória a partir da lista de eventos vindos do banco de dados."""
        self.mapa_atual_eventos.clear() # Limpa a memória atual
        
        if not lista_eventos_db:
            return
            
        for evento in lista_eventos_db:
            linha = evento["pos_y"]
            coluna = evento["pos_x"]
            
            self.adicionar_evento_memoria(
                linha=linha,
                coluna=coluna,
                nome=evento["nome"],
                emoji=evento["emoji"],
                event_type=evento["event_type"],
                parametros=evento["parametros"],
                evento_id=evento.get("id")
            )

    def compose(self) -> ComposeResult:
        # 1. Nossa Barra Superior (Removido o Header nativo para não haver conflitos)
        with Horizontal(id="top-menu", ):
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
        from app.db.database import SessionLocal
        
        with SessionLocal() as db:
            # 1. Carrega o Mapa Base
            mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id).first()
            if not mapa_db:
                return

            self.mapa_atual_matriz = mapa_db.mapa_em_si
            
            objetos_salvos = mapa_db.objetos if mapa_db.objetos else {}
            self.mapa_atual_objetos = self._desempacotar_objetos_do_banco(objetos_salvos)

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
            configs_salvas = mapa_db.configs if mapa_db.configs else {}
            self.mapa_atual_dados = {
                "id": mapa_db.id,
                "nome": mapa_db.nome,
                "tipo": mapa_db.tipo,
                "mapa_pai_id": mapa_db.mapa_pai_id,
                "largura": mapa_db.largura,
                "altura": mapa_db.altura,
                "configs": configs_salvas
            }
            
            self.tem_alteracoes = False
            self.id_mapa_na_agulha = None
            
            # Desenha tudo na tela (Chão + Objetos + Eventos)
            self.exibir_mapa_na_tela()
            self.notify(f"Mapa '{mapa_db.nome}' e eventos carregados!")

    
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
            tipo_pincel = CatalogoTiles.obter_tipo(self.tile_selecionado)
            
            # 🪄 TRATAMENTO EXCLUSIVO PARA EVENTOS
            if tipo_pincel == "evento":
                # Abrimos o modal apenas no INÍCIO do clique. 
                # Isso impede o Textual de abrir 50 janelas enquanto o usuário arrasta o mouse!
                if event.inicio_de_traco:
                    # Desliga a trava de clique contínuo imediatamente
                    self.query_one("#mapa-view", MapaInterativo).mouse_pressionado = False
                    
                    # Verifica se já existia um evento nessa posição para abrir em Modo Edição
                    evento_atual = self.mapa_atual_eventos.get((linha, coluna))
                    
                    # Abre o Modal passando as coordenadas e escuta o callback de retorno
                    self.app.push_screen(
                        PropriedadesEventoFormScreen(linha, coluna, self.tile_selecionado, evento_atual),
                        lambda dados: self.ao_terminar_configurar_evento(linha, coluna, dados)
                    )
                return # Interrompe o fluxo padrão de desenho contínuo

            # MODO BORRACHA / TERRENO / OBJETO (Mantém-se idêntico ao seu código anterior)
            if event.inicio_de_traco:
                self.salvar_estado_historico()

            if self.tile_selecionado == "❌":
                if (linha, coluna) in self.mapa_atual_objetos: del self.mapa_atual_objetos[(linha, coluna)]
                if (linha, coluna) in self.mapa_atual_eventos: del self.mapa_atual_eventos[(linha, coluna)] # Borracha apaga eventos também!
            elif tipo_pincel == "terreno":
                if self.mapa_atual_matriz[linha][coluna] != self.tile_selecionado:
                    self.mapa_atual_matriz[linha][coluna] = self.tile_selecionado
            else:
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
        
    def ao_terminar_configurar_evento(self, linha: int, coluna: int, dados_evento: dict | None):
        """Callback acionado quando o usuário confirma os dados do evento no Modal."""
        if dados_evento is None:
            return # Usuário clicou em Cancelar, nada é alterado

        # Usa a nossa função estruturada (que validamos no teste TDD anterior!)
        self.adicionar_evento_memoria(
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
                # ✅ NOVO: Verifica primeiro se há um evento lógico nesta coordenada
                dados_evento = self.mapa_atual_eventos.get((linha_idx, col_idx))
                
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
        
        self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.mapa_atual_dados['nome']}")
        self.query_one("#mapa-view", MapaInterativo).update(texto_mapa)
        

    def salvar_mapa_no_banco(self):
        """Salva o mapa atual, os objetos estáticos e os eventos dinâmicos no banco de dados."""
        from app.db.database import SessionLocal # Ajuste o import conforme o seu projeto
        
        mapa_id_atual = self.mapa_atual_dados.get("id") if self.mapa_atual_dados else None
        nome_mapa = self.mapa_atual_dados.get("nome") if self.mapa_atual_dados else None
        try:
            with SessionLocal() as db:
                # ==========================================
                # 1. SALVAR O MAPA BASE E OBJETOS (CENÁRIO)
                # ==========================================
                if mapa_id_atual is not None:
                    # MODO UPDATE
                    mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id_atual).first()
                    mapa_db.nome = nome_mapa
                    mapa_db.tipo = self.mapa_atual_dados.get("tipo")
                    mapa_db.mapa_pai_id = self.mapa_atual_dados.get("mapa_pai_id")
                    mapa_db.largura = self.mapa_atual_dados.get("largura")
                    mapa_db.altura = self.mapa_atual_dados.get("altura")
                    mapa_db.mapa_em_si = self.mapa_atual_matriz 
                    mapa_db.configs = self.mapa_atual_dados.get("configs", {})
                    mapa_db.objetos = self._empacotar_objetos_para_banco()
                    
                    acao_realizada = "atualizado"
                else:
                    # MODO INSERT
                    mapa_db = MapaDB(
                        nome=nome_mapa,
                        tipo=self.mapa_atual_dados.get("tipo"),
                        mapa_pai_id=self.mapa_atual_dados.get("mapa_pai_id"),
                        largura=self.mapa_atual_dados.get("largura"),
                        altura=self.mapa_atual_dados.get("altura"),
                        mapa_em_si=self.mapa_atual_matriz,
                        configs=self.mapa_atual_dados.get("configs", {}), 
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
                self.mapa_atual_dados["id"] = mapa_db.id 
                self.tem_alteracoes = False
                
                self.notify(f"Mapa '{nome_mapa}' e seus eventos foram guardados com sucesso!", severity="success")

        except Exception as e:
            self.notify(f"Erro ao salvar no banco: {e}", severity="error")
    
    
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


class PropriedadesEventoFormScreen(ModalScreen[dict]):
    """Formulário principal que gerencia o JSON do evento com páginas e comandos."""

    def __init__(self, linha: int, coluna: int, emoji: str, dados_existentes: dict = None):
        super().__init__()
        self.linha = linha
        self.coluna = coluna
        self.emoji = emoji
        self.dados_existentes = copy.deepcopy(dados_existentes) or {}
        
        # Estrutura JSON Universal
        params = self.dados_existentes.get("parametros", {})
        if "paginas" not in params:
             # Evento simples ou novo
             self.paginas = [
                 {
                     "id_pagina": 1,
                     "condicoes": {},
                     "configuracao_visual": {"emoji": self.emoji},
                     "gatilho": "acao_jogador",
                     "comandos": []
                 }
             ]
        else:
             self.paginas = params["paginas"]
             
        self.pagina_atual_idx = 0

    def compose(self):
        itens_set = set([  v for sub_dict in dict_item_emoji.values() for k, v in sub_dict.items()])
        racas_set = set([v for _,v in dict_emoji_racas.items()])
        efeitos_set = set([v for _,v in dict_emoji_efeito.items()])
        coletanea_emoji = list([*itens_set, *racas_set, *efeitos_set, *CatalogoTiles.OBJETOS])
        
        with Vertical(id="evt-caixa-full"):
            titulo = f"⚙️ Evento em [{self.linha},{self.coluna}]"
            yield Label(titulo, classes="titulo-secao")
            
            with Horizontal(classes="linha-dupla"):
                yield Label("Nome:", classes="campo-rotulo")
                yield Input(value=self.dados_existentes.get("nome", f"ev_{self.linha}_{self.coluna}"), id="evt-nome")
                yield Label("Emoji:", classes="campo-rotulo")
                
                yield Select([(v, v) for v in coletanea_emoji] +  [(self.emoji, self.emoji)]                             , value=self.emoji, id="evt-emoji")
            
            with Horizontal(classes="linha-dupla"):
                yield Label("Página:", classes="campo-rotulo")
                yield Button("<", id="btn-pag-ant", classes="btn-pequeno")
                yield Label(f" {self.pagina_atual_idx + 1} / {len(self.paginas)} ", id="lbl-pag-atual")
                yield Button(">", id="btn-pag-prox", classes="btn-pequeno")
                yield Button("+ Pág", id="btn-add-pag", variant="primary", classes="btn-pequeno")
                yield Button("- Pág", id="btn-del-pag", variant="error", classes="btn-pequeno")
                
            yield Label("Gatilho:", classes="campo-rotulo")
            yield Select([
                ("Ação do Jogador (Pressionar Botão)", "acao_jogador"),
                ("Toque do Jogador (Pisar)", "toque_jogador"),
                ("Toque do Evento (Bater no herói)", "toque_evento"),
                ("Processo Automático", "processo_automatico"),
                ("Processo Paralelo", "processo_paralelo")
            ], value=self.paginas[0].get("gatilho", "acao_jogador"), id="evt-gatilho")
            
            # ==========================================
            # SEÇÃO DE CONDIÇÕES DA PÁGINA
            # ==========================================
            yield Label("📋 Condições desta Página:", classes="campo-rotulo")
            with Vertical(id="secao-condicoes"):
                # --- Switches ---
                with Horizontal(classes="linha-dupla"):
                    yield Label("Switches:", classes="campo-rotulo")
                    yield Button("+ Switch", id="btn-add-switch", variant="primary", classes="btn-pequeno")
                yield Static("", id="lista-switches")
                
                # --- Variáveis ---
                with Horizontal(classes="linha-dupla"):
                    yield Label("Variáveis:", classes="campo-rotulo")
                    yield Button("+ Variável", id="btn-add-variavel", variant="primary", classes="btn-pequeno")
                yield Static("", id="lista-variaveis")
                
                # --- Self Switch ---
                with Horizontal(classes="linha-dupla"):
                    yield Label("Self Switch:", classes="campo-rotulo")
                    yield Select([
                        ("Nenhum", "nenhum"),
                        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")
                    ], value="nenhum", id="evt-self-switch")
                
                # --- Item Requerido ---
                
                with Horizontal(classes="linha-dupla"):
                    yield Label("Item Requerido:", classes="campo-rotulo")
                    
                    yield Input(placeholder="(vazio = sem requisito)", id="evt-item-requerido", value="")
            
            yield Label("Comandos da Página:", classes="campo-rotulo")
            yield ListView(id="lista-comandos")
            
            with Horizontal(id="evt-botoes"):
                yield Button("+ Adicionar Comando", id="btn-add-cmd", variant="primary")
                yield Button("Cancelar", id="btn-evt-cancelar", variant="error")
                yield Button("Salvar Evento", id="btn-evt-salvar", variant="success")

    def on_mount(self):
        self.atualizar_tela_pagina()

    def atualizar_tela_pagina(self):
        lbl = self.query_one("#lbl-pag-atual", Label)
        lbl.update(f" {self.pagina_atual_idx + 1} / {len(self.paginas)} ")
        
        select_gatilho = self.query_one("#evt-gatilho", Select)
        select_gatilho.value = self.paginas[self.pagina_atual_idx].get("gatilho", "acao_jogador")
        
        # Atualiza a seção de condições com os dados da página atual
        self.atualizar_exibicao_condicoes()
        
        self.atualizar_lista_comandos()

    def _obter_condicoes_pagina_atual(self) -> dict:
        """Retorna o dict de condições da página atual, criando se não existir."""
        pagina = self.paginas[self.pagina_atual_idx]
        if "condicoes" not in pagina:
            pagina["condicoes"] = {}
        return pagina["condicoes"]

    def atualizar_exibicao_condicoes(self):
        """Popula os widgets de condições com os dados da página atual."""
        condicoes = self._obter_condicoes_pagina_atual()
        
        # --- Switches ---
        switches = condicoes.get("switches", [])
        if switches:
            linhas_sw = []
            for i, sw in enumerate(switches):
                val_str = "✅ True" if sw.get("valor", True) else "❌ False"
                linhas_sw.append(f"  [{i}] {sw['nome']} = {val_str}")
            texto_sw = "\n".join(linhas_sw) + "\n  (Clique num switch na lista de comandos para remover)"
        else:
            texto_sw = "  (nenhum)"
        self.query_one("#lista-switches", Static).update(texto_sw)
        
        # --- Variáveis ---
        variaveis = condicoes.get("variaveis", [])
        if variaveis:
            linhas_var = []
            op_simbolos = {
                "maior_ou_igual": ">=", "menor_ou_igual": "<=",
                "igual": "==", "diferente": "!="
            }
            for i, var in enumerate(variaveis):
                op = op_simbolos.get(var.get("operador", "igual"), "==")
                linhas_var.append(f"  [{i}] {var['nome']} {op} {var.get('valor', 0)}")
            texto_var = "\n".join(linhas_var)
        else:
            texto_var = "  (nenhuma)"
        self.query_one("#lista-variaveis", Static).update(texto_var)
        
        # --- Self Switch ---
        self_sw = condicoes.get("self_switch", "nenhum")
        select_ssw = self.query_one("#evt-self-switch", Select)
        select_ssw.value = self_sw or "nenhhum"

        
        # --- Item Requerido ---
        item_req = condicoes.get("item_requerido") or ""
        self.query_one("#evt-item-requerido", Input).value = item_req

    def atualizar_lista_comandos(self):
        lista = self.query_one("#lista-comandos", ListView)
        lista.clear()
        comandos = self.paginas[self.pagina_atual_idx].get("comandos", [])
        for i, cmd in enumerate(comandos):
            dados_str = json.dumps(cmd['dados'], ensure_ascii=False, indent=2)
            texto = f"[{i}] {cmd['tipo']}\n{dados_str}"
            lista.append(ListItem(Label(texto), name=str(i)))

    @on(Select.Changed, "#evt-gatilho")
    def on_gatilho_changed(self, event: Select.Changed):
        if event.value != Select.BLANK:
            self.paginas[self.pagina_atual_idx]["gatilho"] = event.value

    @on(Select.Changed, "#evt-self-switch")
    def on_self_switch_changed(self, event: Select.Changed):
        """Sincroniza o self_switch da página atual quando o Select muda."""
        if event.value == Select.BLANK:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        if event.value == "nenhum":
            condicoes.pop("self_switch", None)
        else:
            condicoes["self_switch"] = event.value

    @on(Input.Changed, "#evt-item-requerido")
    def on_item_requerido_changed(self, event: Input.Changed):
        """Sincroniza o item_requerido da página atual quando o Input muda."""
        condicoes = self._obter_condicoes_pagina_atual()
        valor = event.value.strip()
        if valor:
            condicoes["item_requerido"] = valor
        else:
            condicoes.pop("item_requerido", None)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-evt-cancelar":
            self.dismiss(None)
        elif event.button.id == "btn-pag-ant":
            if self.pagina_atual_idx > 0:
                self.pagina_atual_idx -= 1
                self.atualizar_tela_pagina()
        elif event.button.id == "btn-pag-prox":
            if self.pagina_atual_idx < len(self.paginas) - 1:
                self.pagina_atual_idx += 1
                self.atualizar_tela_pagina()
        elif event.button.id == "btn-add-pag":
            nova_pagina = {
                "id_pagina": len(self.paginas) + 1,
                "condicoes": {},
                "configuracao_visual": {"emoji": self.query_one("#evt-emoji").value},
                "gatilho": "acao_jogador",
                "comandos": []
            }
            self.paginas.append(nova_pagina)
            self.pagina_atual_idx = len(self.paginas) - 1
            self.atualizar_tela_pagina()
        elif event.button.id == "btn-del-pag":
            if len(self.paginas) > 1:
                self.paginas.pop(self.pagina_atual_idx)
                # Reordenar IDs
                for i, p in enumerate(self.paginas):
                    p["id_pagina"] = i + 1
                self.pagina_atual_idx = min(self.pagina_atual_idx, len(self.paginas) - 1)
                self.atualizar_tela_pagina()
            else:
                self.notify("Não é possível deletar a única página!", severity="warning")
        elif event.button.id == "btn-add-cmd":
            self.app.push_screen(AdicionarComandoScreen(), self.ao_adicionar_comando)
        # --- Botões de Condições ---
        elif event.button.id == "btn-add-switch":
            self.app.push_screen(AdicionarSwitchScreen(), self.ao_adicionar_switch)
        elif event.button.id == "btn-add-variavel":
            self.app.push_screen(AdicionarVariavelScreen(), self.ao_adicionar_variavel)
        elif event.button.id and event.button.id.startswith("btn-del-sw-"):
            idx_sw = int(event.button.id.replace("btn-del-sw-", ""))
            self._remover_switch(idx_sw)
        elif event.button.id and event.button.id.startswith("btn-del-var-"):
            idx_var = int(event.button.id.replace("btn-del-var-", ""))
            self._remover_variavel(idx_var)
        elif event.button.id == "btn-evt-salvar":
            nome = self.query_one("#evt-nome").value
            emoji = self.query_one("#evt-emoji").value
            
            parametros = {"paginas": self.paginas}
            
            dados_retorno = {
                "nome": nome,
                "emoji": emoji,
                "event_type": "evento_custom", 
                "parametros": parametros
            }
            if "id" in self.dados_existentes:
                dados_retorno["id"] = self.dados_existentes["id"]
                
            self.dismiss(dados_retorno)

    def ao_adicionar_comando(self, novo_comando):
        if novo_comando:
            self.paginas[self.pagina_atual_idx].setdefault("comandos", []).append(novo_comando)
            self.atualizar_lista_comandos()

    # ==========================================
    # MÉTODOS DE GERENCIAMENTO DE CONDIÇÕES
    # ==========================================
    def ao_adicionar_switch(self, dados_switch: dict | None):
        """Callback do modal AdicionarSwitchScreen."""
        if dados_switch is None:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        condicoes.setdefault("switches", []).append(dados_switch)
        self.atualizar_exibicao_condicoes()
        self.notify(f"Switch '{dados_switch['nome']}' adicionado!")

    def ao_adicionar_variavel(self, dados_variavel: dict | None):
        """Callback do modal AdicionarVariavelScreen."""
        if dados_variavel is None:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        condicoes.setdefault("variaveis", []).append(dados_variavel)
        self.atualizar_exibicao_condicoes()
        self.notify(f"Variável '{dados_variavel['nome']}' adicionada!")

    def _remover_switch(self, idx: int):
        """Remove um switch pelo índice da lista."""
        condicoes = self._obter_condicoes_pagina_atual()
        switches = condicoes.get("switches", [])
        if 0 <= idx < len(switches):
            removido = switches.pop(idx)
            self.atualizar_exibicao_condicoes()
            self.notify(f"Switch '{removido['nome']}' removido.")

    def _remover_variavel(self, idx: int):
        """Remove uma variável pelo índice da lista."""
        condicoes = self._obter_condicoes_pagina_atual()
        variaveis = condicoes.get("variaveis", [])
        if 0 <= idx < len(variaveis):
            removido = variaveis.pop(idx)
            self.atualizar_exibicao_condicoes()
            self.notify(f"Variável '{removido['nome']}' removida.")

    def ao_salvar_edicao_comando(self, novo_comando, idx):
        if novo_comando:
            # Mantemos os ramos caso seja bifurcação para não perder se não editou
            if novo_comando["tipo"] == self.paginas[self.pagina_atual_idx]["comandos"][idx]["tipo"]:
                if "ramos" in self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]:
                    novo_comando["dados"]["ramos"] = self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]["ramos"]
            self.paginas[self.pagina_atual_idx]["comandos"][idx] = novo_comando
            self.atualizar_lista_comandos()

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "lista-comandos":
            idx = int(event.item.name)
            cmd = self.paginas[self.pagina_atual_idx]["comandos"][idx]
            self.app.push_screen(AcoesComandoScreen(cmd), lambda acao: self.ao_acao_comando(acao, idx))

    def ao_acao_comando(self, acao: str, idx: int):
        if not acao: return
        comandos = self.paginas[self.pagina_atual_idx]["comandos"]
        if acao == "excluir":
            comandos.pop(idx)
            self.atualizar_lista_comandos()
        elif acao == "editar":
            cmd = comandos[idx]
            self.app.push_screen(AdicionarComandoScreen(cmd), lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith("editar_ramo_"):
            ramo_nome = acao.replace("editar_ramo_", "")
            cmd = comandos[idx]
            ramos = cmd["dados"].setdefault("ramos", {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            self.app.push_screen(RamoEditorScreen(ramo_nome, ramo_cmds), lambda novos_cmds: self.ao_salvar_ramo(novos_cmds, idx, ramo_nome))

    def ao_salvar_ramo(self, novos_cmds, idx, ramo_nome):
        if novos_cmds is not None:
            self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]["ramos"][ramo_nome] = novos_cmds
            self.atualizar_lista_comandos()


# ==============================================================================
# SUB-MODAL: ADICIONAR SWITCH À CONDIÇÃO
# ==============================================================================
class AdicionarSwitchScreen(ModalScreen[dict]):
    """Modal simples para adicionar uma condição de Switch a uma página."""

    def compose(self):
        with Vertical(id="add-cmd-caixa"):
            yield Label("🔀 Adicionar Condição de Switch", classes="titulo-secao")
            yield Label("Nome do Switch:")
            yield Input(placeholder="Ex: missao_guarda_ativa", id="sw-nome")
            yield Label("Valor Esperado:")
            yield Select([
                ("Ligado (True)", "true"),
                ("Desligado (False)", "false")
            ], value="true", id="sw-valor")
            with Horizontal(id="evt-botoes"):
                yield Button("Cancelar", id="btn-cancel", variant="error")
                yield Button("Confirmar", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            nome = self.query_one("#sw-nome", Input).value.strip()
            if not nome:
                self.notify("Preencha o nome do switch!", severity="error")
                return
            valor = self.query_one("#sw-valor", Select).value == "true"
            self.dismiss({"nome": nome, "valor": valor})


# ==============================================================================
# SUB-MODAL: ADICIONAR VARIÁVEL À CONDIÇÃO
# ==============================================================================
class AdicionarVariavelScreen(ModalScreen[dict]):
    """Modal simples para adicionar uma condição de Variável numérica a uma página."""

    def compose(self):
        with Vertical(id="add-cmd-caixa"):
            yield Label("📊 Adicionar Condição de Variável", classes="titulo-secao")
            yield Label("Nome da Variável:")
            yield Input(placeholder="Ex: reputacao", id="var-nome")
            yield Label("Operador:")
            yield Select([
                ("Maior ou Igual (>=)", "maior_ou_igual"),
                ("Menor ou Igual (<=)", "menor_ou_igual"),
                ("Igual (==)", "igual"),
                ("Diferente (!=)", "diferente")
            ], value="maior_ou_igual", id="var-operador")
            yield Label("Valor:")
            yield Input(placeholder="Ex: 15", id="var-valor", value="0")
            with Horizontal(id="evt-botoes"):
                yield Button("Cancelar", id="btn-cancel", variant="error")
                yield Button("Confirmar", id="btn-save", variant="success")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            nome = self.query_one("#var-nome", Input).value.strip()
            if not nome:
                self.notify("Preencha o nome da variável!", severity="error")
                return
            try:
                valor = int(self.query_one("#var-valor", Input).value)
            except ValueError:
                self.notify("O valor deve ser numérico!", severity="error")
                return
            operador = self.query_one("#var-operador", Select).value
            if operador == Select.BLANK:
                self.notify("Selecione um operador!", severity="error")
                return
            self.dismiss({"nome": nome, "operador": operador, "valor": valor})


class AdicionarComandoScreen(ModalScreen[dict]):
    """Sub-formulário para gerar comandos baseados no tipo selecionado."""
    def __init__(self, comando_existente: dict = None):
        super().__init__()
        self.comando_existente = comando_existente

    def compose(self):
        with Vertical(id="add-cmd-caixa"):
            yield Label("Escolha o tipo de Comando", classes="titulo-secao")
            yield Select([
                ("Mensagem no prompt (Texto)", "mensagem"),
                ("Notificação na tela (Texto)", "noficação"),
                ("Teleporte (Mudar Mapa/Posição)", "teleporte"),
                ("Inventário (Add/Sub)", "mudar_inventario"),
                ("Status do Herói (HP/MP)", "mudar_status_heroi"),
                ("Bifurcação Condicional (Opções)", "bifurcacao_condicional"),
                ("Variável (Valor)", "controle_variavel"),
                ("Switch (Liga/Desliga)", "controle_switch"),
                ("Self Switch (Local)", "controle_self_switch")
            ], id="cmd-tipo")
            yield Container(id="cmd-form-container")
            with Horizontal(id="evt-botoes"):
                yield Button("Cancelar", id="btn-cancel", variant="error")
                yield Button("Confirmar", id="btn-save", variant="success")

    def on_mount(self):
        if self.comando_existente:
            self.query_one("#cmd-tipo", Select).value = self.comando_existente["tipo"]

    @on(Select.Changed, "#cmd-tipo")
    def on_tipo_changed(self, event: Select.Changed):
        container = self.query_one("#cmd-form-container")
        container.remove_children()
        tipo = event.value
        
        dados = {}
        if self.comando_existente and self.comando_existente["tipo"] == tipo:
            dados = self.comando_existente.get("dados", {})
            
        if tipo == "mensagem":
            container.mount(Input(placeholder="Texto da mensagem (Use tags [color] se quiser)", id="cmd-msg-texto", value=dados.get("texto", "")))
        elif tipo == "notificação":
            container.mount(Input(placeholder="Texto da notificação (Use tags [color] se quiser)", id="cmd-notif-texto", value=dados.get("texto", "")))

        elif tipo == "teleporte":
            container.mount(Input(placeholder="ID do Mapa Destino", id="cmd-tel-mapa", value=str(dados.get("mapa_id", ""))))
            container.mount(Input(placeholder="Coordenada X (Coluna)", id="cmd-tel-x", value=str(dados.get("pos_x", ""))))
            container.mount(Input(placeholder="Coordenada Y (Linha)", id="cmd-tel-y", value=str(dados.get("pos_y", ""))))
        elif tipo == "mudar_inventario":
            container.mount(Input(placeholder="Nome exato do Item (ex: pocao_cura)", id="cmd-inv-item", value=dados.get("item", "")))
            container.mount(Select([("Adicionar", "add"), ("Remover", "sub")], value=dados.get("operacao", "add"), id="cmd-inv-op"))
            container.mount(Input(placeholder="Quantidade (ex: 1)", value=str(dados.get("quantidade", 1)), id="cmd-inv-qtd"))
        elif tipo == "mudar_status_heroi":
            container.mount(Select([("Vida (HP)", "hp"), ("Mana (MP)", "mp")], value=dados.get("parametro", "hp"), id="cmd-stat-param"))
            container.mount(Select([("Recuperar (Add)", "add"), ("Causar Dano (Sub)", "sub")], value=dados.get("operacao", "add"), id="cmd-stat-op"))
            container.mount(Input(placeholder="Valor Numérico", value=str(dados.get("valor", 10)), id="cmd-stat-valor"))
        elif tipo == "bifurcacao_condicional":
            container.mount(Input(placeholder="Pergunta ao Jogador?", id="cmd-bif-pergunta", value=dados.get("pergunta", "")))
            opcoes = dados.get("opcoes", ["", ""])
            op1 = opcoes[0] if len(opcoes) > 0 else ""
            op2 = opcoes[1] if len(opcoes) > 1 else ""
            container.mount(Input(placeholder="Opção 1 (ex: Sim)", id="cmd-bif-op1", value=op1))
            container.mount(Input(placeholder="Opção 2 (ex: Não)", id="cmd-bif-op2", value=op2))
        elif tipo == "controle_switch":
            container.mount(Input(placeholder="Nome da Switch", id="cmd-sw-nome", value=dados.get("nome", "")))
            val_str = "true" if dados.get("valor", True) else "false"
            container.mount(Select([("Ligar (True)", "true"), ("Desligar (False)", "false")], value=val_str, id="cmd-sw-valor"))
        elif tipo == "controle_self_switch":
            container.mount(Select([("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")], value=dados.get("letra", "A"), id="cmd-ssw-letra"))
            val_str = "true" if dados.get("valor", True) else "false"
            container.mount(Select([("Ligar (True)", "true"), ("Desligar (False)", "false")], value=val_str, id="cmd-ssw-valor"))
        elif tipo == "controle_variavel":
            container.mount(Input(placeholder="Nome da Variável", id="cmd-variavel-nome", value=dados.get("nome", "")))
            val_str = self.query_one("#cmd-variavel-nome").value 
            container.mount(Input(placeholder="Valor atribuido", id="cmd-variavel-valor", value=dados.get("valor", "")))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            tipo = self.query_one("#cmd-tipo").value
            if not tipo or tipo == Select.BLANK:
                return
                
            comando = {"tipo": tipo, "dados": {}}
            try:
                if tipo == "mensagem":
                    comando["dados"]["texto"] = self.query_one("#cmd-msg-texto").value
                elif tipo == "notificação":
                    comando["dados"]["texto"] = self.query_one("#cmd-notif-texto").value
                elif tipo == "teleporte":
                    comando["dados"]["mapa_id"] = int(self.query_one("#cmd-tel-mapa").value)
                    comando["dados"]["pos_x"] = int(self.query_one("#cmd-tel-x").value)
                    comando["dados"]["pos_y"] = int(self.query_one("#cmd-tel-y").value)
                elif tipo == "mudar_inventario":
                    comando["dados"]["item"] = self.query_one("#cmd-inv-item").value
                    comando["dados"]["operacao"] = self.query_one("#cmd-inv-op").value
                    comando["dados"]["quantidade"] = int(self.query_one("#cmd-inv-qtd").value)
                elif tipo == "mudar_status_heroi":
                    comando["dados"]["parametro"] = self.query_one("#cmd-stat-param").value
                    comando["dados"]["operacao"] = self.query_one("#cmd-stat-op").value
                    comando["dados"]["valor"] = int(self.query_one("#cmd-stat-valor").value)
                elif tipo == "bifurcacao_condicional":
                    pergunta = self.query_one("#cmd-bif-pergunta").value
                    op1 = self.query_one("#cmd-bif-op1").value
                    op2 = self.query_one("#cmd-bif-op2").value
                    comando["dados"]["pergunta"] = pergunta
                    opcoes = []
                    ramos = {}
                    if op1:
                        opcoes.append(op1)
                        ramos[op1] = []
                    if op2:
                        opcoes.append(op2)
                        ramos[op2] = []
                    comando["dados"]["opcoes"] = opcoes
                    comando["dados"]["ramos"] = ramos
                elif tipo == "controle_switch":
                    comando["dados"]["nome"] = self.query_one("#cmd-sw-nome").value
                    comando["dados"]["valor"] = self.query_one("#cmd-sw-valor").value == "true"
                elif tipo == "controle_self_switch":
                    comando["dados"]["letra"] = self.query_one("#cmd-ssw-letra").value
                    comando["dados"]["valor"] = self.query_one("#cmd-ssw-valor").value == "true"
                elif tipo == "controle_variavel":
                    comando["dados"]["nome"] = self.query_one("#cmd-variavel-nome").value
                    comando["dados"]["valor"] = self.query_one("#cmd-variavel-valor").value

                
            except Exception as e:
                self.notify(f"Erro ao salvar comando: Preencha os campos corretamente", severity="error")
                return

            self.dismiss(comando)


class AcoesComandoScreen(ModalScreen[str]):
    """Menu contextual ao clicar num comando."""
    def __init__(self, comando: dict):
        super().__init__()
        self.comando = comando
        
    def compose(self):
        import unicodedata
        with Vertical(id="acoes-cmd-caixa"):
            yield Label(f"Ações: {self.comando['tipo']}", classes="titulo-secao")
            yield Button("Editar Comando", id="btn-editar", variant="success")
            if self.comando["tipo"] == "bifurcacao_condicional":
                for op in self.comando["dados"].get("opcoes", []):
                    id_op = op.replace(' ', '_').replace(',', '-').replace('.', '')
                    id_op = unicodedata.normalize("NFD", id_op)
                    id_op = id_op.encode("ASCII", "ignore").decode("ASCII")
                    yield Button(f"Editar Ramo: '{op}'", id=f"ramo_{id_op}", variant="primary")
            yield Button("Excluir Comando", id="btn-excluir", variant="error")
            yield Button("Voltar", id="btn-cancelar")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancelar":
            self.dismiss(None)
        elif event.button.id == "btn-excluir":
            self.dismiss("excluir")
        elif event.button.id == "btn-editar":
            self.dismiss("editar")
        elif event.button.id.startswith("ramo_"):
            ramo_nome = event.button.id.replace("ramo_", "")
            self.dismiss(f"editar_ramo_{ramo_nome}")


class RamoEditorScreen(ModalScreen[list]):
    """Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou Não)."""
    def __init__(self, nome_ramo: str, comandos: list):
        super().__init__()
        self.nome_ramo = nome_ramo
        self.comandos = copy.deepcopy(comandos)
        
    def compose(self):
        with Vertical(id="evt-caixa-full"):
            yield Label(f"🌿 Ramo de Escolha: '{self.nome_ramo}'", classes="titulo-secao")
            yield ListView(id="lista-comandos-ramo")
            with Horizontal(id="evt-botoes"):
                yield Button("+ Adicionar Comando", id="btn-add-cmd", variant="primary")
                yield Button("Concluir Ramo", id="btn-salvar-ramo", variant="success")

    def on_mount(self):
        self.atualizar_lista()

    def atualizar_lista(self):
        lista = self.query_one("#lista-comandos-ramo", ListView)
        lista.clear()
        for i, cmd in enumerate(self.comandos):
            dados_str = json.dumps(cmd['dados'], ensure_ascii=False, indent=2)
            texto = f"[{i}] {cmd['tipo']}\n{dados_str}"
            lista.append(ListItem(Label(texto), name=str(i)))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-add-cmd":
            self.app.push_screen(AdicionarComandoScreen(), self.ao_adicionar_comando)
        elif event.button.id == "btn-salvar-ramo":
            self.dismiss(self.comandos)

    def ao_adicionar_comando(self, novo_comando):
        if novo_comando:
            self.comandos.append(novo_comando)
            self.atualizar_lista()
            
    def on_list_view_selected(self, event: ListView.Selected):
        idx = int(event.item.name)
        cmd = self.comandos[idx]
        self.app.push_screen(AcoesComandoScreen(cmd), lambda acao: self.ao_acao_comando(acao, idx))

    def ao_acao_comando(self, acao: str, idx: int):
        if not acao: return
        if acao == "excluir":
            self.comandos.pop(idx)
            self.atualizar_lista()
        elif acao == "editar":
            cmd = self.comandos[idx]
            self.app.push_screen(AdicionarComandoScreen(cmd), lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith("editar_ramo_"):
            ramo_nome = acao.replace("editar_ramo_", "")
            cmd = self.comandos[idx]
            ramos = cmd["dados"].setdefault("ramos", {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            # RECURSÃO: Chama outro RamoEditorScreen por cima deste!
            self.app.push_screen(RamoEditorScreen(ramo_nome, ramo_cmds), lambda novos_cmds: self.ao_salvar_subramo(novos_cmds, idx, ramo_nome))

    def ao_salvar_edicao_comando(self, novo_comando, idx):
        if novo_comando:
            if novo_comando["tipo"] == self.comandos[idx]["tipo"]:
                if "ramos" in self.comandos[idx]["dados"]:
                    novo_comando["dados"]["ramos"] = self.comandos[idx]["dados"]["ramos"]
            self.comandos[idx] = novo_comando
            self.atualizar_lista()

    def ao_salvar_subramo(self, novos_cmds, idx, ramo_nome):
        if novos_cmds is not None:
            self.comandos[idx]["dados"]["ramos"][ramo_nome] = novos_cmds
            self.atualizar_lista()


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
