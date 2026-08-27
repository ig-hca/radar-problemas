"""Persistência dos problemas em arquivo JSON local.

Módulo puro de I/O em arquivo: não importa Streamlit e não acessa rede. O formato
do arquivo está documentado em `specs/001-priorizacao-problemas/data-model.md`:
raiz em lista, na ordem de registro, um objeto por problema, sem o score — que é
derivado das notas e recalculado a cada leitura.
"""

import json
import os
import tempfile
from dataclasses import asdict, fields
from pathlib import Path

from dominio import Problema

# Derivado da localização do módulo, nunca do diretório de trabalho: o Streamlit é
# iniciado de lugares variados e precisa achar sempre o mesmo arquivo.
CAMINHO_DADOS = Path(__file__).resolve().parent.parent / "data" / "problemas.json"

MENSAGEM_DE_LEITURA = (
    "Não foi possível ler os problemas salvos. "
    "O arquivo de dados parece estar vazio ou danificado."
)
MENSAGEM_DE_GRAVACAO = (
    "Não foi possível salvar. "
    "Verifique se há espaço em disco e permissão de escrita na pasta de dados."
)

CAMPOS_DE_TEXTO = ("id", "titulo", "descricao", "publico", "registrado_em")
CAMPOS_DE_NOTA = ("frequencia", "intensidade", "acesso", "disposicao_pagar")


class ErroDeArmazenamento(Exception):
    """Falha de leitura ou gravação.

    A mensagem já é o texto que vai para o usuário: em português, compreensível,
    sem stack trace, caminho de arquivo nem detalhe interno da implementação.
    """


def _montar_problema(item: object) -> Problema:
    """Converte um item do arquivo em Problema, recusando qualquer desvio do formato.

    Item malformado não é ignorado nem corrigido: a leitura inteira falha, porque
    carregar só uma parte dos registros tornaria a ordenação indefensável e o
    usuário não saberia que perdeu dados.
    """
    if not isinstance(item, dict):
        raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA)

    for campo in CAMPOS_DE_TEXTO:
        if not isinstance(item.get(campo), str):
            raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA)

    for campo in CAMPOS_DE_NOTA:
        valor = item.get(campo)
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA)

    return Problema(**{campo.name: item[campo.name] for campo in fields(Problema)})


def ler_problemas(caminho: Path = CAMINHO_DADOS) -> list[Problema]:
    """Devolve os problemas salvos, na ordem de registro (FR-011, FR-017).

    Arquivo ausente devolve lista vazia sem erro — é a primeira abertura. Arquivo
    vazio, danificado ou fora do formato levanta `ErroDeArmazenamento`. A leitura
    não corrige nem regrava o arquivo, e não calcula score.
    """
    try:
        conteudo = caminho.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as erro:
        raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA) from erro

    if not conteudo.strip():
        raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA)

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA) from erro

    if not isinstance(dados, list):
        raise ErroDeArmazenamento(MENSAGEM_DE_LEITURA)

    return [_montar_problema(item) for item in dados]


def gravar_problemas(problemas: list[Problema], caminho: Path = CAMINHO_DADOS) -> None:
    """Grava a lista inteira, em ordem de registro, de forma atômica (FR-011, FR-017a).

    A escrita vai para um temporário no mesmo diretório do destino e só então
    `os.replace` troca os dois. Como a troca é atômica dentro do mesmo sistema de
    arquivos, o destino é sempre o conteúdo antigo inteiro ou o novo inteiro —
    nunca um arquivo pela metade. Em caso de falha o temporário é removido e nada
    do que já estava salvo se perde.
    """
    registros = [asdict(problema) for problema in problemas]
    temporario = None

    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=caminho.parent, delete=False, suffix=".tmp"
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(registros, arquivo, ensure_ascii=False, indent=2)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except (OSError, TypeError, ValueError) as erro:
        if temporario is not None:
            try:
                temporario.unlink()
            except OSError:
                pass
        raise ErroDeArmazenamento(MENSAGEM_DE_GRAVACAO) from erro
