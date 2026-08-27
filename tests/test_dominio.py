"""Testes das regras de domínio do Radar de Problemas."""

from datetime import datetime

import dominio
from dominio import Problema

CARIMBO_PADRAO = "2026-08-26T09:00:00.000000"


def problema_com_notas(
    frequencia,
    intensidade,
    acesso,
    disposicao_pagar,
    registrado_em=CARIMBO_PADRAO,
):
    """Monta um Problema direto, sem passar pela criação nem pela validação.

    Os testes de score olham só para as notas, então o resto dos campos é fixo.
    """
    return Problema(
        id="id-de-teste",
        titulo="Título de teste",
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
