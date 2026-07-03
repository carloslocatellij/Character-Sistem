import unicodedata
import esper
import random
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, MovimentComponent, InventoryComponent
)
from app.core.entities.emojis import CatalogoTiles
bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
from typing import Literal

Direcoes: Literal["cima", "baixo", "esquerda", "direita", None]

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
    
    



class AISystem:
    def __init__(self, movement_system):
        self.movement_system = movement_system
        
    def processar_movimento_autonomo(self):
        """Processa movimento autônomo de monstros/NPCs a cada tick."""
        
        deltas = {
            "cima": (0, -1),
            "baixo": (0, 1),
            "esquerda": (-1, 0),
            "direita": (1, 0)
        }
        opcoes: list[str] = ["cima", "baixo", "esquerda", "direita", None]
        
        for ent_id, (pos_comp, ai_comp) in esper.get_components(PositionComponent, MovimentComponent):
            
            # Processa monstros com movimento aleatorio
            if ai_comp.movement_type == "aleatorio":
                # Escolhe uma direção aleatória (4 direções + ficar parado)
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
                        dx, dy = deltas.get(direcao, (0, 0))
                        alvo_x = pos_comp.x + dx
                        alvo_y = pos_comp.y + dy
                        if pos_heroi.x == alvo_x and pos_heroi.y == alvo_y:
                            esper.dispatch_event("ataque_monstro", {
                                "parametros": ai_comp.action_on_touch})

            # Perseguir heroi
            if ai_comp.movement_type == "seguir_heroi":
                pos_heroi = esper.component_for_entity(1, PositionComponent)
                if pos_heroi:
                    dx = pos_heroi.x - pos_comp.x
                    dy = pos_heroi.y - pos_comp.y
                    direcao = None
                    if abs(dx) > abs(dy):
                        direcao = "direita" if dx > 0 else "esquerda"
                    elif dy != 0:
                        direcao = "baixo" if dy > 0 else "cima"

                    if direcao:
                        self.movement_system.mover_entidade(ent_id, direcao)

            if ai_comp.movement_type == "fugir_heroi":
                pos_heroi = esper.component_for_entity(1, PositionComponent)
                if pos_heroi:
                    dx = pos_heroi.x - pos_comp.x
                    dy = pos_heroi.y - pos_comp.y
                    direcao = None
                    if abs(dx) > abs(dy):
                        direcao = "esquerda" if dx > 0 else "direita"
                    elif dy != 0:
                        direcao = "cima" if dy > 0 else "baixo"

                    if direcao:
                        self.movement_system.mover_entidade(ent_id, direcao)

            if ai_comp.movement_type == "patrulha":
                direcoes = ["cima", "esquerda", "baixo", "direita"]
                if not ai_comp.pontos:
                    continue
                pontos_convertidos = []
                for ponto in ai_comp.pontos:
                    ponto = ponto.replace('(','').replace(')','')
                    px, py = ponto.split(',')
                    pontos_convertidos.append((int(px),int(py)))

                current_patrol_index = 0
                # Move para o próximo ponto do caminho de patrulha
                proximo_ponto = pontos_convertidos[current_patrol_index]
                dx = proximo_ponto[0] - pos_comp.x
                dy = proximo_ponto[1] - pos_comp.y
                direcao = None
                if abs(dx) > abs(dy):
                    direcao = "direita" if dx > 0 else "esquerda"
                elif dy != 0:
                    direcao = "baixo" if dy > 0 else "cima"

                if direcao:
                    moveu = self.movement_system.mover_entidade(ent_id, direcao)
                    if moveu: 
                        if pos_comp.x == proximo_ponto[0] and pos_comp.y == proximo_ponto[1]:
                            # Avança para o próximo ponto do caminho de patrulha
                            current_patrol_index = (
                                current_patrol_index + 1) % len(pontos_convertidos)
                    else:
                        outra_op = direcoes[direcoes.index(
                            direcao) + 1 % len(direcoes)]
                        self.movement_system.mover_entidade(ent_id, outra_op)
                            
    def update(self):
        """Processa movimento autônomo de monstros/NPCs a cada tick."""
        self.processar_movimento_autonomo()
                            
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


class InteractionSystem:
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    def interagir(self, entidade_id: int, direcao_olhar: str) -> bool:
        """
        Verifica se há um evento à frente do jogador (ID 1).
        Se houver, publica as informações e parâmetros do evento para o esper,
        delegando a responsabilidade de execução para o EventSystem.
        """
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
    
    
class EventSystem:
    """Sistema processador de eventos universais."""
    
    def __init__(self, inv_sys: InventarySystem, game_state, log_callback, event_bus=None):
        self.inv_sys = inv_sys
        self.game_state = game_state
        self.log_callback = log_callback
        self.event_bus = event_bus
        
        self.pilha_de_comandos = []      # Armazena os blocos de comandos lineares
        self.aguardando_escolha = False
        self.entidade_atual_id = None
        
        


    def processar_evento_interacao(self, payload: dict):
        """Callback disparado pelo esper event_handler  assim que o jogador interage com um bloco."""

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
                
            gatilho = pagina_ativa.get("gatilho", "acao_jogador") #não usado?
            
            comandos = pagina_ativa.get("comandos", [])
            
            self._processar_comandos_sequenciais(comandos, entidade_id)
        except Exception as e:
            logging.info(f"Erro em processar_evento_interacao: {e}")

    def _filtrar_pagina_valida(self, paginas: list, entidade_id: int) -> dict:
        logging.info(f"Filtrando paginas")
        try:
            paginas_ordenadas = sorted(paginas, key=lambda p: p.get("id_pagina", 0), reverse=True)
            for pagina in paginas_ordenadas:
                condicoes = pagina.get("condicoes", {})
                if self._avaliar_condicoes(condicoes, entidade_id):
                    logging.info(f"temos uma pagina")
                    return pagina
            return None
        except Exception as e:
            logging.info(f"Erro em _filtrar_pagina_valida: {e}")
            return None

    def _avaliar_condicoes(self, condicoes: dict, entidade_id: int) -> bool:
        try:
            item_req = condicoes.get("item_requerido")
            if item_req:
                logging.info(f"requer o item {item_req}")
                inv = esper.component_for_entity(1, InventoryComponent)
                if not inv or not self.inv_sys._inventory_has_item(inv, item_req):
                    logging.info(f"mas não tem o item")
                    return False
                    
            switches = condicoes.get("switches", [])
            
            for sw in switches:
                if self.game_state.get_switch(sw["nome"]) != sw.get("valor", True):
                    logging.info(f"A switch {sw} não está ligada")
                    return False
                    
            variaveis = condicoes.get("variaveis", [])
            if len(variaveis) > 0:
                for var in variaveis:
                    atual = self.game_state.get_variable(var["nome"], 0)
                    op = var.get("operador", "igual")
                    
                    val_esperado = var.get("valor", 0)
                    
                    if str(atual).isdigit():
                        atual = int(atual)
                        if op == "maior_ou_igual" and not (atual >= val_esperado): return False
                        if op == "menor_ou_igual" and not (atual <= val_esperado): return False
                        if op == "igual" and not (atual == val_esperado): return False
                        if op == "diferente" and not (atual != val_esperado): return False

                    else:
                        if op == "igual" and not (atual == val_esperado): return False
                        if op == "diferente" and not (atual != val_esperado):  return False
                        
                                
                    logging.info(
                        f"Verificando variável: {var.get("nome", '[Ops: Nada com este nome]')} com o valor: {val_esperado}")
                    
                logging.info(f"Verificou variaveis e o valor é {atual}")


            self_sw = condicoes.get("self_switch")
            if self_sw:
                logging.info(f"requer que a auto condição {self_sw}_Ligada seja verdadeira")
                if not self.game_state.get_switch(f"evento_{entidade_id}_{self_sw}"):
                    logging.info(f"mas a condição [{self_sw}]_Ligada é falsa")
                    return False
                
            return True
        except Exception as e:
            logging.info(f"Erro em _avaliar_condicoes: {e}")
            return False


    def _processar_comandos_sequenciais(self, comandos: list, entidade_id: int):
        
        try:
            self.pilha_de_comandos = [list(comandos)]
            self.aguardando_escolha = False
            self.ramos_disponiveis = {}
            
            self.executar_proximos_comandos()
            
        except Exception as e:
            logging.info(
                f"Erro em _processar_comandos_sequenciais no comando '{comandos}':= {e}")
        
    def executar_proximos_comandos(self):
        """Loop executor não-bloqueante que processa a pilha até o fim ou até uma interrupção."""
        while self.pilha_de_comandos:
            bloco_atual = self.pilha_de_comandos[-1]

            
            if not bloco_atual:
                self.pilha_de_comandos.pop()
                continue

            comando = bloco_atual.pop(0)           
            self._processar_comando_individual(comando)

            # Se o comando executado acima ativou um estado de pausa por pergunta, cede o controle para a TUI
            if self.aguardando_escolha:
                return            
                
                
    def _processar_comando_individual(self, comando):
        """Interpretador genérico e atômico de comandos estruturados do JSON."""
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
            inv = esper.component_for_entity(1, InventoryComponent)
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
            
        elif tipo == "controle_variavel":
            nome = dados.get("nome")
            valor = dados.get("valor")
            operador = dados.get("operador", "=")
            self.game_state.modificar_variavel(nome, operador, valor)


        elif tipo == "bifurcacao_condicional":
            pergunta = dados.get("pergunta", "Escolha uma opção:")
            opcoes = dados.get("opcoes", [])
            ramos = dados.get("ramos", {})

            # Renderiza a pergunta e as opções listadas para a TUI capturar
            self.log_callback(f"[bold yellow]❓ {pergunta}[/]")
            self.ramos_disponiveis = {}

            for idx, opcao in enumerate(opcoes, start=1):
                
                id_op = opcao.replace(' ', '_').replace(
                    ',', '-').replace('.', '')
                id_op = unicodedata.normalize("NFD", id_op)
                id_op = id_op.encode("ASCII", "ignore").decode("ASCII")
                
                # Indexa tanto por número ("1") quanto por texto ("sim") para compatibilidade com chat ou botões
                self.ramos_disponiveis[str(idx)] = ramos.get(id_op, [])
                self.ramos_disponiveis[id_op.strip(
                ).lower()] = ramos.get(id_op, [])

            # 🛑 PAUSA DE BIFURCAÇÃO: Interrompe a execução direta e aguarda a entrada externa
            self.aguardando_escolha = True

            # 🛰️ Opcional: Se for usar a ChoiceBox reativa no Textual, publishe o sinal aqui:
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
        """Injetado externamente pela GamePlayScreen através do #txt-chat ou ChoiceBox."""
        entrada_limpa = str(opcao_escolhida).strip().lower()

        entrada_limpa = entrada_limpa.replace(
            ' ', '_').replace(',', '-').replace('.', '')
        entrada_limpa = unicodedata.normalize("NFD", entrada_limpa)
        entrada_limpa = entrada_limpa.encode("ASCII", "ignore").decode("ASCII")
        
        if entrada_limpa in self.ramos_disponiveis:
            comandos_do_ramo = self.ramos_disponiveis[entrada_limpa]

            # Limpa o travamento de estado
            self.aguardando_escolha = False
            self.ramos_disponiveis = {}

            # Empilha o sub-bloco de comandos correspondente no topo da pilha
            if comandos_do_ramo:    
                self.pilha_de_comandos.append(list(comandos_do_ramo))

            # Retoma o loop sequencial da máquina assíncrona
            self.executar_proximos_comandos()
        else:
            self.log_callback(
                "[bold red]⚠️ Escolha inválida. Selecione uma opção válida.[/]")


esper.clear_dead_entities()