import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.equipamentos_db import ItemDB
from app.core.engine.components import InventoryComponent, EquipmentComponent, StatsComponent

def garantir_itens_padrao(db_session: Session = None) -> List[ItemDB]:
    """Garante que a tabela de itens possui os itens padrão cadastrados."""
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    itens_fallback = [
        ItemDB(nome="Poção de Cura", categoria="consumivel", dano=20, emoji="🧪"),
        ItemDB(nome="Poção de Mana", categoria="consumivel", defesa=15, emoji="🧪"),
        ItemDB(nome="Poção", categoria="consumivel", dano=20, emoji="🧪"),
        ItemDB(nome="Espada Longa", categoria="arma", dano=5, tipo_ataque="corpo", emoji="🗡️"),
        ItemDB(nome="Arco Élfico", categoria="arma", dano=7, tipo_ataque="distancia", emoji="🏹"),
        ItemDB(nome="Armadura de Aço", categoria="armadura", defesa=6, emoji="🦺"),
        ItemDB(nome="Túnica de Couro", categoria="armadura", defesa=3, emoji="🧥"),
        ItemDB(nome="Escudo de Madeira", categoria="escudo", defesa_extra=3, emoji="🛡️"),
    ]

    try:
        from app.db.database import Base, engine
        Base.metadata.create_all(bind=engine)
        itens = db_session.query(ItemDB).all()
        if not itens:
            db_session.add_all(itens_fallback)
            db_session.commit()
            itens = db_session.query(ItemDB).all()
        return itens
    except Exception as e:
        logging.error(f"Erro ao garantir itens padrao: {e}")
        return itens_fallback
    finally:
        if close_session:
            db_session.close()


def obter_todos_itens_db(db_session: Session = None) -> List[ItemDB]:
    """Retorna todos os itens cadastrados no banco de dados."""
    return garantir_itens_padrao(db_session)


def obter_mapeamento_inventario(inv: InventoryComponent) -> Dict[str, int]:
    """Extrai um dicionário {nome_item: quantidade} do componente de inventário."""
    if not inv or not hasattr(inv, "itens"):
        return {}
    itens = inv.itens
    if isinstance(itens, dict):
        return {k: v for k, v in itens.items() if v > 0}
    if isinstance(itens, list):
        mapped = {}
        for entry in itens:
            if isinstance(entry, dict):
                nome = entry.get("nome") or entry.get("item") or entry.get("nome_item")
                qtd = entry.get("quantidade", 1)
            elif hasattr(entry, "nome"):
                nome = getattr(entry, "nome")
                qtd = getattr(entry, "quantidade", 1)
            elif hasattr(entry, "name"):
                nome = getattr(entry, "name")
                qtd = getattr(entry, "quantidade", 1)
            else:
                nome = str(entry)
                qtd = 1
            if nome:
                mapped[nome] = mapped.get(nome, 0) + qtd
        return mapped
    return {}


def inv_adicionar_item(inv: InventoryComponent, nome: str, quantidade: int = 1) -> bool:
    """Adiciona uma quantidade de item ao componente de inventário (case-insensitive)."""
    if not inv:
        return False
    if not hasattr(inv, "itens") or inv.itens is None:
        inv.itens = {}
    
    if isinstance(inv.itens, dict):
        chave_existente = None
        for k in inv.itens.keys():
            if k.lower() == nome.lower():
                chave_existente = k
                break
        if chave_existente:
            inv.itens[chave_existente] += quantidade
        else:
            inv.itens[nome] = quantidade
        return True
    if isinstance(inv.itens, list):
        if any(isinstance(x, dict) for x in inv.itens):
            for entry in inv.itens:
                if isinstance(entry, dict):
                    e_nome = entry.get("nome") or entry.get("item")
                    if e_nome and e_nome.lower() == nome.lower():
                        entry["quantidade"] = entry.get("quantidade", 1) + quantidade
                        return True
            inv.itens.append({"nome": nome, "quantidade": quantidade})
            return True
        inv.itens.extend([nome] * quantidade)
        return True
    return False


def inv_remover_item(inv: InventoryComponent, nome: str, quantidade: int = 1) -> bool:
    """Remove uma quantidade de item do componente de inventário (case-insensitive)."""
    if not inv:
        return False
    itens = getattr(inv, "itens", None)
    if isinstance(itens, dict):
        chave_existente = None
        for k in itens.keys():
            if k.lower() == nome.lower():
                chave_existente = k
                break
        if chave_existente:
            atual = itens[chave_existente]
            if atual >= quantidade:
                itens[chave_existente] = atual - quantidade
                if itens[chave_existente] <= 0:
                    itens.pop(chave_existente, None)
                return True
        return False
    if isinstance(itens, list):
        if any(isinstance(x, dict) for x in itens):
            for entry in itens:
                if isinstance(entry, dict):
                    e_nome = entry.get("nome") or entry.get("item")
                    if e_nome and e_nome.lower() == nome.lower():
                        qtd = entry.get("quantidade", 1)
                        if qtd > quantidade:
                            entry["quantidade"] = qtd - quantidade
                        else:
                            itens.remove(entry)
                        return True
            return False
        removed = 0
        to_remove = []
        for x in itens:
            if isinstance(x, str) and x.lower() == nome.lower():
                to_remove.append(x)
                removed += 1
                if removed == quantidade:
                    break
        if removed == quantidade:
            for x in to_remove:
                itens.remove(x)
            return True
        return False
    return False


def _eh_equipamento(nome_item: str, item_db: Any = None) -> Tuple[bool, str]:
    """Auxiliar para verificar se o item é um equipamento e qual a sua categoria ("arma", "armadura", "escudo")."""
    cat = item_db.categoria.lower() if (item_db and hasattr(item_db, "categoria") and item_db.categoria) else ""
    nome_lower = nome_item.lower()

    kw_equip = [
        "espada", "arco", "machado", "cajado", "armadura", "túnica", "tunica", "escudo",
        "capacete", "botas", "bota", "elmo", "luvas", "luva", "colar", "anel", "cinto",
        "tridente", "adaga", "lança", "lanca", "martelo", "varinha", "peitoral", "manto", "vesta", "traje"
    ]

    is_equip = (
        cat in ["arma", "armadura", "escudo", "equipamento"] or
        any(k in nome_lower for k in kw_equip)
    )
    if cat in ["consumivel", "comum"] and not any(k in nome_lower for k in kw_equip):
        is_equip = False

    if is_equip:
        if cat in ["arma", "armadura", "escudo"]:
            return True, cat
        if any(k in nome_lower for k in ["espada", "arco", "machado", "cajado", "adaga", "lança", "lanca", "martelo", "varinha", "tridente"]):
            return True, "arma"
        if any(k in nome_lower for k in ["armadura", "túnica", "tunica", "capacete", "botas", "bota", "elmo", "luvas", "luva", "colar", "anel", "peitoral", "manto", "traje"]):
            return True, "armadura"
        if "escudo" in nome_lower:
            return True, "escudo"
        return True, "arma"

    return False, ""


def obter_itens_usaveis(inv: InventoryComponent, db_session: Session = None) -> List[Dict[str, Any]]:
    """Retorna uma lista de itens usáveis/consumíveis presentes no inventário."""
    mapping = obter_mapeamento_inventario(inv)
    if not mapping:
        return []

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    usaveis = []
    try:
        todos_db = {i.nome.lower(): i for i in garantir_itens_padrao(db_session)}
        for nome_item, qtd in mapping.items():
            item_db = todos_db.get(nome_item.lower())
            is_eqp, cat_eqp = _eh_equipamento(nome_item, item_db)

            cat = item_db.categoria.lower() if (item_db and getattr(item_db, "categoria", None)) else ""
            nome_lower = nome_item.lower()

            # Itens que não são equipamentos entram como usáveis
            if not is_eqp or cat in ["consumivel", "comum"]:
                emoji = item_db.emoji if (item_db and getattr(item_db, "emoji", None)) else "🧪"
                if "mana" in nome_lower or "mp" in nome_lower:
                    desc = f"Recupera {item_db.defesa if (item_db and getattr(item_db, 'defesa', None)) else 15} MP"
                else:
                    desc = f"Recupera {item_db.dano if (item_db and getattr(item_db, 'dano', None)) else 20} HP"

                usaveis.append({
                    "nome": nome_item,
                    "quantidade": qtd,
                    "emoji": emoji,
                    "categoria": cat or "consumivel",
                    "descricao": desc,
                })
    finally:
        if close_session:
            db_session.close()

    return usaveis


def obter_equipamentos_inventario(inv: InventoryComponent, db_session: Session = None) -> List[Dict[str, Any]]:
    """Retorna uma lista de itens equipáveis presentes no inventário."""
    mapping = obter_mapeamento_inventario(inv)
    if not mapping:
        return []

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    equipamentos = []
    try:
        todos_db = {i.nome.lower(): i for i in garantir_itens_padrao(db_session)}
        for nome_item, qtd in mapping.items():
            item_db = todos_db.get(nome_item.lower())
            is_eqp, cat = _eh_equipamento(nome_item, item_db)

            if is_eqp:
                emoji = item_db.emoji if (item_db and getattr(item_db, "emoji", None)) else ("🗡️" if cat == "arma" else ("🛡️" if cat == "escudo" else "🦺"))
                if cat == "arma":
                    stats_desc = f"+{item_db.dano if (item_db and getattr(item_db, 'dano', None)) else 5} ATK"
                elif cat == "armadura":
                    stats_desc = f"+{item_db.defesa if (item_db and getattr(item_db, 'defesa', None)) else 6} DEF"
                elif cat == "escudo":
                    stats_desc = f"+{item_db.defesa_extra if (item_db and getattr(item_db, 'defesa_extra', None)) else 3} DEF"
                else:
                    stats_desc = "Equipamento"

                equipamentos.append({
                    "nome": nome_item,
                    "quantidade": qtd,
                    "emoji": emoji,
                    "categoria": cat,
                    "descricao": stats_desc,
                })
    finally:
        if close_session:
            db_session.close()

    return equipamentos


def aplicar_usar_item(target_entity_or_stats, inv: InventoryComponent, nome_item: str, db_session: Session = None) -> Tuple[bool, str]:
    """Aplica o efeito de uso do item no herói e o consome do inventário."""
    if not inv or not inv_remover_item(inv, nome_item, 1):
        return False, f"Você não possui '{nome_item}' no inventário."

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    try:
        todos_db = {i.nome.lower(): i for i in garantir_itens_padrao(db_session)}
        item_db = todos_db.get(nome_item.lower())

        nome_canonical = item_db.nome if item_db else nome_item
        nome_lower = nome_item.lower()
        is_domain = hasattr(target_entity_or_stats, "pv_atual")

        if "mana" in nome_lower or "mp" in nome_lower:
            bonus = item_db.defesa if (item_db and item_db.defesa) else 15
            if is_domain:
                atual = getattr(target_entity_or_stats, "pm_atual", 0)
                max_val = getattr(target_entity_or_stats, "max_mp", 100)
                recup = min(max_val - atual, bonus)
                target_entity_or_stats.pm_atual += recup
            else:
                atual = getattr(target_entity_or_stats, "mp", 0)
                max_val = getattr(target_entity_or_stats, "max_mp", 100)
                recup = min(max_val - atual, bonus)
                target_entity_or_stats.mp += recup
            return True, f"✨ Você usou {nome_canonical}. Recuperou {recup} MP!"
        else:
            bonus = item_db.dano if (item_db and item_db.dano) else 20
            if is_domain:
                atual = getattr(target_entity_or_stats, "pv_atual", 0)
                max_val = getattr(target_entity_or_stats, "max_hp", 100)
                recup = min(max_val - atual, bonus)
                target_entity_or_stats.pv_atual += recup
            else:
                atual = getattr(target_entity_or_stats, "hp", 0)
                max_val = getattr(target_entity_or_stats, "max_hp", 100)
                recup = min(max_val - atual, bonus)
                target_entity_or_stats.hp += recup
            return True, f"✨ Você usou {nome_canonical}. Recuperou {recup} HP!"
    finally:
        if close_session:
            db_session.close()


def aplicar_equipar_item(eqp: EquipmentComponent, inv: InventoryComponent, nome_item: str, db_session: Session = None) -> Tuple[bool, str]:
    """Equipa um item do inventário no slot correspondente do EquipmentComponent."""
    if not inv or not eqp:
        return False, "Inventário ou equipamento inválido."

    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    try:
        todos_db = {i.nome.lower(): i for i in garantir_itens_padrao(db_session)}
        item_db = todos_db.get(nome_item.lower())

        nome_canonical = item_db.nome if item_db else nome_item
        cat = item_db.categoria.lower() if (item_db and item_db.categoria) else ""
        nome_lower = nome_item.lower()

        if not cat or cat not in ["arma", "armadura", "escudo"]:
            if any(k in nome_lower for k in ["espada", "arco", "machado", "cajado", "adaga", "lança", "lanca", "martelo", "varinha", "tridente"]):
                cat = "arma"
            elif any(k in nome_lower for k in ["armadura", "túnica", "tunica", "capacete", "botas", "bota", "elmo", "luvas", "luva", "colar", "anel", "peitoral", "manto", "traje"]):
                cat = "armadura"
            elif "escudo" in nome_lower:
                cat = "escudo"
            else:
                cat = "arma"

        if cat == "arma":
            bonus = item_db.dano if (item_db and item_db.dano) else 5
            tipo = item_db.tipo_ataque if (item_db and item_db.tipo_ataque) else "corpo"
            if eqp.arma:
                inv_adicionar_item(inv, eqp.arma["nome"], 1)
            if not inv_remover_item(inv, nome_item, 1):
                return False, f"Você não possui '{nome_item}' no inventário."
            eqp.arma = {"nome": nome_canonical, "bonus_atk": bonus, "tipo": tipo}
            return True, f"⚔️ Equipado como Arma: {nome_canonical} (+{bonus} ATK)."

        elif cat == "armadura":
            bonus = item_db.defesa if (item_db and item_db.defesa) else 6
            if eqp.armadura:
                inv_adicionar_item(inv, eqp.armadura["nome"], 1)
            if not inv_remover_item(inv, nome_item, 1):
                return False, f"Você não possui '{nome_item}' no inventário."
            eqp.armadura = {"nome": nome_canonical, "bonus_def": bonus}
            return True, f"🦺 Equipado como Armadura: {nome_canonical} (+{bonus} DEF)."

        elif cat == "escudo":
            bonus = item_db.defesa_extra if (item_db and item_db.defesa_extra) else 3
            if hasattr(eqp, "escudo") and eqp.escudo:
                inv_adicionar_item(inv, eqp.escudo["nome"], 1)
            if not inv_remover_item(inv, nome_item, 1):
                return False, f"Você não possui '{nome_item}' no inventário."
            eqp.escudo = {"nome": nome_canonical, "bonus_def": bonus}
            return True, f"🛡️ Equipado como Escudo: {nome_canonical} (+{bonus} DEF)."

        return False, f"Item '{nome_item}' não é um equipamento válido."
    finally:
        if close_session:
            db_session.close()


def aplicar_desequipar_item(eqp: EquipmentComponent, inv: InventoryComponent, slot: str) -> Tuple[bool, str]:
    """Desequipa o item do slot ("arma", "armadura", "escudo") e o devolve ao inventário."""
    if not eqp or not inv:
        return False, "Equipamento ou inventário inválido."

    item_equipado = getattr(eqp, slot, None)
    if not item_equipado:
        return False, f"Nenhum item equipado no slot {slot}."

    nome_item = item_equipado.get("nome", "Equipamento")
    setattr(eqp, slot, None)
    inv_adicionar_item(inv, nome_item, 1)

    emoji = "⚔️" if slot == "arma" else ("🛡️" if slot == "escudo" else "🦺")
    return True, f"{emoji} Desequipou: {nome_item}."
