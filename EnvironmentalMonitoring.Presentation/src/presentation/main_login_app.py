"""Ponto de entrada da aplicação Streamlit (login + menu + telas protegidas).

Executar com:
    streamlit run src/presentation/main_login_app.py

- Sem login: somente a tela de Login fica disponível (as outras nem são registradas,
  então nem pela URL é possível acessá-las).
- Com login: Início (menu com botões), Cadastro de Usuários e Consulta de Usuários.
- Sessão expira após TEMPO_INATIVIDADE_MIN minutos sem interação.
"""
import sys
import time
import os       # para acessar variáveis de ambiente
from pathlib import Path
# Adicionar a raiz do projeto ao path para importar src
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
import streamlit as st
from src.config import logger

TEMPO_INATIVIDADE_MIN = int(os.getenv("TEMPO_INATIVIDADE_MIN", 30)) # tempo de inatividade em minutos antes de expirar a sessão, como padrão utiliza 30 minutos
PASTA = Path(__file__).parent

# Configuração única da janela (as telas internas também podem chamar set_page_config)
st.set_page_config(page_title="Academia Data Science", page_icon="🔐", layout="wide")


def _logout(motivo: str = "manual") -> None:
    usuario = st.session_state.get("usuario")
    if usuario:
        logger.info("Logout", extra={"usuario_id": usuario["id_usuario"], "motivo": motivo})
    st.session_state.clear()


# Expira a sessão por inatividade
agora = time.time()
if "usuario" in st.session_state:
    if agora - st.session_state.get("ultimo_acesso", agora) > TEMPO_INATIVIDADE_MIN * 60:
        _logout("inatividade")
        st.session_state["aviso_login"] = "Sessão expirada por inatividade. Faça login novamente."
    else:
        st.session_state["ultimo_acesso"] = agora

# Páginas
login = st.Page(PASTA / "login_page.py", title="Login", icon="🔑")
inicio = st.Page(PASTA / "home_page.py", title="Início", icon="🏠", default=True)
cadastro = st.Page(PASTA / "user_registration_app.py", title="Cadastro de Usuários",
                   icon="👤", url_path="cadastro")
consulta = st.Page(PASTA / "user_data_viewer_app.py", title="Consulta de Usuários",
                   icon="🔐", url_path="consulta")

if "usuario" not in st.session_state:
    # Sem login: só existe a página de login
    pagina = st.navigation([login], position="hidden")
else:
    # Guarda as páginas na sessão para os botões da tela Início (st.switch_page)
    st.session_state["paginas"] = {"cadastro": cadastro, "consulta": consulta, "inicio": inicio}
    usuario = st.session_state["usuario"]
    with st.sidebar:
        st.markdown(f"**👤 {usuario['username']}**  \n{usuario['atribution']}")
        if st.button("Sair", icon="🚪", use_container_width=True):
            _logout()
            st.rerun()
    pagina = st.navigation({"Menu": [inicio, cadastro, consulta]})

pagina.run()
