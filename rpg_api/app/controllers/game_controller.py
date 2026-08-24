from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.models.personagens_db import PersonagemDB, RacaDB, ClasseRPGDB, EquipeMembroDB
from app.models.equipamentos_db import ItemDB
from app.models.habilidades_magias_db import MagiaDB, EfeitoDB
from app.core.entities.personagens import Personagem, Raca, ClasseRPG, Party, Equipe
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
    def converter_efeito_db_para_dominio(db_efeito: EfeitoDB) -> Optional[Efeito]:
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
    def converter_magia_db_para_dominio(db_magia: MagiaDB) -> Optional[Magia]:
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

    @staticmethod
    def converter_para_dominio(db_char: PersonagemDB) -> Personagem:
        """Converte um modelo do SQLAlchemy para a Entidade pura do RPG."""
        if not db_char:
            return None

        # 1. Recria a Raça do Domínio
        try:
            raca_domain = Raca(nome=db_char.raca.nome, bonus_atributos=db_char.raca.bonus_atributos, emoji=db_char.raca.emoji)
        except Exception as e:
            logging.info(f"Erro ao instanciar raça: {e}")
            raca_domain = Raca(nome="Humano", bonus_atributos={}, emoji="👤")
        
        # 2. Recria a Classe do Domínio
        try:
            classe_domain = ClasseRPG(
                nome=db_char.classe.nome, 
                bonus_caminhos=db_char.classe.bonus_caminhos,
                habilidades=db_char.classe.habilidades or [],
            )
        except Exception as e:
            logging.info(f"Erro ao instanciar classe: {e}")
            classe_domain = ClasseRPG(nome="Aventureiro", bonus_caminhos={}, habilidades=[])
            
        # 3. Recria o Personagem
        try:
            personagem = Personagem(
                nome=db_char.nome,
                nivel=int(db_char.nivel),
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
            raise
            
        # Equipar itens se existirem no banco
        if db_char.mao_direita:
            try:
                personagem.mao_direita = Arma(db_char.mao_direita.nome, db_char.mao_direita.dano or 0, db_char.mao_direita.tipo_ataque or "corpo")
            except Exception as e:
                logging.info(f"Erro ao instanciar mao direita: {e}")
                
        if db_char.mao_esquerda:
            try:
                item = db_char.mao_esquerda
                if item.categoria == "escudo":
                    personagem.mao_esquerda = Escudo(item.nome, item.defesa_extra or item.defesa or 0)
                else:
                    personagem.mao_esquerda = Arma(item.nome, item.dano or 0, item.tipo_ataque or "corpo")
            except Exception as e:
                logging.info(f"Erro ao instanciar mão esquerda: {e}")   
                
        if db_char.armadura_equipada:
            try:
                personagem.armadura = Armadura(db_char.armadura_equipada.nome, db_char.armadura_equipada.defesa or 0)
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
                        if magia_dom and not any(m.nome == magia_dom.nome for m in personagem.magias_conhecidas):
                            personagem.magias_conhecidas.append(magia_dom)
            except Exception as e:
                logging.info(f"Erro ao hidratar magias da classe para o personagem: {e}")

        # Carregar inventário individual do personagem
        if getattr(db_char, "inventario", None):
            try:
                inv_raw = db_char.inventario
                if isinstance(inv_raw, list):
                    for item_data in inv_raw:
                        if isinstance(item_data, dict):
                            personagem.adicionar_item_inventario(
                                nome=item_data.get("nome", "Item"),
                                quantidade=item_data.get("quantidade", 1),
                                categoria=item_data.get("categoria", "consumivel")
                            )
                        elif isinstance(item_data, str):
                            personagem.adicionar_item_inventario(nome=item_data, quantidade=1)
                elif isinstance(inv_raw, dict):
                    for nome_item, qtd in inv_raw.items():
                        personagem.adicionar_item_inventario(nome=nome_item, quantidade=qtd)
            except Exception as e:
                logging.info(f"Erro ao carregar inventario individual do personagem: {e}")

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

        
        
    @staticmethod
    def obter_personagem_por_id(db_or_self, p_id: Optional[int] = None) -> Optional[PersonagemDB]:
        if isinstance(db_or_self, GameController):
            return db_or_self.db.get(PersonagemDB, p_id)
        elif hasattr(db_or_self, "get"):
            return db_or_self.get(PersonagemDB, p_id)
        elif hasattr(db_or_self, "query"):
            return db_or_self.query(PersonagemDB).get(p_id)
        return None
        
    def atualizar_elemento(self, el_id: int, dados: dict, model):
        elemento = self.db.get(model, el_id)
        if not elemento:
            raise ValueError(f"{model.__name__} ID {el_id} não encontrado.")
        
        for chave, valor in dados.items():
            try:
                setattr(elemento, chave, valor) 
            except Exception as e:
                raise ValueError(f" ERRO: {e}")
            
        self.db.commit()
        return f"✅ atualizado com sucesso!"

    def listar_tudo(self, modelo):
        """Método genérico para listar registros (RacaDB, ClasseRPGDB, etc)"""
        return self.db.query(modelo).all()

    # ==========================================
    # GESTÃO DE EQUIPE E ALISTAMENTO (PARTY)
    # ==========================================

    def alistar_personagem(self, personagem_id: int, slot: Optional[int] = None, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None) -> bool:
        """
        Alista um personagem para a equipe do jogador.
        - Se for especificado um slot (1-4) que já está ocupado, o ocupante anterior vai para a reserva
          e o novo personagem assume a posição ativa.
        - Se não for especificado slot e houver menos de 4 membros ativos, assume o primeiro slot vago.
        - Se a equipe já estiver com 4 ativos e nenhum slot for forçado, entra como reserva (slot 0).
        """
        from sqlalchemy.orm.attributes import flag_modified
        personagem = self.db.get(PersonagemDB, personagem_id)
        if not personagem:
            return False

        # Verifica se já está registrado na tabela associativa
        membro = self.db.query(EquipeMembroDB).filter(
            EquipeMembroDB.personagem_id == personagem_id,
            (EquipeMembroDB.usuario_id == usuario_id) | (EquipeMembroDB.usuario_id == None),
            (EquipeMembroDB.cenario_id == cenario_id) | (EquipeMembroDB.cenario_id == None)
        ).first()

        ativos = self.db.query(EquipeMembroDB).filter(
            (EquipeMembroDB.usuario_id == usuario_id) | (EquipeMembroDB.usuario_id == None),
            (EquipeMembroDB.cenario_id == cenario_id) | (EquipeMembroDB.cenario_id == None),
            EquipeMembroDB.ativo == 1
        ).all()

        posicoes_ocupadas = {m.slot_posicao: m for m in ativos}

        if slot and 1 <= slot <= 4:
            # Se a posição solicitada já estiver ocupada por outro membro, move o outro para reserva
            if slot in posicoes_ocupadas and posicoes_ocupadas[slot].personagem_id != personagem_id:
                outro = posicoes_ocupadas[slot]
                outro.ativo = 0
                outro.slot_posicao = 0
                if outro.personagem:
                    outro.personagem.slot_equipe = 0

            novo_slot = slot
            is_ativo = 1
        elif len(ativos) < 4:
            novo_slot = next((s for s in range(1, 5) if s not in posicoes_ocupadas), len(ativos) + 1)
            is_ativo = 1
        else:
            novo_slot = 0  # Reserva
            is_ativo = 0

        if membro:
            membro.ativo = is_ativo
            membro.slot_posicao = novo_slot
            if usuario_id is not None:
                membro.usuario_id = usuario_id
            if cenario_id is not None:
                membro.cenario_id = cenario_id
        else:
            membro = EquipeMembroDB(
                usuario_id=usuario_id,
                cenario_id=cenario_id,
                personagem_id=personagem_id,
                slot_posicao=novo_slot,
                ativo=is_ativo
            )
            self.db.add(membro)

        personagem.slot_equipe = novo_slot
        self.db.commit()
        return True

    def desalistar_personagem(self, personagem_id: int, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None) -> bool:
        """Remove um personagem da equipe ativa/alistamento."""
        membro = self.db.query(EquipeMembroDB).filter(
            EquipeMembroDB.personagem_id == personagem_id,
            (EquipeMembroDB.usuario_id == usuario_id) | (EquipeMembroDB.usuario_id == None),
            (EquipeMembroDB.cenario_id == cenario_id) | (EquipeMembroDB.cenario_id == None)
        ).first()

        personagem = self.db.get(PersonagemDB, personagem_id)
        if personagem:
            personagem.slot_equipe = 0

        if membro:
            self.db.delete(membro)
            self.db.commit()
            return True
        self.db.commit()
        return False

    def obter_equipe_party(self, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None) -> Party:
        """
        Carrega a equipe ativa (Party de domínio) do banco de dados.
        Retorna a instância Party contendo até 4 membros ativos e eventuais reservas.
        """
        query_membros = self.db.query(EquipeMembroDB).filter(
            (EquipeMembroDB.usuario_id == usuario_id) | (EquipeMembroDB.usuario_id == None),
            (EquipeMembroDB.cenario_id == cenario_id) | (EquipeMembroDB.cenario_id == None)
        ).order_by(EquipeMembroDB.slot_posicao.asc()).all()

        party = Party()
        if query_membros:
            for m in query_membros:
                if m.personagem:
                    p_dom = GameController.converter_para_dominio(m.personagem)
                    if m.ativo == 1 and len(party.membros) < 4:
                        party.membros.append(p_dom)
                    else:
                        party.reservas.append(p_dom)
            if party.membros:
                return party

        # Fallback 1: Buscar personagens que tenham slot_equipe > 0
        chars_ativos = self.db.query(PersonagemDB).filter(
            PersonagemDB.slot_equipe > 0
        ).order_by(PersonagemDB.slot_equipe.asc()).all()

        chars_reserva = self.db.query(PersonagemDB).filter(
            (PersonagemDB.slot_equipe == 0) | (PersonagemDB.slot_equipe == None)
        ).all()

        if chars_ativos:
            for char_db in chars_ativos[:4]:
                party.adicionar_membro(GameController.converter_para_dominio(char_db))
            for char_db in chars_reserva:
                party.reservas.append(GameController.converter_para_dominio(char_db))
            return party

        # Fallback 2: Se não houver tabela de equipe populada, busca os primeiros PersonagemDB
        chars = self.db.query(PersonagemDB).all()
        for char_db in chars[:4]:
            party.adicionar_membro(GameController.converter_para_dominio(char_db))
        for char_db in chars[4:]:
            party.reservas.append(GameController.converter_para_dominio(char_db))

        return party

    def obter_party_do_jogador(self, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None) -> Party:
        """Alias para obter_equipe_party."""
        return self.obter_equipe_party(usuario_id=usuario_id, cenario_id=cenario_id)

    def obter_personagens_recrutaveis(self, usuario_id: Optional[int] = None, cenario_id: Optional[int] = None) -> List[PersonagemDB]:
        """Retorna todos os personagens disponíveis para recrutamento/alistamento."""
        return self.db.query(PersonagemDB).all()

    def transferir_item_entre_personagens_db(self, id_origem: int, id_destino: int, nome_item: str, quantidade: int = 1) -> bool:
        """
        Transfere um item entre os inventários de dois personagens no banco de dados.
        """
        from sqlalchemy.orm.attributes import flag_modified
        p_origem = self.db.get(PersonagemDB, id_origem)
        p_destino = self.db.get(PersonagemDB, id_destino)
        if not p_origem or not p_destino or quantidade <= 0:
            return False

        inv_origem = [dict(i) for i in (p_origem.inventario or [])]
        inv_destino = [dict(i) for i in (p_destino.inventario or [])]

        item_orig = None
        for it in inv_origem:
            if it.get("nome", "").lower() == nome_item.lower():
                item_orig = it
                break

        if not item_orig or item_orig.get("quantidade", 0) < quantidade:
            return False

        item_orig["quantidade"] -= quantidade
        if item_orig["quantidade"] <= 0:
            inv_origem.remove(item_orig)

        item_dest = None
        for it in inv_destino:
            if it.get("nome", "").lower() == nome_item.lower():
                item_dest = it
                break

        if item_dest:
            item_dest["quantidade"] += quantidade
        else:
            inv_destino.append({
                "nome": item_orig["nome"],
                "quantidade": quantidade,
                "categoria": item_orig.get("categoria", "consumivel"),
                "emoji": item_orig.get("emoji", "🧪")
            })

        p_origem.inventario = inv_origem
        p_destino.inventario = inv_destino
        flag_modified(p_origem, "inventario")
        flag_modified(p_destino, "inventario")
        self.db.commit()
        return True

    def adicionar_item_personagem_db(self, personagem_id: int, nome_item: str, quantidade: int = 1, categoria: str = "consumivel") -> bool:
        """Persiste adição de item ao inventário próprio do personagem no banco."""
        from sqlalchemy.orm.attributes import flag_modified
        personagem = self.db.get(PersonagemDB, personagem_id)
        if not personagem:
            return False
        inv = [dict(i) for i in (personagem.inventario or [])]
        encontrado = False
        for item in inv:
            if isinstance(item, dict) and item.get("nome", "").lower() == nome_item.lower():
                item["quantidade"] = item.get("quantidade", 1) + quantidade
                encontrado = True
                break
        if not encontrado:
            inv.append({"nome": nome_item, "quantidade": quantidade, "categoria": categoria})
        personagem.inventario = inv
        flag_modified(personagem, "inventario")
        self.db.commit()
        return True

    def remover_item_personagem_db(self, personagem_id: int, nome_item: str, quantidade: int = 1) -> bool:
        """Persiste remoção de item do inventário próprio do personagem no banco."""
        from sqlalchemy.orm.attributes import flag_modified
        personagem = self.db.get(PersonagemDB, personagem_id)
        if not personagem or not personagem.inventario:
            return False
        inv = [dict(i) for i in personagem.inventario]
        removido = False
        for idx, item in enumerate(inv):
            if isinstance(item, dict) and item.get("nome", "").lower() == nome_item.lower():
                qtd_atual = item.get("quantidade", 1)
                if qtd_atual >= quantidade:
                    item["quantidade"] = qtd_atual - quantidade
                    if item["quantidade"] <= 0:
                        inv.pop(idx)
                    removido = True
                    break
        if removido:
            personagem.inventario = inv
            flag_modified(personagem, "inventario")
            self.db.commit()
            return True
        return False

    @staticmethod
    def garantir_dados_iniciais_completos(db: Session) -> Dict[str, int]:
        """
        Popula o banco com Raças, Classes, Magias, Itens, Equipamentos e Personagens
        recrutáveis padrão ouro (estilo Final Fantasy).
        """
        from app.core.engine.item_system import garantir_itens_padrao
        garantir_itens_padrao(db)

        # 1. Raças Canônicas
        racas_padrao = [
            ("Humano", {"forca": 1, "agilidade": 1, "resistencia": 1, "percepcao": 1, "exuberancia": 1}, "👤"),
            ("Elfo", {"forca": 0, "agilidade": 2, "resistencia": 0, "percepcao": 2, "exuberancia": 2}, "🧝"),
            ("Anão", {"forca": 2, "agilidade": 0, "resistencia": 3, "percepcao": 1, "exuberancia": 0}, "🧔"),
            ("Orc", {"forca": 3, "agilidade": 1, "resistencia": 2, "percepcao": 0, "exuberancia": 0}, "👹"),
            ("Halfling", {"forca": 0, "agilidade": 3, "resistencia": 1, "percepcao": 2, "exuberancia": 1}, "🧙‍♂️"),
            ("Draconato", {"forca": 2, "agilidade": 1, "resistencia": 2, "percepcao": 1, "exuberancia": 2}, "🐲"),
        ]
        racas_map = {}
        for nome, bonus, emoji in racas_padrao:
            r = db.query(RacaDB).filter(RacaDB.nome.ilike(nome)).first()
            if not r:
                r = RacaDB(nome=nome, bonus_atributos=bonus, emoji=emoji)
                db.add(r)
                db.commit()
                db.refresh(r)
            racas_map[nome.lower()] = r

        # 2. Classes RPG
        classes_padrao = [
            ("Guerreiro", {"terra": 1}, ["Golpe Poderoso", "Investida"]),
            ("Mago", {"fogo": 2, "ar": 1, "luz": 1}, ["Bola de Fogo", "Lança de Gelo", "Chuva de Raios"]),
            ("Ladino", {"ar": 1, "trevas": 1}, ["Ataque Furtivo", "Golpe Rápido"]),
            ("Clérigo", {"luz": 3, "água": 1}, ["Cura Sagrada", "Bênção da Terra", "Cura em Grupo"]),
            ("Paladino", {"luz": 2, "terra": 1}, ["Golpe Sagrado", "Escudo Arcano", "Cura Sagrada"]),
            ("Arqueiro", {"ar": 2, "terra": 1}, ["Disparo Certeiro", "Chuva de Flechas"]),
        ]
        classes_map = {}
        for nome, bonus, habs in classes_padrao:
            c = db.query(ClasseRPGDB).filter(ClasseRPGDB.nome.ilike(nome)).first()
            if not c:
                c = ClasseRPGDB(nome=nome, bonus_caminhos=bonus, habilidades=habs)
                db.add(c)
                db.commit()
                db.refresh(c)
            classes_map[nome.lower()] = c

        # 3. Efeitos & Magias
        efeitos_padrao = [
            ("Queimadura", 3, "dano_continuo", 5, None),
            ("Regeneração", 3, "cura_continua", 8, None),
            ("Bênção de Força", 4, "buff_atributo", 2, "forca"),
            ("Agilidade dos Ventos", 4, "buff_atributo", 2, "agilidade"),
            ("Sono Profundo", 2, "sono", 0, None),
        ]
        efeitos_map = {}
        for nome, dur, tipo, val, attr in efeitos_padrao:
            ef = db.query(EfeitoDB).filter(EfeitoDB.nome.ilike(nome)).first()
            if not ef:
                ef = EfeitoDB(nome=nome, duracao_turnos=dur, tipo=tipo, valor=val, atributo_alvo=attr)
                db.add(ef)
                db.commit()
                db.refresh(ef)
            efeitos_map[nome.lower()] = ef

        magias_padrao = [
            ("Bola de Fogo", 4, {"fogo": 2}, 1, 15, 0, False, "combate", "Lança uma esfera flamejante que incinera o alvo.", {"ignorar_defesa": False}, "Queimadura"),
            ("Cura Sagrada", 3, {"luz": 1}, 1, 0, 20, False, "ambos", "Canaliza energia sagrada para restaurar a vida de um aliado.", {}, None),
            ("Cura em Grupo", 6, {"luz": 2}, 2, 0, 15, True, "ambos", "Restaura os pontos de vida de todos os membros da equipe.", {"cura_area": True}, None),
            ("Lança de Gelo", 3, {"água": 1}, 1, 12, 0, False, "combate", "Projétil gélido perfurante que fere o inimigo.", {}, None),
            ("Chuva de Raios", 5, {"ar": 2}, 2, 10, 0, True, "combate", "Descarga elétrica em área sobre todos os inimigos.", {}, None),
            ("Bênção da Terra", 3, {"terra": 1}, 1, 0, 0, False, "ambos", "Fortalece a constituição física do alvo.", {}, "Bênção de Força"),
            ("Escudo Arcano", 3, {"luz": 1}, 1, 0, 0, False, "combate", "Cria barreira protetora ao redor do aliado.", {}, "Regeneração"),
            ("Golpe Poderoso", 2, {}, 1, 14, 0, False, "combate", "Ataque físico devastador.", {}, None),
            ("Ataque Furtivo", 2, {}, 1, 16, 0, False, "combate", "Ataque preciso nos pontos vitais.", {"ignorar_defesa": True}, None),
            ("Disparo Certeiro", 2, {}, 1, 12, 0, False, "combate", "Tiro de longa distância preciso.", {}, None),
        ]
        for nome, custo, req_cam, req_exub, dano, cura, area, tipo_ex, desc, props, ef_nome in magias_padrao:
            m = db.query(MagiaDB).filter(MagiaDB.nome.ilike(nome)).first()
            ef_id = efeitos_map.get(ef_nome.lower()).id if ef_nome and ef_nome.lower() in efeitos_map else None
            if not m:
                m = MagiaDB(
                    nome=nome, custo_pm=custo, requisito_caminhos=req_cam,
                    requisito_exuberancia=req_exub, dano_base=dano, cura_base=cura,
                    dano_area=area, tipo_execucao=tipo_ex, descricao=desc,
                    propriedades_combate=props, efeito_id=ef_id
                )
                db.add(m)
                db.commit()

        # 4. Itens e Equipamentos Adicionais
        itens_extras = [
            ItemDB(nome="Cajado Arcano", categoria="arma", dano=6, tipo_ataque="corpo", emoji="🪄"),
            ItemDB(nome="Adaga Veloz", categoria="arma", dano=4, tipo_ataque="corpo", emoji="🗡️"),
            ItemDB(nome="Martelo de Guerra", categoria="arma", dano=8, tipo_ataque="corpo", emoji="🔨"),
            ItemDB(nome="Armadura de Placas", categoria="armadura", defesa=8, emoji="🛡️"),
            ItemDB(nome="Túnica Mágica", categoria="armadura", defesa=4, emoji="👘"),
            ItemDB(nome="Escudo Real", categoria="escudo", defesa_extra=5, emoji="🛡️"),
            ItemDB(nome="Elixir da Vida", categoria="consumivel", dano=50, emoji="🧪"),
        ]
        for it in itens_extras:
            existente = db.query(ItemDB).filter(ItemDB.nome.ilike(it.nome)).first()
            if not existente:
                db.add(it)
                db.commit()

        # 5. Personagens Recrutáveis (Party Padrão Final Fantasy)
        itens_db_map = {i.nome.lower(): i for i in db.query(ItemDB).all()}
        personagens_seed = [
            {
                "nome": "Artorias", "nivel": 2, "raca": "humano", "classe": "guerreiro",
                "forca": 4, "agilidade": 3, "resistencia": 3, "percepcao": 2, "exuberancia": 1,
                "arma": "Espada Longa", "escudo": "Escudo de Madeira", "armadura": "Armadura de Aço",
                "inventario": [{"nome": "Poção de Cura", "quantidade": 3, "categoria": "consumivel"}],
                "slot_equipe": 1
            },
            {
                "nome": "Aerith", "nivel": 2, "raca": "elfo", "classe": "clérigo",
                "forca": 1, "agilidade": 3, "resistencia": 2, "percepcao": 4, "exuberancia": 5,
                "arma": "Cajado Arcano", "escudo": None, "armadura": "Túnica Mágica",
                "inventario": [
                    {"nome": "Poção de Mana", "quantidade": 3, "categoria": "consumivel"},
                    {"nome": "Poção de Cura", "quantidade": 2, "categoria": "consumivel"}
                ],
                "slot_equipe": 2
            },
            {
                "nome": "Locke", "nivel": 2, "raca": "halfling", "classe": "ladino",
                "forca": 2, "agilidade": 5, "resistencia": 2, "percepcao": 4, "exuberancia": 2,
                "arma": "Adaga Veloz", "escudo": None, "armadura": "Túnica de Couro",
                "inventario": [{"nome": "Poção de Cura", "quantidade": 2, "categoria": "consumivel"}],
                "slot_equipe": 3
            },
            {
                "nome": "Vivi", "nivel": 2, "raca": "humano", "classe": "mago",
                "forca": 1, "agilidade": 2, "resistencia": 2, "percepcao": 4, "exuberancia": 5,
                "arma": "Cajado Arcano", "escudo": None, "armadura": "Túnica Mágica",
                "inventario": [{"nome": "Poção de Mana", "quantidade": 4, "categoria": "consumivel"}],
                "slot_equipe": 4
            },
            {
                "nome": "Gimli", "nivel": 2, "raca": "anão", "classe": "guerreiro",
                "forca": 5, "agilidade": 2, "resistencia": 4, "percepcao": 2, "exuberancia": 1,
                "arma": "Martelo de Guerra", "escudo": "Escudo Real", "armadura": "Armadura de Placas",
                "inventario": [{"nome": "Poção de Cura", "quantidade": 3, "categoria": "consumivel"}],
                "slot_equipe": 0
            },
            {
                "nome": "Sylvanas", "nivel": 2, "raca": "elfo", "classe": "arqueiro",
                "forca": 3, "agilidade": 5, "resistencia": 2, "percepcao": 4, "exuberancia": 2,
                "arma": "Arco Élfico", "escudo": None, "armadura": "Túnica de Couro",
                "inventario": [{"nome": "Poção de Cura", "quantidade": 2, "categoria": "consumivel"}],
                "slot_equipe": 0
            }
        ]

        for p_data in personagens_seed:
            p_existente = db.query(PersonagemDB).filter(PersonagemDB.nome.ilike(p_data["nome"])).first()
            raca_db = racas_map.get(p_data["raca"])
            classe_db = classes_map.get(p_data["classe"])
            arma_db = itens_db_map.get(p_data["arma"].lower()) if p_data.get("arma") else None
            escudo_db = itens_db_map.get(p_data["escudo"].lower()) if p_data.get("escudo") else None
            armadura_db = itens_db_map.get(p_data["armadura"].lower()) if p_data.get("armadura") else None

            if not p_existente and raca_db and classe_db:
                p_novo = PersonagemDB(
                    nome=p_data["nome"],
                    nivel=p_data["nivel"],
                    raca_id=raca_db.id,
                    classe_id=classe_db.id,
                    forca_base=p_data["forca"],
                    agilidade_base=p_data["agilidade"],
                    resistencia_base=p_data["resistencia"],
                    percepcao_base=p_data["percepcao"],
                    exuberancia_base=p_data["exuberancia"],
                    mao_direita_id=arma_db.id if arma_db else None,
                    mao_esquerda_id=escudo_db.id if escudo_db else None,
                    armadura_id=armadura_db.id if armadura_db else None,
                    inventario=p_data["inventario"],
                    slot_equipe=p_data["slot_equipe"]
                )
                db.add(p_novo)
                db.commit()
                db.refresh(p_novo)

                if p_data["slot_equipe"] > 0:
                    eq_membro = EquipeMembroDB(
                        personagem_id=p_novo.id,
                        slot_posicao=p_data["slot_equipe"],
                        ativo=1
                    )
                    db.add(eq_membro)
                    db.commit()

        return {
            "racas": db.query(RacaDB).count(),
            "classes": db.query(ClasseRPGDB).count(),
            "magias": db.query(MagiaDB).count(),
            "itens": db.query(ItemDB).count(),
            "personagens": db.query(PersonagemDB).count()
        }


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
        
        
