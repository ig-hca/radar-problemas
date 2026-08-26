# Implementation Plan: Priorização de Candidatos a Problema

**Branch**: `develop` | **Feature Directory**: `specs/001-priorizacao-problemas` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-priorizacao-problemas/spec.md`

## Summary

Aplicativo local de usuário único que registra candidatos a problema (título, descrição,
público afetado e quatro notas inteiras de 1 a 5), calcula um score como média simples das
notas, exibe todos os registros ordenados do maior para o menor score com as três primeiras
posições marcadas (`1º`, `2º`, `3º`) e destacadas, e entrega a lista completa como download
de um arquivo que abre direto em editor de planilhas em português.

Abordagem técnica: Python 3.11 + Streamlit. As regras (validação, score, ordenação, ranking)
ficam em módulos puros dentro de `src/`, sem importar Streamlit, cobertos por pytest. A
persistência é um único arquivo `data/problemas.json`, lido na abertura e regravado a cada
alteração de forma atômica (arquivo temporário + substituição), com caminho derivado da
localização do módulo. A exportação é gerada em memória (`io.StringIO` + `csv`, delimitador
`;`, `utf-8-sig`) e entregue por `st.download_button`, sem arquivo intermediário em disco.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Streamlit (interface); biblioteca padrão para o resto (`json`,
`csv`, `io`, `uuid`, `datetime`, `pathlib`, `tempfile`, `os`). Nenhuma dependência de rede.

**Storage**: arquivo JSON local único — `data/problemas.json`, UTF-8, `ensure_ascii=False`,
caminho derivado de `Path(__file__)` (nunca do diretório de trabalho), gravação atômica.

**Testing**: pytest, com `pyproject.toml` na raiz declarando `pythonpath = ["src"]` para que
a suíte enxergue os módulos rodando `pytest` a partir da raiz do repositório.

**Target Platform**: desktop local (Windows/macOS/Linux) rodando `streamlit run src/app.py`
no navegador da própria máquina, offline.

**Project Type**: aplicação single-project — domínio puro + interface Streamlit.

**Performance Goals**: com até 100 problemas registrados, a lista ordenada atualiza em menos
de 1 segundo após um novo registro (SC-003). O volume é irrisório: ordenação em memória de
uma lista de até algumas centenas de itens e uma regravação completa do JSON por alteração.

**Constraints**: offline obrigatório — sem banco de dados, sem autenticação, sem serviço
externo, sem chamada de rede. Domínio não importa Streamlit. Interface não calcula nada.
Nenhuma gravação parcial: falha de escrita deixa o arquivo e a lista exatamente como estavam.

**Scale/Scope**: um usuário, uma máquina, uma tela; ordem de dezenas a poucas centenas de
problemas registrados ao longo de dias de trabalho de campo.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Gate | Situação |
|---|---|---|
| I. Domínio Puro e Isolado | `src/dominio.py`, `src/armazenamento.py` e `src/exportacao.py` não importam `streamlit`, não leem `st.session_state`, não acessam rede; recebem dados simples e devolvem resultado | **PASS** — apenas `src/app.py` importa Streamlit |
| II. Interface Sem Cálculo | `src/app.py` só coleta entrada, chama o domínio e exibe; score formatado, posição e marca de top 3 chegam prontos (FR-010b); nenhum limiar ou fórmula reimplementado na tela | **PASS** — ver [contracts/interface-streamlit.md](./contracts/interface-streamlit.md) |
| III. Testes pytest no Domínio | testes para score (limites e casos de arredondamento), validação (título vazio/só espaços, nota fora da faixa, nota não inteira, nota ausente), ordenação, empate, ranking com menos de 3 itens, leitura de JSON ausente/vazio/malformado, gravação atômica e falha de gravação, e conteúdo do CSV | **PASS** — sem Streamlit, sem rede, sem arquivo fora do repositório (`tmp_path`) |
| IV. Ambiente Local e Fechado | Python 3.11, dados em JSON local com tratamento explícito de ausente/vazio/malformado, única dependência externa é Streamlit (já fixada pela constituição) | **PASS** — nenhuma dependência nova |
| V. Código Legível em Português | nomes, docstrings e mensagens em português; módulos curtos; nenhuma abstração especulativa (sem camada de repositório, sem ORM, sem injeção de dependência) | **PASS** |
| VI. Escopo Enxuto e Spec-First | plano cobre apenas FR-001..FR-018; sem editar/excluir problema, sem filtro, sem busca, sem importação, sem gráficos | **PASS** |

**Resultado**: nenhuma violação. A tabela de Complexity Tracking permanece vazia.

**Re-avaliação pós-Phase 1**: os contratos gerados mantêm os seis gates. O único ponto que
mereceu decisão explícita foi o comportamento após leitura falha do JSON (registro novo
regrava o arquivo ilegível) — registrado em [research.md](./research.md), decisão 8, dentro
do que a spec já determina (FR-017), sem ampliar escopo. **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/001-priorizacao-problemas/
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Phase 0 (/speckit-plan)
├── data-model.md        # Phase 1 (/speckit-plan)
├── quickstart.md        # Phase 1 (/speckit-plan)
├── contracts/           # Phase 1 (/speckit-plan)
│   ├── dominio.md
│   ├── armazenamento-json.md
│   ├── exportacao-csv.md
│   └── interface-streamlit.md
├── checklists/
│   └── requirements.md
├── spec.md
└── tasks.md             # Phase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
pyproject.toml           # metadados + [tool.pytest.ini_options] pythonpath = ["src"]
requirements.txt         # streamlit, pytest

src/
├── app.py               # interface Streamlit — único módulo que importa streamlit
├── dominio.py           # validação, score, ordenação e ranking (puro)
├── armazenamento.py     # leitura e gravação atômica de data/problemas.json (puro)
└── exportacao.py        # geração do CSV em memória (puro)

tests/
├── test_dominio.py      # score, validação, ordenação, empate, ranking
├── test_armazenamento.py# ausente/vazio/malformado, ida e volta, falha de gravação
└── test_exportacao.py   # cabeçalho, ordem, separador, aspas, score com vírgula

data/
└── problemas.json       # criado na primeira gravação; não versionado com dados reais
```

**Structure Decision**: projeto único com o mínimo exigido pela constituição — `src/` para o
código, `tests/` para os testes, `data/` para o arquivo de dados. Dentro de `src/` os módulos
são planos (sem subpacotes): a separação que importa é interface (`app.py`) versus regras
(`dominio.py`, `armazenamento.py`, `exportacao.py`), e três módulos de regra são suficientes
para manter cada responsabilidade isolada sem criar hierarquia especulativa. `pythonpath =
["src"]` no `pyproject.toml` permite `import dominio` nos testes rodando `pytest` da raiz.

## Complexity Tracking

> Nenhuma violação da Constitution Check. Nada a justificar.
