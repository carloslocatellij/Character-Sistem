import esper
from app.models.plataforma_db import SaveDB
from app.core.engine.components import PositionComponent, StatsComponent, RenderComponent, InteractableComponent


class GameStateManager:
    """
    Gerenciador de Estado Global e Persistência de Sessão (Saves).
    Adaptado para capturar e restaurar snapshots do Esper ECS.
    """

    def __init__(self):
        self.switches: dict[str, bool] = {}
        self.variables: dict[str, any] = {}

    # ==========================================
    # GESTÃO DE VARIÁVEIS DO UNIVERSO (LIVRES)
    # ==========================================
    def get_switch(self, nome: str) -> bool:
        return self.switches.get(nome, False)

    def set_switch(self, nome: str, valor: bool):
        self.switches[nome] = valor

    def get_variable(self, nome: str, padrao=0) -> any:
        return self.variables.get(nome, padrao)

    def set_variable(self, nome: str,  valor: any):
        self.variables[nome] = valor
        
        

    def modificar_variavel(self, nome: str, operacao: str, valor: any):
        atual = self.get_variable(nome, 0)
        if operacao == "=":
            self.variables[nome] = valor
            return
        if isinstance(atual, (int, float)) and isinstance(valor, (int, float)):
            if operacao == "+":
                self.variables[nome] = atual + valor
            elif operacao == "-":
                self.variables[nome] = atual - valor
            elif operacao == "*":
                self.variables[nome] = atual * valor
            elif operacao == "/":
                self.variables[nome] = atual / valor if valor != 0 else atual
            else:
                raise ValueError(f"Operação inválida: {operacao}")
        else:
            raise TypeError("As variáveis devem ser numéricas para operações aritméticas.")


    # ==========================================
    # PERSISTÊNCIA ATÔMICA DO MUNDO (ESPER ECS ➡️ BD)
    # ==========================================
    def salvar_sessao_no_banco(self, db_session, usuario_id: int, cenario_id: int, mapa_atual_id: int = 1, slot: int = 1) -> int:
        """
        Captura o estado dos seletores e gera um snapshot das entidades vivas
        no Esper ECS, gravando em JSON na tabela 'saves'.
        """
        snapshot_entidades = {}

        # 🧠 Query em lote no Esper para salvar a posição e dados de cada entidade mutável
        for ent_id, (pos, ren) in esper.get_components(PositionComponent, RenderComponent):
            # Tenta pegar componentes opcionais (como os status de vida e parâmetros dinâmicos)
            stats = esper.component_for_entity(
                ent_id, StatsComponent) if esper.has_component(ent_id, StatsComponent) else None
            interact = esper.component_for_entity(ent_id, InteractableComponent) if esper.has_component(
                ent_id, InteractableComponent) else None

            snapshot_entidades[str(ent_id)] = {
                "components": {
                    "PositionComponent": {"x": pos.x, "y": pos.y},
                    "RenderComponent": {"emoji": ren.emoji},
                    "StatsComponent": {
                        "nome": stats.nome, "classe": stats.classe,
                        "hp": stats.hp, "max_hp": stats.max_hp,
                        "mp": stats.mp, "max_mp": stats.max_mp,
                        "ataque_base": stats.ataque_base, "defesa_base": stats.defesa_base
                    } if stats else None,
                    "InteractableComponent": {
                        "event_type": interact.event_type,
                        "parametros": interact.parametros
                    } if interact else None
                }
            }

        # Consolida o pacote que será persistido na coluna JSON do banco
        dados_sessao_completa = {
            "mapa_atual_id": mapa_atual_id,
            "switches": self.switches,
            "variables": self.variables,
            "entidades": snapshot_entidades
        }

        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot
        ).first()

        if save_db:
            save_db.dados_sessao = dados_sessao_completa
        else:
            save_db = SaveDB(
                usuario_id=usuario_id,
                cenario_id=cenario_id,
                slot_numero=slot,
                dados_sessao=dados_sessao_completa
            )
            db_session.add(save_db)

        db_session.commit()
        return save_db.id

    def carregar_sessao_do_banco(self, db_session, usuario_id: int, cenario_id: int, slot: int = 1) -> dict | None:
        """Busca a sessão persistida no BD e restaura os dicionários de controle da campanha."""
        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot
        ).first()

        if not save_db:
            return None

        dados = save_db.dados_sessao or {}
        self.switches = dados.get("switches", {})
        self.variables = dados.get("variables", {})

        return dados
