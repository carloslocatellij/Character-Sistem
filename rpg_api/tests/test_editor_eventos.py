import pytest
from app.views.map_manager_screen import MapManagerScreen

@pytest.fixture
def editor_vazio():
    return MapManagerScreen()

def test_adicionar_evento_na_memoria(editor_vazio):
    """Garante que o editor consegue registar um evento complexo na coordenada correta."""
    # Simula a adição de um evento na Linha 5, Coluna 10 (y=5, x=10)
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
    assert registo["pos_y"] == 2 # Linha
    assert registo["pos_x"] == 3 # Coluna
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