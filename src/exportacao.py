"""Geração do arquivo CSV com a lista de problemas.

Módulo puro: não importa Streamlit e não escreve em disco. Monta o arquivo inteiro
em memória e devolve os bytes, prontos para o botão de download entregar.
"""

import csv
import io

from dominio import ItemRanking

CABECALHO = [
    "Título",
    "Descrição",
    "Público afetado",
    "Frequência",
    "Intensidade",
    "Acesso ao público",
    "Disposição a pagar",
    "Score",
]


def gerar_csv(itens: list[ItemRanking]) -> bytes:
    """Devolve o conteúdo do arquivo exportado, na ordem do ranking recebido (FR-012, FR-013).

    O separador é ponto e vírgula para a vírgula decimal do score nunca ser
    confundida com troca de coluna, e o encoding é UTF-8 com BOM porque é o que faz
    a planilha em português abrir o arquivo já com acentos corretos e colunas
    separadas, sem assistente de importação (FR-013a). O escapamento de ponto e
    vírgula, aspas e quebra de linha dentro do texto fica por conta da biblioteca
    padrão (FR-013b). Lista vazia devolve só o cabeçalho.
    """
    buffer = io.StringIO()
    escritor = csv.writer(
        buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n"
    )

    escritor.writerow(CABECALHO)
    for item in itens:
        problema = item.problema
        escritor.writerow(
            [
                problema.titulo,
                problema.descricao,
                problema.publico,
                problema.frequencia,
                problema.intensidade,
                problema.acesso,
                problema.disposicao_pagar,
                item.score_formatado,
            ]
        )

    return buffer.getvalue().encode("utf-8-sig")
