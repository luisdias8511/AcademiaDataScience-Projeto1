"""Página Home pública (não autenticada) - Apresentação institucional do sistema.

Segue o layout corporativo apresentado no mockup, com:
- Cabeçalho fixo com branding
- Seção hero com banner
- Seção visão geral
- Seção soluções com imagem
- Seção quem somos
- Rodapé
"""

import base64
from pathlib import Path
import streamlit as st
from src.presentation.public_styles import load_css


def get_image_base64(image_path):
    """Converte imagem em base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def render_header():
    """Renderiza o cabeçalho da página pública."""
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.markdown(
            "<div style='font-size: 24px; font-weight: bold; color: #ff5800;'>monitoramento ambiental</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div></div>", unsafe_allow_html=True)
    
    with col2:
        # Botão que redireciona para a página de login - só aparece se não estiver logado
        if not st.session_state.get("usuario"):
            if st.button("Login", use_container_width=True, key="login_button"):
                st.session_state.current_page = "login"
                st.rerun()


def render_hero():
    """Renderiza a seção hero com imagem de fundo e card."""
    assets_path = Path(__file__).parent / "assets" / "banner_home.jpg"
    
    background_css = ""
    if assets_path.exists():
        image_base64 = get_image_base64(str(assets_path))
        background_css = f'<div class="public-hero" style="background-image: url(\'data:image/jpeg;base64,{image_base64}\');"><div class="public-hero-card"><h1 class="public-hero-title">Monitoramento Ambiental em Tempo Real</h1><p class="public-hero-text">Transforme dados ambientais em decisões inteligentes com nossa plataforma de análise integrada.</p></div></div>'
    else:
        st.error(f"❌ Imagem não encontrada: {assets_path}")
        background_css = '<div class="public-hero"><div class="public-hero-card"><h1 class="public-hero-title">Monitoramento Ambiental em Tempo Real</h1><p class="public-hero-text">Transforme dados ambientais em decisões inteligentes com nossa plataforma de análise integrada.</p></div></div>'
    
    st.markdown(background_css, unsafe_allow_html=True)


def render_overview():
    """Renderiza a seção de visão geral."""
    overview_html = """<div class="public-section"><h2 class="public-section-title">Dados ambientais transformados em conhecimento para decisão</h2><p class="public-section-text">

Nossa plataforma foi desenvolvida para demonstrar como práticas modernas de Engenharia de Dados podem apoiar esse processo, desde a coleta e validação das informações até sua disponibilização para análises e visualizações. Por meio de uma arquitetura estruturada em camadas, os dados são organizados, tratados e preparados para gerar insights que apoiam o acompanhamento de indicadores ambientais, a identificação de anomalias e a tomada de decisões baseada em evidências.

Com foco em governança, qualidade da informação e rastreabilidade, a solução integra diferentes fontes de dados em um ambiente único, promovendo uma visão clara e confiável das condições meteorológicas e da qualidade da água monitoradas ao longo do tempo.</p></div>"""
    st.markdown(overview_html, unsafe_allow_html=True)


def render_solutions():
    """Renderiza a seção de soluções."""
    assets_path = Path(__file__).parent / "assets" / "home_image1.jpg"
    
    # Construir imagem HTML
    image_html = ""
    if assets_path.exists():
        image_base64 = get_image_base64(str(assets_path))
        image_html = f'<div class="public-solutions-image"><img src="data:image/jpeg;base64,{image_base64}" alt="Soluções" style="width: 100%; height: auto; border-radius: 4px;"></div>'
    
    # Construir HTML completo em uma única string
    solutions_html = f"""<div class="public-solutions"><div class="public-solutions-wrapper">{image_html}<div class="public-solutions-text"><h2>Nossas Soluções</h2><p>O projeto reúne um conjunto completo de recursos para gestão e análise de dados ambientais. Desde a coleta de informações provenientes de APIs e inserções manuais até a consolidação em modelos analíticos otimizados, a plataforma oferece suporte à qualidade dos dados, detecção de anomalias, monitoramento de indicadores e visualizações interativas para apoiar estudos, pesquisas e iniciativas de sustentabilidade.</p><a class="public-cta-link">Explore as nossas soluções</a></div></div></div>"""
    
    st.markdown(solutions_html, unsafe_allow_html=True)


def render_about():
    """Renderiza a seção sobre o projeto."""
    # Dados dos integrantes
    integrantes = [
        {"nome": "Alexandre Sass Silva", "imagem": "src/presentation/assets/alexandre_sass_silva.png"},
        {"nome": "Gabriel Diniz Silva", "imagem": "src/presentation/assets/gabriel_diniz_silva.png"},
        {"nome": "Luís Queiroz Dias", "imagem": "src/presentation/assets/luis_queiroz_dias.png"},
        {"nome": "Suélen Strack", "imagem": "src/presentation/assets/suelen_strack.png"}
    ]
    
    # Construir HTML dos avatares
    avatars_html = ""
    for integrante in integrantes:
        img_b64 = get_image_base64(integrante["imagem"])
        avatars_html += f'<div class="about-avatar-card"><img src="data:image/png;base64,{img_b64}" alt="{integrante["nome"]}" class="about-avatar-img"><p class="about-avatar-name">{integrante["nome"]}</p></div>'
    
    # Construir HTML completo
    about_html = f"""<div class="public-about"><h2 class="public-section-title">Quem Somos</h2><p class="public-about-text">Somos uma equipe formada no contexto da Academia Data Science da Avanade, desenvolvendo uma solução prática para aplicar conceitos de Engenharia de Dados, Governança, Qualidade da Informação e Analytics. Nosso objetivo é demonstrar como dados ambientais podem ser transformados em ativos estratégicos por meio de boas práticas de arquitetura, modelagem de dados e visualização de informações. Conheça os integrantes do projeto:</p><div class="about-avatars">{avatars_html}</div></div>"""
    
    st.markdown(about_html, unsafe_allow_html=True)


def render_footer():
    """Renderiza o rodapé."""
    footer_html = """<div class="public-footer">© 2026 Monitoramento Ambiental Todos os direitos reservados.</div>"""
    st.markdown(footer_html, unsafe_allow_html=True)


# ============================================================================
# FUNÇÃO PRINCIPAL - PÁGINA PÚBLICA
# ============================================================================

def show_public_home_page():
    """Renderiza a página Home pública completa."""
    
    # Carrega CSS customizado
    load_css()
    
    # Renderiza componentes em ordem
    render_header()
    render_hero()
    render_overview()
    render_solutions()
    render_about()
    render_footer()
