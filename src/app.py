"""Interface Streamlit do Radar de Problemas.

Único módulo que importa Streamlit. Não calcula nada: coleta a entrada do usuário,
chama o domínio e exibe o que ele devolve.
"""

import streamlit as st

import dominio

st.set_page_config(page_title="Radar de Problemas")
st.title("Radar de Problemas")

if "problemas" not in st.session_state:
    st.session_state["problemas"] = []

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
    novo = dominio.criar_problema(
        titulo=titulo,
        descricao=descricao,
        publico=publico,
        frequencia=frequencia,
        intensidade=intensidade,
        acesso=acesso,
        disposicao_pagar=disposicao_pagar,
    )
    st.session_state["problemas"] = st.session_state["problemas"] + [novo]

st.subheader("Problemas registrados")

for problema in st.session_state["problemas"]:
    score_formatado = dominio.formatar_score(dominio.calcular_score(problema))
    st.markdown(f"**{problema.titulo}** — score {score_formatado}")
    st.caption(
        f"Público: {problema.publico or '—'} · "
        f"Frequência {problema.frequencia} · "
        f"Intensidade {problema.intensidade} · "
        f"Acesso {problema.acesso} · "
        f"Disposição a pagar {problema.disposicao_pagar}"
    )
