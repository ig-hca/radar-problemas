# Contrato: `src/app.py` (interface Streamlit)

Único módulo que importa `streamlit`. **Não calcula nada** (princípio II): coleta a entrada,
chama o domínio, exibe o que ele devolve. Nenhuma fórmula de score, nenhum limiar de top 3,
nenhuma regra de faixa de nota mora aqui — nem repetida "por segurança".

## Estado da sessão

| Chave | Conteúdo |
|---|---|
| `problemas` | lista de `Problema` em ordem de registro, carregada uma vez por sessão |
| `erro_leitura` | mensagem de `ErroDeArmazenamento` da leitura inicial, ou `None` |

Na primeira execução da sessão: `ler_problemas()` dentro de `try/except ErroDeArmazenamento`.
Sucesso ⇒ `problemas`. Falha ⇒ `problemas = []` e `erro_leitura` preenchido; o aplicativo
segue utilizável para novos registros (FR-017, decisão 8 de [../research.md](../research.md)).

## Regiões da tela

**1. Mensagem de erro de leitura** — se `erro_leitura`, `st.error(erro_leitura)`. Texto em
português, sem stack trace (FR-017).

**2. Formulário de registro** (`st.form`) — título (`text_input`), descrição (`text_area`),
público afetado (`text_input`) e quatro `number_input(value=3, step=1)` **sem `min_value`/
`max_value`**: a faixa de 1 a 5 é decidida pelo domínio, não pelo widget (decisão 9 de
research). Ao submeter:

```
1. dominio.criar_problema(...)          → ErroDeValidacao? exibe st.error de cada mensagem e para
2. nova_lista = problemas + [novo]
3. armazenamento.gravar_problemas(nova_lista)  → ErroDeArmazenamento? exibe st.error e para
4. st.session_state["problemas"] = nova_lista  (só depois da gravação bem-sucedida)
```

A ordem dos passos 3 e 4 é o que cumpre FR-015 e FR-017a: se a validação recusa ou a gravação
falha, o estado em memória e o arquivo permanecem exatamente como estavam.

**3. Lista ordenada** — `itens = dominio.montar_ranking(st.session_state["problemas"])`.

- `itens` vazio ⇒ mensagem clara de lista vazia, nunca tela em branco nem erro (FR-016).
- caso contrário, uma linha por item exibindo `rotulo_posicao`, título, público, as quatro
  notas e `score_formatado`. `posicao`, `destacado` e `rotulo_posicao` chegam prontos do
  domínio — a tela **não** faz `if i < 3` (FR-010b).
- linhas com `destacado` recebem diferenciação visual **além** do rótulo textual; o rótulo é
  o que garante a conferência sem depender de cor (FR-010a).

**4. Botão de exportação** — `st.download_button(data=exportacao.gerar_csv(itens),
file_name="radar-de-problemas.csv", mime="text/csv")`. Uma única ação, arquivo em memória,
download direto (FR-012, FR-012a). Disponível também com a lista vazia — o arquivo sai só com
o cabeçalho (Edge Case "Lista vazia").

## Proibições verificáveis na revisão da dupla

- `app.py` não contém `/ 4`, `sum(`, `sorted(`, `<= 3`, `round(`, `.replace(".", ",")` nem
  comparação de nota com `1`/`5`;
- `dominio.py`, `armazenamento.py` e `exportacao.py` não contêm `import streamlit`;
- toda mensagem ao usuário vem do domínio/armazenamento ou é texto fixo de tela — nenhuma é
  montada a partir de exceção genérica do Python.

## Verificação

Esta camada não é coberta por pytest (princípio III cobre o domínio). É verificada à mão pelo
roteiro de [../quickstart.md](../quickstart.md).
