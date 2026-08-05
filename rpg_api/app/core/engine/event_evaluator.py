"""
event_evaluator.py

Centraliza a lógica de avaliação de condições e filtragem de páginas ativas de eventos.
Esta lógica é compartilhada entre a inicialização de entidades no motor (EntityFactory)
e o sistema dinâmico de interações (EventSystem).
"""

import logging
import esper
from typing import Any
from app.core.engine.components import InventoryComponent, InteractableComponent

logger = logging.getLogger(__name__)


def obter_id_referencia_evento(entidade_id: int, world: Any = None) -> int:
    """
    Obtém o ID virtual estável do banco de dados para a entidade de evento (evt.id + 10000).
    Isso é necessário para que chaves de self_switch sejam persistentes a saves.
    Retorna o próprio entidade_id caso não haja ID virtual ou o componente não exista.
    """
    if world is None:
        world = esper
    try:
        if world.entity_exists(entidade_id) and world.has_component(entidade_id, InteractableComponent):
            interact = world.component_for_entity(entidade_id, InteractableComponent)
            if interact.parametros and "id_virtual_evento" in interact.parametros:
                return interact.parametros["id_virtual_evento"]
    except Exception as e:
        logger.error(f"Erro ao obter ID de referência do evento {entidade_id}: {e}")
    return entidade_id


def avaliar_condicoes(condicoes: dict, entidade_id: int, game_state: Any = None, world: Any = None) -> bool:
    """
    Avalia se todas as condições declaradas em uma página de evento são atendidas.
    """
    if world is None:
        world = esper

    # 1. Variáveis
    variaveis = condicoes.get("variaveis", [])
    if variaveis:
        if game_state is None:
            return False
        for var in variaveis:
            atual = game_state.get_variable(var["nome"], None)
            if atual is None:
                return False
            op = var.get("operador", "igual")
            val_esperado = var.get("valor", 0)

            # Conversão segura para numéricos para permitir comparações adequadas
            try:
                if str(atual).isdigit():
                    atual = int(atual)
                if str(val_esperado).isdigit():
                    val_esperado = int(val_esperado)
            except Exception:
                pass

            if isinstance(atual, (int, float)) and isinstance(val_esperado, (int, float)):
                if op == "maior_ou_igual" and not (atual >= val_esperado): return False
                if op == "menor_ou_igual" and not (atual <= val_esperado): return False
                if op == "igual" and not (atual == val_esperado): return False
                if op == "diferente" and not (atual != val_esperado): return False
            else:
                if op == "igual" and not (atual == val_esperado): return False
                if op == "diferente" and not (atual != val_esperado): return False

    # 2. Switches
    switches = condicoes.get("switches", [])
    if switches:
        if game_state is None:
            return False
        for sw in switches:
            if game_state.get_switch(sw["nome"]) != sw.get("valor", True):
                return False

    # 3. Self-Switches
    self_sw = condicoes.get("self_switch")
    if self_sw:
        if game_state is None:
            return False
        id_ref = obter_id_referencia_evento(entidade_id, world)
        if not game_state.get_switch(f"evento_{id_ref}_{self_sw}"):
            return False

    # 4. Item requerido no inventário
    item_req = condicoes.get("item_requerido")
    if item_req:
        try:
            inv = world.component_for_entity(1, InventoryComponent) if world.entity_exists(1) and world.has_component(1, InventoryComponent) else None
            if not inv or not _checar_item_inventario(inv, item_req):
                return False
        except Exception as e:
            logger.error(f"Erro ao checar item requerido {item_req} no inventário: {e}")
            return False

    return True


def _checar_item_inventario(inv: InventoryComponent, nome: str) -> bool:
    """Verifica se o componente de inventário possui o item especificado pelo nome."""
    if not inv:
        return False
    itens = getattr(inv, "itens", None)
    if isinstance(itens, dict):
        return any(k.lower() == nome.lower() and v > 0 for k, v in itens.items())
    if isinstance(itens, list):
        for entry in itens:
            if isinstance(entry, dict):
                entry_nome = entry.get("nome") or entry.get("item") or entry.get("nome_item")
            else:
                entry_nome = str(entry)
            if entry_nome and entry_nome.lower() == nome.lower():
                return True
    return False


def obter_pagina_ativa(
    paginas: list | None,
    entidade_id: int = 0,
    game_state: Any = None,
    world: Any = None
) -> dict | None:
    """
    Retorna a primeira página válida seguindo a avaliação decrescente da Regra 6.
    Itera de trás para frente na lista de páginas; retorna a última página
    cujas condições são atendidas.
    """
    if not paginas:
        return None

    # Filtra dicionários válidos e calcula o ID de página efetivo para ordenação
    paginas_validas = []
    for idx, p in enumerate(paginas):
        if isinstance(p, dict):
            id_efetivo = p.get("id_pagina")
            if id_efetivo is None:
                id_efetivo = idx
            paginas_validas.append((id_efetivo, p))

    # Varredura decrescente: da página de maior id_efetivo para a menor
    paginas_ordenadas = sorted(paginas_validas, key=lambda item: item[0], reverse=True)
    for _, pagina in paginas_ordenadas:
        condicoes = pagina.get("condicoes", {})
        if avaliar_condicoes(condicoes, entidade_id, game_state, world):
            return pagina

    return None
