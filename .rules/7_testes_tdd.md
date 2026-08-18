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


## 4. Testes de Behavior e User Interface:

Todo teste assíncrono no Textual segue o padrão Arrange-Act-Assert dentro de uma função async def:
- Exemplo de teste de batalha:
  ```
  import pytest
  from app.main_cli import RPGApp  #
  from app.views.battle_screen import BarraStatusCombate

  @pytest.mark.asyncio
  async def test_fluxo_da_aplicacao():
      app = RPGApp()
      
      # Na tela de Inicio vai para Jogar
      async with app.run_test() as pilot:
          # 1. Agir (Simular interações do usuário)
          await pilot.press("tab")      # Move o foco
          await pilot.press("tab")      # Move o foco
          await pilot.press("tab")      # Move o foco
          await pilot.press("tab")      # Move o focc
          await pilot.press("enter")    # Pressiona um botão
          await pilot.press("left",)    #  Olha para a esquerda
          await pilot.press("enter")    # Isto vai iniciar um combate com o evento de nome ev_13_16.


          # 2. Asseverar (Verificar o estado da tela ou dados)
          # O pilot.app dá acesso direto à instância rodando/
          assert ' 18/18' in pilot.app.BarraStatusCombate # Verifica se hp do heroi_1 foi mostrado 
          assert ' 23/23' in pilot.app.BarraStatusCombate #Verifica se hp do inimigo_1 foi mostrado

  ```

Principais Ferramentas do Objeto pilot:
  - O objeto pilot retornado pelo run_test() é o seu testador virtual.
  
  Estes são os métodos mais importantes para controlar o app:
  - await pilot.press(*keys): Simula o pressionamento de teclas do teclado (ex: "ctrl+q", "down", "enter").
  - await pilot.click(selector): Simula um clique do mouse usando seletores CSS (ex: await pilot.click("#botao-salvar")).
  - await pilot.pause(seconds): Pausa o teste temporariamente para renderização de animações ou processos em background.
  - await pilot.wait_for_scheduled_animations(): Garante que todas as animações planejadas na tela terminaram antes de prosseguir com as checagens.