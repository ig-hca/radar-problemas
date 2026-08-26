<!--
SYNC IMPACT REPORT
Version change: 1.0.0 → 2.0.0
Regra de interpretador: Python 3.11+ (substitui o pin exato anterior).
-->

# Radar de Problemas Constitution

## Core Principles

### I. Domínio Puro e Isolado
As regras de negócio — cálculo de score e validação de entrada — DEVEM viver em módulo
Python próprio, separado da interface. Esse módulo NÃO PODE importar `streamlit`, ler
`st.session_state`, acessar rede ou depender de qualquer estado visual. As funções do
domínio DEVEM receber dados simples como argumento e devolver o resultado ao chamador.
Racional: só o domínio isolado pode ser exercitado por teste sem subir a aplicação, e é
isso que permite mudar a tela sem mudar a regra.

### II. Interface Sem Cálculo
A interface Streamlit NÃO PODE calcular nada. Sua responsabilidade é coletar a entrada do
usuário, chamar as funções do domínio e exibir o que elas devolverem. É PROIBIDO
reimplementar na interface qualquer fórmula de score, limiar, regra de validação ou
condição de negócio que pertença ao módulo de regras.
Racional: toda regra que vaza para a tela deixa de ser coberta por teste.

### III. Testes pytest no Domínio (NÃO NEGOCIÁVEL)
Toda regra de score ou validação nova ou alterada DEVE ter testes pytest cobrindo o
comportamento esperado e os casos inválidos relevantes: campo ausente, tipo errado, valor
fora da faixa e os limites do score. Os testes NÃO PODEM depender de Streamlit, de rede ou
de arquivos fora do repositório. Uma mudança só é considerada pronta quando a suíte
`pytest` passa inteira.

### IV. Ambiente Local e Fechado
O projeto DEVE rodar em Python 3.11 ou superior, offline e com dependências mínimas. Os
dados DEVEM ser persistidos em arquivo JSON local, com tratamento explícito de arquivo
ausente, vazio ou malformado. É PROIBIDO introduzir banco de dados, autenticação, chamada
de rede, API ou serviço externo de qualquer natureza. Dependência nova exige justificativa
explícita e concordância da dupla antes de entrar no projeto.

### V. Código Legível em Português
O código DEVE ser simples e legível: nomes descritivos, funções curtas e nenhuma abstração
especulativa. Comentários e docstrings DEVEM ser escritos em português e explicar decisões
e regras não óbvias, sem repetir o que o código já diz. Entre duas soluções corretas, vence
a mais fácil de ler.
Racional: é um projeto educacional feito em dupla — o código é lido muito mais vezes do que
é escrito.

### VI. Escopo Enxuto e Spec-First (NÃO NEGOCIÁVEL)
Nada é implementado além dos critérios de aceitação acordados. Toda funcionalidade nova
DEVE passar pela especificação antes de virar código. Ideia que surgir durante a
implementação e não estiver na spec NÃO PODE ser codificada "de passagem": ela volta para a
spec e espera acordo da dupla.
Racional: escopo que cresce sem spec é a forma mais comum de o projeto perder o prazo e a
cobertura de testes.

## Restrições Técnicas
Contexto: projeto educacional desenvolvido em dupla. A stack é fixa — Python 3.11+,
Streamlit para a interface, pytest para os testes e um arquivo JSON local para os dados.
O repositório DEVE manter separados, no mínimo: o módulo de regras de negócio, a camada de
interface Streamlit e o diretório de testes. O formato do arquivo JSON DEVE estar
documentado junto ao código ou à spec correspondente. Falhas de leitura do JSON e entradas
inválidas DEVEM gerar mensagem compreensível para o usuário, sem expor stack trace nem
detalhes internos da implementação. A aplicação inteira DEVE funcionar sem conexão de rede.

## Fluxo de Desenvolvimento
Cada funcionalidade segue esta ordem, sem pular etapas:

1. Spec escrita e critérios de aceitação acordados pela dupla.
2. Testes pytest escritos ou atualizados para as regras envolvidas.
3. Regra implementada no módulo de domínio, até os testes passarem.
4. Interface Streamlit integrada, apenas chamando o domínio e exibindo o resultado.
5. Suíte `pytest` completa executada e verde.

A revisão da dupla DEVE verificar, explicitamente: que o domínio não importa Streamlit, que
a interface não calcula nada, que os casos inválidos estão testados, que o código roda em
Python 3.11+ e que nada além dos critérios de aceitação acordados foi implementado.

## Governance
Esta constituição prevalece sobre qualquer convenção conflitante do projeto. Toda alteração
de código DEVE respeitar os seis princípios e os gates do Fluxo de Desenvolvimento;
complexidade adicional, dependência nova ou qualquer exceção à execução offline DEVE ser
justificada por escrito e aprovada pela dupla antes da implementação.

Emendas a este documento exigem: atualização deste arquivo, registro do motivo da mudança,
ajuste dos testes e da documentação afetados e concordância da dupla. O versionamento segue
semântica MAJOR.MINOR.PATCH:

- MAJOR: remoção ou redefinição incompatível de princípio ou regra de governança.
- MINOR: novo princípio, nova seção ou ampliação material de uma orientação existente.
- PATCH: esclarecimento, ajuste de texto ou correção sem mudança de significado.

**Version**: 2.0.0 | **Ratified**: 2026-08-24 | **Last Amended**: 2026-08-25
