# Regra 7: Testes Automatizados e Práticas de TDD (Test-Driven Development)

A qualidade e a integridade lógica do motor de RPG são garantidas por uma suíte robusta de testes automatizados executados via `pytest`.

## 1. Isolamento de Testes de Dados Aleatórios

- **Determinismo nas Rolagens:** Os testes que dependem de resultados de rolagens de dados (ataque, defesa, iniciativa, dano, absorção) não podem ser suscetíveis à aleatoriedade dos geradores de números pseudo-aleatorios.
- **Uso de `monkeypatch`:** Use o utilitário `monkeypatch` do pytest para interceptar a função de rolar dados (ex: `_rolar_d6` ou equivalentes) e forçar retornos determinísticos. Isso permite validar as fórmulas de dano e acerto com exatidão matemática previsível.
  
  ```python
  # Exemplo de mock determinístico no pytest
  def test_ataque_acerto_deterministico(monkeypatch, personagem_atacante, personagem_alvo):
      # Força a rolagem do d6 a retornar sempre 3
      monkeypatch.setattr("rpg_api.app.core.entities.personagens._rolar_d6", lambda: 3)
      
      resultado = personagem_atacante.atacar(personagem_alvo)
      assert resultado["acertou"] is True
  ```

---

## 2. Gerenciamento e Limpeza de Banco de Dados de Teste

- **Uso do Banco de Memória:** Os testes de integração de banco de dados e ORM devem ser executados com a variável `TEST_VERSION=True`, forçando a conexão a usar o SQLite em memória ou o arquivo `rpg_teste.db`.
- **Fixtures de Transação / Hooks de Setup/Teardown:**
  - Garanta que cada módulo de teste inicialize a estrutura de tabelas do banco de dados antes da execução (`Base.metadata.create_all(engine)`) e realize a limpeza completa ao final (`Base.metadata.drop_all(engine)`).
  - Use fixtures do pytest com escopo de função (`scope="function"`) para limpar ou reverter transações, garantindo que um teste não influencie os dados do teste seguinte.

---

## 3. Cobertura de Código Mínima

Toda nova funcionalidade implementada no Domínio (Core), no motor ECS (Esper) ou nas rotas de API deve obrigatoriamente possuir testes unitários correspondentes sob a pasta `tests/`. Garanta cobertura para:
- Casos felizes (sucesso das regras).
- Casos de exceção (ex: ValueError disparado ao aprender magias sem requisitos elementais).
- Mapeamento e conversão de modelos (Mapper do Banco de Dados para Entidade).
