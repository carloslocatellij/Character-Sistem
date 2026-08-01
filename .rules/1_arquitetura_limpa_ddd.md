# Regra 1: Arquitetura Limpa (Clean Architecture) + Domain-Driven Design (DDD)

Organiza camadas, desacopla responsabilidades no motor RPG.

## 1. Separação de Camadas

Código dividido em 3 camadas independentes:

0. Código limpo: Nomes claros, auto explicativos, extenso. Código Python tipado.

1. **Domínio (Core):**
   - **Local:** `rpg_api/app/core/` (`entities/`, `engine/`).
   - **Regra:** Zero dependências de DB (SQLAlchemy, exceto tipos JSON), UI (Textual), Web (FastAPI).
   - **Responsabilidade:** Entidades negócio puras (`Personagem`, `ClasseRPG`, `Raca`, `Equipamento`), cálculo de atributos, motor ECS (`components`, `systems`, `events`).

2. **Persistência (Models & DB):**
   - **Local:** `rpg_api/app/models/`, `rpg_api/app/db/`.
   - **Regra:** Gerencia mapeamento ORM (SQLAlchemy), persistência.
   - **Responsabilidade:** Tradução tabelas SQLite, colunas JSON para dados relacionais.

3. **Interface (View, CLI, API):**
   - **Local:** `rpg_api/main_cli.py`, `rpg_api/app/views/` (TUI Textual), `rpg_api/app/fastapi/` (API Web).
   - **Regra:** Consome Domínio + Persistência via adaptadores/controladores.
   - **Responsabilidade:** Renderização, input teclado, respostas HTTP.

---

## 2. DDD + Mapper (Adapter)

- **Entidades Ricas:** Modelos domínio (`entities/*`) possuem comportamento, fórmulas (`atacar()`, `lancar_magia()`, `atualizar_atributos_totais()`). Não classes anêmicas.
- **Isolamento Modelos DB:** Isole classes DB (`PersonagemDB`) dos métodos domínio.
- **Mapper:** Controlador (`rpg_api/app/controllers/`) ou CLI mapeia DB para construtores puros domínio antes da lógica.
  
  ```python
  # Exemplo de fluxo correto (Padrão Mapper)
  personagem_db = db.query(PersonagemDB).get(1)
  personagem_dominio = converter_para_dominio(personagem_db) # Cria objeto puro Personagem
  
  # A lógica executa apenas sobre a entidade de domínio
  resultado = personagem_dominio.atacar(alvo_dominio)
  ```
- **Persistência Dados Derivados:** Banco armazena apenas estado bruto (ex: atributos base 0-5). Atributos calculados (HP/Mana Máximo, mods) computados dinamicamente na inicialização do objeto domínio. Evita redundância.
