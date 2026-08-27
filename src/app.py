"""Interface Streamlit do Radar de Problemas.

Único módulo que importa Streamlit. Não calcula nada: coleta a entrada do usuário,
chama o domínio e exibe o que ele devolve.
"""

import streamlit as st

import armazenamento
import dominio
import exportacao

st.set_page_config(page_title="Radar de Problemas")
st.title("Radar de Problemas")

# O arquivo é lido uma única vez por sessão: o Streamlit reexecuta o script inteiro
# a cada interação, e reler a cada clique faria a mensagem de erro piscar.
if "problemas" not in st.session_state:
    try:
        st.session_state["problemas"] = armazenamento.ler_problemas()
        st.session_state["erro_leitura"] = None
    except armazenamento.ErroDeArmazenamento as erro:
        # Arquivo ilegível não trava o aplicativo: a sessão segue utilizável para
        # novos registros, com a lista vazia em memória.
        st.session_state["problemas"] = []
        st.session_state["erro_leitura"] = str(erro)

if st.session_state["erro_leitura"]:
    st.error(st.session_state["erro_leitura"])

with st.form("registro", clear_on_submit=True):
    titulo = st.text_input("Título")
    descricao = st.text_area("Descrição")
    publico = st.text_input("Público afetado")

    # As notas vão sem min_value/max_value de propósito: a faixa de 1 a 5 é decidida
    # pelo domínio, que é onde ela está coberta por teste.
    frequencia = st.number_input("Frequência", value=3, step=1)
    intensidade = st.number_input("Intensidade", value=3, step=1)
    acesso = st.number_input("Acesso ao público", value=3, step=1)
    disposicao_pagar = st.number_input("Disposição a pagar", value=3, step=1)

    registrar = st.form_submit_button("Registrar")

if registrar:
    try:
        novo = dominio.criar_problema(
            titulo=titulo,
            descricao=descricao,
            publico=publico,
            frequencia=frequencia,
            intensidade=intensidade,
            acesso=acesso,
            disposicao_pagar=disposicao_pagar,
        )
        # Gravar antes de trocar o estado é o que garante que uma falha de escrita
        # deixe o arquivo e a lista em memória exatamente como estavam.
        nova_lista = st.session_state["problemas"] + [novo]
        armazenamento.gravar_problemas(nova_lista)
    except dominio.ErroDeValidacao as erro:
        for mensagem in erro.mensagens:
            st.error(mensagem)
    except armazenamento.ErroDeArmazenamento as erro:
        st.error(str(erro))
    else:
        st.session_state["problemas"] = nova_lista

st.subheader("Problemas registrados")

itens = dominio.montar_ranking(st.session_state["problemas"])

if not itens:
    st.info("Nenhum problema registrado ainda. Use o formulário acima para começar.")

for item in itens:
    problema = item.problema

    # A moldura diferencia as três primeiras posições e o rótulo garante a
    # conferência sem depender de cor. Quem decide as duas coisas é o domínio.
    with st.container(border=item.destacado):
        marca = f"{item.rotulo_posicao} " if item.rotulo_posicao else ""
        st.markdown(f"**{marca}{problema.titulo}** — score {item.score_formatado}")
        st.caption(
            f"Público: {problema.publico or '—'} · "
            f"Frequência {problema.frequencia} · "
            f"Intensidade {problema.intensidade} · "
            f"Acesso {problema.acesso} · "
            f"Disposição a pagar {problema.disposicao_pagar}"
        )

# O arquivo é montado em memória e cai direto na pasta de downloads: uma única ação
# do usuário, sem informar caminho e sem arquivo intermediário no projeto.
st.download_button(
    "Baixar a lista em CSV",
    data=exportacao.gerar_csv(itens),
    file_name="radar-de-problemas.csv",
    mime="text/csv",
)
