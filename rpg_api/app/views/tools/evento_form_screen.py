"""
Componente de Formulário de Eventos do Editor de Mapas.

Contém todas as telas modais relacionadas à criação e edição de eventos,
separadas do MapManagerScreen para manter a responsabilidade única de cada módulo.
"""
import copy
import json
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Select, ListView, ListItem, Static
from textual.containers import Horizontal, Vertical, Container
from textual import on
from rich.text import Text
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from app.core.entities.emojis import CatalogoTiles, dict_item_emoji, dict_emoji_efeito, dict_emoji_racas
from app.views.tools.painting_tools import  MapaInterativo
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
from typing import Literal


Modo_de_Captura = Literal['config_ini', None]
CSS_PATH = "styles/styles.css"

# ==============================================================================
# TELA PRINCIPAL: FORMULÁRIO DE PROPRIEDADES DO EVENTO
# ==============================================================================
class PropriedadesEventoFormScreen(ModalScreen[dict]):
    """
    Formulário principal que gerencia o JSON do evento com páginas e comandos.

    Recebe os dados do evento existente (ou None para novo evento) e permite
    configurar nome, emoji, gatilho, condições por página e lista de comandos.
    Ao confirmar, retorna um dicionário com os dados consolidados para o
    MapManagerScreen persistir na memória e no banco de dados.
    """

    def __init__(self, linha: int, coluna: int, emoji: str, dados_existentes: dict = None):
        super().__init__()
        self.linha = linha
        self.coluna = coluna
        self.emoji = emoji
        self.dados_existentes = copy.deepcopy(dados_existentes) or {}

        # Estrutura JSON Universal de Páginas
        params = self.dados_existentes.get("parametros", {})
        if "paginas" not in params:
            # Evento simples ou novo: inicia com uma página padrão
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
        itens_set = set([v for sub_dict in dict_item_emoji.values()
                        for k, v in sub_dict.items()])
        racas_set = set([v for _, v in dict_emoji_racas.items()])
        efeitos_set = set([v for _, v in dict_emoji_efeito.items()])
        coletanea_emoji = list(
            [*itens_set, *racas_set, *efeitos_set, *CatalogoTiles.OBJETOS])

        with Vertical(id="evt-caixa-full"):
            titulo = f"🛠️ Evento em [{self.linha},{self.coluna}]"
            yield Label(titulo, classes="titulo-secao")

            with Horizontal(classes="linha-dupla"):
                yield Label("Nome:", classes="campo-rotulo")
                yield Input(
                    value=self.dados_existentes.get(
                        "nome", f"ev_{self.linha}_{self.coluna}"),
                    id="evt-nome")
                yield Label("Emoji:", classes="campo-rotulo")
                yield Select(
                    [(v, v) for v in coletanea_emoji] +
                    [(self.emoji, self.emoji)],
                    value=self.emoji, id="evt-emoji")

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

    # ==========================================
    # LÓGICA DE NAVEGAÇÃO ENTRE PÁGINAS
    # ==========================================

    def atualizar_tela_pagina(self):
        """Atualiza todos os widgets com os dados da página atual."""
        lbl = self.query_one("#lbl-pag-atual", Label)
        lbl.update(f" {self.pagina_atual_idx + 1} / {len(self.paginas)} ")

        select_gatilho = self.query_one("#evt-gatilho", Select)
        select_gatilho.value = self.paginas[self.pagina_atual_idx].get(
            "gatilho", "acao_jogador")

        self.atualizar_exibicao_condicoes()
        self.atualizar_lista_comandos()

    # ==========================================
    # LÓGICA DE CONDIÇÕES DA PÁGINA
    # ==========================================

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
            texto_sw = "\n".join(
                linhas_sw) + "\n  (Clique num switch na lista de comandos para remover)"
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
                linhas_var.append(
                    f"  [{i}] {var['nome']} {op} {var.get('valor', 0)}")
            texto_var = "\n".join(linhas_var)
        else:
            texto_var = "  (nenhuma)"
        self.query_one("#lista-variaveis", Static).update(texto_var)

        # --- Self Switch ---
        self_sw = condicoes.get("self_switch", "nenhum")
        select_ssw = self.query_one("#evt-self-switch", Select)
        select_ssw.value = self_sw or "nenhum"

        # --- Item Requerido ---
        item_req = condicoes.get("item_requerido") or ""
        self.query_one("#evt-item-requerido", Input).value = item_req

    def atualizar_lista_comandos(self):
        """Renderiza a lista de comandos da página atual."""
        lista = self.query_one("#lista-comandos", ListView)
        lista.clear()
        comandos = self.paginas[self.pagina_atual_idx].get("comandos", [])
        for i, cmd in enumerate(comandos):
            dados_str = json.dumps(cmd['dados'], ensure_ascii=False, indent=2)
            texto = f"[{i}] {cmd['tipo']}\n{dados_str}"
            lista.append(ListItem(Label(texto), name=str(i)))

    # ==========================================
    # REACTIVE HANDLERS
    # ==========================================

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

    # ==========================================
    # HANDLERS DE BOTÕES
    # ==========================================

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
                # Reordena IDs
                for i, p in enumerate(self.paginas):
                    p["id_pagina"] = i + 1
                self.pagina_atual_idx = min(
                    self.pagina_atual_idx, len(self.paginas) - 1)
                self.atualizar_tela_pagina()
            else:
                self.notify("Não é possível deletar a única página!",
                            severity="warning")

        elif event.button.id == "btn-add-cmd":
            self.app.push_screen(AdicionarComandoScreen(),
                                 self.ao_adicionar_comando)

        # --- Botões de Condições ---
        elif event.button.id == "btn-add-switch":
            self.app.push_screen(AdicionarSwitchScreen(),
                                 self.ao_adicionar_switch)

        elif event.button.id == "btn-add-variavel":
            self.app.push_screen(AdicionarVariavelScreen(),
                                 self.ao_adicionar_variavel)

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

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "lista-comandos":
            idx = int(event.item.name)
            cmd = self.paginas[self.pagina_atual_idx]["comandos"][idx]
            self.app.push_screen(
                AcoesComandoScreen(cmd),
                lambda acao: self.ao_acao_comando(acao, idx))

    # ==========================================
    # CALLBACKS DE CONDIÇÕES
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

    # ==========================================
    # CALLBACKS DE COMANDOS
    # ==========================================

    def ao_adicionar_comando(self, novo_comando):
        if novo_comando:
            self.paginas[self.pagina_atual_idx].setdefault(
                "comandos", []).append(novo_comando)
            self.atualizar_lista_comandos()

    def ao_acao_comando(self, acao: str, idx: int):
        if not acao:
            return
        comandos = self.paginas[self.pagina_atual_idx]["comandos"]
        if acao == "excluir":
            comandos.pop(idx)
            self.atualizar_lista_comandos()
        elif acao == "editar":
            cmd = comandos[idx]
            self.app.push_screen(
                AdicionarComandoScreen(cmd),
                lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith("editar_ramo_"):
            ramo_nome = acao.replace("editar_ramo_", "")
            cmd = comandos[idx]
            ramos = cmd["dados"].setdefault("ramos", {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            self.app.push_screen(
                RamoEditorScreen(ramo_nome, ramo_cmds),
                lambda novos_cmds: self.ao_salvar_ramo(novos_cmds, idx, ramo_nome))

    def ao_salvar_edicao_comando(self, novo_comando, idx):
        if novo_comando:
            # Mantemos os ramos caso seja bifurcação para não perder se não editou
            if novo_comando["tipo"] == self.paginas[self.pagina_atual_idx]["comandos"][idx]["tipo"]:
                if "ramos" in self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]:
                    novo_comando["dados"]["ramos"] = (
                        self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]["ramos"]
                    )
            self.paginas[self.pagina_atual_idx]["comandos"][idx] = novo_comando
            self.atualizar_lista_comandos()

    def ao_salvar_ramo(self, novos_cmds, idx, ramo_nome):
        if novos_cmds is not None:
            self.paginas[self.pagina_atual_idx]["comandos"][idx]["dados"]["ramos"][ramo_nome] = novos_cmds
            self.atualizar_lista_comandos()

    # ==========================================
    # CAPTURA / RESTAURAÇÃO DE ESTADO (Modo Mira)
    # ==========================================

    def _capturar_valores_campos_atuais(self) -> dict:
        """Serializa o estado atual dos inputs para não perder o progresso digitado."""
        return {
            "nome": self.query_one("#evt-nome").value,
            "emoji": self.query_one("#evt-emoji").value,
            "gatilho": self.query_one("#evt-gatilho").value,
            "item-requerido": self.query_one("#evt-item-requerido").value,
            "self-switch": self.query_one("#evt-self-switch").value,
            "lista-variaveis": self.query_one("#lista-variaveis").value,
            "lista-switches": self.query_one("#lista-switches").value,
            "lista-comandos": self.query_one("#lista-comandos").value,
            "mapa_teleporte": self.query_one("#cmd-tel-mapa").value,
            "linha_teleporte": self.query_one("#cmd-tel-y").value,
            "coluna_teleporte": self.query_one("#cmd-tel-x").value,
        }

    def restaurar_valores_dos_campos(
        self,
        dados: dict,
        linha_coletada: int = None,
        coluna_coletada: int = None,
        id_alvo: str = None
    ) -> None:
        """Preenche o formulário com o snapshot e injeta a nova coordenada no local exato."""
        self.query_one("#evt-nome").value = dados.get("nome", "")
        self.query_one("#evt-emoji").value = dados.get("emoji", "")
        self.query_one("#evt-gatilho").value = dados.get("gatilho", "")
        self.query_one(
            "#evt-item-requerido").value = dados.get("item-requerido", "")
        self.query_one("#evt-self-switch").value = dados.get("self-switch", "")
        self.query_one(
            "#lista-variaveis").value = dados.get("lista-variaveis", "")
        self.query_one(
            "#lista-switches").value = dados.get("lista-switches", "")
        self.query_one(
            "#lista-comandos").value = dados.get("lista-comandos", "")

        self.query_one("#cmd-tel-y").value = str(linha_coletada)
        self.query_one("#cmd-tel-x").value = str(coluna_coletada)


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


# ==============================================================================
# SUB-MODAL: ADICIONAR / EDITAR COMANDO
# ==============================================================================
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
                ("Notificação na tela (Texto)", "noficacao"),
                ("Teleporte (Mudar Mapa/Posição)", "teleporte"),
                ("Inventário (Add/Sub)", "mudar_inventario"),
                ("Status do Herói (HP/MP)", "mudar_status_heroi"),
                ("Bifurcação Condicional (Opções)", "bifurcacao_condicional"),
                ("Variável (Valor)", "controle_variavel"),
                ("Switch (Liga/Desliga)", "controle_switch"),
                ("Self Switch (Local)", "controle_self_switch"),
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
            container.mount(Input(
                placeholder="Texto da mensagem (Use tags [color] se quiser)",
                id="cmd-msg-texto", value=dados.get("texto", "")))

        elif tipo == "notificacao":
            container.mount(Input(
                placeholder="Texto da notificação (Use tags [color] se quiser)",
                id="cmd-notif-texto", value=dados.get("texto", "")))

        elif tipo == "teleporte":
            with SessionLocal() as db:
                mapas = db.query(MapaDB).all()
                opcoes = [(m.nome, str(m.id)) for m in mapas] + [('', '')]

            container.mount(Select(opcoes, id="cmd-tel-mapa", value=str(dados.get("mapa_id", ""))))
            container.mount(Button("📍 Selecione o local.", id="btn-select-pos-xy", variant = 'success'
            ))
            container.mount(Input(
                placeholder="Coordenada X (Coluna)",
                id="cmd-tel-x", value=str(dados.get("pos_x", ""))))
            container.mount(Input(
                placeholder="Coordenada Y (Linha)",
                id="cmd-tel-y", value=str(dados.get("pos_y", ""))))

        elif tipo == "mudar_inventario":
            container.mount(Input(
                placeholder="Nome exato do Item (ex: pocao_cura)",
                id="cmd-inv-item", value=dados.get("item", "")))
            container.mount(Select(
                [("Adicionar", "add"), ("Remover", "sub")],
                value=dados.get("operacao", "add"), id="cmd-inv-op"))
            container.mount(Input(
                placeholder="Quantidade (ex: 1)",
                value=str(dados.get("quantidade", 1)), id="cmd-inv-qtd"))

        elif tipo == "mudar_status_heroi":
            container.mount(Select(
                [("Vida (HP)", "hp"), ("Mana (MP)", "mp")],
                value=dados.get("parametro", "hp"), id="cmd-stat-param"))
            container.mount(Select(
                [("Recuperar (Add)", "add"), ("Causar Dano (Sub)", "sub")],
                value=dados.get("operacao", "add"), id="cmd-stat-op"))
            container.mount(Input(
                placeholder="Valor Numérico",
                value=str(dados.get("valor", 10)), id="cmd-stat-valor"))

        elif tipo == "bifurcacao_condicional":
            container.mount(Input(
                placeholder="Pergunta ao Jogador?",
                id="cmd-bif-pergunta", value=dados.get("pergunta", "")))
            opcoes = dados.get("opcoes", ["", ""])
            op1 = opcoes[0] if len(opcoes) > 0 else ""
            op2 = opcoes[1] if len(opcoes) > 1 else ""
            container.mount(Input(placeholder="Opção 1 (ex: Sim)", id="cmd-bif-op1", value=op1))
            container.mount(Input(placeholder="Opção 2 (ex: Não)", id="cmd-bif-op2", value=op2))

        elif tipo == "controle_switch":
            container.mount(Input(
                placeholder="Nome da Switch",
                id="cmd-sw-nome", value=dados.get("nome", "")))
            val_str = "true" if dados.get("valor", True) else "false"
            container.mount(Select(
                [("Ligar (True)", "true"), ("Desligar (False)", "false")],
                value=val_str, id="cmd-sw-valor"))

        elif tipo == "controle_self_switch":
            container.mount(Select(
                [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
                value=dados.get("letra", "A"), id="cmd-ssw-letra"))
            val_str = "true" if dados.get("valor", True) else "false"
            container.mount(Select(
                [("Ligar (True)", "true"), ("Desligar (False)", "false")],
                value=val_str, id="cmd-ssw-valor"))

        elif tipo == "controle_variavel":
            container.mount(Input(
                placeholder="Nome da Variável",
                id="cmd-variavel-nome", value=dados.get("nome", "")))
            container.mount(Select(
                [(" = ", "="), (" + ", "+"), (" - ", "-"), (" * ", "*"), (" / ", "//")],
                value=dados.get("operador", "="), id="cmd-variavel-operador"))
            container.mount(Input(
                placeholder="Valor atribuido",
                id="cmd-variavel-valor", value=dados.get("valor", "")))

    def _capturar_valores_campos_atuais(self) -> dict:
        """Serializa o estado atual do formulário de teleporte para não perder progresso."""
        return {
            "mapa_teleporte": self.query_one("#cmd-tel-mapa").value,
            "linha_teleporte": self.query_one("#cmd-tel-y").value,
            "coluna_teleporte": self.query_one("#cmd-tel-x").value,
        }

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-cancel":
            self.dismiss(None)

        # Intercepta botão de seleção de posição XY para teleporte
        if event.button.id == "btn-select-pos-xy":
            self.notify("Selecione a posição para teleporte")
            dados_requisicao = {
                "tipo": 'teleporte',
                "acao_especial": "ativar_capitura_de_posicao",
                #"estado_formulario_atual": self._capturar_valores_campos_atuais(),
                "dados": self._capturar_valores_campos_atuais(),
                "mapa_teleporte": self.query_one("#cmd-tel-mapa").value
            }
            self.dismiss(dados_requisicao)

            
        elif event.button.id == "btn-save":
            tipo = self.query_one("#cmd-tipo").value
            if not tipo or tipo == Select.BLANK:
                return

            comando = {"tipo": tipo, "dados": {}}
            try:
                if tipo == "mensagem":
                    comando["dados"]["texto"] = self.query_one("#cmd-msg-texto").value
                elif tipo == "notificacao":
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
                    comando["dados"]["operador"] = self.query_one("#cmd-variavel-operador").value
                    comando["dados"]["valor"] = self.query_one("#cmd-variavel-valor").value

            except Exception:
                self.notify("Erro ao salvar comando: Preencha os campos corretamente", severity="error")
                return

            self.dismiss(comando)


# ==============================================================================
# SUB-MODAL: MENU DE AÇÕES DE UM COMANDO
# ==============================================================================
class AcoesComandoScreen(ModalScreen[str]):
    """Menu contextual ao clicar num comando da lista."""

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


# ==============================================================================
# SUB-MODAL: EDITOR DE RAMO (recursivo)
# ==============================================================================
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
        if not acao:
            return
        if acao == "excluir":
            self.comandos.pop(idx)
            self.atualizar_lista()
        elif acao == "editar":
            cmd = self.comandos[idx]
            self.app.push_screen(
                AdicionarComandoScreen(cmd),
                lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith("editar_ramo_"):
            ramo_nome = acao.replace("editar_ramo_", "")
            cmd = self.comandos[idx]
            ramos = cmd["dados"].setdefault("ramos", {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            # RECURSÃO: Chama outro RamoEditorScreen por cima deste!
            self.app.push_screen(
                RamoEditorScreen(ramo_nome, ramo_cmds),
                lambda novos_cmds: self.ao_salvar_subramo(novos_cmds, idx, ramo_nome))

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




class SecondaryMap(ModalScreen):
    '''Um mostrador de mapa para coisas como pegar coordenada. '''

    CSS_PATH = CSS_PATH

    def __init__(self):
        self.matriz_do_mapa_secundario: list | None = None
        self.objetos_do_mapa_secundario: dict = {}
        self.id_do_mapa_secundario: int | None = None
        self.contexto_do_modo_de_captura_ativo: Modo_de_Captura = None

        super().__init__()

    def compose(self):
        with Container(id="sec-map-area"):
            yield MapaInterativo("Matriz do Mapa aparecerá aqui...", id="sec-mapa-view")

    def on_mount(self):
        """Executa automaticamente quando o Gerenciador de Mapas abre."""
        logging.info(f"Montagem do mapa secundário...")
        self.carregar_mapa_secundario()

    # CARREGAMENTO DO MAPA SECUNDÁRIO

    def carregar_mapa_secundario(self):
        from app.db.database import SessionLocal

        with SessionLocal() as db:
            # 1. Carrega o Mapa Base
            mapa_sec_db_carregado = db.query(MapaDB).filter(
                MapaDB.id == self.id_do_mapa_secundario).first()

            if not mapa_sec_db_carregado:
                logging.info(f"Não carregou mapa...")
                return

            self.matriz_do_mapa_secundario = mapa_sec_db_carregado.mapa_em_si

            objetos_salvos = mapa_sec_db_carregado.objetos if mapa_sec_db_carregado.objetos else {}
            logging.info(f"Carregou> obj: {objetos_salvos}")
            self.objetos_do_mapa_secundario = self._desempacotar_objetos_do_banco(
                objetos_salvos)


    # =========================================================================
    # CAPTURADOR DE COORDENADAS DO MAPA SECUNDÁRIO
    # =========================================================================
    @on(MapaInterativo.Pintar)
    def processar_pintura(self, event: MapaInterativo.Pintar):
        if self.matriz_do_mapa_secundario is None:
            logging.info(f"Mapa sem matriz...")
            return
        linha, coluna = event.linha, event.coluna

        if 0 <= linha < len(self.matriz_do_mapa_secundario) and 0 <= coluna < len(self.matriz_do_mapa_secundario[0]):
            logging.info(
                f"Modo de captura do mapa secundário: coords: (x={coluna}, y={linha})")

            if event.inicio_de_traco:
                self.query_one("#sec-mapa-view",
                               MapaInterativo).mouse_pressionado = False
                self.modo_captura_coordenada = False
                self.ferramenta_atual = "lapis"
                try:
                    self._reabrir_formulario_enviando_coordenadas(
                        linha, coluna, self.contexto_do_modo_de_captura_ativo)
                except Exception as e:
                    logging.info(
                        f"Erro mapa-secundario ao _reabrir_formulario_enviando_coordenadas: {e}")
                    raise ValueError(
                        f"Erro mapa-secundario ao _reabrir_formulario_enviando_coordenadas: {e}")

            return

    # =========================================================================
    # MONTADOR DA TELA DO MAPA SECUNDÁRIO
    # =========================================================================
    def exibir_mapa_sec_na_tela(self):
        """Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo)."""
        if self.matriz_do_mapa_secundario is None:
            return

        texto_mapa = Text(no_wrap=True)

        for linha_idx in range(len(self.matriz_do_mapa_secundario)):
            for col_idx in range(len(self.matriz_do_mapa_secundario[0])):
                tile_chao = self.matriz_do_mapa_secundario[linha_idx][col_idx]
                tile_objeto = self.matriz_do_mapa_secundario.get(
                    (linha_idx, col_idx))

                if tile_objeto is not None:
                    cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                    texto_mapa.append(
                        tile_objeto, style=f"on {cor_bg}" if cor_bg else "")
                else:
                    texto_mapa.append(tile_chao)
            texto_mapa.append("\n")

        self.query_one("#sec-mapa-view", MapaInterativo).update(texto_mapa)


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
    

    def _reabrir_formulario_enviando_coordenadas(self, linha_coletada: int, coluna_coletada: int, id_alvo: str):
        """Monta o formulário de volta injetando a nova coordenada no escopo correto."""

        
        dados_atuais = dict(
            coordenadas_iniciais=str(
                str(linha_coletada)+','+str(coluna_coletada)),
            switch_coord_ini=True,
        )

        try:
            form_screen = PropriedadesEventoFormScreen(
                linha=linha_coletada,
                coluna=coluna_coletada,
                
                evento_atual=self.eventos_do_mapa_atual.get(
                    (linha_coletada, coluna_coletada))
            )
        except Exception as e:
            raise (f"Erro ao instanciar tela  Form de Evento: {e}")

        # 🌟 Restaura a memória do formulário e passa a coordenada mapeada ao alvo correspondente
        try:
            form_screen.restaurar_valores_dos_campos(
                dados=self.buffer_de_dados_do_formulario,
                linha_coletada=linha_coletada,
                coluna_coletada=coluna_coletada,
                id_alvo=id_alvo
            )
        except Exception as e:
            raise (f"Erro ao restaurar_valores_dos_campos do evento: {e}")
        try:
            self.app.push_screen(
                form_screen,
                lambda dados: self.ao_terminar_configurar_evento(
                    linha_coletada, coluna_coletada, dados)
            )
        except Exception as e:
            raise (f"Erro ao re-lançar tela do evento: {e}")

        # Limpa as flags e buffers de contexto
        self.buffer_de_dados_do_formulario = {}
        self.contexto_do_modo_de_captura_ativo = None
