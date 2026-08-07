from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB
from app.models.equipamentos_db import ItemDB
from app.models.habilidades_magias_db import MagiaDB, EfeitoDB
from app.core.entities.personagens import Personagem, Raca, ClasseRPG
from app.core.entities.habilidades_magias import Magia, Efeito
from app.views.simulador import SimuladorCombate
from app.core.entities.equipamentos import Arma, Armadura, Escudo

from app.models.mapas_db import MapaDB
from app.core.entities.mapas import GestorDeMapas

import logging
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")

class GameController:
    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # TRADUTOR (MAPPER): BANCO DE DADOS -> DOMÍNIO
    # ==========================================
    
    @staticmethod
    def converter_efeito_db_para_dominio(db_efeito: EfeitoDB) -> Efeito:
        if not db_efeito:
            return None
        return Efeito(
            id=db_efeito.id,
            nome=db_efeito.nome,
            duracao_turnos=db_efeito.duracao_turnos,
            tipo=db_efeito.tipo,
            valor=db_efeito.valor or 0,
            atributo_alvo=db_efeito.atributo_alvo,
            configuracoes=db_efeito.configuracoes or {}
        )

    @staticmethod
    def converter_magia_db_para_dominio(db_magia: MagiaDB) -> Magia:
        if not db_magia:
            return None
        efeito_domain = GameController.converter_efeito_db_para_dominio(db_magia.efeito) if db_magia.efeito else None
        return Magia(
            id=db_magia.id,
            nome=db_magia.nome,
            custo_pm=db_magia.custo_pm,
            requisito_caminhos=db_magia.requisito_caminhos or {},
            dano_base=db_magia.dano_base or 0,
            cura_base=db_magia.cura_base or 0,
            dano_area=bool(db_magia.dano_area),
            tipo_execucao=db_magia.tipo_execucao or "combate",
            descricao=db_magia.descricao or "",
            propriedades_combate=db_magia.propriedades_combate or {},
            efeito_aplicado=efeito_domain,
            requisito_exuberancia=db_magia.requisito_exuberancia or 1
        )

    
    def converter_para_dominio(db_char: PersonagemDB) -> Personagem:
        """Converte um modelo do SQLAlchemy para a Entidade pura do RPG."""
        # 1. Recria a Raça do Domínio
        try:
            raca_domain = Raca(nome=db_char.raca.nome, bonus_atributos=db_char.raca.bonus_atributos, emoji=db_char.raca.emoji)
        except Exception as e:
            logging.info(f"Erro ao instanciar raça: {e}")
        
        # 2. Recria a Classe do Domínio
        try:
            classe_domain = ClasseRPG(
                nome=db_char.classe.nome, 
                bonus_caminhos=db_char.classe.bonus_caminhos,
                habilidades=db_char.classe.habilidades,
                #bonus_atributos=db_char.classe.bonus_atributos
            )
        except Exception as e:
            logging.info(f"Erro ao instanciar classe: {e}")
            
            
        # 3. Recria o Personagem
        try:
            personagem = Personagem(
                nome=db_char.nome,
                nivel= int(db_char.nivel),
                raca=raca_domain,
                classe_rpg=classe_domain,
                forca_base=int(db_char.forca_base),
                agilidade_base=int(db_char.agilidade_base),
                res_base=int(db_char.resistencia_base),
                perc_base=int(db_char.percepcao_base),
                exub_base=int(db_char.exuberancia_base)
            )
        except Exception as e:
            logging.info(f"Erro ao instanciar personagem: {e} = {db_char}")
            
            
        # Equipar itens se existirem no banco
        if db_char.mao_direita:
            try:
                personagem.mao_direita = Arma(db_char.mao_direita.nome, db_char.mao_direita.dano, db_char.mao_direita.tipo_ataque)
            except Exception as e:
                logging.info(f"Erro ao instanciar mao direita: {e}")
                
        if db_char.mao_esquerda:
            try:
                item = db_char.mao_esquerda
                if item.categoria == "escudo":
                    personagem.mao_esquerda = Escudo(item.nome, item.defesa)
                else:
                    personagem.mao_esquerda = Arma(item.nome, item.dano, item.tipo_ataque)
            except Exception as e:
                logging.info(f"Erro ao instanciar mão esquerda: {e}")   
                
        if db_char.armadura_equipada:
            try:
                personagem.armadura = Armadura(db_char.armadura_equipada.nome, db_char.armadura_equipada.defesa)
            except Exception as e:
                logging.info(f"Erro ao instanciar armadura: {e}")
                
        # Hydrate class abilities/spells from database into personagem.magias_conhecidas
        if db_char.classe and db_char.classe.habilidades:
            try:
                from sqlalchemy.orm import object_session
                from app.models.habilidades_magias_db import MagiaDB
                session = object_session(db_char)
                if not session:
                    from app.db.database import SessionLocal
                    session = SessionLocal()
                
                for hab_nome in db_char.classe.habilidades:
                    magia_db = session.query(MagiaDB).filter(MagiaDB.nome.ilike(hab_nome)).first()
                    if magia_db:
                        magia_dom = GameController.converter_magia_db_para_dominio(magia_db)
                        if magia_dom and magia_dom not in personagem.magias_conhecidas:
                            personagem.magias_conhecidas.append(magia_dom)
            except Exception as e:
                logging.info(f"Erro ao hidratar magias da classe para o personagem: {e}")

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
        

    def criar_personagem(db, nome, raca_id, classe_id, atributos, usuario_id=None, cenario_id=None):
        novo_personagem = PersonagemDB(
            nome=nome, raca_id=raca_id, classe_id=classe_id, usuario_id=usuario_id, cenario_id=cenario_id,
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

    @staticmethod
    def criar_magia(db, nome, custo_pm, requisito_caminhos, requisito_exuberancia=1, dano_base=0, cura_base=0, dano_area=False, tipo_execucao="combate", descricao="", propriedades_combate=None, efeito_id=None):
        if propriedades_combate is None:
            propriedades_combate = {}
        if requisito_caminhos is None:
            requisito_caminhos = {}
        nova_magia = MagiaDB(
            nome=nome,
            descricao=descricao,
            tipo_execucao=tipo_execucao,
            custo_pm=int(custo_pm),
            requisito_caminhos=requisito_caminhos,
            requisito_exuberancia=int(requisito_exuberancia),
            dano_base=int(dano_base),
            cura_base=int(cura_base),
            dano_area=bool(dano_area),
            propriedades_combate=propriedades_combate,
            efeito_id=efeito_id
        )
        try:
            db.add(nova_magia)
            db.commit()
            return f"✅ Magia '{nome}' salva com sucesso no Banco de Dados!"
        except Exception as e:
            db.rollback()
            return f"Não foi possível registrar a magia devido ao ERRO: {e}"

        
        
    def obter_personagem_por_id(db, p_id: int):
        person = db.query(PersonagemDB).get(p_id)
        return person
        
    
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
        
        
