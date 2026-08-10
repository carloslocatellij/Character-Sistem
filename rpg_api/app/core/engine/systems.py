import unicodedata
import esper

if not getattr(esper, "_safe_patched", False):
    def _safe_dispatch_event(name: str, *args) -> None:
        handlers = list(esper.event_registry.get(name, []))
        for func in handlers:
            handler = func()
            if handler is not None:
                handler(*args)

    esper.dispatch_event = _safe_dispatch_event
    esper._safe_patched = True

import random
import asyncio
from copy import deepcopy
from typing import Optional
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, MovimentComponent, InventoryComponent,
    CollisionComponent, NetworkPlayerComponent,
    CombatStateComponent, BattleParticipantComponent, HeroComponent
)
from app.core.entities.emojis import CatalogoTiles
from app.views.simulador import SimuladorCombate
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
from typing import Literal

Direcoes: Literal["cima", "baixo", "esquerda", "direita", None]

class RenderSystem(esper.Processor):
    """Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em um único frame Text."""
    
    def __init__(self, game_state=None):
        super().__init__()
        self.game_state = game_state

    def renderizar_frame(self, mapa_matriz: list[list[str]], dict_objetos: dict) -> Text:
        if not mapa_matriz:
            return Text("Mapa Vazio")

        texto_final = Text(no_wrap=True)
        altura, largura = len(mapa_matriz), len(mapa_matriz[0])

        world = self.world if (hasattr(self, "world") and self.world is not None) else esper

        # 🧠 Query eficiente no Esper: Coleta a posição de todas as entidades com aparência
        posicoes_entidades = {}
        for ent_id, (pos, render) in world.get_components(PositionComponent, RenderComponent):
            posicoes_entidades[(pos.y, pos.x)] = render.emoji

        # Montagem do Buffer Visual aplicando o Z-Index de renderização
        for y in range(altura):
            for x in range(largura):
                tile_chao = mapa_matriz[y][x]
                tile_objeto = dict_objetos.get((y, x))
                tile_entidade = posicoes_entidades.get((y, x))

                # Descobre o background do terreno abaixo da célula para resolver a transparência
                cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                estilo_fundo = f"on {cor_bg}" if cor_bg else ""

                # Prioridade do Z-Index: 1° Entidades ECS, 2° Objetos de Cenário, 3° Terreno Base
                if tile_entidade is not None:
                    texto_final.append(tile_entidade, style=estilo_fundo)
                elif tile_objeto is not None:
                    texto_final.append(tile_objeto, style=estilo_fundo)
                else:
                    texto_final.append(tile_chao)
            texto_final.append("\n")

        return texto_final

    def process(self, *args, **kwargs):
        from app.core.engine.event_evaluator import obter_pagina_ativa
        for ent_id, interact_comp in esper.get_component(InteractableComponent):
            if interact_comp.parametros and "paginas" in interact_comp.parametros:
                pagina_ativa = obter_pagina_ativa(
                    interact_comp.parametros["paginas"], ent_id, self.game_state, esper)

            if pagina_ativa and pagina_ativa.get("configuracao_visual"):
                emoji_evt = pagina_ativa.get("configuracao_visual", {}).get("emoji", "❓")
                emoji_comp = RenderComponent(
                    emoji=emoji_evt
                )
                esper.add_component(ent_id, emoji_comp)


class MovementSystem(esper.Processor):
    """Sistema lógico encarregado de validar a física e colisões de movimentos."""

    def __init__(self, map_loader=None):
        super().__init__()
        # Guardamos a referência do loader para inspecionar os terrenos e objetos estáveis
        self.map_loader = map_loader
        # Lista de emojis que representam barreiras intransponíveis no jogo
        self.tiles_bloqueantes = bloqueantes

    def mover_entidade(self, entidade_id: int, direcao: str) -> bool:
        """
        Calcula a nova posição de uma entidade e aplica se for válida.
        Retorna True se moveu, ou False se colidiu.
        """
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper

        # 1. Recupera o componente de posição da entidade no Esper
        if not world.entity_exists(entidade_id) or not world.has_component(entidade_id, PositionComponent):
            return False

        pos = world.component_for_entity(entidade_id, PositionComponent)
        proximo_x, proximo_y = pos.x, pos.y

        if direcao == "cima":           proximo_y -= 1
        elif direcao == "baixo":        proximo_y += 1
        elif direcao == "esquerda":     proximo_x -= 1
        elif direcao == "direita":      proximo_x += 1

        # 2. Validação contra os limites lógicos do mapa
        if self.map_loader:
            if not (0 <= proximo_y < self.map_loader.altura and 0 <= proximo_x < self.map_loader.largura):
                return False

            # 3. Validação contra a Camada de Terrenos (Paredes lidas do BD)
            tile_alvo = self.map_loader.matriz_terrenos[proximo_y][proximo_x]
            if tile_alvo in self.tiles_bloqueantes:
                return False

            # 4. Validação contra a Camada de Objetos Estáticos
            if (proximo_y, proximo_x) in self.map_loader.camada_objetos:
                return False

        # 5. Validação contra Outras Entidades do Esper (Evita sobreposição com NPCs/Monstros/Jogadores de rede)
        for outra_ent, outra_pos in world.get_component(PositionComponent):
            if outra_ent != entidade_id:
                is_solid = True
                if world.has_component(outra_ent, CollisionComponent):
                    is_solid = world.component_for_entity(outra_ent, CollisionComponent).solido
                if is_solid and outra_pos.x == proximo_x and outra_pos.y == proximo_y:
                    return False

        # Se passou em todas as regras, o movimento é consolidado na memória
        pos.x = proximo_x
        pos.y = proximo_y
        pos.direcao_olhar = direcao
        return True

    def process(self, *args, **kwargs):
        pass


class AISystem(esper.Processor):
    def __init__(self, game_state=None):
        super().__init__()
        self.roteiro = 0
        self.game_state = game_state

    def process(self, tick, *args, **kwargs):
        """Processa movimento autônomo de monstros/NPCs a cada tick."""
        from app.core.engine.event_evaluator import obter_pagina_ativa
        #logging.info(f"Processando AISystem no tick {tick}")
        
        for ent_id, interact_comp  in esper.get_component(InteractableComponent):
            if interact_comp.parametros and "paginas" in interact_comp.parametros:
                pagina_ativa = obter_pagina_ativa(
                    interact_comp.parametros["paginas"], ent_id, self.game_state, esper)
        
            if pagina_ativa and pagina_ativa.get("movimento"):
                roteiro = pagina_ativa.get("movimento", {}).get("roteiro", [])
                roteiro_idx = pagina_ativa.get("movimento", {}).get("roteiro_idx", 0)
                movement_type = pagina_ativa.get("movimento", {}).get("tipo", "aleatorio")
                mov_comp = MovimentComponent(
                    movement_type=movement_type,
                    roteiro=roteiro,
                    ciclos=pagina_ativa.get("movimento", {}).get("ciclos", 1),
                    action_on_touch=pagina_ativa.get("movimento", {}).get("action_on_touch", None),
                    roteiro_idx=roteiro_idx
                    )
                esper.add_component(ent_id, mov_comp)
                
            
        self.processar_movimento_autonomo(tick)

    # Compatibilidade legado para sistemas que chamam update() em vez de process()
    def update(self, tick):
        """Compatibilidade legado."""
        self.processar_movimento_autonomo(tick)

    def processar_movimento_autonomo(self, tick_de_movimento):
        world = esper # or self.world if (hasattr(self, "world") and self.world is not None)
        movement_sys = world.get_processor(MovementSystem)
        if not movement_sys:
            return
        
        deltas = {
            "cima": (0, -1),
            "baixo": (0, 1),
            "esquerda": (-1, 0),
            "direita": (1, 0)
        }
        opcoes: list[str] = ["cima", "baixo", "esquerda", "direita", None]

        for ent_id, (pos_comp, mov_comp) in world.get_components(PositionComponent, MovimentComponent):
            if mov_comp.movement_type == 'parado':
                continue
            
            #logging.info(f"Processando mov:: ent_{ent_id} no tick {tick_de_movimento}: tipo={mov_comp.movement_type}, roteiro={mov_comp.roteiro}, idx={mov_comp.roteiro_idx}")
            if mov_comp.movement_type == "aleatorio":
                direcao = random.choice(opcoes)
                if not direcao:
                    continue

                moveu = movement_sys.mover_entidade(ent_id, direcao)

                if not moveu:
                    pos_heroi = world.component_for_entity(1, PositionComponent) if world.entity_exists(1) and world.has_component(1, PositionComponent) else None
                    if pos_heroi:
                        dx, dy = deltas.get(direcao, (0, 0))
                        alvo_x = pos_comp.x + dx
                        alvo_y = pos_comp.y + dy
                        if pos_heroi.x == alvo_x and pos_heroi.y == alvo_y:
                            esper.dispatch_event("ataque_monstro", {
                                "parametros": mov_comp.action_on_touch})

            # Perseguir heroi
            elif mov_comp.movement_type == "seguir_heroi":
                pos_heroi = world.component_for_entity(1, PositionComponent) if world.entity_exists(1) and world.has_component(1, PositionComponent) else None
                if pos_heroi:
                    dx = pos_heroi.x - pos_comp.x
                    dy = pos_heroi.y - pos_comp.y
                    direcao = None
                    if abs(dx) > abs(dy):
                        direcao = "direita" if dx > 0 else "esquerda"
                    elif dy != 0:
                        direcao = "baixo" if dy > 0 else "cima"

                    if direcao:
                        movement_sys.mover_entidade(ent_id, direcao)

            # Fugir do heroi
            elif mov_comp.movement_type == "fugir_heroi":
                pos_heroi = world.component_for_entity(1, PositionComponent) if world.entity_exists(1) and world.has_component(1, PositionComponent) else None
                if pos_heroi:
                    dx = pos_heroi.x - pos_comp.x
                    dy = pos_heroi.y - pos_comp.y
                    direcao = None
                    if abs(dx) > abs(dy):
                        direcao = "esquerda" if dx > 0 else "direita"
                    elif dy != 0:
                        direcao = "cima" if dy > 0 else "baixo"

                    if direcao:
                        movement_sys.mover_entidade(ent_id, direcao)

            elif mov_comp.movement_type == "roteiro":
                direcao = None
                if mov_comp.roteiro:
                    direcao = mov_comp.roteiro[mov_comp.roteiro_idx]
                    if isinstance(direcao, str):
                        direcao = direcao.strip().lower()

                if direcao in ('cima', 'baixo', 'direita', 'esquerda'):
                    logging.info(f"Roteiro do NPC {tick_de_movimento}: {direcao}")
                    moveu = movement_sys.mover_entidade(ent_id, direcao)
                    if not moveu:
                        logging.info(f"Erro ao mover: {tick_de_movimento}: {direcao}")

                if mov_comp.roteiro:
                    mov_comp.roteiro_idx = (mov_comp.roteiro_idx + 1) % len(mov_comp.roteiro)


class InventarySystem(esper.Processor):
    """Gerencia estoques de baús e o inventário do personagem."""

    def _get_inventory_mapping(self, inv):
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            return {k: v for k, v in itens.items() if v > 0}
        if isinstance(itens, list):
            mapped = {}
            for entry in itens:
                if isinstance(entry, dict):
                    nome = entry.get("nome") or entry.get("item") or entry.get("nome_item")
                    qtd = entry.get("quantidade", 1)
                else:
                    nome = str(entry)
                    qtd = 1
                if not nome:
                    continue
                mapped[nome] = mapped.get(nome, 0) + qtd
            return mapped
        return {}

    def _inventory_has_item(self, inv, nome):
        mapping = self._get_inventory_mapping(inv)
        for k, v in mapping.items():
            if k.lower() == nome.lower() and v > 0:
                return True
        return False

    def _inventory_remove_item(self, inv, nome, quantidade=1):
        from app.core.engine.item_system import inv_remover_item
        return inv_remover_item(inv, nome, quantidade)

    def _inventory_add_item(self, inv, nome, quantidade=1):
        from app.core.engine.item_system import inv_adicionar_item
        return inv_adicionar_item(inv, nome, quantidade)

    def process(self, *args, **kwargs):
        pass


class InteractionSystem(esper.Processor):
    def __init__(self, event_bus=None):
        super().__init__()
        self.event_bus = event_bus

    def interagir(self, entidade_id: int, direcao_olhar: str) -> bool:
        """
        Verifica se há um evento à frente do jogador.
        Se houver, publica as informações e parâmetros do evento para o esper,
        delegando a responsabilidade de execução para o EventSystem.
        """
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper

        if not world.entity_exists(entidade_id) or not world.has_component(entidade_id, PositionComponent):
            return False

        pos_origem = world.component_for_entity(entidade_id, PositionComponent)
        alvo_x, alvo_y = pos_origem.x, pos_origem.y

        if direcao_olhar == "cima":
            alvo_y -= 1
        elif direcao_olhar == "baixo":
            alvo_y += 1
        elif direcao_olhar == "esquerda":
            alvo_x -= 1
        elif direcao_olhar == "direita":
            alvo_x += 1

        for entidade_alvo, (pos_alvo, interact) in world.get_components(PositionComponent, InteractableComponent):
            if pos_alvo.x == alvo_x and pos_alvo.y == alvo_y:
                payload = {
                    "entidade_id": entidade_alvo,
                    "parametros": getattr(interact, "parametros", {})
                }
                # Executa o callback on_interact se existir
                if interact.on_interact is not None:
                    interact.on_interact(entidade_id, interact.parametros)
                esper.dispatch_event("INTERACTION_SUCCESS", payload)
                return True
        return False

    def process(self, *args, **kwargs):
        pass


class EventSystem(esper.Processor):
    """Sistema processador de eventos universais."""

    def __init__(self, inv_sys: InventarySystem, game_state, log_callback, event_bus=None):
        super().__init__()
        self.inv_sys = inv_sys
        self.game_state = game_state
        self.log_callback = log_callback
        self.event_bus = event_bus

        self.pilha_de_comandos = []      # Armazena os blocos de comandos lineares
        self.aguardando_escolha = False
        self.aguardando_combate = False
        self.ramos_combate_pendente = {}
        self.inimigo_nome_combate_pendente = "Goblin"
        self.entidade_atual_id = None

        # Registra o listener de conclusão de combate interativo via GUI
        try:
            esper.set_handler("combate_finalizado_gui", self._ao_receber_resultado_combate_gui)
        except Exception:
            pass

    def process(self, *args, **kwargs):
        pass

    def processar_evento_interacao(self, payload: dict):
        """Callback disparado pelo esper event_handler assim que o jogador interage com um bloco."""
        logging.info(f" foi por processar_evento_interacao")
        try:
            if self.aguardando_escolha or self.aguardando_combate:
                return

            params = payload.get("parametros", {})
            self.parms = params
            self.entidade_atual_id = payload.get("entidade_id")
            self.aguardando_escolha = False
            self.aguardando_combate = False

            if "paginas" not in params:
                self._processar_evento_antigo(payload)
                return

            entidade_id = payload.get("entidade_id")
            pagina_ativa = self._filtrar_pagina_valida(params.get("paginas", []), entidade_id)
            if not pagina_ativa:
                return

            comandos = pagina_ativa.get("comandos", [])
            self._processar_comandos_sequenciais(comandos, entidade_id)
        except Exception as e:
            logging.info(f"Erro em processar_evento_interacao: {e}")

    def _filtrar_pagina_valida(self, paginas: list, entidade_id: int) -> dict:
        logging.info(f"Filtrando paginas")
        from app.core.engine.event_evaluator import obter_pagina_ativa
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        return obter_pagina_ativa(paginas, entidade_id, self.game_state, world)

    def _avaliar_condicoes(self, condicoes: dict, entidade_id: int) -> bool:
        from app.core.engine.event_evaluator import avaliar_condicoes
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        return avaliar_condicoes(condicoes, entidade_id, self.game_state, world)

    def _processar_comandos_sequenciais(self, comandos: list, entidade_id: int):
        try:
            self.entidade_atual_id = entidade_id
            self.pilha_de_comandos = [list(comandos)]
            self.aguardando_escolha = False
            self.aguardando_combate = False
            self.ramos_disponiveis = {}
            self.executar_proximos_comandos()
        except Exception as e:
            logging.info(f"Erro em _processar_comandos_sequenciais no comando '{comandos}':= {e}")

    def executar_proximos_comandos(self):
        """Loop executor não-bloqueante que processa a pilha até o fim ou até uma interrupção."""
        while self.pilha_de_comandos:
            if self.aguardando_escolha or self.aguardando_combate:
                return

            bloco_atual = self.pilha_de_comandos[-1]
            if not bloco_atual:
                self.pilha_de_comandos.pop()
                continue

            comando = bloco_atual.pop(0)
            self._processar_comando_individual(comando)

            # Se o comando executado ativou um estado de pausa por pergunta ou combate, cede o controle para a TUI
            if self.aguardando_escolha or self.aguardando_combate:
                return

    def _ao_receber_resultado_combate_gui(self, resultado: str):
        if not self.aguardando_combate:
            return
        self.aguardando_combate = False
        ramos = self.ramos_combate_pendente
        inimigo_nome = self.inimigo_nome_combate_pendente
        self.ramos_combate_pendente = {}
        self._executar_ramo_resultado_combate(resultado, ramos, inimigo_nome)

    def _executar_ramo_resultado_combate(self, resultado: str, ramos: dict, inimigo_nome: str):
        if resultado == "venceu":
            self.log_callback(f"[bold green]🏆 Vitória contra {inimigo_nome}![/]")
        elif resultado == "perdeu":
            self.log_callback(f"[bold red]💀 Derrota para {inimigo_nome}...[/]")
        elif resultado == "fugiu":
            self.log_callback(f"[dim]🏃 Você fugiu da batalha contra {inimigo_nome}.[/]")
        elif resultado == "inimigo_fugiu":
            self.log_callback(f"[dim]💨 O inimigo {inimigo_nome} fugiu da batalha![/]")

        comandos_ramo = ramos.get(resultado, [])
        if comandos_ramo:
            self.pilha_de_comandos.append(list(comandos_ramo))
        self.executar_proximos_comandos()

    def _processar_comando_individual(self, comando):
        """Interpretador genérico e atômico de comandos estruturados do JSON."""
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        entidade_id = getattr(self, "entidade_atual_id", None)
        tipo = comando.get("tipo")
        dados = comando.get("dados", {})
        parms = getattr(self, "parms", {}) or {}
        paginas = parms.get("paginas", [])
        emoji = paginas[0].get("configuracao_visual", {}).get("emoji", "💬") if paginas and isinstance(paginas, list) and isinstance(paginas[0], dict) else "💬"


        logging.info(f"comando: {comando}")

        if tipo == "mensagem":
            texto = dados.get("texto", "")
            self.log_callback(f"[cyan]{emoji} {texto}[/]")

        elif tipo == "notificacao":
            texto = dados.get("texto", "")
            try:
                self.log_callback(f"{texto}", notif=True)
            except Exception as e:
                logging.info(f"Notificação: {comando} - {texto}")

        elif tipo == "mudar_inventario":
            item = dados.get("item")
            operacao = dados.get("operacao")
            qtd = dados.get("quantidade", 1)
            inv = world.component_for_entity(1, InventoryComponent) if world.entity_exists(1) and world.has_component(1, InventoryComponent) else None
            if inv:
                if operacao == "add":
                    self.inv_sys._inventory_add_item(inv, item, qtd)
                    self.log_callback(f"[bold cyan]🎁 Obteve: [yellow]{item} x{qtd}[/]![/]")
                elif operacao == "sub":
                    self.inv_sys._inventory_remove_item(inv, item, qtd)
                    self.log_callback(f"[bold red]❌ Perdeu: [yellow]{item} x{qtd}[/]![/]")

        elif tipo == "mudar_status_heroi":
            parametro = dados.get("parametro")
            operacao = dados.get("operacao")
            valor = dados.get("valor", 0)
            stats = world.component_for_entity(1, StatsComponent) if world.entity_exists(1) and world.has_component(1, StatsComponent) else None
            if stats and hasattr(stats, parametro):
                atual = getattr(stats, parametro, 0)
                if operacao == "add":
                    setattr(stats, parametro, atual + valor)
                elif operacao == "sub":
                    setattr(stats, parametro, max(0, atual - valor))
                self.log_callback(f"[white]⚡ {parametro.upper()} modificado ({operacao} {valor}).[/]")

        elif tipo == "mudar_render":
            novo_emoji = dados.get("novo_emoji")
            alvo = dados.get("alvo", "proprio")
            id_alvo = entidade_id if alvo == "proprio" else 1
            try:
                if world.entity_exists(id_alvo) and world.has_component(id_alvo, RenderComponent):
                    render = world.component_for_entity(id_alvo, RenderComponent)
                    if render and novo_emoji:
                        render.emoji = novo_emoji
            except KeyError:
                pass

        elif tipo == "controle_switch":
            nome = dados.get("nome")
            valor = dados.get("valor")
            self.game_state.set_switch(nome, valor)

        elif tipo == "controle_self_switch":
            letra = dados.get("letra")
            valor = dados.get("valor")
            from app.core.engine.event_evaluator import obter_id_referencia_evento
            id_ref = obter_id_referencia_evento(entidade_id, world)
            self.game_state.set_switch(f"evento_{id_ref}_{letra}", valor)

        elif tipo == "controle_variavel":
            nome = dados.get("nome")
            valor = dados.get("valor")
            operador = dados.get("operador", "=")
            self.game_state.modificar_variavel(nome, operador, valor)

        elif tipo == "bifurcacao_condicional":
            pergunta = dados.get("pergunta", "Escolha uma opção:")
            opcoes = dados.get("opcoes", [])
            ramos = dados.get("ramos", {})

            self.log_callback(f"[bold yellow]❓ {pergunta}[/]")
            self.ramos_disponiveis = {}

            for idx, opcao in enumerate(opcoes, start=1):
                id_op = opcao.replace(' ', '_').replace(',', '-').replace('.', '').replace('!','_')
                id_op = unicodedata.normalize("NFD", id_op)
                id_op = id_op.encode("ASCII", "ignore").decode("ASCII")

                self.ramos_disponiveis[str(idx)] = ramos.get(id_op, [])
                self.ramos_disponiveis[id_op.strip().lower()] = ramos.get(id_op, [])

            self.aguardando_escolha = True

            try:
                esper.dispatch_event("disparar_bifurcacao", {
                    "pergunta": pergunta,
                    "opcoes": opcoes
                })
            except Exception as e:
                self.log_callback(f"[red] ERRO_: {e}[/]")
            return

        elif tipo in ["aprender_magia", "ensinar_magia"]:
            nome_magia = dados.get("magia_nome") or dados.get("magia") or dados.get("nome")
            custo_pm = dados.get("custo_pm", 2)
            req_caminhos = dados.get("requisito_caminhos", {})
            req_exub = dados.get("requisito_exuberancia", 1)

            from app.db.database import SessionLocal
            from app.models.habilidades_magias_db import MagiaDB
            from app.controllers.game_controller import GameController
            from app.core.entities.habilidades_magias import Magia

            magia_obj = None
            if nome_magia:
                try:
                    with SessionLocal() as db:
                        m_db = db.query(MagiaDB).filter(MagiaDB.nome.ilike(nome_magia)).first()
                        if m_db:
                            magia_obj = GameController.converter_magia_db_para_dominio(m_db)
                except Exception as e:
                    logging.info(f"Erro ao buscar magia {nome_magia}: {e}")

            if not magia_obj and nome_magia:
                magia_obj = Magia(
                    nome=nome_magia,
                    custo_pm=custo_pm,
                    requisito_caminhos=req_caminhos,
                    requisito_exuberancia=req_exub
                )

            hero = None
            if world.entity_exists(1):
                if world.has_component(1, HeroComponent):
                    hero = world.component_for_entity(1, HeroComponent).personagem
                elif world.has_component(1, StatsComponent):
                    stats = world.component_for_entity(1, StatsComponent)
                    hero = getattr(stats, "personagem", None)

            if hero and magia_obj:
                try:
                    hero.aprender_magia(magia_obj)
                    self.log_callback(f"[bold green]✨ {hero.nome} aprendeu a magia '{magia_obj.nome}'![/]")
                except ValueError as err:
                    self.log_callback(f"[bold red]❌ Requisitos insuficientes para aprender '{magia_obj.nome}': {err}[/]")
            elif magia_obj:
                self.log_callback(f"[bold green]✨ Magia '{magia_obj.nome}' aprendida com sucesso![/]")


        elif tipo == "teleporte":
            try:
                esper.dispatch_event("mudar_mapa", dados)
            except Exception as e:
                logging.info(f"Erro ao dispatchar teleport: {e}")

        elif tipo == "iniciar_combate":
            # dados contém: nome, nivel, raca, classe, forca, agilidade, resistencia, percepcao, exuberancia, emoji, xp_recompensa, e ramos ({'venceu': [], ...})
            inimigo_nome = dados.get("nome") or dados.get("inimigo_nome", "Goblin")
            inimigo_nivel = dados.get("nivel") or dados.get("inimigo_nivel", 1)
            ramos = dados.get("ramos", {})

            self.ramos_combate_pendente = ramos
            self.inimigo_nome_combate_pendente = inimigo_nome

            # Verifica se há listeners registrados na GUI para o combate
            has_gui_handler = False
            try:
                if "solicitar_iniciar_combate" in esper.event_registry:
                    has_gui_handler = len(esper.event_registry["solicitar_iniciar_combate"]) > 0
            except Exception:
                has_gui_handler = False

            if has_gui_handler:
                self.aguardando_combate = True
                try:
                    esper.dispatch_event("solicitar_iniciar_combate", dados)
                    logging.info(f"Combate interativo solicitado na GUI com inimigo: {inimigo_nome}")
                except Exception as erro_combate:
                    logging.info(f"Erro ao solicitar combate: {erro_combate}")
                return

            # Modo Headless / Simulação (Fallback para testes automatizados sem GUI)
            self.log_callback(f"[bold red]⚔️ Combate iniciado contra {inimigo_nome} (Nv. {inimigo_nivel})![/]")

            aliado_char = None
            if world.entity_exists(1) and world.has_component(1, StatsComponent):
                stats_heroi = world.component_for_entity(1, StatsComponent)
                raca_h = Raca("Humano")
                classe_h = ClasseRPG(getattr(stats_heroi, "classe", "guerreiro"))
                aliado_char = Personagem(
                    nome=getattr(stats_heroi, "nome", "Herói"),
                    nivel=1,
                    raca=raca_h,
                    classe_rpg=classe_h,
                    forca_base=5,
                    agilidade_base=5,
                    res_base=5,
                    perc_base=3,
                    exub_base=3
                )
                aliado_char.max_hp = getattr(stats_heroi, "max_hp", 100)
                aliado_char.pv_atual = getattr(stats_heroi, "hp", 100)
                aliado_char.max_mp = getattr(stats_heroi, "max_mp", 50)
                aliado_char.pm_atual = getattr(stats_heroi, "mp", 50)
            else:
                raca_h = Raca("Humano")
                classe_h = ClasseRPG("guerreiro")
                aliado_char = Personagem("Herói", 1, raca_h, classe_h, 5, 5, 5, 3, 3)

            raca_val = dados.get("raca", "Goblin")
            raca_e = Raca(raca_val if isinstance(raca_val, str) else "Goblin")
            classe_val = dados.get("classe", "Guerreiro")
            classe_e = ClasseRPG(classe_val if isinstance(classe_val, str) else "guerreiro")
            inimigo_char = Personagem(
                nome=inimigo_nome,
                nivel=int(inimigo_nivel),
                raca=raca_e,
                classe_rpg=classe_e,
                forca_base=int(dados.get("forca", 3 + int(inimigo_nivel))),
                agilidade_base=int(dados.get("agilidade", 3)),
                res_base=int(dados.get("resistencia", 3)),
                perc_base=int(dados.get("percepcao", 2)),
                exub_base=int(dados.get("exuberancia", 1))
            )

            simulador = SimuladorCombate([aliado_char], [inimigo_char])
            relatorio = simulador.simular_batalha(silencioso=True)
            vencedor = relatorio.get("vencedor")

            resultado_combate = "venceu" if vencedor == "Aliados" else "perdeu"

            if world.entity_exists(1) and world.has_component(1, StatsComponent):
                stats_heroi = world.component_for_entity(1, StatsComponent)
                stats_heroi.hp = max(0, int(aliado_char.pv_atual))

            self._executar_ramo_resultado_combate(resultado_combate, ramos, inimigo_nome)

    def avancar_ramo_evento(self, opcao_escolhida: str):
        entrada_limpa = str(opcao_escolhida).strip().lower()
        entrada_limpa = entrada_limpa.replace(' ', '_').replace(',', '-').replace('.', '').replace('!','_')
        entrada_limpa = unicodedata.normalize("NFD", entrada_limpa)
        entrada_limpa = entrada_limpa.encode("ASCII", "ignore").decode("ASCII")

        if entrada_limpa in self.ramos_disponiveis:
            comandos_do_ramo = self.ramos_disponiveis[entrada_limpa]
            self.aguardando_escolha = False
            self.ramos_disponiveis = {}

            if comandos_do_ramo:
                self.pilha_de_comandos.append(list(comandos_do_ramo))

            self.executar_proximos_comandos()
        else:
            self.log_callback("[bold red]⚠️ Escolha inválida. Selecione uma opção válida.[/]")

    def _processar_evento_antigo(self, payload):
        # Placeholder legada para eventos antigos que não usam "paginas"
        pass


class NetworkSystem(esper.Processor):
    """
    Sistema responsável por sincronizar o estado de outros jogadores conectados
    através da rede (multiplayer).
    """
    def __init__(self):
        super().__init__()
        self.jogadores_conectados = {} # { connection_id: entity_id }

    def process(self, *args, **kwargs):
        # Lógica periódica de rede (ex: interpolação/limpeza de fantasmas se necessário)
        pass

    def adicionar_jogador(self, connection_id: str, username: str, x: int, y: int, emoji: str = "🧙"):
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper

        # Se já existe, apenas atualiza e retorna o ID da entidade existente
        if connection_id in self.jogadores_conectados:
            ent_id = self.jogadores_conectados[connection_id]
            if world.entity_exists(ent_id):
                pos = world.component_for_entity(ent_id, PositionComponent)
                pos.x = x
                pos.y = y
                return ent_id

        # Cria nova entidade para o jogador remoto
        ent_id = world.create_entity()
        world.add_component(ent_id, PositionComponent(x=x, y=y))
        world.add_component(ent_id, RenderComponent(emoji=emoji))
        world.add_component(ent_id, CollisionComponent(solido=True))
        world.add_component(ent_id, NetworkPlayerComponent(username=username, connection_id=connection_id))
        world.add_component(ent_id, StatsComponent(
            nome=username,
            classe="mago",
            hp=100,
            max_hp=100,
            mp=50,
            max_mp=50,
            ataque_base=10,
            defesa_base=5
        ))

        self.jogadores_conectados[connection_id] = ent_id
        logging.info(f"Jogador remoto conectado: {username} ({connection_id}) na posição ({x}, {y})")
        return ent_id

    def remover_jogador(self, connection_id: str):
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        if connection_id in self.jogadores_conectados:
            ent_id = self.jogadores_conectados[connection_id]
            if world.entity_exists(ent_id):
                world.delete_entity(ent_id)
            del self.jogadores_conectados[connection_id]
            logging.info(f"Jogador remoto desconectado: {connection_id}")

    def atualizar_jogador(self, connection_id: str, x: int, y: int, direcao: str = "baixo"):
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        if connection_id in self.jogadores_conectados:
            ent_id = self.jogadores_conectados[connection_id]
            if world.entity_exists(ent_id) and world.has_component(ent_id, PositionComponent):
                pos = world.component_for_entity(ent_id, PositionComponent)
                pos.x = x
                pos.y = y
                pos.direcao_olhar = direcao

esper.clear_dead_entities()


# ==============================================================================
# SISTEMA DE COMBATE POR TURNOS
# ==============================================================================

class BattleSystem(esper.Processor):
    """
    Motor lógico puro de combate por turnos.
    Opera exclusivamente sobre objetos Personagem em RAM (sem dependência de UI).
    Emite eventos via esper.dispatch_event para a BattleScreen consumir.
    Regra 5: Utiliza deepcopy obrigatório em todos os combatentes antes de iniciar.
    """

    def __init__(self):
        super().__init__()
        self.combate_ativo: bool = False
        self.heroi: Optional[object] = None        # Objeto Personagem (domínio)
        self.inimigos: list = []                   # Lista de 1-4 inimigos (domínio)
        self.turno: int = 0
        self.heroi_vai_primeiro: bool = True

    @property
    def inimigo(self) -> Optional[object]:
        """Alias de retrocompatibilidade: retorna o primeiro inimigo da lista."""
        return self.inimigos[0] if self.inimigos else None

    def iniciar_combate(self, heroi: object, inimigos) -> None:
        """
        Configura os combatentes com deepcopy e dispara o evento de início.
        O deepcopy garante que cada batalha inicie com o estado original dos personagens (Regra 5).

        Args:
            heroi: Objeto Personagem do domínio (jogador).
            inimigos: Lista de objetos Personagem (1 a 4 inimigos). Aceita também
                      um único objeto para retrocompatibilidade.
        """
        self.heroi = deepcopy(heroi)
        # Suporta um único inimigo (retrocompatibilidade) ou lista de 1-4
        if not isinstance(inimigos, list):
            inimigos = [inimigos]
        self.inimigos = [deepcopy(i) for i in inimigos]
        self.combate_ativo = True
        self.turno = 0

        # Rola iniciativa: 1d6 + Agilidade (Regra 5)
        # Para grupo de inimigos: usa a maior agilidade do grupo como referência
        iniciativa_jogador = random.randint(1, 6) + heroi.atributos_totais.get("agilidade", 0)
        max_agi_inimigos = max(
            (i.atributos_totais.get("agilidade", 0) for i in self.inimigos), default=0
        )
        iniciativa_inimigos = random.randint(1, 6) + max_agi_inimigos
        self.heroi_vai_primeiro = iniciativa_jogador >= iniciativa_inimigos

        nomes_inimigos = ", ".join(i.nome for i in self.inimigos)
        logging.info(
            f"Combate iniciado: {heroi.nome} vs [{nomes_inimigos}] | "
            f"Iniciativa jogador={iniciativa_jogador}, inimigos={iniciativa_inimigos}"
        )

        esper.dispatch_event("combate_iniciado", {
            "heroi": self.heroi,
            "inimigos": self.inimigos,
            # Mantém alias singular para compatibilidade com handlers antigos
            "inimigo": self.inimigos[0] if self.inimigos else None,
            "iniciativa_jogador": iniciativa_jogador,
            "iniciativa_inimigo": iniciativa_inimigos,
            "heroi_vai_primeiro": self.heroi_vai_primeiro,
        })

    def _snapshot_inimigos(self) -> list:
        """Retorna a lista de dicts com o estado atual de cada inimigo (para eventos)."""
        return [
            {
                "nome": i.nome,
                "hp": i.pv_atual,
                "hp_max": i.max_hp,
                "vivo": i.pv_atual > 0,
                "index": idx,
            }
            for idx, i in enumerate(self.inimigos)
        ]

    def executar_acao_jogador(self, acao: str, alvo_index: int = 0, nome_item: Optional[str] = None, nome_magia: Optional[str] = None) -> None:
        """
        Processa a ação escolhida pelo jogador e depois agenda o turno da IA de forma assíncrona.
        Este método é invocado diretamente pela BattleScreen após a confirmação no RadioSet.

        Args:
            acao: Ação escolhida ("ataque", "magia", "item", "fugir").
            alvo_index: Índice do inimigo alvo na lista self.inimigos (padrão: 0).
            nome_item: Nome opcional do item a ser usado.
        """
        if not self.combate_ativo:
            logging.info("Tentativa de executar acao sem combate ativo.")
            return

        # Filtra inimigos vivos e escolhe o alvo válido
        inimigos_vivos = [i for i in self.inimigos if i.pv_atual > 0]
        if not inimigos_vivos:
            self._encerrar_combate(vencedor="jogador")
            return

        alvo = inimigos_vivos[min(alvo_index, len(inimigos_vivos) - 1)]

        # Processa efeitos temporários ativos no herói
        efeitos_relatorio = self.heroi.finalizar_turno() if hasattr(self.heroi, "finalizar_turno") else []
        pula_turno_heroi = any(ef.get("pula_turno") for ef in efeitos_relatorio)

        if self.heroi.pv_atual <= 0:
            resultado = {
                "atacante": self.heroi.nome,
                "alvo": self.heroi.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": f"{self.heroi.nome} sofreu dano fatal de efeito!",
                "efeitos_processados": efeitos_relatorio,
                "alvo_morreu": True
            }
            esper.dispatch_event("turno_calculado", {
                "turno": self.turno,
                "fase": "jogador",
                "acao": "efeito",
                "resultado": resultado,
                "heroi_hp": self.heroi.pv_atual,
                "heroi_mp": self.heroi.pm_atual,
                "inimigos": self._snapshot_inimigos(),
                "inimigo_hp": alvo.pv_atual,
            })
            self._encerrar_combate(vencedor="inimigo")
            return

        if pula_turno_heroi:
            msg_pula = next((ef.get("mensagem") for ef in efeitos_relatorio if ef.get("pula_turno")), f"{self.heroi.nome} perdeu o turno!")
            resultado = {
                "atacante": self.heroi.nome,
                "alvo": self.heroi.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": msg_pula,
                "efeitos_processados": efeitos_relatorio
            }
            esper.dispatch_event("turno_calculado", {
                "turno": self.turno,
                "fase": "jogador",
                "acao": "efeito",
                "resultado": resultado,
                "heroi_hp": self.heroi.pv_atual,
                "heroi_mp": self.heroi.pm_atual,
                "inimigos": self._snapshot_inimigos(),
                "inimigo_hp": alvo.pv_atual,
            })
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon(self._agendar_turno_inimigo)
            except RuntimeError:
                self._executar_turno_inimigo_sincrono()
            return

        # Caso especial: Ação de usar Item
        if acao == "item":
            world = self.world if (hasattr(self, "world") and self.world is not None) else esper
            inv = world.component_for_entity(1, InventoryComponent) if world.entity_exists(1) and world.has_component(1, InventoryComponent) else None

            from app.core.engine.item_system import aplicar_usar_item, obter_itens_usaveis

            # Se o nome do item não foi especificado, busca o primeiro usável do inventário
            if not nome_item and inv:
                usaveis = obter_itens_usaveis(inv)
                if usaveis:
                    nome_item = usaveis[0]["nome"]

            if not nome_item or not inv:
                resultado = {
                    "atacante": self.heroi.nome,
                    "alvo": self.heroi.nome,
                    "acertou": False,
                    "acao": "item",
                    "erro_item": "Você não possui item usável no inventário!",
                    "dano_causado": 0
                }
                # Emite o evento informando o erro, para que a View libere o controle
                esper.dispatch_event("turno_calculado", {
                    "turno": self.turno,
                    "fase": "jogador",
                    "acao": acao,
                    "resultado": resultado,
                    "heroi_hp": self.heroi.pv_atual,
                    "heroi_mp": self.heroi.pm_atual,
                    "inimigos": self._snapshot_inimigos(),
                    "inimigo_hp": alvo.pv_atual,
                })
                return  # Interrompe o fluxo e não passa o turno
            else:
                sucesso, msg_uso = aplicar_usar_item(self.heroi, inv, nome_item)
                if sucesso:
                    resultado = {
                        "atacante": self.heroi.nome,
                        "alvo": self.heroi.nome,
                        "acertou": True,
                        "acao": "cura",
                        "dano_causado": 0,
                        "descricao": f"{self.heroi.nome} usou {nome_item}! ({msg_uso})"
                    }
                else:
                    resultado = {
                        "atacante": self.heroi.nome,
                        "alvo": self.heroi.nome,
                        "acertou": False,
                        "acao": "item",
                        "erro_item": msg_uso,
                        "dano_causado": 0
                    }
                    esper.dispatch_event("turno_calculado", {
                        "turno": self.turno,
                        "fase": "jogador",
                        "acao": acao,
                        "resultado": resultado,
                        "heroi_hp": self.heroi.pv_atual,
                        "heroi_mp": self.heroi.pm_atual,
                        "inimigos": self._snapshot_inimigos(),
                        "inimigo_hp": alvo.pv_atual,
                    })
                    return
        else:
            resultado = self._resolver_acao_personagem(acao, atacante=self.heroi, alvo=alvo, nome_magia=nome_magia)

        if efeitos_relatorio and isinstance(resultado, dict):
            resultado["efeitos_processados"] = efeitos_relatorio

        logging.info(f"Turno {self.turno} - Jogador: {acao} alvo={alvo.nome} | Resultado: {resultado}")

        esper.dispatch_event("turno_calculado", {
            "turno": self.turno,
            "fase": "jogador",
            "acao": acao,
            "resultado": resultado,
            "heroi_hp": self.heroi.pv_atual,
            "heroi_mp": self.heroi.pm_atual,
            # Lista completa de estados dos inimigos para a UI atualizar as barras
            "inimigos": self._snapshot_inimigos(),
            # Alias singular de retrocompatibilidade
            "inimigo_hp": alvo.pv_atual,
        })

        # Verifica se todos os inimigos foram derrotados
        if all(i.pv_atual <= 0 for i in self.inimigos):
            self._encerrar_combate(vencedor="jogador")
            return

        # Agenda o turno da IA de forma assíncrona no loop do asyncio do Textual
        # Isso garante que a UI não congele (Regra 3: nunca bloqueie a thread principal)
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon(self._agendar_turno_inimigo)
        except RuntimeError:
            # Fallback se não houver loop asyncio ativo (ex: testes unitários)
            self._executar_turno_inimigo_sincrono()

    def _agendar_turno_inimigo(self) -> None:
        """Cria a corrotina do turno do inimigo no event loop ativo."""
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._turno_inimigo_assincrono())
        except Exception as erro_task:
            logging.info(f"Erro ao criar task do turno inimigo: {erro_task}")
            self._executar_turno_inimigo_sincrono()

    async def _turno_inimigo_assincrono(self) -> None:
        """
        Calcula o turno da IA do inimigo sem bloquear o event loop do Textual.
        O delay de 0.9s cria a pausa dramática para o jogador ler o log (Regra 3).
        """
        await asyncio.sleep(0.9)
        self._executar_turno_inimigo_sincrono()

    def _executar_turno_inimigo_sincrono(self) -> None:
        """Núcleo de execução do turno de todos os inimigos vivos (IA simples)."""
        if not self.combate_ativo:
            return

        # Cada inimigo vivo ataca o herói em sequência
        for inimigo_ativo in self.inimigos:
            if inimigo_ativo.pv_atual <= 0:
                continue  # Inimigo derrotado não age
            if not self.combate_ativo:
                break

            efeitos_relatorio = inimigo_ativo.finalizar_turno() if hasattr(inimigo_ativo, "finalizar_turno") else []
            pula_turno_inimigo = any(ef.get("pula_turno") for ef in efeitos_relatorio)

            if inimigo_ativo.pv_atual <= 0:
                logging.info(f"☠ {inimigo_ativo.nome} foi derrotado por efeito contínuo!")
                resultado = {
                    "atacante": inimigo_ativo.nome,
                    "alvo": inimigo_ativo.nome,
                    "acertou": False,
                    "acao": "efeito",
                    "descricao": f"{inimigo_ativo.nome} foi derrotado por efeito contínuo!",
                    "efeitos_processados": efeitos_relatorio,
                    "alvo_morreu": True
                }
                esper.dispatch_event("turno_calculado", {
                    "turno": self.turno,
                    "fase": "inimigo",
                    "acao": "efeito",
                    "resultado": resultado,
                    "heroi_hp": self.heroi.pv_atual,
                    "heroi_mp": self.heroi.pm_atual,
                    "inimigos": self._snapshot_inimigos(),
                    "inimigo_hp": inimigo_ativo.pv_atual,
                })
                if all(i.pv_atual <= 0 for i in self.inimigos):
                    self._encerrar_combate(vencedor="jogador")
                    return
                continue

            if pula_turno_inimigo:
                self.turno += 1
                msg_pula = next((ef.get("mensagem") for ef in efeitos_relatorio if ef.get("pula_turno")), f"{inimigo_ativo.nome} perdeu o turno!")
                esper.dispatch_event("turno_calculado", {
                    "turno": self.turno,
                    "fase": "inimigo",
                    "acao": "efeito",
                    "resultado": {
                        "atacante": inimigo_ativo.nome,
                        "alvo": inimigo_ativo.nome,
                        "acertou": False,
                        "acao": "efeito",
                        "descricao": msg_pula,
                        "efeitos_processados": efeitos_relatorio
                    },
                    "heroi_hp": self.heroi.pv_atual,
                    "heroi_mp": self.heroi.pm_atual,
                    "inimigos": self._snapshot_inimigos(),
                    "inimigo_hp": inimigo_ativo.pv_atual,
                })
                continue

            acao_ia = self._decidir_acao_ia_por(inimigo_ativo)
            resultado = self._resolver_acao_personagem(acao_ia, atacante=inimigo_ativo, alvo=self.heroi)
            if efeitos_relatorio and isinstance(resultado, dict):
                resultado["efeitos_processados"] = efeitos_relatorio
            self.turno += 1
            logging.info(
                f"Turno {self.turno} - IA [{inimigo_ativo.nome}]: {acao_ia} | Resultado: {resultado}"
            )

            esper.dispatch_event("turno_calculado", {
                "turno": self.turno,
                "fase": "inimigo",
                "acao": acao_ia,
                "resultado": resultado,
                "heroi_hp": self.heroi.pv_atual,
                "heroi_mp": self.heroi.pm_atual,
                # Lista completa de estados para a UI
                "inimigos": self._snapshot_inimigos(),
                "inimigo_hp": inimigo_ativo.pv_atual,
            })

            if self.heroi.pv_atual <= 0:
                self._encerrar_combate(vencedor="inimigo")
                return

    def _decidir_acao_ia(self) -> str:
        """
        IA simples para o primeiro inimigo da lista (alias de retrocompatibilidade).
        Use _decidir_acao_ia_por(inimigo) para IA por inimigo específico.
        """
        return self._decidir_acao_ia_por(self.inimigo) if self.inimigo else "ataque"

    def _decidir_acao_ia_por(self, inimigo_ativo: object) -> str:
        """
        IA simples mas funcional para um inimigo específico:
        - Se tem mana e magias, usa magia com 30% de chance
        - Se HP baixo (<30%), tenta se curar com 40% de chance
        - Caso contrário, ataca fisicamente
        """
        if not inimigo_ativo:
            return "ataque"

        hp_percentual = inimigo_ativo.pv_atual / max(1, inimigo_ativo.max_hp)

        # Comportamento defensivo com HP baixo
        if hp_percentual < 0.3 and random.random() < 0.4:
            # Tenta se curar parcialmente (efeito narrativo)
            inimigo_ativo.pv_atual = min(
                inimigo_ativo.max_hp,
                inimigo_ativo.pv_atual + random.randint(2, 6)
            )
            return "cura"

        # Usa magia se tiver mana e magias conhecidas
        if inimigo_ativo.pm_atual >= 5 and inimigo_ativo.magias_conhecidas and random.random() < 0.3:
            return "magia"

        return "ataque"

    def _resolver_acao_personagem(self, acao: str, atacante: object, alvo: object, nome_magia: Optional[str] = None) -> dict:
        """Roteia a ação para o método correto da entidade Personagem do domínio."""
        try:
            if acao == "ataque":
                return atacante.atacar(alvo)
            elif acao == "magia" and atacante.magias_conhecidas:
                magia = None
                if nome_magia:
                    magia = next((m for m in atacante.magias_conhecidas if m.nome == nome_magia), None)
                if not magia:
                    magia = atacante.magias_conhecidas[0]

                # Se a magia for de cura ou efeito benéfico (buff, cura contínua, proteção), o alvo é o próprio atacante
                alvo_magia = alvo
                if magia.cura_base > 0 or (magia.efeito_aplicado and magia.efeito_aplicado.tipo in ["cura_continua", "buff_atributo", "protecao_elemental"]):
                    alvo_magia = atacante

                res = atacante.lancar_magia(magia, alvo_magia)
                if isinstance(res, dict):
                    res["acao"] = "magia"
                    res["magia"] = magia.nome
                    if "sucesso" in res and "acertou" not in res:
                        res["acertou"] = res["sucesso"]
                return res
            elif acao == "cura":
                # IA usando cura não causa dano — retorna resultado descritivo
                return {
                    "atacante": atacante.nome, "alvo": atacante.nome,
                    "acertou": True, "acao": "cura",
                    "dano_causado": 0,
                    "descricao": f"{atacante.nome} se recuperou um pouco."
                }
            else:
                # Ataque desarmado como fallback
                return atacante.atacar(alvo)
        except Exception as erro_acao:
            logging.info(f"Erro ao resolver ação '{acao}': {erro_acao}")
            return {
                "atacante": getattr(atacante, 'nome', '?'),
                "alvo": getattr(alvo, 'nome', '?'),
                "acertou": False, "dano_causado": 0,
                "erro": str(erro_acao)
            }

    def _encerrar_combate(self, vencedor: str) -> None:
        """Encerra o combate e remove o CombatStateComponent da entidade do jogador."""
        self.combate_ativo = False
        logging.info(f"Combate encerrado. Vencedor: {vencedor}")

        # Remove o marcador de combate do jogador no ECS
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        if world.entity_exists(1) and world.has_component(1, CombatStateComponent):
            world.remove_component(1, CombatStateComponent)

        esper.dispatch_event("combate_encerrado", {"vencedor": vencedor})

    def process(self, *args, **kwargs) -> None:
        """O BattleSystem não precisa de processamento periódico — opera sob demanda."""
        pass
