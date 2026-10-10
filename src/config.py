# Configuração central de logging do projeto.
# Os logs são ESTRUTURADOS (uma linha JSON por evento) - a lógica completa está em
# src/security/logging.py. Os demais módulos continuam usando:
#     from src.config import logger
import os

# LOG_DIR é reexportado aqui porque outros pontos do projeto podem precisar da pasta de logs
from src.security.structured_logging import LOG_DIR, configurar_logger

# carrega as variáveis do .env para o ambiente
from dotenv import load_dotenv
load_dotenv()

# Lê a variável LOG_TO_CONSOLE do .env
logger = configurar_logger(console=os.getenv("LOG_TO_CONSOLE").lower() == "true")
