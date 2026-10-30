"""Estilos CSS para a página pública (não autenticada)."""

import streamlit as st


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
        .sidebar-title {
            font-weight: 700;
            font-size: 1rem;
            line-height: 24px;
            color: #333;
            text-decoration: none;        
            margin-bottom: 1rem;
            color: #ff5800;
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
            padding: 3rem 2rem 8rem 2rem;
        }

        .public-about-text {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.7;
            text-align: center;
            max-width: 900px;
            margin: 1.5rem auto;
        }

        /* Avatares centralizados */
        .about-avatars {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 2rem;
            width: 100%;
        }

        .about-avatar-card {
            text-align: center;
            flex-shrink: 0;
        }

        .about-avatar-img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 0.5rem;
        }

        .about-avatar-name {
            font-size: 0.9rem;
            font-weight: 600;
            color: #333;
            margin: 0;
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
                font-size: 1.5rem;
            }

            .public-about {
                padding: 2.5rem 1rem;
            }

            .about-avatars {
                gap: 1.5rem;
            }

            .about-avatar-img {
                width: 100px;
                height: 100px;
            }

            .about-avatar-name {
                font-size: 0.8rem;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
