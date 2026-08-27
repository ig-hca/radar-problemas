"""Testes da geração do arquivo CSV exportado."""

import csv
import io

import dominio
import exportacao
from dominio import Problema

CABECALHO_ESPERADO = [
    "Título",
    "Descrição",
    "Público afetado",
    "Frequência",
    "Intensidade",
    "Acesso ao público",
    "Disposição a pagar",
    "Score",
]

BOM = b"\xef\xbb\xbf"


def problema(titulo, notas=(4, 5, 3, 2), descricao="", publico="Público de teste"):
    """Monta um Problema com o que o CSV precisa exibir."""
    frequencia, intensidade, acesso, disposicao_pagar = notas
    return Problema(
        id=f"id-{titulo}",
        titulo=titulo,
        descricao=descricao,
        publico=publico,
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
        registrado_em="2026-08-26T09:00:00.000000",
    )


def linhas_do_csv(conteudo):
    """Relê os bytes gerados do mesmo jeito que uma planilha releria."""
    texto = conteudo.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(texto, newline=""), delimiter=";"))


# --- estrutura (FR-013) ---


def test_csv_comeca_com_o_cabecalho_das_oito_colunas():
    conteudo = exportacao.gerar_csv(dominio.montar_ranking([problema("Uma dor")]))

    assert linhas_do_csv(conteudo)[0] == CABECALHO_ESPERADO


def test_csv_tem_uma_linha_por_problema_na_ordem_do_ranking():
    itens = dominio.montar_ranking(
        [
            problema("Score médio", notas=(3, 3, 3, 3)),
            problema("Score máximo", notas=(5, 5, 5, 5)),
            problema("Score mínimo", notas=(1, 1, 1, 1)),
        ]
    )

    linhas = linhas_do_csv(exportacao.gerar_csv(itens))

    assert len(linhas) == 4
    assert [linha[0] for linha in linhas[1:]] == ["Score máximo", "Score médio", "Score mínimo"]


def test_csv_de_lista_vazia_traz_so_o_cabecalho():
    assert linhas_do_csv(exportacao.gerar_csv([])) == [CABECALHO_ESPERADO]


# --- formato (FR-013a) ---


def test_score_sai_com_virgula_e_duas_casas():
    itens = dominio.montar_ranking(
        [problema("Meio", notas=(4, 5, 3, 2)), problema("Cheio", notas=(5, 5, 5, 5))]
    )

    linhas = linhas_do_csv(exportacao.gerar_csv(itens))

    assert [linha[-1] for linha in linhas[1:]] == ["5,00", "3,50"]


def test_notas_saem_como_inteiros_sem_formatacao():
    conteudo = exportacao.gerar_csv(dominio.montar_ranking([problema("Uma dor")]))

    assert linhas_do_csv(conteudo)[1][3:7] == ["4", "5", "3", "2"]


def test_colunas_sao_separadas_por_ponto_e_virgula():
    conteudo = exportacao.gerar_csv(dominio.montar_ranking([problema("Uma dor")]))
    primeira_linha = conteudo.decode("utf-8-sig").splitlines()[0]

    assert primeira_linha.count(";") == 7
    assert "," not in primeira_linha


def test_bytes_comecam_com_o_bom_que_o_excel_espera():
    assert exportacao.gerar_csv([]).startswith(BOM)


# --- texto livre (FR-013b) ---


def test_descricao_com_ponto_e_virgula_volta_inteira_e_sem_coluna_extra():
    descricao = "Perde produto; não sabe quanto"
    itens = dominio.montar_ranking([problema("Uma dor", descricao=descricao)])

    linha = linhas_do_csv(exportacao.gerar_csv(itens))[1]

    assert len(linha) == 8
    assert linha[1] == descricao


def test_descricao_com_aspas_volta_identica():
    descricao = 'O cliente disse "perco 30% toda semana"'
    itens = dominio.montar_ranking([problema("Uma dor", descricao=descricao)])

    linha = linhas_do_csv(exportacao.gerar_csv(itens))[1]

    assert len(linha) == 8
    assert linha[1] == descricao


def test_descricao_com_quebra_de_linha_volta_em_um_unico_campo():
    descricao = "Primeira observação\nSegunda observação"
    itens = dominio.montar_ranking([problema("Uma dor", descricao=descricao)])

    linhas = linhas_do_csv(exportacao.gerar_csv(itens))

    assert len(linhas) == 2
    assert len(linhas[1]) == 8
    assert linhas[1][1] == descricao


def test_texto_acentuado_sobrevive_a_ida_e_volta():
    itens = dominio.montar_ranking(
        [problema("Padaria perde produção", descricao="Ação, coração e pão")]
    )

    linha = linhas_do_csv(exportacao.gerar_csv(itens))[1]

    assert linha[0] == "Padaria perde produção"
    assert linha[1] == "Ação, coração e pão"
