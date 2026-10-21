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
from src.config import logger                   # logger estruturado (JSON) do projeto
from src.security.log_utils import tratar_erro  # função padronizada para registrar erros


def show_user_registration_page():
    """Renderiza a página de cadastro de usuários."""
    try:
        logger.info("Iniciando Cadastro de Usuários")
        
        with st.form("user_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            cpf = st.text_input("CPF")
            full_name = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
            phone = st.text_input("Telefone (opcional)")
            atribution = st.text_input("Atribuição")
            submitted = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)
        
        if submitted:
            user = NewUser(
                username=username,
                password=password,
                cpf=cpf,
                full_name=full_name,
                email=email,
                phone=phone or None,
                atribution=atribution,
            )
            errors = register_user(user)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("Usuário cadastrado com dados protegidos (LGPD).")
        
        logger.info("Fim do Cadastro de Usuários")
    
    except Exception as erro:
        st.error("Não foi possível concluir o cadastro. Consulte o log da aplicação.")
        tratar_erro(erro, "Erro durante o cadastro de usuário", encerrar=False)


# ============================================================================
# EXECUÇÃO STANDALONE (quando aberto diretamente)
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Cadastro de Usuários", page_icon="👤")
    st.title("Cadastro de Usuários")
    st.caption("🔒 Nome, CPF, e-mail, telefone e senha são protegidos (LGPD) antes de serem gravados.")
    st.divider()
    show_user_registration_page()
