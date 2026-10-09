# Configuração da Função de logging
import os
import logging

# Cria a pasta de logs se não existir
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',

    # Além de gravar no arquivo de log, também exibe no console
    # handlers=[
    #             logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding='utf-8'),
    #             logging.StreamHandler()
    #         ],
    #         force=True

    # Apenas Grava no arquivo de log, sem exibir no console
    filename='logs/app.log',   # <-- grava em arquivo
    filemode='a',              # 'a' = append (não apaga o histórico)
    encoding='utf-8'
)
logger = logging.getLogger('TempH2OLogger')
