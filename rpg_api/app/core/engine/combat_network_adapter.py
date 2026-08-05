"""
Adapter de rede para combate multiplayer (PvP).

Este módulo define os contratos e interfaces para sincronização de turnos
entre dois jogadores via rede. Funciona como stub determinístico nesta versão,
pronto para substituição por implementação WebSocket/Supabase Realtime.

Arquitetura preparada (Ponto 5 do plano):
- CombatNetworkAdapter: Interface de envio/recebimento de ações de turno
- AcaoCombateRede: Payload tipado para sincronização de turnos
- SessaoCombatePvP: Metadados de uma sessão de combate entre dois jogadores
"""
import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")


# ==============================================================================
# CONTRATOS DE DADOS
# ==============================================================================

@dataclass
class AcaoCombateRede:
    """
    Payload tipado para sincronização de turno via rede.
    Esta estrutura é serializada (JSON) e enviada ao oponente.
    """
    jogador_id: str               # ID único do jogador remetente
    session_id: str               # ID da sessão de combate PvP
    acao: str                     # "ataque" | "magia" | "fugir" | "item"
    turno_idx: int                # Índice do turno para validação de ordem
    timestamp: float = field(default_factory=time.time)
    dados_extras: Dict[str, Any] = field(default_factory=dict)  # Dados adicionais (ex: qual magia)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionário (para envio via WebSocket/HTTP)."""
        return {
            "jogador_id": self.jogador_id,
            "session_id": self.session_id,
            "acao": self.acao,
            "turno_idx": self.turno_idx,
            "timestamp": self.timestamp,
            "dados_extras": self.dados_extras,
        }

    @classmethod
    def from_dict(cls, dados: Dict[str, Any]) -> "AcaoCombateRede":
        """Desserializa de dicionário (para recebimento via WebSocket/HTTP)."""
        return cls(
            jogador_id=dados["jogador_id"],
            session_id=dados["session_id"],
            acao=dados["acao"],
            turno_idx=dados["turno_idx"],
            timestamp=dados.get("timestamp", time.time()),
            dados_extras=dados.get("dados_extras", {}),
        )


@dataclass
class SessaoCombatePvP:
    """Metadados de uma sessão de combate entre dois jogadores humanos."""
    session_id: str
    jogador_local_id: str
    jogador_remoto_id: str
    jogador_local_vai_primeiro: bool = True
    turno_atual: int = 0
    estado: str = "aguardando_inicio"  # "aguardando_inicio" | "em_andamento" | "encerrado"
    criado_em: float = field(default_factory=time.time)


# ==============================================================================
# ADAPTER DE REDE (STUB)
# ==============================================================================

class CombatNetworkAdapter:
    """
    Adapter preparatório para suporte a combates PvP online.

    Esta classe funciona como stub determinístico que poderá ser substituída
    por implementação WebSocket real (Supabase Realtime, asyncio WebSocket nativo,
    ou qualquer protocolo de mensageria em tempo real).

    ## Para implementar WebSocket real (substitua os métodos abaixo):
    - `enviar_acao()` → await websocket.send(acao.to_dict())
    - `aguardar_acao_oponente()` → await websocket.recv() com timeout
    - `conectar()` → websocket = await websockets.connect(url, headers=...)
    - `desconectar()` → await websocket.close()
    """

    def __init__(self):
        self.sessao_ativa: Optional[SessaoCombatePvP] = None
        self.modo_online: bool = False
        self._callback_acao_recebida: Optional[Callable[[AcaoCombateRede], None]] = None
        self._websocket = None  # Placeholder para futura conexão WS

    def registrar_callback_acao(
        self, callback: Callable[[AcaoCombateRede], None]
    ) -> None:
        """
        Registra o callback que será invocado quando uma ação do oponente
        chegar pela rede. O callback recebe um objeto AcaoCombateRede.
        """
        self._callback_acao_recebida = callback
        logging.info("CombatNetworkAdapter: callback de ação registrado.")

    async def conectar(self, server_url: str, session_id: str, jogador_id: str) -> bool:
        """
        [STUB] Conecta ao servidor de combate PvP.

        TODO: Implementar com:
            self._websocket = await websockets.connect(
                f"{server_url}/combat/{session_id}",
                extra_headers={"X-Player-ID": jogador_id}
            )
        """
        logging.info(
            f"[STUB] Tentativa de conexão PvP: servidor={server_url}, "
            f"sessão={session_id}, jogador={jogador_id}"
        )
        self.modo_online = False  # Stub: sempre offline
        return False

    async def desconectar(self) -> None:
        """
        [STUB] Encerra a conexão com o servidor de combate.

        TODO: Implementar com: await self._websocket.close()
        """
        logging.info("[STUB] Desconexão PvP simulada.")
        self.modo_online = False
        self.sessao_ativa = None

    async def enviar_acao(self, acao: AcaoCombateRede) -> bool:
        """
        [STUB] Envia a ação do turno para o oponente via rede.

        TODO: Implementar com:
            await self._websocket.send(json.dumps(acao.to_dict()))
            return True

        Retorna True em caso de sucesso, False em caso de falha de rede.
        """
        logging.info(f"[STUB] Ação enviada (simulada): {acao.to_dict()}")
        return False  # Stub: sempre falha de rede

    async def aguardar_acao_oponente(
        self, timeout_segundos: float = 30.0
    ) -> Optional[AcaoCombateRede]:
        """
        [STUB] Aguarda a ação do oponente com timeout.

        TODO: Implementar com:
            mensagem = await asyncio.wait_for(
                self._websocket.recv(), timeout=timeout_segundos
            )
            return AcaoCombateRede.from_dict(json.loads(mensagem))

        Retorna None em caso de timeout ou desconexão.
        """
        logging.info(
            f"[STUB] Aguardando ação do oponente (timeout={timeout_segundos}s) — não implementado."
        )
        await asyncio.sleep(0)  # Yield para não bloquear
        return None

    def iniciar_sessao_pvp(
        self,
        session_id: str,
        jogador_local_id: str,
        jogador_remoto_id: str,
        vai_primeiro: bool = True,
    ) -> SessaoCombatePvP:
        """Cria e registra uma nova sessão de combate PvP."""
        self.sessao_ativa = SessaoCombatePvP(
            session_id=session_id,
            jogador_local_id=jogador_local_id,
            jogador_remoto_id=jogador_remoto_id,
            jogador_local_vai_primeiro=vai_primeiro,
        )
        logging.info(
            f"Sessão PvP criada: {session_id} | "
            f"{jogador_local_id} vs {jogador_remoto_id}"
        )
        return self.sessao_ativa

    def encerrar_sessao(self, motivo: str = "combate_encerrado") -> None:
        """Finaliza a sessão ativa de combate PvP."""
        if self.sessao_ativa:
            self.sessao_ativa.estado = "encerrado"
            logging.info(
                f"Sessão PvP encerrada: {self.sessao_ativa.session_id} | Motivo: {motivo}"
            )
        self.sessao_ativa = None
