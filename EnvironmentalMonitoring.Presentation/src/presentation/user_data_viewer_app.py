"""Tela Streamlit de consulta de usuários com dados protegidos (LGPD).

Mostra os dados EXATAMENTE como gravados no banco (hash / criptografados) e permite,
com um botão, descriptografar os campos reversíveis usando src/security/lgpd.py.
"""
import sys
from pathlib import Path
# Adicionar a raiz do projeto ao path para importar src
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
import pandas as pd
import streamlit as st
from src.services.user_service import decrypt_user, list_protected_users
from src.config import logger                   # logger estruturado (JSON) do projeto
from src.security.log_utils import tratar_erro  # função padronizada para registrar erros

IRREVERSIVEL = "🔒 Hash SHA-256 (irreversível)"


def show_user_data_viewer_page():
    """Renderiza a página de consulta de usuários com dados protegidos (LGPD)."""
    try:
        logger.info("Iniciando Consulta de Usuários (LGPD)")

        users = list_protected_users()
        if not users:
            st.info("Nenhum usuário cadastrado.")
        else:
            # 1) Visão geral: tudo como está no banco (hash / criptografado)
            st.subheader("Dados gravados no banco")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Id": u["id_usuario"],
                            "Usuário": u["username"],
                            "Senha (hash)": u["password_hash"],
                            "CPF (hash)": u["cpf_hash"],
                            "Nome Completo (cripto)": u["nome_completo_cripto"],
                            "E-mail (cripto)": u["email_cripto"],
                            "Telefone (cripto)": u["telefone_cripto"],
                            "Atribuição": u["atribution"],
                        }
                        for u in users
                    ]
                ),
                hide_index=True,
            )

            # 2) Seleção do usuário
            st.subheader("Descriptografar usuário")
            opcoes = {f"#{u['id_usuario']} - {u['username']}": u for u in users}
            escolha = st.selectbox("Selecione o usuário", list(opcoes))
            registro = opcoes[escolha]

            # Se trocar o usuário selecionado, esconde o que estava descriptografado
            if st.session_state.get("decrypted_id") != registro["id_usuario"]:
                st.session_state.pop("decrypted", None)

            col1, col2, _ = st.columns([1, 1, 4])
            if col1.button("🔓 Descriptografar", type="primary"):
                try:
                    st.session_state["decrypted"] = decrypt_user(registro)
                    st.session_state["decrypted_id"] = registro["id_usuario"]
                except ValueError as erro:
                    st.error(str(erro))
            if col2.button("🔒 Ocultar"):
                st.session_state.pop("decrypted", None)
                st.session_state.pop("decrypted_id", None)

            # 3) Comparativo: valor gravado x valor descriptografado
            aberto = st.session_state.get("decrypted")
            oculto = "••••••••"

            def _valor(campo: str) -> str:
                if aberto is None:
                    return oculto
                return aberto.get(campo) or "—"

            st.table(
                pd.DataFrame(
                    [
                        {"Campo": "Usuário", "Valor gravado": registro["username"],
                         "Valor descriptografado": registro["username"]},
                        {"Campo": "Senha (hash)", "Valor gravado": registro["password_hash"],
                        "Valor descriptografado": "PBKDF2-SHA256"},
                        {"Campo": "CPF", "Valor gravado": registro["cpf_hash"],
                         "Valor descriptografado": "IRREVERSIVEL"},
                        {"Campo": "Nome Completo", "Valor gravado": registro["nome_completo_cripto"] or "—",
                         "Valor descriptografado": _valor("full_name")},
                        {"Campo": "E-mail", "Valor gravado": registro["email_cripto"],
                         "Valor descriptografado": _valor("email")},
                        {"Campo": "Telefone", "Valor gravado": registro["telefone_cripto"] or "—",
                         "Valor descriptografado": _valor("phone")},
                        {"Campo": "Atribuição", "Valor gravado": registro["atribution"],
                         "Valor descriptografado": registro["atribution"]},
                    ]
                ).set_index("Campo")
            )

        logger.info("Fim da Consulta de Usuários (LGPD)")

    except Exception as erro:
        st.error("Não foi possível carregar os usuários. Consulte o log da aplicação.")
        tratar_erro(erro, "Erro durante a consulta de usuários (LGPD)", encerrar=False)


# ============================================================================
# EXECUÇÃO STANDALONE (quando aberto diretamente)
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Consulta de Usuários (LGPD)", page_icon="🔐", layout="wide")
    st.title("Consulta de Usuários (LGPD)")
    st.caption("Dados exibidos como estão gravados no banco. "
               "Somente nome, e-mail e telefone podem ser descriptografados; CPF e Senha são hash.")
    st.divider()
    show_user_data_viewer_page()
