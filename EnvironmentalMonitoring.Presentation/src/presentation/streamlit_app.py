"""Interface gráfica Streamlit para Monitoramento e Análise de Dados Ambientais.

Aplicação interativa para consultar, processar e analisar dados meteorológicos
e de qualidade da água por estação e período.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Adicionar diretório pai ao path para importar src
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st

from src.presentation.streamlit_support import (
    load_stations,
    validate_date_range,
    render_statistics_table,
    render_download_buttons,
    run_ingestion_pipeline,
    run_analytics_pipeline
)
from src.presentation.user_registration_app import show_user_registration_page
from src.presentation.user_data_viewer_app import show_user_data_viewer_page
from src.presentation.manual_ingestion_app import show_manual_ingestion_page
from src.presentation.public_home_page import show_public_home_page
from src.presentation.login_page import show_login_page
from src.config import logger
from src.security.log_utils import tratar_erro

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Monitoramento Ambiental",
    page_icon="🌤️",
    layout="wide",
)

# Ocultar status widget
st.markdown("""<style>[data-testid="stHeader"] {display: none; !important;} [data-testid="stMainBlockContainer"] {padding-top: 0; !important;}</style>""", unsafe_allow_html=True)

# Inicializar session state ANTES de usar
st.session_state.setdefault("weather_statistics", None)
st.session_state.setdefault("water_statistics", None)
st.session_state.setdefault("weather_csv_path", None)
st.session_state.setdefault("weather_outliers_path", None)
st.session_state.setdefault("water_csv_path", None)
st.session_state.setdefault("water_outliers_path", None)
st.session_state.setdefault("selected_station_name", None)
st.session_state.setdefault("selected_period", None)
st.session_state.setdefault("current_page", "public_home")
st.session_state.setdefault("decrypted_id", None)
st.session_state.setdefault("decrypted", None)
st.session_state.setdefault("usuario", None)
st.session_state.setdefault("ultimo_acesso", None)

# ============================================================================
# CONTROLE DE SESSÃO E AUTENTICAÇÃO
# ============================================================================

import time

TEMPO_INATIVIDADE_MIN = int(__import__('os').getenv("TEMPO_INATIVIDADE_MIN", 30))

def verificar_sessao():
    """Verifica se o usuário está logado e se a sessão não expirou."""
    if "usuario" in st.session_state and st.session_state.usuario:
        agora = time.time()
        if "ultimo_acesso" in st.session_state and st.session_state.ultimo_acesso:
            if agora - st.session_state.ultimo_acesso > TEMPO_INATIVIDADE_MIN * 60:
                _logout("inatividade")
                st.warning("Sessão expirada por inatividade. Faça login novamente.")
                st.rerun()
        st.session_state.ultimo_acesso = agora


verificar_sessao()

def _logout(motivo: str = "manual") -> None:
    """Realiza logout do usuário com registro em log.
    
    Args:
        motivo: Razão do logout (manual, inatividade, etc)
    """
    usuario = st.session_state.get("usuario")
    if usuario:
        logger.info("Logout", extra={"usuario_id": usuario.get("id_usuario", "N/A"), "motivo": motivo})
    st.session_state.clear()
    st.session_state.current_page = "public_home"

# ============================================================================
# HEADER
# ============================================================================

def render_header():
    """Renderiza o cabeçalho da página pública."""
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.markdown(
            "<div style='font-size: 24px; font-weight: bold; color: #ff5800; font-family: \"Trebuchet MS\", sans-serif; font-weight: 700;'>monitoramento ambiental</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div></div>", unsafe_allow_html=True)
    
    with col2:
        # Botão que redireciona para a página de login - só aparece se não estiver logado
        if not st.session_state.get("usuario") and not st.session_state.current_page == "login":
            if st.button("Login", use_container_width=True, key="login_button"):
                st.session_state.current_page = "login"
                st.rerun()

render_header()

# ============================================================================
# BARRA LATERAL - Apenas para usuários autenticados (pós-login)
# ============================================================================

if st.session_state.usuario and st.session_state.current_page not in ["login"]:
    
    with st.sidebar:
        usuario = st.session_state.usuario

        st.markdown(f"**{usuario.get('username', 'Usuário')}**  \n{usuario.get('atribution', '')}")
       
        # Home
        if st.button("Home", use_container_width=True, key="sidebar_home"):
            st.session_state.current_page = "public_home"
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Pipelines Ambientais**")
        
        # Pipelines Ambientais
        if st.button("Ingestão de Dados", use_container_width=True, key="sidebar_ingestion"):
            st.session_state.current_page = "ingestion"
            st.rerun()
        
        if st.button("Ingestão Manual", use_container_width=True, key="sidebar_manual_ingestion"):
            st.session_state.current_page = "manual_ingestion"
            st.rerun()
        
        if st.button("Analytics e Relatórios", use_container_width=True, key="sidebar_analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()
        
        if st.button("Dashboard", use_container_width=True, key="sidebar_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Gestão de Usuários**")
        
        # Gestão de Usuários
        if st.button("Cadastro de Usuários", use_container_width=True, key="sidebar_user_registration"):
            st.session_state.current_page = "user_registration"
            st.rerun()
        
        if st.button("Consulta de Usuários", use_container_width=True, key="sidebar_user_viewer"):
            st.session_state.current_page = "user_viewer"
            st.rerun()
        
        st.divider()
        if st.button("Sair", use_container_width=True, key="sidebar_logout"):
            _logout()
            st.rerun()

# Mostrar título apenas nas páginas autenticadas
if st.session_state.current_page not in ["public_home"] and st.session_state.current_page not in ["login"]:
    st.title("Monitoramento e Análise de Dados Ambientais")

# ============================================================================
# FUNÇÃO PÁGINA HOME
# ============================================================================

def page_public_home():
    """Página Home"""
    show_public_home_page()


# ============================================================================
# FUNÇÃO PÁGINA LOGIN
# ============================================================================

def page_login():
    """Página de login."""
    show_login_page()


# ============================================================================
# FUNÇÃO PÁGINA INGESTÃO
# ============================================================================

def page_ingestion():
    """Página de ingestão de dados."""
    st.markdown("### Pipeline de Ingestão e Persistência")
    
    st.markdown("Coleta e persistência de dados meteorológicos e de qualidade da água.")
    st.divider()
    
    # Carregar estações
    stations = load_stations()
    
    if not stations:
        st.warning("Nenhuma estação foi encontrada no banco de dados.")
        return
    
    # Criar dicionário de opções
    station_options = {
        f"{station.name}": station
        for station in stations
    }
    
    # Formulário
    with st.form("ingestion_form"):
        st.subheader("Parâmetros da Ingestão")
        
        # Seleção de estação
        selected_label = st.selectbox(
            "Estação",
            options=list(station_options.keys()),
            key="ingestion_station_select",
        )
        selected_station = station_options[selected_label]

        # Seleção de período de análise
        start_date_value = st.date_input(
            "Data inicial",
            value=date.today() - timedelta(days=2),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
            key="ingestion_start_date",
        )
        end_date_value = st.date_input(
            "Data final",
            value=date.today() - timedelta(days=1),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
            key="ingestion_end_date",
        )
        
        # Validar datas
        validation_error = validate_date_range(
            start_date_value,
            end_date_value,
        )
        
        if validation_error:
            st.error(validation_error)
        
        # Botão de submissão
        submitted = st.form_submit_button(
            "Executar Ingestão",
            type="primary",
            use_container_width=True,
        )
        
        # Executar pipeline se formulário foi enviado
        if submitted:
            if not validation_error:
                run_ingestion_pipeline(
                    selected_station,
                    start_date_value,
                    end_date_value,
                )


# ============================================================================
# FUNÇÃO PÁGINA INGESTÃO MANUAL
# ============================================================================

def page_manual_ingestion():
    """Página de ingestão manual de dados."""
    st.markdown("### Ingestão Manual via JSON")
    
    show_manual_ingestion_page()


# ============================================================================
# FUNÇÃO PÁGINA ANALYTICS
# ============================================================================

def page_analytics():
    """Página de analytics e relatórios."""
    st.markdown("### Pipeline de Analytics e Relatórios")
    
    st.markdown("Análise de dados e geração de relatórios.")
    st.divider()
    
    # Carregar estações
    stations = load_stations()
    
    if not stations:
        st.warning("Nenhuma estação foi encontrada no banco de dados.")
        return
    
    # Criar dicionário de opções
    station_options = {
        f"{station.name}": station
        for station in stations
    }
    
    # Formulário
    with st.form("analytics_form"):
        st.subheader("Parâmetros da Análise")
        
        # Seleção de estação
        selected_label = st.selectbox(
            "Estação",
            options=list(station_options.keys()),
            key="analytics_station_select",
        )
        selected_station = station_options[selected_label]

        # Seleção de período de análise
        start_date_value = st.date_input(
            "Data inicial",
            value=date.today() - timedelta(days=2),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
            key="analytics_start_date",
        )
        end_date_value = st.date_input(
            "Data final",
            value=date.today() - timedelta(days=1),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
            key="analytics_end_date",
        )
        
        # Validar datas
        validation_error = validate_date_range(
            start_date_value,
            end_date_value,
        )
        
        if validation_error:
            st.error(validation_error)
        
        # Botão de submissão
        submitted = st.form_submit_button(
            "Executar Analytics",
            type="primary",
            use_container_width=True,
        )
        
        # Executar pipeline se formulário foi enviado
        if submitted:
            if not validation_error:
                run_analytics_pipeline(
                    selected_station,
                    start_date_value,
                    end_date_value,
                )
    
    # Exibir resultados se disponível
    if st.session_state.weather_statistics or st.session_state.water_statistics:
        st.title("Resultados")
        st.divider()

        # Meteorologia        
        if st.session_state.weather_statistics:
            stats = st.session_state.weather_statistics
            total_obs = sum(
                result.count
                for result in stats
            )
            total_out = sum(
                len(result.outliers)
                for result in stats
            )
            # st.subheader("**Estatísticas Meteorológicas**")       
            st.divider()     
            st.metric(
                "Parâmetros",
                len(stats),
            )     
            st.metric(
                "Observações",
                total_obs,
            )
            st.metric(
                "Outliers",
                total_out,
            )        
            
            render_statistics_table(stats)
            
            st.write("**Downloads**")
            render_download_buttons(
                st.session_state.weather_csv_path,
                st.session_state.weather_outliers_path,
                "weather",
            )
        else:
            st.info("Nenhum resultado de meteorologia disponível.")

        st.divider()

        # #Qualidade da Água    
        # if st.session_state.water_statistics:
        #     stats = st.session_state.water_statistics
        #     total_obs = sum(
        #         result.count
        #         for result in stats
        #     )
        #     total_out = sum(
        #         len(result.outliers)
        #         for result in stats
        #     )
        #     st.subheader("**Estatísticas de Qualidade da Água**")
        #     st.divider()
        #     st.metric(
        #         "Parâmetros",
        #         len(stats),
        #     )            
        #     st.metric(
        #         "Observações",
        #         total_obs,
        #     )            
        #     st.metric(
        #         "Outliers",
        #         total_out,
        #     )    
            
        #     render_statistics_table(stats)
            
        #     st.write("**Downloads**")
        #     render_download_buttons(
        #         st.session_state.water_csv_path,
        #         st.session_state.water_outliers_path,
        #         "water",
        #     )
        # else:
        #     st.info("Nenhum resultado de qualidade da água disponível.")


# ============================================================================
# FUNÇÃO PÁGINA CADASTRO DE USUÁRIOS
# ============================================================================

def page_user_registration():
    """Página de cadastro de usuários."""
    st.markdown("### 👤 Cadastro de Usuários")
    
    st.caption("🔒 Nome, CPF, e-mail, telefone e senha são protegidos (LGPD) antes de serem gravados.")
    st.divider()
    
    # Chamar a função do arquivo user_registration_app.py
    show_user_registration_page()


# ============================================================================
# FUNÇÃO PÁGINA CONSULTA DE USUÁRIOS
# ============================================================================

def page_user_data_viewer():
    """Página de consulta de usuários com dados protegidos (LGPD)."""
    st.markdown("### Consulta de Usuários (LGPD)")
    
    st.caption("Dados exibidos como estão gravados no banco. "
               "Somente nome, e-mail e telefone podem ser descriptografados; CPF e Senha são hash.")
    st.divider()
    
    # Chamar a função do arquivo user_data_viewer_app.py
    show_user_data_viewer_page()

# ============================================================================
# FUNÇÃO PÁGINA DASHBOARD
# ============================================================================

def page_dashboard():
    """Página de redirecionamento para Dashboard Power BI."""
    st.markdown("### Dashboard - Análise de Dados")
    
    st.markdown("Você será redirecionado para o dashboard interativo no Power BI.")
    st.divider()
    
    # Botão para abrir o Power BI
    st.link_button(
        "Abrir Dashboard Power BI",
        "https://app.powerbi.com/links/U62QaGqjCt?ctid=cf36141c-ddd7-45a7-b073-111f66d0b30c&pbi_source=linkShare",
        use_container_width=True,
    )


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que renderiza a interface."""
    
    if st.session_state.current_page == "public_home":
        page_public_home()
    elif st.session_state.current_page == "login":
        page_login()
    elif st.session_state.current_page == "ingestion":
        page_ingestion()
    elif st.session_state.current_page == "manual_ingestion":
        page_manual_ingestion()
    elif st.session_state.current_page == "analytics":
        page_analytics()
    elif st.session_state.current_page == "dashboard":
        page_dashboard()
    elif st.session_state.current_page == "user_registration":
        page_user_registration()
    elif st.session_state.current_page == "user_viewer":
        page_user_data_viewer()



if __name__ == "__main__":
    main()
