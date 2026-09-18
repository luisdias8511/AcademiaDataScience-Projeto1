# Para que o Python consiga ler as Variáveis de Ambiente do .env, abra o terminal e instale o pacote python-dotenv: python.exe -m pip install python-dotenv
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega os valores
api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")

print(f"Conectando em: {api_url}")