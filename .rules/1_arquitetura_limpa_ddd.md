# Regra 1: Arquitetura Limpa (Clean Architecture) e Domain-Driven Design (DDD)

Esta regra dita a organização das camadas do projeto e o desacoplamento de responsabilidades no desenvolvimento do motor de RPG.

## 1. Separação de Camadas

O código do projeto deve ser rigorosamente dividido em três camadas independentes:

1. **Domínio (Core):**
   - **Localização:** `rpg_api/app/core/` (incluindo `entities/` e `engine/`).
   - **Regra:** Não pode conter dependências ou importações de frameworks externos de banco de dados (como SQLAlchemy, exceto tipos básicos de JSON se estritamente necessários), bibliotecas de UI (Textual) ou frameworks Web (FastAPI).
   - **Responsabilidade:** Contém as entidades de negócio puras (`Personagem`, `ClasseRPG`, `Raca`, `Equipamento`), lógica de cálculo de atributos e o motor ECS (`components`, `systems`, `events`).

2. **Persistência (Models & DB):**
   - **Localização:** `rpg_api/app/models/` e `rpg_api/app/db/`.
   - **Regra:** Gerencia o mapeamento ORM (SQLAlchemy) e a persistência de dados.
   - **Responsabilidade:** Tradução física de tabelas SQLite e colunas JSON para dados relacionais.

3. **Interface de Usuário e Apresentação (View, CLI, API):**
   - **Localização:** `rpg_api/main_cli.py`, `rpg_api/app/views/` (TUI Textual) e `rpg_api/app/fastapi/` (API Web).
   - **Regra:** Consome as camadas de Domínio e Persistência através de adaptadores e controladores.
   - **Responsabilidade:** Renderização em tela, captura de inputs do teclado e respostas HTTP.

---

## 2. Domain-Driven Design (DDD) e o Padrão Mapper (Adapter)

- **Entidades Ricas no Domínio:** Os modelos do domínio (`entities/*`) devem possuir o comportamento e as fórmulas lógicas associadas a eles (ex: `atacar()`, `lancar_magia()`, `atualizar_atributos_totais()`). Eles não devem simplesmente ser classes de transporte de dados anêmicas.
- **Isolamento de Modelos DB:** Nunca passe instâncias das classes do banco de dados (ex: `PersonagemDB`) para dentro dos métodos do domínio.
- **Função de Mapeamento (Mapper):** O controlador (`rpg_api/app/controllers/`) ou a CLI deve mapear as propriedades dos objetos do banco de dados para os construtores puros das entidades do domínio antes de invocar a lógica de simulação ou regras de negócio:
  
  ```python
  # Exemplo de fluxo correto (Padrão Mapper)
  personagem_db = db.query(PersonagemDB).get(1)
  personagem_dominio = converter_para_dominio(personagem_db) # Cria objeto puro Personagem
  
  # A lógica executa apenas sobre a entidade de domínio
  resultado = personagem_dominio.atacar(alvo_dominio)
  ```
- **Persistência de Dados Derivados:** O banco de dados armazena apenas atributos de estado bruto (ex: atributos base do personagem de 0 a 5). Atributos calculados (HP Máximo, Mana Máximo, modificadores de combate) devem ser computados dinamicamente na inicialização do objeto de domínio, evitando redundância de dados no banco.
