# app/screens/map_manager_screen.py

import copy
from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Footer, Header, Tree, Static, Label, Button, Input, Select
from textual.containers import Horizontal, Vertical, Container
from textual.message import Message
from textual import on
from textual.events import MouseDown, MouseUp, MouseMove
from app.core.mapas import GestorDeMapas
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from rich.text import Text

CSS_PATH = "styles.css"

def padronizar_largura_tile(tile_string: str) -> str:
    """
    Verifica a largura visual do caractere no terminal.
    Se for um caractere magro (tamanho 1), adiciona um espaço para ficar com tamanho 2.
    """
    if Text(tile_string).cell_len == 1:
        return f"{tile_string}"
    return tile_string

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
            
    # class Clicado(Message):
    #     """Mensagem (Evento) enviada quando o mapa é clicado."""
    #     def __init__(self, linha: int, coluna: int):
    #         self.linha = linha
    #         self.coluna = coluna
    #         super().__init__()

    # def on_click(self, event: Click) -> None:
    #     """Calcula a posição do clique e avisa a tela principal."""
    #     # Como os emojis costumam ocupar 2 colunas no terminal, dividimos por 2!
    #     linha = event.y
    #     coluna = event.x // 2 
    #     self.post_message(self.Clicado(linha, coluna))
        

class MapManagerScreen(Screen):
    """
    Tela principal do Gerenciador de Mapas.
    Responsável por exibir as ferramentas de edição, a paleta e o mapa em si.
    """
    CSS_PATH = CSS_PATH 
    
    def __init__(self):
        super().__init__()
        self.mapa_atual_matriz = None
        self.mapa_atual_dados = None
        self.tile_selecionado = "  "
        self.tem_alteracoes = False
        self.id_mapa_na_agulha = None
        
        # 🧠 NOVA MEMÓRIA: Máquina do Tempo
        self.historico_desfazer = []
        self.historico_refazer = []

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
                        yield Button(" Desfazer", id="btn-desfazer", classes="btn-pequeno")
                        yield Button(" Refazer", id="btn-refazer", classes="btn-pequeno")
                    
                    with Container(id="grade-paleta"):
                        tiles_disponiveis = ["  ", "🔲", "🟫", "🟦", "🏰","🌲",
                                             "🌳", "🌴", "🌵", "🍄", "🌻", "🚪",
                                             "💀", "⛺", "🪨", "⛲", "🔥", "🕋",
                                             "💎", "🧊", "📦", "📖", "🪑", "🪦",
                                             "🌭", "🍔", "🍕", "🍺", "🍫", "🌹"]
                                             
                        for i, tile in enumerate(tiles_disponiveis):
                            yield Button(tile, classes="btn-paleta", id=f"tile-{i}")
                    
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
            todos_mapas = db.query(MapaDB).all()

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
        """Puxa os dados reais do banco e exibe na tela principal."""
        with SessionLocal() as db:
            mapa_db = db.query(MapaDB).filter(MapaDB.id == mapa_id).first()
            if not mapa_db:
                return

            # Alimenta a memória do sistema
            self.mapa_atual_matriz = mapa_db.mapa_em_si
            self.mapa_atual_dados = {
                "id": mapa_db.id,
                "nome": mapa_db.nome,
                "tipo": mapa_db.tipo,
                "mapa_pai_id": mapa_db.mapa_pai_id,
                "largura": mapa_db.largura,
                "altura": mapa_db.altura,
            }
            
            # Limpa o estado
            self.tem_alteracoes = False
            self.id_mapa_na_agulha = None
            
            # Exibe!
            self.exibir_mapa_na_tela()
            self.notify(f"Mapa '{mapa_db.nome}' carregado!")

# --- FUNÇÃO DE PINTURA ---
    # @on(MapaInterativo.Clicado)
    # def pintar_mapa(self, event: MapaInterativo.Clicado):
    #     """Escuta o evento do mapa e aplica o tile selecionado na matriz."""
    #     if self.mapa_atual_matriz is None: return
         
    #     linha, coluna = event.linha, event.coluna
        
    #     # Proteção: Verifica se o clique não foi fora dos limites da matriz
    #     if 0 <= linha < len(self.mapa_atual_matriz):
    #         if 0 <= coluna < len(self.mapa_atual_matriz[0]):
    #             # 1. Altera o dado na memória
    #             self.mapa_atual_matriz[linha][coluna] = self.tile_selecionado
    #             self.tem_alteracoes = True
    #             # 2. Manda redesenhar a tela para refletir a mudança
    #             self.exibir_mapa_na_tela()

    
    def salvar_estado_historico(self):
        """Tira uma fotografia à matriz atual antes de a alterarmos."""
        # Limitamos o histórico a 20 passos para não consumir muita RAM
        if len(self.historico_desfazer) > 20:
            self.historico_desfazer.pop(0)
            
        # O deepcopy entra em todas as listas e sub-listas criando clones independentes
        copia_matriz = copy.deepcopy(self.mapa_atual_matriz)
        self.historico_desfazer.append(copia_matriz)
        
        # Sempre que começamos a pintar algo novo, o "futuro" do refazer é apagado
        self.historico_refazer.clear()

    @on(MapaInterativo.Pintar)
    def processar_pintura(self, event: MapaInterativo.Pintar):
        """Pinta os blocos à medida que o mouse é arrastado."""
        if self.mapa_atual_matriz is None:
            return 
            
        linha, coluna = event.linha, event.coluna
        
        # Verifica se o mouse está dentro dos limites da grelha
        if 0 <= linha < len(self.mapa_atual_matriz) and 0 <= coluna < len(self.mapa_atual_matriz[0]):
            
            # Se for o primeiro bloco que tocamos ao apertar o botão, guardamos a foto!
            if event.inicio_de_traco:
                self.salvar_estado_historico()

            # Evita repintar o mesmo bloco se o mouse estiver a passar por cima dele repetidamente
            if self.mapa_atual_matriz[linha][coluna] != self.tile_selecionado:
                self.mapa_atual_matriz[linha][coluna] = self.tile_selecionado
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
        estado_atual = copy.deepcopy(self.mapa_atual_matriz)
        self.historico_refazer.append(estado_atual)
        
        # 2. Puxa a foto antiga
        estado_anterior = self.historico_desfazer.pop()
        self.mapa_atual_matriz = estado_anterior
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()

    def refazer_acao(self):
        """Avança a matriz para o estado guardado no futuro."""
        if not self.historico_refazer:
            self.notify("Não há ações para refazer!", severity="warning")
            return

        # 1. Guarda a foto atual de volta no "Desfazer"
        estado_atual = copy.deepcopy(self.mapa_atual_matriz)
        self.historico_desfazer.append(estado_atual)
        
        # 2. Puxa a foto do futuro
        estado_futuro = self.historico_refazer.pop()
        self.mapa_atual_matriz = estado_futuro
        self.tem_alteracoes = True
        self.exibir_mapa_na_tela()

    def exibir_mapa_na_tela(self):
        """Converte a matriz numa string visível e joga na tela de forma segura."""
        if self.mapa_atual_matriz:
            texto_mapa = "\n".join(["".join(linha) for linha in self.mapa_atual_matriz])
            texto_seguro = Text(texto_mapa, no_wrap=True, style="pointer: wait", )

            self.query_one("#mapa-titulo", Label).update(f"Mapa: {self.mapa_atual_dados['nome']}")
            self.query_one("#mapa-view", MapaInterativo).update(texto_seguro)

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
            mapa_existente = db.query(MapaDB).filter(MapaDB.nome == nome_mapa).first()

            # Se achou um mapa com este nome, E o ID dele é diferente do nosso mapa atual
            if mapa_existente and mapa_existente.id != mapa_id_atual:
                self.notify(f"Já existe um mapa chamado '{nome_mapa}'. Escolha outro nome em Opções!", severity="error")
                return # Interrompe a função aqui, não salva nada.

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
                    # Atualizamos a matriz (o desenho) com as últimas pinceladas
                    mapa_para_atualizar.mapa_em_si = self.mapa_atual_matriz 
                    
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
                    configs={} 
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
                yield Select([("  ", "  "), ("🟦", "🟦"), ("░░", "░░"), ("⬛", "⬛"), ("🟫", "🟫")], prompt="Tile Chão", id="input-tile-chao", value="  " )
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
            mapas = db.query(MapaDB).all()
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