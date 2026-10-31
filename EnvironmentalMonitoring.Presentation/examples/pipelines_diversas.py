"""Pipeline Principal: Fluxo completo com dados de weather e water.

Demonstra o fluxo de ponta a ponta com dois tipos de dados ambientais:
Escolha de Estação → Período → Ingestion (Weather + Water) → Persistência → Recuperação + Filtros → Analytics → Tabelas

EXECUTAR:
- Interface Streamlit (padrão):  python -m src.main
- Interface Streamlit (tela cadastro de usuários):  python -m src.main --register-user
- Interface Streamlit (tela exibição de usuários):  python -m src.main --viewer-user
- Interface Streamlit (tela de login):              python -m src.main --login
"""

import sys
import subprocess

# ============================================================================
# FUNÇÕES DE INGESTION PARALELA
# ============================================================================

def fetch_weather_task(ingestion_service, station, start_date, end_date):
    """Task para executar ingestion de weather em thread paralela."""
    return ("weather", ingestion_service.fetch_weather_readings(station, start_date, end_date))

def fetch_water_task(ingestion_service, station, start_date, end_date):
    """Task para executar ingestion de water em thread paralela."""
    return ("water", ingestion_service.get_water_readings(station, start_date, end_date))


# ============================================================================
# PIPELINE DE CADASTRO DE USUÁRIOS
# ============================================================================

def run_register_user_registration_pipeline():
    """Executa a tela Streamlit de cadastro de usuários."""
    from pathlib import Path

    register_user_app = Path(__file__).parent / "presentation" / "user_registration_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(register_user_app)])


# ============================================================================
# PIPELINE DE EXIBIÇÃO DE USUÁRIOS
# ============================================================================

def run_viewer_user_registration_pipeline():
    """Executa a tela Streamlit de exibição de usuários."""
    from pathlib import Path

    display_user_app = Path(__file__).parent / "presentation" / "user_data_viewer_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(display_user_app)])

# ============================================================================
# PIPELINE DE LOGIN
# ============================================================================

def run_login_pipeline():
    """Executa a tela Streamlit de login."""
    from pathlib import Path

    login_app = Path(__file__).parent / "presentation" / "main_login_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(login_app)])



# ============================================================================
# PIPELINE STREAMLIT
# ============================================================================

def run_streamlit_pipeline():
    """Executa o pipeline via interface Streamlit (Web UI)."""
    import os
    from pathlib import Path
    
    # Obter caminho do arquivo streamlit_app.py
    streamlit_app = Path(__file__).parent / "presentation" / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print(f"❌ Erro: Arquivo {streamlit_app} não encontrado")
        return
    
    print(f"\n🚀 Iniciando interface Streamlit...")
    print(f"📂 Aplicação: {streamlit_app}\n")
    
    # Executar streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_app)])



# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que escolhe entre CLI, cadastro de usuários ou Streamlit."""
    # Verificar se usuário solicitou outros modos de execução
    if "--register-user" in sys.argv:
        run_register_user_registration_pipeline()
    elif "--viewer-user" in sys.argv:
        run_viewer_user_registration_pipeline()
    elif "--login" in sys.argv:
        run_login_pipeline()
    else:
        # Por padrão, executar Streamlit
        run_streamlit_pipeline()


if __name__ == "__main__":
    main()
