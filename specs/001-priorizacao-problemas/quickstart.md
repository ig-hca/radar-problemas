# Quickstart — Validar a feature de ponta a ponta

Roteiro para conferir que a implementação atende a spec. Os cenários automáticos rodam por
pytest; os manuais são o que a dupla executa na tela antes de dar a feature por pronta.

## Pré-requisitos

- Python 3.11 ou superior (`python --version`)
- Repositório clonado, terminal aberto **na raiz** do repositório
- Sem conexão de rede necessária depois da instalação das dependências

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 1. Suíte de testes (gate obrigatório)

```bash
pytest
```

Rodar sempre **da raiz** — `pythonpath = ["src"]` no `pyproject.toml` é o que permite
`import dominio` nos testes. Esperado: suíte inteira verde. Uma mudança só é considerada
pronta com a suíte completa passando (princípio III da constituição).

O que a suíte precisa cobrir está listado em cada contrato:
[dominio](./contracts/dominio.md), [armazenamento](./contracts/armazenamento-json.md),
[exportação](./contracts/exportacao-csv.md).

## 2. Verificação dos gates da constituição

```bash
# domínio não pode importar streamlit — não deve retornar nada
grep -rn "import streamlit" src/dominio.py src/armazenamento.py src/exportacao.py

# a interface não pode calcular — inspecionar cada ocorrência, se houver
grep -nE "/ 4|sum\(|sorted\(|<= 3|round\(" src/app.py
```

No PowerShell: `Select-String -Pattern "import streamlit" -Path src\dominio.py,src\armazenamento.py,src\exportacao.py`.

## 3. Subir o aplicativo

```bash
streamlit run src/app.py
```

Abre no navegador local. Deve funcionar com a rede desligada (princípio IV).

## 4. Cenários manuais

Rodar em sequência, na mesma sessão, a partir de `data/problemas.json` inexistente.

| # | Passos | Esperado | Cobre |
|---|---|---|---|
| 1 | Abrir o aplicativo sem nenhum registro | Indicação clara de lista vazia, sem erro | FR-016, US4-2 |
| 2 | Registrar título + descrição + público, notas `4, 5, 3, 2` | Problema na lista com score `3,50` | US1-1, FR-005..007 |
| 3 | Registrar com notas `5, 5, 5, 5` e depois `1, 2, 2, 2` | Scores `5,00` e `1,75` | US1-2, US1-3 |
| 4 | Registrar mais dois, totalizando cinco com scores distintos | Lista do maior para o menor score; `1º`, `2º` e `3º` marcados e destacados; 4º e 5º sem marca e sem destaque | US2-1, US2-2, FR-008, FR-010, FR-010a |
| 5 | Registrar dois problemas com as mesmas quatro notas | Ficam adjacentes, o registrado primeiro aparece antes; recarregar a página mantém a mesma ordem | US2-3, FR-009 |
| 6 | Submeter com título vazio, e depois só com espaços | Mensagem clara de título obrigatório; lista inalterada | US3-1, US3-4, FR-002, FR-015 |
| 7 | Submeter com intensidade `6`, e depois frequência `0` | Mensagem clara de nota entre 1 e 5; lista inalterada | US3-2, US3-3, FR-003, FR-014 |
| 8 | Submeter deixando descrição e público vazios | Registro aceito normalmente | FR-004 |
| 9 | Fechar o aplicativo (Ctrl+C) e rodar `streamlit run src/app.py` de novo | Todos os problemas voltam com os mesmos dados, scores e ordem | US4-1, FR-011, SC-005 |
| 10 | Abrir `data/problemas.json` num editor | Acentos legíveis (`ç`, `ã`), sem `\uXXXX`; nenhuma chave de score; notas como inteiros | Formato do arquivo |
| 11 | Escrever `isto não é json` em `data/problemas.json` e reabrir o aplicativo | Mensagem compreensível, sem stack trace; aplicativo segue utilizável para registrar | US4-3, FR-017 |
| 12 | Restaurar o arquivo, deixá-lo somente leitura, tentar registrar | Mensagem compreensível de falha ao salvar; problema **não** aparece na lista; arquivo intacto, sem `.tmp` sobrando na pasta `data/` | US4-4, FR-017a |
| 13 | Registrar um problema cuja descrição tenha `;`, aspas e quebra de linha | Aceito sem recusa nem substituição | FR-013b |
| 14 | Clicar em exportar uma única vez | Arquivo `radar-de-problemas.csv` cai na pasta de downloads, sem pedir caminho; nenhum CSV aparece no projeto | US5-1, FR-012, FR-012a |
| 15 | Abrir o arquivo baixado no Excel/LibreOffice em português (duplo clique) | Oito colunas separadas sem ajuste manual; acentos corretos; score `3,50` em coluna própria; linhas na mesma ordem decrescente da tela | US5-2, US5-3, SC-006, FR-013, FR-013a |
| 16 | Localizar no arquivo aberto a linha do problema do passo 13 | Descrição inteira em uma única célula, idêntica ao digitado; demais colunas alinhadas | US5-4, FR-013b |
| 17 | Apagar `data/problemas.json`, reabrir e exportar com a lista vazia | Arquivo baixado só com a linha de cabeçalho, sem erro | Edge Case "Lista vazia" |
| 18 | Com apenas dois problemas registrados, ver a lista | Só `1º` e `2º`, ambos destacados, nenhum `3º`, sem erro | US2-4, Edge Case "Menos de três" |

## 5. Critérios de conclusão

- [ ] `pytest` verde da raiz do repositório
- [ ] Os 18 cenários manuais conferidos
- [ ] `grep` do passo 2 sem ocorrência de Streamlit no domínio e sem cálculo em `app.py`
- [ ] Nenhuma funcionalidade além dos FRs da spec (princípio VI)
