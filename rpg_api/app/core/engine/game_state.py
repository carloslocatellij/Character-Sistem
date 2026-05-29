# app/core/engine/game_state.py
from app.models.plataforma_db import SaveDB

class GameStateManager:
    """
    Gerenciador de Estado Global de Altura Máxima.
    Suporta persistência multi-jogo isolada no banco de dados.
    """
    def __init__(self):
        self.switches: dict[str, bool] = {}
        # Suporta implicitamente: int, float, bool, str (Perfeito para nomes de NPCs, facções, etc)
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

    def set_variable(self, nome: str, valor: any):
        self.variables[nome] = valor

    def modificar_variavel(self, nome: str, operacao: str, valor: any):
        """Modifica incrementalmente se for numérico ou substitui via 'set'."""
        atual = self.get_variable(nome, 0)
        
        if operacao == "set":
            self.variables[nome] = valor
            return
            
        if isinstance(atual, (int, float)) and isinstance(valor, (int, float)):
            if operacao == "add": self.variables[nome] = atual + valor
            elif operacao == "sub": self.variables[nome] = atual - valor

    # ==========================================
    # PERSISTÊNCIA MULTIPLAYER / MULTI-JOGO
    # ==========================================
    def salvar_sessao_no_banco(self, ecs_manager, db_session, usuario_id: int, cenario_id: int, mapa_atual_id: int, slot: int = 1):
        """
        Gera um snapshot completo em tempo de execução de todas as entidades do mapa 
        e salva no banco isolado por Usuário e Cenário.
        """
        snapshot_entidades = {}

        # 1. Captura o estado de todas as entidades ativas na Engine lúdica
        for ent_id, componentes in ecs_manager.entities.items():
            pos = componentes.get("PositionComponent")
            stats = componentes.get("StatsComponent")
            inv = componentes.get("InventoryComponent")
            eqp = componentes.get("EquipmentComponent")
            interact = componentes.get("InteractableComponent")
            render = componentes.get("RenderComponent")
            ai = componentes.get("AIComponent")

            if pos:
                dados_entidade = {
                    "pos_x": pos.x,
                    "pos_y": pos.y,
                    "direcao": pos.direcao_olhar,
                    "render_emoji": render.emoji if render else "👾"
                }

                if stats:
                    dados_entidade["stats"] = {
                        "nome": stats.nome,
                        "hp": stats.hp,
                        "max_hp": stats.max_hp,
                        "mp": stats.mp,
                        "max_mp": stats.max_mp,
                        "ataque_base": stats.ataque_base, # 🔑 Chave padronizada
                        "defesa_base": stats.defesa_base
                    }

                if inv: dados_entidade["inventario"] = inv.itens
                if eqp: dados_entidade["equipamento"] = {"arma": eqp.arma, "armadura": eqp.armadura}
                if interact: dados_entidade["is_active"] = interact.is_active

                # Salva o estado e os IDs textuais no dicionário serializável
                snapshot_entidades[str(ent_id)] = dados_entidade

        # 2. Consolida o pacote de sessão independente
        dados_sessao_completa = {
            "mapa_atual_id": mapa_atual_id,
            "switches": self.switches,
            "variables": self.variables,
            "entidades": snapshot_entidades
        }

        # 3. Executa a gravação atómica no SQL
        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot
        ).first()

        if save_db:
            save_db.dados_sessao = dados_sessao_completa
        else:
            novo_save = SaveDB(
                usuario_id=usuario_id,
                cenario_id=cenario_id,
                slot_numero=slot,
                dados_sessao=dados_sessao_completa
            )
            db_session.add(novo_save)

        db_session.commit()

    def carregar_sessao_do_banco(self, db_session, usuario_id: int, cenario_id: int, slot: int = 1) -> dict | None:
        """Busca os dados de sessão salvos. Retorna o JSON completo ou None se for um jogo novo."""
        save_db = db_session.query(SaveDB).filter(
            SaveDB.usuario_id == usuario_id,
            SaveDB.cenario_id == cenario_id,
            SaveDB.slot_numero == slot
        ).first()

        if not save_db:
            return None

        # Restaura os switches e variáveis globais da campanha para a memória do gestor
        self.switches = save_db.dados_sessao.get("switches", {})
        self.variables = save_db.dados_sessao.get("variables", {})

        return save_db.dados_sessao