"""Tela inicial (após o login) com os botões de navegação."""
import streamlit as st

usuario = st.session_state["usuario"]
paginas = st.session_state["paginas"]

st.title(f"Olá, {usuario['username']} 👋")
st.caption("Selecione a funcionalidade desejada.")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("👤 Cadastro de Usuários")
        st.write("Cadastrar novos usuários. Os dados pessoais são protegidos (LGPD) antes da gravação.")
        if st.button("Abrir cadastro", type="primary", use_container_width=True):
            st.switch_page(paginas["cadastro"])
with col2:
    with st.container(border=True):
        st.subheader("🔐 Consulta de Usuários")
        st.write("Visualizar os dados como estão gravados no banco e descriptografar os campos permitidos.")
        if st.button("Abrir consulta", type="primary", use_container_width=True):
            st.switch_page(paginas["consulta"])
