from app.db.database import Base, engine, SessionLocal
from app.models.personagens_db import RacaDB, ClasseRPGDB, PersonagemDB
from app.models.equipamentos_db import ItemDB # NOVO IMPORT NECESSÁRIO


def setup_module(module):
    """Cria as tabelas no banco de teste antes de rodar."""
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    """Limpa o banco de teste depois de rodar."""
    Base.metadata.drop_all(bind=engine)

def test_criar_personagem_com_relacionamentos():
    db = SessionLocal()
    
    # 1. Criamos e salvamos uma Raça
    raca_orc = RacaDB(nome="orco", bonus_atributos={"forca": 2, "agilidade": -1})
    db.add(raca_orc)
    
    # 2. Criamos e salvamos uma Classe
    classe_barbaro = ClasseRPGDB(nome="Bárbaro", bonus_caminhos={"terra": 1}, habilidades=["Fúria"])
    db.add(classe_barbaro)
    
    # Precisamos fazer o "commit" e "refresh" (ou "flush") para que o banco gere os IDs reais (id=1, etc)
    db.commit()
    db.refresh(raca_orc)
    db.refresh(classe_barbaro)
    
    # 3. Criamos o Personagem vinculando os IDs!
    thrall = PersonagemDB(
        nome="Thrall",
        nivel=3,
        raca_id=raca_orc.id,
        classe_id=classe_barbaro.id,
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
    # Vamos buscar o personagem pelo nome
    personagem_salvo = db.query(PersonagemDB).filter(PersonagemDB.nome == "Thrall").first()
    
    # Validamos os dados básicos
    assert personagem_salvo is not None
    assert personagem_salvo.nivel == 3
    
    # Validamos a MÁGICA DOS RELACIONAMENTOS:
    # O SQLAlchemy buscou automaticamente a raça e a classe vinculadas!
    assert personagem_salvo.raca.nome == "orco"
    assert personagem_salvo.raca.bonus_atributos["forca"] == 2
    
    assert personagem_salvo.classe.nome == "Bárbaro"
    assert personagem_salvo.classe.bonus_caminhos["terra"] == 1
    
    db.close()
    
def test_personagem_com_equipamentos():
    db = SessionLocal()
    
    # 1. Criamos a Base (Raça e Classe)
    raca = RacaDB(nome="Humane")
    classe = ClasseRPGDB(nome="Warriore", bonus_caminhos={}, habilidades=None)
    db.add_all([raca, classe])
    db.commit()
    
    # 2. Forjamos as armas e armaduras no banco
    espada = ItemDB(nome="Espada de Aço", categoria="arma", dano=5, emoji="🗡️")
    escudo = ItemDB(nome="Escudo de Madeira", categoria="escudo", defesa=2, emoji="🛡️")
    db.add_all([espada, escudo])
    db.commit()
    
    # Atualizamos os objetos para pegar os IDs gerados pelo banco
    db.refresh(raca)
    db.refresh(classe)
    db.refresh(espada)
    db.refresh(escudo)
    
    # 3. Criamos o Herói e equipamos os itens através dos IDs
    heroi = PersonagemDB(
        nome="Arthur",
        nivel=5,
        raca_id=raca.id,
        classe_id=classe.id,
        mao_direita_id=espada.id,
        mao_esquerda_id=escudo.id
    )
    db.add(heroi)
    db.commit()
    
    # ==========================================
    # 4. A HORA DA VERDADE
    # ==========================================
    # Buscamos o Arthur no banco para ver se ele está armado
    arthur_salvo = db.query(PersonagemDB).filter(PersonagemDB.nome == "Arthur").first()
    
    assert arthur_salvo is not None
    assert arthur_salvo.mao_direita is not None
    assert arthur_salvo.mao_direita.nome == "Espada de Aço"
    assert arthur_salvo.mao_esquerda.defesa == 2 # Lendo os status do escudo!
    assert arthur_salvo.armadura_equipada is None # Não equipamos armadura, deve ser None
    
    db.close()