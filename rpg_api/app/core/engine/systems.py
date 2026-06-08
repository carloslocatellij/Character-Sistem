import esper
import random
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, AIComponent, InventoryComponent
)
from app.core.entities.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

class RenderSystem:
    """Sistema responsável por compilar as camadas de Terreno, Objetos e Esper ECS em um único frame Text."""

    def renderizar_frame(self, mapa_matriz: list[list[str]], dict_objetos: dict) -> Text:
        if not mapa_matriz:
            return Text("Mapa Vazio")

        texto_final = Text(no_wrap=True)
        altura, largura = len(mapa_matriz), len(mapa_matriz[0])

        # 🧠 Query eficiente no Esper: Coleta a posição de todas as entidades com aparência
        posicoes_entidades = {}
        for ent_id, (pos, render) in esper.get_components(PositionComponent, RenderComponent):
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
    

class MovementSystem:
    """Sistema lógico encarregado de validar a física e colisões de movimentos."""

    def __init__(self, map_loader):
        # Guardamos a referência do loader para inspecionar os terrenos e objetos estáveis
        self.map_loader = map_loader
        # Lista de emojis que representam barreiras intransponíveis no jogo
        self.tiles_bloqueantes = bloqueantes

    def mover_entidade(self, entidade_id: int, direcao: str) -> bool:
        """
        Calcula a nova posição de uma entidade e aplica se for válida.
        Retorna True se moveu, ou False se colidiu.
        """
        # 1. Recupera o componente de posição da entidade no Esper
        pos = esper.component_for_entity(entidade_id, PositionComponent)

        proximo_x, proximo_y = pos.x, pos.y

        if direcao == "cima":           proximo_y -= 1
        elif direcao == "baixo":        proximo_y += 1
        elif direcao == "esquerda":     proximo_x -= 1
        elif direcao == "direita":      proximo_x += 1

        # 2. Validação contra os limites lógicos do mapa
        if not (0 <= proximo_y < self.map_loader.altura and 0 <= proximo_x < self.map_loader.largura):
            return False

        # 3. Validação contra a Camada de Terrenos (Paredes lidas do BD)
        tile_alvo = self.map_loader.matriz_terrenos[proximo_y][proximo_x]
        if tile_alvo in self.tiles_bloqueantes:
            return False

        # 4. Validação contra a Camada de Objetos Estáticos
        if (proximo_y, proximo_x) in self.map_loader.camada_objetos:
            return False

        # 5. Validação contra Outras Entidades do Esper (Evita sobreposição com NPCs/Monstros)
        for outra_ent, outra_pos in esper.get_component(PositionComponent):
            if outra_ent != entidade_id:
                if outra_pos.x == proximo_x and outra_pos.y == proximo_y:
                    return False

        # Se passou em todas as regras, o movimento é consolidado na memória
        pos.x = proximo_x
        pos.y = proximo_y
        return True
    
    
class InteractionSystem:
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def interagir(self, entidade_id: int, direcao_olhar: str) -> bool:
        pos_origem = esper.component_for_entity(entidade_id, PositionComponent)
        alvo_x, alvo_y = pos_origem.x, pos_origem.y

        if direcao_olhar == "cima":
            alvo_y -= 1
        elif direcao_olhar == "baixo":
            alvo_y += 1
        elif direcao_olhar == "esquerda":
            alvo_x -= 1
        elif direcao_olhar == "direita":
            alvo_x += 1

        for entidade_alvo, (pos_alvo, interact) in esper.get_components(PositionComponent, InteractableComponent):
            if pos_alvo.x == alvo_x and pos_alvo.y == alvo_y:
                if interact.on_interact:
                    interact.on_interact(entidade_id, interact.parametros)
                    logging.info(
                        f"foi por on_interact: id {entidade_id} - par: {interact.parametros}")

                # SE TIVER EVENT BUS: Notifica a UI de forma desacoplada!
                if self.event_bus:
                    self.event_bus.publish("INTERACTION_SUCCESS", {
                        "entidade_id": entidade_alvo,
                        "tipo": interact.tipo_evento,
                        "parametros": interact.parametros
                    })
                    logging.info(
                        f"foi por event_bus: ent: {entidade_alvo} - par: {interact.parametros}")
                return True
        return False



class AISystem:
    def __init__(self, engine_manager, movement_system, event_bus):
        self.engine = engine_manager
        self.movement_system = movement_system
        self.event_bus = event_bus

    def update(self):
        """Processa movimento autônomo de monstros/NPCs a cada tick."""
        for ent_id, (pos_comp, ai_comp) in esper.get_components(PositionComponent, AIComponent):
            # Só processa monstros com movimento aleatório por enquanto
            if ai_comp.tipo_movimento != "aleatório":
                continue

            # Escolhe uma direção aleatória (4 direções + ficar parado)
            opcoes = ["cima", "baixo", "esquerda", "direita", None]
            direcao = random.choice(opcoes)

            if not direcao:
                continue  # 20% de chance de ficar parado

            # Tenta mover usando a mesma lógica de colisão do jogador
            moveu = self.movement_system.mover_entidade(ent_id, direcao)

            # Se colidiu com algo, verifica se foi o herói
            if not moveu:
                pos_heroi = esper.component_for_entity(1, PositionComponent)
                if pos_heroi:
                    # Calcula a posição alvo que tentou alcançar
                    deltas = {
                        "cima": (0, -1),
                        "baixo": (0, 1),
                        "esquerda": (-1, 0),
                        "direita": (1, 0)
                    }
                    dx, dy = deltas.get(direcao, (0, 0))
                    alvo_x = pos_comp.x + dx
                    alvo_y = pos_comp.y + dy

                    # Se a colisão foi com o herói, emite evento de ataque
                    if pos_heroi.x == alvo_x and pos_heroi.y == alvo_y:
                        if self.event_bus:
                            self.event_bus.publish("ataque_monstro", {
                                "parametros": ai_comp.action_on_touch
                            })
                            
                            
class InventarySystem():
    """ Gerencia estoques de baús e o inventário do personagem. 
    """
       


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

class EventSystem:
    """Sistema processador de eventos universais."""
    
    def __init__(self, inv_sys: InventarySystem, game_state, log_callback):
        self.inv_sys = inv_sys
        self.game_state = game_state
        self.log_callback = log_callback

    def processar_evento_interacao(self, payload: dict):
        try:
            params = payload.get("parametros", {})
            if "paginas" not in params:
                self._processar_evento_antigo(payload)
                return
            
            entidade_id = payload.get("entidade_id")
            pagina_ativa = self._filtrar_pagina_valida(params.get("paginas", []), entidade_id)
            if not pagina_ativa:
                return
                
            gatilho = pagina_ativa.get("gatilho", "acao_jogador")
            comandos = pagina_ativa.get("comandos", [])
            self._processar_comandos_sequenciais(comandos, entidade_id)
        except Exception as e:
            logging.info(f"Erro em processar_evento_interacao: {e}")

    def _filtrar_pagina_valida(self, paginas: list, entidade_id: int) -> dict:
        try:
            paginas_ordenadas = sorted(paginas, key=lambda p: p.get("id_pagina", 0), reverse=True)
            for pagina in paginas_ordenadas:
                condicoes = pagina.get("condicoes", {})
                if self._avaliar_condicoes(condicoes, entidade_id):
                    return pagina
            return None
        except Exception as e:
            logging.info(f"Erro em _filtrar_pagina_valida: {e}")
            return None

    def _avaliar_condicoes(self, condicoes: dict, entidade_id: int) -> bool:
        try:
            item_req = condicoes.get("item_requerido")
            if item_req:
                inv = esper.component_for_entity(1, InventoryComponent)
                if not inv or not self.inv_sys._inventory_has_item(inv, item_req):
                    return False
                    
            switches = condicoes.get("switches", [])
            for sw in switches:
                if self.game_state.get_switch(sw["nome"]) != sw.get("valor", True):
                    return False
                    
            variaveis = condicoes.get("variaveis", [])
            for var in variaveis:
                atual = self.game_state.get_variable(var["nome"], 0)
                op = var.get("operador", "igual")
                val = var.get("valor", 0)
                if op == "maior_ou_igual" and not (atual >= val): return False
                if op == "menor_ou_igual" and not (atual <= val): return False
                if op == "igual" and not (atual == val): return False
                if op == "diferente" and not (atual != val): return False

            self_sw = condicoes.get("self_switch")
            if self_sw:
                if not self.game_state.get_switch(f"evento_{entidade_id}_{self_sw}"):
                    return False
                    
            return True
        except Exception as e:
            logging.info(f"Erro em _avaliar_condicoes: {e}")
            return False

    def _processar_comandos_sequenciais(self, comandos: list, entidade_id: int):
        for comando in comandos:
            try:
                tipo = comando.get("tipo")
                dados = comando.get("dados", {})
                
                if tipo == "mensagem":
                    texto = dados.get("texto", "")
                    self.log_callback(f"[cyan]💬 {texto}[/]")
                    
                elif tipo == "mudar_inventario":
                    item = dados.get("item")
                    operacao = dados.get("operacao")
                    qtd = dados.get("quantidade", 1)
                    inv = esper.component_for_entity(1, InventoryComponent)
                    if inv:
                        if operacao == "add":
                            self.inv_sys._inventory_add_item(inv, item, qtd)
                            self.log_callback(f"[bold cyan]🎁 Obteve: [yellow]{item} x{qtd}[/yellow]![/]")
                        elif operacao == "sub":
                            self.inv_sys._inventory_remove_item(inv, item, qtd)
                            self.log_callback(f"[bold red]❌ Perdeu: [yellow]{item} x{qtd}[/yellow]![/]")
                            
                elif tipo == "mudar_status_heroi":
                    parametro = dados.get("parametro")
                    operacao = dados.get("operacao")
                    valor = dados.get("valor", 0)
                    stats = esper.component_for_entity(1, StatsComponent)
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
                        render = esper.component_for_entity(id_alvo, RenderComponent)
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
                    self.game_state.set_switch(f"evento_{entidade_id}_{letra}", valor)
                    
                elif tipo == "bifurcacao_condicional":
                    pergunta = dados.get("pergunta", "Escolha:")
                    opcoes = dados.get("opcoes", [])
                    ramos = dados.get("ramos", {})
                    
                    self.log_callback(f"[yellow]❓ {pergunta} (Opções: {', '.join(opcoes)})[/]")
                    if opcoes and opcoes[0] in ramos:
                        self.log_callback(f"[dim]>>> Simulando escolha: {opcoes[0]}[/]")
                        self._processar_comandos_sequenciais(ramos[opcoes[0]], entidade_id)
                
                elif tipo == "efeito_sonoro":
                    arquivo = dados.get("arquivo")
                    self.log_callback(f"[dim]🎵 Som tocando: {arquivo}[/]")
                    
                elif tipo == "mover_evento":
                    self.log_callback(f"[dim]🏃 Movimento de evento acionado.[/]")
            except Exception as e:
                logging.info(f"Erro em _processar_comandos_sequenciais no comando '{comando.get('tipo', 'desconhecido')}': {e}")

    def _processar_evento_antigo(self, payload: dict):
        try:
            tipo = payload.get("tipo", "evento")
            params = payload.get("parametros", {})

            if tipo == "bau":
                self.ao_recolher_bau(payload)
            elif tipo == "npc_dialogo":
                self.log_callback(f"[cyan]💬 NPC: {params.get('texto', 'Olá!')}[/]")
            else:
                self.log_callback(f"[white]✨ Evento ativado: {tipo}[/]")
        except Exception as e:
            logging.info(f"Erro em _processar_evento_antigo: {e}")

    def ao_recolher_bau(self, dados):
        try:
            params = dados.get("parametros", {})
            estado_nome = params.get("estado_atual")
            bloco = params.get("estados").get(
                estado_nome) if estado_nome and estado_nome in params.get("estados") else params
            
            item_nome = bloco.get("item") or bloco.get("item_id") or bloco.get("nome") or "item desconhecido"
            qtd = bloco.get("quantidade") or bloco.get("qtd") or 1
            msg = bloco.get("mensagem") or bloco.get("msg") or "Você abriu um baú!"
            
            inv = esper.component_for_entity(1, InventoryComponent)
            if inv:
                self.inv_sys._inventory_add_item(inv, item_nome, qtd)

            self.log_callback(
                f"[bold cyan]🎁 {msg} e coletou: [yellow]{item_nome} x{qtd}[/yellow]! "
                f"(Digite /equipar ou /usar no terminal para usufruir)[/]"
            )
        except Exception as e:
            logging.info(f"Erro em ao_recolher_bau: {e}")