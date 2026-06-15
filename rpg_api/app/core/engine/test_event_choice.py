import esper
import random
import logging
from rich.text import Text
from app.core.engine.components import (
    PositionComponent, InteractableComponent, RenderComponent,
    StatsComponent, AIComponent, InventoryComponent
)
from app.core.entities.emojis import CatalogoTiles

bloqueantes = CatalogoTiles.TERRENOS_BLOQUEANTES
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

# Outros sistemas omitidos para manter o foco...


class InteractionSystem:
    def __init__(self, engine_manager, log_callback, game_state_manager, inv_sys, event_bus):
        self.engine = engine_manager
        self.log_callback = log_callback
        self.game_state = game_state_manager
        self.inv_sys = inv_sys
        self.event_bus = event_bus

    def tentar_interacao(self):
        """
        Verifica se há um evento à frente do jogador (ID 1).
        Se houver, publica as informações e parâmetros do evento para o EventBus,
        delegando a responsabilidade de execução para o EventSystem.
        """
        player_pos = esper.component_for_entity(1, PositionComponent)
        if not player_pos:
            return

        # Calcula a coordenada à frente com base na direção do olhar do herói
        alvo_x, alvo_y = player_pos.x, player_pos.y
        if player_pos.direcao_olhar == "cima":
            alvo_y -= 1
        elif player_pos.direcao_olhar == "baixo":
            alvo_y += 1
        elif player_pos.direcao_olhar == "esquerda":
            alvo_x -= 1
        elif player_pos.direcao_olhar == "direita":
            alvo_x += 1

        # Varre todas as entidades interatíveis para ver se alguma está na coordenada alvo
        for entidade_id, (pos, interact) in esper.get_components(PositionComponent, InteractableComponent):
            if pos.x == alvo_x and pos.y == alvo_y and interact.is_active:
                # 🚀 PUBLICAÇÃO PARA O EVENTBUS:
                # Desacopla a física da interpretação enviando os parâmetros para o EventSystem canalizar.
                payload = {
                    "entidade_id": entidade_id,
                    "event_type": interact.event_type,
                    "parameters": interact.parameters
                }
                self.event_bus.publish("INTERACTION_SUCCESS", payload)
                break


class EventSystem:
    def __init__(self, engine_manager, log_callback, game_state_manager, inv_sys, event_bus):
        self.engine = engine_manager
        self.log_callback = log_callback
        self.game_state = game_state_manager
        self.inv_sys = inv_sys
        self.event_bus = event_bus

        # Infraestrutura de Pilha Assíncrona e Controle de Estados para Diálogos/Bifurcações
        self.pilha_de_comandos = []      # Armazena os blocos de comandos lineares
        # Flag que indica se o jogo está travado por uma pergunta
        self.aguardando_escolha = False
        self.ramos_disponiveis = {}       # Mapeia as opções válidas para o jogador escolher
        # Guarda o ID do evento que está rodando no momento
        self.entidade_atual_id = None

        # Se inscreve no canal do EventBus para escutar os chamados gerados pelo InteractionSystem
        self.event_bus.subscribe("disparar_interacao",
                                 self.ao_receber_chamado_interacao)

    def ao_receber_chamado_interacao(self, payload: dict):
        """Callback disparado pelo EventBus assim que o jogador interage com um bloco."""
        # Se já estiver processando um diálogo com escolha pendente, bloqueia novas concorrências
        if self.aguardando_escolha:
            return

        self.entidade_atual_id = payload.get("entidade_id")
        parametros = payload.get("parameters", {})

        # 🧠 NOVA ENGINE: Padrão RPG Maker com suporte a Páginas Condicionais
        if "paginas" in parametros:
            paginas = parametros["paginas"]
            # Lê de forma decrescente (da maior página para a menor)
            pagina_valida = None
            for pagina in sorted(paginas, key=lambda x: x.get("id_pagina", 0), reverse=True):
                if self._validar_condicoes_pagina(pagina.get("condicoes", {})):
                    pagina_valida = pagina
                    break

            if pagina_valida:
                comandos = pagina_valida.get("comandos", [])
                self._processar_comandos_sequenciais(comandos)

        # ⏳ RETROCOMPATIBILIDADE: Trata os dicionários legados antigos (ex: Baú antigo ou NPC antigo)
        else:
            self._processar_evento_antigo(payload)

    def _validar_condicoes_pagina(self, condicoes: dict) -> bool:
        """Avaliador genérico de condições lógicas no GameStateManager."""
        if not condicoes:
            return True

        # 1. Verifica os Switches Globais
        for sw in condicoes.get("switches", []):
            if self.game_state.get_switch(sw["nome"]) != sw["valor"]:
                return False

        # 2. Verifica as Variáveis Globais (Numéricas ou Textuais)
        for var in condicoes.get("variaveis", []):
            nome = var["nome"]
            operador = var["operador"]
            valor_esperado = var["valor"]
            valor_atual = self.game_state.get_variable(nome)

            if operador == "igual" and valor_atual != valor_esperado:
                return False
            elif operador == "maior_ou_igual" and not (isinstance(valor_atual, (int, float)) and valor_atual >= valor_esperado):
                return False
            elif operador == "menor_ou_igual" and not (isinstance(valor_atual, (int, float)) and valor_atual <= valor_esperado):
                return False
            elif operador == "diferente" and valor_atual == valor_esperado:
                return False

        # 3. Verifica Self Switch local do próprio evento
        if condicoes.get("self_switch"):
            letra = condicoes["self_switch"]
            chave_local = f"self_{self.entidade_atual_id}_{letra}"
            if not self.game_state.get_switch(chave_local):
                return False

        # 4. Verifica se exige algum Item no Inventário do Herói (Entidade ID 1)
        if condicoes.get("item_requerido"):
            item_nome = condicoes["item_requerido"]
            inv = esper.component_for_entity(1, InventoryComponent)
            if not inv or inv.itens.get(item_nome, 0) <= 0:
                return False

        return True

    def _processar_comandos_sequenciais(self, lista_comandos):
        """Inicializa a pilha de execução com o bloco principal de comandos da página ativa."""
        if not lista_comandos:
            return

        self.pilha_de_comandos = [list(lista_comandos)]
        self.aguardando_escolha = False
        self.ramos_disponiveis = {}

        self.executar_proximos_comandos()

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

        if tipo == "mensagem":
            self.log_callback(dados.get("texto", ""))

        elif tipo == "bifurcacao_condicional":
            pergunta = dados.get("pergunta", "Escolha uma opção:")
            opcoes = dados.get("opcoes", [])
            ramos = dados.get("ramos", {})

            # Renderiza a pergunta e as opções listadas para a TUI capturar
            self.log_callback(f"[bold yellow]❓ {pergunta}[/]")
            self.ramos_disponiveis = {}

            for idx, opcao in enumerate(opcoes, start=1):
                self.log_callback(f"  [cyan]{idx} - {opcao}[/]")
                # Indexa tanto por número ("1") quanto por texto ("sim") para compatibilidade com chat ou botões
                self.ramos_disponiveis[str(idx)] = ramos.get(opcao, [])
                self.ramos_disponiveis[opcao.strip(
                ).lower()] = ramos.get(opcao, [])

            # 🛑 PAUSA DE BIFURCAÇÃO: Interrompe a execução direta e aguarda a entrada externa
            self.aguardando_escolha = True

            # 🛰️ Opcional: Se for usar a ChoiceBox reativa no Textual, publishe o sinal aqui:
            self.event_bus.publish("abrir_choice_box", {
                                "pergunta": pergunta, "opcoes": opcoes})
            return

        elif tipo == "controle_switch":
            self.game_state.set_switch(
                dados.get("nome"), dados.get("valor", False))

        elif tipo == "controle_self_switch":
            letra = dados.get("letra", "A")
            valor = dados.get("valor", False)
            # Salva o switch local vinculando dinamicamente ao ID do evento atual para evitar colisões
            chave_local = f"self_{self.entidade_atual_id}_{letra}"
            self.game_state.set_switch(chave_local, valor)

        elif tipo == "mudar_inventario":
            try:
                item_nome = dados.get("item")
                qtd = dados.get("quantidade") or dados.get("qtd") or 1
                operacao = dados.get("operacao", "add")

                inv = esper.component_for_entity(1, InventoryComponent)
                if inv:
                    if operacao == "add":
                        self.inv_sys._inventory_add_item(inv, item_nome, qtd)
                        self.log_callback(
                            f"[yellow]+ {qtd}x {item_nome} adicionado ao inventário.[/]")
                    elif operacao == "sub":
                        atual = inv.itens.get(item_nome, 0)
                        inv.itens[item_nome] = max(0, atual - qtd)
                        self.log_callback(
                            f"[red]- {qtd}x {item_nome} removido do inventário.[/]")
            except Exception as e:
                logging.info(
                    f"Erro ao mudar inventário no comando do EventSystem: {e}")

        elif tipo == "teleporte":
            # 🌌 Transmite o sinal de teleporte para a GamePlayScreen recarregar a engine do zero
            self.event_bus.publish("mudar_mapa", dados)

    def avancar_ramo_evento(self, opcao_escolhida: str):
        """Injetado externamente pela GamePlayScreen através do #txt-chat ou ChoiceBox."""
        entrada_limpa = str(opcao_escolhida).strip().lower()

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
