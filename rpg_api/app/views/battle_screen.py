"""
Tela de Combate por Turnos — BattleScreen (Padrão Ouro Final Fantasy)

Interface TUI do sistema de combate usando o framework Textual.
Suporta combates de 1 a 4 Aliados contra 1 a 4 Inimigos com turnos individuais,
timeline de iniciativa, modais contextuais de magias e itens por combatente.

Segue estritamente a Arquitetura Limpa: esta tela APENAS escuta eventos do BattleSystem
e redesenha a si mesma de forma reativa. Nunca calcula dano ou lógica de jogo.
"""
import esper
import logging
import asyncio
from typing import Optional, Any, List, Dict

from textual.screen import Screen, ModalScreen
from textual.widgets import Static, RichLog, Label, ProgressBar, RadioSet, RadioButton, Button, ListView, ListItem
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual import on
from textual.message import Message
from textual.widget import Widget

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


# ==============================================================================
# WIDGET ANIMÁVEL DO SPRITE DO COMBATENTE
# ==============================================================================

class CombatenteSprite(Static):
    """
    Widget de sprite do combatente com posição X animável via reactive.
    """
    x_pos: reactive[float] = reactive(0.0)
    y_pos: reactive[float] = reactive(3.0)

    def watch_x_pos(self, novo_x: float) -> None:
        self.styles.offset = (int(novo_x), int(self.y_pos))

    def watch_y_pos(self, novo_y: float) -> None:
        self.styles.offset = (int(self.x_pos), int(novo_y))


# ==============================================================================
# WIDGET DE EFEITO DE ATAQUE (💥 ✨ 💊 🔥 ⚡ ❄️)
# ==============================================================================

class EfeitoAtaque(Static):
    """Emoji de impacto ou projétil que aparece brevemente na arena."""
    x_pos: reactive[float] = reactive(0.0)
    y_pos: reactive[float] = reactive(2.0)

    def watch_x_pos(self, novo_x: float) -> None:
        self.styles.offset = (int(novo_x), int(self.y_pos))

    def watch_y_pos(self, novo_y: float) -> None:
        self.styles.offset = (int(self.x_pos), int(novo_y))


# ==============================================================================
# WIDGET DE BARRA DE STATUS REATIVA (Compacta para colunas laterais)
# ==============================================================================

class BarraStatusCombate(Widget):
    """
    Widget composto de status (Nome, Nível/Classe, HP Bar, MP Bar, Efeitos) para um combatente.
    """

    def __init__(
        self,
        nome: str,
        hp_atual: int,
        hp_max: int,
        mp_atual: int,
        mp_max: int,
        classes_css: str = "",
        widget_id: str = "",
        classe_ou_tipo: str = "",
    ):
        super().__init__(id=widget_id if widget_id else None, classes=classes_css if classes_css else "")
        self._nome = nome
        self._hp_atual = hp_atual
        self._hp_max = max(1, hp_max)
        self._mp_atual = mp_atual
        self._mp_max = max(1, mp_max)
        self._classe_ou_tipo = classe_ou_tipo

    def compose(self):
        yield Label(f"{self._nome}", id=f"{self.id}-nome" if self.id else "lbl-nome", classes="combatente-nome")
        yield ProgressBar(
            total=self._hp_max,
            id=f"{self.id}-hp-bar" if self.id else "hp-bar",
            classes="hp-bar",
            show_eta=False,
            show_percentage=False,
        )
        yield Label(
            f"💟 {self._hp_atual}/{self._hp_max}",
            id=f"{self.id}-hp-label" if self.id else "hp-label",
            classes="hp-label",
        )
        yield ProgressBar(
            total=self._mp_max,
            id=f"{self.id}-mp-bar" if self.id else "mp-bar",
            classes="mp-bar",
            show_eta=False,
            show_percentage=False,
        )
        yield Label(
            f"🔮 {self._mp_atual}/{self._mp_max}",
            id=f"{self.id}-mp-label" if self.id else "mp-label",
            classes="mp-label",
        )

    def on_mount(self) -> None:
        self.atualizar(self._hp_atual, self._hp_max, self._mp_atual, self._mp_max)

    def atualizar(self, hp_atual: int, hp_max: int, mp_atual: int, mp_max: int, efeitos: Optional[List[str]] = None) -> None:
        """Atualiza os valores e redesenha as barras."""
        self._hp_atual = max(0, hp_atual)
        self._hp_max = max(1, hp_max)
        self._mp_atual = max(0, mp_atual)
        self._mp_max = max(1, mp_max)
        try:
            hp_bar = self.query_one(f"#{self.id}-hp-bar", ProgressBar)
            hp_bar.total = self._hp_max
            hp_bar.progress = self._hp_atual

            mp_bar = self.query_one(f"#{self.id}-mp-bar", ProgressBar)
            mp_bar.total = self._mp_max
            mp_bar.progress = self._mp_atual

            self.query_one(f"#{self.id}-hp-label", Label).update(f"💟 {self._hp_atual}/{self._hp_max}")
            self.query_one(f"#{self.id}-mp-label", Label).update(f"🔮 {self._mp_atual}/{self._mp_max}")
        except Exception as erro_update:
            logging.info(f"BarraStatusCombate.atualizar: {erro_update}")


# ==============================================================================
# TELA PRINCIPAL DE COMBATE — BattleScreen (4v4 Padrão Ouro)
# ==============================================================================

class BattleScreen(Screen):
    """
    Tela de combate por turnos multi-aliados (1-4) vs multi-inimigos (1-4).
    Segue o Padrão Ouro estilo Final Fantasy com timeline superior, colunas dedicadas,
    destaque visual para o combatente da vez e modais de habilidades e itens por personagem.
    """

    CSS_PATH = "styles/battle_styles.css"

    turno_liberado: reactive[bool] = reactive(True)
    heroi_hp: reactive[int] = reactive(0)
    heroi_mp: reactive[int] = reactive(0)
    heroi_hp_max: reactive[int] = reactive(100)
    heroi_mp_max: reactive[int] = reactive(100)

    class AcaoConfirmada(Message):
        """Mensagem de ação do jogador com @property control para evitar OnDecoratorError."""
        def __init__(self, control: Widget, acao: str, alvo_index: int = 0) -> None:
            super().__init__()
            self._control = control
            self.acao = acao
            self.alvo_index = alvo_index

        @property
        def control(self) -> Widget:
            return self._control

    def __init__(self, heroi_ou_party: Any, inimigos_dados: Any):
        super().__init__()

        # Normaliza aliados (Party, lista ou personagem único)
        if hasattr(heroi_ou_party, "membros"):
            self.aliados_dados = list(heroi_ou_party.membros)[:4]
        elif isinstance(heroi_ou_party, list):
            self.aliados_dados = list(heroi_ou_party)[:4]
        else:
            self.aliados_dados = [heroi_ou_party]

        # Normaliza inimigos (lista ou dict/objeto único)
        if isinstance(inimigos_dados, list):
            self.inimigos_dados = list(inimigos_dados)[:4]
        else:
            self.inimigos_dados = [inimigos_dados]

        self.heroi_personagem = self.aliados_dados[0] if self.aliados_dados else None
        self.combatente_ativo_obj = self.heroi_personagem
        self.indice_aliado_ativo = 0
        self.e_aliado_ativo = True
        self.fila_turnos_snapshot = []
        self.rodada_atual = 1
        self.battle_sys: Optional[Any] = None

    # ==========================================
    # COMPOSIÇÃO DA INTERFACE — Layout Padrão Ouro
    # ==========================================

    def compose(self):
        # ─── LINHA SUPERIOR: TIMELINE DE INICIATIVA ───────────────────────
        with Container(id="painel-timeline"):
            yield Label("⏳ LINHA DO TEMPO: Aguardando combate...", id="lbl-timeline-turnos")

        with Horizontal(id="battle-layout"):

            # ─── COLUNA ESQUERDA: EQUIPE ALIADA (1 a 4) ──────────────────────
            with Vertical(id="painel-aliados"):
                yield Label("👥 EQUIPE ALIADA", classes="painel-titulo")
                for i, aliado in enumerate(self.aliados_dados):
                    nome = getattr(aliado, "nome", f"Aliado {i+1}")
                    emoji_raca = str(getattr(aliado, "raca", "🧙"))
                    yield BarraStatusCombate(
                        nome=f"{emoji_raca} {nome}",
                        hp_atual=getattr(aliado, "pv_atual", 50),
                        hp_max=getattr(aliado, "max_hp", 100),
                        mp_atual=getattr(aliado, "pm_atual", 20),
                        mp_max=getattr(aliado, "max_mp", 50),
                        widget_id=f"barra-aliado-{i}",
                        classes_css="barra-aliado" + (" combatente-ativo" if i == 0 else ""),
                    )

            # ─── COLUNA CENTRAL: ARENA + LOG + PAINEL DE AÇÕES ──────────────
            with Vertical(id="painel-central"):

                # Arena de Sprites
                with Container(id="arena"):
                    yield Label("⚔️ VS ⚔️", id="lbl-vs")

                    # Sprites dos Aliados
                    for i, aliado in enumerate(self.aliados_dados):
                        emoji_raca = str(getattr(aliado, "raca", "🧙"))
                        yield CombatenteSprite(
                            emoji_raca,
                            id=f"sprite-aliado-{i}",
                            classes="combatente heroi-side",
                        )

                    # Sprites dos Inimigos
                    for i, dados in enumerate(self.inimigos_dados):
                        emoji = dados.get("emoji", "👹") if isinstance(dados, dict) else str(getattr(dados, "raca", "👹"))
                        yield CombatenteSprite(
                            emoji,
                            id=f"sprite-inimigo-{i}",
                            classes="combatente inimigo-side",
                        )

                # Log Narrativo de Batalha
                yield RichLog(id="battle-log", highlight=True, markup=True, wrap=True)

                # Painel de Ações do Jogador
                with Container(id="action-panel"):
                    yield Label(f"🎯 Vez de: {getattr(self.heroi_personagem, 'nome', 'Herói')}", id="action-turn-label", classes="painel-titulo")
                    with Horizontal(id="action-horizontal"):

                        # Coluna de Comandos
                        with Vertical(id="acao-coluna"):
                            yield Label("⚔️ Comando:", id="action-label")
                            with RadioSet(id="action-radioset"):
                                yield RadioButton("⚔️  Atacar", value=True, id="act-atacar")
                                yield RadioButton("✨  Magias / Habilidades", id="act-magia")
                                yield RadioButton("🧪  Usar Item", id="act-item")
                                yield RadioButton("🛡️  Defender", id="act-defender")
                                yield RadioButton("🏃  Fugir do Combate", id="act-fugir")

                        # Coluna de Seleção de Alvo Contextual
                        with Vertical(id="alvo-coluna"):
                            yield Label("🎯 Alvo:", id="target-label")
                            with RadioSet(id="target-radioset"):
                                for i, dados in enumerate(self.inimigos_dados):
                                    nome_inimigo = dados.get("nome", f"Inimigo {i+1}") if isinstance(dados, dict) else getattr(dados, "nome", f"Inimigo {i+1}")
                                    emoji = dados.get("emoji", "👹") if isinstance(dados, dict) else "👹"
                                    yield RadioButton(
                                        f"{emoji} {nome_inimigo}",
                                        value=(i == 0),
                                        id=f"target-{i}",
                                    )

                    yield Button(
                        "✅  Confirmar Ação",
                        variant="success",
                        id="btn-confirmar-acao",
                    )

            # ─── COLUNA DIREITA: INIMIGOS (1 a 4) ───────────────────────────
            with Vertical(id="painel-inimigos"):
                yield Label("👹 INIMIGOS", classes="painel-titulo")
                for i, dados in enumerate(self.inimigos_dados):
                    nome_inimigo = dados.get("nome", f"Inimigo {i+1}") if isinstance(dados, dict) else getattr(dados, "nome", f"Inimigo {i+1}")
                    emoji = dados.get("emoji", "👹") if isinstance(dados, dict) else "👹"
                    yield BarraStatusCombate(
                        nome=f"{emoji} {nome_inimigo}",
                        hp_atual=100,
                        hp_max=100,
                        mp_atual=0,
                        mp_max=1,
                        widget_id=f"barra-inimigo-{i}",
                        classes_css="barra-inimigo",
                    )

    # ==========================================
    # LIFECYCLE: MOUNT / UNMOUNT
    # ==========================================

    def on_mount(self) -> None:
        """Registra handlers do Esper e inicializa o motor de combate."""
        esper.set_handler("combate_iniciado", self._ao_combate_iniciado)
        esper.set_handler("turno_iniciado", self._ao_turno_iniciado)
        esper.set_handler("turno_calculado", self._ao_turno_calculado)
        esper.set_handler("combate_encerrado", self._ao_combate_encerrado)

        self.call_next(self._posicionar_sprites_iniciais)

        from app.core.engine.systems import BattleSystem
        self.battle_sys = esper.get_processor(BattleSystem)

        if self.battle_sys:
            # Prepara objetos Personagem de domínio para inimigos
            inimigos_obj = []
            for d in self.inimigos_dados:
                if isinstance(d, dict):
                    inimigos_obj.append(self._criar_personagem_inimigo(d))
                else:
                    inimigos_obj.append(d)

            self.battle_sys.iniciar_combate(self.aliados_dados, inimigos_obj)
        else:
            self._escrever_log("[bold red]❌ Erro: BattleSystem não encontrado no Esper![/]")
            logging.error("BattleScreen: BattleSystem não registrado.")

    def on_unmount(self) -> None:
        try:
            esper.remove_handler("combate_iniciado", self._ao_combate_iniciado)
            esper.remove_handler("turno_iniciado", self._ao_turno_iniciado)
            esper.remove_handler("turno_calculado", self._ao_turno_calculado)
            esper.remove_handler("combate_encerrado", self._ao_combate_encerrado)
        except Exception as erro_unmount:
            logging.info(f"BattleScreen.on_unmount: {erro_unmount}")

    # ==========================================
    # WATCHERS REATIVOS
    # ==========================================

    def watch_turno_liberado(self, liberado: bool) -> None:
        try:
            btn = self.query_one("#btn-confirmar-acao", Button)
            btn.disabled = not liberado
            radioset = self.query_one("#action-radioset", RadioSet)
            radioset.disabled = not liberado
        except Exception:
            pass

    # ==========================================
    # HANDLERS DOS EVENTOS DO BATTLESYSTEM
    # ==========================================

    def _ao_combate_iniciado(self, dados: dict) -> None:
        """Inicializa os dados visuais do combate 4v4 e anima entrada."""
        aliados = dados.get("aliados", self.aliados_dados)
        inimigos = dados.get("inimigos", self.inimigos_dados)
        self.fila_turnos_snapshot = dados.get("fila_turnos", [])
        self.rodada_atual = dados.get("rodada", 1)

        # Atualiza barras de aliados
        for i, a in enumerate(aliados):
            try:
                barra = self.query_one(f"#barra-aliado-{i}", BarraStatusCombate)
                barra.atualizar(a.pv_atual, a.max_hp, a.pm_atual, a.max_mp)
            except Exception:
                pass

        # Atualiza barras de inimigos
        for i, inimigo in enumerate(inimigos):
            try:
                barra = self.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
                barra.atualizar(inimigo.pv_atual, inimigo.max_hp, getattr(inimigo, "pm_atual", 0), getattr(inimigo, "max_mp", 1))
            except Exception:
                pass

        self._atualizar_timeline_visual()

        nomes_aliados = ", ".join(getattr(a, "nome", "?") for a in aliados)
        nomes_inimigos = ", ".join(getattr(e, "nome", "?") for e in inimigos)

        self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
        self._escrever_log(f"[bold red]🎇 COMBATE INICIADO! (Rodada {self.rodada_atual})[/]")
        self._escrever_log(f"[cyan]Equipe: {nomes_aliados}[/] [bold white]VS[/] [red]Inimigos: {nomes_inimigos}[/]")
        self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")

        self.call_next(self._animar_entrada_sprites)

    def _ao_turno_iniciado(self, dados: dict) -> None:
        """Atualiza o combatente ativo da vez, destacando sua barra e liberando/bloqueando ações."""
        self.combatente_ativo_obj = dados.get("combatente_ativo")
        e_aliado = dados.get("e_aliado", True)
        self.e_aliado_ativo = e_aliado
        self.indice_aliado_ativo = dados.get("indice_time", 0)
        self.fila_turnos_snapshot = dados.get("fila_turnos", [])
        self.rodada_atual = dados.get("rodada", 1)

        # Atualiza destaque nas barras de status
        for i in range(len(self.aliados_dados)):
            try:
                barra = self.query_one(f"#barra-aliado-{i}", BarraStatusCombate)
                if e_aliado and i == self.indice_aliado_ativo:
                    barra.add_class("combatente-ativo")
                else:
                    barra.remove_class("combatente-ativo")
            except Exception:
                pass

        for i in range(len(self.inimigos_dados)):
            try:
                barra = self.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
                if not e_aliado and i == self.indice_aliado_ativo:
                    barra.add_class("combatente-ativo")
                else:
                    barra.remove_class("combatente-ativo")
            except Exception:
                pass

        # Atualiza label do turno no painel de ações
        nome_ativo = getattr(self.combatente_ativo_obj, "nome", "Combatente")
        classe_ativo = getattr(getattr(self.combatente_ativo_obj, "classe", None), "nome", "")
        desc_classe = f" ({classe_ativo})" if classe_ativo else ""

        try:
            lbl_turno = self.query_one("#action-turn-label", Label)
            if e_aliado:
                lbl_turno.update(f"🎯 Turno de: [bold green]{nome_ativo}[/]{desc_classe}")
            else:
                lbl_turno.update(f"⏳ Turno de IA: [bold red]{nome_ativo}[/]{desc_classe}...")
        except Exception:
            pass

        self._atualizar_timeline_visual()
        self.turno_liberado = e_aliado

    def _ao_turno_calculado(self, dados: dict) -> None:
        """Processa o resultado do turno, atualiza barras, escreve logs e anima."""
        fase = dados.get("fase", "jogador")
        resultado = dados.get("resultado", {})
        atacante = dados.get("atacante", self.combatente_ativo_obj)

        if resultado.get("erro_item"):
            self._escrever_log(f"[bold red]❌ {resultado['erro_item']}[/]")
            self.turno_liberado = True
            return

        # Atualiza todas as barras de aliados
        lista_aliados = dados.get("aliados", [])
        for info in lista_aliados:
            idx = info.get("index", 0)
            try:
                barra = self.query_one(f"#barra-aliado-{idx}", BarraStatusCombate)
                barra.atualizar(info["hp"], info["hp_max"], info["mp"], info["mp_max"])
                if not info["vivo"]:
                    barra.add_class("combatente-derrotado")
                    try:
                        self.query_one(f"#sprite-aliado-{idx}", CombatenteSprite).add_class("sprite-derrotado")
                    except Exception:
                        pass
            except Exception:
                pass

        # Atualiza todas as barras de inimigos
        lista_inimigos = dados.get("inimigos", [])
        for info in lista_inimigos:
            idx = info.get("index", 0)
            try:
                barra = self.query_one(f"#barra-inimigo-{idx}", BarraStatusCombate)
                barra.atualizar(info["hp"], info["hp_max"], info.get("mp", 0), info.get("mp_max", 1))
                if not info["vivo"]:
                    barra.add_class("combatente-derrotado")
                    try:
                        self.query_one(f"#sprite-inimigo-{idx}", CombatenteSprite).add_class("sprite-derrotado")
                    except Exception:
                        pass
            except Exception:
                pass

        self._escrever_log_turno(resultado, fase)

        # Dispara animações
        self.call_next(lambda: self._animar_ataque(fase, resultado))

    def _ao_combate_encerrado(self, dados: dict) -> None:
        """Processa a finalização do combate."""
        vencedor = dados.get("vencedor", "jogador")
        self.turno_liberado = False

        if vencedor == "jogador":
            resultado_final = "venceu"
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
            self._escrever_log("[bold green]🏆 VITÓRIA GLORIOSA! Toda a ameaça foi derrotada![/]")
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
            self.screen.add_class("vitoria")
        elif vencedor == "fuga":
            resultado_final = "fugiu"
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
            self._escrever_log("[bold cyan]💨 A equipe recuou estrategicamente e fugiu com segurança![/]")
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
        else:
            resultado_final = "perdeu"
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
            self._escrever_log("[bold red]💀 DERROTA... Todos os aliados tombaram em batalha.[/]")
            self._escrever_log("[bold yellow]═══════════════════════════════════════════════════════════[/]")
            self.screen.add_class("derrota")

        self.set_timer(2.2, lambda: self._fechar_tela_combate(resultado_final))

    # ==========================================
    # TIMELINE VISUAL DE TURNOS
    # ==========================================

    def _atualizar_timeline_visual(self) -> None:
        """Renderiza a sequência de iniciativa no banner superior."""
        try:
            lbl = self.query_one("#lbl-timeline-turnos", Label)
            if not self.fila_turnos_snapshot:
                lbl.update(f"⏳ Rodada {self.rodada_atual}")
                return

            badges = []
            for item in self.fila_turnos_snapshot:
                nome = item.get("nome", "?")
                tipo = item.get("tipo", "aliado")
                iniciativa = item.get("iniciativa", 0)
                ativo = item.get("ativo", False)
                vivo = item.get("vivo", True)

                if not vivo:
                    badges.append(f"[dim]☠ {nome}[/]")
                elif ativo:
                    badges.append(f"[bold yellow]▶ [{nome} ({iniciativa})][/]")
                elif tipo == "aliado":
                    badges.append(f"[cyan]🛡️ {nome}[/]")
                else:
                    badges.append(f"[red]👹 {nome}[/]")

            texto_timeline = f"⏳ [bold yellow]Rodada {self.rodada_atual}:[/] " + " ➔ ".join(badges)
            lbl.update(texto_timeline)
        except Exception as erro_timeline:
            logging.info(f"_atualizar_timeline_visual: {erro_timeline}")

    # ==========================================
    # POSICIONAMENTO E ANIMAÇÕES
    # ==========================================

    def _obter_largura_arena(self) -> float:
        try:
            arena = self.query_one("#arena")
            w = arena.content_size.width or arena.size.width
            if w > 10:
                return float(w)
        except Exception:
            pass
        return 80.0

    def _calcular_posicoes_aliados(self, n: int) -> list:
        center_x = self._obter_largura_arena() / 2.0
        base_x = max(4.0, center_x - 30.0)
        offsets = {1: [0.0], 2: [-4.0, 6.0], 3: [-8.0, 0.0, 8.0], 4: [-10.0, -3.0, 4.0, 11.0]}
        return [base_x + off for off in offsets.get(n, [0.0] * n)]

    def _calcular_posicoes_inimigos(self, n: int) -> list:
        center_x = self._obter_largura_arena() / 2.0
        base_x = center_x + 14.0
        offsets = {1: [0.0], 2: [-3.0, 7.0], 3: [-6.0, 2.0, 10.0], 4: [-7.0, 0.0, 7.0, 14.0]}
        return [base_x + off for off in offsets.get(n, [0.0] * n)]

    def _posicionar_sprites_iniciais(self) -> None:
        try:
            pos_aliados = self._calcular_posicoes_aliados(len(self.aliados_dados))
            for i, pos_x in enumerate(pos_aliados):
                sprite = self.query_one(f"#sprite-aliado-{i}", CombatenteSprite)
                sprite.x_pos = pos_x - 25.0

            pos_inimigos = self._calcular_posicoes_inimigos(len(self.inimigos_dados))
            for i, pos_x in enumerate(pos_inimigos):
                sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                sprite.x_pos = pos_x + 25.0
        except Exception as erro_pos:
            logging.info(f"_posicionar_sprites_iniciais: {erro_pos}")

    def _animar_entrada_sprites(self) -> None:
        try:
            pos_aliados = self._calcular_posicoes_aliados(len(self.aliados_dados))
            for i, pos_x in enumerate(pos_aliados):
                sprite = self.query_one(f"#sprite-aliado-{i}", CombatenteSprite)
                sprite.animate("x_pos", value=float(pos_x), duration=0.6)

            pos_inimigos = self._calcular_posicoes_inimigos(len(self.inimigos_dados))
            for i, pos_x in enumerate(pos_inimigos):
                sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                sprite.animate("x_pos", value=float(pos_x), duration=0.6)
        except Exception as erro_anim:
            logging.info(f"_animar_entrada_sprites: {erro_anim}")

    def _animar_ataque(self, fase: str, resultado: dict) -> None:
        """Anima ataque físico ou magia para o combatente da vez."""
        try:
            acao = resultado.get("acao", "ataque")
            idx_time = self.indice_aliado_ativo

            if fase == "jogador":
                sprite = self.query_one(f"#sprite-aliado-{idx_time}", CombatenteSprite)
                pos_orig = self._calcular_posicoes_aliados(len(self.aliados_dados))[min(idx_time, len(self.aliados_dados)-1)]
                pos_alvo = pos_orig + 20.0
            else:
                sprite = self.query_one(f"#sprite-inimigo-{idx_time}", CombatenteSprite)
                pos_orig = self._calcular_posicoes_inimigos(len(self.inimigos_dados))[min(idx_time, len(self.inimigos_dados)-1)]
                pos_alvo = pos_orig - 20.0

            if acao == "magia":
                magia_nome = resultado.get("magia", "").lower()
                emoji_magico = "🔥" if "fogo" in magia_nome else "⚡" if "raio" in magia_nome else "❄️" if "gelo" in magia_nome else "💚" if "cura" in magia_nome else "✨"

                arena = self.query_one("#arena")
                proj = EfeitoAtaque(emoji_magico, classes="efeito-ataque")
                proj.x_pos = pos_orig
                proj.y_pos = 2.0
                proj.styles.offset = (int(proj.x_pos), int(proj.y_pos))
                arena.mount(proj)
                proj.animate(
                    "x_pos",
                    value=pos_alvo,
                    duration=0.65,
                    on_complete=lambda: self._completar_magia_hit(proj, fase, resultado, sprite, pos_orig)
                )
            else:
                sprite.animate(
                    "x_pos",
                    value=pos_alvo,
                    duration=0.18,
                    on_complete=lambda: self._flash_impacto(fase, resultado, sprite, pos_orig)
                )
        except Exception as erro_atk:
            logging.info(f"_animar_ataque: {erro_atk}")

    def _completar_magia_hit(self, proj: EfeitoAtaque, fase: str, resultado: dict, sprite: CombatenteSprite, pos_orig: float) -> None:
        try:
            proj.remove()
        except Exception:
            pass
        self._flash_impacto(fase, resultado, sprite, pos_orig)

    def _flash_impacto(self, fase: str, resultado: dict, sprite: CombatenteSprite, pos_orig: float) -> None:
        acertou = resultado.get("acertou", False)
        acao = resultado.get("acao", "ataque")

        if acertou:
            classe_flash = "flash-magic" if acao == "magia" else "flash-red" if fase == "jogador" else "flash-blue"
            self._flash_tela(classe_flash)

            emoji_efeito = "💊" if acao in ["cura", "item"] else "✨" if acao == "magia" else "💥"
            self._mostrar_efeito_impacto(emoji_efeito, fase)

        sprite.animate("x_pos", value=pos_orig, duration=0.22)

    def _flash_tela(self, classe_css: str) -> None:
        def f_on(): self.screen.add_class(classe_css)
        def f_off(): self.screen.remove_class(classe_css)
        f_on()
        self.set_timer(0.08, f_off)
        self.set_timer(0.16, f_on)
        self.set_timer(0.24, f_off)

    def _mostrar_efeito_impacto(self, emoji: str, fase: str) -> None:
        try:
            arena = self.query_one("#arena")
            pos_x = self._obter_largura_arena() / 2.0 + (10.0 if fase == "jogador" else -10.0)
            efeito = EfeitoAtaque(emoji, classes="efeito-ataque")
            efeito.styles.offset = (int(pos_x), 2)
            arena.mount(efeito)
            self.set_timer(0.45, lambda: self._remover_efeito(efeito))
        except Exception as erro_efeito:
            logging.info(f"_mostrar_efeito_impacto: {erro_efeito}")

    def _remover_efeito(self, efeito: EfeitoAtaque) -> None:
        try:
            efeito.remove()
        except Exception:
            pass

    # ==========================================
    # CONFIRMAÇÃO DE AÇÕES DO JOGADOR
    # ==========================================

    @on(Button.Pressed, "#btn-confirmar-acao")
    def ao_confirmar_acao(self, event: Button.Pressed) -> None:
        if not self.turno_liberado or not self.battle_sys:
            return

        try:
            radioset = self.query_one("#action-radioset", RadioSet)
            id_botao = radioset.pressed_button.id if radioset.pressed_button else "act-atacar"
            mapeamento = {
                "act-atacar": "ataque",
                "act-magia": "magia",
                "act-item": "item",
                "act-defender": "defender",
                "act-fugir": "fugir",
            }
            acao = mapeamento.get(id_botao, "ataque")
        except Exception:
            acao = "ataque"

        alvo_index = 0
        try:
            target_rs = self.query_one("#target-radioset", RadioSet)
            if target_rs.pressed_button:
                alvo_index = int(str(target_rs.pressed_button.id).split("-")[1])
        except Exception:
            alvo_index = 0

        # Identifica o combatente ativo
        aliado_ativo = self.combatente_ativo_obj or self.heroi_personagem

        if acao == "fugir":
            self.turno_liberado = False
            self.battle_sys.executar_acao_jogador("fugir")
            return

        if acao == "defender":
            self.turno_liberado = False
            self.battle_sys.executar_acao_jogador("defender")
            return

        if acao == "magia":
            magias = getattr(aliado_ativo, "magias_conhecidas", [])
            magias_combate = [m for m in magias if getattr(m, "tipo_execucao", "combate") in ["combate", "ambos"]]
            if not magias_combate:
                self._escrever_log(f"[bold red]❌ {aliado_ativo.nome} não conhece magias de combate![/]")
                return

            def ao_escolher_magia(nome_magia_escolhida):
                if nome_magia_escolhida:
                    self.turno_liberado = False
                    self.battle_sys.executar_acao_jogador("magia", alvo_index=alvo_index, nome_magia=nome_magia_escolhida)

            self.app.push_screen(UsarMagiaBatalhaModal(magias_combate), ao_escolher_magia)
            return

        if acao == "item":
            # Coleta itens do inventário individual do personagem ativo
            itens_individuais = aliado_ativo.obter_itens_inventario() if hasattr(aliado_ativo, "obter_itens_inventario") else []
            from app.core.engine.components import InventoryComponent
            from app.core.engine.item_system import obter_itens_usaveis
            inv_ecs = esper.component_for_entity(1, InventoryComponent) if esper.has_component(1, InventoryComponent) else None
            itens_ecs = obter_itens_usaveis(inv_ecs) if inv_ecs else []

            itens_consolidados = []
            for it in itens_individuais:
                itens_consolidados.append({"nome": it["nome"], "quantidade": it["quantidade"], "emoji": "🧪", "descricao": "Item individual"})
            for it in itens_ecs:
                if not any(c["nome"].lower() == it["nome"].lower() for c in itens_consolidados):
                    itens_consolidados.append(it)

            if not itens_consolidados:
                self._escrever_log(f"[bold red]❌ {aliado_ativo.nome} não possui itens usáveis![/]")
                return

            def ao_escolher_item(nome_item_escolhido):
                if nome_item_escolhido:
                    self.turno_liberado = False
                    self.battle_sys.executar_acao_jogador("item", alvo_index=alvo_index, nome_item=nome_item_escolhido)

            self.app.push_screen(UsarItemBatalhaModal(itens_consolidados), ao_escolher_item)
            return

        # Ação de Ataque padrão
        self.turno_liberado = False
        self.battle_sys.executar_acao_jogador("ataque", alvo_index=alvo_index)

    # ==========================================
    # LOGS FORMATADOS
    # ==========================================

    def _escrever_log(self, texto: str) -> None:
        try:
            self.query_one("#battle-log", RichLog).write(texto)
        except Exception:
            pass

    def _escrever_log_turno(self, resultado: dict, fase: str) -> None:
        try:
            atacante = resultado.get("atacante", "?")
            alvo = resultado.get("alvo", "?")
            acertou = resultado.get("acertou", False)
            dano = resultado.get("dano_causado", 0)
            acao = resultado.get("acao", "ataque")
            prefixo = "🧙" if fase == "jogador" else "👹"

            if resultado.get("efeitos_processados"):
                for ef in resultado["efeitos_processados"]:
                    nome_ef = ef.get("nome", "Efeito")
                    val_ef = ef.get("valor", 0)
                    tipo_ef = ef.get("tipo")
                    alvo_ef = ef.get("personagem", atacante)
                    if tipo_ef == "dano_continuo":
                        self._escrever_log(f"🧪 [bold red]Veneno/Efeito {nome_ef}: {alvo_ef} sofreu -{val_ef} HP![/]")
                    elif tipo_ef == "cura_continua":
                        self._escrever_log(f"💊 [bold green]Regeneração {nome_ef}: {alvo_ef} recuperou +{val_ef} HP![/]")

            if acao == "defender":
                self._escrever_log(f"🛡️ [bold cyan]{resultado.get('descricao')}[/]")
                return

            if acao == "fugir":
                self._escrever_log(f"[yellow]{resultado.get('descricao')}[/]")
                return

            if acao == "item":
                self._escrever_log(f"🧪 [bold green]{resultado.get('descricao')}[/]")
                return

            if acao == "magia":
                magia = resultado.get("magia", "Magia")
                if resultado.get("dano_area"):
                    self._escrever_log(f"✨ [bold yellow]{atacante}[/] conjurou [bold yellow]{magia}[/] em [bold magenta]ÁREA[/]! Causou [red]{dano} de dano total[/]!")
                elif acertou:
                    cura = resultado.get("cura_realizada", 0)
                    if cura > 0:
                        self._escrever_log(f"💚 [bold yellow]{atacante}[/] conjurou [bold green]{magia}[/] em [bold]{alvo}[/]! (+{cura} HP)")
                    else:
                        self._escrever_log(f"✨ [bold yellow]{atacante}[/] conjurou [bold red]{magia}[/] contra [bold]{alvo}[/]! (-{dano} HP)")
                else:
                    self._escrever_log(f"✨ [dim]{atacante} tentou lançar {magia} contra {alvo}, mas o alvo esquivou/resistiu![/]")
                return

            if acertou:
                self._escrever_log(f"{prefixo} [bold]{atacante}[/] atacou [bold]{alvo}[/]! [red]💥 -{dano} HP[/]")
                if resultado.get("alvo_morreu"):
                    self._escrever_log(f"[bold red]☠ {alvo} foi derrotado![/]")
            else:
                self._escrever_log(f"{prefixo} [dim]{atacante} errou o golpe contra {alvo}! (Esquiva)[/]")

        except Exception as erro_log:
            logging.info(f"_escrever_log_turno: {erro_log}")

    def _fechar_tela_combate(self, resultado: str) -> None:
        self._sincronizar_combate_para_ecs()
        esper.dispatch_event("combate_finalizado_gui", resultado)
        self.app.pop_screen()

    def _sincronizar_combate_para_ecs(self) -> None:
        if not self.battle_sys or not self.battle_sys.heroi:
            return
        try:
            from app.core.engine.components import StatsComponent, EquipmentComponent
            if esper.has_component(1, StatsComponent):
                stats = esper.component_for_entity(1, StatsComponent)
                heroi = self.battle_sys.heroi
                stats.hp = max(0, int(heroi.pv_atual))
                stats.mp = max(0, int(heroi.pm_atual))
                stats.max_hp = int(heroi.max_hp)
                stats.max_mp = int(heroi.max_mp)
                stats.atributos = dict(heroi.atributos_totais)

            if esper.has_component(1, EquipmentComponent):
                eqp = esper.component_for_entity(1, EquipmentComponent)
                heroi = self.battle_sys.heroi
                if getattr(heroi, "mao_direita", None):
                    eqp.arma = {
                        "nome": heroi.mao_direita.nome,
                        "bonus_atk": getattr(heroi.mao_direita, "dano", 0),
                        "emoji": getattr(heroi.mao_direita, "emoji", "🗡️")
                    }
                else:
                    eqp.arma = None

                if getattr(heroi, "armadura", None):
                    eqp.armadura = {
                        "nome": heroi.armadura.nome,
                        "bonus_def": getattr(heroi.armadura, "defesa", 0),
                        "emoji": getattr(heroi.armadura, "emoji", "🛡️")
                    }
                else:
                    eqp.armadura = None
        except Exception as erro_sync:
            logging.info(f"Erro ao sincronizar combate para ECS: {erro_sync}")

    def _criar_personagem_inimigo(self, dados: dict) -> Any:
        from app.core.entities.personagens import Personagem, Raca, ClasseRPG
        raca = Raca(nome=dados.get("raca", "Monstro"), bonus_atributos={}, emoji=dados.get("emoji", "👹"))
        classe = ClasseRPG(nome=dados.get("classe", "Monstro"))
        p = Personagem(
            nome=dados.get("nome", "Inimigo"),
            nivel=int(dados.get("nivel", 1)),
            raca=raca,
            classe_rpg=classe,
            forca_base=int(dados.get("forca", 2)),
            agilidade_base=int(dados.get("agilidade", 1)),
            res_base=int(dados.get("resistencia", 2)),
            perc_base=int(dados.get("percepcao", 1)),
            exub_base=int(dados.get("exuberancia", 0)),
        )
        p.pv_atual = int(dados.get("pv_atual", p.max_hp))
        p.pm_atual = int(dados.get("pm_atual", p.max_mp))
        return p


# ==============================================================================
# MODAIS DE ITENS E MAGIAS
# ==============================================================================

class UsarItemBatalhaModal(ModalScreen[Optional[str]]):
    """Modal para escolha de itens usáveis pelo combatente ativo."""
    CSS_PATH = "styles/battle_styles.css"

    def __init__(self, itens_usaveis: list):
        super().__init__()
        self.itens_usaveis = itens_usaveis
        self.item_selecionado = None

    def compose(self):
        with Vertical(id="batalha-item-dialog"):
            yield Label("🧪 Itens do Combatente", classes="painel-titulo")
            yield ListView(id="list-itens-batalha")
            yield Static("Selecione um item da lista.", id="lbl-batalha-item-desc")
            with Horizontal(id="batalha-item-botoes"):
                yield Button("✨ Usar Item", id="btn-confirmar-item-batalha", variant="success", disabled=True)
                yield Button("Cancelar", id="btn-cancelar-item-batalha", variant="error")

    def on_mount(self) -> None:
        list_view = self.query_one("#list-itens-batalha", ListView)
        for item in self.itens_usaveis:
            widget = ListItem(
                Label(f"{item.get('emoji', '🧪')} {item['nome']} (x{item['quantidade']}) — {item.get('descricao', '')}"),
                name=item['nome']
            )
            list_view.append(widget)
        if not self.itens_usaveis:
            self.query_one("#lbl-batalha-item-desc", Static).update("Nenhum item usável.")

    @on(ListView.Highlighted, "#list-itens-batalha")
    def on_item_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.item_selecionado = event.item.name
            self.query_one("#lbl-batalha-item-desc", Static).update(f"Usar: [bold yellow]{self.item_selecionado}[/]")
            self.query_one("#btn-confirmar-item-batalha", Button).disabled = False

    @on(ListView.Selected, "#list-itens-batalha")
    def on_item_selected(self, event: ListView.Selected):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.dismiss(event.item.name)

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirmar-item-batalha":
            self.dismiss(self.item_selecionado)
        elif event.button.id == "btn-cancelar-item-batalha":
            self.dismiss(None)


class UsarMagiaBatalhaModal(ModalScreen[Optional[str]]):
    """Modal para escolha de magias/habilidades do combatente ativo."""
    CSS_PATH = "styles/battle_styles.css"

    def __init__(self, magias_disponiveis: list):
        super().__init__()
        self.magias_disponiveis = magias_disponiveis
        self.magia_selecionada = None

    def compose(self):
        with Vertical(id="batalha-magia-dialog"):
            yield Label("🪄 Habilidades e Magias", classes="painel-titulo")
            yield ListView(id="list-magias-batalha")
            yield Static("Selecione uma magia da lista.", id="lbl-batalha-magia-desc")
            with Horizontal(id="batalha-magia-botoes"):
                yield Button("✨ Conjurar", id="btn-confirmar-magia-batalha", variant="success", disabled=True)
                yield Button("Cancelar", id="btn-cancelar-magia-batalha", variant="error")

    def on_mount(self) -> None:
        list_view = self.query_one("#list-magias-batalha", ListView)
        for magia in self.magias_disponiveis:
            nome = getattr(magia, "nome", "")
            custo_pm = getattr(magia, "custo_pm", 0)
            dano = getattr(magia, "dano_base", 0)
            cura = getattr(magia, "cura_base", 0)
            area = " [ÁREA]" if getattr(magia, "dano_area", False) else ""
            desc = f"Dano: {dano}{area}" if dano > 0 else f"Cura: {cura}{area}" if cura > 0 else "Suporte"

            widget = ListItem(
                Label(f"✨ {nome} (🔮 {custo_pm} PM) — {desc}"),
                name=nome
            )
            list_view.append(widget)
        if not self.magias_disponiveis:
            self.query_one("#lbl-batalha-magia-desc", Static).update("Nenhuma magia conhecida.")

    @on(ListView.Highlighted, "#list-magias-batalha")
    def on_magia_highlighted(self, event: ListView.Highlighted):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.magia_selecionada = event.item.name
            self.query_one("#lbl-batalha-magia-desc", Static).update(f"Conjurar: [bold yellow]{self.magia_selecionada}[/]")
            self.query_one("#btn-confirmar-magia-batalha", Button).disabled = False

    @on(ListView.Selected, "#list-magias-batalha")
    def on_magia_selected(self, event: ListView.Selected):
        if event.item and hasattr(event.item, "name") and event.item.name:
            self.dismiss(event.item.name)

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirmar-magia-batalha":
            self.dismiss(self.magia_selecionada)
        elif event.button.id == "btn-cancelar-magia-batalha":
            self.dismiss(None)
