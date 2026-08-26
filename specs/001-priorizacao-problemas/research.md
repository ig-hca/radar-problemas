# Phase 0 — Research: Priorização de Candidatos a Problema

A stack já vinha fixada pela constituição (Python 3.11+, Streamlit, pytest, JSON local) e o
input do usuário fechou as escolhas restantes. Não sobrou nenhum **NEEDS CLARIFICATION** no
Technical Context. O que segue registra as decisões que ainda tinham alternativa real, com o
motivo de cada uma.

---

## 1. Localização do arquivo de dados

**Decisão**: `CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data" / "problemas.json"`,
calculado dentro de `src/armazenamento.py` (`parent` = `src/`, `parent.parent` = raiz do
repositório).

**Racional**: Streamlit é executado de diretórios variados (`streamlit run src/app.py` da
raiz, ou a partir do IDE) e o diretório de trabalho não é confiável. Derivar da localização
do módulo faz o aplicativo encontrar sempre o mesmo arquivo, independentemente de onde foi
iniciado — condição prática para FR-011 e SC-005.

**Alternativas consideradas**: `Path("data/problemas.json")` relativo ao cwd (rejeitado:
cria arquivos diferentes conforme o diretório de partida, quebrando a persistência sem erro
visível); variável de ambiente (rejeitado: configuração sem pedido na spec, princípio VI).

---

## 2. Gravação atômica

**Decisão**: escrever em arquivo temporário criado **no mesmo diretório** do destino
(`tempfile.NamedTemporaryFile(dir=..., delete=False)`), com `flush()` + `os.fsync()`, fechar
e então `os.replace(temporario, destino)`. Em qualquer exceção, remover o temporário e
levantar `ErroDeArmazenamento`.

**Racional**: `os.replace` é atômico dentro do mesmo sistema de arquivos no POSIX e no
Windows — o arquivo definitivo ou é o antigo inteiro ou o novo inteiro, nunca metade. É o que
FR-017a exige: falha de escrita não pode deixar gravação parcial. O temporário no mesmo
diretório evita que a substituição atravesse volumes (onde `os.replace` deixaria de ser
atômico e poderia falhar).

**Alternativas consideradas**: `open(destino, "w")` direto (rejeitado: um erro no meio da
escrita trunca o arquivo e perde todos os registros anteriores); temporário em `/tmp`
(rejeitado: volume potencialmente diferente); escrita com backup `.bak` (rejeitado: não
pedido pela spec e não resolve o problema melhor que `os.replace`).

---

## 3. Propagação da falha de gravação até a interface

**Decisão**: `armazenamento.gravar_problemas` levanta `ErroDeArmazenamento`, exceção própria
com mensagem já em português e compreensível. `src/app.py` captura essa exceção específica e
exibe `st.error(...)` **sem** atualizar a lista em memória. A ordem é: validar → montar a
nova lista → gravar → só em caso de sucesso trocar o estado da sessão.

**Racional**: FR-017a e o cenário 4 da História 4 exigem que a lista permaneça exatamente
como estava. Gravar **antes** de mexer no estado é o que garante isso, e uma exceção própria
evita que a interface tenha de inspecionar `OSError`/`PermissionError` (detalhe interno) para
decidir a mensagem.

**Alternativas consideradas**: devolver `(ok, mensagem)` (rejeitado: torna fácil ignorar o
erro por engano, e o caminho feliz fica ruidoso); deixar `OSError` vazar até o Streamlit
(rejeitado: mostra stack trace ao usuário, proibido pelas Restrições Técnicas da
constituição).

---

## 4. Arredondamento e formatação do score

**Decisão**: guardar as notas como inteiros; calcular `score = sum(notas) / 4` como `float` na
leitura; formatar apenas na exibição e na exportação com
`f"{score:.2f}".replace(".", ",")`. O valor arredondado nunca é gravado no JSON.

**Racional**: com quatro notas inteiras, a soma vai de 4 a 20 e a média é sempre um múltiplo
exato de 0,25 (`x,00`, `x,25`, `x,50`, `x,75`). Esses valores são representáveis exatamente em
ponto flutuante binário, então `:.2f` é exato e o caso ambíguo de "meia unidade" — onde
`round()` do Python usaria arredondamento bancário e divergiria da suposição da spec — nunca
ocorre. Não é preciso trazer `Decimal` para dentro do domínio, e o código fica mais legível
(princípio V). Guardar o score arredondado seria dado derivado no arquivo, que sai de sincronia
se a fórmula mudar.

**Alternativas consideradas**: `Decimal` com `ROUND_HALF_UP` (rejeitado: complexidade sem
caso de uso — nenhuma média atingível cai no meio do caminho); `round(score, 2)` (rejeitado:
arredondamento bancário contraria a suposição declarada na spec, mesmo que hoje inócuo);
gravar `score` no JSON (rejeitado: duplicação de verdade, FR-005 define o score como derivado).

---

## 5. Ordenação e desempate

**Decisão**: `sorted(problemas, key=lambda p: (-p.score, p.registrado_em))`, sobre a lista na
ordem de registro (o JSON guarda os problemas em ordem de inserção, sempre por `append`).

**Racional**: a chave primária atende FR-008 (decrescente por score) e `registrado_em` atende
FR-009 (mais antigo primeiro no empate), que é o "carimbo de registro usado para o desempate"
do input. Como `sorted` é estável, dois registros com o mesmo score **e** o mesmo carimbo
(caso extremo de dois registros no mesmo microssegundo) ainda saem na ordem do arquivo — a
ordenação é reproduzível para os mesmos dados em qualquer execução, como SC-005 exige.

**Alternativas consideradas**: desempate por título (rejeitado: contraria FR-009 e títulos
duplicados são permitidos); desempate por `id` (rejeitado: UUID4 é aleatório, ordem sem
significado); confiar apenas na estabilidade do `sorted` sem chave de carimbo (rejeitado: o
input pede o carimbo explícito, e uma chave explícita documenta a regra no próprio código).

---

## 6. Posição e marca de top 3 vindas do domínio

**Decisão**: `dominio.montar_ranking(problemas)` devolve uma lista de `ItemRanking`, cada um
com `posicao` (int, começando em 1), `destacado` (bool) e `rotulo_posicao` (str: `"1º"`,
`"2º"`, `"3º"` ou `""`), além do problema e do `score_formatado`. `destacado` é
`posicao <= 3`, o que cobre naturalmente o caso de menos de três problemas.

**Racional**: FR-010b é explícito — a informação de quem está no top 3 é derivada da ordenação
e entregue junto com cada problema, não decidida na tela. Entregar até o rótulo textual
pronto deixa `app.py` sem nenhuma condicional de regra, atendendo o princípio II ao pé da
letra, e torna FR-010a testável por pytest sem subir o Streamlit.

**Alternativas consideradas**: devolver só a lista ordenada e a tela fazer `if i < 3`
(rejeitado: viola FR-010b e princípio II); devolver posição mas montar `"1º"` na tela
(rejeitado: é regra de apresentação do domínio segundo FR-010a, e sem teste se ficar na tela).

---

## 7. Exportação em memória

**Decisão**: `exportacao.gerar_csv(itens_do_ranking) -> bytes`. Monta com `io.StringIO` +
`csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")`, e
devolve `buffer.getvalue().encode("utf-8-sig")`. A interface passa esses bytes direto para
`st.download_button(..., file_name="radar-de-problemas.csv", mime="text/csv")`.

**Racional**: `st.download_button` entrega o arquivo pela pasta de downloads do navegador,
atendendo FR-012a sem o usuário informar caminho. Gerar em memória evita arquivo intermediário
em disco (pedido do input) e elimina toda uma classe de erro de escrita na exportação. O
delimitador `;` atende FR-013a e mantém a vírgula decimal do score sem ambiguidade de coluna;
`utf-8-sig` (BOM) é o que faz o Excel em português abrir o arquivo já com acentos corretos e
colunas separadas, sem assistente de importação (FR-012, SC-006); `QUOTE_MINIMAL` da
biblioteca padrão coloca aspas exatamente nos campos com `;`, aspas ou quebra de linha e
duplica aspas internas, que é FR-013b sem escrever escapamento à mão.

**Alternativas consideradas**: `pandas.to_csv` (rejeitado: dependência nova sem justificativa,
princípio IV); escrever em `data/export.csv` e oferecer o arquivo (rejeitado: arquivo
intermediário, e o usuário teria de localizá-lo — contraria FR-012a); `.xlsx` via openpyxl
(rejeitado: dependência nova; CSV com `;` já abre sem ajuste manual).

---

## 8. Comportamento com JSON ausente, vazio ou malformado

**Decisão**: três casos distintos —

- **arquivo ausente**: devolve lista vazia, **sem** mensagem de erro (é a primeira abertura,
  cenário 2 da História 4; a tela mostra a indicação de lista vazia de FR-016);
- **arquivo vazio, só espaços, JSON inválido ou estrutura inesperada** (raiz que não é lista,
  item que não é objeto, campo obrigatório ausente ou de tipo errado): levanta
  `ErroDeArmazenamento` com mensagem em português sem detalhe técnico;
- na interface, esse erro vira `st.error(...)` e a sessão segue com lista vazia em memória,
  utilizável para novos registros (FR-017).

**Consequência aceita e registrada**: se o usuário registrar um problema novo depois de uma
leitura falha, a gravação substitui o arquivo ilegível — o conteúdo anterior, que já não podia
ser lido, é perdido. Isso é o que FR-017 pede ("permanece utilizável para novos registros")
levado à sua conclusão. Criar cópia de segurança do arquivo corrompido resolveria o
incômodo, mas é comportamento que a spec não pede e que o princípio VI manda devolver para a
spec em vez de codificar de passagem.

**Alternativas consideradas**: tratar arquivo ausente como erro (rejeitado: contradiz o
cenário 2 da História 4 — primeira abertura é situação normal); ignorar silenciosamente itens
malformados e carregar o resto (rejeitado: a ordenação deixaria de ser defensável e o usuário
não saberia que perdeu registros); bloquear novos registros até o arquivo ser consertado
(rejeitado: contraria FR-017 explicitamente).

---

## 9. Widgets das notas na interface

**Decisão**: `st.number_input(..., value=3, step=1)` **sem** `min_value`/`max_value`, e toda a
verificação de faixa feita por `dominio.validar_problema`.

**Racional**: se o widget travasse a faixa, a regra de 1 a 5 passaria a morar na tela — regra
não coberta por teste, que é exatamente o que o princípio II proíbe — e os cenários 2 e 3 da
História 3 (nota 6, nota 0) ficariam impossíveis de exercitar no aplicativo. Com o widget
livre, FR-003 e FR-014 são exercidos de verdade e continuam testados por pytest no domínio.

**Alternativas consideradas**: `st.slider(1, 5)` (rejeitado: mesmo problema, e ainda esconde
a regra); `st.number_input` com `min_value=1, max_value=5` (rejeitado: idem); validar na tela
antes de chamar o domínio (rejeitado: duplicação de regra, princípio II).

---

## 10. Estado da sessão e ciclo de vida

**Decisão**: a lista de problemas é lida do disco **uma vez por sessão**, guardada em
`st.session_state`, e regravada inteira a cada registro bem-sucedido. O `ErroDeArmazenamento`
da leitura inicial também fica no `session_state` para ser exibido enquanto durar a sessão.

**Racional**: Streamlit reexecuta o script inteiro a cada interação; sem `session_state` o
arquivo seria lido a cada clique e a mensagem de erro de leitura piscaria de forma
imprevisível. Regravar a lista inteira (em vez de append incremental) mantém o formato do
arquivo trivialmente correto e é irrelevante em custo para a escala de SC-003.

**Alternativas consideradas**: `@st.cache_data` (rejeitado: invalidação de cache é
complexidade desnecessária num único arquivo pequeno); reler o disco a cada rerun (rejeitado:
I/O repetido e mensagens de erro instáveis).
