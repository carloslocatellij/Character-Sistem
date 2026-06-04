from app.core.entities.equipamentos import Item, Arma, Armadura, Escudo

def test_criacao_item_basico():
    """Testa se um item genérico é criado com os valores corretos."""
    pocao = Item(nome="Poção de Cura", peso=0.5, emoji="🧪")
    
    assert pocao.nome == "Poção de Cura"
    assert pocao.peso == 0.5
    assert pocao.emoji == "🧪"

def test_criacao_arma():
    """Testa a herança da classe Arma e suas propriedades específicas."""
    espada = Arma(nome="Espada Longa", peso=2.0, dano=5, tipo="corpo", emoji="🗡️")
    
    # Testa atributos herdados
    assert espada.nome == "Espada Longa"
    assert espada.peso == 2.0
    # Testa atributos específicos
    assert espada.dano == 5
    assert espada.tipo == "corpo"

def test_criacao_armadura_e_escudo():
    """Testa a herança e atributos de equipamentos defensivos."""
    cota_malha = Armadura(nome="Cota de Malha", peso=10.0, defesa=3)
    escudo_madeira = Escudo(nome="Escudo de Madeira", peso=3.0, defesa_extra=2)
    
    # Armadura
    assert cota_malha.nome == "Cota de Malha"
    assert cota_malha.defesa == 3
    assert cota_malha.emoji == "🦺" # Valor padrão herdado
    
    # Escudo
    assert escudo_madeira.defesa_extra == 2
    assert escudo_madeira.emoji == "🛡️"