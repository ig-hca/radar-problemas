# Phase 1 — Data Model: Priorização de Candidatos a Problema

Duas entidades: **Problema**, que é persistido, e **ItemRanking**, que é derivado em tempo de
execução e nunca gravado. O score também é derivado — calculado na leitura, formatado só na
exibição (FR-005, decisão 4 de [research.md](./research.md)).

---

## Entidade: Problema

Uma dor observada em campo que o usuário está avaliando.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id` | `str` | sim | Identificador estável, gerado no registro com `uuid.uuid4()` e nunca alterado. Não é exibido nem exportado; existe para dar identidade ao registro entre execuções. |
| `titulo` | `str` | sim | Não vazio após `strip()` (FR-002). Gravado já com `strip()` aplicado. Duplicatas permitidas. |
| `descricao` | `str` | não | Opcional (FR-004); ausente vira `""`. Aceita `;`, aspas e quebra de linha sem recusa nem substituição (FR-013b). |
| `publico` | `str` | não | Público afetado. Opcional (FR-004); ausente vira `""`. Mesmas liberdades de texto da descrição. |
| `frequencia` | `int` | sim | Inteiro de 1 a 5 (FR-003). Com que frequência a dor acontece. |
| `intensidade` | `int` | sim | Inteiro de 1 a 5 (FR-003). Quão intensa é a dor. |
| `acesso` | `int` | sim | Inteiro de 1 a 5 (FR-003). Quão fácil é chegar em quem sofre a dor. |
| `disposicao_pagar` | `int` | sim | Inteiro de 1 a 5 (FR-003). Disposição do público a pagar por uma solução. |
| `registrado_em` | `str` | sim | Carimbo do momento do registro, ISO 8601 (`datetime.now().isoformat(timespec="microseconds")`). Usado no desempate (FR-009) e ordenável como string por ser ISO de largura fixa. |

**Derivado, não armazenado**:

- `score` — `(frequencia + intensidade + acesso + disposicao_pagar) / 4`, `float` (FR-005).
  Sempre múltiplo exato de 0,25, entre 1,00 e 5,00.
- `score_formatado` — `f"{score:.2f}".replace(".", ",")` → `"3,50"`, `"5,00"`, `"1,75"`
  (FR-006, FR-007). Mesma string na tela e no CSV (FR-013a).

**Transições de estado**: nenhuma. Um Problema é criado e permanece imutável — esta versão
não cobre edição nem exclusão (Fora de Escopo da spec).

---

## Entidade: ItemRanking

A visão de um Problema dentro da ordenação. Produzida por `dominio.montar_ranking`, consumida
pela tela e pela exportação. Nunca é gravada.

| Campo | Tipo | Regra |
|---|---|---|
| `problema` | `Problema` | O registro em si, intocado. |
| `score` | `float` | Score calculado (FR-005). |
| `score_formatado` | `str` | `"3,50"` — pronto para exibir e exportar (FR-006, FR-007, FR-013a). |
| `posicao` | `int` | Posição na ordenação, começando em 1. Estritamente sequencial: em caso de empate, as posições não se repetem (suposição posicional da spec). |
| `destacado` | `bool` | `posicao <= 3`. Com menos de três problemas, todos os existentes ficam `True` (FR-010). |
| `rotulo_posicao` | `str` | `"1º"`, `"2º"`, `"3º"` quando `destacado`; `""` caso contrário (FR-010a). Vem pronto do domínio (FR-010b). |

**Regra de ordenação** (FR-008, FR-009): `sorted(problemas, key=lambda p: (-score(p), p.registrado_em))`
sobre a lista na ordem de registro. Decrescente por score; empate resolvido pelo carimbo mais
antigo; `sorted` estável garante ordem reproduzível mesmo com carimbos idênticos.

---

## Regras de validação (FR-002, FR-003, FR-014)

Aplicadas por `dominio.validar_problema` sobre a entrada crua, **antes** de qualquer gravação.
Todas as mensagens em português, apontando o campo e o que corrigir. A validação coleta
**todos** os erros e os devolve juntos, em vez de parar no primeiro.

| Situação | Mensagem |
|---|---|
| `titulo` vazio, ausente ou só espaços | `O título é obrigatório.` |
| nota ausente ou não numérica | `A nota de {campo} é obrigatória e deve ser um número inteiro de 1 a 5.` |
| nota fracionária (ex.: `3.5`) | `A nota de {campo} deve ser um número inteiro de 1 a 5.` |
| nota inteira fora de 1..5 (ex.: `0`, `6`) | `A nota de {campo} deve estar entre 1 e 5.` |

`{campo}` é o rótulo em português da dimensão: *frequência*, *intensidade*, *acesso ao
público*, *disposição a pagar*.

Registro recusado ⇒ nada é gravado, nem parcialmente, e a lista permanece idêntica (FR-015).

---

## Formato do arquivo `data/problemas.json`

UTF-8, `ensure_ascii=False` (acentos legíveis no arquivo), `indent=2`. A raiz é uma **lista**,
na ordem de registro — o mais antigo primeiro. A ordenação por score é sempre recalculada na
leitura; o arquivo nunca guarda ranking, posição, destaque nem score.

```json
[
  {
    "id": "0f1e2d3c-4b5a-6789-abcd-ef0123456789",
    "titulo": "Dono de padaria perde vendas por falta de controle de estoque",
    "descricao": "Relatou jogar fora produto vencido toda semana;\nnão sabe o quanto perde.",
    "publico": "Donos de padaria de bairro",
    "frequencia": 5,
    "intensidade": 4,
    "acesso": 3,
    "disposicao_pagar": 2,
    "registrado_em": "2026-08-26T09:14:02.481930"
  }
]
```

**Contrato de leitura** (FR-017): arquivo ausente ⇒ lista vazia sem erro. Arquivo vazio, só
espaços, JSON inválido, raiz que não é lista, item que não é objeto, campo obrigatório ausente
ou de tipo errado ⇒ `ErroDeArmazenamento` com mensagem compreensível, sem detalhe interno.
Detalhes em [contracts/armazenamento-json.md](./contracts/armazenamento-json.md).

---

## Colunas do arquivo exportado (FR-013)

Uma linha de cabeçalho e uma linha por problema, na mesma ordem decrescente da tela.

| # | Cabeçalho | Origem |
|---|---|---|
| 1 | `Título` | `problema.titulo` |
| 2 | `Descrição` | `problema.descricao` |
| 3 | `Público afetado` | `problema.publico` |
| 4 | `Frequência` | `problema.frequencia` |
| 5 | `Intensidade` | `problema.intensidade` |
| 6 | `Acesso ao público` | `problema.acesso` |
| 7 | `Disposição a pagar` | `problema.disposicao_pagar` |
| 8 | `Score` | `item.score_formatado` (`3,50`) |

`id`, `registrado_em`, posição e destaque não são exportados — FR-013 lista exatamente estas
oito colunas, e o princípio VI barra acrescentar outras.
