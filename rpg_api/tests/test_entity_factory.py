# rpg_api/tests/test_entity_factory.py
"""
Suíte de testes da EntityFactory e funções auxiliares.

Cobre:
  - mapear_tipo_entidade(): mapeamento de strings do banco para TipoEntidade
  - obter_pagina_ativa(): varredura decrescente de páginas (Regra 6)
  - criar_entidade_evento(): construção correta de componentes por tipo
  - criar_entidade_jogador_de_save(): hidratação do Player via dados do SaveDB
  - criar_entidade_jogador_novo(): hidratação do Player via objeto de domínio
  - Garantia de que MovimentComponent só é adicionado quando a página ativa define "movimento"
  - Garantia de que StatsComponent só é adicionado para Monstro e Pacifico
"""

import pytest
import esper

from app.core.engine.entity_factory import (
    EntityFactory,
    TipoEntidade,
    mapear_tipo_entidade,
    obter_pagina_ativa,
)
from app.core.engine.components import (
    CollisionComponent,
    InteractableComponent,
    MovimentComponent,
    PositionComponent,
    RenderComponent,
    StatsComponent,
    InventoryComponent,
    EquipmentComponent,
)


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture(autouse=True)
def limpar_mundo_esper():
    """Garante isolamento total entre testes: reinicia o esper antes de cada um."""
    esper.clear_database()
    yield
    esper.clear_database()


def _criar_entidade_vazia() -> int:
    """Cria uma entidade em branco no esper e retorna seu ID."""
    return esper.create_entity()


# ==============================================================================
# TESTES: mapear_tipo_entidade
# ==============================================================================

class TestMapearTipoEntidade:
    """Verifica que strings do banco de dados são mapeadas corretamente."""

    def test_monstro_retorna_tipo_monstro(self):
        assert mapear_tipo_entidade("monstro") == TipoEntidade.MONSTRO

    def test_npc_retorna_tipo_npc(self):
        assert mapear_tipo_entidade("npc") == TipoEntidade.NPC

    def test_npc_dialogo_retorna_tipo_npc(self):
        assert mapear_tipo_entidade("npc_dialogo") == TipoEntidade.NPC

    def test_npc_loja_retorna_tipo_npc(self):
        assert mapear_tipo_entidade("npc_loja") == TipoEntidade.NPC

    def test_pacifico_retorna_tipo_pacifico(self):
        assert mapear_tipo_entidade("pacifico") == TipoEntidade.PACIFICO

    def test_bau_retorna_tipo_item(self):
        assert mapear_tipo_entidade("bau") == TipoEntidade.ITEM

    def test_item_retorna_tipo_item(self):
        assert mapear_tipo_entidade("item") == TipoEntidade.ITEM

    def test_colecionavel_retorna_tipo_item(self):
        assert mapear_tipo_entidade("colecionavel") == TipoEntidade.ITEM

    def test_porta_retorna_tipo_interativo(self):
        assert mapear_tipo_entidade("porta") == TipoEntidade.INTERATIVO

    def test_alavanca_retorna_tipo_interativo(self):
        assert mapear_tipo_entidade("alavanca") == TipoEntidade.INTERATIVO

    def test_armadilha_retorna_tipo_interativo(self):
        assert mapear_tipo_entidade("armadilha") == TipoEntidade.INTERATIVO

    def test_evento_custom_retorna_tipo_interativo(self):
        assert mapear_tipo_entidade("evento_custom") == TipoEntidade.INTERATIVO

    def test_veiculo_retorna_tipo_veiculo(self):
        assert mapear_tipo_entidade("veiculo") == TipoEntidade.VEICULO

    def test_cenario_retorna_tipo_cenario(self):
        assert mapear_tipo_entidade("cenario") == TipoEntidade.CENARIO

    def test_string_desconhecida_faz_fallback_para_interativo(self):
        assert mapear_tipo_entidade("xyz_desconhecido") == TipoEntidade.INTERATIVO

    def test_string_com_espacos_e_maiusculas_e_normalizada(self):
        """Garante que strings com espaços ou maiúsculas são toleradas."""
        assert mapear_tipo_entidade("  MONSTRO  ".strip().lower()) == TipoEntidade.MONSTRO


# ==============================================================================
# TESTES: obter_pagina_ativa
# ==============================================================================

class TestObterPaginaAtiva:
    """Verifica a varredura decrescente de páginas (Regra 6)."""

    def test_lista_vazia_retorna_none(self):
        assert obter_pagina_ativa([]) is None

    def test_none_retorna_none(self):
        assert obter_pagina_ativa(None) is None

    def test_lista_com_uma_pagina_retorna_essa_pagina(self):
        pagina_unica = {"gatilho": "acao_jogador", "comandos": ["dialogo"]}
        resultado = obter_pagina_ativa([pagina_unica])
        assert resultado == pagina_unica

    def test_lista_com_multiplas_paginas_retorna_a_ultima(self):
        """Por varredura decrescente, sem switches, a última página é sempre retornada."""
        pagina_inicial = {"gatilho": "acao_jogador", "comandos": ["dialogo_basico"]}
        pagina_avancada = {"gatilho": "acao_jogador", "comandos": ["dialogo_avancado"]}
        resultado = obter_pagina_ativa([pagina_inicial, pagina_avancada])
        assert resultado == pagina_avancada

    def test_lista_com_tres_paginas_retorna_a_ultima(self):
        paginas = [
            {"gatilho": "acao_jogador", "id": 1},
            {"gatilho": "acao_jogador", "id": 2},
            {"gatilho": "acao_jogador", "id": 3},
        ]
        resultado = obter_pagina_ativa(paginas)
        assert resultado["id"] == 3

    def test_pagina_com_dicionario_invalido_e_ignorada(self):
        """Entradas que não são dict devem ser ignoradas na varredura."""
        paginas = ["string_invalida", {"gatilho": "valido"}]
        resultado = obter_pagina_ativa(paginas)
        assert resultado == {"gatilho": "valido"}


# ==============================================================================
# TESTES: criar_entidade_evento — componentes base
# ==============================================================================

class TestCriarEntidadeEventoBase:
    """Verifica que toda entidade de evento recebe os componentes base."""

    def test_entidade_interativo_recebe_componentes_base(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="porta",
            nome="Porta Secreta",
            emoji="🚪",
            pos_x=3,
            pos_y=5,
            parametros_base={},
        )

        assert esper.has_component(entidade_id, PositionComponent)
        assert esper.has_component(entidade_id, RenderComponent)
        assert esper.has_component(entidade_id, CollisionComponent)
        assert esper.has_component(entidade_id, InteractableComponent)

    def test_posicao_correta_e_aplicada(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="porta",
            nome="Porta",
            emoji="🚪",
            pos_x=7,
            pos_y=2,
            parametros_base={},
        )

        posicao = esper.component_for_entity(entidade_id, PositionComponent)
        assert posicao.x == 7
        assert posicao.y == 2

    def test_emoji_correto_no_render_component(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="cenario",
            nome="Árvore",
            emoji="🌲",
            pos_x=0,
            pos_y=0,
            parametros_base={},
        )

        render = esper.component_for_entity(entidade_id, RenderComponent)
        assert render.emoji == "🌲"


# ==============================================================================
# TESTES: criar_entidade_evento — tipo MONSTRO
# ==============================================================================

class TestCriarEntidadeMonstro:
    """Verifica que Monstros recebem StatsComponent e MovimentComponent condicionalmente."""

    def test_monstro_sem_paginas_nao_recebe_moviment_component(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="monstro",
            nome="Goblin",
            emoji="👹",
            pos_x=1,
            pos_y=1,
            parametros_base={"paginas": []},
        )

        assert esper.has_component(entidade_id, StatsComponent)
        assert not esper.has_component(entidade_id, MovimentComponent)

    def test_monstro_com_pagina_sem_movimento_nao_recebe_moviment_component(self):
        entidade_id = _criar_entidade_vazia()
        params = {"paginas": [{"gatilho": "toque_jogador", "comandos": ["ataque"]}]}
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="monstro",
            nome="Orc",
            emoji="🧌",
            pos_x=2,
            pos_y=2,
            parametros_base=params,
        )

        assert esper.has_component(entidade_id, StatsComponent)
        assert not esper.has_component(entidade_id, MovimentComponent)

    def test_monstro_com_movimento_na_pagina_ativa_recebe_moviment_component(self):
        entidade_id = _criar_entidade_vazia()
        params = {
            "paginas": [
                {"gatilho": "acao_jogador", "movimento": {"tipo": "aleatorio", "roteiro": [], "ciclos": 0}}
            ]
        }
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="monstro",
            nome="Lobo",
            emoji="🐺",
            pos_x=3,
            pos_y=3,
            parametros_base=params,
        )

        assert esper.has_component(entidade_id, StatsComponent)
        assert esper.has_component(entidade_id, MovimentComponent)

    def test_monstro_usa_valor_dano_do_parametro(self):
        entidade_id = _criar_entidade_vazia()
        params = {"ação": {"mudar_hp": {"valor": 15}}, "paginas": []}
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="monstro",
            nome="Dragão",
            emoji="🐉",
            pos_x=0,
            pos_y=0,
            parametros_base=params,
        )

        stats = esper.component_for_entity(entidade_id, StatsComponent)
        assert stats.ataque_base == 15

    def test_paginas_vazias_nao_causa_index_error(self):
        """Verifica que a correção do bug IndexError está funcionando."""
        entidade_id = _criar_entidade_vazia()
        # Este cenário causava IndexError no código antigo: paginas[0] com lista vazia
        params = {"paginas": []}
        try:
            EntityFactory.criar_entidade_evento(
                entity_id=entidade_id,
                event_type="monstro",
                nome="Esqueleto",
                emoji="💀",
                pos_x=0,
                pos_y=0,
                parametros_base=params,
            )
        except IndexError:
            pytest.fail("criar_entidade_evento lançou IndexError com paginas=[]!")


# ==============================================================================
# TESTES: criar_entidade_evento — tipo NPC
# ==============================================================================

class TestCriarEntidadeNpc:
    """Verifica que NPCs não recebem StatsComponent de combate."""

    def test_npc_sem_paginas_nao_recebe_stats_nem_movimento(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="npc",
            nome="Vendedor",
            emoji="🧓",
            pos_x=4,
            pos_y=4,
            parametros_base={"paginas": []},
        )

        assert not esper.has_component(entidade_id, StatsComponent)
        assert not esper.has_component(entidade_id, MovimentComponent)

    def test_npc_com_movimento_na_pagina_recebe_moviment_component(self):
        entidade_id = _criar_entidade_vazia()
        params = {
            "paginas": [{"gatilho": "processo_paralelo", "movimento": {"tipo": "patrulha", "roteiro": ["esquerda", "direita"], "ciclos": 2}}]
        }
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="npc_dialogo",
            nome="Guarda",
            emoji="💂",
            pos_x=5,
            pos_y=5,
            parametros_base=params,
        )

        assert not esper.has_component(entidade_id, StatsComponent)
        assert esper.has_component(entidade_id, MovimentComponent)


# ==============================================================================
# TESTES: criar_entidade_evento — tipo ITEM
# ==============================================================================

class TestCriarEntidadeItem:
    """Verifica que Itens são atravessáveis (CollisionComponent.solido=False)."""

    def test_item_tem_collision_solido_false(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="bau",
            nome="Baú do Tesouro",
            emoji="📦",
            pos_x=6,
            pos_y=6,
            parametros_base={},
        )

        colisao = esper.component_for_entity(entidade_id, CollisionComponent)
        assert colisao.solido is False

    def test_item_nao_recebe_stats_nem_movimento(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="colecionavel",
            nome="Moeda de Ouro",
            emoji="🪙",
            pos_x=7,
            pos_y=7,
            parametros_base={},
        )

        assert not esper.has_component(entidade_id, StatsComponent)
        assert not esper.has_component(entidade_id, MovimentComponent)


# ==============================================================================
# TESTES: criar_entidade_evento — tipo INTERATIVO
# ==============================================================================

class TestCriarEntidadeInterativo:
    """Verifica que Interativos são sólidos e não têm stats de combate."""

    def test_interativo_tem_collision_solido_true(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="porta",
            nome="Portão da Fortaleza",
            emoji="🚪",
            pos_x=8,
            pos_y=8,
            parametros_base={},
        )

        colisao = esper.component_for_entity(entidade_id, CollisionComponent)
        assert colisao.solido is True
        assert not esper.has_component(entidade_id, StatsComponent)
        assert not esper.has_component(entidade_id, MovimentComponent)


# ==============================================================================
# TESTES: criar_entidade_evento — tipo CENARIO
# ==============================================================================

class TestCriarEntidadeCenario:
    """Verifica que Cenários respeitam o parâmetro "solido"."""

    def test_cenario_sem_parametro_solido_e_atravessavel(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="cenario",
            nome="Arbusto",
            emoji="🌿",
            pos_x=9,
            pos_y=9,
            parametros_base={},
        )

        colisao = esper.component_for_entity(entidade_id, CollisionComponent)
        assert colisao.solido is False

    def test_cenario_com_parametro_solido_true_e_bloqueante(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="cenario",
            nome="Coluna de Pedra",
            emoji="🪨",
            pos_x=10,
            pos_y=10,
            parametros_base={"solido": True},
        )

        colisao = esper.component_for_entity(entidade_id, CollisionComponent)
        assert colisao.solido is True


# ==============================================================================
# TESTES: criar_entidade_evento — tipo PACIFICO
# ==============================================================================

class TestCriarEntidadePacifico:
    """Verifica que Pacíficos têm HP mas ataque_base=0."""

    def test_pacifico_tem_stats_com_ataque_zero(self):
        entidade_id = _criar_entidade_vazia()
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="pacifico",
            nome="Ovelhinha",
            emoji="🐑",
            pos_x=1,
            pos_y=2,
            parametros_base={"paginas": []},
        )

        assert esper.has_component(entidade_id, StatsComponent)
        stats = esper.component_for_entity(entidade_id, StatsComponent)
        assert stats.ataque_base == 0

    def test_pacifico_com_movimento_recebe_moviment_component(self):
        entidade_id = _criar_entidade_vazia()
        params = {
            "paginas": [{"gatilho": "processo_paralelo", "movimento": {"tipo": "aleatorio", "roteiro": [], "ciclos": 0}}]
        }
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="pacifico",
            nome="Cervo",
            emoji="🦌",
            pos_x=3,
            pos_y=4,
            parametros_base=params,
        )

        assert esper.has_component(entidade_id, MovimentComponent)


# ==============================================================================
# TESTES: criar_entidade_evento — dados salvos no SaveDB
# ==============================================================================

class TestCriarEntidadeComDadosSalvos:
    """Verifica que dados persistidos no SaveDB sobrescrevem posição padrão."""

    def test_posicao_salva_e_restaurada_corretamente(self):
        entidade_id = _criar_entidade_vazia()
        dados_salvos = {
            "components": {
                "PositionComponent": {"x": 15, "y": 20},
            }
        }
        EntityFactory.criar_entidade_evento(
            entity_id=entidade_id,
            event_type="monstro",
            nome="Goblin Errante",
            emoji="👹",
            pos_x=1,   # posição inicial do banco — deve ser sobrescrita
            pos_y=1,
            parametros_base={"paginas": []},
            dados_salvos=dados_salvos,
        )

        posicao = esper.component_for_entity(entidade_id, PositionComponent)
        assert posicao.x == 15
        assert posicao.y == 20


# ==============================================================================
# TESTES: criar_entidade_jogador_de_save
# ==============================================================================

class TestCriarEntidadeJogadorDeSave:
    """Verifica hidratação completa do Player a partir de dados do SaveDB."""

    def test_jogador_recebe_todos_os_componentes_de_save(self):
        esper.create_entity()  # Cria slot ID=1
        EntityFactory.criar_entidade_jogador_de_save(
            entity_id=1,
            pos_x=5,
            pos_y=10,
            direcao_olhar="cima",
            emoji="🧙",
            stats_dict={"nome": "Herói", "classe": "mago", "hp": 40, "max_hp": 50,
                        "mp": 8, "max_mp": 10, "ataque_base": 12, "defesa_base": 4},
            inv_dict={"itens": {}},
            eqp_dict={"arma": None, "armadura": None},
        )

        assert esper.has_component(1, PositionComponent)
        assert esper.has_component(1, RenderComponent)
        assert esper.has_component(1, CollisionComponent)
        assert esper.has_component(1, InventoryComponent)
        assert esper.has_component(1, EquipmentComponent)
        assert esper.has_component(1, StatsComponent)

    def test_jogador_tem_posicao_correta(self):
        esper.create_entity()  # Cria slot ID=1
        EntityFactory.criar_entidade_jogador_de_save(
            entity_id=1,
            pos_x=7,
            pos_y=3,
            direcao_olhar="direita",
            emoji="🧙",
            stats_dict={},
            inv_dict={"itens": {}},
            eqp_dict={"arma": None, "armadura": None},
        )

        posicao = esper.component_for_entity(1, PositionComponent)
        assert posicao.x == 7
        assert posicao.y == 3
        assert posicao.direcao_olhar == "direita"

    def test_jogador_tem_stats_corretos_do_save(self):
        esper.create_entity()  # Cria slot ID=1
        stats_entrada = {
            "nome": "Aldemar",
            "classe": "guerreiro",
            "hp": 35,
            "max_hp": 60,
            "mp": 5,
            "max_mp": 20,
            "ataque_base": 18,
            "defesa_base": 8,
        }
        EntityFactory.criar_entidade_jogador_de_save(
            entity_id=1,
            pos_x=0,
            pos_y=0,
            direcao_olhar="baixo",
            emoji="⚔️",
            stats_dict=stats_entrada,
            inv_dict={"itens": {}},
            eqp_dict={"arma": None, "armadura": None},
        )

        stats = esper.component_for_entity(1, StatsComponent)
        assert stats.nome == "Aldemar"
        assert stats.hp == 35
        assert stats.max_hp == 60
        assert stats.ataque_base == 18
