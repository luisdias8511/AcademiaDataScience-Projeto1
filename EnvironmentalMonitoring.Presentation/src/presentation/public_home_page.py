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
from streamlit_avatar import avatar

# ============================================================================
# ESTILOS CSS
# ============================================================================

def load_css():
    """Carrega estilos CSS customizados para a página pública."""
    css = """
    <style>
        /* Reset de estilos */
        body {
            margin: 0;
            padding: 0;
        }

        /* Gradiente principal - Rosa para Laranja */
        .gradient-text {
            background: linear-gradient(90deg, #ce0569 12.66%, #ff5800 94.55%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* ===== CABEÇALHO ===== */
        .public-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            border-bottom: 1px solid #e0e0e0;
            background-color: white;
        }

        .public-header-brand {
            font-size: 1rem;
            font-weight: 600;
            background-color: #ff5800;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -0.3px;
        }

        .public-header-login {
            background: white;
            border: 1px solid #999;
            padding: 0.5rem 1.2rem;
            border-radius: 3px;
            color: #333;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .public-header-login:hover {
            border-color: #ce0569;
            color: #ce0569;
        }

        /* ===== SEÇÃO HERO ===== */
        .public-hero {
            position: relative;
            width: 100%;
            height: 420px;
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding-left: 5%;
        }

        .public-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.2);
        }

        .public-hero-card {
            position: relative;
            z-index: 10;
            background: white;
            border-radius: 4px;
            padding: 2.5rem;
            max-width: 450px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }

        .public-hero-title {
            font-size: 1.9rem;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 1rem 0;
            line-height: 1.25;
        }

        .public-hero-text {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.65;
            margin: 0;
        }

        /* ===== SEÇÃO VISÃO GERAL ===== */
        .public-section {
            width: 100%;
            padding: 3rem 2rem;
        }

        .public-section-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 2rem 0;
            background: linear-gradient(90deg, #ce0569 12.66%, #ff5800 94.55%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .public-section-text {
            text-align: center;
            font-size: 0.95rem;
            color: #555;
            line-height: 1.7;
            max-width: 1000px;
            margin: 0 auto;
        }

        /* ===== SEÇÃO SOLUÇÕES ===== */
        .public-solutions {
            width: 100%;
            padding: 3rem 2rem;
            background-color: #fafafa;
        }

        .public-solutions-wrapper {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }

        .public-solutions-image {
            width: 100%;
        }

        .public-solutions-image img {
            width: 100%;
            height: auto;
            display: block;
            border-radius: 4px;
        }

        .public-solutions-text h2 {
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 1.5rem 0;
            background: linear-gradient(90deg, #ce0569 12.66%, #ff5800 94.55%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .public-solutions-text p {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.7;
            margin: 0 0 1.2rem 0;
        }

        .public-solutions-list {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
        }

        .public-solutions-list li {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.7;
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
        }

        .public-solutions-list li::before {
            content: '✓';
            position: absolute;
            left: 0;
            color: #ce0569;
            font-weight: bold;
            font-size: 1.1rem;
        }

        .public-cta-link {
            display: inline-block;
            margin-top: 1.5rem;
            color: #000 !important;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: color 0.2s ease;
        }

        .public-cta-link:hover {
            color: #ce0569;
        }

        .public-cta-link::after {
            content: ' →';
            margin-left: 0.3rem;
        }

        /* ===== SEÇÃO QUEM SOMOS ===== */
        .public-about {
            width: 100%;
            padding: 3rem 2rem;
        }

        .public-about-text {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.7;
            text-align: center;
            max-width: 900px;
            margin: 1.5rem auto;
        }

        /* ===== RODAPÉ ===== */
        .public-footer {
            text-align: center;
            padding: 2rem;
            color: #999;
            font-size: 0.85rem;
            border-top: 1px solid #e0e0e0;
        }

        /* ===== RESPONSIVIDADE ===== */
        @media (max-width: 768px) {
            .public-header {
                flex-direction: column;
                gap: 1rem;
                padding: 1rem;
            }

            .public-hero {
                height: 340px;
                padding-left: 2%;
            }

            .public-hero-card {
                max-width: 90%;
                padding: 1.5rem;
            }

            .public-hero-title {
                font-size: 1.5rem;
            }

            .public-section {
                padding: 2.5rem 1rem;
            }

            .public-section-title {
                font-size: 1.6rem;
            }

            .public-solutions {
                padding: 2.5rem 1rem;
            }

            .public-solutions-wrapper {
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }

            .public-solutions-text h2 {
                text-align: center;
                font-size: 1.6rem;
            }

            .public-solutions-text {
                text-align: center;
            }

            .public-cta-link {
                display: block;
                text-align: center;
                width: 100%;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ============================================================================
# COMPONENTES DA PÁGINA
# ============================================================================

def get_image_base64(image_path):
    """Converte uma imagem para base64 para embutir na URL."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        st.error(f"Erro ao carregar imagem: {e}")
        return ""


def render_header():
    """Renderiza o cabeçalho da página pública."""
    # Botão de login redireciona para main_login_app.py
    header_html = """<div class="public-header"><div class="public-header-brand">monitoramento ambiental</div></div>"""
    # header_html = """<div class="public-header"><div class="public-header-brand">monitoramento ambiental</div></div>"""

    st.markdown(header_html, unsafe_allow_html=True)


def render_hero():
    """Renderiza a seção hero com imagem de fundo e card."""
    assets_path = Path(__file__).parent / "assets" / "banner_home.jpg"
    
    if not assets_path.exists():
        st.error(f"❌ Imagem não encontrada: {assets_path}")
        return
    
    image_base64 = get_image_base64(str(assets_path))
    background_css = f"""<style>.public-hero {{background-image: url('data:image/jpeg;base64,{image_base64}');}}</style>"""
    
    hero_html = """<div class="public-hero"><div class="public-hero-card"><h1 class="public-hero-title">Monitoramento Ambiental Inteligente</h1><p class="public-hero-text">Centralize dados meteorológicos e de qualidade da água em uma plataforma única, apoiando análises, governança, rastreabilidade e tomada de decisão baseada em dados.</p></div></div>"""
    
    st.markdown(background_css, unsafe_allow_html=True)
    st.markdown(hero_html, unsafe_allow_html=True)


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
    about_html = """<div class="public-about"><h2 class="public-section-title">Quem Somos</h2><p class="public-about-text">Somos uma equipe formada no contexto da Academia Data Science da Avanade, desenvolvendo uma solução prática para aplicar conceitos de Engenharia de Dados, Governança, Qualidade da Informação e Analytics. Nosso objetivo é demonstrar como dados ambientais podem ser transformados em ativos estratégicos por meio de boas práticas de arquitetura, modelagem de dados e visualização de informações. Conheça os integrantes do projeto:</p><div style="text-align: center; margin-top: 1.5rem;"></div></div>"""
    st.markdown(about_html, unsafe_allow_html=True)    
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
