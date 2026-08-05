# Regra 7: Testes/TDD

Qualidade e integridade garantidas por `pytest`.

## 1. Isolamento Dados Aleatórios

- **Determinismo:** Testes de rolagem (ataque, defesa, dano) não podem ter aleatoriedade.
- **`monkeypatch`:** Use `monkeypatch` (pytest) para interceptar função rolar dados (`_rolar_d6`) e forçar retornos determinísticos. Valide fórmulas com precisão.
  
  ```python
  # Exemplo de mock determinístico no pytest
  def test_ataque_acerto_deterministico(monkeypatch, personagem_atacante, personagem_alvo):
      # Força a rolagem do d6 a retornar sempre 3
      monkeypatch.setattr("rpg_api.app.core.entities.personagens._rolar_d6", lambda: 3)
      
      resultado = personagem_atacante.atacar(personagem_alvo)
      assert resultado["acertou"] is True
  ```

---

## 2. Limpeza DB Teste

- **Banco Memória:** Testes integração ORM com `TEST_VERSION=True` (SQLite memória/`rpg_teste.db`).
- **Setup/Teardown:**
  - Iniciar tabelas antes (`Base.metadata.create_all(engine)`), limpar ao final (`Base.metadata.drop_all(engine)`).
  - Fixtures `scope="function"` para limpar/reverter transações entre testes.

---

## 3. Cobertura Mínima

Nova funcionalidade (Domínio, ECS, API) requer testes unitários em `tests/`. Cubra:
- Casos felizes (sucesso regras).
- Casos exceção (ex: erro requisitos magia).
- Mapeamento (DB para Entidade).
