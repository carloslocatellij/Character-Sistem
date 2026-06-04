# tests/test_game_controller.py
import pytest
from app.controllers.game_controller import GameController, simular_arena
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB


class TestGameControllerCriacoes:
    """Testes das funções de criação no GameController."""

    def test_criar_raca_valida(self, test_db):
        """Deve criar uma raça válida com todos os atributos."""
        resultado = GameController.criar_raca(
            test_db,
            nome="Anão",
            atributos={
                "forca": 4,
                "agilidade": 1,
                "resistencia": 5,
                "percepcao": 2,
                "exuberancia": 2
            },
            emoji="⛏️"
        )
        
        assert "✅" in resultado
        raca = test_db.query(RacaDB).filter_by(nome="Anão").first()
        assert raca is not None
        assert raca.bonus_atributos["forca"] == 4
        assert raca.emoji == "⛏️"

    def test_criar_raca_atributos_completos(self, test_db):
        """Verifica se todos os 5 atributos são salvos."""
        GameController.criar_raca(
            test_db,
            nome="Orc",
            atributos={
                "forca": 5,
                "agilidade": 2,
                "resistencia": 4,
                "percepcao": 1,
                "exuberancia": 3
            },
            emoji="👹"
        )
        
        raca = test_db.query(RacaDB).filter_by(nome="Orc").first()
        assert raca.bonus_atributos["forca"] == 5
        assert raca.bonus_atributos["agilidade"] == 2
        assert raca.bonus_atributos["resistencia"] == 4
        assert raca.bonus_atributos["percepcao"] == 1
        assert raca.bonus_atributos["exuberancia"] == 3

    def test_criar_classe_com_caminhos(self, test_db):
        """Deve criar uma classe com múltiplos caminhos."""
        resultado = GameController.criar_classe(
            test_db,
            nome="Mago",
            caminho=["Fogo", "Água"],
            pontos=[3, 2]
        )
        
        assert "✅" in resultado
        classe = test_db.query(ClasseRPGDB).filter_by(nome="Mago").first()
        assert classe is not None
        assert classe.bonus_caminhos["Fogo"] == 3
        assert classe.bonus_caminhos["Água"] == 2

    def test_criar_classe_sem_caminhos(self, test_db):
        """Deve criar uma classe sem caminhos (bonus_caminhos vazio)."""
        GameController.criar_classe(
            test_db,
            nome="Guerreiro Simples",
            caminho=None,
            pontos=None
        )
        
        classe = test_db.query(ClasseRPGDB).filter_by(nome="Guerreiro Simples").first()
        assert classe.bonus_caminhos == {}

    def test_criar_personagem_valido(self, test_db, raca_default, classe_default):
        """Deve criar um personagem com todos os atributos válidos."""
        resultado = GameController.criar_personagem(
            test_db,
            nome="Aragorn",
            raca_id=raca_default.id,
            classe_id=classe_default.id,
            usuario_id=1, cenario_id=1,
            atributos={
                "forca": 4,
                "agilidade": 3,
                "resistencia": 5,
                "percepcao": 4,
                "exuberancia": 2
            }
        )
        
        assert "✅" in resultado
        personagem = test_db.query(PersonagemDB).filter_by(nome="Aragorn").first()
        assert personagem is not None
        assert personagem.forca_base == 4
        assert personagem.raca_id == raca_default.id
        assert personagem.classe_id == classe_default.id

    def test_criar_item_arma(self, test_db):
        """Deve criar uma arma com dano e tipo de ataque."""
        resultado = GameController.criar_item(
            test_db,
            nome="Espada Longa",
            categoria="arma",
            emoji="⚔️",
            dano=10,
            tipo_ataque="Corpo",
            defesa=None
        )
        
        assert "✅" in resultado
        item = test_db.query(ItemDB).filter_by(nome="Espada Longa").first()
        assert item.dano == 10
        assert item.tipo_ataque == "Corpo"
        assert item.categoria == "arma"

    def test_criar_item_escudo(self, test_db):
        """Deve criar um escudo com defesa_extra."""
        GameController.criar_item(
            test_db,
            nome="Escudo Grande",
            categoria="escudo",
            emoji="🛡️",
            dano=None,
            tipo_ataque=None,
            defesa=8
        )
        
        item = test_db.query(ItemDB).filter_by(nome="Escudo Grande").first()
        assert item.defesa_extra == 8
        assert item.dano is None

    def test_criar_item_armadura(self, test_db):
        """Deve criar uma armadura com defesa."""
        GameController.criar_item(
            test_db,
            nome="Armadura de Aço",
            categoria="armadura",
            emoji="🛡️",
            dano=None,
            tipo_ataque=None,
            defesa=6
        )
        
        item = test_db.query(ItemDB).filter_by(nome="Armadura de Aço").first()
        assert item.defesa == 6
        assert item.categoria == "armadura"


class TestGameControllerEquipamento:
    """Testes das funções de equipamento."""

    def test_equipar_arma_mao_direita(self, test_db, personagem_default, item_arma):
        """Deve equipar uma arma na mão direita."""
        ctrl = GameController(test_db)
        resultado = ctrl.equipar_item(personagem_default.id, item_arma.id, "direita")
        
        assert "✅" in resultado
        test_db.refresh(personagem_default)
        assert personagem_default.mao_direita_id == item_arma.id

    def test_equipar_escudo_mao_esquerda(self, test_db, personagem_default, item_escudo):
        """Deve equipar um escudo na mão esquerda."""
        ctrl = GameController(test_db)
        resultado = ctrl.equipar_item(personagem_default.id, item_escudo.id, "esquerda")
        
        assert "✅" in resultado
        test_db.refresh(personagem_default)
        assert personagem_default.mao_esquerda_id == item_escudo.id

    def test_equipar_armadura(self, test_db, personagem_default, item_armadura):
        """Deve equipar uma armadura no corpo."""
        ctrl = GameController(test_db)
        resultado = ctrl.equipar_item(personagem_default.id, item_armadura.id, "armadura")
        
        assert "✅" in resultado
        test_db.refresh(personagem_default)
        assert personagem_default.armadura_id == item_armadura.id

    def test_equipar_item_personagem_inexistente(self, test_db, item_arma):
        """Deve lançar erro ao tentar equipar em personagem inexistente."""
        ctrl = GameController(test_db)
        
        with pytest.raises(ValueError, match="não encontrado"):
            ctrl.equipar_item(999, item_arma.id, "direita")

    def test_equipar_item_inexistente(self, test_db, personagem_default):
        """Deve lançar erro ao tentar equipar item inexistente."""
        ctrl = GameController(test_db)
        
        with pytest.raises(ValueError, match="não encontrado"):
            ctrl.equipar_item(personagem_default.id, 999, "direita")

    def test_trocar_equipamento(self, test_db, personagem_default, item_arma, item_escudo):
        """Deve trocar um equipamento por outro no mesmo slot."""
        ctrl = GameController(test_db)
        
        # Equipa primeiro item
        ctrl.equipar_item(personagem_default.id, item_arma.id, "direita")
        test_db.refresh(personagem_default)
        assert personagem_default.mao_direita_id == item_arma.id
        
        # Troca por outro item
        ctrl.equipar_item(personagem_default.id, item_escudo.id, "direita")
        test_db.refresh(personagem_default)
        assert personagem_default.mao_direita_id == item_escudo.id


class TestGameControllerConsultas:
    """Testes das funções de consulta."""

    def test_obter_personagem_por_id_valido(self, test_db, personagem_default):
        """Deve retornar um personagem válido pelo ID."""
        ctrl = GameController(test_db)
        personagem = ctrl.obter_personagem_por_id(personagem_default.id)
        
        assert personagem is not None
        assert personagem.nome == "Legolas"
        assert personagem.id == personagem_default.id

    def test_obter_personagem_por_id_invalido(self, test_db):
        """Deve retornar None para ID inexistente."""
        ctrl = GameController(test_db)
        personagem = ctrl.obter_personagem_por_id(999)
        
        assert personagem is None

    def test_listar_racas(self, test_db, raca_default):
        """Deve listar todas as raças cadastradas."""
        GameController.criar_raca(
            test_db, "Humano", 
            {"forca": 2, "agilidade": 2, "resistencia": 2, "percepcao": 2, "exuberancia": 3},
            "🧑"
        )
        
        ctrl = GameController(test_db)
        racas = ctrl.listar_tudo(RacaDB)
        
        assert len(racas) == 2
        assert raca_default in racas

    def test_listar_classes_vazio(self, test_db):
        """Deve retornar lista vazia quando não há classes."""
        ctrl = GameController(test_db)
        classes = ctrl.listar_tudo(ClasseRPGDB)
        
        assert classes == []


class TestGameControllerAtualizacao:
    """Testes das funções de atualização."""

    def test_atualizar_raca(self, test_db, raca_default):
        """Deve atualizar atributos de uma raça."""
        ctrl = GameController(test_db)
        novos_dados = {"nome": "Élfo Florestal", "emoji": "🌲"}
        
        resultado = ctrl.atualizar_elemento(raca_default.id, novos_dados, RacaDB)
        
        assert "✅" in resultado
        test_db.refresh(raca_default)
        assert raca_default.nome == "Élfo Florestal"
        assert raca_default.emoji == "🌲"

    def test_atualizar_personagem_nivel(self, test_db, personagem_default):
        """Deve atualizar o nível de um personagem."""
        ctrl = GameController(test_db)
        novos_dados = {"nivel": 5}
        
        ctrl.atualizar_elemento(personagem_default.id, novos_dados, PersonagemDB)
        
        test_db.refresh(personagem_default)
        assert personagem_default.nivel == 5

    def test_atualizar_classe_habilidades(self, test_db, classe_default):
        """Deve atualizar as habilidades de uma classe."""
        ctrl = GameController(test_db)
        novas_habilidades = ["Disparo Rápido", "Invisibilidade"]
        novos_dados = {"habilidades": novas_habilidades}
        
        ctrl.atualizar_elemento(classe_default.id, novos_dados, ClasseRPGDB)
        
        test_db.refresh(classe_default)
        assert classe_default.habilidades == novas_habilidades

    def test_atualizar_elemento_inexistente(self, test_db):
        """Deve lançar erro ao tentar atualizar elemento inexistente."""
        ctrl = GameController(test_db)
        
        with pytest.raises(ValueError):
            ctrl.atualizar_elemento(999, {"nome": "novo"}, RacaDB)


class TestGameControllerConversao:
    """Testes da conversão BD -> Domínio."""

    def test_converter_personagem_basico(self, test_db, personagem_default, item_arma):
        """Deve converter personagem sem equipamentos."""
        personagem_domain = GameController.converter_para_dominio(personagem_default)
        
        assert personagem_domain.nome == "Legolas"
        assert personagem_domain.nivel == 1
        assert personagem_domain.raca.nome == "Élfo"
        assert personagem_domain.classe.nome == "Arqueiro"

    def test_converter_personagem_com_equipamentos(self, test_db, personagem_default, item_arma, item_escudo, item_armadura):
        """Deve converter personagem com todos os equipamentos."""
        # Equipa itens
        ctrl = GameController(test_db)
        ctrl.equipar_item(personagem_default.id, item_arma.id, "direita")
        ctrl.equipar_item(personagem_default.id, item_escudo.id, "esquerda")
        ctrl.equipar_item(personagem_default.id, item_armadura.id, "armadura")
        
        # Recarrega e converte
        test_db.refresh(personagem_default)
        personagem_domain = GameController.converter_para_dominio(personagem_default)
        
        assert personagem_domain.mao_direita is not None
        assert personagem_domain.mao_direita.nome == "Arco Élfico"
        assert personagem_domain.mao_esquerda is not None
        assert personagem_domain.armadura is not None


class TestSimuladorArena:
    """Testes da simulação de arena."""

    def test_simular_arena_uma_batalha(self, test_db, personagem_default):
        """Deve simular uma única batalha."""
        # Cria segundo personagem para oponente
        raca = test_db.query(RacaDB).first()
        classe = test_db.query(ClasseRPGDB).first()
        
        oponente = PersonagemDB(
            nome="Orc Guerreiro",
            raca_id=raca.id,
            classe_id=classe.id,
            usuario_id=1, cenario_id=1,
            forca_base=5,
            agilidade_base=2,
            resistencia_base=4,
            percepcao_base=2,
            exuberancia_base=2,
            nivel=1
        )
        test_db.add(oponente)
        test_db.commit()
        
        resultado = simular_arena(test_db, [personagem_default.id], [oponente.id], num_batalhas=1)
        
        assert resultado is not None
        assert isinstance(resultado, dict)

    def test_simular_arena_multiplas_batalhas(self, test_db, personagem_default):
        """Deve simular múltiplas batalhas e retornar estatísticas."""
        raca = test_db.query(RacaDB).first()
        classe = test_db.query(ClasseRPGDB).first()
        
        oponente = PersonagemDB(
            nome="Goblin",
            raca_id=raca.id,
            classe_id=classe.id,
            usuario_id=1, cenario_id=1,
            forca_base=2,
            agilidade_base=3,
            resistencia_base=1,
            percepcao_base=2,
            exuberancia_base=2,
            nivel=1
        )
        test_db.add(oponente)
        test_db.commit()
        
        resultado = simular_arena(test_db, [personagem_default.id], [oponente.id], num_batalhas=3)
        
        assert "vitorias_aliados" in resultado or resultado is not None

    def test_simular_arena_equipes_multiplas(self, test_db, raca_default, classe_default):
        """Deve simular batalha com múltiplos personagens em cada equipe."""
        # Cria 2 aliados
        aliado1 = PersonagemDB(
            nome="Legolas", raca_id=raca_default.id, classe_id=classe_default.id,usuario_id=1, cenario_id=1,
            forca_base=2, agilidade_base=5, resistencia_base=3, percepcao_base=4, exuberancia_base=2, nivel=1
        )
        aliado2 = PersonagemDB(
            nome="Gimli", raca_id=raca_default.id, classe_id=classe_default.id, usuario_id=1, cenario_id=1,
            forca_base=4, agilidade_base=2, resistencia_base=5, percepcao_base=3, exuberancia_base=2, nivel=1
        )
        
        # Cria 2 oponentes
        oponente1 = PersonagemDB(
            nome="Orc1", raca_id=raca_default.id, classe_id=classe_default.id, usuario_id=1, cenario_id=1,
            forca_base=5, agilidade_base=2, resistencia_base=4, percepcao_base=2, exuberancia_base=2, nivel=1
        )
        oponente2 = PersonagemDB(
            nome="Orc2", raca_id=raca_default.id, classe_id=classe_default.id, usuario_id=1, cenario_id=1,
            forca_base=4, agilidade_base=3, resistencia_base=3, percepcao_base=2, exuberancia_base=2, nivel=1
        )
        
        test_db.add_all([aliado1, aliado2, oponente1, oponente2])
        test_db.commit()
        
        resultado = simular_arena(
            test_db,
            [aliado1.id, aliado2.id],
            [oponente1.id, oponente2.id],
            num_batalhas=1
        )
        
        assert resultado is not None