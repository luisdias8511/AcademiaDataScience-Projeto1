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
    run_pipeline,
)


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

st.title("Monitoramento e Análise de Dados Ambientais")
st.markdown("Consulte dados meteorológicos e de qualidade da água por estação e período.")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que renderiza a interface."""
    
    # Inicializar session state
    st.session_state.setdefault("weather_statistics", None)
    st.session_state.setdefault("water_statistics", None)
    st.session_state.setdefault("weather_csv_path", None)
    st.session_state.setdefault("weather_outliers_path", None)
    st.session_state.setdefault("water_csv_path", None)
    st.session_state.setdefault("water_outliers_path", None)
    st.session_state.setdefault("selected_station_name", None)
    st.session_state.setdefault("selected_period", None)
    
    # Carregar estações
    stations = load_stations()
    
    if not stations:
        st.warning("Nenhuma estação foi encontrada no banco de dados.")
        st.stop()
    
    # Criar dicionário de opções
    station_options = {
        f"{station.name}": station
        for station in stations
    }
    
    # Formulário
    with st.form("environmental_pipeline_form"):
        st.subheader("Parâmetros da Análise")
        
        # Seleção de estação
        selected_label = st.selectbox(
            "Estação",
            options=list(station_options.keys()),
        )
        selected_station = station_options[selected_label]

        # Seleção de período de análise
        start_date_value = st.date_input(
            "Data inicial",
            value=date.today() - timedelta(days=2),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
        )
        end_date_value = st.date_input(
            "Data final",
            value=date.today() - timedelta(days=1),
            format="DD/MM/YYYY",
            max_value=date.today() - timedelta(days=1),
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
            "Obter Resultados",
            type="primary",
            use_container_width=True,
        )
        
        # Executar pipeline se formulário foi enviado
        if submitted:
            if not validation_error:
                run_pipeline(
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
            st.subheader("**Estatísticas Meteorológicas**")       
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

        #Qualidade da Água    
        if st.session_state.water_statistics:
            stats = st.session_state.water_statistics
            total_obs = sum(
                result.count
                for result in stats
            )
            total_out = sum(
                len(result.outliers)
                for result in stats
            )
            st.subheader("**Estatísticas de Qualidade da Água**")
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
                st.session_state.water_csv_path,
                st.session_state.water_outliers_path,
                "water",
            )
        else:
            st.info("Nenhum resultado de qualidade da água disponível.")


if __name__ == "__main__":
    main()
