"""Testes da leitura e da gravação do arquivo de problemas."""

import json
import os

import pytest

import armazenamento
from armazenamento import ErroDeArmazenamento
from dominio import Problema

REGISTRO_VALIDO = {
    "id": "0f1e2d3c-4b5a-6789-abcd-ef0123456789",
    "titulo": "Padaria joga fora produto vencido",
    "descricao": "Perde produto toda semana; não sabe o quanto.",
    "publico": "Donos de padaria de bairro",
    "frequencia": 5,
    "intensidade": 4,
    "acesso": 3,
    "disposicao_pagar": 2,
    "registrado_em": "2026-08-26T09:14:02.481930",
}


def problema(titulo, registrado_em, notas=(5, 4, 3, 2)):
    """Monta um Problema com o mínimo que os testes de arquivo precisam distinguir."""
    frequencia, intensidade, acesso, disposicao_pagar = notas
    return Problema(
        id=f"id-{titulo}",
        titulo=titulo,
        descricao="Descrição com acentuação: pão, ação e coração.",
        publico="Público afetado",
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
        registrado_em=registrado_em,
    )


def mensagem_sem_detalhe_interno(mensagem, caminho):
    """A mensagem ao usuário não pode vazar caminho, nome de arquivo nem de exceção."""
    proibidos = [
        str(caminho),
        caminho.name,
        "JSONDecodeError",
        "ErroDeArmazenamento",
        "Traceback",
    ]
    return all(proibido not in mensagem for proibido in proibidos)


# --- ler_problemas: arquivo ausente (FR-016) ---


def test_ler_problemas_sem_arquivo_devolve_lista_vazia(tmp_path):
    caminho = tmp_path / "problemas.json"

    assert armazenamento.ler_problemas(caminho) == []


# --- ler_problemas: arquivo ilegível (FR-017) ---


@pytest.mark.parametrize(
    "conteudo",
    [
        pytest.param("", id="arquivo vazio"),
        pytest.param("   \n  ", id="so espacos"),
        pytest.param("[{isto não é json}]", id="json invalido"),
        pytest.param("{}", id="raiz nao e lista"),
        pytest.param('["texto"]', id="item nao e objeto"),
        pytest.param('[{"titulo": "Sem os outros campos"}]', id="campo obrigatorio ausente"),
        pytest.param(
            json.dumps([{**REGISTRO_VALIDO, "frequencia": "4"}], ensure_ascii=False),
            id="nota como texto",
        ),
    ],
)
def test_ler_problemas_com_arquivo_ilegivel_levanta_erro(tmp_path, conteudo):
    caminho = tmp_path / "problemas.json"
    caminho.write_text(conteudo, encoding="utf-8")

    with pytest.raises(ErroDeArmazenamento) as erro:
        armazenamento.ler_problemas(caminho)

    assert mensagem_sem_detalhe_interno(str(erro.value), caminho)


# --- gravar_problemas + ler_problemas: ida e volta (FR-011, FR-005) ---


def test_gravar_e_reler_devolve_os_mesmos_problemas_na_mesma_ordem(tmp_path):
    caminho = tmp_path / "problemas.json"
    problemas = [
        problema("Primeiro registrado", "2026-08-26T09:00:00.000000"),
        problema("Segundo registrado", "2026-08-26T10:00:00.000000", notas=(1, 1, 1, 1)),
        problema("Terceiro registrado", "2026-08-26T11:00:00.000000", notas=(5, 5, 5, 5)),
    ]

    armazenamento.gravar_problemas(problemas, caminho)
    relidos = armazenamento.ler_problemas(caminho)

    assert relidos == problemas
    assert all(isinstance(relido.frequencia, int) for relido in relidos)
    assert all(isinstance(relido.disposicao_pagar, int) for relido in relidos)


def test_arquivo_gravado_mantem_acentos_legiveis_e_nao_guarda_score(tmp_path):
    caminho = tmp_path / "problemas.json"

    armazenamento.gravar_problemas([problema("Ação", "2026-08-26T09:00:00.000000")], caminho)

    texto = caminho.read_text(encoding="utf-8")
    assert "coração" in texto
    # Sem escapes \uXXXX no arquivo: o acento tem de ir legivel.
    assert chr(92) + "u" not in texto
    assert "score" not in json.loads(texto)[0]


# --- gravar_problemas: falha de gravação (FR-017a) ---


def test_falha_de_gravacao_preserva_o_arquivo_anterior_e_nao_deixa_temporario(
    tmp_path, monkeypatch
):
    caminho = tmp_path / "problemas.json"
    armazenamento.gravar_problemas([problema("Já salvo", "2026-08-26T09:00:00.000000")], caminho)
    bytes_antes = caminho.read_bytes()

    def replace_que_falha(origem, destino):
        raise OSError("disco cheio")

    monkeypatch.setattr(os, "replace", replace_que_falha)

    with pytest.raises(ErroDeArmazenamento) as erro:
        armazenamento.gravar_problemas(
            [problema("Nunca chega ao disco", "2026-08-26T12:00:00.000000")], caminho
        )

    assert mensagem_sem_detalhe_interno(str(erro.value), caminho)
    assert caminho.read_bytes() == bytes_antes
    assert list(tmp_path.iterdir()) == [caminho]
