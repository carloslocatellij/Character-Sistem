import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from app.core.equipamentos import Arma, Armadura, Escudo, Item
from app.core.habilidades_magias import Magia, Habilidade, Efeito
from app.core.emojis import dict_emoji_racas
from math import ceil

# ... (Mantenha as classes Raca e ClasseRPG exatamente como fizemos antes) ...

@dataclass
class Raca:
    nome: str
    bonus_atributos: Dict[str, int] = field(default_factory=dict)
    emoji: str = "👤"
    
    def __str__(self) -> str:
      return f"{dict_emoji_racas.get(self.nome.lower(), self.emoji)}"

@dataclass
class ClasseRPG:
    nome: str
    bonus_caminhos: Dict[str, int] = field(default_factory=dict) # Agora é um dicionário! Ex: {"fogo": 1}
    habilidades: List[str] = field(default_factory=list)
    #bonus_atributos: Dict[str, int] = field(default_factory=dict)

# ==========================================
# DOMÍNIO: PERSONAGEM PRINCIPAL
# ==========================================

class Personagem:
    def __init__(self, nome: str, 
                 nivel: int,
                 raca: Raca,
                 classe_rpg: ClasseRPG,
                 forca_base: int,
                 agilidade_base: int,
                 res_base: int,
                 perc_base: int,
                 exub_base: int):
        
        self.nome = nome
        self.nivel = nivel
        self.raca = raca
        self.classe = classe_rpg
        
        self.atributos_base = {
            "forca": forca_base, "agilidade": agilidade_base,
            "resistencia": res_base, "percepcao": perc_base, "exuberancia": exub_base
        }
        
        self.atributos_totais = self.atributos_base.copy()
        
        self.mao_direita: Optional[Arma] = None
        self.mao_esquerda: Optional[Item] = None 
        self.armadura: Optional[Armadura] = None
        self.itens_corpo: List[Item] = [] 
        self.equipamentos: List[Item] = [] 
        self.efeitos_ativos: List[Dict] = []
        
        self.pv_max = 0
        self.pv_atual = 0
        self.pm_max = 0
        self.pm_atual = 0
        self.mod_atq_corpo = 0
        self.mod_atq_distancia = 0
        
        #Dicionário base dos Caminhos de Magia
        self.caminhos_magia_base = {
            "luz": 0, "trevas": 0, "fogo": 0, "água": 0, "ar": 0, "terra": 0
        }
        self.caminhos_magia = self.caminhos_magia_base.copy()
        self.magias_conhecidas: List[Magia] = []
        
        self.atualizar_atributos_totais()

    def __str__(self):
        str_representante = f"""
        {self.nome} {self.raca} | 
        |Nv: {self.nivel} |{self.classe.nome}
        |💚: {self.pv_atual}/{self.pv_max} |🔮: {self.pm_atual}/{self.pm_max}
        |{self.mao_direita or "👊"}: {self.mod_atq_corpo} |🏹: {self.mod_atq_distancia} 
        |{self.armadura or "🦵"}: {self.armadura.defesa if self.armadura else 0} |{self.mao_esquerda or "🤜"}: 
        {self.mao_esquerda.defesa_extra if isinstance(self.mao_esquerda, Escudo) else 0}
        |🪄: {self.classe.habilidades} | {self.efeitos_ativos}
        """

        # Adicionar informações de efeitos ativos
        if self.efeitos_ativos:
            str_efeitos = ", ".join([f"{ef.nome}{ef} ({dur} turnos)" for ef, dur in self.efeitos_ativos])
            str_representante += f" |✨ Efeitos Ativos: {str_efeitos}"

        return str_representante

    # ... (Mantenha os métodos atualizar_atributos_totais, _calcular_status_derivados e reset_status) ...
    def atualizar_atributos_totais(self):
        """Recalcula atributos E Caminhos de Magia."""
        self.atributos_totais = self.atributos_base.copy()
        self.caminhos_magia = self.caminhos_magia_base.copy()
        
        # Bônus de Atributos
        for attr, valor in self.raca.bonus_atributos.items():
            if attr in self.atributos_totais: self.atributos_totais[attr] += valor
        # for attr, valor in self.classe.bonus_atributos.items():
        #     if attr in self.atributos_totais: self.atributos_totais[attr] += valor
            
        # NOVO: Bônus de Caminhos de Magia da Classe
        if self.classe.bonus_caminhos:
            for caminho, pontos in self.classe.bonus_caminhos.items():
                if caminho in self.caminhos_magia:
                    self.caminhos_magia[caminho] += pontos
                
        self._calcular_status_derivados()

    def _calcular_status_derivados(self):
        res = self.atributos_totais["resistencia"]
        perc = self.atributos_totais["percepcao"]
        exub = self.atributos_totais["exuberancia"]
        forca = self.atributos_totais["forca"]
        agi = self.atributos_totais["agilidade"]

        self.pv_max =  int(7+ (ceil(self.nivel * ceil((res+2) / 2) + ceil((self.nivel + res) *3)))) #int((((self.nivel + 4) / 4) * (res + 1.5)) ** 2)
        self.pm_max =  int((ceil((self.nivel + 5) / 4) * ceil((perc + exub + 1) / 2)) * 3) #int((((self.nivel + 5) / 5) * ((perc + exub + 0.5) / 1.5)) ** 2)
        self.mod_atq_corpo = int(self.nivel * ceil(forca + (agi / 2))) #int((((self.nivel + 5) / 5) * (forca + (agi / 2))) ** 2)
        self.mod_atq_distancia = int(self.nivel * ceil(agi + (forca / 2))) #int((((self.nivel + 5) / 5) * (agi + (forca / 2))) ** 2)
        
        # self.pv_max =  int((((self.nivel + 4) / 4) * (res + 1.5)) ** 2)
        # self.pm_max =  int((((self.nivel + 5) / 5) * ((perc + exub + 0.5) / 1.5)) ** 2)
        # self.mod_atq_corpo = int((((self.nivel + 5) / 5) * (forca + (agi / 2))) ** 2)
        # self.mod_atq_distancia = int((((self.nivel + 5) / 5) * (agi + (forca / 2))) ** 2)
        
        
        self.reset_status()

    def reset_status(self):
        self.pv_atual = self.pv_max
        self.pm_atual = self.pm_max

    # ==========================================
    # MECÂNICAS DE COMBATE E SISTEMA
    # ==========================================

    def _rolar_d6(self, quantidade: int) -> int:
        """Utilitário interno para rolagens de dados (Domain Service embutido)."""
        if quantidade <= 0: return 0
        return sum(random.randint(1, 6) for _ in range(quantidade))

    def calcular_defesa_esquiva(self) -> int:
        """1d6 + Agilidade + Defesa do Escudo (se houver)."""
        agi = self.atributos_totais["agilidade"]
        rolagem = self._rolar_d6(2 + int(agi // 2)) # Mais agilidade dá direito a rolar mais dados
        bonus_escudo = self.mao_esquerda.defesa_extra if isinstance(self.mao_esquerda, Escudo) else 0
        return rolagem + (agi * (bonus_escudo+1))

    def receber_dano(self, dano_bruto: int) -> Dict[str, Any]:
        """Processa a absorção de dano (1d6 por Res + Armadura)."""
        res = self.atributos_totais["resistencia"]
        absorcao_dados = self._rolar_d6((res+1) // 2) # Cada 2 pontos de Resistencia dão direito a 1d6 de absorção
        bonus_armadura = self.armadura.defesa if self.armadura else 0
        
        defesa_total = absorcao_dados + bonus_armadura
        dano_real = max(0, dano_bruto - defesa_total)
        
        self.pv_atual -= dano_real
        
        # Retorna o "Evento" do que acabou de acontecer
        return {
            "dano_recebido": dano_real,
            "dano_bloqueado": defesa_total,
            "absorcao_dados": absorcao_dados,
            "bonus_armadura": bonus_armadura,
            "pv_restante": self.pv_atual,
            "morreu": self.pv_atual <= 0
        }

    def receber_dano_de_efeito(self, dano: int):
        """Dano direto que ignora armadura (ex: veneno)."""
        self.pv_atual -= dano
        return {"dano_recebido": dano, "pv_restante": self.pv_atual, "morreu": self.pv_atual <= 0}

    def atacar(self, alvo: 'Personagem') -> Dict[str, Any]:
        """Realiza a mecânica completa de ataque contra um alvo."""
        forca = self.atributos_totais["forca"]
        # 1. Identifica a arma ou usa ataque desarmado
        arma = self.mao_direita
        arma_nome = arma.nome if isinstance(arma, Arma) else "Ataque Desarmado"
        tipo_atq = arma.tipo if isinstance(arma, Arma) else "corpo"
        dano_arma = arma.dano if isinstance(arma, Arma) else 0
        
        # 2. Modificadores e Rolagem de Acerto (3d6)
        modificador = self.mod_atq_corpo if tipo_atq == "corpo" else self.mod_atq_distancia
        rolagem_ataque = self._rolar_d6(3 + int(forca // 3))
        ataque_total = rolagem_ataque + modificador
        defesa_alvo = alvo.calcular_defesa_esquiva()
        
        acertou = ataque_total > defesa_alvo
        resultado = {
            "atacante": self.nome, "alvo": alvo.nome,
            "arma_nome": arma_nome,
            "acertou": acertou, "ataque_total": ataque_total, "rolagem_ataque": rolagem_ataque,
            "defesa_alvo": defesa_alvo, "dano_causado": 0
        }

        # 3. Cálculo de Dano (se acertou)
        if acertou:
            atributo_dano = self.atributos_totais["forca"] if tipo_atq == "corpo" else self.atributos_totais["agilidade"]
            dano_bruto = self._rolar_d6(atributo_dano) + dano_arma
            
            # Delega a responsabilidade de sofrer o dano para o alvo
            evento_dano = alvo.receber_dano(dano_bruto)
            resultado["dano_causado"] = evento_dano["dano_recebido"]
            resultado["dano_bruto"] = dano_bruto
            resultado["absorcao_dados"] = evento_dano["absorcao_dados"]
            resultado["bonus_armadura"] = evento_dano["bonus_armadura"]
            resultado["defesa_total"] = evento_dano["dano_bloqueado"]
            resultado["pv_restante"] = evento_dano["pv_restante"]
            resultado["alvo_morreu"] = evento_dano["morreu"]

        return resultado
    
    
    # ==========================================
    # GERENCIAMENTO DE EFEITOS
    # ==========================================
    
    def aplicar_efeito(self, efeito: Efeito):
        """Adiciona um efeito à lista de ativos."""
        # Se for um buff de atributo, aplicamos imediatamente
        if efeito.tipo in ["buff_atributo", "debuff_atributo"] and efeito.atributo_alvo:
            modificador = efeito.valor if efeito.tipo == "buff_atributo" else -efeito.valor
            self.atributos_totais[efeito.atributo_alvo] += modificador
            self._calcular_status_derivados() # Recalcula vida/ataque se o atributo mudar
            
        # Guarda na lista para controle de tempo
        from copy import deepcopy
        self.efeitos_ativos.append(deepcopy(efeito)) # Copia para não alterar o objeto base
        

    def finalizar_turno(self) -> List[Dict]:
        """Roda no fim do turno: processa venenos, curas e reduz duração."""
        relatorio_efeitos = []
        efeitos_restantes = []

        for efeito in self.efeitos_ativos:
            resultado = efeito.processar_efeito(self)
            relatorio_efeitos.append(resultado)
            
            if efeito.duracao_turnos > 0:
                efeitos_restantes.append(efeito)
            else:
                # Se o efeito acabou e era um buff, removemos o modificador
                if efeito.tipo in ["buff_atributo", "debuff_atributo"] and efeito.atributo_alvo:
                    modificador = -efeito.valor if efeito.tipo == "buff_atributo" else efeito.valor
                    self.atributos_totais[efeito.atributo_alvo] += modificador
                    self._calcular_status_derivados()

        self.efeitos_ativos = efeitos_restantes
        return relatorio_efeitos
    
    # ==========================================
    # MAGIAS E HABILIDADES
    # ==========================================

    # ==========================================
    # VALIDAÇÃO DE REQUISITOS DE MAGIA (SPEC)
    # ==========================================

    def validar_requisitos_magia(self, magia: Magia) -> bool:
        """Verifica se o personagem tem a Exuberância e os Pontos nos Caminhos exigidos."""
        # 1. Verifica Exuberância
        if self.atributos_totais["exuberancia"] < magia.requisito_exuberancia:
            return False
            
        # 2. Verifica os Caminhos
        for caminho_exigido, pontos_exigidos in magia.requisito_caminhos.items():
            # Pega os pontos que o personagem tem (ou 0 se o caminho não existir no dicionário)
            pontos_do_personagem = self.caminhos_magia.get(caminho_exigido, 0)
            if pontos_do_personagem < pontos_exigidos:
                return False
                
        return True
    
    def aprender_magia(self, magia: Magia):
        """Tenta adicionar a magia à lista do personagem, levanta Exceção se não puder."""
        if self.validar_requisitos_magia(magia):
            self.magias_conhecidas.append(magia)
        else:
            # Levantando uma exceção conforme exigido na SPEC.md
            raise ValueError(f"O personagem {self.nome} não atende aos requisitos para aprender '{magia.nome}'.")
        
    def lancar_magia(self, magia: Magia, alvo: 'Personagem') -> Dict:
        """Executa a magia conforme MANUAL.md (Teste Resistido)."""
        if self.pm_atual < magia.custo_pm:
            return {"atacante": self.nome, "sucesso": False, "motivo": "Mana insuficiente"}
            
        if not self.validar_requisitos_magia(magia):
             return {"atacante": self.nome, "sucesso": False, "motivo": "Exuberância insuficiente"}

        self.pm_atual -= magia.custo_pm
        
        # Teste de Ataque Mágico (Exuberância do Atacante vs Dificuldade Base 4)
        # Assumindo que a força do caminho dá bônus. Para simplificar, usamos Exuberância + Rolar d6
        ataque_magico = self._rolar_d6(3) + self.atributos_totais["exuberancia"]
        
        # Alvo tenta esquivar com agilidade ou resistir
        defesa_alvo = alvo.calcular_defesa_esquiva()
        
        acertou = ataque_magico > defesa_alvo
        evento = {
            "atacante": self.nome, "alvo": alvo.nome, "magia": magia.nome,
            "sucesso": acertou, "pm_restante": self.pm_atual, "dano_causado": 0
        }

        if acertou:
            # Magias ignoram armadura convencional, dão dano direto ou aplicam efeito
            if magia.dano_base > 0:
                dano_final = self._rolar_d6(1) + magia.dano_base # Dano = 1d6 + Base
                evento_dano = alvo.receber_dano_de_efeito(dano_final)
                evento["dano_causado"] = evento_dano["dano_recebido"]
                evento["alvo_morreu"] = evento_dano["morreu"]
                
            if magia.efeito_aplicado:
                alvo.aplicar_efeito(magia.efeito_aplicado)
                evento["efeito_aplicado"] = magia.efeito_aplicado.nome

        return evento