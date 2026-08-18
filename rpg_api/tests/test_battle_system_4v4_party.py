import pytest
import esper
import random
from unittest.mock import patch
from app.core.entities.personagens import Personagem, Raca, ClasseRPG, Party
from app.core.entities.habilidades_magias import Magia, Efeito
from app.core.engine.systems import BattleSystem

@pytest.fixture
def battle_sys():
    esper.clear_database()
    esper.event_registry.clear()
    bs = BattleSystem()
    return bs

@pytest.fixture
def party_4_aliados():
    raca_hum = Raca("Humano", bonus_atributos={"forca": 1, "destreza": 1, "constituicao": 1, "inteligencia": 1, "sabedoria": 1, "carisma": 1})
    raca_elfo = Raca("Elfo", bonus_atributos={"destreza": 2, "sabedoria": 1})
    
    cls_guerreiro = ClasseRPG("Guerreiro", bonus_caminhos={})
    cls_clerigo = ClasseRPG("Clérigo", bonus_caminhos={"luz": 2})
    cls_ladino = ClasseRPG("Ladino", bonus_caminhos={})
    cls_mago = ClasseRPG("Mago", bonus_caminhos={"fogo": 2, "ar": 2})

    p1 = Personagem("Artorias", 2, raca_hum, cls_guerreiro, 4, 2, 3, 2, 2)
    p2 = Personagem("Aerith", 2, raca_elfo, cls_clerigo, 2, 3, 2, 3, 4)
    p3 = Personagem("Locke", 2, raca_hum, cls_ladino, 2, 5, 2, 4, 2)
    p4 = Personagem("Vivi", 2, raca_hum, cls_mago, 1, 1, 2, 3, 4)

    for p in [p1, p2, p3, p4]:
        p.reset_status()

    # Adiciona itens e magias
    p1.adicionar_item_inventario("Poção de Vida", 3)
    p2.adicionar_item_inventario("Elixir de Mana", 2)

    magia_cura = Magia("Cura Sagrada", custo_pm=3, requisito_caminhos={"luz": 1}, cura_base=12, tipo_execucao="ambos")
    p2.aprender_magia(magia_cura)

    magia_area = Magia("Chuva de Raios", custo_pm=5, requisito_caminhos={"ar": 2}, dano_base=15, dano_area=True, tipo_execucao="combate")
    p4.aprender_magia(magia_area)

    party = Party()
    for p in [p1, p2, p3, p4]:
        party.adicionar_membro(p)

    return party

@pytest.fixture
def inimigos_4():
    raca_monstro = Raca("Monstro")
    cls_monstro = ClasseRPG("Monstro")

    i1 = Personagem("Orc Chefe", 2, raca_monstro, cls_monstro, 3, 2, 3, 2, 2)
    i2 = Personagem("Goblin Arqueiro", 2, raca_monstro, cls_monstro, 2, 4, 2, 3, 2)
    i3 = Personagem("Esqueleto Guerreiro", 2, raca_monstro, cls_monstro, 2, 1, 2, 2, 2)
    i4 = Personagem("Xamã Sombrio", 2, raca_monstro, cls_monstro, 2, 3, 2, 3, 2)

    for i in [i1, i2, i3, i4]:
        i.reset_status()

    return [i1, i2, i3, i4]


_GLOBAL_HANDLERS = {}

@pytest.fixture
def eventos_capturados(battle_sys):
    eventos = []
    def capturar(nome):
        def h(dados):
            eventos.append({"evento": nome, "dados": dados})
        return h

    for ev in ["combate_iniciado", "turno_iniciado", "turno_calculado", "combate_encerrado"]:
        handler = capturar(ev)
        _GLOBAL_HANDLERS[ev] = handler
        esper.set_handler(ev, handler)

    yield eventos

    for ev, h in list(_GLOBAL_HANDLERS.items()):
        try:
            esper.remove_handler(ev, h)
        except Exception:
            pass
    _GLOBAL_HANDLERS.clear()


class TestBattleSystem4v4Party:

    def test_iniciar_combate_com_party_4_aliados_vs_4_inimigos(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Valida inicialização 4v4 com deepcopy e geração de fila de 8 combatentes por iniciativa."""
        monkeypatch.setattr(random, "randint", lambda a, b: 3)

        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)

        assert battle_sys.combate_ativo is True
        assert len(battle_sys.aliados) == 4
        assert len(battle_sys.inimigos) == 4
        assert len(battle_sys.fila_turnos) == 8

        # Deepcopy check
        assert battle_sys.aliados[0] is not party_4_aliados.membros[0]

        ev_ini = next((e for e in eventos_capturados if e["evento"] == "combate_iniciado"), None)
        assert ev_ini is not None
        assert len(ev_ini["dados"]["aliados"]) == 4
        assert len(ev_ini["dados"]["inimigos"]) == 4
        assert len(ev_ini["dados"]["fila_turnos"]) == 8

    def test_rotacao_turnos_individuais_aliados_e_inimigos(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Valida que cada personagem (aliado ou inimigo) possui seu próprio turno individual."""
        monkeypatch.setattr(random, "randint", lambda a, b: 2)

        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)

        turnos_iniciados = [e for e in eventos_capturados if e["evento"] == "turno_iniciado"]
        assert len(turnos_iniciados) >= 1
        primeiro_turno = turnos_iniciados[0]["dados"]
        assert primeiro_turno["turno"] == 1
        assert primeiro_turno["e_aliado"] is True
        assert primeiro_turno["combatente_ativo"].nome == "Locke"

    def test_aliado_usa_magia_em_area_atinge_todos_inimigos_vivos(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Valida que magia em área atinge todos os 4 inimigos de uma única vez."""
        monkeypatch.setattr(random, "randint", lambda a, b: 2)

        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)
        eventos_capturados.clear()

        # Força o turno para o mago Vivi
        vivi = next(a for a in battle_sys.aliados if a.nome == "Vivi")
        battle_sys.fila_turnos[battle_sys.indice_turno_atual] = {
            "combatente": vivi, "tipo": "aliado", "iniciativa": 10, "agilidade": 1, "indice_time": 3, "nome": "Vivi"
        }

        # Mock de acerto garantido
        monkeypatch.setattr(vivi, "_rolar_d6", lambda qtd: qtd * 6)
        for i in battle_sys.inimigos:
            monkeypatch.setattr(i, "_rolar_d6", lambda qtd: qtd * 1)

        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("magia", nome_magia="Chuva de Raios")

        ev_calc = next((e for e in eventos_capturados if e["evento"] == "turno_calculado"), None)
        assert ev_calc is not None
        res = ev_calc["dados"]["resultado"]
        assert res["sucesso"] is True
        assert res.get("dano_area") is True
        assert res.get("alvos_atingidos") == 4
        assert res["dano_causado"] > 0

    def test_aliado_usa_magia_cura_em_outro_aliado(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Valida que suporte/cura pode ser direcionado a outro membro da equipe."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)
        eventos_capturados.clear()

        aerith = next(a for a in battle_sys.aliados if a.nome == "Aerith")
        artorias = next(a for a in battle_sys.aliados if a.nome == "Artorias")
        artorias.pv_atual = 5 # Ferido

        battle_sys.fila_turnos[battle_sys.indice_turno_atual] = {
            "combatente": aerith, "tipo": "aliado", "iniciativa": 10, "agilidade": 3, "indice_time": 1, "nome": "Aerith"
        }

        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("magia", nome_magia="Cura Sagrada", alvo_tipo="aliado", alvo_index=0)

        ev_calc = next((e for e in eventos_capturados if e["evento"] == "turno_calculado"), None)
        assert ev_calc is not None
        assert artorias.pv_atual > 5

    def test_aliado_usa_item_do_inventario_individual(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Valida uso de item do inventário individual do combatente da vez."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)

        artorias = next(a for a in battle_sys.aliados if a.nome == "Artorias")
        artorias.pv_atual = 4
        qtd_inicial = artorias.obter_quantidade_item("Poção de Vida")
        assert qtd_inicial == 3

        battle_sys.fila_turnos[battle_sys.indice_turno_atual] = {
            "combatente": artorias, "tipo": "aliado", "iniciativa": 10, "agilidade": 2, "indice_time": 0, "nome": "Artorias"
        }

        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("item", nome_item="Poção de Vida", alvo_tipo="aliado", alvo_index=0)

        assert artorias.pv_atual > 4
        assert artorias.obter_quantidade_item("Poção de Vida") == 2

    def test_combatente_derrotado_durante_rodada_e_pulado(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Se um combatente morre antes de agir na rodada, o turno deve ignorá-lo suavemente."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)

        # Força o segundo combatente da fila como morto
        battle_sys.fila_turnos[1]["combatente"].pv_atual = 0

        # Primeiro combatente age
        with patch.object(battle_sys, "_agendar_turno_inimigo"):
            battle_sys.executar_acao_jogador("ataque", alvo_index=0)

        # O ponteiro deve avançar além do combatente morto
        assert battle_sys.indice_turno_atual >= 1

    def test_vitoria_quando_todos_inimigos_sao_derrotados(self, battle_sys, party_4_aliados, inimigos_4, eventos_capturados):
        """Ao abater os 4 inimigos, dispara 'combate_encerrado' com vencedor='jogador'."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)
        eventos_capturados.clear()

        # Mata os 4 inimigos
        for i in battle_sys.inimigos:
            i.pv_atual = 0

        battle_sys._processar_proximo_turno()

        assert battle_sys.combate_ativo is False
        ev_fim = next((e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None)
        assert ev_fim is not None
        assert ev_fim["dados"]["vencedor"] == "jogador"

    def test_derrota_quando_todos_aliados_sao_derrotados(self, battle_sys, party_4_aliados, inimigos_4, eventos_capturados):
        """Ao abater os 4 aliados, dispara 'combate_encerrado' com vencedor='inimigo'."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)
        eventos_capturados.clear()

        # Mata os 4 aliados
        for a in battle_sys.aliados:
            a.pv_atual = 0

        battle_sys._processar_proximo_turno()

        assert battle_sys.combate_ativo is False
        ev_fim = next((e for e in eventos_capturados if e["evento"] == "combate_encerrado"), None)
        assert ev_fim is not None
        assert ev_fim["dados"]["vencedor"] == "inimigo"

    def test_ia_inimiga_escolhe_alvo_inteligente(self, battle_sys, party_4_aliados, inimigos_4, monkeypatch, eventos_capturados):
        """Inimigo seleciona alvo vivo entre os aliados disponíveis."""
        battle_sys.iniciar_combate(party_4_aliados, inimigos_4)
        eventos_capturados.clear()

        orc = battle_sys.inimigos[0]
        battle_sys.fila_turnos[battle_sys.indice_turno_atual] = {
            "combatente": orc, "tipo": "inimigo", "iniciativa": 10, "agilidade": 2, "indice_time": 0, "nome": "Orc Chefe"
        }

        monkeypatch.setattr(random, "random", lambda: 0.9) # Garante ataque físico
        battle_sys._executar_turno_inimigo_sincrono()

        ev_calc = next((e for e in eventos_capturados if e["evento"] == "turno_calculado"), None)
        assert ev_calc is not None
        assert ev_calc["dados"]["fase"] == "inimigo"
        assert ev_calc["dados"]["atacante"].nome == "Orc Chefe"
