import pytest
from app.core.entities.personagens import Personagem, Raca, ClasseRPG, Party, Equipe
from app.core.entities.equipamentos import Arma, Armadura, Escudo
from app.core.entities.habilidades_magias import Magia, Efeito
from app.controllers.game_controller import GameController
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB, EquipeMembroDB
from app.models.equipamentos_db import ItemDB
from app.models.habilidades_magias_db import MagiaDB, EfeitoDB


@pytest.fixture
def party_exemplo():
    raca = Raca(nome="Humano", bonus_atributos={"forca": 1, "agilidade": 1, "resistencia": 1, "percepcao": 1, "exuberancia": 1})
    classe_guerreiro = ClasseRPG(nome="Guerreiro", bonus_caminhos={"terra": 1})
    classe_mago = ClasseRPG(nome="Mago", bonus_caminhos={"fogo": 2})
    classe_clerigo = ClasseRPG(nome="Clérigo", bonus_caminhos={"luz": 2})
    classe_ladino = ClasseRPG(nome="Ladino", bonus_caminhos={"ar": 1})
    classe_paladino = ClasseRPG(nome="Paladino", bonus_caminhos={"luz": 1, "terra": 1})

    p1 = Personagem("Artorias", 2, raca, classe_guerreiro, 4, 3, 3, 2, 1)
    p2 = Personagem("Vivi", 2, raca, classe_mago, 1, 2, 2, 4, 5)
    p3 = Personagem("Aerith", 2, raca, classe_clerigo, 1, 3, 2, 4, 5)
    p4 = Personagem("Locke", 2, raca, classe_ladino, 2, 5, 2, 4, 2)
    p5 = Personagem("Cecil", 2, raca, classe_paladino, 4, 2, 4, 2, 3)

    return {"p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5}


class TestPartyDomain:
    """Testes da Entidade de Domínio Party (Equipe de até 4 membros)."""

    def test_criacao_party_vazia(self):
        party = Party()
        assert len(party) == 0
        assert party.esta_viva() is False
        assert len(party.reservas) == 0

    def test_adicao_ate_4_membros_ativos(self, party_exemplo):
        party = Party()
        assert party.adicionar_membro(party_exemplo["p1"]) is True
        assert party.adicionar_membro(party_exemplo["p2"]) is True
        assert party.adicionar_membro(party_exemplo["p3"]) is True
        assert party.adicionar_membro(party_exemplo["p4"]) is True
        assert len(party.membros) == 4
        assert len(party.reservas) == 0
        assert party.esta_viva() is True

    def test_adicao_alem_de_4_vai_para_reserva(self, party_exemplo):
        party = Party()
        party.adicionar_membro(party_exemplo["p1"])
        party.adicionar_membro(party_exemplo["p2"])
        party.adicionar_membro(party_exemplo["p3"])
        party.adicionar_membro(party_exemplo["p4"])
        
        # 5º membro deve ir para reservas
        assert party.adicionar_membro(party_exemplo["p5"]) is False
        assert len(party.membros) == 4
        assert len(party.reservas) == 1
        assert party.reservas[0].nome == "Cecil"

    def test_remover_membro_e_promover_reserva(self, party_exemplo):
        party = Party()
        party.adicionar_membro(party_exemplo["p1"])
        party.adicionar_membro(party_exemplo["p2"])
        party.adicionar_membro(party_exemplo["p3"])
        party.adicionar_membro(party_exemplo["p4"])
        party.adicionar_membro(party_exemplo["p5"])  # Reserva

        removido = party.remover_membro("Vivi")
        assert removido.nome == "Vivi"
        assert len(party.membros) == 4
        assert party.membros[-1].nome == "Cecil"  # Promovido da reserva
        assert len(party.reservas) == 0

    def test_trocar_posicoes_ativas(self, party_exemplo):
        party = Party([party_exemplo["p1"], party_exemplo["p2"]])
        assert party.membros[0].nome == "Artorias"
        assert party.membros[1].nome == "Vivi"
        
        assert party.trocar_posicoes_ativas(0, 1) is True
        assert party.membros[0].nome == "Vivi"
        assert party.membros[1].nome == "Artorias"

    def test_membros_vivos_e_esta_viva(self, party_exemplo):
        party = Party([party_exemplo["p1"], party_exemplo["p2"]])
        assert party.esta_viva() is True
        assert len(party.obter_membros_vivos()) == 2

        # Zera HP de um
        party_exemplo["p1"].pv_atual = 0
        assert party.esta_viva() is True
        assert len(party.obter_membros_vivos()) == 1

        # Zera HP de todos
        party_exemplo["p2"].pv_atual = 0
        assert party.esta_viva() is False
        assert len(party.obter_membros_vivos()) == 0


class TestInventarioIndividualPersonagem:
    """Testes de inventário próprio e individual por personagem."""

    def test_adicionar_e_remover_item_individual(self, party_exemplo):
        artorias = party_exemplo["p1"]
        assert artorias.obter_quantidade_item("Poção de Cura") == 0

        artorias.adicionar_item_inventario("Poção de Cura", 3)
        assert artorias.obter_quantidade_item("Poção de Cura") == 3

        sucesso = artorias.remover_item_inventario("Poção de Cura", 2)
        assert sucesso is True
        assert artorias.obter_quantidade_item("Poção de Cura") == 1

        sucesso_invalido = artorias.remover_item_inventario("Poção de Cura", 5)
        assert sucesso_invalido is False
        assert artorias.obter_quantidade_item("Poção de Cura") == 1

    def test_transferir_item_entre_membros_da_party(self, party_exemplo):
        party = Party([party_exemplo["p1"], party_exemplo["p2"]])
        p1 = party_exemplo["p1"]
        p2 = party_exemplo["p2"]

        p1.adicionar_item_inventario("Elixir", 2)
        assert p1.obter_quantidade_item("Elixir") == 2
        assert p2.obter_quantidade_item("Elixir") == 0

        sucesso = party.transferir_item(p1, p2, "Elixir", 1)
        assert sucesso is True
        assert p1.obter_quantidade_item("Elixir") == 1
        assert p2.obter_quantidade_item("Elixir") == 1


class TestAlistamentoEGameController:
    """Testes de persistência, alistamento e mapeamento no banco."""

    def test_seed_completo_dados_iniciais(self, test_db):
        resumo = GameController.garantir_dados_iniciais_completos(test_db)
        assert resumo["racas"] >= 6
        assert resumo["classes"] >= 6
        assert resumo["magias"] >= 10
        assert resumo["personagens"] >= 6

    def test_alistar_e_desalistar_personagem(self, test_db):
        GameController.garantir_dados_iniciais_completos(test_db)
        ctrl = GameController(test_db)

        personagens = ctrl.obter_personagens_recrutaveis()
        assert len(personagens) >= 6

        # Pega um personagem não alistado (Gimli ou Sylvanas)
        gimli = next(p for p in personagens if p.nome == "Gimli")
        
        # Alista Gimli
        sucesso_alistar = ctrl.alistar_personagem(gimli.id, slot=1)
        assert sucesso_alistar is True

        party = ctrl.obter_equipe_party()
        assert any(m.nome == "Gimli" for m in party.membros)

        # Desalista Gimli
        sucesso_desalistar = ctrl.desalistar_personagem(gimli.id)
        assert sucesso_desalistar is True

    def test_persistencia_inventario_individual_db(self, test_db):
        GameController.garantir_dados_iniciais_completos(test_db)
        ctrl = GameController(test_db)

        artorias_db = test_db.query(PersonagemDB).filter(PersonagemDB.nome == "Artorias").first()
        assert artorias_db is not None

        ctrl.adicionar_item_personagem_db(artorias_db.id, "Poção de Mana", 5)
        test_db.refresh(artorias_db)

        artorias_dom = GameController.converter_para_dominio(artorias_db)
        assert artorias_dom.obter_quantidade_item("Poção de Mana") == 5

        ctrl.remover_item_personagem_db(artorias_db.id, "Poção de Mana", 2)
        test_db.refresh(artorias_db)

        artorias_dom_atualizado = GameController.converter_para_dominio(artorias_db)
        assert artorias_dom_atualizado.obter_quantidade_item("Poção de Mana") == 3
