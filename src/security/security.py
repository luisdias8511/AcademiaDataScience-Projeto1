# Para que o Python consiga ler as Variáveis de Ambiente do .env, abra o terminal e instale o pacote python-dotenv: python.exe -m pip install python-dotenv
import os
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Configuração de logs - em substuição dos prints() comuns, recursos mais avançados
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('TempH2OLogger')


# Carrega as variáveis do arquivo .env
load_dotenv()

# Pega os valores
api_url_temp = os.getenv("API_URL_TEMP")
api_url_water = os.getenv("API_URL_WATER")
api_key = os.getenv("API_KEY_CRIPTOGRAFADA")
fernet_key = os.getenv("FERNET_KEY")

try:
    #Tenta Descriptografia da chave de API criptografada
    f = Fernet(fernet_key)
    api_key_real = f.decrypt(api_key.encode()).decode()

    #print(f"Conectando em: {api_url}")
    #print(f"Usando a chave de API: {api_key_real}")
    # Configuração de logs - em substuição dos prints() comuns, recursos mais avançados
    logger.info(f"Conectando em Temperatura: {api_url_temp}")
    logger.info(f"Conectando em Água: {api_url_water}")
    logger.info("Chave de API descriptografada com sucesso") #Removendo a exibição da chave real nos logs

except Exception as erro:
    # Caso ocorra algum erro na Descriptografia, o código exibe o erro em vez de quebrar
    #print(f"Erro ao descriptografar a chave de API: {erro}")
    # Configuração de logs - em substuição dos prints() comuns, recursos mais avançados
    logger.error(f"Erro ao descriptografar a chave de API: {erro}", exc_info=True) # E agora exibe também o rastreamento completo do erro nos logs