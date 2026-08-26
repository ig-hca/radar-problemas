# Contrato: `src/dominio.py`

Módulo puro. **Não importa `streamlit`**, não lê `st.session_state`, não toca em disco, não
acessa rede. Recebe dados simples e devolve o resultado ao chamador (princípio I).

## Tipos expostos

```python
@dataclass(frozen=True)
class Problema:
    id: str
    titulo: str
    descricao: str
    publico: str
    frequencia: int
    intensidade: int
    acesso: int
    disposicao_pagar: int
    registrado_em: str

@dataclass(frozen=True)
class ItemRanking:
    problema: Problema
    score: float
    score_formatado: str
    posicao: int
    destacado: bool
    rotulo_posicao: str

class ErroDeValidacao(Exception):
    """Entrada recusada. `mensagens` traz um texto em português por problema encontrado."""
    mensagens: list[str]
```

Campos e regras em [../data-model.md](../data-model.md).

## Funções

### `validar_problema(titulo, descricao, publico, frequencia, intensidade, acesso, disposicao_pagar) -> None`

Verifica a entrada crua vinda da tela. Levanta `ErroDeValidacao` com **todas** as mensagens
aplicáveis (não para na primeira). Não cria nada, não grava nada.

- Recusa título vazio, ausente ou só espaços (FR-002).
- Recusa nota ausente, não numérica, fracionária ou fora de 1..5 (FR-003).
- Aceita `descricao` e `publico` vazios (FR-004).
- Aceita `;`, aspas e quebra de linha em qualquer texto (FR-013b).
- Mensagens em português, identificando o campo e o que corrigir (FR-014).

`bool` **não** é aceito como nota: em Python `True == 1`, mas nota booleana é entrada errada.

### `criar_problema(titulo, descricao, publico, frequencia, intensidade, acesso, disposicao_pagar) -> Problema`

Valida (mesmas regras acima, mesma exceção) e devolve um `Problema` novo com `id` gerado por
`uuid.uuid4()` e `registrado_em` do instante atual em ISO 8601. Aplica `strip()` no título;
`descricao` e `publico` ausentes viram `""`. **Não persiste** — quem grava é
`armazenamento.gravar_problemas`.

### `calcular_score(problema) -> float`

Média aritmética simples das quatro notas, peso igual (FR-005). Sempre múltiplo exato de 0,25
entre 1,0 e 5,0.

### `formatar_score(score) -> str`

`f"{score:.2f}".replace(".", ",")` → `"3,50"`, `"5,00"`, `"1,75"`. Duas casas sempre,
inclusive em valores inteiros; vírgula como separador decimal (FR-006, FR-007). A mesma
string vai para a tela e para o CSV (FR-013a).

### `montar_ranking(problemas) -> list[ItemRanking]`

Recebe a lista na ordem de registro e devolve a lista ordenada, com posição, destaque e
rótulo já resolvidos (FR-008, FR-009, FR-010, FR-010a, FR-010b).

- Ordena por `(-score, registrado_em)` sobre a lista em ordem de registro; `sorted` estável
  mantém a ordem do arquivo quando score e carimbo coincidem.
- `posicao` sequencial a partir de 1, sem repetir em empate.
- `destacado = posicao <= 3`; com menos de três problemas, todos ficam destacados.
- `rotulo_posicao` = `"1º"`/`"2º"`/`"3º"` quando destacado, `""` caso contrário.
- Lista vazia devolve lista vazia, sem erro.

## Invariantes

- Nenhuma função do módulo escreve em disco ou faz I/O de rede.
- `montar_ranking(mesma_lista)` devolve sempre o mesmo resultado (SC-005, SC-007).
- Chamadas com entrada inválida não produzem efeito colateral algum (FR-015).

## Cobertura pytest exigida (princípio III)

Score: `4,5,3,2 → "3,50"`; `5,5,5,5 → "5,00"`; `1,2,2,2 → "1,75"`; `1,1,1,1 → "1,00"`;
`1,1,1,2 → "1,25"`.
Validação: título `""`, `"   "`, ausente; nota `0`, `6`, `-1`, `"quatro"`, `None`, `3.5`,
`True`; múltiplos erros de uma vez; descrição/público vazios aceitos; texto com `;`, aspas e
`\n` aceito.
Ranking: ordem decrescente com cinco scores distintos; empate respeitando o carimbo mais
antigo; lista vazia; um, dois e três problemas (destaque e rótulos); quarto colocado sem
rótulo e sem destaque.
