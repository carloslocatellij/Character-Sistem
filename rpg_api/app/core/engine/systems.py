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
from typing import Optional, List, Dict, Any, Tuple
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
    Motor lógico puro de combate por turnos multi-personagens (estilo Final Fantasy).
    Opera exclusivamente sobre objetos Personagem do Domínio (RAM, sem dependência de UI).
    Suporta equipes de 1 a 4 aliados contra grupos de 1 a 4 inimigos.
    Cada combatente possui seu próprio turno baseado em iniciativa individual (Regra 5).
    Emite eventos via esper.dispatch_event para a BattleScreen consumir.
    Regra 5: Utiliza deepcopy obrigatório em todos os combatentes antes de iniciar.
    """

    def __init__(self):
        super().__init__()
        self.combate_ativo: bool = False
        self.aliados: List[Any] = []              # Lista de 1 a 4 aliados (domínio)
        self.inimigos: List[Any] = []             # Lista de 1 a 4 inimigos (domínio)
        self.rodada: int = 1
        self.turno: int = 0
        self.fila_turnos: List[Dict[str, Any]] = []  # Ordem de iniciativa da rodada
        self.indice_turno_atual: int = 0
        self.heroi_vai_primeiro: bool = True

    @property
    def heroi(self) -> Optional[Any]:
        """Alias de retrocompatibilidade: retorna o primeiro aliado (líder da equipe)."""
        return self.aliados[0] if self.aliados else None

    @heroi.setter
    def heroi(self, valor: Any) -> None:
        if valor is not None:
            if not self.aliados:
                self.aliados = [valor]
            else:
                self.aliados[0] = valor

    @property
    def inimigo(self) -> Optional[Any]:
        """Alias de retrocompatibilidade: retorna o primeiro inimigo da lista."""
        return self.inimigos[0] if self.inimigos else None

    @property
    def combatente_ativo(self) -> Optional[Any]:
        """Retorna o combatente cujo turno está ativo no momento."""
        if self.fila_turnos and 0 <= self.indice_turno_atual < len(self.fila_turnos):
            return self.fila_turnos[self.indice_turno_atual]["combatente"]
        return self.heroi

    def iniciar_combate(self, heroi_ou_aliados: Any, inimigos: Any) -> None:
        """
        Configura os combatentes com deepcopy e inicia a primeira rodada.
        Suporta:
        - heroi_ou_aliados: Objeto Personagem único, Lista de Personagem (1 a 4), ou instância de Party.
        - inimigos: Objeto Personagem único ou Lista de Personagem (1 a 4).
        """
        # 1. Normaliza lista de aliados
        if hasattr(heroi_ou_aliados, "membros"):
            # Objeto Party / Equipe
            aliados_lista = [m for m in heroi_ou_aliados.membros if getattr(m, "pv_atual", 1) > 0]
            if not aliados_lista and heroi_ou_aliados.membros:
                aliados_lista = list(heroi_ou_aliados.membros)
        elif isinstance(heroi_ou_aliados, list):
            aliados_lista = list(heroi_ou_aliados)
        else:
            aliados_lista = [heroi_ou_aliados]

        # 2. Normaliza lista de inimigos
        if isinstance(inimigos, list):
            inimigos_lista = list(inimigos)
        else:
            inimigos_lista = [inimigos]

        # Deepcopy obrigatório (Regra 5)
        self.aliados = [deepcopy(a) for a in aliados_lista[:4]]
        self.inimigos = [deepcopy(i) for i in inimigos_lista[:4]]
        self.combate_ativo = True
        self.rodada = 1
        self.turno = 0

        # Monta a fila de iniciativa da Rodada 1
        self._montar_fila_turnos()

        primeiro_tipo = self.fila_turnos[0]["tipo"] if self.fila_turnos else "aliado"
        self.heroi_vai_primeiro = (primeiro_tipo == "aliado")

        nomes_aliados = ", ".join(getattr(a, 'nome', '?') for a in self.aliados)
        nomes_inimigos = ", ".join(getattr(i, 'nome', '?') for i in self.inimigos)
        logging.info(f"Combate iniciado: [{nomes_aliados}] vs [{nomes_inimigos}] (Rodada 1)")

        iniciativa_jogador = self.fila_turnos[0]["iniciativa"] if self.fila_turnos else 0
        iniciativa_inimigo = next((e["iniciativa"] for e in self.fila_turnos if e["tipo"] == "inimigo"), 0)

        esper.dispatch_event("combate_iniciado", {
            "heroi": self.heroi,
            "aliados": self.aliados,
            "inimigos": self.inimigos,
            "inimigo": self.inimigo,
            "iniciativa_jogador": iniciativa_jogador,
            "iniciativa_inimigo": iniciativa_inimigo,
            "heroi_vai_primeiro": self.heroi_vai_primeiro,
            "fila_turnos": self._snapshot_fila_turnos(),
            "rodada": self.rodada,
        })

        # Dispara o processamento do primeiro turno da fila
        self._processar_proximo_turno()

    def _montar_fila_turnos(self) -> None:
        """
        Rola iniciativa individual (1d6 + Agilidade) para todos os combatentes vivos (Regra 5).
        Ordena a fila de ações da rodada em ordem decrescente.
        """
        self.fila_turnos = []
        for idx, a in enumerate(self.aliados):
            if a.pv_atual > 0:
                rolagem = random.randint(1, 6)
                agi = a.atributos_totais.get("agilidade", 0)
                self.fila_turnos.append({
                    "combatente": a,
                    "tipo": "aliado",
                    "iniciativa": rolagem + agi,
                    "agilidade": agi,
                    "indice_time": idx,
                    "nome": a.nome
                })

        for idx, i in enumerate(self.inimigos):
            if i.pv_atual > 0:
                rolagem = random.randint(1, 6)
                agi = i.atributos_totais.get("agilidade", 0)
                self.fila_turnos.append({
                    "combatente": i,
                    "tipo": "inimigo",
                    "iniciativa": rolagem + agi,
                    "agilidade": agi,
                    "indice_time": idx,
                    "nome": i.nome
                })

        # Ordena por Iniciativa -> Agilidade -> Desempate aleatório estável
        self.fila_turnos.sort(key=lambda x: (x["iniciativa"], x["agilidade"], random.random()), reverse=True)
        self.indice_turno_atual = 0

    def _snapshot_aliados(self) -> List[Dict[str, Any]]:
        """Retorna o estado serializado de todos os aliados para renderização na UI."""
        idx_ativo = -1
        if self.fila_turnos and 0 <= self.indice_turno_atual < len(self.fila_turnos):
            entry = self.fila_turnos[self.indice_turno_atual]
            if entry["tipo"] == "aliado":
                idx_ativo = entry["indice_time"]

        return [
            {
                "nome": a.nome,
                "hp": a.pv_atual,
                "hp_max": a.max_hp,
                "mp": a.pm_atual,
                "mp_max": a.max_mp,
                "vivo": a.pv_atual > 0,
                "index": idx,
                "ativo": (idx == idx_ativo),
                "classe": a.classe.nome if hasattr(a, "classe") else "Aventureiro",
                "emoji": str(getattr(a, "raca", "🧙")),
                "efeitos": [ef.nome for ef in getattr(a, "efeitos_ativos", [])]
            }
            for idx, a in enumerate(self.aliados)
        ]

    def _snapshot_inimigos(self) -> List[Dict[str, Any]]:
        """Retorna o estado serializado de todos os inimigos para renderização na UI."""
        idx_ativo = -1
        if self.fila_turnos and 0 <= self.indice_turno_atual < len(self.fila_turnos):
            entry = self.fila_turnos[self.indice_turno_atual]
            if entry["tipo"] == "inimigo":
                idx_ativo = entry["indice_time"]

        return [
            {
                "nome": i.nome,
                "hp": i.pv_atual,
                "hp_max": i.max_hp,
                "mp": i.pm_atual,
                "mp_max": i.max_mp,
                "vivo": i.pv_atual > 0,
                "index": idx,
                "ativo": (idx == idx_ativo),
                "emoji": getattr(i, "emoji", "👹"),
                "efeitos": [ef.nome for ef in getattr(i, "efeitos_ativos", [])]
            }
            for idx, i in enumerate(self.inimigos)
        ]

    def _snapshot_fila_turnos(self) -> List[Dict[str, Any]]:
        """Retorna a visão ordenada da linha do tempo/fila de turnos."""
        return [
            {
                "nome": e["combatente"].nome,
                "tipo": e["tipo"],
                "iniciativa": e["iniciativa"],
                "vivo": e["combatente"].pv_atual > 0,
                "ativo": (idx == self.indice_turno_atual)
            }
            for idx, e in enumerate(self.fila_turnos)
        ]

    def _processar_proximo_turno(self) -> None:
        """
        Avança o ponteiro da fila de turnos para o próximo combatente vivo.
        Se todos agiram na rodada, recalcula a fila e inicia nova rodada.
        """
        if not self.combate_ativo:
            return

        # Verifica vitória ou derrota
        if all(i.pv_atual <= 0 for i in self.inimigos):
            self._encerrar_combate(vencedor="jogador")
            return
        if all(a.pv_atual <= 0 for a in self.aliados):
            self._encerrar_combate(vencedor="inimigo")
            return

        # Se ultrapassou o fim da fila da rodada atual, inicia uma nova rodada
        if self.indice_turno_atual >= len(self.fila_turnos):
            self.rodada += 1
            self._montar_fila_turnos()
            if not self.fila_turnos:
                return

        # Pega o combatente da vez
        entry = self.fila_turnos[self.indice_turno_atual]
        combatente = entry["combatente"]

        # Se o combatente foi derrotado antes de agir, pula
        if combatente.pv_atual <= 0:
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        self.turno += 1

        esper.dispatch_event("turno_iniciado", {
            "turno": self.turno,
            "rodada": self.rodada,
            "combatente_ativo": combatente,
            "tipo": entry["tipo"],
            "indice_time": entry["indice_time"],
            "e_aliado": (entry["tipo"] == "aliado"),
            "aliados": self._snapshot_aliados(),
            "inimigos": self._snapshot_inimigos(),
            "fila_turnos": self._snapshot_fila_turnos(),
            "heroi_hp": self.heroi.pv_atual if self.heroi else 0,
            "heroi_mp": self.heroi.pm_atual if self.heroi else 0,
            "inimigo_hp": self.inimigo.pv_atual if self.inimigo else 0,
        })

        if entry["tipo"] == "aliado":
            # Aguarda input do jogador para este aliado ativo
            logging.info(f"Turno {self.turno} (Rodada {self.rodada}): Aguardando ação de {combatente.nome}")
            return
        else:
            # Turno de inimigo: executa IA assincronamente se houver loop ativo rodando (Textual GUI)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.call_soon(self._agendar_turno_inimigo)
            except RuntimeError:
                pass

    def executar_acao_jogador(
        self,
        acao: str,
        alvo_index: int = 0,
        nome_item: Optional[str] = None,
        nome_magia: Optional[str] = None,
        alvo_tipo: str = "inimigo"
    ) -> None:
        """
        Executa a ação escolhida pelo jogador para o aliado cujo turno está ativo.
        """
        if not self.combate_ativo:
            logging.info("Tentativa de executar ação sem combate ativo.")
            return

        # Obtém o aliado ativo atual
        if self.fila_turnos and 0 <= self.indice_turno_atual < len(self.fila_turnos):
            entry = self.fila_turnos[self.indice_turno_atual]
            if entry["tipo"] == "aliado":
                atacante = entry["combatente"]
            else:
                atacante = self.heroi
        else:
            atacante = self.heroi

        if not atacante or atacante.pv_atual <= 0:
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        inimigos_vivos = [i for i in self.inimigos if i.pv_atual > 0]
        aliados_vivos = [a for a in self.aliados if a.pv_atual > 0]

        if not inimigos_vivos:
            self._encerrar_combate(vencedor="jogador")
            return

        # Determina o alvo
        if alvo_tipo == "aliado":
            alvo = self.aliados[min(alvo_index, len(self.aliados) - 1)] if self.aliados else atacante
        else:
            alvo = inimigos_vivos[min(alvo_index, len(inimigos_vivos) - 1)]

        # 1. Processa efeitos ativos no início do turno do personagem
        efeitos_relatorio = atacante.finalizar_turno() if hasattr(atacante, "finalizar_turno") else []
        pula_turno = any(ef.get("pula_turno") for ef in efeitos_relatorio)

        if atacante.pv_atual <= 0:
            resultado = {
                "atacante": atacante.nome,
                "alvo": atacante.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": f"☠ {atacante.nome} sucumbiu a efeitos contínuos!",
                "efeitos_processados": efeitos_relatorio,
                "alvo_morreu": True
            }
            self._emitir_resultado_turno(atacante, alvo, "efeito", resultado)
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        if pula_turno:
            msg_pula = next((ef.get("mensagem") for ef in efeitos_relatorio if ef.get("pula_turno")), f"{atacante.nome} perdeu o turno!")
            resultado = {
                "atacante": atacante.nome,
                "alvo": atacante.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": msg_pula,
                "efeitos_processados": efeitos_relatorio
            }
            self._emitir_resultado_turno(atacante, alvo, "efeito", resultado)
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        # 2. Executa a ação
        if acao == "item":
            # Verifica o inventário individual do personagem ativo ou inventário do ECS
            item_disponivel = None
            if hasattr(atacante, "obter_itens_inventario"):
                itens_p = atacante.obter_itens_inventario()
                if nome_item:
                    item_disponivel = next((it for it in itens_p if it["nome"].lower() == nome_item.lower()), None)
                elif itens_p:
                    item_disponivel = itens_p[0]
                    nome_item = item_disponivel["nome"]

            # Fallback para ECS InventoryComponent se não estiver no inventário individual
            world = self.world if (hasattr(self, "world") and self.world is not None) else esper
            inv_ecs = world.component_for_entity(1, InventoryComponent) if world.entity_exists(1) and world.has_component(1, InventoryComponent) else None

            from app.core.engine.item_system import aplicar_usar_item, obter_itens_usaveis
            if not item_disponivel and not nome_item and inv_ecs:
                usaveis = obter_itens_usaveis(inv_ecs)
                if usaveis:
                    nome_item = usaveis[0]["nome"]

            if not nome_item:
                resultado = {
                    "atacante": atacante.nome,
                    "alvo": atacante.nome,
                    "acertou": False,
                    "acao": "item",
                    "erro_item": "Você não possui item usável no inventário!",
                    "dano_causado": 0
                }
                self._emitir_resultado_turno(atacante, atacante, acao, resultado, fase="jogador")
                return  # Não gasta turno se não tiver item

            alvo_item = alvo if alvo_tipo == "aliado" else atacante
            if item_disponivel:
                atacante.remover_item_inventario(nome_item, 1)
                # Aplica efeito do item
                if "mana" in nome_item.lower() or "mp" in nome_item.lower():
                    recup = min(alvo_item.max_mp - alvo_item.pm_atual, 15)
                    alvo_item.pm_atual += recup
                    msg_uso = f"Recuperou {recup} MP"
                else:
                    recup = min(alvo_item.max_hp - alvo_item.pv_atual, 20)
                    alvo_item.pv_atual += recup
                    msg_uso = f"Recuperou {recup} HP"
                sucesso = True
            elif inv_ecs:
                sucesso, msg_uso = aplicar_usar_item(alvo_item, inv_ecs, nome_item)
            else:
                sucesso = False
                msg_uso = f"Você não possui '{nome_item}' no inventário."

            if sucesso:
                resultado = {
                    "atacante": atacante.nome,
                    "alvo": alvo_item.nome,
                    "acertou": True,
                    "acao": "cura",
                    "dano_causado": 0,
                    "descricao": f"🧪 {atacante.nome} usou {nome_item} em {alvo_item.nome}! ({msg_uso})"
                }
            else:
                resultado = {
                    "atacante": atacante.nome,
                    "alvo": atacante.nome,
                    "acertou": False,
                    "acao": "item",
                    "erro_item": msg_uso,
                    "dano_causado": 0
                }
                self._emitir_resultado_turno(atacante, atacante, acao, resultado, fase="jogador")
                return

        elif acao == "defender":
            resultado = {
                "atacante": atacante.nome,
                "alvo": atacante.nome,
                "acertou": True,
                "acao": "defender",
                "descricao": f"🛡️ {atacante.nome} assumiu postura defensiva (+Defesa)!"
            }
        elif acao == "fugir":
            # Teste de fuga baseado em agilidade
            chance = 0.5 + (atacante.atributos_totais.get("agilidade", 1) * 0.05)
            if random.random() < chance:
                resultado = {
                    "atacante": atacante.nome,
                    "alvo": atacante.nome,
                    "acertou": True,
                    "acao": "fugir",
                    "descricao": f"🏃 {atacante.nome} conseguiu abrir caminho e a equipe fugiu com sucesso!"
                }
                self._emitir_resultado_turno(atacante, alvo, acao, resultado, fase="jogador")
                self._encerrar_combate(vencedor="fuga")
                return
            else:
                resultado = {
                    "atacante": atacante.nome,
                    "alvo": atacante.nome,
                    "acertou": False,
                    "acao": "fugir",
                    "descricao": f"❌ A tentativa de fuga de {atacante.nome} falhou!"
                }
        else:
            # Ataque ou Magia
            resultado = self._resolver_acao_personagem(acao, atacante=atacante, alvo=alvo, nome_magia=nome_magia)

        if efeitos_relatorio and isinstance(resultado, dict):
            resultado["efeitos_processados"] = efeitos_relatorio

        self._emitir_resultado_turno(atacante, alvo, acao, resultado, fase="jogador")

        # Verifica se combate terminou
        if all(i.pv_atual <= 0 for i in self.inimigos):
            self._encerrar_combate(vencedor="jogador")
            return

        # Avança para o próximo turno da fila
        self.indice_turno_atual += 1
        self._processar_proximo_turno()

    def _emitir_resultado_turno(self, atacante: Any, alvo: Any, acao: str, resultado: Dict[str, Any], fase: Optional[str] = None) -> None:
        """Dispara o evento turno_calculado com estado consolidado para a UI."""
        if fase is None:
            fase = "jogador" if any(a.nome == getattr(atacante, "nome", "") for a in self.aliados) else "inimigo"

        esper.dispatch_event("turno_calculado", {
            "turno": self.turno,
            "rodada": self.rodada,
            "fase": fase,
            "acao": acao,
            "atacante": atacante,
            "alvo": alvo,
            "resultado": resultado,
            "aliados": self._snapshot_aliados(),
            "inimigos": self._snapshot_inimigos(),
            "fila_turnos": self._snapshot_fila_turnos(),
            # Aliases de compatibilidade
            "heroi_hp": self.heroi.pv_atual if self.heroi else 0,
            "heroi_mp": self.heroi.pm_atual if self.heroi else 0,
            "inimigo_hp": alvo.pv_atual if alvo else (self.inimigo.pv_atual if self.inimigo else 0),
        })

    def _agendar_turno_inimigo(self) -> None:
        """Cria a corrotina do turno do inimigo no event loop ativo."""
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._turno_inimigo_assincrono())
        except Exception as erro_task:
            logging.info(f"Erro ao criar task do turno inimigo: {erro_task}")
            self._executar_turno_inimigo_sincrono()

    async def _turno_inimigo_assincrono(self) -> None:
        """Pausa dramática de 0.8s para leitura do turno anterior antes do inimigo agir."""
        await asyncio.sleep(0.8)
        self._executar_turno_inimigo_sincrono()

    def _executar_turno_inimigo_sincrono(self) -> None:
        """Processa a ação de IA para o inimigo ativo da fila de turnos."""
        if not self.combate_ativo:
            return

        # Identifica o inimigo ativo
        inimigo_ativo = None
        if self.fila_turnos and 0 <= self.indice_turno_atual < len(self.fila_turnos):
            entry = self.fila_turnos[self.indice_turno_atual]
            if entry["tipo"] == "inimigo" and entry["combatente"].pv_atual > 0:
                inimigo_ativo = entry["combatente"]

        # Se chamado diretamente em teste ou fora da fila, pega o primeiro inimigo vivo
        if not inimigo_ativo:
            inimigos_vivos = [i for i in self.inimigos if i.pv_atual > 0]
            if inimigos_vivos:
                inimigo_ativo = inimigos_vivos[0]
            elif self.inimigos:
                inimigo_ativo = self.inimigos[0]

        if not inimigo_ativo:
            return

        # 1. Processa efeitos ativos no início do turno do inimigo
        efeitos_relatorio = inimigo_ativo.finalizar_turno() if hasattr(inimigo_ativo, "finalizar_turno") else []
        pula_turno = any(ef.get("pula_turno") for ef in efeitos_relatorio)

        if inimigo_ativo.pv_atual <= 0:
            resultado = {
                "atacante": inimigo_ativo.nome,
                "alvo": inimigo_ativo.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": f"☠ {inimigo_ativo.nome} foi derrotado por efeitos contínuos!",
                "efeitos_processados": efeitos_relatorio,
                "alvo_morreu": True
            }
            self._emitir_resultado_turno(inimigo_ativo, inimigo_ativo, "efeito", resultado, fase="inimigo")
            if all(i.pv_atual <= 0 for i in self.inimigos):
                self._encerrar_combate(vencedor="jogador")
                return
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        if pula_turno:
            msg_pula = next((ef.get("mensagem") for ef in efeitos_relatorio if ef.get("pula_turno")), f"{inimigo_ativo.nome} perdeu o turno!")
            resultado = {
                "atacante": inimigo_ativo.nome,
                "alvo": inimigo_ativo.nome,
                "acertou": False,
                "acao": "efeito",
                "descricao": msg_pula,
                "efeitos_processados": efeitos_relatorio
            }
            self._emitir_resultado_turno(inimigo_ativo, inimigo_ativo, "efeito", resultado, fase="inimigo")
            self.indice_turno_atual += 1
            self._processar_proximo_turno()
            return

        # 2. Escolha de alvo aliado inteligente (IA)
        aliados_vivos = [a for a in self.aliados if a.pv_atual > 0]
        if not aliados_vivos:
            self._encerrar_combate(vencedor="inimigo")
            return

        # IA escolhe o aliado com menor HP com 50% de chance, ou aleatório
        if random.random() < 0.5:
            alvo_aliado = min(aliados_vivos, key=lambda a: a.pv_atual)
        else:
            alvo_aliado = random.choice(aliados_vivos)

        acao_ia = self._decidir_acao_ia_por(inimigo_ativo)
        resultado = self._resolver_acao_personagem(acao_ia, atacante=inimigo_ativo, alvo=alvo_aliado)

        if efeitos_relatorio and isinstance(resultado, dict):
            resultado["efeitos_processados"] = efeitos_relatorio

        logging.info(f"Turno {self.turno} - IA [{inimigo_ativo.nome}]: {acao_ia} em {alvo_aliado.nome} | Resultado: {resultado}")
        self._emitir_resultado_turno(inimigo_ativo, alvo_aliado, acao_ia, resultado, fase="inimigo")

        if all(a.pv_atual <= 0 for a in self.aliados):
            self._encerrar_combate(vencedor="inimigo")
            return

        self.indice_turno_atual += 1
        self._processar_proximo_turno()

    def _decidir_acao_ia(self) -> str:
        """Alias de retrocompatibilidade para o primeiro inimigo."""
        return self._decidir_acao_ia_por(self.inimigo) if self.inimigo else "ataque"

    def _decidir_acao_ia_por(self, inimigo_ativo: Any) -> str:
        """IA adaptativa para o inimigo ativo."""
        if not inimigo_ativo:
            return "ataque"

        hp_percentual = inimigo_ativo.pv_atual / max(1, inimigo_ativo.max_hp)

        # Se tem baixa vida e possui magia de cura ou recurso de regeneração
        if hp_percentual < 0.35 and random.random() < 0.4:
            inimigo_ativo.pv_atual = min(inimigo_ativo.max_hp, inimigo_ativo.pv_atual + random.randint(4, 10))
            return "cura"

        # Se tem mana e magias conhecidas
        if getattr(inimigo_ativo, "pm_atual", 0) >= 3 and getattr(inimigo_ativo, "magias_conhecidas", None) and random.random() < 0.4:
            return "magia"

        return "ataque"

    def _resolver_acao_personagem(self, acao: str, atacante: Any, alvo: Any, nome_magia: Optional[str] = None) -> Dict[str, Any]:
        """Roteia a ação para os métodos do Domínio Personagem com suporte a magias em área."""
        try:
            if acao == "ataque":
                return atacante.atacar(alvo)

            elif acao == "magia" and getattr(atacante, "magias_conhecidas", None):
                magia = None
                if nome_magia:
                    magia = next((m for m in atacante.magias_conhecidas if m.nome.lower() == nome_magia.lower()), None)
                if not magia and atacante.magias_conhecidas:
                    magia = atacante.magias_conhecidas[0]

                if not magia:
                    return atacante.atacar(alvo)

                # Magia em área (atinge múltiplos combatentes)
                if getattr(magia, "dano_area", False):
                    # Se for dano em área, atinge todos os inimigos vivos
                    alvos_area = [i for i in self.inimigos if i.pv_atual > 0] if any(a.nome == atacante.nome for a in self.aliados) else [a for a in self.aliados if a.pv_atual > 0]
                    dano_total = 0
                    mortos = 0
                    for a_area in alvos_area:
                        res = atacante.lancar_magia(magia, a_area)
                        dano_total += res.get("dano_causado", 0)
                        if res.get("alvo_morreu"):
                            mortos += 1

                    return {
                        "atacante": atacante.nome,
                        "alvo": "Todos os Inimigos",
                        "magia": magia.nome,
                        "sucesso": True,
                        "dano_causado": dano_total,
                        "dano_area": True,
                        "alvos_atingidos": len(alvos_area),
                        "descricao": f"✨ {atacante.nome} conjurou {magia.nome} em ÁREA! Causou {dano_total} de dano total ({len(alvos_area)} alvos)."
                    }

                # Magia de cura/suporte com alvo em si mesmo ou em aliado
                alvo_magia = alvo
                if magia.cura_base > 0 or (magia.efeito_aplicado and magia.efeito_aplicado.tipo in ["cura_continua", "buff_atributo", "protecao_elemental"]):
                    if any(a.nome == atacante.nome for a in self.aliados) and not any(a.nome == alvo.nome for a in self.aliados):
                        alvo_magia = atacante

                res = atacante.lancar_magia(magia, alvo_magia)
                if isinstance(res, dict):
                    res["acao"] = "magia"
                    res["magia"] = magia.nome
                    if "sucesso" in res and "acertou" not in res:
                        res["acertou"] = res["sucesso"]
                return res

            elif acao == "cura":
                return {
                    "atacante": atacante.nome,
                    "alvo": atacante.nome,
                    "acertou": True,
                    "acao": "cura",
                    "dano_causado": 0,
                    "descricao": f"💚 {atacante.nome} concentrou suas energias e recuperou um pouco de vida."
                }
            else:
                return atacante.atacar(alvo)

        except Exception as erro_acao:
            logging.info(f"Erro ao resolver ação '{acao}': {erro_acao}")
            return {
                "atacante": getattr(atacante, 'nome', '?'),
                "alvo": getattr(alvo, 'nome', '?'),
                "acertou": False,
                "dano_causado": 0,
                "erro": str(erro_acao)
            }

    def _encerrar_combate(self, vencedor: str) -> None:
        """Encerra o combate, remove marcadores ECS e emite o evento de término."""
        self.combate_ativo = False
        logging.info(f"Combate encerrado. Vencedor: {vencedor}")

        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        if world.entity_exists(1) and world.has_component(1, CombatStateComponent):
            world.remove_component(1, CombatStateComponent)

        esper.dispatch_event("combate_encerrado", {
            "vencedor": vencedor,
            "rodada": self.rodada,
            "turno": self.turno,
            "aliados": self._snapshot_aliados(),
            "inimigos": self._snapshot_inimigos(),
        })

    def process(self, *args, **kwargs) -> None:
        """Processamento sob demanda."""
        pass
