# Regras de Desenvolvimento do Projeto (SisCharlesRpg)

Bem-vindo ao projeto SisCharlesRpg. Como agente de IA, você deve seguir estritamente as regras de desenvolvimento definidas para pautar o projeto. Elas estão organizadas por temas e localizadas na pasta [.rules/](file:///[$HOME]/Dev/Character-Sistem/.rules/).

Consulte as regras específicas sempre que for implementar ou depurar o código:


1. **[Arquitetura Limpa e DDD](file:///[$HOME]/Dev/Character-Sistem/.rules/1_arquitetura_limpa_ddd.md)**: Regula a separação rígida de camadas entre Domínio (Core), Persistência (SQLAlchemy/Models) e Interfaces (CLI/Textual/FastAPI), além de ditar o uso do padrão Mapper.
2. **[ECS e Esper](file:///[$HOME]/Dev/Character-Sistem/.rules/2_ecs_esper.md)**: Regras para codificação no padrão Entity-Component-System usando a biblioteca Esper, processamento de mundos com `WorldContext` e a natureza Headless do motor.
3. **[TUI e Textual](file:///[$HOME]/Dev/Character-Sistem/.rules/3_textual_tui.md)**: Melhores práticas para o framework de terminal Textual, incluindo prevenção do `OnDecoratorError` com a propriedade `control` nas mensagens customizadas, controle reativo de foco, interrupção de inputs e tratamento de threads/timers.
4. **[Persistência e Banco de Dados](file:///[$HOME]/Dev/Character-Sistem/.rules/4_banco_dados_persist%C3%AAncia.md)**: Diretrizes de roteamento de banco de dados baseado na flag `TEST_VERSION` para isolar testes de produção, uso de colunas JSON para dados complexos e integração assíncrona.
5. **[Fórmulas de Combate](file:///[$HOME]/Dev/Character-Sistem/.rules/5_sistema_combate_formulas.md)**: Especificações das fórmulas do jogo (HP, modificadores de ataque corpo-a-corpo e distância, esquiva, acertos, dano, absorção) e exigência de `deepcopy` nas simulações.
6. **[Interpretador de Eventos](file:///[$HOME]/Dev/Character-Sistem/.rules/6_interpretador_eventos.md)**: Regras do pipeline do `EventSystem`, avaliação decrescente de condições de páginas de eventos e a pilha de comandos linear não-bloqueante que interage assincronamente com o jogador.
7. **[Testes e TDD](file:///[$HOME]/Dev/Character-Sistem/.rules/7_testes_tdd.md)**: Normas de desenvolvimento baseado em testes (TDD), uso do `monkeypatch` para rolagens determinísticas e setup/teardown de banco de dados para testes.

---

> [!IMPORTANT]
> A preservação da integridade da arquitetura desacoplada e a garantia de que novos recursos passem pela suíte de testes (com mock determinístico de aleatoriedades) são requisitos cruciais de aceitação de código neste repositório.
