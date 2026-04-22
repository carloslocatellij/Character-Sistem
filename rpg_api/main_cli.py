import os
from app.db.database import SessionLocal, engine, Base
from app.controllers.game_controller import GameController as GC
from app.controllers.game_controller import simular_arena
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from rich.console import Console
from rich.prompt import Prompt,IntPrompt
from rich.table import Table
console = Console()
print = console.print

# Garante que as tabelas existem (útil para rodar o CLI a primeira vez)
Base.metadata.create_all(bind=engine)
barrinha = "="*40

def menu_criar_raca(db):
        print("\n--- 🧬 CRIAR NOVA RAÇA ---")
        nome = Prompt.ask("Nome da Raça: ")
        forca = IntPrompt.ask("Bônus de Força: ")
        agi = IntPrompt.ask("Bônus de Agilidade: ")
        res = IntPrompt.ask("Bônus de Resistência: ")
        perc =  IntPrompt.ask("Bônus de Percepção: ")
        exub =  IntPrompt.ask("Bônus de Exuberância: ")
        
        atributos = dict(forca= forca, agilidade=agi, resistencia=res, percepcao=perc, exuberancia=exub)
        
        print(GC.criar_raca(db, nome, atributos))
        
def menu_criar_classe(db):
        print("\n--- 📜 CRIAR NOVA CLASSE ---")
        nome = Prompt.ask("Nome da Classe: ")
        maximo_de_pontos = 2
        pontos_totais = 0
        lista_pontos = []
        caminhos =[]
        while pontos_totais < maximo_de_pontos:
            print(f"\nVocê tem {maximo_de_pontos - pontos_totais} pontos totais")
            caminho = Prompt.ask("Caminho de Magia Primário:" , choices=["fogo", "água", "ar", "terra",
                                                                        "sombra", "luz", "planta", "metal",
                                                                        "sangue"], default=None)
            if caminho == 'None':  break
            caminhos.append(caminho)
            try:
                pontos = IntPrompt.ask(f"Pontos no caminho {caminho}: (máximo: {maximo_de_pontos - pontos_totais}) ")
                lista_pontos.append(pontos)
                pontos_totais += pontos
            except:
                pontos = None
                
        print(GC.criar_classe(db, nome, caminhos, lista_pontos))
        
def menu_criar_personagem(db):
        print("\n--- 👤 CRIAR NOVO PERSONAGEM ---")
        racas = db.query(RacaDB).all()  # Lista Raças
        print("\nRaças disponíveis:")
        
        qnt_tabelas_racas = len(racas)/4
        for r in racas: 
            
            tabela_racas = Table("Raça", "ID")
            tabela_racas.add_row(f'{r.nome}', f'[blue]{r.id}')
        
        print(tabela_racas)
        
        raca_id = IntPrompt.ask("ID da Raça escolhida: ")

        # Lista Classes
        try:
            classes = db.query(ClasseRPGDB).all()
        except Exception as e:
            print(f"❌ Ocorreu um erro ao buscar as classes: {e}")
            return
        print("\nClasses disponíveis:")
        for c in classes: print(f"[{c.id}] {c.nome}")
        classe_id = IntPrompt.ask("ID da Classe escolhida: ")
        
        nome = input("\nNome do Personagem: ")
        forca = int(input("Força Base (0 a 5): "))
        agi = int(input("Agilidade Base (0 a 5): "))
        res = int(input("Resistência Base (0 a 5): "))
        perc = int(input("Percepção Base (0 a 5): "))
        exub = int(input("Exuberância Base (0 a 5): "))
        
        atributos = dict(forca= forca, agilidade=agi, resistencia=res, percepcao=perc, exuberancia=exub)
        
        print(GC.criar_personagem(db, nome, raca_id, classe_id, atributos))
        

def menu_equipar(ctrl: GC):
    print("\n--- 🗡️ EQUIPAR PERSONAGEM ---")
    chars = ctrl.db.query(PersonagemDB).all()
    for p in chars: print(f"[{p.id}] {p.nome}")
    char_id = int(input("ID do Personagem: "))
    
    itens = ctrl.db.query(ItemDB).all()
    for i in itens: print(f"[{i.id}] {i.nome} ({i.categoria})")
    item_id = int(input("ID do Item: "))
    
    slot = input("Slot (direita/esquerda/armadura): ").lower()
    print(ctrl.equipar_item(char_id, item_id, slot))
    
def menu_criar_item(db):
    print("\n--- ⛏ CRIAR NOVO ITEM ---")
    print("--- PRIMEIRO DEFINA A CATEGORIA DO ITEM --- ")
    print(barrinha)
    print("1. Arma ⚔")
    print("2. Armadura 🤺")
    print("3. Escudo 🛡")
    print("4. Outros 🌡")
    print("5. Voltar")
    
    escolha = input("Escolha uma opção: ")
    try:
        if escolha == '1': 
            item_categoria = 'arma'
            item_defesa = None
        elif escolha == '2':
            item_categoria = 'armadura'
            item_dano = tipo_ataque = None
        elif escolha == '3':
            item_categoria = 'escudo'
            item_dano = tipo_ataque = None
        elif escolha == '4':
            item_categoria = item_dano = item_defesa = tipo_ataque = None
        elif escolha == '5': 
            print("Tentando voltar...")
            return
        else:
            print("⚠️ Opção inválida!")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")
        db.rollback()
        
    print("--- DEFINA OS ATRIBUTOS DO ITEM --- ")
    item_nome = input("Nome para o novo item: ")
    item_emoji = input("Defina um emoji (tecla win + . no janelas).")
    if item_categoria == 'arma':
        escolha2 = None
        while escolha2 not in ['1', '2']:
            print("Tipo de ataque da arma (corpo / distâcia):")
            print("1. Corpo-a-Corpo ⚔")
            print("2. Distância 🏹")
            escolha2 = input("Escolha uma opção: ")
            if escolha2 == '1': tipo_ataque = 'corpo'
            elif escolha2 == '2': tipo_ataque = 'distancia'
            else: print("⚠️ Opção inválida!") 
        item_dano = int(input("Digite o valor para o dano da arma:"))
    elif item_categoria == 'armadura':
        item_defesa = int(input("Digite o valor para a defesa da armadura:"))
    elif item_categoria == 'escudo':
        item_defesa = int(input("Digite o valor para a defesa do escudo:"))
    else:
        pass
        
    print(GC.criar_item(db, item_nome, item_categoria, item_emoji,
                        item_dano or None, tipo_ataque or None, item_defesa or None))
    

def menu_arena(db):
    print("\n--- ⚔️ ARENA DE SIMULAÇÃO ---")
    aliados = oponentes = None
    
    while aliados == None and oponentes == None:
        while aliados == None:
            print(" -- MONTE A SUA EQUIPE DE ALIADOS --")
            personagens = db.query(PersonagemDB).all()
            print([f"{p.nome} -ID:[{p.id}]" for p in personagens])
            
            #TODO: Necessário tratar inputs 
            aliados = [int(i.strip()) for i in input("IDs Aliados (ex: 1,2): ").split(",")]
            
        while oponentes == None:
            
            #TODO: Necessário tratar inputs 
            oponentes = [int(i.strip()) for i in input("IDs Oponentes (ex: 3,4): ").split(",")]
            
            
    qtd = int(input("Quantidade de batalhas (1 para detalhado): "))
    
    resultado = simular_arena(db, aliados, oponentes, qtd)
    
    if qtd == 1:
        print(f"\n🏆 Vencedor: {resultado['vencedor']}")
        return
    else:
        print(f"\n📊 Resultados de {qtd} batalhas:")
        print(f"Aliados: {resultado['vitorias_aliados']} vitórias")
        print(f"Oponentes: {resultado['vitorias_oponentes']} vitórias")
        return

# ==========================================
# LOOP PRINCIPAL DO PROGRAMA
# ==========================================
def main():
    db = SessionLocal()
    while True:

        print(barrinha)
        print("🛡️ GERENCIADOR DE RPG DE MESA 🛡️")
        print(barrinha)
        
        print("1. Criar Raça")
        print("2. Criar Classe")
        print("3. Criar Personagem")
        print("4. Criar Item")
        print("5. Equipar Item")
        print("6. Simular Batalha na Arena")
        print("7. Sair")
        
        escolha = IntPrompt.ask("Escolha uma opção: ")
        
        try:
            if escolha == 1: menu_criar_raca(db)
            elif escolha == 2: menu_criar_classe(db)
            elif escolha == 3: menu_criar_personagem(db)
            elif escolha == 4: menu_criar_item(db)
            elif escolha == 5: menu_equipar(GC(db))
            elif escolha == 6: menu_arena(db)
            elif escolha == 7:
                print("Encerrando o sistema...")
                break
            else:
                print("⚠️ Opção inválida!")
        except Exception as e:
            print(f"❌ Ocorreu um erro: {e}")
            db.rollback() # Previne que o banco trave em caso de erro de input

    db.close()

if __name__ == "__main__":
    main()