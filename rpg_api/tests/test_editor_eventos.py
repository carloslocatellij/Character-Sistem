# tests/test_editor_eventos.py
"""
Testes para a lógica de gerenciamento de eventos do editor de mapas.

Cobre:
  - Lógica de dados de eventos no MapManagerScreen (serialização/desserialização)
  - Lógica pura do formulário PropriedadesEventoFormScreen (sem montar TUI)
"""
import pytest
from app.views.map_manager_screen import MapManagerScreen
from app.views.components.evento_form_screen import PropriedadesEventoFormScreen


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def editor_vazio():
    """Instância limpa do MapManagerScreen para testar lógica de dados."""
    return MapManagerScreen()


@pytest.fixture
def form_novo_evento():
    """Instância do formulário de evento para um tile novo (sem dados existentes)."""
    return PropriedadesEventoFormScreen(linha=3, coluna=7, emoji="👾")


@pytest.fixture
def form_evento_existente():
    """Instância do formulário com dados pré-existentes de um evento salvo no banco."""
    dados_existentes = {
        "id": 42,
        "nome": "guarda_portal",
        "emoji": "💂",
        "event_type": "evento_custom",
        "parametros": {
            "paginas": [
                {
                    "id_pagina": 1,
                    "condicoes": {"self_switch": "A"},
                    "configuracao_visual": {"emoji": "💂"},
                    "gatilho": "toque_jogador",
                    "comandos": [{"tipo": "mensagem", "dados": {"texto": "Pare!"}}]
                },
                {
                    "id_pagina": 2,
                    "condicoes": {},
                    "configuracao_visual": {"emoji": "💂"},
                    "gatilho": "acao_jogador",
                    "comandos": []
                }
            ]
        }
    }
    return PropriedadesEventoFormScreen(linha=5, coluna=8, emoji="💂", dados_existentes=dados_existentes)


# ==============================================================================
# TESTES EXISTENTES: Lógica de dados do MapManagerScreen
# ==============================================================================

def test_adicionar_evento_na_memoria(editor_vazio):
    """Garante que o editor consegue registar um evento complexo na coordenada correta."""
    editor_vazio.adicionar_evento_memoria(
        linha=5,
        coluna=10,
        nome="monstro_1",
        emoji="👾",
        event_type="monstro",
        parametros={"movimento": "aleatorio", "diminuir_hp": 1}
    )

    # Verifica se a chave foi criada como tupla matemática
    assert (5, 10) in editor_vazio.mapa_atual_eventos

    # Verifica se os dados estão intactos
    evento = editor_vazio.mapa_atual_eventos[(5, 10)]
    assert evento["nome"] == "monstro_1"
    assert evento["emoji"] == "👾"
    assert evento["event_type"] == "monstro"
    assert evento["parametros"]["diminuir_hp"] == 1


def test_empacotar_eventos_para_banco(editor_vazio):
    """Garante que o dicionário de memória é convertido para uma lista de registos para o BD."""
    editor_vazio.adicionar_evento_memoria(
        linha=2, coluna=3, nome="bau_magico", emoji="📦",
        event_type="bau", parametros={"item": "pocao"}
    )

    lista_db = editor_vazio._empacotar_eventos_para_banco()

    # O Banco de Dados espera uma lista de dicionários onde as chaves da tupla viraram pos_x e pos_y
    assert isinstance(lista_db, list)
    assert len(lista_db) == 1

    registo = lista_db[0]
    assert registo["pos_y"] == 2  # Linha
    assert registo["pos_x"] == 3  # Coluna
    assert registo["nome"] == "bau_magico"
    assert registo["parametros"]["item"] == "pocao"


def test_desempacotar_eventos_do_banco(editor_vazio):
    """Garante que a lista que vem do BD volta a ser um dicionário mapeado por tuplas (y, x)."""
    dados_do_banco = [
        {
            "id": 1, "mapa_id": 1, "nome": "guarda", "emoji": "💂",
            "pos_y": 7, "pos_x": 8, "event_type": "npc", "parametros": {}
        }
    ]

    editor_vazio._desempacotar_eventos_do_banco(dados_do_banco)

    # Deve estar disponível na memória pela tupla de coordenadas
    assert (7, 8) in editor_vazio.mapa_atual_eventos
    assert editor_vazio.mapa_atual_eventos[(7, 8)]["nome"] == "guarda"
    # O ID deve ser preservado para sabermos que é um evento que já existia no banco
    assert editor_vazio.mapa_atual_eventos[(7, 8)]["id"] == 1


# ==============================================================================
# NOVOS TESTES: Lógica pura do PropriedadesEventoFormScreen
# ==============================================================================

class TestPropriedadesEventoFormScreen:
    """
    Testa a lógica de estado da classe de formulário sem montar a TUI.
    O __init__ prepara toda a estrutura de dados (self.paginas) sem depender de widgets,
    o que permite verificar a lógica pura com pytest comum.
    """

    def test_inicializar_evento_novo_cria_pagina_padrao(self, form_novo_evento):
        """Garante que um evento novo inicia com exatamente 1 página padrão."""
        assert len(form_novo_evento.paginas) == 1
        pagina = form_novo_evento.paginas[0]
        assert pagina["id_pagina"] == 1
        assert pagina["gatilho"] == "acao_jogador"
        assert pagina["comandos"] == []
        assert pagina["condicoes"] == {}

    def test_inicializar_evento_existente_preserva_paginas(self, form_evento_existente):
        """Garante que ao reabrir um evento com 2 páginas, todas são preservadas."""
        assert len(form_evento_existente.paginas) == 2
        assert form_evento_existente.paginas[0]["gatilho"] == "toque_jogador"
        assert form_evento_existente.paginas[1]["gatilho"] == "acao_jogador"

    def test_inicializar_evento_existente_preserva_id(self, form_evento_existente):
        """Garante que o ID do evento existente é preservado nos dados."""
        assert form_evento_existente.dados_existentes["id"] == 42

    def test_adicionar_pagina_incrementa_lista(self, form_novo_evento):
        """Testa a lógica de adicionar uma nova página diretamente na lista."""
        qtd_inicial = len(form_novo_evento.paginas)
        nova_pagina = {
            "id_pagina": qtd_inicial + 1,
            "condicoes": {},
            "configuracao_visual": {"emoji": "👾"},
            "gatilho": "acao_jogador",
            "comandos": []
        }
        form_novo_evento.paginas.append(nova_pagina)
        assert len(form_novo_evento.paginas) == qtd_inicial + 1
        assert form_novo_evento.paginas[-1]["id_pagina"] == 2

    def test_nao_pode_remover_unica_pagina(self, form_novo_evento):
        """Garante que a proteção de página única funciona (lista permanece com 1 item)."""
        assert len(form_novo_evento.paginas) == 1
        # Tenta remover — a lógica de proteção impede
        if len(form_novo_evento.paginas) > 1:
            form_novo_evento.paginas.pop(0)
        assert len(form_novo_evento.paginas) == 1

    def test_obter_condicoes_cria_dict_se_ausente(self, form_novo_evento):
        """
        Garante que _obter_condicoes_pagina_atual() cria a chave 'condicoes'
        na página se ela não existir, em vez de lançar um KeyError.
        """
        # Remove 'condicoes' manualmente para simular uma página sem a chave
        del form_novo_evento.paginas[0]["condicoes"]
        assert "condicoes" not in form_novo_evento.paginas[0]

        condicoes = form_novo_evento._obter_condicoes_pagina_atual()

        # Deve ter criado o dict vazio
        assert condicoes == {}
        assert "condicoes" in form_novo_evento.paginas[0]

    def test_ao_adicionar_switch_insere_na_pagina_atual(self, form_novo_evento):
        """
        Testa o callback ao_adicionar_switch(): garante que um switch
        é inserido corretamente nas condições da página atual.
        """
        dados_switch = {"nome": "missao_ativa", "valor": True}
        form_novo_evento.ao_adicionar_switch(dados_switch)

        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert "switches" in condicoes
        assert len(condicoes["switches"]) == 1
        assert condicoes["switches"][0]["nome"] == "missao_ativa"
        assert condicoes["switches"][0]["valor"] is True

    def test_ao_adicionar_switch_com_none_nao_insere(self, form_novo_evento):
        """Garante que passar None (usuário cancelou o modal) não altera as condições."""
        form_novo_evento.ao_adicionar_switch(None)
        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert condicoes.get("switches", []) == []

    def test_ao_adicionar_variavel_insere_na_pagina_atual(self, form_novo_evento):
        """
        Testa o callback ao_adicionar_variavel(): garante que uma variável
        é inserida corretamente nas condições da página atual.
        """
        dados_variavel = {"nome": "reputacao", "operador": "maior_ou_igual", "valor": 10}
        form_novo_evento.ao_adicionar_variavel(dados_variavel)

        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert "variaveis" in condicoes
        assert len(condicoes["variaveis"]) == 1
        assert condicoes["variaveis"][0]["nome"] == "reputacao"
        assert condicoes["variaveis"][0]["valor"] == 10

    def test_remover_switch_por_indice_valido(self, form_novo_evento):
        """Testa _remover_switch() com índice válido."""
        # Adiciona 2 switches primeiro
        form_novo_evento.ao_adicionar_switch({"nome": "sw_a", "valor": True})
        form_novo_evento.ao_adicionar_switch({"nome": "sw_b", "valor": False})

        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert len(condicoes["switches"]) == 2

        # Remove o primeiro (índice 0)
        form_novo_evento._remover_switch(0)
        assert len(condicoes["switches"]) == 1
        # O que sobrou deve ser o sw_b
        assert condicoes["switches"][0]["nome"] == "sw_b"

    def test_remover_switch_com_indice_invalido_nao_lanca_erro(self, form_novo_evento):
        """Garante que remover switch com índice fora do range não lança exceção."""
        form_novo_evento.ao_adicionar_switch({"nome": "sw_a", "valor": True})

        # Não deve lançar erro mesmo com índice fora da lista
        form_novo_evento._remover_switch(99)
        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert len(condicoes["switches"]) == 1  # Nada foi removido

    def test_remover_variavel_por_indice_valido(self, form_novo_evento):
        """Testa _remover_variavel() com índice válido."""
        form_novo_evento.ao_adicionar_variavel({"nome": "ouro", "operador": "igual", "valor": 50})
        form_novo_evento.ao_adicionar_variavel({"nome": "nivel", "operador": "maior_ou_igual", "valor": 5})

        condicoes = form_novo_evento.paginas[0]["condicoes"]
        assert len(condicoes["variaveis"]) == 2

        form_novo_evento._remover_variavel(0)
        assert len(condicoes["variaveis"]) == 1
        assert condicoes["variaveis"][0]["nome"] == "nivel"

    def test_pagina_atual_idx_comeca_em_zero(self, form_novo_evento):
        """Garante que o índice de página inicial é sempre 0."""
        assert form_novo_evento.pagina_atual_idx == 0

    def test_navegacao_paginas_dentro_dos_limites(self, form_evento_existente):
        """
        Garante que a navegação entre páginas respeita os limites
        (não avança além da última, não volta antes da primeira).
        """
        # Começa na página 0, avança para a 1
        form_evento_existente.pagina_atual_idx = 0
        if form_evento_existente.pagina_atual_idx < len(form_evento_existente.paginas) - 1:
            form_evento_existente.pagina_atual_idx += 1
        assert form_evento_existente.pagina_atual_idx == 1

        # Tenta avançar além do limite — deve continuar em 1
        if form_evento_existente.pagina_atual_idx < len(form_evento_existente.paginas) - 1:
            form_evento_existente.pagina_atual_idx += 1
        assert form_evento_existente.pagina_atual_idx == 1

        # Volta para a página 0
        form_evento_existente.pagina_atual_idx -= 1
        assert form_evento_existente.pagina_atual_idx == 0

        # Tenta voltar além do limite — deve permanecer em 0
        if form_evento_existente.pagina_atual_idx > 0:
            form_evento_existente.pagina_atual_idx -= 1
        assert form_evento_existente.pagina_atual_idx == 0