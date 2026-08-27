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


@dataclass(frozen=True)
class ItemRanking:
    """Um problema já colocado na ordenação, pronto para a tela e para a exportação.

    Tudo o que a interface precisa mostrar chega resolvido daqui: o score já
    formatado, a posição, se a linha entra no destaque e o rótulo dessa posição
    (FR-010b). Nunca é gravado — é derivado da lista de problemas a cada exibição.
    """

    problema: Problema
    score: float
    score_formatado: str
    posicao: int
    destacado: bool
    rotulo_posicao: str


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


# Rótulo em português de cada nota, usado nas mensagens de erro (FR-014).
ROTULOS_DAS_NOTAS = {
    "frequencia": "frequência",
    "intensidade": "intensidade",
    "acesso": "acesso ao público",
    "disposicao_pagar": "disposição a pagar",
}


def _erro_da_nota(rotulo: str, valor: object) -> str | None:
    """Devolve a mensagem para uma nota inválida, ou None se ela estiver correta.

    A ordem das verificações vai do problema mais grave para o mais específico:
    primeiro o que nem é número, depois o que é número mas não é inteiro, e só
    então a faixa. `bool` é recusado de propósito: em Python `True == 1`, mas
    booleano não é nota, é entrada errada.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return f"A nota de {rotulo} é obrigatória e deve ser um número inteiro de 1 a 5."
    if not isinstance(valor, int):
        return f"A nota de {rotulo} deve ser um número inteiro de 1 a 5."
    if not 1 <= valor <= 5:
        return f"A nota de {rotulo} deve estar entre 1 e 5."
    return None


def validar_problema(
    titulo: str | None,
    descricao: str | None,
    publico: str | None,
    frequencia: object,
    intensidade: object,
    acesso: object,
    disposicao_pagar: object,
) -> None:
    """Verifica a entrada crua vinda da tela (FR-002, FR-003, FR-014).

    Coleta **todas** as mensagens aplicáveis antes de levantar `ErroDeValidacao`,
    para o usuário corrigir tudo de uma vez em vez de descobrir um erro por vez.
    Descrição e público são opcionais e aceitam qualquer texto, inclusive com
    ponto e vírgula, aspas e quebra de linha (FR-004, FR-013b). Não cria nem grava
    nada.
    """
    mensagens = []

    if not isinstance(titulo, str) or not titulo.strip():
        mensagens.append("O título é obrigatório.")

    notas = {
        "frequencia": frequencia,
        "intensidade": intensidade,
        "acesso": acesso,
        "disposicao_pagar": disposicao_pagar,
    }
    for campo, valor in notas.items():
        erro = _erro_da_nota(ROTULOS_DAS_NOTAS[campo], valor)
        if erro is not None:
            mensagens.append(erro)

    if mensagens:
        raise ErroDeValidacao(mensagens)


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

    A validação vem antes de qualquer outra coisa: entrada recusada não produz
    Problema nenhum, nem parcial (FR-015).
    """
    validar_problema(
        titulo=titulo,
        descricao=descricao,
        publico=publico,
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
    )

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


def montar_ranking(problemas: list[Problema]) -> list[ItemRanking]:
    """Ordena os problemas do maior para o menor score (FR-008, FR-009).

    Recebe a lista na ordem de registro. O empate é resolvido pelo carimbo mais
    antigo; como `sorted` é estável, dois carimbos iguais mantêm a ordem do arquivo,
    e a mesma lista devolve sempre o mesmo resultado. Lista vazia devolve lista
    vazia, sem erro.

    A posição é sequencial a partir de 1 e não se repete em empate. As três
    primeiras ficam destacadas e recebem o rótulo `1º`, `2º` ou `3º`; com menos de
    três problemas, todos os existentes ficam destacados (FR-010, FR-010a). O
    destaque e o rótulo saem prontos daqui para a tela não decidir nada (FR-010b).
    """
    ordenados = sorted(
        problemas, key=lambda problema: (-calcular_score(problema), problema.registrado_em)
    )

    itens = []
    for posicao, problema in enumerate(ordenados, start=1):
        score = calcular_score(problema)
        destacado = posicao <= 3
        itens.append(
            ItemRanking(
                problema=problema,
                score=score,
                score_formatado=formatar_score(score),
                posicao=posicao,
                destacado=destacado,
                rotulo_posicao=f"{posicao}º" if destacado else "",
            )
        )
    return itens
