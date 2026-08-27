"""Testes das regras de domínio do Radar de Problemas."""

from datetime import datetime

import pytest

import dominio
from dominio import Problema

CARIMBO_PADRAO = "2026-08-26T09:00:00.000000"


def problema_com_notas(
    frequencia,
    intensidade,
    acesso,
    disposicao_pagar,
    registrado_em=CARIMBO_PADRAO,
    titulo="Título de teste",
):
    """Monta um Problema direto, sem passar pela criação nem pela validação.

    As notas são o que os testes olham; título e carimbo entram quando o teste
    precisa distinguir um problema do outro na ordenação.
    """
    return Problema(
        id="id-de-teste",
        titulo=titulo,
        descricao="",
        publico="",
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
        registrado_em=registrado_em,
    )


# --- calcular_score (FR-005) ---


def test_score_de_4_5_3_2_e_3_ponto_5():
    assert dominio.calcular_score(problema_com_notas(4, 5, 3, 2)) == 3.5


def test_score_maximo_e_5():
    assert dominio.calcular_score(problema_com_notas(5, 5, 5, 5)) == 5.0


def test_score_de_1_2_2_2_e_1_ponto_75():
    assert dominio.calcular_score(problema_com_notas(1, 2, 2, 2)) == 1.75


def test_score_minimo_e_1():
    assert dominio.calcular_score(problema_com_notas(1, 1, 1, 1)) == 1.0


def test_score_de_1_1_1_2_e_1_ponto_25():
    assert dominio.calcular_score(problema_com_notas(1, 1, 1, 2)) == 1.25


# --- formatar_score (FR-006, FR-007) ---


def test_formatar_score_usa_virgula_e_duas_casas():
    assert dominio.formatar_score(3.5) == "3,50"


def test_formatar_score_de_valor_inteiro_mantem_as_duas_casas():
    assert dominio.formatar_score(5.0) == "5,00"


def test_formatar_score_de_1_ponto_75():
    assert dominio.formatar_score(1.75) == "1,75"


def test_formatar_score_do_minimo():
    assert dominio.formatar_score(1.0) == "1,00"


# --- criar_problema (FR-001, FR-004) ---


def test_criar_problema_aplica_strip_no_titulo():
    problema = dominio.criar_problema(
        titulo="   Padaria perde produto vencido   ",
        descricao="",
        publico="",
        frequencia=4,
        intensidade=5,
        acesso=3,
        disposicao_pagar=2,
    )

    assert problema.titulo == "Padaria perde produto vencido"


def test_criar_problema_sem_descricao_e_sem_publico_guarda_texto_vazio():
    problema = dominio.criar_problema(
        titulo="Dor sem contexto",
        descricao=None,
        publico=None,
        frequencia=3,
        intensidade=3,
        acesso=3,
        disposicao_pagar=3,
    )

    assert problema.descricao == ""
    assert problema.publico == ""


def test_criar_problema_gera_id_diferente_a_cada_chamada():
    primeiro = dominio.criar_problema(
        titulo="Mesma dor",
        descricao="",
        publico="",
        frequencia=3,
        intensidade=3,
        acesso=3,
        disposicao_pagar=3,
    )
    segundo = dominio.criar_problema(
        titulo="Mesma dor",
        descricao="",
        publico="",
        frequencia=3,
        intensidade=3,
        acesso=3,
        disposicao_pagar=3,
    )

    assert primeiro.id != segundo.id


def test_criar_problema_registra_carimbo_em_iso_8601():
    problema = dominio.criar_problema(
        titulo="Dor recém-registrada",
        descricao="",
        publico="",
        frequencia=1,
        intensidade=1,
        acesso=1,
        disposicao_pagar=1,
    )

    # fromisoformat aceita exatamente o formato produzido por isoformat: se o carimbo
    # não for ISO 8601, esta linha levanta ValueError e o teste falha.
    assert datetime.fromisoformat(problema.registrado_em)


# --- montar_ranking: ordem por score (FR-008) ---


def test_montar_ranking_ordena_do_maior_para_o_menor_score():
    problemas = [
        problema_com_notas(3, 3, 3, 3, titulo="Terceiro"),
        problema_com_notas(5, 5, 5, 5, titulo="Primeiro"),
        problema_com_notas(1, 1, 1, 1, titulo="Quinto"),
        problema_com_notas(4, 4, 4, 4, titulo="Segundo"),
        problema_com_notas(2, 2, 2, 2, titulo="Quarto"),
    ]

    itens = dominio.montar_ranking(problemas)

    assert [item.problema.titulo for item in itens] == [
        "Primeiro",
        "Segundo",
        "Terceiro",
        "Quarto",
        "Quinto",
    ]


# --- montar_ranking: empate e reprodutibilidade (FR-009) ---


def test_montar_ranking_desempata_pelo_carimbo_mais_antigo():
    # O mais novo entra primeiro na lista de registro de propósito: se a ordenação
    # olhasse a posição na lista em vez do carimbo, o teste falharia.
    problemas = [
        problema_com_notas(
            4, 4, 4, 4, registrado_em="2026-08-26T10:00:00.000000", titulo="Mais novo"
        ),
        problema_com_notas(
            4, 4, 4, 4, registrado_em="2026-08-26T09:00:00.000000", titulo="Mais antigo"
        ),
    ]

    itens = dominio.montar_ranking(problemas)

    assert [item.problema.titulo for item in itens] == ["Mais antigo", "Mais novo"]


def test_montar_ranking_devolve_a_mesma_ordem_em_chamadas_seguidas():
    problemas = [
        problema_com_notas(4, 4, 4, 4, titulo="Empatado A"),
        problema_com_notas(5, 5, 5, 5, titulo="Sozinho no topo"),
        problema_com_notas(4, 4, 4, 4, titulo="Empatado B"),
    ]

    primeira = dominio.montar_ranking(problemas)
    segunda = dominio.montar_ranking(problemas)

    assert [item.problema.titulo for item in primeira] == [
        item.problema.titulo for item in segunda
    ]
    assert [item.problema.titulo for item in primeira] == [
        "Sozinho no topo",
        "Empatado A",
        "Empatado B",
    ]


# --- montar_ranking: posição, destaque e rótulo (FR-010, FR-010a, FR-010b) ---


def test_montar_ranking_de_lista_vazia_devolve_lista_vazia():
    assert dominio.montar_ranking([]) == []


def test_montar_ranking_com_um_problema_destaca_o_unico():
    itens = dominio.montar_ranking([problema_com_notas(3, 3, 3, 3)])

    assert [(item.posicao, item.destacado, item.rotulo_posicao) for item in itens] == [
        (1, True, "1º"),
    ]


def test_montar_ranking_com_dois_problemas_destaca_os_dois():
    problemas = [
        problema_com_notas(5, 5, 5, 5),
        problema_com_notas(4, 4, 4, 4),
    ]

    itens = dominio.montar_ranking(problemas)

    assert [(item.posicao, item.destacado, item.rotulo_posicao) for item in itens] == [
        (1, True, "1º"),
        (2, True, "2º"),
    ]


def test_montar_ranking_com_tres_problemas_destaca_os_tres():
    problemas = [
        problema_com_notas(5, 5, 5, 5),
        problema_com_notas(4, 4, 4, 4),
        problema_com_notas(3, 3, 3, 3),
    ]

    itens = dominio.montar_ranking(problemas)

    assert [(item.posicao, item.destacado, item.rotulo_posicao) for item in itens] == [
        (1, True, "1º"),
        (2, True, "2º"),
        (3, True, "3º"),
    ]


def test_montar_ranking_com_cinco_problemas_destaca_so_os_tres_primeiros():
    problemas = [
        problema_com_notas(5, 5, 5, 5),
        problema_com_notas(4, 4, 4, 4),
        problema_com_notas(3, 3, 3, 3),
        problema_com_notas(2, 2, 2, 2),
        problema_com_notas(1, 1, 1, 1),
    ]

    itens = dominio.montar_ranking(problemas)

    assert [item.posicao for item in itens] == [1, 2, 3, 4, 5]
    assert [item.rotulo_posicao for item in itens] == ["1º", "2º", "3º", "", ""]
    assert itens[3].destacado is False
    assert itens[4].destacado is False


# --- validar_problema: entrada base dos testes de validação ---

ENTRADA_VALIDA = {
    "titulo": "Padaria joga fora produto vencido",
    "descricao": "",
    "publico": "",
    "frequencia": 3,
    "intensidade": 3,
    "acesso": 3,
    "disposicao_pagar": 3,
}

# Rótulo em português de cada nota, como aparece nas mensagens de erro.
ROTULOS_DAS_NOTAS = [
    ("frequencia", "frequência"),
    ("intensidade", "intensidade"),
    ("acesso", "acesso ao público"),
    ("disposicao_pagar", "disposição a pagar"),
]


def validar(**alteracoes):
    """Valida uma entrada válida com apenas o campo em teste alterado."""
    return dominio.validar_problema(**{**ENTRADA_VALIDA, **alteracoes})


# --- validar_problema: título (FR-002, FR-014) ---


@pytest.mark.parametrize("titulo", ["", "   ", None])
def test_validar_problema_recusa_titulo_vazio(titulo):
    with pytest.raises(dominio.ErroDeValidacao) as erro:
        validar(titulo=titulo)

    assert erro.value.mensagens == ["O título é obrigatório."]


# --- validar_problema: notas (FR-003, FR-014) ---


@pytest.mark.parametrize("campo,rotulo", ROTULOS_DAS_NOTAS)
@pytest.mark.parametrize(
    "nota,modelo_da_mensagem",
    [
        (0, "A nota de {rotulo} deve estar entre 1 e 5."),
        (6, "A nota de {rotulo} deve estar entre 1 e 5."),
        (-1, "A nota de {rotulo} deve estar entre 1 e 5."),
        (3.5, "A nota de {rotulo} deve ser um número inteiro de 1 a 5."),
        ("quatro", "A nota de {rotulo} é obrigatória e deve ser um número inteiro de 1 a 5."),
        (None, "A nota de {rotulo} é obrigatória e deve ser um número inteiro de 1 a 5."),
        # True vale 1 em Python, mas booleano não é nota: é entrada errada.
        (True, "A nota de {rotulo} é obrigatória e deve ser um número inteiro de 1 a 5."),
    ],
)
def test_validar_problema_recusa_nota_invalida(campo, rotulo, nota, modelo_da_mensagem):
    with pytest.raises(dominio.ErroDeValidacao) as erro:
        validar(**{campo: nota})

    assert erro.value.mensagens == [modelo_da_mensagem.format(rotulo=rotulo)]


# --- validar_problema: o que a validação aceita (FR-004, FR-013b, FR-014) ---


def test_validar_problema_aceita_descricao_e_publico_vazios():
    assert validar(descricao="", publico="") is None


def test_validar_problema_aceita_ponto_e_virgula_aspas_e_quebra_de_linha():
    texto = 'Cliente disse: "perco 30%"; sem controle\nnenhum do estoque'

    assert validar(titulo=texto, descricao=texto, publico=texto) is None


def test_validar_problema_devolve_todas_as_mensagens_de_uma_vez():
    with pytest.raises(dominio.ErroDeValidacao) as erro:
        validar(titulo="", intensidade=6)

    assert erro.value.mensagens == [
        "O título é obrigatório.",
        "A nota de intensidade deve estar entre 1 e 5.",
    ]


# --- criar_problema recusa entrada inválida (FR-015) ---


def test_criar_problema_com_entrada_invalida_nao_devolve_problema():
    with pytest.raises(dominio.ErroDeValidacao) as erro:
        dominio.criar_problema(
            titulo="   ",
            descricao="",
            publico="",
            frequencia=3,
            intensidade=6,
            acesso=3,
            disposicao_pagar=3,
        )

    assert erro.value.mensagens == [
        "O título é obrigatório.",
        "A nota de intensidade deve estar entre 1 e 5.",
    ]
