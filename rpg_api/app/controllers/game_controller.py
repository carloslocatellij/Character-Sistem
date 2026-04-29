from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from app.core.personagens import Personagem, Raca, ClasseRPG
from app.core.simulador import SimuladorCombate
from app.core.equipamentos import Arma, Armadura, Escudo

from app.models.mapas_db import MapaDB
from app.core.mapas import GestorDeMapas

class GameController:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # TRADUTOR (MAPPER): BANCO DE DADOS -> DOMÍNIO
    # ==========================================
    def converter_para_dominio(db_char: PersonagemDB) -> Personagem:
        """Converte um modelo do SQLAlchemy para a Entidade pura do RPG."""
        # 1. Recria a Raça do Domínio
        raca_domain = Raca(nome=db_char.raca.nome, bonus_atributos=db_char.raca.bonus_atributos)
        
        # 2. Recria a Classe do Domínio
        classe_domain = ClasseRPG(
            nome=db_char.classe.nome, 
            bonus_caminhos=db_char.classe.bonus_caminhos,
            habilidades=db_char.classe.habilidades,
            #bonus_atributos=db_char.classe.bonus_atributos
        )
        
        # 3. Recria o Personagem
        personagem = Personagem(
            nome=db_char.nome,
            nivel=db_char.nivel,
            raca=raca_domain,
            classe_rpg=classe_domain,
            forca_base=db_char.forca_base,
            agilidade_base=db_char.agilidade_base,
            res_base=db_char.resistencia_base,
            perc_base=db_char.percepcao_base,
            exub_base=db_char.exuberancia_base
        )
        # Equipar itens se existirem no banco
        if db_char.mao_direita:
            personagem.mao_direita = Arma(db_char.mao_direita.nome, db_char.mao_direita.dano, db_char.mao_direita.tipo_ataque)
        if db_char.mao_esquerda:
            item = db_char.mao_esquerda
            if item.categoria == "escudo":
                personagem.mao_esquerda = Escudo(item.nome, item.defesa)
            else:
                personagem.mao_esquerda = Arma(item.nome, item.dano, item.tipo_ataque)
        if db_char.armadura_equipada:
            personagem.armadura = Armadura(db_char.armadura_equipada.nome, db_char.armadura_equipada.defesa)
        
        return personagem
    
    
    def equipar_item(self, personagem_id: int, item_id: int, slot: str):
        """
        Equipa um item em um slot específico: 'direita', 'esquerda', 'armadura'.
        """
        personagem = self.db.query(PersonagemDB).get(personagem_id)
        item = self.db.query(ItemDB).get(item_id)
        
        if not personagem or not item:
            raise ValueError("Personagem ou Item não encontrado.")

        if slot == 'direita': personagem.mao_direita_id = item.id
        elif slot == 'esquerda': personagem.mao_esquerda_id = item.id
        elif slot == 'armadura': personagem.armadura_id = item.id
        
        self.db.commit()
        return f"✅ {item.nome} equipado em {personagem.nome} ({slot})."

    # ==========================================
    # FUNÇÕES DE INTERAÇÃO DO CLI
    # ==========================================

    def criar_raca(db, nome, atributos, emoji):

        nova_raca = RacaDB(nome=nome, bonus_atributos={"forca": atributos.get('forca'),
                                                    "agilidade": atributos.get('agilidade'),
                                                    "resistencia":atributos.get('resistencia') ,
                                                    "percepcao" : atributos.get('percepcao'),
                                                    "exuberancia": atributos.get('exuberancia')},
                           emoji=emoji)
        try:
            db.add(nova_raca)
            db.commit()
            return f"✅ Raça '{nome}' salva com sucesso no Banco de Dados!"
        except Exception as e:
            return f"Não foi possível registrar a raça devido ao ERRO: {e}"
        

    def criar_classe(db, nome, caminho, pontos):
        if caminho == None or pontos == None:
            bonus_caminhos = {}
        else:
            bonus_caminhos = {caminho: pontos for caminho, pontos in zip(caminho, pontos)}
            
        nova_classe = ClasseRPGDB(nome=nome, bonus_caminhos=bonus_caminhos, habilidades=[])
        try:
            db.add(nova_classe)
            db.commit()
            return f"✅ Classe '{nome}' salva com sucesso no Banco de Dados!"
        except Exception as e:
            return f"Não foi possível registrar a classe devido ao ERRO: {e}"
        

    def criar_personagem(db, nome, raca_id, classe_id, atributos):
        novo_personagem = PersonagemDB(
            nome=nome, raca_id=raca_id, classe_id=classe_id,
            forca_base=atributos.get('forca'),
            agilidade_base=atributos.get('agilidade'),
            resistencia_base=atributos.get('resistencia'),
            percepcao_base=atributos.get('percepcao'),
            exuberancia_base=atributos.get('exuberancia'))
        
        try:
            db.add(novo_personagem)
            db.commit()
            return f"✅ Personagem '{nome}' forjado e salvo com sucesso no Banco de Dados!"
        except Exception as e:
            return f"Não foi possível registrar o personagem devido ao ERRO: {e}"
        
    
    def criar_item(db, nome, categoria, emoji, dano=None, tipo_ataque=None, defesa=None,peso=1):
        if dano: dano = int(dano)
        if defesa: defesa = int(defesa)
        
        novo_item = ItemDB(nome=nome,
                           categoria=categoria,
                           peso=peso,
                           emoji=emoji,
                           dano=dano,
                           tipo_ataque=tipo_ataque,
                           defesa=defesa,
                           defesa_extra=defesa if categoria == "escudo" else None
                           )
        try:
            db.add(novo_item)
            db.commit()
            return f"✅ Item '{nome}' forjado e salvo com sucesso no Banco de Dados!"
        except Exception as e:
            return f"Não foi possível registrar o item devido ao ERRO: {e}"
        
        
    def obter_personagem_por_id(self, p_id: int):
            return self.db.query(PersonagemDB).get(p_id)
        
    
    def atualizar_elemento(self,  el_id:int, dados:dict, model):
        elemento = self.db.query(model).get(el_id)
        if not elemento:
            raise ValueError(f"{elemento} não encontrado.")
        
        for chave, valor in dados.items():
            try:
                setattr(elemento, chave, valor) 
            except Exception as e:
                raise ValueError(f" ERRO: {e}")
            
        self.db.commit()
        return f"✅  atualizado com sucesso!"
    

    def listar_tudo(self, modelo):
        """Método genérico para listar registros (RacaDB, ClasseRPGDB, etc)"""
        return self.db.query(modelo).all()


def simular_arena(db, ids_aliados: List[int], ids_oponentes: List[int], num_batalhas: int = 1):
        # Busca no banco e converte para o Domínio
    equipa_aliada = [GameController.converter_para_dominio(db.query(PersonagemDB).get(i)) for i in ids_aliados]
    equipa_oponente = [GameController.converter_para_dominio(db.query(PersonagemDB).get(i)) for i in ids_oponentes]
    
    for person in equipa_aliada + equipa_oponente:
        print(person)
    
    # Inicia o Simulador que construímos!
    simulador = SimuladorCombate(equipa_aliada, equipa_oponente)
    
    if num_batalhas == 1:
        return simulador.simular_batalha(silencioso=False)
    else:
        print("\n📊 ESTATÍSTICAS DA BATALHA:")
        relatorio = simulador.simular_multiplas_batalhas(num_batalhas)
        
        return simulador.simular_multiplas_batalhas(num_batalhas)
    
    
    def criar_e_salvar_mapa(self, nome: str, tipo: str, h: int, w: int, configs: dict):
        # 1. Gera a matriz usando o Core
        matriz = GestorDeMapas.gerar_masmorra(h, w, configs)
        
        # 2. Cria o registro no banco
        novo_mapa = MapaDB(
            nome=nome, tipo=tipo, altura=h, largura=w,
            mapa_em_si=matriz, configs=configs
        )
        self.db.add(novo_mapa)
        self.db.commit()
        return novo_mapa

    def exportar_mapa_para_csv(self, mapa_id: int, caminho_arquivo: str):
        mapa_db = self.db.query(MapaDB).get(mapa_id)
        csv_text = GestorDeMapas.para_csv(mapa_db.mapa_em_si)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(csv_text)