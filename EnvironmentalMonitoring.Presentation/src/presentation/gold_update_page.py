"""Página Streamlit para atualização manual da camada Gold do data warehouse."""

from datetime import date, datetime, timedelta
import streamlit as st

from src.database.gold_repository import GoldRepository
from src.services.gold_update_service import GoldUpdateService
from src.config import logger
from src.security.log_utils import tratar_erro


def show_gold_update_page():
    """Exibe a página de atualização da camada Gold."""
    
    # ========================================================================
    # CABEÇALHO
    # ========================================================================
    st.title("Atualização da Camada Gold")
    st.write(
        "Selecione o período que será processado da camada Silver "
        "para a camada Gold."
    )
    
    # ========================================================================
    # BUSCAR DATAS DISPONÍVEIS DA SILVER LAYER
    # ========================================================================
    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def get_date_range():
        """Busca as datas min/max da Silver layer."""
        try:
            repo = GoldRepository()
            repo._connect()
            min_date, max_date = repo.get_available_date_range()
            repo._disconnect()
            return min_date, max_date
        except Exception as e:
            logger.error(f"Erro ao buscar datas disponíveis: {e}")
            return None, None
    
    min_available_date, max_available_date = get_date_range()
    
    # Datas padrão: usar data disponível ou hoje
    if min_available_date:
        default_start = min_available_date
    else:
        default_start = date.today() - timedelta(days=30)
    
    if max_available_date:
        default_end = max_available_date
    else:
        default_end = date.today()
    
    # ========================================================================
    # FORM COM INPUTS DE DATA
    # ========================================================================
    with st.form("gold_update_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data inicial",
                value=default_start,
                min_value=min_available_date if min_available_date else date(2020, 1, 1),
                max_value=default_end if default_end else date.today(),
                help="Primeira data do período a processar (inclusiva)"
            )
        
        with col2:
            end_date = st.date_input(
                "Data final",
                value=default_end,
                min_value=default_start if default_start else date(2020, 1, 1),
                max_value=max_available_date if max_available_date else date.today(),
                help="Última data do período a processar (inclusiva)"
            )
        
        # Mostrar informação sobre datas disponíveis
        if min_available_date and max_available_date:
            st.info(
                f"ℹ️ Dados disponíveis de **{min_available_date}** a **{max_available_date}**"
            )
        elif not min_available_date or not max_available_date:
            st.warning(
                "⚠️ Não foi possível determinar a faixa de datas disponíveis. "
                "Verifique se há dados na camada Silver."
            )
        
        submitted = st.form_submit_button(
            "🚀 Atualizar camada Gold",
            use_container_width=True,
            type="primary"
        )
    
    # ========================================================================
    # PROCESSAMENTO DO FORM
    # ========================================================================
    if submitted:
        # Validações
        validation_error = None
        
        if start_date > end_date:
            validation_error = (
                "Data inicial não pode ser maior que data final"
            )
        elif end_date > date.today():
            validation_error = (
                "Data final não pode ser futura"
            )
        elif start_date == date.today() or end_date == date.today():
            # Mostrar aviso se incluir o dia de hoje
            st.warning(
                "⚠️ Você selecionou uma data que inclui hoje. "
                "Certifique-se de que todas as leituras foram já processadas."
            )
        
        if validation_error:
            st.error(f"❌ Erro de validação: {validation_error}")
        else:
            # ================================================================
            # EXECUTAR ATUALIZAÇÃO
            # ================================================================
            with st.spinner("⏳ Processando atualização da camada Gold..."):
                try:
                    service = GoldUpdateService()
                    result = service.update_gold_layer(start_date, end_date)
                    
                    # Armazenar resultado na sessão para exibir depois
                    st.session_state.gold_update_result = result
                    
                except Exception as e:
                    tratar_erro(e, "Atualização Gold", encerrar=False)
                    st.error(
                        "Não foi possível atualizar a camada Gold. "
                        "Consulte os logs para obter mais informações."
                    )
    
    # ========================================================================
    # EXIBIR RESULTADO SE HOUVER
    # ========================================================================
    if "gold_update_result" in st.session_state:
        result = st.session_state.gold_update_result
        
        st.divider()
        
        if result.is_success:
            st.success("✅ Camada Gold atualizada com sucesso!")
            
            # ================================================================
            # EXIBIR MÉTRICAS
            # ================================================================
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Datas inseridas",
                    result.inserted_dates
                )
            
            with col2:
                st.metric(
                    "Horários inseridos",
                    result.inserted_times
                )
            
            with col3:
                st.metric(
                    "Fatos inseridos",
                    result.inserted_facts
                )
            
            with col4:
                st.metric(
                    "Fatos atualizados",
                    result.updated_facts
                )
            
            # ================================================================
            # INFORMAÇÕES ADICIONAIS
            # ================================================================
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Total processado",
                    result.processed_facts
                )
            
            with col2:
                st.metric(
                    "Duração",
                    f"{result.duration_seconds:.2f}s"
                )
            
            # ================================================================
            # DETALHES DA EXECUÇÃO
            # ================================================================
            st.divider()
            
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.info(
                    f"**Período processado**\n\n"
                    f"De: {result.start_date.strftime('%d/%m/%Y')}\n\n"
                    f"Até: {result.end_date.strftime('%d/%m/%Y')}"
                )
            
            with detail_col2:
                st.info(
                    f"**Tempo de execução**\n\n"
                    f"Início: {result.started_at.strftime('%H:%M:%S')}\n\n"
                    f"Fim: {result.finished_at.strftime('%H:%M:%S')}"
                )
            
            with detail_col3:
                st.info(
                    f"**Pipeline Run ID**\n\n"
                    f"`{result.pipeline_run_id}`"
                )
            
        else:
            # Erro na execução
            st.error(f"❌ {result.error_message}")
            
            st.divider()
            
            error_col1, error_col2 = st.columns(2)
            
            with error_col1:
                st.info(
                    f"**Período solicitado**\n\n"
                    f"De: {result.start_date.strftime('%d/%m/%Y')}\n\n"
                    f"Até: {result.end_date.strftime('%d/%m/%Y')}"
                )
            
            with error_col2:
                st.warning(
                    f"**Pipeline Run ID**\n\n"
                    f"`{result.pipeline_run_id}`\n\n"
                    f"Duração: {result.duration_seconds:.2f}s"
                )
            
            st.info(
                "Para mais detalhes sobre o erro, consulte os logs da aplicação."
            )


if __name__ == "__main__":
    show_gold_update_page()
