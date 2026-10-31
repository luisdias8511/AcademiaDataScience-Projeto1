"""Página Home Principal - Plataforma de Monitoramento Ambiental.

Interface de navegação principal com acesso a todos os pipelines e funcionalidades.
"""

import streamlit as st


def show_home_page():
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
    