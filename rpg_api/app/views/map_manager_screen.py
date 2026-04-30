# app/screens/map_manager_screen.py

from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, Tree, Static, Label, Button, Input, Select
from textual.containers import Horizontal, Vertical, Container
from textual.events import Click
from textual.message import Message
from textual import on
from app.core.mapas import GestorDeMapas
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB


class MapaInterativo(Static):
    """
    Componente customizado que exibe o mapa e captura cliques do rato.
    """
    class Clicado(Message):
        """Mensagem (Evento) enviada quando o mapa é clicado."""
        def __init__(self, linha: int, coluna: int):
            self.linha = linha
            self.coluna = coluna
            super().__init__()

    def on_click(self, event: Click) -> None:
        """Calcula a posição do clique e avisa a tela principal."""
        # event.y é a linha (vertical)
        # event.x é a coluna (horizontal). 
        # Como os emojis costumam ocupar 2 colunas no terminal, dividimos por 2!
        linha = event.y
        coluna = event.x // 2 
        
        # Dispara o nosso evento customizado
        self.post_message(self.Clicado(linha, coluna))
        

class MapManagerScreen(Screen):
    """
    Tela principal do Gerenciador de Mapas.
    Responsável por exibir as ferramentas de edição, a paleta e o mapa em si.
    """

    CSS = """
    /* --- BARRA SUPERIOR (NOSSO HEADER CUSTOMIZADO) --- */
    #top-menu {
        layout: horizontal;
        height: 4; /* 3 linhas para os botões + 1 linha para a borda inferior */
        border-bottom: solid green;
        padding: 0 1;
    }

    #top-menu Button {
        width: auto; /* O botão cresce o suficiente para caber o nome */
        height: 3;   /* Altura padrão e perfeita para botões no Textual */
        margin-right: 1; /* Apenas uma margem por fora, sem padding por dentro */
        min-width: 10; /* Garante que não fiquem pequenos demais */
    }

    /* O botão de fechar fica alinhado à extrema direita */
    #btn-fechar {
        dock: right;
        margin-right: 1;
        padding: 1;
        width: 10%;
        height: 10%;        
    }

    /* --- RESTANTE DO LAYOUT --- */
    #main-container {
        layout: horizontal;
        width: 100%;
        height: 100%;
    }

    #sidebar {
        width: 25%;
        height: 100%;
        border-right: solid green;
    }

    #paleta-container {
        height: 50%;
        border-bottom: dashed green;
        padding: 1;
    }

    #arvore-container {
        height: 50%;
        padding: 1;
    }

    #map-area {
        width: 75%;
        height: 100%;
        padding: 1;
        align: center middle; /* Centraliza o conteúdo no meio da tela */
    }
    
    #lbl-tile-atual {
        text-style: bold;
        color: yellow;
        margin-bottom: 1;
    }
    
    #grade-paleta {
        layout: grid;
        grid-size: 5; /* 5 colunas de botões */
        grid-gutter: 1; /* Espaço entre os botões */
    }
    
    .btn-paleta {
        min-width: 4;
        height: 1;
        border: none;
        padding: 0;
    }
    """
    def __init__(self):
        super().__init__()
        self.mapa_atual_matriz = None
        self.mapa_atual_dados = None
        # 🧠 Novo Estado: O nosso "pincel" de pintura
        self.tile_selecionado = "  "

    def compose(self) -> ComposeResult:
        # 1. Nossa Barra Superior (Removido o Header nativo para não haver conflitos)
        with Horizontal(id="top-menu"):
            yield Button("Menu", id="btn-menu")
            # Adicionamos aqui os botões vitais para a nossa lógica funcionar
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
                    
                    # Grade com vários botões de tiles
                    with Container(id="grade-paleta"):
                        tiles_disponiveis = ["  ", "🔲", "🔷", "🔵", "🍺","🌲", "🌳", "🌴", "🍄", "🌻", "🚪", "💀", "⛺"]
                        # for tile in tiles_disponiveis:
                        #     yield Button(tile, classes="btn-paleta", id=f"tile-{tile}")
                        for i, tile in enumerate(tiles_disponiveis):
                            # O 'id' agora fica seguro: "tile-0", "tile-1", etc.
                            # O texto visual do botão continua a ser o emoji (tile).
                            yield Button(tile, classes="btn-paleta", id=f"tile-{i}")
                    
                with Container(id="arvore-container"):
                    yield Label("📂 Mapas", classes="titulo-secao")
                    yield Tree("Mundo")

            with Container(id="map-area"):
                yield Label("Mapa: Mundo", id="mapa-titulo")
                # --- SUBSTITUÍMOS O STATIC PELO NOSSO NOVO COMPONENTE ---
                yield MapaInterativo("Matriz do Mapa aparecerá aqui...", id="mapa-view")
        
        yield Footer()

# --- NOVA FUNÇÃO DE PINTURA ---
    @on(MapaInterativo.Clicado)
    def pintar_mapa(self, event: MapaInterativo.Clicado):
        """Escuta o evento do mapa e aplica o tile selecionado na matriz."""
        if self.mapa_atual_matriz is None:
            return # Não faz nada se não houver mapa gerado
            
        linha = event.linha
        coluna = event.coluna
        
        # Proteção: Verifica se o clique não foi fora dos limites da matriz
        if 0 <= linha < len(self.mapa_atual_matriz):
            if 0 <= coluna < len(self.mapa_atual_matriz[0]):
                
                # 1. Altera o dado na memória
                self.mapa_atual_matriz[linha][coluna] = self.tile_selecionado
                
                # 2. Manda redesenhar a tela para refletir a mudança
                self.exibir_mapa_na_tela()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Gerencia os cliques na tela principal."""
        if event.button.has_class("btn-paleta"):
            # O texto do botão (label) é o nosso novo tile!
            self.tile_selecionado = str(event.button.label)
            # Atualiza o aviso visual na tela
            self.query_one("#lbl-tile-atual", Label).update(f"Selecionado: {self.tile_selecionado}")
            return # Termina aqui
        
        if event.button.id == "btn-fechar":
            self.dismiss()
            
        elif event.button.id == "btn-novo":
            # Abre o Modal e diz ao Textual para chamar a função 'ao_terminar_form' quando fechar
            self.app.push_screen(NovoMapaFormScreen(), self.ao_terminar_form)

        elif event.button.id == "btn-salvar":
            self.salvar_mapa_no_banco()
    

    def ao_terminar_form(self, dados_do_form: dict | None):
        """Callback acionado quando o usuário clica em 'Gerar' ou 'Cancelar' no form."""
        if dados_do_form is None:
            return # O usuário clicou em Cancelar

        # 1. Guarda os dados na memória temporária do sistema
        self.mapa_atual_dados = dados_do_form
        
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
        

    def exibir_mapa_na_tela(self):
        """Converte a matriz numa string visível e joga na tela."""
        if self.mapa_atual_matriz:
            # Junta as listas da matriz num blocão de texto usando quebra de linha (\n)
            texto_mapa = "\n".join(["".join(linha) for linha in self.mapa_atual_matriz])
            
            # Atualiza os widgets na tela
            self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.mapa_atual_dados['nome']}")
            self.query_one("#mapa-view", Static).update(texto_mapa)

    def salvar_mapa_no_banco(self):
        """Pega o que está na memória e salva de verdade no Banco de Dados."""
        if self.mapa_atual_matriz is None or self.mapa_atual_dados is None:
            self.notify("Não há nenhum mapa gerado para salvar!", severity="warning")
            return

        # Abre uma sessão com o banco de dados
        with SessionLocal() as db:
            novo_mapa = MapaDB(
                nome=self.mapa_atual_dados["nome"],
                tipo=self.mapa_atual_dados["tipo"],
                largura=self.mapa_atual_dados["largura"],
                altura=self.mapa_atual_dados["altura"],
                mapa_em_si=self.mapa_atual_matriz,
                configs={} # Podemos implementar configurações avançadas depois
            )
            db.add(novo_mapa)
            db.commit()
            
            self.notify(f"Mapa '{self.mapa_atual_dados['nome']}' guardado no banco com sucesso!")
            

class NovoMapaFormScreen(ModalScreen[dict]):
    """
    Tela flutuante (Modal) para preenchimento das propriedades do novo mapa.
    Retorna um dicionário com os dados preenchidos quando fechada.
    """

    # O CSS escurece o fundo e centraliza a nossa "caixa" de formulário
    CSS = """
    NovoMapaFormScreen {
        align: center middle;
        background: $background 50%;
    }
    #form-caixa {
        width: 50; /* Aumentei um pouco a largura para caberem mais campos */
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid green;
    }
    
    /* Organização dos campos lado a lado para economizar espaço vertical */
    .linha-dupla {
        layout: horizontal;
        height: auto;
    }
    .linha-dupla Input {
        width: 1fr; /* Divide o espaço igualmente */
    }

    #form-botoes {
        layout: horizontal;
        align: center middle;
        margin-top: 1;
        height: auto;
        width: 100%;
    }
    #form-botoes Button {
        margin: 0 1;
        width: auto; /* O botão cresce o suficiente para caber o nome */
        height: 3;   /* Altura padrão e perfeita para botões no Textual */
        margin-right: 1; /* Apenas uma margem por fora, sem padding por dentro */
        min-width: 10; /* Garante que não fiquem pequenos demais */
    }
    
    /* As caixas de configuração dinâmicas */
    .caixa-config {
        height: auto;
        border: round grey;
        padding: 1;
        margin-top: 1;
    }
    """

    def compose(self):
        with Vertical(id="form-caixa"):
            yield Label("✨ Gerar Novo Mapa", classes="titulo-secao")
            
            # --- CAMPOS GERAIS (Sempre visíveis) ---
            yield Input(placeholder="Nome do Mapa", id="input-nome")
            yield Select((("Masmorra", "masmorra"), ("Caverna", "caverna")), prompt="Tipo de Mapa", id="select-tipo", value="masmorra")
            
            with Horizontal(classes="linha-dupla"):
                yield Input(placeholder="Largura (ex: 40)", id="input-largura")
                yield Input(placeholder="Altura (ex: 20)", id="input-altura")
                
            with Horizontal(classes="linha-dupla"):
                yield Input(placeholder="Tile Parede", id="input-tile-parede", value="🔲")
                yield Input(placeholder="Tile Chão", id="input-tile-chao", value="  ")

            # --- CAIXAS DE CONFIGURAÇÃO ESPECÍFICAS ---
            
            # 1. Configurações de Masmorra
            with Vertical(id="configs-masmorra", classes="caixa-config"):
                yield Label("⚙️ Configurações da Masmorra")
                yield Input(placeholder="Máx de Salas", id="input-max-salas", value="25")
                with Horizontal(classes="linha-dupla"):
                    yield Input(placeholder="Tam. Mínimo Sala", id="input-tam-min", value="3")
                    yield Input(placeholder="Tam. Máximo Sala", id="input-tam-max", value="15")

            # 2. Configurações de Caverna (Inicialmente oculta)
            with Vertical(id="configs-caverna", classes="caixa-config"):
                yield Label("⚙️ Configurações da Caverna")
                yield Input(placeholder="Taxa de Preenchimento %", id="input-taxa-caverna", value="45")
                # Futuramente você pode adicionar mais configurações de caverna aqui

            # --- BOTÕES DE AÇÃO ---
            with Horizontal(id="form-botoes"):
                yield Button("Cancelar", id="btn-cancelar", variant="error")
                yield Button("Gerar", id="btn-gerar", variant="success")

    def on_mount(self):
        """Executado quando a tela é carregada. Garante que apenas a caixa certa está visível."""
        self.atualizar_visibilidade_configs("masmorra")

    @on(Select.Changed, "#select-tipo")
    def on_select_changed(self, event: Select.Changed) -> None:
        """
        Evento disparado SEMPRE que o utilizador escolhe uma opção diferente no Select.
        """
        if event.value != Select.BLANK:
            self.atualizar_visibilidade_configs(str(event.value))

    def atualizar_visibilidade_configs(self, tipo_selecionado: str):
        """Esconde todas as caixas de configuração e mostra apenas a do tipo selecionado."""
        # Esconde todas
        self.query_one("#configs-masmorra").display = False
        self.query_one("#configs-caverna").display = False
        
        # Mostra a correta
        if tipo_selecionado == "masmorra":
            self.query_one("#configs-masmorra").display = True
        elif tipo_selecionado == "caverna":
            self.query_one("#configs-caverna").display = True

    def on_button_pressed(self, event: Button.Pressed):
        """Captura os cliques dos botões."""
        if event.button.id == "btn-cancelar":
            self.dismiss(None) 
            
        elif event.button.id == "btn-gerar":
            nome = self.query_one("#input-nome").value
            tipo = self.query_one("#select-tipo").value
            
            if not nome or tipo == Select.BLANK:
                self.notify("Preencha o nome e escolha um tipo!", severity="error")
                return

            # Cria o dicionário base
            dados_mapa = {
                "nome": nome,
                "tipo": str(tipo),
                "largura": int(self.query_one("#input-largura").value or 30),
                "altura": int(self.query_one("#input-altura").value or 30),
                "tile_parede": self.query_one("#input-tile-parede").value,
                "tile_chao": self.query_one("#input-tile-chao").value,
                "configs": {}
            }
            
            # Adiciona as configurações dinâmicas dependendo do tipo
            if tipo == "masmorra":
                dados_mapa["configs"] = {
                    "max_salas": int(self.query_one("#input-max-salas").value),
                    "tam_min_sala": int(self.query_one("#input-tam-min").value),
                    "tam_max_sala": int(self.query_one("#input-tam-max").value)
                }
            elif tipo == "caverna":
                dados_mapa["configs"] = {
                    "taxa_preenchimento": int(self.query_one("#input-taxa-caverna").value)
                }
            
            # Fecha a tela passando os dados completos de volta!
            self.dismiss(dados_mapa)