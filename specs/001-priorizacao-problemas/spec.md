# Feature Specification: Priorização de Candidatos a Problema

**Feature Branch**: `develop`

**Feature Directory**: `specs/001-priorizacao-problemas`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "Um aplicativo para uma pessoa em fase de descoberta de problemas registrar e comparar candidatos a problema, e decidir com base em evidência qual perseguir, em vez de decidir por intuição. Quem usa: um estudante empreendedor que acabou de sair de entrevistas de campo e tem uma lista bagunçada de dores anotadas, e precisa comparar essas dores entre si. Para quê: transformar impressões soltas em uma ordenação defensável, para justificar publicamente por que escolheu um problema e não outro."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registrar um candidato a problema e ver seu score (Priority: P1)

O estudante acabou de sair de uma rodada de entrevistas e tem uma dor anotada no caderno.
Ele abre o aplicativo, escreve o título da dor, uma descrição do que ouviu, qual público é
afetado, e atribui quatro notas de 1 a 5: com que frequência a dor acontece, quão intensa
ela é, quão fácil é chegar em pessoas que sofrem dela, e quanto esse público demonstra
disposição a pagar por uma solução. Ao confirmar, o problema passa a existir no aplicativo
com um score numérico que resume as quatro notas.

**Why this priority**: É a fundação de tudo. Sem registro e sem score, não existe nada para
comparar, ordenar ou exportar. Sozinha, esta história já entrega valor: converte uma
impressão solta em um número comparável.

**Independent Test**: Pode ser testada isoladamente registrando um único problema com as
quatro notas e conferindo que o score exibido é a média dessas notas com duas casas
decimais.

**Acceptance Scenarios**:

1. **Given** o aplicativo aberto e nenhum problema registrado, **When** o usuário informa
   título, descrição, público afetado e as notas 4, 5, 3 e 2, **Then** o problema passa a
   constar na lista exibindo o score `3,50`.
2. **Given** o aplicativo aberto, **When** o usuário registra um problema com as quatro
   notas iguais a 5, **Then** o score exibido é `5,00`.
3. **Given** o aplicativo aberto, **When** o usuário registra um problema com as notas 1,
   2, 2 e 2, **Then** o score exibido é `1,75` (duas casas decimais, sem truncar a segunda).

---

### User Story 2 - Comparar os candidatos em uma ordenação defensável (Priority: P2)

Com várias dores já registradas, o estudante precisa saber quais delas se destacam. Ele vê
todos os problemas listados do maior para o menor score, com os três primeiros
visualmente destacados, e usa essa ordenação para explicar publicamente por que vai
perseguir um problema e não outro.

**Why this priority**: É o propósito central do aplicativo — a decisão baseada em evidência.
Depende da História 1 existir, mas é ela que transforma registros isolados em uma escolha
justificável.

**Independent Test**: Pode ser testada registrando quatro ou mais problemas com scores
diferentes e verificando que a ordem exibida é decrescente por score e que exatamente as
três primeiras posições aparecem destacadas.

**Acceptance Scenarios**:

1. **Given** cinco problemas registrados com scores distintos, **When** o usuário visualiza
   a lista, **Then** os problemas aparecem do maior para o menor score.
2. **Given** cinco problemas registrados, **When** o usuário visualiza a lista, **Then** os
   três primeiros da ordenação estão visualmente destacados e os demais não.
3. **Given** dois problemas registrados com o mesmo score, **When** o usuário visualiza a
   lista, **Then** ambos aparecem em posições adjacentes, o registrado primeiro aparecendo
   antes, e a ordem se mantém a mesma a cada nova visualização.
4. **Given** apenas dois problemas registrados, **When** o usuário visualiza a lista,
   **Then** os dois aparecem destacados e nenhum erro é apresentado.

---

### User Story 3 - Ser impedido de registrar dados inválidos (Priority: P3)

O estudante digita apressado entre uma entrevista e outra. Se ele esquecer o título ou
escrever uma nota fora da faixa de 1 a 5, o aplicativo recusa o registro e explica em
linguagem clara o que precisa ser corrigido, sem gravar nada pela metade.

**Why this priority**: A ordenação só é defensável se todo registro respeitar as mesmas
regras. Um único registro sem título ou com nota fora da faixa contamina a comparação.

**Independent Test**: Pode ser testada tentando registrar um problema sem título e outro
com nota 0 ou 6, verificando que uma mensagem clara é exibida e que a lista de problemas
permanece exatamente como estava.

**Acceptance Scenarios**:

1. **Given** o formulário de registro, **When** o usuário deixa o título vazio (ou apenas
   com espaços) e confirma, **Then** o aplicativo exibe uma mensagem em linguagem clara
   indicando que o título é obrigatório e nenhum problema é registrado.
2. **Given** o formulário de registro, **When** o usuário informa a nota 6 para intensidade
   e confirma, **Then** o aplicativo exibe uma mensagem indicando que as notas devem estar
   entre 1 e 5 e nenhum problema é registrado.
3. **Given** o formulário de registro, **When** o usuário informa a nota 0 para frequência
   e confirma, **Then** o aplicativo recusa o registro com mensagem clara.
4. **Given** uma tentativa de registro recusada, **When** o usuário visualiza a lista,
   **Then** a lista contém exatamente os mesmos problemas que continha antes da tentativa.

---

### User Story 4 - Retomar o trabalho depois de fechar o aplicativo (Priority: P4)

O estudante registra dores ao longo de vários dias, entre rodadas de entrevistas. Ao fechar
o aplicativo e abri-lo de novo mais tarde, todos os problemas que ele já havia registrado
continuam lá, com as mesmas notas, os mesmos scores e a mesma ordenação.

**Why this priority**: Sem persistência o aplicativo só serve para uma sessão, e o trabalho
de campo acontece ao longo de dias. É essencial para o uso real, mas as histórias anteriores
já podem ser demonstradas sem ela.

**Independent Test**: Pode ser testada registrando três problemas, fechando o aplicativo,
reabrindo e conferindo que os três continuam presentes, com os mesmos dados e a mesma ordem.

**Acceptance Scenarios**:

1. **Given** três problemas registrados, **When** o usuário fecha e reabre o aplicativo,
   **Then** os três problemas aparecem com título, descrição, público, notas e scores
   idênticos aos registrados.
2. **Given** o aplicativo aberto pela primeira vez, sem nenhum registro anterior, **When** o
   usuário visualiza a lista, **Then** uma indicação clara de lista vazia é exibida e nenhum
   erro é apresentado.
3. **Given** que os dados armazenados não podem ser lidos (ausentes, vazios ou corrompidos),
   **When** o usuário abre o aplicativo, **Then** uma mensagem compreensível é exibida, sem
   expor detalhes internos, e o aplicativo permanece utilizável para novos registros.

---

### User Story 5 - Levar a lista para uma planilha (Priority: P5)

Para apresentar a decisão ao professor ou à dupla, o estudante quer os dados fora do
aplicativo. Com uma única ação, ele obtém a lista completa de problemas em um arquivo que
abre diretamente em um editor de planilhas.

**Why this priority**: Amplia o alcance do trabalho já feito, mas não é necessária para
decidir dentro do aplicativo. É a última fatia de valor.

**Independent Test**: Pode ser testada registrando alguns problemas, acionando a exportação
uma única vez e abrindo o arquivo resultante em um editor de planilhas comum.

**Acceptance Scenarios**:

1. **Given** quatro problemas registrados, **When** o usuário aciona a exportação uma única
   vez, **Then** ele obtém um arquivo contendo os quatro problemas, com uma linha por
   problema e uma linha de cabeçalho identificando as colunas.
2. **Given** o arquivo exportado, **When** ele é aberto em um editor de planilhas comum,
   **Then** título, descrição, público afetado, as quatro notas e o score aparecem em
   colunas separadas, sem ajuste manual.
3. **Given** problemas com scores diferentes, **When** o usuário exporta a lista, **Then** as
   linhas aparecem na mesma ordem decrescente de score exibida na tela.

---

### Edge Cases

- **Lista vazia**: com nenhum problema registrado, a exportação produz um arquivo apenas com
  a linha de cabeçalho, e a lista exibe uma indicação de lista vazia em vez de erro.
- **Menos de três problemas**: o destaque se aplica a quantos existirem (um ou dois), sem
  erro e sem posições vazias.
- **Empate de score**: problemas com o mesmo score mantêm entre si a ordem de registro (o
  mais antigo primeiro), de modo que a ordenação exibida seja sempre a mesma para os mesmos
  dados.
- **Score com arredondamento**: notas cuja média tem mais de duas casas decimais (ex.: 1, 1,
  1, 2 → 1,25; 1, 2, 2, 2 → 1,75) são exibidas com exatamente duas casas.
- **Nota não numérica ou ausente**: o registro é recusado com mensagem clara, do mesmo modo
  que uma nota fora da faixa.
- **Título só com espaços**: tratado como título ausente e recusado.
- **Título duplicado**: permitido — o usuário pode registrar duas dores com o mesmo título;
  ambas constam na lista e no ranking.
- **Descrição e público vazios**: permitidos; apenas o título e as quatro notas são
  obrigatórios.
- **Armazenamento ilegível**: arquivo ausente, vazio ou malformado gera mensagem
  compreensível para o usuário, sem expor detalhes técnicos, e não derruba o aplicativo.
- **Textos longos**: títulos e descrições extensos são preservados integralmente no registro
  e na exportação.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir registrar um candidato a problema informando título,
  descrição, público afetado e quatro notas: frequência da dor, intensidade da dor,
  facilidade de acesso a quem sofre a dor e disposição do público a pagar por uma solução.
- **FR-002**: O sistema MUST exigir título não vazio (desconsiderando espaços em branco nas
  extremidades) para aceitar um registro.
- **FR-003**: O sistema MUST aceitar como nota válida apenas número inteiro de 1 a 5,
  inclusive, para cada uma das quatro dimensões.
- **FR-004**: O sistema MUST tratar descrição e público afetado como campos opcionais, sem
  recusar o registro quando estiverem vazios.
- **FR-005**: O sistema MUST calcular o score de cada problema como a média aritmética
  simples das quatro notas, com peso igual entre elas.
- **FR-006**: O sistema MUST exibir o score com exatamente duas casas decimais, inclusive
  quando o resultado for um número inteiro.
- **FR-007**: O sistema MUST exibir o score usando vírgula como separador decimal, seguindo
  a convenção do português (ex.: `3,50`, `5,00`, `1,75`).
- **FR-008**: O sistema MUST exibir os problemas registrados ordenados do maior para o menor
  score.
- **FR-009**: O sistema MUST desempatar problemas de mesmo score pela ordem de registro (o
  registrado primeiro aparece antes), garantindo ordenação estável e reproduzível.
- **FR-010**: O sistema MUST destacar visualmente as três primeiras posições da ordenação,
  ou todas as posições existentes quando houver menos de três problemas.
- **FR-011**: O sistema MUST preservar os problemas registrados entre execuções, de modo que
  continuem disponíveis com os mesmos dados após o aplicativo ser fechado e reaberto.
- **FR-012**: O sistema MUST permitir que, com uma única ação do usuário, a lista completa de
  problemas seja obtida em um arquivo que abre diretamente em um editor de planilhas comum,
  sem exigir nenhum ajuste manual de formatação por parte do usuário.
- **FR-013**: O arquivo obtido na exportação MUST apresentar uma linha de cabeçalho
  identificando as colunas e, para cada problema, título, descrição, público afetado, as
  quatro notas e o score em colunas separadas, na mesma ordem decrescente exibida na tela.
- **FR-014**: O sistema MUST recusar o registro quando qualquer regra de validação (FR-002,
  FR-003) for violada, exibindo mensagem em português, em linguagem clara, que identifique o
  campo problemático e o que precisa ser corrigido.
- **FR-015**: O sistema MUST NOT gravar nenhum dado — nem parcial — quando um registro for
  recusado por validação; a lista de problemas deve permanecer inalterada.
- **FR-016**: O sistema MUST exibir uma indicação clara quando não houver nenhum problema
  registrado, em vez de tela vazia sem explicação ou mensagem de erro.
- **FR-017**: O sistema MUST tratar armazenamento ausente, vazio ou malformado exibindo
  mensagem compreensível ao usuário, sem expor detalhes internos, e permanecendo utilizável
  para novos registros.
- **FR-018**: O sistema MUST funcionar para um único usuário local, sem contas, sem login e
  sem qualquer dependência de conexão de rede ou serviço externo.

### Key Entities *(include if feature involves data)*

- **Candidato a Problema**: uma dor observada em campo que o usuário está avaliando.
  Atributos: título (obrigatório), descrição (opcional), público afetado (opcional), nota de
  frequência, nota de intensidade, nota de acesso ao público, nota de disposição a pagar
  (todas de 1 a 5), e momento de registro (usado para desempate e para manter a ordem
  estável). O score não é informado pelo usuário: é derivado das quatro notas.
- **Ranking**: a visão ordenada de todos os Candidatos a Problema, do maior para o menor
  score, com as três primeiras posições destacadas. É derivada dos registros existentes, não
  é armazenada nem editada diretamente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue registrar um candidato a problema completo (título,
  descrição, público e as quatro notas) em menos de 1 minuto.
- **SC-002**: 100% dos scores exibidos correspondem à média das quatro notas informadas,
  apresentada com duas casas decimais, verificável por conferência manual em qualquer
  registro.
- **SC-003**: Com até 100 problemas registrados, a lista ordenada aparece atualizada em
  menos de 1 segundo após um novo registro.
- **SC-004**: 100% das tentativas de registro sem título ou com nota fora da faixa de 1 a 5
  são recusadas com mensagem compreensível, e nenhuma delas altera a lista de problemas.
- **SC-005**: Após fechar e reabrir o aplicativo, 100% dos problemas registrados reaparecem
  com os mesmos dados, os mesmos scores e a mesma ordem.
- **SC-006**: A lista completa é exportada com uma única ação do usuário e abre em um editor
  de planilhas comum sem nenhum ajuste manual de formatação.
- **SC-007**: Uma terceira pessoa, olhando apenas o arquivo exportado, consegue reproduzir a
  ordenação apresentada e explicar por que o primeiro colocado ficou à frente do segundo.
- **SC-008**: Em uma sessão de uso, o usuário consegue apontar qual problema vai perseguir e
  justificar a escolha citando as notas e o score, sem recorrer a anotações fora do
  aplicativo.

## Assumptions

- As quatro notas são números inteiros de 1 a 5; não são aceitos valores fracionários. A
  descrição do usuário fala em "notas de 1 a 5", e inteiros são a leitura natural para
  avaliação em escala.
- As quatro dimensões têm peso igual no score, já que o usuário descreveu o score como "a
  média das quatro notas", sem menção a pesos.
- O score é apresentado com duas casas decimais usando arredondamento aritmético comum
  (meia unidade arredonda para cima), e não truncamento.
- O score é exibido com vírgula como separador decimal, por ser a convenção do português e a
  esperada pelo público do aplicativo.
- Apenas o título é obrigatório entre os campos de texto; descrição e público afetado são
  opcionais, porque a descrição do usuário só menciona recusa de registro "sem título".
- Em caso de empate no score, a ordem de registro decide, para que a ordenação seja sempre
  a mesma para os mesmos dados. O usuário não especificou desempate.
- O destaque das três primeiras posições é posicional: destacam-se as três primeiras linhas
  da ordenação, mesmo que haja empate na terceira posição.
- Havendo menos de três problemas registrados, todos os existentes ficam destacados.
- "Formato que abre em qualquer planilha" é interpretado como um arquivo tabular que o
  usuário abre diretamente em um editor de planilhas comum, com colunas já separadas e sem
  nenhuma etapa de importação ou conversão manual. Qual formato de arquivo atende a esse
  comportamento é decisão do plano, não da spec.
- Os dados são de um único usuário, guardados localmente na máquina onde o aplicativo roda,
  conforme a restrição de operação offline da constituição do projeto.
- Títulos duplicados são permitidos: duas entrevistas podem gerar dores com o mesmo nome.
- Todas as mensagens ao usuário são em português.

## Fora de Escopo *(nesta versão)*

Explicitamente excluídos, conforme a descrição do usuário:

- Múltiplos usuários, contas e login.
- Edição colaborativa ou compartilhamento entre pessoas.
- Qualquer integração com serviço externo, API ou acesso à rede.
- Qualquer análise além da ordenação por score (gráficos, agrupamentos, tendências,
  recomendações automáticas, pesos configuráveis por dimensão).

Excluídos por decorrência da lista acima, e sujeitos a acordo da dupla caso sejam desejados:

- Editar ou excluir um problema já registrado. Esta versão cobre registrar, comparar e
  exportar; correção de um registro errado não foi pedida e não está incluída.
- Importar problemas de um arquivo externo.
- Filtrar ou buscar problemas dentro da lista.
