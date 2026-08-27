---

description: "Task list for feature implementation"
---

# Tasks: Priorização de Candidatos a Problema

**Input**: Design documents from `/specs/001-priorizacao-problemas/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: incluídos e obrigatórios — o princípio III da constituição torna os testes pytest do domínio não negociáveis, e o Fluxo de Desenvolvimento exige o teste escrito **antes** da regra. Os testes aparecem intercalados, cada um imediatamente antes da regra que cobre.

**Organization**: tarefas agrupadas por história de usuário, para que cada uma seja implementada e testada de forma independente.

## Format: `[ID] [P?] [Story] Descrição — **Pronto quando**: critério`

- **[P]**: pode rodar em paralelo (arquivo diferente, sem dependência pendente)
- **[Story]**: história de usuário à qual a tarefa pertence (US1..US5)
- Todo caminho de arquivo é relativo à raiz do repositório

## Path Conventions

Projeto único: `src/` para o código, `tests/` para os testes, `data/` para o arquivo de dados, conforme a Structure Decision do [plan.md](./plan.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: esqueleto do projeto, dependências e configuração do pytest.

- [X] T001 Criar os diretórios `src/`, `tests/` e `data/` na raiz, com `data/.gitkeep` para versionar a pasta vazia — **Pronto quando**: os três diretórios existem e `data/.gitkeep` está rastreado pelo git.
- [X] T002 [P] Criar `pyproject.toml` na raiz declarando o projeto, `requires-python = ">=3.11"` e `[tool.pytest.ini_options]` com `pythonpath = ["src"]` — **Pronto quando**: `pytest` executado da raiz termina com "no tests ran" em vez de erro de configuração ou de importação.
- [X] T003 [P] Criar `requirements.txt` na raiz com `streamlit` e `pytest`, sem nenhuma outra dependência — **Pronto quando**: `pip install -r requirements.txt` conclui e `streamlit --version` responde.
- [X] T004 [P] Criar `.gitignore` na raiz ignorando `data/problemas.json`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/` e `*.egg-info/` — **Pronto quando**: `git status` continua limpo depois de rodar o aplicativo e a suíte, e `git check-ignore data/problemas.json` confirma o arquivo ignorado.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: o tipo `Problema` e a exceção de validação, dos quais todas as histórias dependem.

**⚠️ CRITICAL**: nenhuma história pode começar antes desta fase.

- [X] T005 Criar `src/dominio.py` com a dataclass `Problema` (`frozen=True`) contendo `id`, `titulo`, `descricao`, `publico`, `frequencia`, `intensidade`, `acesso`, `disposicao_pagar` e `registrado_em`, conforme [data-model.md](./data-model.md) — **Pronto quando**: `from dominio import Problema` funciona no pytest e o módulo não contém `import streamlit`.
- [X] T006 Adicionar a exceção `ErroDeValidacao` (com atributo `mensagens: list[str]`) em `src/dominio.py` — **Pronto quando**: `ErroDeValidacao(["x"]).mensagens == ["x"]` é verdadeiro no interpretador.

**Checkpoint**: tipo base pronto — as histórias podem começar.

---

## Phase 3: User Story 1 - Registrar um candidato e ver seu score (Priority: P1) 🎯 MVP

**Goal**: registrar um problema com as quatro notas e ver seu score na tela.

**Independent Test**: registrar um único problema com as notas 4, 5, 3 e 2 e conferir que a lista exibe o score `3,50`.

- [X] T007 [US1] Escrever em `tests/test_dominio.py` os testes de `calcular_score` cobrindo `4,5,3,2 → 3.5`, `5,5,5,5 → 5.0`, `1,2,2,2 → 1.75`, `1,1,1,1 → 1.0` e `1,1,1,2 → 1.25` (FR-005) — **Pronto quando**: os cinco testes rodam e falham por `calcular_score` não existir.
- [X] T008 [US1] Implementar `calcular_score(problema) -> float` como média simples das quatro notas em `src/dominio.py` (FR-005) — **Pronto quando**: os testes de T007 passam.
- [X] T009 [US1] Escrever em `tests/test_dominio.py` os testes de `formatar_score` cobrindo `3.5 → "3,50"`, `5.0 → "5,00"`, `1.75 → "1,75"` e `1.0 → "1,00"` (FR-006, FR-007) — **Pronto quando**: os quatro testes rodam e falham por `formatar_score` não existir.
- [X] T010 [US1] Implementar `formatar_score(score) -> str` com duas casas e vírgula decimal em `src/dominio.py` (FR-006, FR-007) — **Pronto quando**: os testes de T009 passam.
- [X] T011 [US1] Escrever em `tests/test_dominio.py` os testes de `criar_problema` verificando `strip()` no título, `descricao`/`publico` ausentes virando `""`, `id` diferente entre duas chamadas e `registrado_em` em ISO 8601 (FR-001, FR-004) — **Pronto quando**: os testes rodam e falham por `criar_problema` não existir.
- [X] T012 [US1] Implementar `criar_problema(...) -> Problema` em `src/dominio.py`, gerando `id` com `uuid.uuid4()` e `registrado_em` com `datetime.now().isoformat(timespec="microseconds")` (FR-001) — **Pronto quando**: os testes de T011 passam. A chamada à validação entra na T026.
- [X] T013 [US1] Criar `src/app.py` com formulário Streamlit (título, descrição, público e quatro `number_input(value=3, step=1)` sem `min_value`/`max_value`) que guarda os problemas em `st.session_state["problemas"]` e exibe cada um com `formatar_score` (FR-001, FR-006, FR-007) — **Pronto quando**: `streamlit run src/app.py` registra um problema com notas 4, 5, 3, 2 e a tela mostra `3,50`.

**Checkpoint**: US1 funcional — registro e score visíveis, ainda em memória de sessão.

---

## Phase 4: User Story 2 - Comparar os candidatos em uma ordenação defensável (Priority: P2)

**Goal**: exibir todos os problemas do maior para o menor score, com as três primeiras posições marcadas e destacadas.

**Independent Test**: registrar quatro ou mais problemas com scores diferentes e conferir a ordem decrescente e as marcas `1º`, `2º` e `3º` apenas nas três primeiras linhas.

- [ ] T014 [US2] Escrever em `tests/test_dominio.py` o teste de ordem decrescente de `montar_ranking` com cinco problemas de scores distintos (FR-008) — **Pronto quando**: o teste roda e falha por `montar_ranking` não existir.
- [ ] T015 [US2] Escrever em `tests/test_dominio.py` o teste de empate verificando que dois problemas de mesmo score saem na ordem de `registrado_em`, do mais antigo para o mais novo, e que duas chamadas seguidas devolvem a mesma ordem (FR-009) — **Pronto quando**: o teste roda e falha junto com o de T014.
- [ ] T016 [US2] Adicionar a dataclass `ItemRanking` (`frozen=True`) com `problema`, `score`, `score_formatado`, `posicao`, `destacado` e `rotulo_posicao` em `src/dominio.py` conforme [contracts/dominio.md](./contracts/dominio.md) — **Pronto quando**: `from dominio import ItemRanking` funciona no pytest.
- [ ] T017 [US2] Implementar `montar_ranking(problemas)` em `src/dominio.py` ordenando por `(-score, registrado_em)` sobre a lista em ordem de registro (FR-008, FR-009) — **Pronto quando**: os testes de T014 e T015 passam.
- [ ] T018 [US2] Escrever em `tests/test_dominio.py` os testes de posição e destaque cobrindo lista vazia, um, dois e três problemas (todos destacados) e cinco problemas (4º e 5º com `destacado is False` e `rotulo_posicao == ""`) (FR-010, FR-010a, FR-010b) — **Pronto quando**: os testes rodam e falham por `posicao`/`destacado`/`rotulo_posicao` virem vazios ou incorretos.
- [ ] T019 [US2] Preencher `posicao` (sequencial a partir de 1), `destacado` (`posicao <= 3`) e `rotulo_posicao` (`"1º"`, `"2º"`, `"3º"` ou `""`) dentro de `montar_ranking` em `src/dominio.py` (FR-010, FR-010a, FR-010b) — **Pronto quando**: os testes de T018 passam.
- [ ] T020 [US2] Substituir a exibição de `src/app.py` pela iteração sobre `dominio.montar_ranking(...)`, mostrando `rotulo_posicao`, título, público, as quatro notas e `score_formatado`, com diferenciação visual nas linhas `destacado` (FR-008, FR-010, FR-010a) — **Pronto quando**: com cinco problemas na tela, as três primeiras linhas trazem `1º`, `2º` e `3º` e destaque visual, e `src/app.py` não contém `sorted(`, `<= 3` nem comparação de índice.

**Checkpoint**: US1 e US2 funcionam de forma independente.

---

## Phase 5: User Story 3 - Ser impedido de registrar dados inválidos (Priority: P3)

**Goal**: recusar título vazio e nota fora da faixa com mensagem clara, sem gravar nada.

**Independent Test**: tentar registrar sem título e depois com nota 0 ou 6, conferindo a mensagem e que a lista permanece idêntica.

- [ ] T021 [US3] Escrever em `tests/test_dominio.py` os testes de título inválido em `validar_problema` para `""`, `"   "` e `None`, verificando `ErroDeValidacao` com mensagem em português citando o título (FR-002, FR-014) — **Pronto quando**: os testes rodam e falham por `validar_problema` não existir.
- [ ] T022 [US3] Escrever em `tests/test_dominio.py` os testes de nota inválida para `0`, `6`, `-1`, `3.5`, `"quatro"`, `None` e `True`, em cada uma das quatro dimensões, verificando `ErroDeValidacao` com mensagem que nomeia o campo (FR-003, FR-014) — **Pronto quando**: os testes rodam e falham junto com os de T021.
- [ ] T023 [US3] Escrever em `tests/test_dominio.py` os testes de aceitação da validação: descrição e público vazios aceitos, texto com `;`, aspas e `\n` aceito, e uma entrada com título vazio **e** nota 6 devolvendo as duas mensagens de uma vez (FR-004, FR-013b, FR-014) — **Pronto quando**: os testes rodam e falham junto com os de T021 e T022.
- [ ] T024 [US3] Implementar `validar_problema(...)` em `src/dominio.py` coletando todas as mensagens aplicáveis antes de levantar `ErroDeValidacao`, com os textos definidos em [data-model.md](./data-model.md) (FR-002, FR-003, FR-014) — **Pronto quando**: os testes de T021, T022 e T023 passam.
- [ ] T025 [US3] Escrever em `tests/test_dominio.py` o teste de que `criar_problema` com entrada inválida levanta `ErroDeValidacao` e não devolve nenhum `Problema` (FR-015) — **Pronto quando**: o teste roda e falha porque `criar_problema` ainda aceita a entrada.
- [ ] T026 [US3] Fazer `criar_problema` chamar `validar_problema` como primeira instrução em `src/dominio.py` (FR-015) — **Pronto quando**: o teste de T025 passa e os testes de T011 continuam verdes.
- [ ] T027 [US3] Envolver a submissão do formulário de `src/app.py` em `try/except ErroDeValidacao`, exibindo cada mensagem com `st.error` e mantendo `st.session_state["problemas"]` intacto (FR-014, FR-015) — **Pronto quando**: na tela, submeter com título vazio e depois com intensidade 6 mostra as mensagens e a lista continua com exatamente os mesmos problemas de antes.

**Checkpoint**: US1, US2 e US3 funcionam de forma independente.

---

## Phase 6: User Story 4 - Retomar o trabalho depois de fechar o aplicativo (Priority: P4)

**Goal**: preservar os problemas entre execuções em `data/problemas.json`, com falhas de leitura e de gravação tratadas.

**Independent Test**: registrar três problemas, fechar o aplicativo, reabrir e conferir que os três continuam presentes, com os mesmos dados e a mesma ordem.

- [ ] T028 [US4] Criar `src/armazenamento.py` com `CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data" / "problemas.json"` e a exceção `ErroDeArmazenamento` (decisão 1 de [research.md](./research.md)) — **Pronto quando**: `from armazenamento import CAMINHO_DADOS` funciona, o caminho aponta para `data/problemas.json` na raiz do repositório mesmo com o pytest rodado de outro diretório, e o módulo não contém `import streamlit`.
- [ ] T029 [P] [US4] Escrever em `tests/test_armazenamento.py` o teste de `ler_problemas` com arquivo ausente devolvendo `[]` sem erro (FR-016, História 4 cenário 2) — **Pronto quando**: o teste roda com `tmp_path` e falha por `ler_problemas` não existir.
- [ ] T030 [US4] Escrever em `tests/test_armazenamento.py` os testes de leitura falha para arquivo vazio, só com espaços, JSON inválido, raiz `{}`, item `"texto"`, campo obrigatório ausente e nota `"4"`, cada um levantando `ErroDeArmazenamento` com mensagem sem caminho nem nome de exceção (FR-017) — **Pronto quando**: os sete testes rodam e falham junto com o de T029.
- [ ] T031 [US4] Implementar `ler_problemas(caminho=CAMINHO_DADOS) -> list[Problema]` em `src/armazenamento.py` conforme [contracts/armazenamento-json.md](./contracts/armazenamento-json.md) (FR-011, FR-017) — **Pronto quando**: os testes de T029 e T030 passam.
- [ ] T032 [US4] Escrever em `tests/test_armazenamento.py` o teste de ida e volta gravando três problemas e relendo, conferindo mesma ordem, notas de volta como `int`, acentos legíveis no texto do arquivo (sem `\uXXXX`) e ausência da chave `score` (FR-011, FR-005) — **Pronto quando**: o teste roda e falha por `gravar_problemas` não existir.
- [ ] T033 [US4] Escrever em `tests/test_armazenamento.py` o teste de falha de gravação com `monkeypatch` fazendo `os.replace` levantar `OSError`, conferindo `ErroDeArmazenamento`, arquivo anterior byte a byte intacto e nenhum arquivo temporário sobrando no diretório (FR-017a) — **Pronto quando**: o teste roda e falha junto com o de T032.
- [ ] T034 [US4] Implementar `gravar_problemas(problemas, caminho=CAMINHO_DADOS)` em `src/armazenamento.py` com `mkdir` da pasta, arquivo temporário no mesmo diretório, `json.dump(..., ensure_ascii=False, indent=2)` em UTF-8, `flush` + `os.fsync`, `os.replace` e remoção do temporário em caso de erro (FR-011, FR-017a; decisão 2 de research) — **Pronto quando**: os testes de T032 e T033 passam.
- [ ] T035 [US4] Ligar `src/app.py` ao armazenamento: ler uma vez por sessão dentro de `try/except ErroDeArmazenamento` guardando o erro em `st.session_state["erro_leitura"]`, e no registro gravar a nova lista **antes** de atualizar `st.session_state["problemas"]` (FR-011, FR-017, FR-017a; [contracts/interface-streamlit.md](./contracts/interface-streamlit.md)) — **Pronto quando**: fechar e reabrir o aplicativo preserva os problemas, um `problemas.json` corrompido mostra `st.error` sem stack trace e o aplicativo segue registrando, e com o arquivo somente leitura o registro falha com mensagem e a lista não muda.
- [ ] T036 [US4] Exibir em `src/app.py` uma indicação clara de lista vazia quando `montar_ranking` devolver lista vazia, em vez de tela em branco (FR-016) — **Pronto quando**: abrir o aplicativo sem `data/problemas.json` mostra a mensagem de lista vazia e nenhum erro.

**Checkpoint**: US1 a US4 funcionam de forma independente.

---

## Phase 7: User Story 5 - Levar a lista para uma planilha (Priority: P5)

**Goal**: entregar a lista completa como download de um CSV que abre direto em planilha em português.

**Independent Test**: registrar alguns problemas, acionar a exportação uma única vez e abrir o arquivo baixado em um editor de planilhas comum.

- [ ] T037 [P] [US5] Escrever em `tests/test_exportacao.py` os testes de estrutura de `gerar_csv`: cabeçalho exato com as oito colunas de [data-model.md](./data-model.md), uma linha por problema na ordem do ranking recebido e lista vazia produzindo só o cabeçalho (FR-013) — **Pronto quando**: os testes rodam e falham por `gerar_csv` não existir.
- [ ] T038 [US5] Escrever em `tests/test_exportacao.py` os testes de formato: score saindo como `3,50` e `5,00`, notas como inteiros sem formatação, delimitador `;` e bytes começando com o BOM `b"\xef\xbb\xbf"` (FR-013a) — **Pronto quando**: os testes rodam e falham junto com os de T037.
- [ ] T039 [US5] Escrever em `tests/test_exportacao.py` os testes de texto: descrição com `;`, com aspas e com `\n` voltando idêntica ao relê-la com `csv.reader(..., delimiter=";")`, sem mudar o número de colunas da linha, e texto acentuado íntegro após decodificar com `utf-8-sig` (FR-013b) — **Pronto quando**: os testes rodam e falham junto com os de T037 e T038.
- [ ] T040 [US5] Implementar `gerar_csv(itens) -> bytes` em `src/exportacao.py` com `io.StringIO`, `csv.writer(delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")` e `encode("utf-8-sig")`, sem escrever em disco (FR-012, FR-013, FR-013a, FR-013b; decisão 7 de research) — **Pronto quando**: os testes de T037, T038 e T039 passam e `src/exportacao.py` não contém `open(` nem `import streamlit`.
- [ ] T041 [US5] Adicionar em `src/app.py` o `st.download_button` com `data=exportacao.gerar_csv(itens)`, `file_name="radar-de-problemas.csv"` e `mime="text/csv"` (FR-012, FR-012a) — **Pronto quando**: um clique baixa o arquivo para a pasta de downloads sem pedir caminho, o arquivo abre no Excel em português com as oito colunas separadas, e nenhum `.csv` aparece dentro do repositório.

**Checkpoint**: todas as histórias funcionam de forma independente.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: verificação dos gates da constituição e validação final.

- [ ] T042 [P] Escrever docstrings em português nos quatro módulos de `src/`, com a de `src/armazenamento.py` apontando o formato do JSON documentado em [data-model.md](./data-model.md) (princípio V e Restrições Técnicas da constituição) — **Pronto quando**: cada módulo tem docstring de topo explicando sua responsabilidade e nenhum comentário repete o que o código já diz.
- [ ] T043 Verificar os gates de separação com `grep -rn "import streamlit" src/dominio.py src/armazenamento.py src/exportacao.py` e `grep -nE "/ 4|sum\(|sorted\(|<= 3|round\(|replace\(\"\.\"" src/app.py` (princípios I e II) — **Pronto quando**: o primeiro comando não retorna nada e o segundo não retorna nenhuma ocorrência que seja cálculo ou regra.
- [ ] T044 Rodar `pytest` a partir da raiz do repositório (princípio III) — **Pronto quando**: a suíte inteira passa, sem teste pulado e sem aviso de importação.
- [ ] T045 Executar os 18 cenários manuais de [quickstart.md](./quickstart.md) com a rede desligada (princípio IV) — **Pronto quando**: os 18 cenários conferem e a lista de critérios de conclusão do quickstart está toda marcada.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Fase 1)**: sem dependências.
- **Foundational (Fase 2)**: depende da Fase 1 — bloqueia todas as histórias.
- **US1 (Fase 3)**: depende da Fase 2.
- **US2 (Fase 4)**: depende de US1 (usa `calcular_score` e `formatar_score`).
- **US3 (Fase 5)**: depende de US1 (liga a validação a `criar_problema`); independente de US2.
- **US4 (Fase 6)**: depende de US1 (persiste `Problema`); independente de US2 e US3.
- **US5 (Fase 7)**: depende de US2 (exporta a partir do ranking, na ordem da tela).
- **Polish (Fase 8)**: depende de todas as histórias desejadas.

### User Story Dependencies

Nenhuma história depende de outra para ser **testada** — cada uma tem seu próprio critério de teste independente. As dependências acima são de código já escrito, não de comportamento: US2, US3 e US4 partem todas de US1 e não se enxergam entre si.

### Within Each User Story

- O teste vem antes da regra e deve falhar antes de a regra existir (Fluxo de Desenvolvimento, passo 2).
- Domínio antes de armazenamento e exportação; regras antes da interface (passos 3 e 4).
- A tarefa de `src/app.py` fecha cada história.

### Parallel Opportunities

- T002, T003 e T004 são arquivos diferentes na raiz e podem ser feitos em paralelo.
- T029 e T037 abrem arquivos de teste novos (`tests/test_armazenamento.py`, `tests/test_exportacao.py`) e não colidem com `tests/test_dominio.py`.
- Depois da Fase 3, a dupla pode dividir: uma pessoa em US2 (`ranking`), outra em US4 (`armazenamento`) — arquivos diferentes, sem sobreposição, exceto pelas tarefas de `src/app.py`, que devem ser feitas uma de cada vez.
- As demais tarefas de `tests/test_dominio.py` e de `src/dominio.py` tocam o mesmo arquivo e **não** são paralelizáveis.

---

## Parallel Example: Fase 1

```bash
# Três arquivos diferentes na raiz, sem dependência entre si:
Task: "Criar pyproject.toml com pythonpath = [\"src\"]"
Task: "Criar requirements.txt com streamlit e pytest"
Task: "Criar .gitignore ignorando data/problemas.json e artefatos de ambiente Python"
```

---

## Implementation Strategy

### MVP First (US1)

1. Fase 1: Setup.
2. Fase 2: Foundational.
3. Fase 3: US1.
4. **PARAR E VALIDAR**: registrar um problema com notas 4, 5, 3, 2 e conferir `3,50`.

### Incremental Delivery

1. Setup + Foundational → base pronta.
2. US1 → score na tela (MVP).
3. US2 → ordenação defensável com top 3 marcado.
4. US3 → entrada inválida recusada com mensagem clara.
5. US4 → o trabalho sobrevive ao fechamento do aplicativo.
6. US5 → a lista sai para a planilha.
7. Polish → gates verificados e quickstart executado.

Cada história acrescenta valor sem quebrar as anteriores: ao fim de qualquer fase a suíte `pytest` está verde e o aplicativo roda.

---

## Notes

- `[P]` = arquivos diferentes, sem dependência pendente.
- Todo teste deve ser visto falhando antes de a regra ser implementada.
- Commit ao fim de cada tarefa ou de cada par teste+regra.
- Nada além dos FRs da spec entra no código (princípio VI): edição, exclusão, filtro, busca e importação continuam fora de escopo.
