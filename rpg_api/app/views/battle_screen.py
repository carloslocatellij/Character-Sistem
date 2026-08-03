"""
Tela de Combate por Turnos — BattleScreen

Interface TUI do sistema de combate usando o framework Textual.
Segue estritamente a Arquitetura Limpa: esta tela APENAS escuta eventos do BattleSystem
e redesenha a si mesma de forma reativa. Nunca calcula dano ou lógica de jogo.

Fluxo de uso:
    # Para iniciar o combate com 1 a 4 inimigos a partir do GamePlayScreen:
    self.app.push_screen(BattleScreen(heroi_personagem, [dados_inimigo1, dados_inimigo2]))

    # Retrocompatível com dict único:
    self.app.push_screen(BattleScreen(heroi_personagem, dados_inimigo_dict))

    # A tela se fecha automaticamente ao fim do combate:
    self.app.pop_screen()
"""
import esper
import logging
from typing import Optional, Any

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
# Baseado no poc_animation.py: usa reactive + animate para movimentação fluida
# ==============================================================================

class CombatenteSprite(Static):
    """
    Widget de sprite do combatente com posição X animável via reactive.
    Seguindo o padrão do poc_animation.py: animamos a propriedade numérica pura
    x_pos, e o watcher atualiza o offset CSS de forma reativa e sem AssertionError.
    """

    x_pos: reactive[float] = reactive(0.0)
    y_pos: reactive[float] = reactive(3.0)

    def watch_x_pos(self, novo_x: float) -> None:
        """Sempre que x_pos mudar (via animação), atualiza o offset visual do sprite."""
        self.styles.offset = (int(novo_x), int(self.y_pos))

    def watch_y_pos(self, novo_y: float) -> None:
        self.styles.offset = (int(self.x_pos), int(novo_y))


# ==============================================================================
# WIDGET DE EFEITO DE ATAQUE (💥 ✨ 💊)
# ==============================================================================

class EfeitoAtaque(Static):
    """
    Emoji de impacto que aparece brevemente na arena durante o ataque.
    Criado dinamicamente e removido após 0.5s (Regra 3: sem bloqueio de thread).
    """
    pass


# ==============================================================================
# WIDGET DE BARRA DE STATUS REATIVA (versão compacta para colunas laterais)
# ==============================================================================

class BarraStatusCombate(Widget):
    """
    Widget composto de barra de status (nome + HP bar + MP bar) para um combatente.
    Versão compacta com layout vertical para encaixar nas colunas laterais estreitas.
    As barras atualizam-se de forma reativa via métodos externos.
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
    ):
        super().__init__(id=widget_id if widget_id else None, classes=classes_css if classes_css else "")
        self._nome = nome
        self._hp_atual = hp_atual
        self._hp_max = hp_max
        self._mp_atual = mp_atual
        self._mp_max = mp_max

    def compose(self):
        yield Label(self._nome, classes="combatente-nome")
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
            total=max(1, self._mp_max),
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

    def atualizar(self, hp_atual: int, hp_max: int, mp_atual: int, mp_max: int) -> None:
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

            self.query_one(f"#{self.id}-hp-label", Label).update(
                f"💟 {self._hp_atual}/{self._hp_max}"
            )
            self.query_one(f"#{self.id}-mp-label", Label).update(
                f"🔮 {self._mp_atual}/{self._mp_max}"
            )
        except Exception as erro_update:
            logging.info(f"BarraStatusCombate.atualizar: {erro_update}")


# ==============================================================================
# TELA PRINCIPAL DE COMBATE
# ==============================================================================

class BattleScreen(Screen):
    """
    Tela de combate por turnos — suporta 1 a 4 inimigos.

    Princípio fundamental (Regra 1 - Arquitetura Limpa):
    - Esta tela APENAS escuta eventos do BattleSystem e redesenha widgets.
    - NUNCA calcula dano, iniciativa ou lógica de jogo.
    - Toda matemática é delegada ao BattleSystem (Domínio Core).

    Layout de 3 colunas:
    ┌────────────┬──────────────────────┬────────────┐
    │  ALIADOS   │   ARENA + LOG + AÇÃO │  INIMIGOS  │
    └────────────┴──────────────────────┴────────────┘

    Lifecycle:
        push_screen(BattleScreen(heroi, [dados_inimigo1, ...]))  → inicia combate
        app.pop_screen()                                          → volta ao mapa
    """

    CSS_PATH = "styles/battle_styles.css"

    # Variáveis reativas — qualquer mudança aqui dispara automaticamente os watchers
    heroi_hp: reactive[int] = reactive(0)
    heroi_mp: reactive[int] = reactive(0)
    heroi_hp_max: reactive[int] = reactive(100)
    heroi_mp_max: reactive[int] = reactive(100)
    turno_liberado: reactive[bool] = reactive(True)

    # ==========================================
    # MENSAGEM CUSTOMIZADA: Ação do Jogador
    # ==========================================
    class AcaoConfirmada(Message):
        """
        Mensagem interna emitida quando o jogador confirma sua ação.
        Segue o padrão da Regra 3: propriedade `control` obrigatória
        para evitar OnDecoratorError no Textual.
        """

        def __init__(self, control: Widget, acao: str) -> None:
            super().__init__()
            self._control = control
            self.acao = acao

        @property
        def control(self) -> Widget:
            return self._control

    def __init__(
        self,
        heroi_personagem: Any,
        inimigos_dados,
    ):
        super().__init__()
        self.heroi_personagem = heroi_personagem
        # Retrocompatível: aceita dict único ou lista de dicts
        if isinstance(inimigos_dados, dict):
            self.inimigos_dados = [inimigos_dados]
        else:
            self.inimigos_dados = list(inimigos_dados)[:4]  # Máximo de 4 inimigos
        self.battle_sys: Optional[Any] = None

    # ==========================================
    # COMPOSIÇÃO DA INTERFACE — Layout 3 colunas
    # ==========================================

    def compose(self):
        with Horizontal(id="battle-layout"):

            # ─── COLUNA ESQUERDA: ALIADOS ───────────────────────────────────
            with Vertical(id="painel-aliados"):
                yield Label("🎯 ALIADOS", classes="painel-titulo")
                yield BarraStatusCombate(
                    nome=f"🧙 {getattr(self.heroi_personagem, 'nome', 'Herói')}",
                    hp_atual=getattr(self.heroi_personagem, 'pv_atual', 50),
                    hp_max=getattr(self.heroi_personagem, 'max_hp', 100),
                    mp_atual=getattr(self.heroi_personagem, 'pm_atual', 20),
                    mp_max=getattr(self.heroi_personagem, 'max_mp', 50),
                    widget_id="barra-heroi",
                    classes_css="barra-aliado",
                )

            # ─── COLUNA CENTRAL: ARENA + LOG + AÇÕES ────────────────────────
            with Vertical(id="painel-central"):

                # Arena de sprites animados
                with Container(id="arena"):
                    yield Label("VS", id="lbl-vs")
                    yield CombatenteSprite(
                        getattr(self.heroi_personagem, 'raca', None) and
                        str(getattr(self.heroi_personagem, 'raca', '🧙')) or "🧙",
                        id="sprite-heroi",
                        classes="combatente heroi-side",
                    )
                    # Sprites dos inimigos distribuídos na arena
                    for i, dados in enumerate(self.inimigos_dados):
                        yield CombatenteSprite(
                            dados.get("emoji", "👹"),
                            id=f"sprite-inimigo-{i}",
                            classes="combatente inimigo-side",
                        )

                # Log de batalha
                yield RichLog(id="battle-log", highlight=True, markup=True, wrap=True)

                # Painel de ações do jogador
                with Container(id="action-panel"):
                    with Horizontal(id="action-horizontal"):

                        # Coluna de ações
                        with Vertical(id="acao-coluna"):
                            yield Label("🎯  Escolha sua ação:", id="action-label")
                            with RadioSet(id="action-radioset"):
                                yield RadioButton("🎯  Atacar", value=True, id="act-atacar")
                                yield RadioButton("🪄  Magia", id="act-magia")
                                yield RadioButton("🧪  Usar Item", id="act-item")
                                yield RadioButton("🏃  Fugir do Combate", id="act-fugir")

                        # Coluna de seleção de alvo (visível apenas com múltiplos inimigos)
                        with Vertical(
                            id="alvo-coluna",
                            classes="" if len(self.inimigos_dados) > 1 else "oculto"
                        ):
                            yield Label("🎯 Alvo:", id="target-label")
                            with RadioSet(id="target-radioset"):
                                for i, dados in enumerate(self.inimigos_dados):
                                    yield RadioButton(
                                        f"{dados.get('emoji', '👹')} {dados.get('nome', 'Inimigo')}",
                                        value=(i == 0),
                                        id=f"target-{i}",
                                    )

                    yield Button(
                        "✅  Confirmar Ação",
                        variant="success",
                        id="btn-confirmar-acao",
                    )

            # ─── COLUNA DIREITA: INIMIGOS ────────────────────────────────────
            with Vertical(id="painel-inimigos"):
                yield Label("👹 INIMIGOS", classes="painel-titulo")
                for i, dados in enumerate(self.inimigos_dados):
                    yield BarraStatusCombate(
                        nome=f"{dados.get('emoji', '👹')} {dados.get('nome', 'Inimigo')}",
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
        """Registra handlers do Esper, posiciona sprites e inicia o combate via BattleSystem."""
        # Registra os listeners de eventos do motor de combate
        esper.set_handler("combate_iniciado", self._ao_combate_iniciado)
        esper.set_handler("turno_calculado", self._ao_turno_calculado)
        esper.set_handler("combate_encerrado", self._ao_combate_encerrado)

        # Posiciona os sprites dos inimigos na arena de forma distribuída
        self.call_next(self._posicionar_sprites_iniciais)

        # Obtém o BattleSystem registrado no Esper
        from app.core.engine.systems import BattleSystem
        self.battle_sys = esper.get_processor(BattleSystem)

        if self.battle_sys:
            inimigos = [self._criar_personagem_inimigo(d) for d in self.inimigos_dados]
            self.battle_sys.iniciar_combate(self.heroi_personagem, inimigos)
        else:
            self._escrever_log("[bold red]❌ Erro: BattleSystem não encontrado no Esper![/]")
            logging.error("BattleScreen: BattleSystem não está registrado no Esper.")

    def on_unmount(self) -> None:
        """Remove os handlers do Esper ao fechar a tela para evitar memory leaks."""
        try:
            esper.remove_handler("combate_iniciado", self._ao_combate_iniciado)
            esper.remove_handler("turno_calculado", self._ao_turno_calculado)
            esper.remove_handler("combate_encerrado", self._ao_combate_encerrado)
        except Exception as erro_unmount:
            logging.info(f"BattleScreen.on_unmount: {erro_unmount}")

    # ==========================================
    # WATCHERS REATIVOS (redesenho automático)
    # ==========================================

    def watch_heroi_hp(self, novo_hp: int) -> None:
        """Atualiza a barra de HP do herói sempre que o valor reativo muda."""
        try:
            barra = self.query_one("#barra-heroi", BarraStatusCombate)
            barra.atualizar(novo_hp, self.heroi_hp_max, self.heroi_mp, self.heroi_mp_max)
        except Exception:
            pass

    def watch_heroi_mp(self, novo_mp: int) -> None:
        try:
            barra = self.query_one("#barra-heroi", BarraStatusCombate)
            barra.atualizar(self.heroi_hp, self.heroi_hp_max, novo_mp, self.heroi_mp_max)
        except Exception:
            pass

    def watch_turno_liberado(self, liberado: bool) -> None:
        """Habilita/desabilita o painel de ações conforme o estado do turno."""
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
        """
        Callback disparado pelo BattleSystem quando o combate é configurado.
        Inicializa os valores reativos, atualiza barras de inimigos e lança animação de entrada.
        """
        heroi = dados.get("heroi")
        inimigos = dados.get("inimigos", [dados.get("inimigo")] if dados.get("inimigo") else [])
        iniciativa_jogador = dados.get("iniciativa_jogador", 0)
        iniciativa_inimigo = dados.get("iniciativa_inimigo", 0)
        heroi_vai_primeiro = dados.get("heroi_vai_primeiro", True)

        if heroi:
            self.heroi_hp_max = heroi.max_hp
            self.heroi_mp_max = heroi.max_mp
            self.heroi_hp = heroi.pv_atual
            self.heroi_mp = heroi.pm_atual

        # Inicializa as barras dos inimigos com os valores reais do BattleSystem
        for i, inimigo in enumerate(inimigos):
            try:
                barra = self.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
                barra.atualizar(inimigo.pv_atual, inimigo.max_hp, 0, 1)
            except Exception:
                pass

        nomes_inimigos = " | ".join(getattr(e, 'nome', '?') for e in inimigos)
        self._escrever_log("[bold yellow]══════════════════════════════[/]")
        self._escrever_log(
            f"[bold red]🎇  COMBATE INICIADO![/]  "
            f"[cyan]{getattr(heroi, 'nome', '?')}[/] vs [red]{nomes_inimigos}[/]"
        )
        self._escrever_log(
            f"[dim]🎲 Iniciativa: Herói={iniciativa_jogador} | "
            f"Inimigos={iniciativa_inimigo}[/]"
        )
        if heroi_vai_primeiro:
            self._escrever_log("[green]▶ Você age primeiro![/]")
        else:
            self._escrever_log("[orange1]▶ Os inimigos agem primeiro![/]")
        self._escrever_log("[bold yellow]══════════════════════════════[/]")

        # Animação de entrada dos sprites
        self.call_next(self._animar_entrada_sprites)

        # Se inimigos vão primeiro, desabilita ações e agenda o turno da IA
        if not heroi_vai_primeiro:
            self.turno_liberado = False
            if self.battle_sys:
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    loop.call_soon(self.battle_sys._agendar_turno_inimigo)
                except Exception as erro_ia:
                    logging.info(f"Erro ao agendar IA no início: {erro_ia}")

    def _ao_turno_calculado(self, dados: dict) -> None:
        """
        Callback disparado pelo BattleSystem após calcular um turno.
        Atualiza os valores reativos e dispara as animações de combate.
        """
        fase = dados.get("fase", "jogador")
        resultado = dados.get("resultado", {})
        
        # Se houve erro ao tentar usar um item (ex: não possui poção no inventário)
        if resultado.get("erro_item"):
            self._escrever_log(f"[bold red]❌ {resultado['erro_item']}[/]")
            self.turno_liberado = True
            return

        novo_heroi_hp = dados.get("heroi_hp", self.heroi_hp)
        lista_inimigos = dados.get("inimigos", [])

        # Atualiza reativos do herói — dispara watchers automaticamente
        self.heroi_hp = novo_heroi_hp
        self.heroi_mp = dados.get("heroi_mp", self.heroi_mp)

        # Atualiza barras de TODOS os inimigos com o estado atual
        for info in lista_inimigos:
            i = info.get("index", 0)
            try:
                barra = self.query_one(f"#barra-inimigo-{i}", BarraStatusCombate)
                barra.atualizar(info["hp"], info["hp_max"], 0, 1)
                # Marca visualmente o inimigo derrotado
                if not info["vivo"]:
                    barra.add_class("combatente-derrotado")
                    try:
                        sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                        sprite.add_class("sprite-derrotado")
                    except Exception:
                        pass
            except Exception:
                pass

        # Escreve o log narrativo do turno
        self._escrever_log_turno(resultado, fase)

        # Dispara animação conforme o atacante do turno
        if fase == "jogador":
            self.call_next(lambda: self._animar_ataque("heroi", resultado))
        else:
            self.call_next(lambda: self._animar_ataque("inimigo", resultado))
            # Libera o painel de ações para o próximo turno do jogador
            self.set_timer(1.5, lambda: setattr(self, "turno_liberado", True))

    def _ao_combate_encerrado(self, dados: dict) -> None:
        """Callback disparado quando o combate termina (vitória ou derrota)."""
        vencedor = dados.get("vencedor", "jogador")

        self.turno_liberado = False

        if vencedor == "jogador":
            resultado_final = "venceu"
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
            self._escrever_log("[bold green]🏆  VITÓRIA! Você derrotou todos os inimigos![/]")
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
            self.screen.add_class("vitoria")
        elif vencedor == "inimigo_fugiu":
            resultado_final = "inimigo_fugiu"
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
            self._escrever_log("[bold green]💨 O inimigo fugiu da batalha![/]")
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
        else:
            resultado_final = "perdeu"
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
            self._escrever_log("[bold red]💀  DERROTA! Você foi derrotado...[/]")
            self._escrever_log("[bold yellow]══════════════════════════════[/]")
            self.screen.add_class("derrota")

        # Fecha a tela após 2.5 segundos para o jogador ler o resultado
        self.set_timer(2.5, lambda: self._fechar_tela_combate(resultado_final))

    # ==========================================
    # ANIMAÇÕES (padrão poc_animation.py)
    # ==========================================

    def _posicionar_sprites_iniciais(self) -> None:
        """Posiciona os sprites de inimigos de forma distribuída na arena antes da animação."""
        try:
            n_inimigos = len(self.inimigos_dados)
            # Posições X dos inimigos na arena (distribuídas entre 50% e 90% da arena)
            posicoes_x_inimigos = self._calcular_posicoes_inimigos(n_inimigos)
            for i, pos_x in enumerate(posicoes_x_inimigos):
                sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                sprite.x_pos = pos_x + 30.0  # Começa fora da tela para a animação de entrada
        except Exception as erro_pos:
            logging.info(f"_posicionar_sprites_iniciais: {erro_pos}")

    def _calcular_posicoes_inimigos(self, n: int) -> list:
        """Calcula as posições X finais de N inimigos distribuídos na metade direita da arena."""
        # Arena centralizada: posições de destino entre 45 e 80
        base = [45, 58, 52, 65]
        if n == 1:
            return [52]
        elif n == 2:
            return [46, 60]
        elif n == 3:
            return [44, 54, 64]
        else:
            return base[:n]

    def _animar_entrada_sprites(self) -> None:
        """Sprites entram animados a partir das bordas da arena."""
        try:
            sprite_heroi = self.query_one("#sprite-heroi", CombatenteSprite)
            sprite_heroi.x_pos = -8.0
            sprite_heroi.animate("x_pos", value=8.0, duration=0.6)

            n_inimigos = len(self.inimigos_dados)
            posicoes_finais = self._calcular_posicoes_inimigos(n_inimigos)
            for i, pos_x_final in enumerate(posicoes_finais):
                try:
                    sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                    sprite.x_pos = pos_x_final + 30.0  # Sai de fora da tela
                    sprite.animate("x_pos", value=float(pos_x_final), duration=0.6)
                except Exception:
                    pass
        except Exception as erro_anim:
            logging.info(f"_animar_entrada_sprites: {erro_anim}")

    def _animar_ataque(self, atacante: str, resultado: dict) -> None:
        """Anima o sprite do atacante avançando sobre o alvo e recuando."""
        try:
            if atacante == "heroi":
                sprite = self.query_one("#sprite-heroi", CombatenteSprite)
                posicao_original = 8.0
                posicao_ataque = 40.0
            else:
                # Encontra o inimigo atacante pelo nome no resultado
                nome_atacante = resultado.get("atacante", "")
                sprite = None
                posicao_original = 52.0
                posicao_ataque = 18.0
                for i, dados in enumerate(self.inimigos_dados):
                    if dados.get("nome", "") == nome_atacante or i == 0:
                        try:
                            sprite = self.query_one(f"#sprite-inimigo-{i}", CombatenteSprite)
                            posicoes = self._calcular_posicoes_inimigos(len(self.inimigos_dados))
                            posicao_original = float(posicoes[i])
                            posicao_ataque = 18.0
                        except Exception:
                            pass
                        break
                if sprite is None:
                    try:
                        sprite = self.query_one("#sprite-inimigo-0", CombatenteSprite)
                    except Exception:
                        return

            sprite.animate(
                "x_pos",
                value=posicao_ataque,
                duration=0.18,
                on_complete=lambda: self._flash_impacto(atacante, resultado, sprite, posicao_original),
            )
        except Exception as erro_ataque:
            logging.info(f"_animar_ataque: {erro_ataque}")

    def _flash_impacto(
        self, atacante: str, resultado: dict, sprite: CombatenteSprite, posicao_original: float
    ) -> None:
        """Efeito visual de impacto: flash piscante na tela + emoji 💥 na arena + recuo do sprite."""
        acertou = resultado.get("acertou", False)
        acao = resultado.get("acao", "ataque")

        if acertou:
            # Flash de tela piscando 2x (mais dramático)
            classe_flash = "flash-red" if atacante == "heroi" else "flash-blue"
            self._flash_tela(classe_flash)

            # Emoji de impacto na arena
            if acao == "magia":
                emoji_efeito = "✨"
            elif acao == "cura":
                emoji_efeito = "💊"
            else:
                emoji_efeito = "💥"
            self._mostrar_efeito_impacto(emoji_efeito, atacante)

        # Recua o sprite para a posição original
        sprite.animate("x_pos", value=posicao_original, duration=0.25)

    def _flash_tela(self, classe_css: str) -> None:
        """Faz a tela piscar 2x com a classe CSS de cor de impacto (efeito dramático)."""
        def flash_on():  self.screen.add_class(classe_css)
        def flash_off(): self.screen.remove_class(classe_css)
        flash_on()
        self.set_timer(0.15, flash_off)
        self.set_timer(0.30, flash_on)
        self.set_timer(0.45, flash_off)

    def _mostrar_efeito_impacto(self, emoji: str, atacante: str) -> None:
        """
        Cria um EfeitoAtaque dinâmico na arena e o remove após 0.5s.
        Posiciona o emoji no lado do alvo (herói ataca → emoji no lado inimigo, e vice-versa).
        """
        try:
            arena = self.query_one("#arena")
            # Posição do emoji: do lado do alvo
            pos_x = 38 if atacante == "heroi" else 12
            efeito = EfeitoAtaque(emoji, classes="efeito-ataque")
            efeito.styles.offset = (pos_x, 2)
            arena.mount(efeito)
            self.set_timer(0.5, lambda: self._remover_efeito(efeito))
        except Exception as erro_efeito:
            logging.info(f"_mostrar_efeito_impacto: {erro_efeito}")

    def _remover_efeito(self, efeito: EfeitoAtaque) -> None:
        """Remove o widget de efeito de forma segura."""
        try:
            efeito.remove()
        except Exception:
            pass

    # ==========================================
    # HANDLER DE AÇÃO DO JOGADOR (RadioSet + Button)
    # ==========================================

    @on(Button.Pressed, "#btn-confirmar-acao")
    def ao_confirmar_acao(self, event: Button.Pressed) -> None:
        """
        Captura a ação selecionada pelo jogador no RadioSet e o alvo no TargetRadioSet.
        Envia ao BattleSystem via executar_acao_jogador(acao, alvo_index).
        Desabilita o painel para evitar múltiplos cliques durante o processamento.
        """
        if not self.turno_liberado:
            return

        # Detecta a ação escolhida
        try:
            radioset = self.query_one("#action-radioset", RadioSet)
            if radioset.pressed_button is None:
                return

            mapeamento_acoes = {
                "act-atacar": "ataque",
                "act-magia": "magia",
                "act-item": "item",
                "act-fugir": "fugir",
            }
            id_botao = radioset.pressed_button.id
            acao = mapeamento_acoes.get(id_botao, "ataque")

        except Exception as erro_radioset:
            logging.info(f"Erro ao capturar ação do RadioSet: {erro_radioset}")
            acao = "ataque"

        # Detecta o alvo selecionado (0 se painel de alvo oculto)
        alvo_index = 0
        try:
            target_rs = self.query_one("#target-radioset", RadioSet)
            if target_rs.pressed_button:
                target_id = target_rs.pressed_button.id  # "target-0", "target-1", etc.
                alvo_index = int(str(target_id).split("-")[1])
        except Exception:
            alvo_index = 0

        if acao == "fugir":
            self._escrever_log("[dim]🏃 Você fugiu do combate![/]")
            self.set_timer(0.8, lambda: self._fechar_tela_combate("fugiu"))
            return

        if acao == "item":
            from app.core.engine.components import InventoryComponent
            inv = esper.component_for_entity(1, InventoryComponent) if esper.has_component(1, InventoryComponent) else None
            from app.core.engine.item_system import obter_itens_usaveis
            itens_usaveis = obter_itens_usaveis(inv) if inv else []

            if not itens_usaveis:
                self._escrever_log("[bold red]❌ Você não possui nenhum item usável no inventário![/]")
                return

            def ao_escolher_item(nome_item_escolhido):
                if nome_item_escolhido:
                    self.turno_liberado = False
                    if self.battle_sys:
                        self.battle_sys.executar_acao_jogador("item", alvo_index=alvo_index, nome_item=nome_item_escolhido)

            self.app.push_screen(UsarItemBatalhaModal(itens_usaveis), ao_escolher_item)
            return

        # Desabilita o painel durante o processamento do turno
        self.turno_liberado = False

        if self.battle_sys:
            self.battle_sys.executar_acao_jogador(acao, alvo_index=alvo_index)

    # ==========================================
    # UTILITÁRIOS INTERNOS
    # ==========================================

    def _escrever_log(self, texto: str) -> None:
        """Escreve uma linha formatada no log de batalha."""
        try:
            log = self.query_one("#battle-log", RichLog)
            log.write(texto)
        except Exception as erro_log:
            logging.info(f"BattleScreen._escrever_log: {erro_log}")

    def _escrever_log_turno(self, resultado: dict, fase: str) -> None:
        """Formata e escreve o relatório narrativo de um turno no log."""
        try:
            atacante_nome = resultado.get("atacante", "?")
            alvo_nome = resultado.get("alvo", "?")
            acertou = resultado.get("acertou", False)
            dano_causado = resultado.get("dano_causado", 0)
            acao = resultado.get("acao", "ataque")

            prefixo = "🧙" if fase == "jogador" else "👹"

            if acao == "cura":
                descricao = resultado.get("descricao", f"{atacante_nome} se recuperou.")
                self._escrever_log(f"{prefixo} [dim]{descricao}[/]")
                return

            if acertou:
                dano_bruto = resultado.get("dano_bruto", dano_causado)
                defesa = resultado.get("defesa_total", 0)
                self._escrever_log(
                    f"{prefixo} [bold]{atacante_nome}[/] acertou [bold]{alvo_nome}[/]! "
                    f"[red]💥 -{dano_causado} HP[/] "
                    f"[dim](bruto:{dano_bruto} | bloq:{defesa})[/]"
                )
                if resultado.get("alvo_morreu"):
                    self._escrever_log(f"[bold red]☠ {alvo_nome} foi derrotado![/]")
            else:
                self._escrever_log(
                    f"{prefixo} [dim]{atacante_nome} errou o ataque contra {alvo_nome}! (Esquiva)[/]"
                )
        except Exception as erro_log:
            logging.info(f"BattleScreen._escrever_log_turno: {erro_log}")

    def _fechar_tela_combate(self, resultado: str) -> None:
        """Encerra a tela de combate e devolve o controle à tela principal."""
        self._sincronizar_combate_para_ecs()
        if resultado == "venceu":
            esper.dispatch_event("combate_finalizado_gui", "venceu")
        elif resultado == "perdeu":
            esper.dispatch_event("combate_finalizado_gui", "perdeu")
        else:
            esper.dispatch_event("combate_finalizado_gui", "fugiu")
        self.app.pop_screen()

    def _sincronizar_combate_para_ecs(self) -> None:
        """Sincroniza o status atual (HP/Mana) e equipamentos do herói da batalha de volta para o ECS."""
        if not self.battle_sys or not self.battle_sys.heroi:
            return
            
        try:
            from app.core.engine.components import StatsComponent, EquipmentComponent
            stats = esper.component_for_entity(1, StatsComponent)
            if stats:
                heroi = self.battle_sys.heroi
                stats.hp = max(0, int(heroi.pv_atual))
                stats.mp = max(0, int(heroi.pm_atual))
                stats.max_hp = int(heroi.max_hp)
                stats.max_mp = int(heroi.max_mp)
                logging.info(f"Sincronização combate -> ECS realizada com sucesso. HP={stats.hp}, MP={stats.mp}")
                
            eqp = esper.component_for_entity(1, EquipmentComponent)
            if eqp:
                heroi = self.battle_sys.heroi
                
                # Mapeia mao_direita (Arma) para eqp.arma
                if heroi.mao_direita:
                    eqp.arma = {
                        "nome": heroi.mao_direita.nome,
                        "bonus_atk": getattr(heroi.mao_direita, "dano", 3),
                        "tipo": getattr(heroi.mao_direita, "tipo", "corpo")
                    }
                else:
                    eqp.arma = None
                
                # Mapeia mao_esquerda (Escudo ou Arma) e armadura para eqp.armadura / eqp.escudo
                from app.core.entities.equipamentos import Escudo
                if isinstance(heroi.mao_esquerda, Escudo):
                    eqp.escudo = {
                        "nome": heroi.mao_esquerda.nome,
                        "bonus_def": getattr(heroi.mao_esquerda, "defesa_extra", 2)
                    }
                else:
                    eqp.escudo = None
                    
                armadura_item = getattr(heroi, "armadura", None) or getattr(heroi, "armadura_equipada", None)
                if armadura_item:
                    eqp.armadura = {
                        "nome": armadura_item.nome,
                        "bonus_def": getattr(armadura_item, "defesa", 3)
                    }
                else:
                    eqp.armadura = None
        except Exception as erro_sync:
            logging.error(f"Erro ao sincronizar combate de volta para ECS: {erro_sync}")

    def _criar_personagem_inimigo(self, dados: dict) -> Any:
        """
        Mapper: dados do JSON do evento → objeto Personagem do domínio.
        Segue o padrão Mapper da Regra 1 (Clean Architecture).

        Args:
            dados: Dict com os atributos do inimigo vindos do JSON do evento.
        """
        from app.core.entities.personagens import Personagem, Raca, ClasseRPG

        raca = Raca(
            nome=dados.get("raca", "Humano"),
            bonus_atributos={},
            emoji=dados.get("emoji", "👹"),
        )
        classe = ClasseRPG(
            nome=dados.get("classe", "Guerreiro"),
            bonus_caminhos={},
            habilidades=[],
        )
        inimigo = Personagem(
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
        inimigo.pv_atual = int(dados.get("pv_atual", inimigo.max_hp))
        inimigo.pm_atual = int(dados.get("pm_atual", inimigo.max_mp))
        return inimigo


class UsarItemBatalhaModal(ModalScreen[Optional[str]]):
    """
    Modal de seleção de item usável durante a batalha.
    """
    CSS_PATH = "styles/battle_styles.css"

    def __init__(self, itens_usaveis: list):
        super().__init__()
        self.itens_usaveis = itens_usaveis
        self.item_selecionado = None

    def compose(self):
        with Vertical(id="batalha-item-dialog"):
            yield Label("🧪 Selecione um Item para Usar na Batalha", classes="painel-titulo")
            yield ListView(id="list-itens-batalha")
            yield Static("Selecione um item da lista.", id="lbl-batalha-item-desc")
            with Horizontal(id="batalha-item-botoes"):
                yield Button("✨ Usar Item", id="btn-confirmar-item-batalha", variant="success", disabled=True)
                yield Button("Cancelar", id="btn-cancelar-item-batalha", variant="error")

    def on_mount(self) -> None:
        list_view = self.query_one("#list-itens-batalha", ListView)
        for item in self.itens_usaveis:
            widget = ListItem(
                Label(f"{item['emoji']} {item['nome']} (x{item['quantidade']}) — {item['descricao']}"),
                name=item['nome']
            )
            list_view.append(widget)
        if not self.itens_usaveis:
            self.query_one("#lbl-batalha-item-desc", Static).update("Nenhum item usável no inventário.")

    @on(ListView.Selected, "#list-itens-batalha")
    def on_item_selecionado(self, event: ListView.Selected):
        if event.item and hasattr(event.item, "name"):
            self.item_selecionado = event.item.name
            self.query_one("#lbl-batalha-item-desc", Static).update(f"Usar: [bold yellow]{self.item_selecionado}[/]")
            self.query_one("#btn-confirmar-item-batalha", Button).disabled = False

    @on(Button.Pressed)
    def on_button_click(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-confirmar-item-batalha":
            self.dismiss(self.item_selecionado)
        elif event.button.id == "btn-cancelar-item-batalha":
            self.dismiss(None)
