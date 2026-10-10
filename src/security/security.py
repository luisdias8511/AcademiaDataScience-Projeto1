"""
CARREGAMENTO SEGURO DE CREDENCIAIS DA API
=========================================
Este módulo lê as configurações do arquivo .env e descriptografa a chave da API,
disponibilizando-a na variável `api_key_real` para os clientes de ingestão
(water_client.py, weather_client.py, etl_water.py, etl_weather.py).

A lógica de criptografia e de hash foi movida para módulos próprios:
    - src/security/crypto.py  -> criptografia reversível (Fernet)
    - src/security/hashing.py -> anonimização irreversível (SHA-256)
"""
# Para que o Python consiga ler as Variáveis de Ambiente do .env, abra o terminal e instale o pacote python-dotenv: python.exe -m pip install python-dotenv
import os                                       # leitura das variáveis de ambiente
from src.config import logger                   # logger estruturado (JSON) do projeto
from dotenv import load_dotenv                  # carrega o arquivo .env para o ambiente
from src.security.log_utils import tratar_erro  # função padronizada para registrar erros
from src.security.crypto import criptografar, descriptografar  # criptografia reversível
# anonimizar_cpf não é usada aqui, mas é importada para que códigos antigos que faziam
# "from src.security.security import anonimizar_cpf" continuem funcionando.
from src.security.hashing import anonimizar_cpf  # noqa: F401 - reexportado por compatibilidade


# 1) Carrega as variáveis do arquivo .env para o ambiente do processo
load_dotenv()

# 2) Lê os valores necessários (retorna None se a variável não existir)
api_url_temp = os.getenv("API_URL_TEMP")          # URL da API de temperatura/clima
api_url_water = os.getenv("API_URL_WATER")        # URL da API de qualidade da água
api_key = os.getenv("API_KEY_CRIPTOGRAFADA")      # chave da API guardada CRIPTOGRAFADA no .env
fernet_key = os.getenv("FERNET_KEY")              # chave mestra usada para descriptografar

# 3) Valor inicial: se a descriptografia falhar, os clientes verão None e darão erro claro
api_key_real = None

try:
    # 4) Descriptografa a chave de API usando o módulo de criptografia reversível (crypto.py)
    api_key_real = descriptografar(api_key, fernet_key)

    # 5) Registra no log estruturado. As URLs vão no campo extra "url" do JSON.
    logger.info("Conectando em Temperatura", extra={"url": api_url_temp})
    logger.info("Conectando em Água", extra={"url": api_url_water})
    # SEGURANÇA: registramos apenas que deu certo - NUNCA o valor da chave real
    logger.info("Chave de API descriptografada com sucesso")

except Exception as erro:
    # 6) Em caso de falha (chave ausente, inválida...), registra o erro sem derrubar a aplicação
    tratar_erro(erro, "Erro durante a Descriptografia da chave de API", encerrar=False)


def criptografar_email(email: str) -> str:
    """Criptografa um e-mail de forma REVERSÍVEL (pode ser lido de volta com descriptografar).

    E-mail é um dado que precisa ser recuperado no futuro (para contato),
    por isso usamos criptografia e não hash.
    """
    return criptografar(email, fernet_key)

