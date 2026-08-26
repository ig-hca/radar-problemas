# Contrato: `src/exportacao.py`

Módulo puro. **Não importa `streamlit`**, **não escreve em disco**: gera o arquivo inteiro em
memória e devolve os bytes (princípio I, decisão 7 de [../research.md](../research.md)).

## `gerar_csv(itens) -> bytes`

Recebe a lista de `ItemRanking` já ordenada por `dominio.montar_ranking` e devolve o conteúdo
completo do arquivo, pronto para `st.download_button`.

```python
buffer = io.StringIO()
escritor = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
escritor.writerow(CABECALHO)
for item in itens:
    escritor.writerow([...])
return buffer.getvalue().encode("utf-8-sig")
```

## Formato

| Aspecto | Decisão | Requisito |
|---|---|---|
| Separador de colunas | `;` (ponto e vírgula) | FR-013a — a vírgula decimal do score nunca vira troca de coluna |
| Aspas | `csv.QUOTE_MINIMAL` da biblioteca padrão | FR-013b — aspas só onde há `;`, `"` ou quebra de linha; aspas internas duplicadas pela própria biblioteca |
| Encoding | `utf-8-sig` (UTF-8 com BOM) | FR-012, SC-006 — Excel em português abre com acentos corretos e colunas separadas, sem assistente de importação |
| Fim de linha | `\r\n` | Padrão CSV (RFC 4180); mantém a quebra de linha *dentro* de um campo distinta do fim de registro |
| Cabeçalho | sempre presente, uma linha | FR-013 |
| Ordem das linhas | a mesma do ranking recebido | FR-013 |
| Score | `item.score_formatado` (`3,50`) | FR-013a — string idêntica à da tela |
| Notas | inteiros, sem formatação | FR-013 |

Colunas, na ordem: `Título`, `Descrição`, `Público afetado`, `Frequência`, `Intensidade`,
`Acesso ao público`, `Disposição a pagar`, `Score` — ver [../data-model.md](../data-model.md).

Lista vazia ⇒ bytes contendo **apenas** a linha de cabeçalho (Edge Case "Lista vazia").

## Entrega ao usuário (feita em `src/app.py`)

`st.download_button(label=..., data=gerar_csv(itens), file_name="radar-de-problemas.csv",
mime="text/csv")` — uma única ação do usuário, arquivo cai na pasta de downloads do
dispositivo, sem informar caminho e sem arquivo intermediário no projeto (FR-012, FR-012a).

## Cobertura pytest exigida (princípio III)

- cabeçalho exato, com as oito colunas na ordem definida;
- uma linha por problema, na mesma ordem do ranking recebido;
- lista vazia ⇒ só o cabeçalho;
- score sai como `3,50` (vírgula, duas casas), inclusive `5,00`;
- descrição contendo `;` sai entre aspas e o número de colunas da linha não muda;
- descrição contendo aspas sai com as aspas duplicadas;
- descrição contendo `\n` sai entre aspas e volta inteira em um único campo — verificado
  relendo com `csv.reader(..., delimiter=";")`;
- os bytes começam com o BOM `b"\xef\xbb\xbf"`;
- texto acentuado sobrevive à ida e volta pela decodificação `utf-8-sig`;
- a função não cria arquivo nenhum (diretório de trabalho e `tmp_path` inalterados).
