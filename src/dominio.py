"""Regras de negócio do Radar de Problemas.

Módulo puro: não importa Streamlit, não lê estado de tela, não toca em disco e não
acessa rede. Recebe dados simples como argumento e devolve o resultado ao chamador.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Problema:
    """Uma dor observada em campo, com as quatro notas que a avaliam.

    As notas são inteiros de 1 a 5. `registrado_em` é um carimbo ISO 8601 usado para
    desempatar problemas de mesmo score. O score não é guardado aqui: é sempre
    recalculado a partir das notas.
    """

    id: str
    titulo: str
    descricao: str
    publico: str
    frequencia: int
    intensidade: int
    acesso: int
    disposicao_pagar: int
    registrado_em: str


class ErroDeValidacao(Exception):
    """Entrada recusada pela validação.

    `mensagens` traz um texto em português por problema encontrado — a validação
    coleta todos os erros de uma vez, em vez de parar no primeiro.
    """

    def __init__(self, mensagens: list[str]) -> None:
        super().__init__(" ".join(mensagens))
        self.mensagens = mensagens


def calcular_score(problema: Problema) -> float:
    """Média simples das quatro notas, todas com o mesmo peso (FR-005).

    O resultado é sempre múltiplo exato de 0,25, entre 1,0 e 5,0.
    """
    notas = (
        problema.frequencia,
        problema.intensidade,
        problema.acesso,
        problema.disposicao_pagar,
    )
    return sum(notas) / len(notas)


def formatar_score(score: float) -> str:
    """Score pronto para exibir: duas casas decimais e vírgula (FR-006, FR-007).

    A mesma string vai para a tela e para o arquivo exportado (FR-013a).
    """
    return f"{score:.2f}".replace(".", ",")


def criar_problema(
    titulo: str,
    descricao: str | None,
    publico: str | None,
    frequencia: int,
    intensidade: int,
    acesso: int,
    disposicao_pagar: int,
) -> Problema:
    """Monta um Problema novo a partir da entrada da tela (FR-001, FR-004).

    Gera o identificador e o carimbo de registro. Descrição e público são opcionais:
    quando não vêm preenchidos, viram texto vazio. Não persiste nada — quem grava é
    o módulo de armazenamento.
    """
    return Problema(
        id=str(uuid.uuid4()),
        titulo=titulo.strip(),
        descricao=descricao or "",
        publico=publico or "",
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
        registrado_em=datetime.now().isoformat(timespec="microseconds"),
    )
