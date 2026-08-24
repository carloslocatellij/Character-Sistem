import random
from app.db.database import Base, engine, SessionLocal, garantir_schema_atualizado
from app.models.personagens_db import RacaDB, ClasseRPGDB, PersonagemDB
from app.models.equipamentos_db import ItemDB


def setup_module(module):
    """Cria as tabelas no banco de teste antes de rodar."""
    garantir_schema_atualizado(engine)

def teardown_module(module):
    """Limpa o banco de teste depois de rodar."""
    db = SessionLocal()
    try:
        db.query(PersonagemDB).delete()
        db.query(ItemDB).delete()
        db.query(ClasseRPGDB).delete()
        db.query(RacaDB).delete()
        db.commit()
    except Exception:
        pass
    finally:
        db.close()

def test_criar_personagem_com_relacionamentos():
    db = SessionLocal()
    rand_sufixo = random.randint(1000, 99999)
    
    # 1. Criamos e salvamos uma Raça
    nome_raca = f"orco_{rand_sufixo}"
    raca_orc = RacaDB(nome=nome_raca, bonus_atributos={"forca": 2, "agilidade": -1})
    db.add(raca_orc)
    
    # 2. Criamos e salvamos uma Classe
    nome_classe = f"Barbaro_{rand_sufixo}"
    classe_barbaro = ClasseRPGDB(nome=nome_classe, bonus_caminhos={"terra": 1}, habilidades=["Fúria"])
    db.add(classe_barbaro)
    
    db.commit()
    db.refresh(raca_orc)
    db.refresh(classe_barbaro)
    
    # 3. Criamos o Personagem vinculando os IDs!
    nome_personagem = f"Thrall_{rand_sufixo}"
    thrall = PersonagemDB(
        nome=nome_personagem,
        nivel=3,
        raca_id=raca_orc.id,
        classe_id=classe_barbaro.id,
        usuario_id=None,
        cenario_id=None,
        forca_base=3,
        agilidade_base=2,
        resistencia_base=4,
        percepcao_base=1,
        exuberancia_base=2
    )
    db.add(thrall)
    db.commit()
    
    # ==========================================
    # 4. A HORA DA VERDADE: CONSULTANDO O BANCO
    # ==========================================
    personagem_salvo = db.query(PersonagemDB).filter(PersonagemDB.nome == nome_personagem).first()
    
    # Validamos os dados básicos
    assert personagem_salvo is not None
    assert personagem_salvo.nivel == 3
    
    # Validamos os relacionamentos
    assert personagem_salvo.raca.nome == nome_raca
    assert personagem_salvo.raca.bonus_atributos["forca"] == 2
    
    assert personagem_salvo.classe.nome == nome_classe
    assert personagem_salvo.classe.bonus_caminhos["terra"] == 1
    
    db.close()
    
def test_personagem_com_equipamentos():
    db = SessionLocal()
    rand_sufixo = random.randint(1000, 99999)
    
    # 1. Criamos a Base (Raça e Classe)
    raca = RacaDB(nome=f"Humane_{rand_sufixo}")
    classe = ClasseRPGDB(nome=f"Warriore_{rand_sufixo}", bonus_caminhos={}, habilidades=None)
    db.add_all([raca, classe])
    db.commit()
    
    # 2. Forjamos as armas e armaduras no banco
    espada = ItemDB(nome=f"Espada de Aço {rand_sufixo}", categoria="arma", dano=5, emoji="🗡️")
    escudo = ItemDB(nome=f"Escudo de Madeira {rand_sufixo}", categoria="escudo", defesa=2, emoji="🛡️")
    db.add_all([espada, escudo])
    db.commit()
    
    # Atualizamos os objetos para pegar os IDs gerados pelo banco
    db.refresh(raca)
    db.refresh(classe)
    db.refresh(espada)
    db.refresh(escudo)
    
    # 3. Criamos o Herói e equipamos os itens através dos IDs
    nome_heroi = f"Arthur_{rand_sufixo}"
    heroi = PersonagemDB(
        nome=nome_heroi,
        nivel=5,
        raca_id=raca.id,
        usuario_id=None,
        cenario_id=None,
        classe_id=classe.id,
        mao_direita_id=espada.id,
        mao_esquerda_id=escudo.id
    )
    db.add(heroi)
    db.commit()
    
    # ==========================================
    # 4. A HORA DA VERDADE
    # ==========================================
    arthur_salvo = db.query(PersonagemDB).filter(PersonagemDB.nome == nome_heroi).first()
    
    assert arthur_salvo is not None
    assert arthur_salvo.mao_direita is not None
    assert arthur_salvo.mao_direita.nome == f"Espada de Aço {rand_sufixo}"
    assert arthur_salvo.mao_esquerda.defesa == 2
    assert arthur_salvo.armadura_equipada is None
    
    db.close()