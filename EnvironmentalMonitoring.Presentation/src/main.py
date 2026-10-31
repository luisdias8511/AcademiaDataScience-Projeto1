"""Pipeline Principal do Sistema de Monitoramento Ambiental
PARA EXECUTAR:
- Interface Streamlit (padrão):  python -m src.main
"""

import sys
import subprocess

# ============================================================================
# PIPELINE STREAMLIT
# ============================================================================

def run_streamlit_pipeline():
    """Executa o pipeline via interface Streamlit (Web UI)."""

    from pathlib import Path
    
    # Obter caminho do arquivo streamlit_app.py
    streamlit_app = Path(__file__).parent / "presentation" / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print(f"❌ Erro: Arquivo {streamlit_app} não encontrado")
        return
    
    print(f"\n🚀 Iniciando interface Streamlit...")
    
    # Executar streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_app)])



# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal pipeline Streamlit."""
    run_streamlit_pipeline()

if __name__ == "__main__":
    main()
