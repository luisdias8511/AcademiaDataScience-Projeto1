# Para que o Python consiga ler as Variáveis de Ambiente do .env, abra o terminal e instale o pacote python-dotenv: python.exe -m pip install python-dotenv
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega os valores
api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY_CRIPTOGRAFADA")
fernet_key = os.getenv("FERNET_KEY")

#Descriptografia da chave de API criptografada
f = Fernet(fernet_key)
api_key_real = f.decrypt(api_key.encode()).decode()

print(f"Conectando em: {api_url}")
print(f"Usando a chave de API: {api_key_real}")