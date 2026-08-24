# Radar de Problemas Constitution
<!-- Constituição do projeto educacional Radar de Problemas. -->

## Core Principles

### I. Python Estável e Simples
O projeto deve usar exclusivamente Python 3.14.7. A implementação deve priorizar código simples, legível e com dependências mínimas; qualquer dependência nova deve ter justificativa clara. Comentários adicionados ao código devem ser concisos e escritos em português quando ajudarem a explicar uma decisão ou regra não óbvia.

### II. Interface Streamlit
A interface de usuário deve ser implementada com Streamlit e permanecer responsável apenas por apresentação, entrada do usuário e composição do fluxo. A camada de interface não deve conter regras de negócio, cálculos de score ou validações que precisem ser reutilizados.

### III. Dados Locais em JSON
Os dados da aplicação devem ser persistidos em arquivos JSON locais, usando operações determinísticas e tratamento explícito de arquivos ausentes ou inválidos. É proibido introduzir banco de dados, API externa, serviço remoto ou outra forma de persistência que exija infraestrutura fora do projeto.

### IV. Domínio Separado e Testável
Regras de negócio, incluindo score e validações, devem viver em módulos Python independentes da interface e do armazenamento. Esses módulos devem poder ser exercitados sem iniciar o Streamlit, acessar a rede ou depender do estado visual da aplicação.

### V. Testes com pytest
Toda regra de score ou validação nova ou alterada deve ter testes automatizados com pytest, cobrindo o comportamento esperado e os casos inválidos relevantes. Uma mudança só é considerada pronta quando os testes do domínio passam e a interface continua integrando corretamente as funções testadas.

## Restrições Técnicas
O código deve funcionar offline e não pode depender de serviços externos. O formato JSON deve ser documentado junto ao código ou à especificação correspondente, e falhas de leitura ou validações inválidas devem gerar mensagens compreensíveis para o usuário sem expor detalhes desnecessários da implementação.

## Fluxo de Desenvolvimento
Cada funcionalidade deve começar pela definição do comportamento e das regras de negócio. O trabalho deve seguir este fluxo mínimo: escrever ou atualizar testes pytest, implementar a regra em módulo independente, integrar a interface Streamlit e executar a suíte de testes. Revisões devem verificar a separação entre interface, domínio e persistência, além da compatibilidade com Python 3.14.7.

## Governance
Esta constituição prevalece sobre convenções conflitantes do projeto. Toda alteração deve respeitar os cinco princípios e os gates do fluxo de desenvolvimento. Emendas devem atualizar este arquivo, explicar o motivo da mudança e ajustar testes ou documentação afetados. Complexidade adicional, nova dependência ou qualquer exceção à execução offline deve ser justificada explicitamente e aprovada antes da implementação.

**Version**: 1.0.0 | **Ratified**: 2026-08-24 | **Last Amended**: 2026-08-24
