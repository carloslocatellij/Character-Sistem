import unicodedata
import esper
import random
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, MovimentComponent, InventoryComponent,
    CollisionComponent, NetworkPlayerComponent
)
from app.core.entities.emojis import CatalogoTiles
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
            return itens
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
        return self._get_inventory_mapping(inv).get(nome, 0) > 0

    def _inventory_remove_item(self, inv, nome, quantidade=1):
        if not inv:
            return False
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            atual = itens.get(nome, 0)
            if atual >= quantidade:
                itens[nome] = atual - quantidade
                if itens[nome] <= 0:
                    itens.pop(nome, None)
                return True
            return False
        if isinstance(itens, list):
            if any(isinstance(x, dict) for x in itens):
                for entry in itens:
                    if isinstance(entry, dict) and entry.get("nome") == nome:
                        qtd = entry.get("quantidade", 1)
                        if qtd > quantidade:
                            entry["quantidade"] = qtd - quantidade
                        else:
                            itens.remove(entry)
                        return True
                return False
            removed = 0
            while removed < quantidade and nome in itens:
                itens.remove(nome)
                removed += 1
            return removed == quantidade
        return False

    def _inventory_add_item(self, inv, nome, quantidade=1):
        if not inv:
            return False
        itens = getattr(inv, "itens", None)
        if isinstance(itens, dict):
            itens[nome] = itens.get(nome, 0) + quantidade
            return True
        if isinstance(itens, list):
            if any(isinstance(x, dict) for x in itens):
                for entry in itens:
                    if isinstance(entry, dict) and entry.get("nome") == nome:
                        entry["quantidade"] = entry.get("quantidade", 1) + quantidade
                        return True
                itens.append({"nome": nome, "quantidade": quantidade})
                return True
            itens.extend([nome] * quantidade)
            return True
        return False

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
        self.entidade_atual_id = None

    def process(self, *args, **kwargs):
        pass

    def processar_evento_interacao(self, payload: dict):
        """Callback disparado pelo esper event_handler assim que o jogador interage com um bloco."""
        logging.info(f" foi por processar_evento_interacao")
        try:
            if self.aguardando_escolha:
                return

            params = payload.get("parametros", {})
            self.parms = params
            self.entidade_atual_id = payload.get("entidade_id")
            self.aguardando_escolha = False

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
            self.pilha_de_comandos = [list(comandos)]
            self.aguardando_escolha = False
            self.ramos_disponiveis = {}
            self.executar_proximos_comandos()
        except Exception as e:
            logging.info(f"Erro em _processar_comandos_sequenciais no comando '{comandos}':= {e}")

    def executar_proximos_comandos(self):
        """Loop executor não-bloqueante que processa a pilha até o fim ou até uma interrupção."""
        while self.pilha_de_comandos:
            bloco_atual = self.pilha_de_comandos[-1]
            if not bloco_atual:
                self.pilha_de_comandos.pop()
                continue

            comando = bloco_atual.pop(0)
            self._processar_comando_individual(comando)

            # Se o comando executado ativou um estado de pausa por pergunta, cede o controle para a TUI
            if self.aguardando_escolha:
                return

    def _processar_comando_individual(self, comando):
        """Interpretador genérico e atômico de comandos estruturados do JSON."""
        world = self.world if (hasattr(self, "world") and self.world is not None) else esper
        tipo = comando.get("tipo")
        dados = comando.get("dados", {})
        entidade_id = self.entidade_atual_id
        emoji = self.parms.get('paginas')[0].get('configuracao_visual', {}).get('emoji', '💬') if self.parms.get('paginas') else '💬'

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

        elif tipo == "teleporte":
            try:
                esper.dispatch_event("mudar_mapa", dados)
            except Exception as e:
                logging.info(f"Erro ao dispatchar teleport: {e}")

        elif tipo == "efeito_sonoro":
            arquivo = dados.get("arquivo")
            self.log_callback(f"[dim]🎵 Som tocando: {arquivo}[/]")

        elif tipo == "mover":
            self.log_callback(f"[dim]🏃 Movimento de evento acionado.[/]")

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
