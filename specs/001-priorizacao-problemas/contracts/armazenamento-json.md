# Contrato: `src/armazenamento.py`

Módulo puro de I/O em arquivo local. **Não importa `streamlit`** e não acessa rede
(princípios I e IV).

## Constante de caminho

```python
CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data" / "problemas.json"
```

Derivado da localização do módulo, **nunca** do diretório de trabalho (decisão 1 de
[../research.md](../research.md)). As funções aceitam `caminho` opcional para os testes
usarem `tmp_path`; a interface sempre usa o padrão.

## Exceção

```python
class ErroDeArmazenamento(Exception):
    """Falha de leitura ou gravação. A mensagem já é o texto que vai para o usuário:
    em português, compreensível, sem stack trace nem detalhe interno."""
```

## `ler_problemas(caminho=CAMINHO_DADOS) -> list[Problema]`

| Situação do arquivo | Resultado |
|---|---|
| não existe | `[]`, sem erro — primeira abertura (História 4, cenário 2; FR-016 cuida da tela) |
| existe e é uma lista válida | lista de `Problema` **na ordem do arquivo** (ordem de registro) |
| vazio ou só espaços | `ErroDeArmazenamento` |
| JSON inválido | `ErroDeArmazenamento` |
| raiz não é lista | `ErroDeArmazenamento` |
| item não é objeto | `ErroDeArmazenamento` |
| campo obrigatório ausente, ou nota que não é inteiro | `ErroDeArmazenamento` |

Mensagem única para todos os casos de falha, do tipo: *"Não foi possível ler os problemas
salvos. O arquivo de dados parece estar vazio ou danificado."* Nada de caminho absoluto,
nome de exceção ou trecho de JSON na mensagem (Restrições Técnicas da constituição, FR-017).

A leitura **não** corrige nem regrava o arquivo, e não calcula score.

## `gravar_problemas(problemas, caminho=CAMINHO_DADOS) -> None`

Grava a lista inteira, em ordem de registro, de forma atômica:

1. `caminho.parent.mkdir(parents=True, exist_ok=True)` — cria `data/` se faltar.
2. Arquivo temporário **no mesmo diretório** do destino (`tempfile.NamedTemporaryFile(dir=..., delete=False)`).
3. `json.dump(..., ensure_ascii=False, indent=2)`, encoding UTF-8 — acentos legíveis no arquivo.
4. `flush()` + `os.fsync()`, fechar.
5. `os.replace(temporario, caminho)` — substituição atômica.

Qualquer `OSError`/`TypeError`/`ValueError` no caminho acima ⇒ remover o temporário (ignorando
falha na remoção) e levantar `ErroDeArmazenamento` com mensagem do tipo: *"Não foi possível
salvar. Verifique se há espaço em disco e permissão de escrita na pasta de dados."*

**Garantia (FR-017a)**: em caso de falha, `caminho` continua exatamente como estava antes da
chamada — conteúdo antigo íntegro ou arquivo inexistente. Nunca um arquivo pela metade, e
nenhum resíduo temporário deixado para trás.

O score **não** é gravado (é derivado — FR-005, decisão 4 de research).

## Cobertura pytest exigida (princípio III)

Usando `tmp_path`, nunca arquivos fora do repositório:

- arquivo ausente ⇒ `[]` sem erro;
- gravar e reler devolve os mesmos problemas, na mesma ordem, com os mesmos tipos
  (notas voltam como `int`) — SC-005;
- acentos aparecem legíveis no texto do arquivo (`"ç"` presente, sem `\uXXXX`);
- arquivo vazio, só espaços, JSON inválido, raiz `{}`, item `"texto"`, campo faltando, nota
  `"4"` ⇒ `ErroDeArmazenamento`;
- falha de gravação (destino simulado como não gravável, ou `os.replace` com `monkeypatch`
  levantando `OSError`) ⇒ `ErroDeArmazenamento`, arquivo anterior intacto e nenhum arquivo
  temporário sobrando no diretório;
- o score não aparece como chave no JSON gravado.
