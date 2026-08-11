"""
entity_factory.py

Fábrica de Entidades ECS (EntityFactory).

Centraliza toda a lógica de criação/hidratação de entidades no esper,
eliminando chamadas espalhadas de esper.add_component no GameEngineLoader.

Cada tipo de entidade do jogo (Player, Npc, Monstro, Pacifico, Item,
Interativo, Veiculo, Cenario) possui um construtor dedicado que adiciona
apenas os componentes adequados ao comportamento esperado.

Regras seguidas:
  - Regra 1 (Clean Architecture): sem importações de Textual ou FastAPI.
  - Regra 2 (ECS/Esper): componentes são structs puras; lógica fica aqui.
  - Regra 6 (Eventos): a página ativa é determinada por varredura decrescente.
"""

import logging
from enum import Enum
from typing import Any

import esper

from app.core.engine.components import (
    StatsComponent,
    RenderComponent,
    MovimentComponent,
    PositionComponent,
    CollisionComponent,
    EquipmentComponent,
    InventoryComponent,
    InteractableComponent,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# ENUM DE TIPOS DE ENTIDADE
# ==============================================================================

class TipoEntidade(Enum):
    """Tipos canônicos de entidade reconhecidos pelo motor de jogo."""
    PLAYER     = "player"
    NPC        = "npc"        # Diálogo / loja — sem combate
    MONSTRO    = "monstro"    # Combate + MovimentComponent agressivo
    PACIFICO   = "pacifico"   # Movimento sem atacar
    ITEM       = "item"       # Baú / colecionável — sem movimento
    INTERATIVO = "interativo" # Portas / alavancas / armadilhas — sem movimento
    VEICULO    = "veiculo"    # Transporte — MovimentComponent especial
    CENARIO    = "cenario"    # Decoração pura — CollisionComponent opcional


# Mapeamento de strings do banco de dados para TipoEntidade
_MAPA_EVENT_TYPE_PARA_TIPO_ENTIDADE: dict[str, TipoEntidade] = {
    "monstro":       TipoEntidade.MONSTRO,
    "npc":           TipoEntidade.NPC,
    "npc_dialogo":   TipoEntidade.NPC,
    "npc_loja":      TipoEntidade.NPC,
    "pacifico":      TipoEntidade.PACIFICO,
    "animal":        TipoEntidade.PACIFICO,
    "bau":           TipoEntidade.ITEM,
    "item":          TipoEntidade.ITEM,
    "colecionavel":  TipoEntidade.ITEM,
    "porta":         TipoEntidade.INTERATIVO,
    "teleport":      TipoEntidade.INTERATIVO,
    "interativo":    TipoEntidade.INTERATIVO,
    "alavanca":      TipoEntidade.INTERATIVO,
    "armadilha":     TipoEntidade.INTERATIVO,
    "evento_custom": TipoEntidade.INTERATIVO,
    "veiculo":       TipoEntidade.VEICULO,
    "cenario":       TipoEntidade.CENARIO,
    "bloco":         TipoEntidade.CENARIO,
}


# ==============================================================================
# FUNÇÕES AUXILIARES PURAS
# ==============================================================================

def mapear_tipo_entidade(event_type: str) -> TipoEntidade:
    """
    Converte a string ``event_type`` do banco de dados no enum TipoEntidade.
    Strings não reconhecidas recebem fallback para INTERATIVO para que
    a entidade ainda apareça no mapa sem comportamento especial.
    """
    return _MAPA_EVENT_TYPE_PARA_TIPO_ENTIDADE.get(
        event_type.strip().lower(), TipoEntidade.INTERATIVO
    )


from app.core.engine.event_evaluator import obter_pagina_ativa


# ==============================================================================
# FÁBRICA DE ENTIDADES
# ==============================================================================

class EntityFactory:
    """
    Cria e hidrata entidades no esper de forma centralizada e tipada.
    Todos os métodos são estáticos — a fábrica não mantém estado interno.
    """

    # --------------------------------------------------------------------------
    # API PÚBLICA — entidades de evento (NPCs, Monstros, Itens etc.)
    # ---------------    @staticmethod
    def criar_entidade_evento(
        entity_id: int,
        event_type: str,
        nome: str,
        emoji: str,
        pos_x: int,
        pos_y: int,
        parametros_base: dict[str, Any],
        dados_salvos: dict[str, Any] | None = None,
        game_state: Any = None,
        world: Any = None,
    ) -> None:
        """
        Ponto de entrada principal para criação de entidades de evento.

        Determina o TipoEntidade a partir do ``event_type``, determina a
        página ativa e delega para o construtor específico do tipo.

        Args:
            entity_id: ID da entidade já criada no esper via esper.create_entity().
            event_type: String do banco de dados (ex: "monstro", "npc", "bau").
            nome: Nome do evento/entidade.
            emoji: Representação visual na TUI.
            pos_x: Coluna inicial no mapa.
            pos_y: Linha inicial no mapa.
            parametros_base: Dicionário completo de parâmetros do EventoDB.
            dados_salvos: Dados de componentes persistidos no SaveDB (pode ser None).
            game_state: Estado do jogo para avaliação de switches e variáveis.
            world: O mundo do Esper para checar inventário do herói.
        """
        tipo_entidade = mapear_tipo_entidade(event_type)
        paginas = parametros_base.get("paginas", [])
        pagina_ativa = obter_pagina_ativa(paginas, entidade_id=entity_id, game_state=game_state, world=world)

        # Determina posição: prioriza dado salvo para entidades com movimento
        posicao_x, posicao_y = pos_x, pos_y
        if dados_salvos:
            componentes_salvos = dados_salvos.get("components", dados_salvos)
            posicao_salva = componentes_salvos.get("PositionComponent", {})
            posicao_x = posicao_salva.get("x", pos_x)
            posicao_y = posicao_salva.get("y", pos_y)

        # Componentes base presentes em toda entidade de evento
        EntityFactory._construir_base(
            entity_id=entity_id,
            pos_x=posicao_x,
            pos_y=posicao_y,
            emoji=emoji,
            event_type=event_type,
            parametros_base=parametros_base,
        )

        # Componentes adicionais específicos por tipo
        if tipo_entidade == TipoEntidade.MONSTRO:
            stats_salvos = _extrair_stats_salvos(dados_salvos) if dados_salvos else {}
            EntityFactory._construir_monstro(
                entity_id=entity_id,
                nome=nome,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
                stats_salvos=stats_salvos,
            )

        elif tipo_entidade == TipoEntidade.NPC:
            EntityFactory._construir_npc(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
            )

        elif tipo_entidade == TipoEntidade.PACIFICO:
            stats_salvos = _extrair_stats_salvos(dados_salvos) if dados_salvos else {}
            EntityFactory._construir_pacifico(
                entity_id=entity_id,
                nome=nome,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
                stats_salvos=stats_salvos,
            )

        elif tipo_entidade == TipoEntidade.ITEM:
            EntityFactory._construir_item(entity_id=entity_id)

        elif tipo_entidade == TipoEntidade.INTERATIVO:
            EntityFactory._construir_interativo(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
                )

        elif tipo_entidade == TipoEntidade.VEICULO:
            EntityFactory._construir_veiculo(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
            )

        elif tipo_entidade == TipoEntidade.CENARIO:
            EntityFactory._construir_cenario(
                entity_id=entity_id,
                parametros_base=parametros_base,
            )

    # --------------------------------------------------------------------------
    # API PÚBLICA — entidade do jogador (ID 1 fixo)
    # --------------------------------------------------------------------------

    @staticmethod
    def criar_entidade_jogador_de_save(
        entity_id: int,
        pos_x: int,
        pos_y: int,
        direcao_olhar: str,
        emoji: str,
        stats_dict: dict[str, Any],
        inv_dict: dict[str, Any],
        eqp_dict: dict[str, Any],
    ) -> None:
        """
        Hidrata a entidade do jogador a partir de dados do SaveDB.

        Args:
            entity_id: Deve ser 1 (herói nômade fixo).
            pos_x: Posição X restaurada do save.
            pos_y: Posição Y restaurada do save.
            direcao_olhar: Direção do sprite ("baixo", "cima", etc.).
            emoji: Emoji representando a raça/classe do personagem.
            stats_dict: Dicionário com campos do StatsComponent.
            inv_dict: Dicionário com campo "itens".
            eqp_dict: Dicionário com campos "arma" e "armadura".
        """
        esper.add_component(
            entity_id,
            PositionComponent(x=pos_x, y=pos_y, direcao_olhar=direcao_olhar),
        )
        esper.add_component(entity_id, RenderComponent(emoji=emoji))
        esper.add_component(entity_id, CollisionComponent(solido=True))
        inv_salvo = inv_dict.get("itens", {})
        if not inv_salvo:
            inv_salvo = {
                "Poção de Cura": 1,
                "Poção de Mana": 1,
            }
        esper.add_component(entity_id, InventoryComponent(itens=inv_salvo))

        componente_equipamento = EquipmentComponent()
        componente_equipamento.arma = eqp_dict.get("arma")
        componente_equipamento.armadura = eqp_dict.get("armadura")
        componente_equipamento.escudo = eqp_dict.get("escudo")
        esper.add_component(entity_id, componente_equipamento)

        if stats_dict:
            esper.add_component(
                entity_id,
                StatsComponent(
                    nome=stats_dict.get("nome", "Herói"),
                    classe=stats_dict.get("classe", "mago"),
                    hp=stats_dict.get("hp", 50),
                    max_hp=stats_dict.get("max_hp", 50),
                    mp=stats_dict.get("mp", 10),
                    max_mp=stats_dict.get("max_mp", 10),
                    ataque_base=stats_dict.get("ataque_base", 10),
                    defesa_base=stats_dict.get("defesa_base", 5),
                ),
            )

    @staticmethod
    def criar_entidade_jogador_novo(
        entity_id: int,
        pos_x: int,
        pos_y: int,
        personagem_dominio: Any,
        defesa_extra_calculada: int = 0,
    ) -> None:
        """
        Hidrata a entidade do jogador a partir de um objeto de domínio (novo jogo).

        Args:
            entity_id: Deve ser 1 (herói nômade fixo).
            pos_x: Posição X inicial definida pelo mapa.
            pos_y: Posição Y inicial definida pelo mapa.
            personagem_dominio: Objeto retornado por GameController.converter_para_dominio().
            defesa_extra_calculada: Defesa bônus proveniente de escudo equipado.
        """
        emoji_raca = str(
            personagem_dominio.raca if hasattr(personagem_dominio, "raca") else "🧙"
        )

        arma_eqp = None
        if hasattr(personagem_dominio, "mao_direita") and personagem_dominio.mao_direita:
            m_dir = personagem_dominio.mao_direita
            arma_eqp = {
                "nome": getattr(m_dir, "nome", "Espada Longa"),
                "bonus_atk": getattr(m_dir, "dano", 5),
                "tipo": getattr(m_dir, "tipo", "corpo")
            }

        armadura_eqp = None
        if hasattr(personagem_dominio, "armadura") and personagem_dominio.armadura:
            arm = personagem_dominio.armadura
            armadura_eqp = {
                "nome": getattr(arm, "nome", "Armadura de Aço"),
                "bonus_def": getattr(arm, "defesa", 6)
            }

        escudo_eqp = None
        if hasattr(personagem_dominio, "mao_esquerda") and personagem_dominio.mao_esquerda:
            m_esq = personagem_dominio.mao_esquerda
            if hasattr(m_esq, "defesa"):
                escudo_eqp = {
                    "nome": getattr(m_esq, "nome", "Escudo de Madeira"),
                    "bonus_def": getattr(m_esq, "defesa", 3)
                }

        inv_inicial = {
            "Poção de Cura": 1,
            "Poção de Mana": 1,
        }

        esper.add_component(
            entity_id,
            PositionComponent(x=pos_x, y=pos_y, direcao_olhar="baixo"),
        )
        esper.add_component(entity_id, RenderComponent(emoji=emoji_raca))
        esper.add_component(entity_id, CollisionComponent(solido=True))
        esper.add_component(entity_id, InventoryComponent(itens=inv_inicial))
        esper.add_component(
            entity_id,
            EquipmentComponent(arma=arma_eqp, armadura=armadura_eqp, escudo=escudo_eqp)
        )
        esper.add_component(
            entity_id,
            StatsComponent(
                nome=personagem_dominio.nome,
                classe="mago",
                hp=int(personagem_dominio.pv_atual),
                max_hp=int(personagem_dominio.max_hp),
                mp=int(personagem_dominio.pm_atual),
                max_mp=int(personagem_dominio.max_mp),
                ataque_base=int(personagem_dominio.mod_atq_corpo or 0),
                defesa_base=int(defesa_extra_calculada),
            ),
        )

    # --------------------------------------------------------------------------
    # CONSTRUTORES INTERNOS POR TIPO
    # --------------------------------------------------------------------------

    @staticmethod
    def _construir_base(
        entity_id: int,
        pos_x: int,
        pos_y: int,
        emoji: str,
        event_type: str,
        parametros_base: dict[str, Any],
    ) -> None:
        """
        Adiciona os componentes comuns a todas as entidades de evento:
        PositionComponent, RenderComponent, CollisionComponent e InteractableComponent.
        """
        esper.add_component(entity_id, PositionComponent(x=pos_x, y=pos_y))
        esper.add_component(entity_id, RenderComponent(emoji=emoji))
        esper.add_component(entity_id, CollisionComponent(solido=True))
        esper.add_component(
            entity_id,
            InteractableComponent(
                event_type=event_type,
                parametros=parametros_base,
            ),
        )

    @staticmethod
    def _construir_monstro(
        entity_id: int,
        nome: str,
        pagina_ativa: dict | None,
        parametros_base: dict[str, Any],
        stats_salvos: dict[str, Any],
    ) -> None:
        """
        Adiciona StatsComponent (combate) e MovimentComponent (se a página ativa
        definir movimento) para entidades do tipo Monstro.
        """
        valor_dano = (
            parametros_base.get("ação", {}).get("mudar_hp", {}).get("valor", 2)
        ) #Isto talvez deva ser construido no InteractSystem usando ColisionComponent

        esper.add_component(
            entity_id,
            StatsComponent(
                nome=stats_salvos.get("nome", nome),
                classe="",
                hp=stats_salvos.get("hp", 10),
                max_hp=stats_salvos.get("max_hp", 10),
                mp=stats_salvos.get("mp", 0),
                max_mp=stats_salvos.get("max_mp", 0),
                ataque_base=stats_salvos.get("ataque_base", valor_dano),
                defesa_base=stats_salvos.get("defesa_base", 2),
            ),
        )

        if pagina_ativa and "movimento" in pagina_ativa:
            EntityFactory._adicionar_moviment_component(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
            )

    @staticmethod
    def _construir_npc(
        entity_id: int,
        pagina_ativa: dict | None,
        parametros_base: dict[str, Any],
    ) -> None:
        """
        NPCs não possuem StatsComponent de combate nem MovimentComponent agressivo.
        Podem ter movimento de patrulha decorativo se a página ativa o definir.
        """
        if pagina_ativa and "movimento" in pagina_ativa:
            EntityFactory._adicionar_moviment_component(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,
            )

    @staticmethod
    def _construir_pacifico(
        entity_id: int,
        nome: str,
        pagina_ativa: dict | None,
        parametros_base: dict[str, Any],
        stats_salvos: dict[str, Any],
    ) -> None:
        """
        Entidades pacíficas possuem HP defensivo mas não atacam ao tocar o jogador.
        """
        esper.add_component(
            entity_id,
            StatsComponent(
                nome=stats_salvos.get("nome", nome),
                classe="",
                hp=stats_salvos.get("hp", 15),
                max_hp=stats_salvos.get("max_hp", 15),
                mp=stats_salvos.get("mp", 0),
                max_mp=stats_salvos.get("max_mp", 0),
                ataque_base=0,   # Pacífico nunca ataca
                defesa_base=stats_salvos.get("defesa_base", 3),
            ),
        )

        if pagina_ativa and "movimento" in pagina_ativa:
            EntityFactory._adicionar_moviment_component(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base=parametros_base,  # sem action_on_touch agressivo
            )

    @staticmethod
    def _construir_item(entity_id: int) -> None:
        """
        Itens são atravessáveis — o jogador pode andar sobre eles
        para coletar. Sobrescrevemos o CollisionComponent adicionado em _construir_base.
        """
        esper.add_component(entity_id, CollisionComponent(solido=False))

    @staticmethod
    def _construir_interativo(
        entity_id: int,
        pagina_ativa: dict | None = None,
        parametros_base: dict[str, Any] | None = None,
    ) -> None:
        """
        Entidades interativas (portas, alavancas, armadilhas) são sólidas,
        sem stats de combate e sem movimento autônomo.
        Apenas o bloco base já é suficiente — método presente para clareza.
        """
        pass  # CollisionComponent(solido=True) já foi adicionado em _construir_base

    @staticmethod
    def _construir_veiculo(
        entity_id: int,
        pagina_ativa: dict | None,
        parametros_base: dict[str, Any],
    ) -> None:
        """
        Veículos possuem MovimentComponent com tipo especial e não atacam.
        """
        if pagina_ativa and "movimento" in pagina_ativa:
            EntityFactory._adicionar_moviment_component(
                entity_id=entity_id,
                pagina_ativa=pagina_ativa,
                parametros_base={},  # sem action_on_touch combate
            )

    @staticmethod
    def _construir_cenario(
        entity_id: int,
        parametros_base: dict[str, Any],
    ) -> None:
        """
        Decorações de cenário podem ser atravessáveis (ex: vegetação baixa)
        ou sólidas (ex: coluna de pedra). Controlado pelo parâmetro "solido".
        Sobrescrevemos o CollisionComponent adicionado em _construir_base.
        """
        e_solido = parametros_base.get("solido", False)
        esper.add_component(entity_id, CollisionComponent(solido=bool(e_solido)))

    # --------------------------------------------------------------------------
    # HELPER INTERNO: adição do MovimentComponent reutilizável
    # --------------------------------------------------------------------------

    @staticmethod
    def _adicionar_moviment_component(
        entity_id: int,
        pagina_ativa: dict[str, Any],
        parametros_base: dict[str, Any],
    ) -> None:
        """Lê os dados de movimento da página ativa e adiciona o MovimentComponent."""
        dados_de_movimento = pagina_ativa.get("movimento", {})
        esper.add_component(
            entity_id,
            MovimentComponent(
                movement_type=dados_de_movimento.get("tipo", "aleatorio"),
                roteiro=dados_de_movimento.get("roteiro", []),
                ciclos=dados_de_movimento.get("ciclos", 0),
                action_on_touch=parametros_base.get("ação", {}),
            ),
        )


# ==============================================================================
# FUNÇÕES AUXILIARES PRIVADAS DO MÓDULO
# ==============================================================================

def _extrair_stats_salvos(dados_salvos: dict[str, Any]) -> dict[str, Any]:
    """Extrai o dicionário de StatsComponent de dados_salvos do SaveDB."""
    if not dados_salvos:
        return {}
    componentes = dados_salvos.get("components", dados_salvos)
    return componentes.get("StatsComponent", {})
