"""
Testes do Sistema de Combate por Turnos — BattleSystem

Testa o motor de combate de forma HEADLESS (sem UI Textual), validando:
- Configuração de combatentes com deepcopy (Regra 5)
- Cálculo de iniciativa (1d6 + Agilidade)
- Resolução de ações (ataque, magia, cura)
- Encerramento do combate (vitória/derrota)
- Emissão de eventos via Esper event bus
- IA do inimigo (decidir_acao)
- Combate com múltiplos inimigos (1-4)
- Componentes CombatStateComponent e BattleParticipantComponent

Conforme Regra 7 (TDD): rolagens aleatórias usam monkeypatch para resultados determinísticos.
"""
import pytest
import esper
import random
from copy import deepcopy
from unittest.mock import MagicMock, patch, call

from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.engine.components import CombatStateComponent, BattleParticipantComponent
from app.core.engine.systems import BattleSystem


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def raca_humana():
    return Raca(nome="Humano", bonus_atributos={}, emoji="🧑")


@pytest.fixture
def classe_guerreiro():
    return ClasseRPG(nome="Guerreiro", bonus_caminhos={}, habilidades=[])


@pytest.fixture
def heroi(raca_humana, classe_guerreiro):
    """Herói de referência para os testes de combate."""
    return Personagem(
        nome="Herói Teste",
        nivel=3,
        raca=raca_humana,
        classe_rpg=classe_guerreiro,
        forca_base=3,
        agilidade_base=2,
        res_base=3,
        perc_base=2,
        exub_base=1,
    )


@pytest.fixture
def inimigo(raca_humana, classe_guerreiro):
    """Inimigo de referência para os testes de combate."""
    return Personagem(
        nome="Goblin",
        nivel=1,
        raca=raca_humana,
        classe_rpg=classe_guerreiro,
        forca_base=1,
        agilidade_base=1,
        res_base=1,
        perc_base=1,
        exub_base=0,
    )


@pytest.fixture
def battle_sys():
    """Instância limpa do BattleSystem para cada teste."""
    sistema = BattleSystem()
    # Registra o BattleSystem em um mundo Esper isolado para testes
    world_nome = f"teste_battle_{id(sistema)}"
    esper.switch_world(world_nome)
    esper.add_processor(sistema)
    yield sistema
    # Cleanup: remove o mundo de teste
    try:
        esper.switch_world("default")
        esper.delete_world(world_nome)
    except Exception:
        pass


@pytest.fixture
def eventos_capturados():
    """Captura os eventos disparados pelo Esper durante os testes."""
    eventos = []

    def capturar(nome_evento):
        def handler(dados):
            eventos.append({"evento": nome_evento, "dados": dados})
        return handler

    handlers = {}
    for evento in ["combate_iniciado", "turno_calculado", "combate_encerrado"]:
        handler = capturar(evento)
        handlers[evento] = handler
        esper.set_handler(evento, handler)

    yield eventos

    for evento, handler in handlers.items():
        try:
            esper.remove_handler(evento, handler)
        except Exception:
            pass


# ==============================================================================
# TESTES: COMPONENTES DE COMBATE
# ==============================================================================

class TestComponentesCombate:
    """Testa os novos componentes ECS relacionados ao combate."""

    def test_combat_state_component_valores_padrao(self):
        """CombatStateComponent deve inicializar com valores padrão corretos."""
        comp = CombatStateComponent()
        assert comp.em_combate is True
        assert comp.turno_atual == 0
        assert comp.fase_turno == "aguardando_acao"
        assert comp.iniciativa_jogador == 0
        assert comp.iniciativa_inimigo == 0

    def test_battle_participant_component_criacao(self):
        """BattleParticipantComponent deve aceitar tipo jogador/inimigo/rede."""
        comp_jogador = BattleParticipantComponent(
            personagem_id="heroi_1", tipo="jogador"
        )
        comp_inimigo = BattleParticipantComponent(
            personagem_id="goblin_1", tipo="inimigo", nivel=3, emoji_sprite="👹"
        )
        assert comp_jogador.tipo == "jogador"
        assert comp_inimigo.tipo == "inimigo"
        assert comp_inimigo.nivel == 3
        assert comp_inimigo.emoji_sprite == "👹"


# ==============================================================================
# TESTES: INICIALIZAÇÃO DO COMBATE
# ==============================================================================

class TestInicializacaoCombate:
    """Testa o setup do combate via BattleSystem.iniciar_combate."""

    def test_iniciar_combate_usa_deepcopy(self, battle_sys, heroi, inimigo):
        """
        Regra 5: O BattleSystem deve usar deepcopy para isolar os combatentes.
        Modificar herói interno não deve afetar o herói original.
        Aceita tanto um único inimigo quanto lista (ambos são suportados).
        """
        hp_original_heroi = heroi.pv_atual
        hp_original_inimigo = inimigo.pv_atual

        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])

        # Confirma que os objetos internos são cópias independentes
        assert battle_sys.heroi is not heroi
        assert battle_sys.inimigo is not inimigo  # alias property para inimigos[0]
        assert battle_sys.heroi.pv_atual == hp_original_heroi
        assert battle_sys.inimigo.pv_atual == hp_original_inimigo

    def test_iniciar_combate_dispara_evento(self, battle_sys, heroi, inimigo, eventos_capturados):
        """BattleSystem deve disparar o evento 'combate_iniciado' ao iniciar."""
        battle_sys.iniciar_combate(heroi, [inimigo])

        assert len(eventos_capturados) >= 1
        evento_inicio = next(
            (e for e in eventos_capturados if e["evento"] == "combate_iniciado"), None
        )
        assert evento_inicio is not None
        assert "heroi" in evento_inicio["dados"]
        assert "inimigo" in evento_inicio["dados"]   # alias retrocompatível
        assert "inimigos" in evento_inicio["dados"]  # nova lista
        assert "iniciativa_jogador" in evento_inicio["dados"]
        assert "iniciativa_inimigo" in evento_inicio["dados"]

    def test_iniciar_combate_ativa_flag_combate_ativo(self, battle_sys, heroi, inimigo):
        """battle_sys.combate_ativo deve ser True após iniciar."""
        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])
        assert battle_sys.combate_ativo is True

    def test_iniciativa_considera_agilidade(self, battle_sys, heroi, inimigo, monkeypatch):
        """
        Regra 5: Iniciativa = 1d6 + Agilidade.
        Com d6 fixo em 1, o personagem com maior Agilidade vai primeiro.
        """
        # Herói tem agilidade=2, inimigo agilidade=1
        # Com dado fixo em 1: herói=3, inimigo=2 → herói vai primeiro
        monkeypatch.setattr(random, "randint", lambda a, b: 1)

        com_evento = []
        def capturar_inicio(dados):
            com_evento.append(dados)
        esper.set_handler("combate_iniciado", capturar_inicio)

        battle_sys.iniciar_combate(heroi, [inimigo])
        esper.remove_handler("combate_iniciado", capturar_inicio)

        assert len(com_evento) == 1
        ini_jogador = com_evento[0]["iniciativa_jogador"]
        ini_inimigo = com_evento[0]["iniciativa_inimigo"]
        assert ini_jogador > ini_inimigo
        assert battle_sys.heroi_vai_primeiro is True


# ==============================================================================
# TESTES: EXECUÇÃO DE TURNO DO JOGADOR
# ==============================================================================

class TestTurnoJogador:
    """Testa a execução de ações do jogador via BattleSystem."""

    def test_acao_ataque_dispara_turno_calculado(
        self, battle_sys, heroi, inimigo, monkeypatch, eventos_capturados
    ):
        """executar_acao_jogador('ataque') deve disparar 'turno_calculado' com fase='jogador'."""
        # Garante acerto: d6 alto para ataque, baixo para defesa
        monkeypatch.setattr(random, "randint", lambda a, b: 6 if b == 6 else 1)

        battle_sys.iniciar_combate(heroi, [inimigo])
        # Limpa eventos de início
        eventos_capturados.clear()

        # Bloqueia a task assíncrona da IA (não temos event loop em testes síncronos)
        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("ataque")

        evento_turno = next(
            (e for e in eventos_capturados if e["evento"] == "turno_calculado"), None
        )
        assert evento_turno is not None
        assert evento_turno["dados"]["fase"] == "jogador"
        assert "resultado" in evento_turno["dados"]
        assert "inimigos" in evento_turno["dados"]  # novo campo com snapshot de inimigos

    def test_acao_invalida_sem_combate_ativo(self, battle_sys, heroi, inimigo):
        """executar_acao_jogador deve ignorar quando combate_ativo=False."""
        battle_sys.combate_ativo = False
        # Não deve disparar eventos nem lançar exceção
        battle_sys.executar_acao_jogador("ataque")

    def test_inimigo_morto_encerra_combate(
        self, battle_sys, heroi, inimigo, monkeypatch, eventos_capturados
    ):
        """Quando o inimigo morre no turno do jogador, deve disparar 'combate_encerrado'."""
        # Usa dados muito altos para garantir morte do inimigo
        monkeypatch.setattr(random, "randint", lambda a, b: 6)

        battle_sys.iniciar_combate(heroi, [inimigo])
        # Força o HP do inimigo para 1 para garantir morte no próximo ataque
        battle_sys.inimigos[0].pv_atual = 1

        eventos_capturados.clear()

        # Executa a ação (inimigo vai morrer)
        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("ataque")

        evento_encerrado = next(
            (e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None
        )
        assert evento_encerrado is not None
        assert evento_encerrado["dados"]["vencedor"] == "jogador"
        assert battle_sys.combate_ativo is False


# ==============================================================================
# TESTES: COMBATE COM MÚLTIPLOS INIMIGOS
# ==============================================================================

class TestMultiplosInimigos:
    """Testa o suporte a 1-4 inimigos no BattleSystem."""

    @pytest.fixture
    def inimigo2(self, raca_humana, classe_guerreiro):
        """Segundo inimigo para testes de grupo."""
        return Personagem(
            nome="Kobold",
            nivel=1,
            raca=raca_humana,
            classe_rpg=classe_guerreiro,
            forca_base=1,
            agilidade_base=2,
            res_base=1,
            perc_base=1,
            exub_base=0,
        )

    def test_iniciar_com_dois_inimigos(self, battle_sys, heroi, inimigo, inimigo2):
        """BattleSystem deve aceitar lista de 2 inimigos."""
        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo, inimigo2])

        assert len(battle_sys.inimigos) == 2
        assert battle_sys.inimigos[0].nome == "Goblin"
        assert battle_sys.inimigos[1].nome == "Kobold"
        # Alias retrocompatível
        assert battle_sys.inimigo.nome == "Goblin"

    def test_snapshot_inimigos_retorna_estados(self, battle_sys, heroi, inimigo, inimigo2):
        """_snapshot_inimigos deve retornar lista com hp, hp_max, vivo e index."""
        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo, inimigo2])

        snapshot = battle_sys._snapshot_inimigos()
        assert len(snapshot) == 2
        assert snapshot[0]["index"] == 0
        assert snapshot[1]["index"] == 1
        assert snapshot[0]["vivo"] is True

    def test_turno_calculado_inclui_lista_inimigos(
        self, battle_sys, heroi, inimigo, inimigo2, monkeypatch, eventos_capturados
    ):
        """O evento turno_calculado deve incluir o campo 'inimigos' com snapshot completo."""
        monkeypatch.setattr(random, "randint", lambda a, b: 3)
        monkeypatch.setattr(random, "random", lambda: 0.9)

        battle_sys.iniciar_combate(heroi, [inimigo, inimigo2])
        eventos_capturados.clear()

        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("ataque", alvo_index=0)

        evento = next(
            (e for e in eventos_capturados if e["evento"] == "turno_calculado"), None
        )
        assert evento is not None
        assert "inimigos" in evento["dados"]
        assert len(evento["dados"]["inimigos"]) == 2

    def test_todos_inimigos_mortos_encerra_vitoria(
        self, battle_sys, heroi, inimigo, inimigo2, monkeypatch, eventos_capturados
    ):
        """Todos os inimigos com HP 0 deve encerrar com vitória do jogador."""
        monkeypatch.setattr(random, "randint", lambda a, b: 6)

        battle_sys.iniciar_combate(heroi, [inimigo, inimigo2])
        # Força HP zerado de ambos
        battle_sys.inimigos[0].pv_atual = 1
        battle_sys.inimigos[1].pv_atual = 0  # já morto
        eventos_capturados.clear()

        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("ataque", alvo_index=0)

        evento_enc = next(
            (e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None
        )
        assert evento_enc is not None
        assert evento_enc["dados"]["vencedor"] == "jogador"


# ==============================================================================
# TESTES: IA DO INIMIGO
# ==============================================================================

class TestIAInimigo:
    """Testa o comportamento de tomada de decisão da IA do inimigo."""

    def test_ia_ataca_com_hp_alto(self, battle_sys, heroi, inimigo, monkeypatch):
        """
        Com HP > 30%, a IA deve preferir atacar (sem chance de cura).
        """
        # Garante: random() retorna 0.9 → não cura, não usa magia
        monkeypatch.setattr(random, "random", lambda: 0.9)

        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])

        # HP alto: 100%
        battle_sys.inimigos[0].pv_atual = battle_sys.inimigos[0].max_hp
        acao = battle_sys._decidir_acao_ia()
        assert acao == "ataque"

    def test_ia_pode_curar_com_hp_baixo(self, battle_sys, heroi, inimigo, monkeypatch):
        """
        Com HP < 30% e random < 0.4, a IA deve tentar se curar.
        """
        monkeypatch.setattr(random, "random", lambda: 0.1)  # < 0.4 → cura

        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])

        # HP muito baixo: < 30%
        battle_sys.inimigos[0].pv_atual = 1
        acao = battle_sys._decidir_acao_ia()
        assert acao == "cura"

    def test_turno_inimigo_sincronizado_dispara_evento(
        self, battle_sys, heroi, inimigo, monkeypatch, eventos_capturados
    ):
        """O turno síncrono do inimigo deve disparar 'turno_calculado' com fase='inimigo'."""
        monkeypatch.setattr(random, "randint", lambda a, b: 1)
        monkeypatch.setattr(random, "random", lambda: 0.9)

        battle_sys.iniciar_combate(heroi, [inimigo])
        eventos_capturados.clear()

        battle_sys._executar_turno_inimigo_sincrono()

        evento_turno = next(
            (e for e in eventos_capturados if e["evento"] == "turno_calculado"), None
        )
        assert evento_turno is not None
        assert evento_turno["dados"]["fase"] == "inimigo"

    def test_heroi_morto_encerra_com_derrota(
        self, battle_sys, heroi, inimigo, monkeypatch, eventos_capturados
    ):
        """Quando o herói morre no turno do inimigo, deve disparar 'combate_encerrado' com derrota."""
        monkeypatch.setattr(random, "randint", lambda a, b: 6)
        monkeypatch.setattr(random, "random", lambda: 0.9)

        battle_sys.iniciar_combate(heroi, [inimigo])
        eventos_capturados.clear()

        # Força o HP do herói para 0 diretamente (morte garantida, determinística)
        # Isso é necessário porque o cálculo de dano vs. defesa pode variar
        battle_sys.heroi.pv_atual = 0

        battle_sys._executar_turno_inimigo_sincrono()

        evento_encerrado = next(
            (e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None
        )
        assert evento_encerrado is not None
        assert evento_encerrado["dados"]["vencedor"] == "inimigo"


# ==============================================================================
# TESTES: RESOLUÇÃO DE AÇÕES
# ==============================================================================

class TestResolucaoAcoes:
    """Testa o mapeamento de ações para métodos do Personagem de domínio."""

    def test_resolver_ataque_retorna_resultado_valido(self, battle_sys, heroi, inimigo):
        """_resolver_acao_personagem('ataque') deve retornar dict com 'acertou' e 'atacante'."""
        resultado = battle_sys._resolver_acao_personagem("ataque", atacante=heroi, alvo=inimigo)
        assert "acertou" in resultado
        assert "atacante" in resultado
        assert resultado["atacante"] == heroi.nome

    def test_resolver_acao_invalida_usa_ataque_fallback(self, battle_sys, heroi, inimigo):
        """Ação desconhecida deve cair no fallback de ataque desarmado."""
        resultado = battle_sys._resolver_acao_personagem("voar", atacante=heroi, alvo=inimigo)
        # Não deve lançar exceção e deve retornar resultado com acertou
        assert "acertou" in resultado

    def test_resolver_cura_retorna_sem_dano(self, battle_sys, heroi, inimigo):
        """Ação 'cura' da IA deve retornar dano_causado=0."""
        resultado = battle_sys._resolver_acao_personagem("cura", atacante=inimigo, alvo=heroi)
        assert resultado["dano_causado"] == 0
        assert resultado["acertou"] is True


# ==============================================================================
# TESTES: ENCERRAMENTO E LIMPEZA
# ==============================================================================

class TestEncerramentoCombate:
    """Testa o processo de encerramento do combate e limpeza do ECS."""

    def test_encerrar_combate_desativa_flag(self, battle_sys, heroi, inimigo):
        """Após _encerrar_combate, battle_sys.combate_ativo deve ser False."""
        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])

        with patch.object(esper, "dispatch_event"):
            battle_sys._encerrar_combate(vencedor="jogador")

        assert battle_sys.combate_ativo is False

    def test_encerrar_dispara_evento_correto(self, battle_sys, heroi, inimigo, eventos_capturados):
        """_encerrar_combate deve disparar 'combate_encerrado' com o vencedor correto."""
        with patch.object(esper, "dispatch_event"):
            battle_sys.iniciar_combate(heroi, [inimigo])

        eventos_capturados.clear()
        battle_sys._encerrar_combate(vencedor="inimigo")

        evento = next(
            (e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None
        )
        assert evento is not None
        assert evento["dados"]["vencedor"] == "inimigo"


# ==============================================================================
# TESTES: INTEGRIDADE DO EVENTO iniciar_combate NO EVENTSYSTEM
# ==============================================================================

class TestEventoIniciarCombate:
    """Testa que o EventSystem processa corretamente o tipo 'iniciar_combate'."""

    def test_command_iniciar_combate_dispara_evento_esper(self):
        """
        O EventSystem deve disparar 'solicitar_iniciar_combate' ao processar
        um comando do tipo 'iniciar_combate'.
        """
        from app.core.engine.systems import EventSystem, InventarySystem
        from unittest.mock import MagicMock

        inv_sys = InventarySystem()
        game_state = MagicMock()
        game_state.set_switch = MagicMock()

        log_callback = MagicMock()
        event_sys = EventSystem(inv_sys, game_state, log_callback)

        # Configura o estado mínimo necessário
        event_sys.parms = {"paginas": [{"configuracao_visual": {"emoji": "⚔️"}}]}
        event_sys.entidade_atual_id = 1

        dados_inimigo = {
            "nome": "Goblin",
            "nivel": 2,
            "forca": 2,
            "agilidade": 1,
            "resistencia": 2,
            "percepcao": 1,
            "exuberancia": 0,
            "emoji": "👹",
        }

        eventos_disparados = []
        def capturar_combate(dados):
            eventos_disparados.append(dados)

        esper.set_handler("solicitar_iniciar_combate", capturar_combate)

        evento_cmd = {"tipo": "iniciar_combate", "dados": dados_inimigo}
        event_sys._processar_comando_individual(evento_cmd)

        esper.remove_handler("solicitar_iniciar_combate", capturar_combate)

        assert len(eventos_disparados) == 1
        assert eventos_disparados[0]["nome"] == "Goblin"

    def test_iniciar_combate_executa_ramos_conforme_resultado(self):
        """Testa que o comando iniciar_combate processa ramos de resultado (ex: venceu)."""
        from app.core.engine.systems import EventSystem, InventarySystem
        from unittest.mock import MagicMock

        inv_sys = InventarySystem()
        game_state = MagicMock()
        game_state.set_switch = MagicMock()

        log_callback = MagicMock()
        event_sys = EventSystem(inv_sys, game_state, log_callback)

        event_sys.parms = {"paginas": [{"configuracao_visual": {"emoji": "⚔️"}}]}
        event_sys.entidade_atual_id = 1

        dados_inimigo = {
            "nome": "Goblin Fraco",
            "nivel": 1,
            "forca": 1,
            "agilidade": 1,
            "resistencia": 1,
            "percepcao": 1,
            "exuberancia": 0,
            "emoji": "👹",
            "ramos": {
                "venceu": [
                    {
                        "tipo": "controle_switch",
                        "dados": {"nome": "goblin_derrotado", "valor": True}
                    }
                ],
                "perdeu": []
            }
        }

        evento_cmd = {"tipo": "iniciar_combate", "dados": dados_inimigo}
        event_sys._processar_comando_individual(evento_cmd)

        # O Herói tem mais atributos base e vence o Goblin Fraco, ativando o switch do ramo "venceu"
        game_state.set_switch.assert_called_with("goblin_derrotado", True)

    def test_ramo_perdeu_com_notificacao_e_teleporte(self):
        """Testa que o ramo 'perdeu' executando notificacao seguida de teleporte não causa RuntimeError."""
        from app.core.engine.systems import EventSystem, InventarySystem
        from unittest.mock import MagicMock

        inv_sys = InventarySystem()
        game_state = MagicMock()
        log_callback = MagicMock()
        event_sys = EventSystem(inv_sys, game_state, log_callback)

        event_sys.parms = {"paginas": [{"configuracao_visual": {"emoji": "⚔️"}}]}
        event_sys.entidade_atual_id = 1
        event_sys.aguardando_combate = True

        teleporte_executado = []

        def simular_ao_mudar_de_mapa(dados):
            teleporte_executado.append(dados)
            # Simula o re-registro de handlers que acontecia ao mudar de mapa
            esper.set_handler("mudar_mapa", simular_ao_mudar_de_mapa)

        esper.set_handler("mudar_mapa", simular_ao_mudar_de_mapa)

        ramos = {
            "perdeu": [
                {
                    "tipo": "notificacao",
                    "dados": {"texto": "Você perdeu a batalha!"}
                },
                {
                    "tipo": "teleporte",
                    "dados": {"mapa_id": 2, "pos_x": 10, "pos_y": 10}
                }
            ]
        }
        event_sys.ramos_combate_pendente = ramos
        event_sys.inimigo_nome_combate_pendente = "Chefe Boss"

        try:
            esper.dispatch_event("combate_finalizado_gui", "perdeu")
        finally:
            try:
                esper.remove_handler("mudar_mapa", simular_ao_mudar_de_mapa)
            except Exception:
                pass

        assert len(teleporte_executado) == 1
        assert teleporte_executado[0]["mapa_id"] == 2
        log_callback.assert_any_call("Você perdeu a batalha!", notif=True)


class TestUsoDeItensEBatalha:
    """Testa a integração do inventário e status dos jogadores no combate."""

    def test_usar_item_com_sucesso(self, battle_sys, heroi, inimigo):
        """Se o inventário do herói no ECS possui poção, ela deve ser consumida e curar o herói."""
        from app.core.engine.components import InventoryComponent
        
        # Reduz HP do herói para testar a cura
        heroi.pv_atual = 10
        battle_sys.iniciar_combate(heroi, [inimigo])
        
        # Configura a entidade 1 no ECS com o componente de inventário contendo uma poção
        try:
            esper.components_for_entity(1)
        except KeyError:
            esper.create_entity()
            
        esper.add_component(1, InventoryComponent(itens={"poção": 1}))
        
        # Executa a ação de usar item
        # Ao usar, o HP do herói deve curar 20 pontos e a poção deve ser consumida do ECS
        battle_sys.executar_acao_jogador("item")
        
        # O HP do herói de domínio no BattleSystem deve ter aumentado (de 10 para 30)
        assert battle_sys.heroi.pv_atual == 30
        
        # A poção deve ter sido removida do InventoryComponent no ECS
        inv = esper.component_for_entity(1, InventoryComponent)
        assert "poção" not in inv.itens

    def test_usar_item_sem_sucesso(self, battle_sys, heroi, inimigo):
        """Se o inventário do herói no ECS não possui poção, deve disparar erro e não curar."""
        from app.core.engine.components import InventoryComponent
        
        heroi.pv_atual = 10
        battle_sys.iniciar_combate(heroi, [inimigo])
        
        try:
            esper.components_for_entity(1)
        except KeyError:
            esper.create_entity()
            
        esper.add_component(1, InventoryComponent(itens={}))
        
        eventos_recebidos = []
        def capturar_turno(dados):
            eventos_recebidos.append(dados)
            
        esper.set_handler("turno_calculado", capturar_turno)
        
        # Tenta usar poção sem ter no inventário
        battle_sys.executar_acao_jogador("item")
        
        esper.remove_handler("turno_calculado", capturar_turno)
        
        # HP não deve ter sido alterado
        assert battle_sys.heroi.pv_atual == 10
        
        # Deve ter gerado um erro_item no resultado do evento
        assert len(eventos_recebidos) == 1
        assert "erro_item" in eventos_recebidos[0]["resultado"]
        assert "Você não possui" in eventos_recebidos[0]["resultado"]["erro_item"]

    def test_sincronizacao_combate_para_ecs(self, heroi):
        """Testa que os status e equipamentos do domínio são sincronizados de volta para o ECS."""
        esper.clear_database()
        from app.views.battle_screen import BattleScreen
        from app.core.engine.components import StatsComponent, EquipmentComponent
        
        try:
            esper.components_for_entity(1)
        except KeyError:
            esper.create_entity()
            
        # Adiciona componentes vazios para sincronizar
        esper.add_component(1, StatsComponent(nome="Herói", classe="mago", hp=100, max_hp=100, mp=50, max_mp=50, ataque_base=10, defesa_base=5))
        esper.add_component(1, EquipmentComponent())
        
        screen = BattleScreen(heroi, [])
        screen.battle_sys = MagicMock()
        screen.battle_sys.heroi = heroi
        
        # Altera o HP e equipamentos do herói do domínio
        heroi.pv_atual = 45
        heroi.pm_atual = 15
        
        from app.core.entities.equipamentos import Arma, Armadura
        heroi.mao_direita = Arma(nome="Espada de Teste", dano=8, tipo="corpo")
        heroi.armadura = Armadura(nome="Couro de Teste", defesa=4)
        
        # Executa a sincronização
        screen._sincronizar_combate_para_ecs()
        
        # Verifica se o ECS foi atualizado
        stats = esper.component_for_entity(1, StatsComponent)
        eqp = esper.component_for_entity(1, EquipmentComponent)
        
        assert stats.hp == 45
        assert stats.mp == 15
        assert eqp.arma["nome"] == "Espada de Teste"
        assert eqp.arma["bonus_atk"] == 8
        assert eqp.armadura["nome"] == "Couro de Teste"
        assert eqp.armadura["bonus_def"] == 4
        esper.clear_database()

    def test_obter_heroi_dominio_hidratacao_do_ecs(self):
        """Testa que _obter_heroi_dominio enriquece a entidade do domínio com o estado do ECS."""
        esper.clear_database()
        from app.views.game_play_screen import GamePlayScreen
        from app.core.engine.components import StatsComponent, EquipmentComponent
        from app.models.personagens_db import PersonagemDB
        
        try:
            esper.components_for_entity(1)
        except KeyError:
            esper.create_entity()
            
        esper.add_component(1, StatsComponent(nome="Herói ECS", classe="mago", hp=20, max_hp=100, mp=12, max_mp=50, ataque_base=10, defesa_base=5))
        
        eqp_comp = EquipmentComponent()
        eqp_comp.arma = {"nome": "Espada Divina", "bonus_atk": 10, "tipo": "corpo"}
        eqp_comp.armadura = {"nome": "Armadura Divina", "bonus_def": 8}
        esper.add_component(1, eqp_comp)
        
        # Criamos um mock da tela e do banco
        screen = MagicMock(spec=GamePlayScreen)
        screen.personagem_id = 1
        
        # Mock do PersonagemDB
        personagem_db = MagicMock(spec=PersonagemDB)
        personagem_db.nome = "Herói DB"
        personagem_db.nivel = 1
        personagem_db.raca = MagicMock()
        personagem_db.raca.nome = "Humano"
        personagem_db.raca.bonus_atributos = {}
        personagem_db.raca.emoji = "🧑"
        personagem_db.classe = MagicMock()
        personagem_db.classe.nome = "Guerreiro"
        personagem_db.classe.bonus_caminhos = {}
        personagem_db.classe.habilidades = []
        personagem_db.forca_base = 3
        personagem_db.agilidade_base = 2
        personagem_db.resistencia_base = 3
        personagem_db.percepcao_base = 2
        personagem_db.exuberancia_base = 1
        personagem_db.mao_direita = None
        personagem_db.mao_esquerda = None
        personagem_db.armadura_equipada = None
        
        with patch("app.views.game_play_screen.SessionLocal") as mock_session_class:
            mock_session = MagicMock()
            mock_session.query().filter_by().first.return_value = personagem_db
            mock_session_class.return_value.__enter__.return_value = mock_session
            
            # Invoca o método original que foi modificado em game_play_screen
            heroi_dominio = GamePlayScreen._obter_heroi_dominio(screen)
            
            assert heroi_dominio is not None
            assert heroi_dominio.pv_atual == 20
            assert heroi_dominio.pm_atual == 12
            assert heroi_dominio.mao_direita.nome == "Espada Divina"
            assert heroi_dominio.mao_direita.dano == 10
            assert heroi_dominio.armadura.nome == "Armadura Divina"
            assert heroi_dominio.armadura.defesa == 8
            
        esper.clear_database()
