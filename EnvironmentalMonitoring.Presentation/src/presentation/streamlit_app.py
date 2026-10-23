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

import pandas as pd
import streamlit as st

from src.presentation.streamlit_support import (
    load_stations,
    validate_date_range,
    render_statistics_table,
    render_download_buttons,
    run_ingestion_pipeline,
    run_analytics_pipeline,
    run_pipeline,
)
from src.presentation.user_registration_app import show_user_registration_page
from src.presentation.user_data_viewer_app import show_user_data_viewer_page
from src.presentation.manual_ingestion_app import show_manual_ingestion_page
from src.presentation.public_home_page import show_public_home_page
from src.config import logger
from src.security.log_utils import tratar_erro
from streamlit_avatar import avatar

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Monitoramento Ambiental",
    page_icon="🌤️",
    layout="wide",
)

# Ocultar status widget
st.markdown("""
    <style>
        [data-testid="stStatusWidget"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

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

# Mostrar título apenas nas páginas autenticadas
if st.session_state.current_page != "public_home":
    st.title("Monitoramento e Análise de Dados Ambientais")

# ============================================================================
# FUNÇÃO PÁGINA HOME PÚBLICA
# ============================================================================

def page_public_home():
    """Página Home pública (não autenticada)."""
    show_public_home_page()


# ============================================================================
# FUNÇÃO PÁGINA INICIAL (AUTENTICADA)
# ============================================================================

def page_home():
    """Página inicial com links para os pipelines."""
    st.markdown("### Plataforma de Monitoramento Ambiental e Gestão de Usuários")
    st.markdown("Escolha uma opção para começar:")
    st.divider()
    
    # Linha 1: Pipelines Ambientais
    st.markdown("**📊 Pipelines de Dados Ambientais**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Ingestão de Dados", use_container_width=True, key="btn_ingestion"):
            st.session_state.current_page = "ingestion"
            st.rerun()
    
    with col2:
        if st.button("📋 Ingestão Manual", use_container_width=True, key="btn_manual_ingestion"):
            st.session_state.current_page = "manual_ingestion"
            st.rerun()
    
    with col3:
        if st.button("📈 Analytics e Relatórios", use_container_width=True, key="btn_analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col4:
        if st.button("📊 Dashboard", use_container_width=True, key="btn_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    st.divider()
    
    # Linha 2: Gestão de Usuários
    st.markdown("**👥 Gestão de Usuários**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👤 Cadastro de Usuários", use_container_width=True, key="btn_user_registration"):
            st.session_state.current_page = "user_registration"
            st.rerun()
    
    with col2:
        if st.button("🔐 Consulta de Usuários (LGPD)", use_container_width=True, key="btn_user_viewer"):
            st.session_state.current_page = "user_viewer"
            st.rerun()
    
    st.divider()
    
    # Linha 3: Informações
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("ℹ️ Sobre Nós", use_container_width=True, key="btn_about"):
            st.session_state.current_page = "about"
            st.rerun()


# ============================================================================
# FUNÇÃO PÁGINA INGESTÃO
# ============================================================================

def page_ingestion():
    """Página de ingestão de dados."""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 📥 Pipeline de Ingestão e Persistência")
    
    with col2:
        if st.button("Voltar", key="btn_back_ingestion"):
            st.session_state.current_page = "home"
            st.rerun()
    
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
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 📋 Ingestão Manual via JSON")
    
    with col2:
        if st.button("Voltar", key="btn_back_manual_ingestion"):
            st.session_state.current_page = "home"
            st.rerun()
    
    show_manual_ingestion_page()


# ============================================================================
# FUNÇÃO PÁGINA ANALYTICS
# ============================================================================

def page_analytics():
    """Página de analytics e relatórios."""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 📊 Pipeline de Analytics e Relatórios")
    
    with col2:
        if st.button("Voltar", key="btn_back_analytics"):
            st.session_state.current_page = "home"
            st.rerun()
    
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
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 👤 Cadastro de Usuários")
    
    with col2:
        if st.button("Voltar", key="btn_back_user_registration"):
            st.session_state.current_page = "home"
            st.rerun()
    
    st.caption("🔒 Nome, CPF, e-mail, telefone e senha são protegidos (LGPD) antes de serem gravados.")
    st.divider()
    
    # Chamar a função do arquivo user_registration_app.py
    show_user_registration_page()


# ============================================================================
# FUNÇÃO PÁGINA CONSULTA DE USUÁRIOS
# ============================================================================

def page_user_data_viewer():
    """Página de consulta de usuários com dados protegidos (LGPD)."""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 🔐 Consulta de Usuários (LGPD)")
    
    with col2:
        if st.button("Voltar", key="btn_back_user_viewer"):
            st.session_state.current_page = "home"
            st.rerun()
    
    st.caption("Dados exibidos como estão gravados no banco. "
               "Somente nome, e-mail e telefone podem ser descriptografados; CPF e Senha são hash.")
    st.divider()
    
    # Chamar a função do arquivo user_data_viewer_app.py
    show_user_data_viewer_page()


# ============================================================================
# FUNÇÃO PÁGINA SOBRE NÓS
# ============================================================================

def page_about():
    """Página com informações sobre a equipe de desenvolvimento."""
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    
    with col1:
        st.markdown("### ℹ️ Sobre Nós")
    
    with col2:
        if st.button("Voltar", key="btn_back_about"):
            st.session_state.current_page = "home"
            st.rerun()
    
    st.divider()
    
    st.markdown("## Equipe de Desenvolvimento")
    st.markdown("Conheça os integrantes do projeto Academia Data Science:")
    st.divider()

    import base64

    def get_image_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    result = avatar(
        [
            {
                "url": f"data:image/png;base64,{get_image_base64('src/presentation/assets/alexandre_sass_silva.png')}",
                "size": 80,
                "title": "Alexandre Sass Silva",
                "caption": "Alexandre Sass Silva",
                "key": "avatar1",
            },
            {
                "url": f"data:image/png;base64,{get_image_base64('src/presentation/assets/gabriel_diniz_silva.png')}",
                "size": 80,
                "title": "Gabriel Diniz Silva",
                "caption": "Gabriel Diniz Silva",
                "key": "avatar2",
            },
            {
                "url": f"data:image/png;base64,{get_image_base64('src/presentation/assets/luis_queiroz_dias.png')}",
                "size": 80,
                "title": "Luís Queiroz Dias",
                "caption": "Luís Queiroz Dias",
                "key": "avatar3",
            },
            {
                "url": f"data:image/png;base64,{get_image_base64('src/presentation/assets/suelen_strack.png')}",
                "size": 80,
                "title": "Suélen Strack",
                "caption": "Suélen Strack",
                "key": "avatar4",
            },
        ]
    )
    st.write(result)


# ============================================================================
# FUNÇÃO PÁGINA DASHBOARD
# ============================================================================

def page_dashboard():
    """Página de exibição da arquitetura Gold (Dashboard)."""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("### 📊 Arquitetura Gold - Dashboard Estrutural")
    
    with col2:
        if st.button("Voltar", key="btn_back_dashboard"):
            st.session_state.current_page = "home"
            st.rerun()
    
    st.markdown("Visualização da arquitetura de dados do modelo dimensional (Star Schema).")
    st.divider()
    
    try:
        # Ler arquivo gold_architecture.md
        gold_arch_path = Path(__file__).parent.parent.parent / "docs" / "gold_architecture.md"
        
        if gold_arch_path.exists():
            with open(gold_arch_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Exibir conteúdo em abas para melhor organização
            st.markdown(content)
        else:
            st.error(f"❌ Arquivo não encontrado: {gold_arch_path}")
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo: {e}")
        logger.error(f"Erro ao exibir dashboard: {e}")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que renderiza a interface."""
    
    if st.session_state.current_page == "public_home":
        page_public_home()
    elif st.session_state.current_page == "home":
        page_home()
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
    elif st.session_state.current_page == "about":
        page_about()


if __name__ == "__main__":
    main()
