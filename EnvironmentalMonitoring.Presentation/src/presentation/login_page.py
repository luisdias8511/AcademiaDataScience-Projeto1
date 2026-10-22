"""Tela de login (usuário e senha da tabela Users)."""
import time
import streamlit as st
import os
from src.config import logger
from src.security.log_utils import tratar_erro
from src.services.auth_service import authenticate

MAX_TENTATIVAS = int(os.getenv("MAX_TENTATIVAS", 5))            # tentativas erradas antes do bloqueio, como padrão utiliza 5 tentativas
BLOQUEIO_SEGUNDOS = int(os.getenv("BLOQUEIO_SEGUNDOS", 300))    # tempo de bloqueio em segundos, como padrão utiliza 300 segundos (5 minutos)

try:
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        st.title("🔑 Login")
        st.caption("Acesse com o usuário e a senha cadastrados.")

        if aviso := st.session_state.pop("aviso_login", None):
            st.warning(aviso)

        bloqueado_ate = st.session_state.get("bloqueado_ate", 0)
        restante = int(bloqueado_ate - time.time())

        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if entrar:
            if restante > 0:
                st.error(f"Muitas tentativas inválidas. Aguarde {restante // 60 + 1} minuto(s).")
            elif not username or not password:
                st.error("Informe usuário e senha.")
            else:
                usuario = authenticate(username, password)
                if usuario:
                    st.session_state.pop("tentativas", None)
                    st.session_state.pop("bloqueado_ate", None)
                    st.session_state["usuario"] = usuario
                    st.session_state["ultimo_acesso"] = time.time()
                    st.rerun()  # main_app passa a exibir o menu
                else:
                    tentativas = st.session_state.get("tentativas", 0) + 1
                    st.session_state["tentativas"] = tentativas
                    if tentativas >= MAX_TENTATIVAS:
                        st.session_state["bloqueado_ate"] = time.time() + BLOQUEIO_SEGUNDOS
                        st.session_state["tentativas"] = 0
                        logger.warning("Login bloqueado temporariamente por excesso de tentativas",
                                       extra={"username": username.strip()})
                        restante = int(st.session_state["bloqueado_ate"] - time.time())
                        st.error(f"Muitas tentativas inválidas. Aguarde {restante // 60 + 1} minuto(s).")
                    else:
                        st.error("Usuário ou senha inválidos.")
except Exception as erro:
    st.error("Não foi possível realizar o login. Consulte o log da aplicação.")
    tratar_erro(erro, "Erro durante o login", encerrar=False)
