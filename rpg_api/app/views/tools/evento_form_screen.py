'''
Componente de Formulário de Eventos do Editor de Mapas.

Contém todas as telas modais relacionadas à criação e edição de eventos,
separadas do MapManagerScreen para manter a responsabilidade única de cada módulo.
'''
import copy
import json
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Select, ListView, ListItem, Static, RichLog
from textual.containers import Horizontal, Vertical, Container
from textual import on
from rich.text import Text
from app.db.database import SessionLocal
from app.models.mapas_db import MapaDB
from app.models.equipamentos_db import ItemDB
from app.core.entities.emojis import CatalogoTiles, dict_item_emoji, dict_emoji_efeito, dict_emoji_racas
from app.views.tools.painting_tools import  MapaInterativo
import logging
logging.basicConfig(level=logging.INFO, filename='log.log', filemode='a')
from typing import Literal
import emoji

Modo_de_Captura = Literal["config_ini", None]
#CSS_PATH = 'styles/styles.css'


# ==============================================================================
# TELA PRINCIPAL: FORMULÁRIO DE PROPRIEDADES DO EVENTO
# ==============================================================================
class PropriedadesEventoFormScreen(ModalScreen[dict]):
    '''
    Formulário principal que gerencia o JSON do evento com páginas e comandos.

    Recebe os dados do evento existente (ou None para novo evento) e permite
    configurar nome, emoji, gatilho, condições por página e lista de comandos.
    Ao confirmar, retorna um dicionário com os dados consolidados para o
    MapManagerScreen persistir na memória e no banco de dados.
    '''

    BINDING = [('esq', 'self.dismiss(None)', '')]

    def __init__(self, linha: int, coluna: int, emoji: str, dados_existentes: dict = None):
        super().__init__()
        self.linha_y_do_evento = linha
        self.coluna_x_do_evento = coluna
        self.emoji = emoji
        self.dados_existentes = copy.deepcopy(dados_existentes) or {}

        # Estrutura JSON Universal de Páginas
        evt_parametros = self.dados_existentes.get('parametros', {})
        if 'paginas' not in evt_parametros:
            # Evento simples ou novo: inicia com uma página padrão
            self.paginas = [
                {
                    'id_pagina': 1,
                    'condicoes': {},
                    'configuracao_visual': {'emoji': self.emoji},
                    'gatilho': 'acao_jogador',
                    "movimento": {'tipo': 'parado'},
                    'comandos': []
                }
            ]
        else:
            self.paginas = evt_parametros['paginas']

        self.pagina_atual_idx = 0

    def compose(self):
        itens_set = set([v for sub_dict in dict_item_emoji.values()
                        for k, v in sub_dict.items()])
        racas_set = set([v for _, v in dict_emoji_racas.items()])
        efeitos_set = set([v for _, v in dict_emoji_efeito.items()])
        paleta_set = set(CatalogoTiles.OBJETOS + CatalogoTiles.TERRENOS + CatalogoTiles.TERRENOS_BLOQUEANTES + CatalogoTiles.EVENTOS )
        sem_repetidos = set(
            [*itens_set, *racas_set, *efeitos_set, *paleta_set])
        coletanea_emoji = list(sem_repetidos)

        with Vertical(id='evt-caixa-full'):
            #titulo = f'🛠️ Evento em [{self.linha_y_do_evento},{self.coluna_x_do_evento}]'
            #yield Label( titulo, classes='titulo-secao')
            # with Horizontal(classes='linha-dupla'):
            #     yield Label('Nome do Evento:', classes='campo-rotulo')
            #     yield Label('Emoji:', classes='campo-rotulo')
            with Horizontal(classes='linha-dupla'):

                yield Input(
                    value=self.dados_existentes.get(
                        'nome', f'ev_{self.linha_y_do_evento}_{self.coluna_x_do_evento}'),
                    id='evt-nome')
                yield Select(
                    [(v, v) for v in coletanea_emoji] +
                    [(self.emoji, self.emoji)],
                    value=emoji.emojize(self.paginas[self.pagina_atual_idx].get("configuracao_visual",{}).get("emoji", self.emoji)),
                    id='evt-emoji')
                #yield Label('Página:', classes='campo-rotulo')
                yield Button('<', id='btn-pag-ant', classes='btn-pequeno')
                yield Label(f' {self.pagina_atual_idx + 1} / {len(self.paginas)} ', id='lbl-pag-atual')
                yield Button('>', id='btn-pag-prox', classes='btn-pequeno')
                yield Button('+ Pág', id='btn-add-pag', variant='primary', classes='btn-pequeno')
                yield Button('- Pág', id='btn-del-pag', variant='error', classes='btn-pequeno')

            with Horizontal(classes='linha-dupla'):
                #yield Label('Movimento do Evento:', classes='campo-rotulo')
                yield Select([('Parado', 'parado'), 
                            ('Aleatório', 'aleatorio'),
                            ('Seguir Herói', 'seguir_heroi'),
                            ('Fugir do Herói', 'fugir_heroi'),
                            ('Roteiro de Movimento', 'roteiro')],
                            value=self.paginas[self.pagina_atual_idx].get('movimento', {}).get('tipo', 'parado'),
                            id='evt-movimento')
                    
                #yield Label('Gatilho:', classes='campo-rotulo')
                yield Select([
                    ('Ação do Jogador (Pressionar Botão)', 'acao_jogador'),
                    ('Toque do Jogador (Pisar)', 'toque_jogador'),
                    ('Toque do Evento (Bater no herói)', 'toque_evento'),
                    ('Processo Automático', 'processo_automatico'),
                    ('Processo Paralelo', 'processo_paralelo')
                ], value=self.paginas[self.pagina_atual_idx].get('gatilho', 'acao_jogador'), id='evt-gatilho')

            with Container(classes='container-roteiro'):
                with Vertical():
                    with Horizontal(classes='linha-dupla'):
                        yield Button('⏫ ', id='btn-roteiro-up', flat=True, variant='warning', classes='btn-pequeno')
                        yield Button('⏩ ', id='btn-roteiro-right', flat=True, variant='warning', classes='btn-pequeno')
                        yield Button('⏬ ', id='btn-roteiro-down', flat=True, variant='warning', classes='btn-pequeno')
                        yield Button('⏪ ', id='btn-roteiro-left', flat=True, variant='warning', classes='btn-pequeno')
                        yield Button('⛔Limpa', id='btn-roteiro-limpa', flat=True, variant='warning', classes='btn-pequeno')
                    
                    yield Input(placeholder='Direções do Roteiro', disabled=True ,id='id_roteiro_mv',
                                valid_empty=False,
                                value=','.join(self.paginas[self.pagina_atual_idx].get('movimento', {}).get('roteiro', '')))
                

            # ==========================================
            # SEÇÃO DE CONDIÇÕES DA PÁGINA
            # ==========================================
            yield Label('📋 Condições desta Página:', classes='campo-rotulo')
            with Vertical(id='secao-condicoes'):
                # --- Switches ---
                with Horizontal(classes='linha-dupla'):
                    yield Label('Interruptores:', classes='campo-rotulo')
                    yield Button(' + ', id='btn-add-switch', variant='primary', 
                                 tooltip=str('''Um nome chave(Ligada/Desligada) 
                                             que quando atribuída, passa a ser
                                             a condição, que deve ser acionada 
                                             por um evento, para que esta página
                                             possa ser acionada.
                                             Exemplo:  Evento A: comando
                                             [0] controle_switch {
                                                 "nome": "falou_para_mago",
                                                 "valor": "Ligar(true)"} 
                                            Significa que a variável: 
                                            falou_para_mago passa a ser Verdadeira.
                                 '''), classes='btn-pequeno')
                    yield ListView(id='lista-switches')

                # --- Variáveis ---
                with Horizontal(classes='linha-dupla'):
                    yield Label('Variáveis:', classes='campo-rotulo')
                    yield Button(' + ', id='btn-add-variavel', variant='primary',
                                 tooltip=str('''Um nome para um valor que pode variar
                                             e que quando atribuída nos comandos
                                             de um evento acionado, passa a ser o valor
                                             condição para esta página poder ser acionada.
                                             Exemplo:  Evento A: comando
                                             [0] controle_variavel {
                                                 "nome": "quantos_cafes_tomou",
                                                 "operador": "+",
                                                 "valor": "1"} 
                                            adiciona 1 ao valor de "quantos_cafes_tomou"
                                 '''), classes='btn-pequeno')
                    yield ListView( id='lista-variaveis')

                # --- Self Switch ---
                with Horizontal(classes='linha-dupla'):
                    yield Label('Interruptor Próprio:', classes='campo-rotulo')
                    yield Select([
                        ('Nenhum', 'nenhum'),
                        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
                    ], value='nenhum',
                        tooltip=str('''Uma valor de chave própria(A, B, C, D) que quando atribuída nos comandos de
                                    um evento acionado, passa a ser determinante para esta página poder 
                                    ser acionada. Exemplo:  Evento A: comando
                                    [0] controle_de_self_switch {"letra": "A", "valor": true (Ligar)}
                                 '''), id='evt-self-switch')

                # --- Item Requerido ---
                    yield Label('Item Requerido:', classes='campo-rotulo')
                    yield Select([], id='evt-item-requerido')

            yield Label('Comandos da Página:', classes='campo-rotulo')
            yield ListView(id='lista-comandos')

            with Horizontal(id='evt-botoes'):
                yield Button('+ Adicionar Comando', id='btn-add-cmd', variant='primary')
                yield Button('Cancelar', id='btn-evt-cancelar', variant='error')
                yield Button('Salvar Evento', id='btn-evt-salvar', variant='success')

    def on_mount(self):
        with SessionLocal() as db:
            itens = db.query(ItemDB).all()
            self.query_one("#evt-item-requerido", Select).set_options([
                (str(i.nome), str(i.id)) for i in itens
            ] + [('nada','')])
        self.query_one(".container-roteiro").display = False
        
        self.atualizar_tela_pagina()

    # ==========================================
    # LÓGICA DE NAVEGAÇÃO ENTRE PÁGINAS
    # ==========================================

    def atualizar_tela_pagina(self):
        '''Atualiza todos os widgets com os dados da página atual.'''
        lbl = self.query_one('#lbl-pag-atual', Label)
        lbl.update(f' {self.pagina_atual_idx + 1} / {len(self.paginas)} ')

        select_gatilho = self.query_one('#evt-gatilho', Select)
        select_gatilho.value = self.paginas[self.pagina_atual_idx].get(
            'gatilho', 'acao_jogador')
        select_movimento = self.query_one('#evt-movimento', Select)
        select_movimento.value = self.paginas[self.pagina_atual_idx].get(
            'movimento', {}).get('tipo', 'parado')
        select_emoji = self.query_one('#evt-emoji', Select)
        select_emoji.value = emoji.emojize(self.paginas[self.pagina_atual_idx].get(
            'configuracao_visual', {}).get('emoji', self.emoji))
        

        self.atualizar_exibicao_condicoes()
        self.atualizar_lista_comandos()

    # ==========================================
    # LÓGICA DE CONDIÇÕES DA PÁGINA
    # ==========================================

    def _obter_condicoes_pagina_atual(self) -> dict:
        '''Retorna o dict de condições da página atual, criando se não existir.'''
        pagina = self.paginas[self.pagina_atual_idx]
        if 'condicoes' not in pagina:
            pagina['condicoes'] = {}
        return pagina['condicoes']

    def atualizar_exibicao_condicoes(self):
        '''Popula os widgets de condições com os dados da página atual.'''
        condicoes = self._obter_condicoes_pagina_atual()


        # --- Switches ---
        switches = condicoes.get('switches', [])
        lista_sw = self.query_one('#lista-switches', ListView)
        lista_sw.clear()
        if len(switches) > 0:
            for i, switch in enumerate(switches):
                val_str = '✅ True' if switch.get('valor', True) else '❌ False'
                texto_switch = ListItem(Horizontal(
                    Label(f'  [{i}] {switch["nome"]} = {val_str}'),
                    Button(
                        " - ", name=f"btn-del-sw-{i}", variant="error", classes="btn-pequeno"),
                    classes="linha-condicional-item"))
                lista_sw.append(texto_switch)


        # --- Variáveis ---
        variaveis = condicoes.get('variaveis', [])
        conteiner_vars = self.query_one('#lista-variaveis', ListView)
        conteiner_vars.clear()
        if len(variaveis) > 0:
            op_simbolos = {
                'maior_ou_igual': '>=', 'menor_ou_igual': '<=',
                'igual': '==', 'diferente': '!='
            }
            
            # 2. Iteramos criando uma linha visual para cada variável
            for i, var in enumerate(variaveis):
                op = op_simbolos.get(var.get('operador', 'igual'), '==')
                texto_linha = f'[{i}] {var["nome"]} {op} {var.get("valor", 0)}'
                
                linha_layout = ListItem(Horizontal(
                    Label(texto_linha, classes="texto-var"),
                    Button(
                        " - ", name=f"btn-del-var-{i}", variant="error", classes="btn-pequeno"),
                ), classes="linha-condicional-item")
                conteiner_vars.append(linha_layout)
        # else:
        #     conteiner_vars.append(
        #         ListItem(Label('  (nenhuma)'), classes="linha-condicional-item"))


        # --- Self Switch ---
        self_switch = condicoes.get('self_switch', 'nenhum')
        select_ssw = self.query_one('#evt-self-switch', Select)
        select_ssw.value = self_switch or 'nenhum'

        # --- Item Requerido ---
        item_req = condicoes.get('item_requerido') or ''
        self.query_one('#evt-item-requerido', Select).value = item_req

    def atualizar_lista_comandos(self):
        '''Renderiza a lista de comandos da página atual.'''
        lista = self.query_one('#lista-comandos', ListView)
        lista.clear()
        comandos = self.paginas[self.pagina_atual_idx].get('comandos', [])
        for i, comando in enumerate(comandos):
            dados_str = json.dumps(comando["dados"], ensure_ascii=False, indent=2)
            texto = f'[{i}] {comando["tipo"]}\n{dados_str}'
            lista.append(ListItem(Label(texto), name=str(i)))

    # ==========================================
    # REACTIVE HANDLERS
    # ==========================================

    @on(Select.Changed, '#evt-gatilho')
    def on_gatilho_changed(self, event: Select.Changed):
        if event.value != Select.BLANK:
            self.paginas[self.pagina_atual_idx]['gatilho'] = event.value
            
    @on(Select.Changed, '#evt-movimento')
    def on_movimento_changed(self, event: Select.Changed):
        if event.value != Select.BLANK:
            self.paginas[self.pagina_atual_idx]['movimento'] = {'tipo': event.value}
            
        if event.value == 'roteiro':
            self.query_one(".container-roteiro").display = True
        else:
            self.query_one(".container-roteiro").display = False
    
            
    @on(Select.Changed, '#evt-emoji')
    def on_emoji_changed(self, event: Select.Changed):
        if event.value != Select.BLANK:
            self.paginas[self.pagina_atual_idx]['configuracao_visual'] = {
                'emoji': event.value}

    @on(Select.Changed, '#evt-self-switch')
    def on_self_switch_changed(self, event: Select.Changed):
        '''Sincroniza o self_switch da página atual quando o Select muda.'''
        if event.value == Select.BLANK:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        if event.value == 'nenhum':
            condicoes.pop('self_switch', None)
        else:
            condicoes['self_switch'] = event.value

    @on(Select.Changed, '#evt-item-requerido')
    def on_item_requerido_changed(self, event: Select.Changed):
        '''Sincroniza o item_requerido da página atual quando o Input muda.'''
        condicoes = self._obter_condicoes_pagina_atual()
        if event and event.value not in ['', 'NoSelection', Select.BLANK, Select.NULL]:
            value = event.value.strip()
            condicoes['item_requerido'] = value
        else:
            value = None
            condicoes.pop('item_requerido', None)

    # ==========================================
    # HANDLERS DE BOTÕES
    # ==========================================

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-evt-cancelar':
            self.dismiss(None)

        elif event.button.id == 'btn-pag-ant':
            if self.pagina_atual_idx > 0:
                self.pagina_atual_idx -= 1
                self.atualizar_tela_pagina()

        elif event.button.id == 'btn-pag-prox':
            if self.pagina_atual_idx < len(self.paginas) - 1:
                self.pagina_atual_idx += 1
                self.atualizar_tela_pagina()

        elif event.button.id == 'btn-add-pag':
            nova_pagina = {
                'id_pagina': len(self.paginas) + 1,
                'condicoes': {},
                'configuracao_visual': {'emoji': self.query_one('#evt-emoji').value},
                'movimento': {'tipo': 'parado'},
                'gatilho': 'acao_jogador',
                'comandos': []
            }
            self.paginas.append(nova_pagina)
            self.pagina_atual_idx = len(self.paginas) - 1
            self.atualizar_tela_pagina()

        elif event.button.id == 'btn-del-pag':
            if len(self.paginas) > 1:
                self.paginas.pop(self.pagina_atual_idx)
                # Reordena IDs
                for i, p in enumerate(self.paginas):
                    p['id_pagina'] = i + 1
                self.pagina_atual_idx = min(
                    self.pagina_atual_idx, len(self.paginas) - 1)
                self.atualizar_tela_pagina()
            else:
                self.notify('Não é possível deletar a única página!',
                            severity='warning')

        elif event.button.id == 'btn-add-cmd':
            self.app.push_screen(AdicionarComandoScreen(),
                                 self.ao_adicionar_comando)

        # --- Botões de Condições ---
        elif event.button.id == 'btn-add-switch':
            self.app.push_screen(AdicionarSwitchScreen(),
                                 self.ao_adicionar_switch)

        elif event.button.id == 'btn-add-variavel':
            self.app.push_screen(AdicionarVariavelScreen(),
                                 self.ao_adicionar_variavel)

        elif event.button.name and event.button.name.startswith('btn-del-sw-'):
            idx_sw = int(event.button.name.replace('btn-del-sw-', ''))
            self._remover_switch(idx_sw)

        elif event.button.name and event.button.name.startswith('btn-del-var-'):
            idx_var = int(event.button.name.replace('btn-del-var-', ''))
            self._remover_variavel(idx_var)
            
        elif event.button.id == 'btn-roteiro-up':
            roteiro_atual = self.query_one('#id_roteiro_mv').value
            self.query_one('#id_roteiro_mv').value = roteiro_atual + ', cima'  if len(roteiro_atual) > 0 else 'cima'
            self.paginas[self.pagina_atual_idx]['movimento']['roteiro'] =  [dir for dir in self.query_one(
                '#id_roteiro_mv').value.split(',')]
            
        elif event.button.id == 'btn-roteiro-down':
            roteiro_atual = self.query_one('#id_roteiro_mv').value
            self.query_one('#id_roteiro_mv').value = roteiro_atual + ', baixo'  if len(roteiro_atual) > 0 else 'baixo'
            self.paginas[self.pagina_atual_idx]['movimento']['roteiro'] =  [dir for dir in self.query_one(
                '#id_roteiro_mv').value.split(',')]
            
        elif event.button.id == 'btn-roteiro-right':
            roteiro_atual = self.query_one('#id_roteiro_mv').value
            self.query_one('#id_roteiro_mv').value = roteiro_atual + ', direita' if len(roteiro_atual) > 0 else 'direita'
            self.paginas[self.pagina_atual_idx]['movimento']['roteiro'] =  [dir for dir in self.query_one(
                '#id_roteiro_mv').value.split(',')]
            
        elif event.button.id == 'btn-roteiro-left':
            roteiro_atual = self.query_one('#id_roteiro_mv').value
            self.query_one('#id_roteiro_mv').value = roteiro_atual + ', esquerda' if len(roteiro_atual) > 0 else 'esquerda'
            self.paginas[self.pagina_atual_idx]['movimento']['roteiro'] = [dir for dir in self.query_one(
                '#id_roteiro_mv').value.split(',')]

        elif event.button.id == 'btn-roteiro-limpa':
            self.query_one('#id_roteiro_mv').value = ''
            
        elif event.button.id == 'btn-evt-salvar':
            nome = self.query_one('#evt-nome').value
            emoji = self.query_one('#evt-emoji').value

            parametros = {'paginas': self.paginas}

            dados_retorno = {
                'nome': nome,
                'emoji': emoji,
                'event_type': 'evento_custom',
                'parametros': parametros
            }
            if 'id' in self.dados_existentes:
                dados_retorno['id'] = self.dados_existentes['id']

            self.dismiss(dados_retorno)

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == 'lista-comandos':
            idx = int(event.item.name)
            cmd = self.paginas[self.pagina_atual_idx]['comandos'][idx]
            self.app.push_screen(
                AcoesComandoScreen(cmd),
                lambda acao: self.ao_acao_comando(acao, idx))

    # ==========================================
    # CALLBACKS DE CONDIÇÕES
    # ==========================================

    def ao_adicionar_switch(self, dados_switch: dict | None):
        '''Callback do modal AdicionarSwitchScreen.'''
        if dados_switch is None:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        condicoes.setdefault('switches', []).append(dados_switch)
        self.atualizar_exibicao_condicoes()
        self.notify(f'Switch "{dados_switch["nome"]}" adicionado!')

    def ao_adicionar_variavel(self, dados_variavel: dict | None):
        '''Callback do modal AdicionarVariavelScreen.'''
        if dados_variavel is None:
            return
        condicoes = self._obter_condicoes_pagina_atual()
        condicoes.setdefault('variaveis', []).append(dados_variavel)
        self.atualizar_exibicao_condicoes()
        self.notify(f'Variável "{dados_variavel["nome"]}" adicionada!')

    def _remover_switch(self, idx: int):
        '''Remove um switch pelo índice da lista.'''
        condicoes = self._obter_condicoes_pagina_atual()
        switches = condicoes.get('switches', [])
        if 0 <= idx < len(switches):
            removido = switches.pop(idx)
            self.atualizar_exibicao_condicoes()
            self.notify(f'Switch "{removido["nome"]}" removido.')

    def _remover_variavel(self, idx: int):
        '''Remove uma variável pelo índice da lista.'''
        condicoes = self._obter_condicoes_pagina_atual()
        variaveis = condicoes.get('variaveis', [])
        if 0 <= idx < len(variaveis):
            removido = variaveis.pop(idx)
            self.atualizar_exibicao_condicoes()
            self.notify(f'Variável "{removido["nome"]}" removida.')

    # ==========================================
    # CALLBACKS DE COMANDOS
    # ==========================================

    def ao_adicionar_comando(self, novo_comando):
        if novo_comando:
            self.paginas[self.pagina_atual_idx].setdefault(
                'comandos', []).append(novo_comando)
            self.atualizar_lista_comandos()

    def ao_acao_comando(self, acao: str, idx: int):
        if not acao:
            return
        comandos = self.paginas[self.pagina_atual_idx]['comandos']
        if acao == 'excluir':
            comandos.pop(idx)
            self.atualizar_lista_comandos()
        elif acao == 'editar':
            cmd = comandos[idx]
            self.app.push_screen(
                AdicionarComandoScreen(cmd),
                lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith('editar_ramo_'):
            ramo_nome = acao.replace('editar_ramo_', '')
            cmd = comandos[idx]
            ramos = cmd['dados'].setdefault('ramos', {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            self.app.push_screen(
                RamoEditorScreen(ramo_nome, ramo_cmds),
                lambda novos_cmds: self.ao_salvar_ramo(novos_cmds, idx, ramo_nome))

    def ao_salvar_edicao_comando(self, novo_comando, idx):
        if novo_comando:
            # Mantemos os ramos caso seja bifurcação para não perder se não editou
            if novo_comando['tipo'] == self.paginas[self.pagina_atual_idx]['comandos'][idx]['tipo']:
                if 'ramos' in self.paginas[self.pagina_atual_idx]['comandos'][idx]['dados']:
                    novo_comando['dados']['ramos'] = (
                        self.paginas[self.pagina_atual_idx]['comandos'][idx]['dados']['ramos']
                    )
            self.paginas[self.pagina_atual_idx]['comandos'][idx] = novo_comando
            self.atualizar_lista_comandos()

    def ao_salvar_ramo(self, novos_cmds, idx, ramo_nome):
        if novos_cmds is not None:
            self.paginas[self.pagina_atual_idx]['comandos'][idx]['dados']['ramos'][ramo_nome] = novos_cmds
            self.atualizar_lista_comandos()

    # ==========================================
    # CAPTURA / RESTAURAÇÃO DE ESTADO (Modo Mira)
    # ==========================================

    def _capturar_valores_campos_atuais(self) -> dict:
        '''Serializa o estado atual dos inputs para não perder o progresso digitado.'''
        return {
            'nome': self.query_one('#evt-nome').value,
            'emoji': self.query_one('#evt-emoji').value,
            'gatilho': self.query_one('#evt-gatilho').value,
            'item-requerido': self.query_one('#evt-item-requerido').value,
            'self-switch': self.query_one('#evt-self-switch').value,
            'lista-variaveis': self.query_one('#lista-variaveis').value,
            'lista-switches': self.query_one('#lista-switches').value,
            'lista-comandos': self.query_one('#lista-comandos').value,
            'movimento': self.query_one('#evt-movimento').value,
            'mapa_teleporte': self.query_one('#cmd-tel-mapa').value,
            'linha_teleporte': self.query_one('#cmd-tel-y').value,
            'coluna_teleporte': self.query_one('#cmd-tel-x').value,
        }

    def restaurar_valores_dos_campos(
        self,
        dados: dict,
        linha_coletada: int = None,
        coluna_coletada: int = None,
        id_alvo: str = None
    ) -> None:
        '''Preenche o formulário com o snapshot e injeta a nova coordenada no local exato.'''
        self.query_one('#evt-nome').value = dados.get('nome', '')
        self.query_one('#evt-emoji').value = dados.get('emoji', '')
        self.query_one('#evt-gatilho').value = dados.get('gatilho', '')
        self.query_one(
            '#evt-item-requerido').value = dados.get('item-requerido', '')
        self.query_one('#evt-self-switch').value = dados.get('self-switch', '')
        self.query_one(
            '#lista-variaveis').value = dados.get('lista-variaveis', '')
        self.query_one(
            '#lista-switches').value = dados.get('lista-switches', '')
        self.query_one(
            '#lista-comandos').value = dados.get('lista-comandos', '')
        try:
            self.query_one(
                '#evt-movimento').value = dados.get('movimento', 'parado').get('tipo', 'parado')
        except Exception as e:
            raise RuntimeError(f'Erro: não consegue obter o tipo: {e}')

        self.query_one('#cmd-tel-y').value = str(linha_coletada)
        self.query_one('#cmd-tel-x').value = str(coluna_coletada)


# ==============================================================================
# SUB-MODAL: ADICIONAR SWITCH À CONDIÇÃO
# ==============================================================================
class AdicionarSwitchScreen(ModalScreen[dict]):
    '''Modal simples para adicionar uma condição de Switch a uma página.'''

    def compose(self):
        with Vertical(id='add-cmd-caixa'):
            yield Label('🔀 Adicionar Condição de Switch', classes='titulo-secao')
            yield Label('Nome do Switch:')
            yield Input(placeholder='Ex: missao_guarda_ativa', id='sw-nome')
            yield Label('Valor Esperado:')
            yield Select([
                ('Ligado (True)', 'true'),
                ('Desligado (False)', 'false')
            ], value='true', id='sw-valor')
            with Horizontal(id='evt-botoes'):
                yield Button('Cancelar', id='btn-cancel', variant='error')
                yield Button('Confirmar', id='btn-save', variant='success')

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-cancel':
            self.dismiss(None)
        elif event.button.id == 'btn-save':
            nome = self.query_one('#sw-nome', Input).value.strip()
            if not nome:
                self.notify('Preencha o nome do switch!', severity='error')
                return
            valor = self.query_one('#sw-valor', Select).value == 'true'
            self.dismiss({'nome': nome, 'valor': valor})


# ==============================================================================
# SUB-MODAL: ADICIONAR VARIÁVEL À CONDIÇÃO
# ==============================================================================
class AdicionarVariavelScreen(ModalScreen[dict]):
    '''Modal simples para adicionar uma condição de Variável numérica a uma página.'''

    def compose(self):
        with Vertical(id='add-cmd-caixa'):
            yield Label('📊 Adicionar Condição de Variável', classes='titulo-secao')
            yield Label('Nome da Variável:')
            yield Input(placeholder='Ex: reputacao', id='var-nome')
            yield Label('Operador:')
            yield Select([
                ('Maior ou Igual (>=)', 'maior_ou_igual'),
                ('Menor ou Igual (<=)', 'menor_ou_igual'),
                ('Igual (==)', 'igual'),
                ('Diferente (!=)', 'diferente')
            ], value='maior_ou_igual', id='var-operador')
            yield Label('Valor:')
            yield Input(placeholder='Ex: 15', id='var-valor', value='0')
            with Horizontal(id='evt-botoes'):
                yield Button('Cancelar', id='btn-cancel', variant='error')
                yield Button('Confirmar', id='btn-save', variant='success')

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-cancel':
            self.dismiss(None)
        elif event.button.id == 'btn-save':
            nome = self.query_one('#var-nome', Input).value.strip()
            if not nome:
                self.notify('Preencha o nome da variável!', severity='error')
                return
            try:
                valor = int(self.query_one('#var-valor', Input).value)
            except ValueError:
                self.notify('O valor deve ser numérico!', severity='error')
                return
            operador = self.query_one('#var-operador', Select).value
            if operador == Select.BLANK:
                self.notify('Selecione um operador!', severity='error')
                return
            self.dismiss({'nome': nome, 'operador': operador, 'valor': valor})
            

# ==============================================================================
# SUB-MODAL: ADICIONAR / EDITAR COMANDO
# ==============================================================================
class AdicionarComandoScreen(ModalScreen[dict]):
    '''Sub-formulário para gerar comandos baseados no tipo selecionado.'''

    def __init__(self, comando_existente: dict = None):
        super().__init__()
        self.comando_existente = comando_existente
        logging.info(f'dados existentes {comando_existente}')

    def compose(self):
        with Vertical(id='add-cmd-caixa'):
            yield Label('Escolha o tipo de Comando', classes='titulo-secao')
            yield Select([
                ('Mensagem no prompt (Texto)', 'mensagem'),
                ('Notificação na tela (Texto)', 'notificacao'),
                ('Teleporte (Mudar Mapa/Posição)', 'teleporte'),
                ('Inventário (Add/Sub)', 'mudar_inventario'),
                ('Status do Herói (HP/MP)', 'mudar_status_heroi'),
                ('Bifurcação Condicional (Opções)', 'bifurcacao_condicional'),
                ('Variável (Valor)', 'controle_variavel'),
                ('Switch (Liga/Desliga)', 'controle_switch'),
                ('Self Switch (Local)', 'controle_self_switch'),
                ('⚔️ Iniciar Combate (Batalha)', 'iniciar_combate'),
            ], id='cmd-tipo')
            yield Container(id='cmd-form-container')
            with Horizontal(id='evt-botoes'):
                yield Button('Cancelar', id='btn-cancel', variant='error')
                yield Button('Confirmar', id='btn-save', variant='success')

    def on_mount(self):
        if self.comando_existente:
            self.query_one('#cmd-tipo', Select).value = self.comando_existente['tipo']

    @on(Select.Changed, '#cmd-tipo')
    def on_tipo_changed(self, event: Select.Changed):
        container = self.query_one('#cmd-form-container')
        container.remove_children()
        tipo = event.value

        dados = {}
        if self.comando_existente and self.comando_existente['tipo'] == tipo:
            dados = self.comando_existente.get('dados', {})

        if tipo == 'mensagem':
            container.mount(Input(
                placeholder='Texto da mensagem (Use tags [color] se quiser)',
                id='cmd-msg-texto', value=dados.get('texto', '')))

        elif tipo == 'notificacao':
            container.mount(Input(
                placeholder='Texto da notificação (Use tags [color] se quiser)',
                id='cmd-notif-texto', value=dados.get('texto', '')))

        elif tipo == 'teleporte':
            with SessionLocal() as db:
                mapas = db.query(MapaDB).all()
                opcoes = [(m.nome, str(m.id)) for m in mapas] + [("", "")]

            container.mount(Select(opcoes, id='cmd-tel-mapa', value=str(dados.get('mapa_id', ''))))
            container.mount(Button('📍 Selecione o local.', id='btn-select-pos-xy', variant = "success"
            ))
            container.mount(Input(
                placeholder='Coordenada X (Coluna)',
                id='cmd-tel-x', value=str(dados.get('pos_x', ''))))
            container.mount(Input(
                placeholder='Coordenada Y (Linha)',
                id='cmd-tel-y', value=str(dados.get('pos_y', ''))))

        elif tipo == 'mudar_inventario':
            container.mount(Input(
                placeholder='Nome exato do Item (ex: pocao_cura)',
                id='cmd-inv-item', value=dados.get('item', '')))
            container.mount(Select(
                [('Adicionar', 'add'), ('Remover', 'sub')],
                value=dados.get('operacao', 'add'), id='cmd-inv-op'))
            container.mount(Input(
                placeholder='Quantidade (ex: 1)',
                value=str(dados.get('quantidade', 1)), id='cmd-inv-qtd'))

        elif tipo == 'mudar_status_heroi':
            container.mount(Select(
                [('Vida (HP) atual', 'hp'), ('Mana (MP) atual', 'mp'),
                 ('Vida (HP) máximo', 'hp_max'), ('Mana (MP) máximo', 'mp_max')],
                value=dados.get('parametro', 'hp'), id='cmd-stat-param'))
            container.mount(Select(
                [('Aumentar (Add)', 'add'), ('Diminuir (Sub)', 'sub')],
                value=dados.get('operacao', 'add'), id='cmd-stat-op'))
            container.mount(Input(
                placeholder='Valor Numérico',
                value=str(dados.get('valor', 10)), id='cmd-stat-valor'))

        elif tipo == 'bifurcacao_condicional':
            container.mount(Input(
                placeholder='Pergunta ao Jogador?',
                id='cmd-bif-pergunta', value=dados.get('pergunta', '')))
            opcoes = dados.get('opcoes', ['', ''])
            op1 = opcoes[0] if len(opcoes) > 0 else ''
            op2 = opcoes[1] if len(opcoes) > 1 else ''
            container.mount(Input(placeholder='Opção 1 (ex: Sim)', id='cmd-bif-op1', value=op1))
            container.mount(Input(placeholder='Opção 2 (ex: Não)', id='cmd-bif-op2', value=op2))

        elif tipo == 'controle_switch':
            container.mount(Input(
                placeholder='Nome da Switch',
                id='cmd-sw-nome', value=dados.get('nome', '')))
            val_str = 'true' if dados.get('valor', True) else 'false'
            container.mount(Select(
                [('Ligar (True)', 'true'), ('Desligar (False)', 'false')],
                value=val_str, id='cmd-sw-valor'))

        elif tipo == 'controle_self_switch':
            container.mount(Select(
                [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                value=dados.get('letra', 'A'), id='cmd-ssw-letra'))
            val_str = 'true' if dados.get('valor', True) else 'false'
            container.mount(Select(
                [('Ligar (True)', 'true'), ('Desligar (False)', 'false')],
                value=val_str, id='cmd-ssw-valor'))

        elif tipo == 'controle_variavel':
            container.mount(Input(
                placeholder='Nome da Variável',
                id='cmd-variavel-nome', value=dados.get('nome', '')))
            container.mount(Select(
                [(' = ', '='), (' + ', '+'), (' - ', '-'), (' * ', '*'), (' / ', '//')],
                value=dados.get('operador', '='), id='cmd-variavel-operador'))
            container.mount(Input(
                placeholder='Valor atribuido',
                id='cmd-variavel-valor', value=dados.get('valor', '')))

        elif tipo == 'iniciar_combate':
            # --- Campos de Configuração do Inimigo ---
            container.mount(Label('👹  Inimigo:', classes='campo-rotulo'))
            container.mount(Input(
                placeholder='Nome do Inimigo (ex: Goblin Guerreiro)',
                id='cmd-bat-nome',
                value=dados.get('nome', 'Goblin')))
            container.mount(Input(
                placeholder='Nível do Inimigo (1-20)',
                id='cmd-bat-nivel',
                value=str(dados.get('nivel', 1))))
            container.mount(Select([
                    ('Humano', 'Humano'), ('Goblin', 'Goblin'), ('Orc', 'Orc'),
                    ('Elfo', 'Elfo'), ('Anão', 'Anão'), ('Morto-Vivo', 'Morto-Vivo'),
                    ('Dragão', 'Dragão'), ('Espírito', 'Espirito'),
                ],
                value=dados.get('raca', 'Goblin'),
                id='cmd-bat-raca'))
            container.mount(Select([
                    ('Guerreiro', 'Guerreiro'), ('Arqueiro', 'Arqueiro'),
                    ('Mago', 'Mago'), ('Bárbaro', 'Barbaro'), ('Ladino', 'Ladino'),
                ],
                value=dados.get('classe', 'Guerreiro'),
                id='cmd-bat-classe'))
            container.mount(Label('📊  Atributos Base (0 a 5):', classes='campo-rotulo'))
            container.mount(Input(
                placeholder='Força Base (0-5)',
                id='cmd-bat-forca',
                value=str(dados.get('forca', 2))))
            container.mount(Input(
                placeholder='Agilidade Base (0-5)',
                id='cmd-bat-agi',
                value=str(dados.get('agilidade', 1))))
            container.mount(Input(
                placeholder='Resistência Base (0-5)',
                id='cmd-bat-res',
                value=str(dados.get('resistencia', 2))))
            container.mount(Input(
                placeholder='Percepção Base (0-5)',
                id='cmd-bat-perc',
                value=str(dados.get('percepcao', 1))))
            container.mount(Input(
                placeholder='Exuberância Base (0-5)',
                id='cmd-bat-exub',
                value=str(dados.get('exuberancia', 0))))
            container.mount(Label('🏆  Recompensa:', classes='campo-rotulo'))
            container.mount(Input(
                placeholder='XP de Recompensa',
                id='cmd-bat-xp',
                value=str(dados.get('xp_recompensa', 10))))
            container.mount(Input(
                placeholder='Emoji Sprite do Inimigo (ex: 👹)',
                id='cmd-bat-emoji',
                value=dados.get('emoji', '👹')))

    def _capturar_valores_campos_atuais(self) -> dict:
        '''Serializa o estado atual do formulário de teleporte para não perder progresso.'''
        return {
            'mapa_teleporte': self.query_one('#cmd-tel-mapa').value,
            'linha_teleporte': self.query_one('#cmd-tel-y').value,
            'coluna_teleporte': self.query_one('#cmd-tel-x').value,
        }

    def  _ao_obter_coordenadas_teleporte(self, dados_coords:dict) -> None:

        self.query_one('#cmd-tel-y').value = str(dados_coords.get("linha", 0))
        self.query_one('#cmd-tel-x').value = str(dados_coords.get("coluna", 0))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-cancel':
            self.dismiss(None)

        # Intercepta botão de seleção de posição XY para teleporte
        if event.button.id == 'btn-select-pos-xy':
            if not self.query_one('#cmd-tel-mapa').value in [Select.BLANK, None, '']:
                
                self.notify('Selecione a posição para teleporte')
                
                dados_requisicao = {
                    'tipo': "teleporte",
                    'acao_especial': 'ativar_capitura_de_posicao',
                    #'estado_formulario_atual': self._capturar_valores_campos_atuais(),
                    'dados': self._capturar_valores_campos_atuais(),
                    'mapa_teleporte': self.query_one('#cmd-tel-mapa').value
                }
                self.app.push_screen(SecondaryMap(dados_requisicao["mapa_teleporte"],
                                                dados_requisicao["acao_especial"]),
                                    lambda dados_coords: self._ao_obter_coordenadas_teleporte(
                                        dados_coords)
                                )
            else:
                self.notify('Primeiro selecione o mapa para o teleporte')
                
            
        elif event.button.id == 'btn-save':
            tipo = self.query_one('#cmd-tipo').value
            if not tipo or tipo == Select.BLANK:
                return

            comando = {'tipo': tipo, 'dados': {}}
            try:
                if tipo == 'mensagem':
                    comando['dados']['texto'] = self.query_one('#cmd-msg-texto').value
                elif tipo == 'notificacao':
                    comando['dados']['texto'] = self.query_one('#cmd-notif-texto').value
                elif tipo == 'teleporte':
                    comando['dados']['mapa_id'] = int(self.query_one('#cmd-tel-mapa').value)
                    comando['dados']['pos_x'] = int(self.query_one('#cmd-tel-x').value)
                    comando['dados']['pos_y'] = int(self.query_one('#cmd-tel-y').value)
                elif tipo == 'mudar_inventario':
                    comando['dados']['item'] = self.query_one('#cmd-inv-item').value
                    comando['dados']['operacao'] = self.query_one('#cmd-inv-op').value
                    comando['dados']['quantidade'] = int(self.query_one('#cmd-inv-qtd').value)
                elif tipo == 'mudar_status_heroi':
                    comando['dados']['parametro'] = self.query_one('#cmd-stat-param').value
                    comando['dados']['operacao'] = self.query_one('#cmd-stat-op').value
                    comando['dados']['valor'] = int(self.query_one('#cmd-stat-valor').value)
                elif tipo == 'bifurcacao_condicional':
                    pergunta = self.query_one('#cmd-bif-pergunta').value
                    op1 = self.query_one('#cmd-bif-op1').value
                    op2 = self.query_one('#cmd-bif-op2').value
                    comando['dados']['pergunta'] = pergunta
                    opcoes = []
                    ramos = {}
                    if op1:
                        opcoes.append(op1)
                        ramos[op1] = []
                    if op2:
                        opcoes.append(op2)
                        ramos[op2] = []
                    comando['dados']['opcoes'] = opcoes
                    comando['dados']['ramos'] = ramos
                elif tipo == 'controle_switch':
                    comando['dados']['nome'] = self.query_one('#cmd-sw-nome').value
                    comando['dados']['valor'] = self.query_one('#cmd-sw-valor').value == 'true'
                elif tipo == 'controle_self_switch':
                    comando['dados']['letra'] = self.query_one('#cmd-ssw-letra').value
                    comando['dados']['valor'] = self.query_one('#cmd-ssw-valor').value == 'true'
                elif tipo == 'controle_variavel':
                    comando['dados']['nome'] = self.query_one('#cmd-variavel-nome').value
                    comando['dados']['operador'] = self.query_one('#cmd-variavel-operador').value
                    comando['dados']['valor'] = self.query_one('#cmd-variavel-valor').value

                elif tipo == 'iniciar_combate':
                    # Captura todos os campos de configuração do inimigo
                    def _safe_int(widget_id: str, default: int) -> int:
                        try:
                            return int(self.query_one(widget_id).value or default)
                        except (ValueError, TypeError):
                            return default

                    comando['dados']['nome'] = self.query_one('#cmd-bat-nome').value or 'Goblin'
                    comando['dados']['nivel'] = _safe_int('#cmd-bat-nivel', 1)
                    comando['dados']['raca'] = self.query_one('#cmd-bat-raca').value
                    comando['dados']['classe'] = self.query_one('#cmd-bat-classe').value
                    comando['dados']['forca'] = _safe_int('#cmd-bat-forca', 2)
                    comando['dados']['agilidade'] = _safe_int('#cmd-bat-agi', 1)
                    comando['dados']['resistencia'] = _safe_int('#cmd-bat-res', 2)
                    comando['dados']['percepcao'] = _safe_int('#cmd-bat-perc', 1)
                    comando['dados']['exuberancia'] = _safe_int('#cmd-bat-exub', 0)
                    comando['dados']['xp_recompensa'] = _safe_int('#cmd-bat-xp', 10)
                    comando['dados']['emoji'] = self.query_one('#cmd-bat-emoji').value or '👹'

            except Exception:
                self.notify('Erro ao salvar comando: Preencha os campos corretamente', severity='error')
                return

            self.dismiss(comando)


# ==============================================================================
# SUB-MODAL: MENU DE AÇÕES DE UM COMANDO
# ==============================================================================
class AcoesComandoScreen(ModalScreen[str]):
    '''Menu contextual ao clicar num comando da lista.'''

    def __init__(self, comando: dict):
        super().__init__()
        self.comando = comando

    def compose(self):
        import unicodedata
        with Vertical(id='acoes-cmd-caixa'):
            yield Label(f'Ações: {self.comando["tipo"]}', classes='titulo-secao')
            yield Button('Editar Comando', id='btn-editar', variant='success')
            if self.comando['tipo'] == 'bifurcacao_condicional':
                for op in self.comando['dados'].get('opcoes', []):
                    id_op = op.replace(" ", "_").replace(
                        ",", "-").replace(".", "").replace('!', '_')
                    id_op = unicodedata.normalize('NFD', id_op)
                    id_op = id_op.encode('ASCII', 'ignore').decode('ASCII')
                    yield Button(f'Editar Ramo: "{op}"', id=f'ramo_{id_op}', variant='primary')
            yield Button('Excluir Comando', id='btn-excluir', variant='error')
            yield Button('Voltar', id='btn-cancelar')

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-cancelar':
            self.dismiss(None)
        elif event.button.id == 'btn-excluir':
            self.dismiss('excluir')
        elif event.button.id == 'btn-editar':
            self.dismiss('editar')
        elif event.button.id.startswith('ramo_'):
            ramo_nome = event.button.id.replace('ramo_', '')
            self.dismiss(f'editar_ramo_{ramo_nome}')


# ==============================================================================
# SUB-MODAL: EDITOR DE RAMO (recursivo)
# ==============================================================================
class RamoEditorScreen(ModalScreen[list]):
    '''Tela recursiva para editar os comandos dentro de um ramo (ex: resposta Sim ou Não).'''

    def __init__(self, nome_ramo: str, comandos: list):
        super().__init__()
        self.nome_ramo = nome_ramo
        self.comandos = copy.deepcopy(comandos)

    def compose(self):
        with Vertical(id='evt-caixa-full'):
            yield Label(f'🌿 Ramo de Escolha: "{self.nome_ramo}"', classes='titulo-secao')
            yield ListView(id='lista-comandos-ramo')
            with Horizontal(id='evt-botoes'):
                yield Button('+ Adicionar Comando', id='btn-add-cmd', variant='primary')
                yield Button('Concluir Ramo', id='btn-salvar-ramo', variant='success')

    def on_mount(self):
        self.atualizar_lista()

    def atualizar_lista(self):
        lista = self.query_one('#lista-comandos-ramo', ListView)
        lista.clear()
        for i, cmd in enumerate(self.comandos):
            dados_str = json.dumps(cmd["dados"], ensure_ascii=False, indent=2)
            texto = f'[{i}] {cmd["tipo"]}\n{dados_str}'
            lista.append(ListItem(Label(texto), name=str(i)))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == 'btn-add-cmd':
            self.app.push_screen(AdicionarComandoScreen(), self.ao_adicionar_comando)
        elif event.button.id == 'btn-salvar-ramo':
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
        if acao == 'excluir':
            self.comandos.pop(idx)
            self.atualizar_lista()
        elif acao == 'editar':
            cmd = self.comandos[idx]
            self.app.push_screen(
                AdicionarComandoScreen(cmd),
                lambda novo_cmd: self.ao_salvar_edicao_comando(novo_cmd, idx))
        elif acao.startswith('editar_ramo_'):
            ramo_nome = acao.replace('editar_ramo_', '')
            cmd = self.comandos[idx]
            ramos = cmd['dados'].setdefault('ramos', {})
            ramo_cmds = ramos.setdefault(ramo_nome, [])
            # RECURSÃO: Chama outro RamoEditorScreen por cima deste!
            self.app.push_screen(
                RamoEditorScreen(ramo_nome, ramo_cmds),
                lambda novos_cmds: self.ao_salvar_subramo(novos_cmds, idx, ramo_nome))

    def ao_salvar_edicao_comando(self, novo_comando, idx):
        if novo_comando:
            if novo_comando['tipo'] == self.comandos[idx]['tipo']:
                if 'ramos' in self.comandos[idx]['dados']:
                    novo_comando['dados']['ramos'] = self.comandos[idx]['dados']['ramos']
            self.comandos[idx] = novo_comando
            self.atualizar_lista()

    def ao_salvar_subramo(self, novos_cmds, idx, ramo_nome):
        if novos_cmds is not None:
            self.comandos[idx]['dados']['ramos'][ramo_nome] = novos_cmds
            self.atualizar_lista()




class SecondaryMap(ModalScreen):
    """Um mostrador de mapa para coisas como pegar coordenada. """

    #CSS_PATH = CSS_PATH

    def __init__(self, id_do_mapa_secundario: int, contexto_do_modo_de_captura_ativo: Modo_de_Captura):
        self.matriz_do_mapa_secundario: list | None = None
        self.objetos_do_mapa_secundario: dict = {}
        self.id_do_mapa_secundario: int  = id_do_mapa_secundario
        self.contexto_do_modo_de_captura_ativo: Modo_de_Captura = None

        super().__init__()

    def compose(self):
        with Container(id='sec-map-area'):
            yield MapaInterativo('Matriz do Mapa aparecerá aqui...', id='sec-mapa-view', )

    def on_mount(self):
        '''Executa automaticamente quando o Gerenciador de Mapas abre.'''
        logging.info(f'Montagem do mapa secundário...')
        self.carregar_mapa_secundario()
        self.exibir_mapa_sec_na_tela()
        
    # CARREGAMENTO DO MAPA SECUNDÁRIO

    def carregar_mapa_secundario(self):
        from app.db.database import SessionLocal

        with SessionLocal() as db:
            # 1. Carrega o Mapa Base
            mapa_sec_db_carregado = db.query(MapaDB).filter(
                MapaDB.id == self.id_do_mapa_secundario).first()

            if not mapa_sec_db_carregado:
                logging.info(f'Não carregou mapa...')
                return

            self.matriz_do_mapa_secundario = mapa_sec_db_carregado.mapa_em_si

            objetos_salvos = mapa_sec_db_carregado.objetos if mapa_sec_db_carregado.objetos else {}
            self.objetos_do_mapa_secundario = self._desempacotar_objetos_do_banco(
                objetos_salvos)
            
            logging.info(f'Carregou> obj: {objetos_salvos}')


    # =========================================================================
    # CAPTURADOR DE COORDENADAS DO MAPA SECUNDÁRIO
    # =========================================================================
    @on(MapaInterativo.Pintar)
    def processar_pintura(self, event: MapaInterativo.Pintar):
        if self.matriz_do_mapa_secundario is None:
            logging.info(f'Mapa sem matriz...')
            return
        linha, coluna = event.linha, event.coluna

        if 0 <= linha < len(self.matriz_do_mapa_secundario) and 0 <= coluna < len(self.matriz_do_mapa_secundario[0]):
            logging.info(
                f'Modo de captura do mapa secundário: coords: (x={coluna}, y={linha})')

            if event.inicio_de_traco:
                self.query_one('#sec-mapa-view',
                               MapaInterativo).mouse_pressionado = False
                self.modo_captura_coordenada = False
                self.ferramenta_atual = 'lapis'
                try:
                    coordenadas_coletadas = {"linha": linha, "coluna": coluna}
                    self.dismiss(coordenadas_coletadas)
                except Exception as e:
                    logging.info(
                        f'Erro mapa-secundario ao coletar coordenadas: {coordenadas_coletadas}')
                    raise ValueError(
                        f'Erro mapa-secundario ao coletar coordenadas: {coordenadas_coletadas}')

            return

    # =========================================================================
    # MONTADOR DA TELA DO MAPA SECUNDÁRIO
    # =========================================================================
    def exibir_mapa_sec_na_tela(self):
        '''Monta o mapa base e sobrepõe os objetos aplicando transparência (cor de fundo).'''
        if self.matriz_do_mapa_secundario is None:
            logging.info(f'Mapa sem matriz...')
            return

        texto_mapa = Text(no_wrap=True)
        logging.info(f'Exibir mapa secundário...')
        
        for linha_idx in range(len(self.matriz_do_mapa_secundario)):
            for col_idx in range(len(self.matriz_do_mapa_secundario[0])):
                tile_chao = self.matriz_do_mapa_secundario[linha_idx][col_idx]
                tile_objeto = self.objetos_do_mapa_secundario.get(
                    (linha_idx, col_idx))

                if tile_objeto is not None:
                    cor_bg = CatalogoTiles.obter_cor_fundo(tile_chao)
                    texto_mapa.append(
                        tile_objeto, style=f'on {cor_bg}' if cor_bg else '')
                else:
                    texto_mapa.append(tile_chao)
            texto_mapa.append('\n')

        self.query_one('#sec-mapa-view', MapaInterativo).update(texto_mapa)


    def _desempacotar_objetos_do_banco(self, objetos_json: dict) -> dict:
        '''Transforma o texto "1,2" do Banco de volta em tupla matemática (1, 2).'''
        objetos_na_memoria = {}
        if not objetos_json:
            return objetos_na_memoria  # Retorna vazio se não houver objetos

        try:
            for chave_texto, emoji in objetos_json.items():
                partes = chave_texto.split(',')
                linha = int(partes[0])
                coluna = int(partes[1])
                objetos_na_memoria[(linha, coluna)] = emoji
        except Exception as e:
            logging.info(f'Erro ao _desempacotar_objetos_do_banco: {e}')
            raise ValueError(f'Erro ao _desempacotar_objetos_do_banco: {e}')
        return objetos_na_memoria
    
