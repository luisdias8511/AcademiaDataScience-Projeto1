"""Tela Streamlit de cadastro de usuários."""

import sys
from pathlib import Path

# Adicionar a raiz do projeto ao path para importar src
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from src.models.user import NewUser
from src.services.user_service import register_user

st.set_page_config(page_title="Cadastro de Usuários", page_icon="👤")
st.title("Cadastro de Usuários")

with st.form("user_form"):
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    email = st.text_input("E-mail")
    cpf = st.text_input("CPF")
    phone = st.text_input("Telefone (opcional)")
    atribution = st.text_input("Atribuição")
    submitted = st.form_submit_button("Cadastrar")

if submitted:
    user = NewUser(
        username=username,
        password=password,
        email=email,
        cpf=cpf,
        phone=phone or None,
        atribution=atribution,
    )
    errors = register_user(user)

    if errors:
        for error in errors:
            st.error(error)
    else:
        st.success("Usuário cadastrado.")
