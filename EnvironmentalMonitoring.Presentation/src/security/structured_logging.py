"""
LOGGING ESTRUTURADO (requisito 3.7 do PDF)
==========================================
Em vez de usar print() ou logs em texto livre, cada evento do pipeline é gravado
como UMA LINHA JSON (formato "JSON Lines") no arquivo logs/app.log, contendo:
    - timestamp : carimbo de data/hora (UTC, padrão ISO-8601)
    - level     : nível de severidade (INFO, WARNING, ERROR...)
    - message   : mensagem descritiva
    - + informações de onde o log foi gerado (módulo, função, linha)
    - + campos extras opcionais (ex.: operador_id, total_rejeitados)

Exemplo de uma linha gerada:
{"timestamp": "2026-10-07T21:09:14+00:00", "level": "INFO", "logger": "TempH2OLogger",
 "module": "security", "function": "<module>", "line": 25, "message": "Conectando..."}

Por que JSON? Porque é fácil de ser lido por máquinas (ferramentas de monitoramento,
Power BI, Azure Monitor, Elastic etc.), permitindo filtrar por nível, módulo, data...
"""
import json                                       # converte o dicionário do log em texto JSON
import logging                                    # biblioteca padrão de logs do Python
import os                                         # leitura de variáveis de ambiente e criação de pastas
from datetime import datetime, timezone           # geração do carimbo de data/hora
from logging.handlers import RotatingFileHandler

from numpy import record  # handler que "gira" o arquivo quando ele fica grande

# ---------------------------------------------------------------------------
# 1) CONFIGURAÇÕES (podem ser alteradas pelo .env sem mexer no código)
# ---------------------------------------------------------------------------
# os.getenv("NOME", "padrão") -> lê a variável do ambiente; se não existir, usa o valor padrão
LOGGER_NAME = "TempH2OLogger"                         # nome do logger principal do projeto
LOG_DIR = os.getenv("LOG_DIR", "logs")                # pasta onde os logs serão gravados
LOG_FILE = os.getenv("LOG_FILE", "app.log")           # nome do arquivo de log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()    # nível mínimo registrado (DEBUG < INFO < WARNING < ERROR)

# Raiz do projeto: src/security/structured_logging.py -> sobe 3 níveis
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _relativizar(texto):
    """Remove o caminho absoluto da raiz do projeto, deixando só a estrutura local."""
    if isinstance(texto, str):
        return texto.replace(PROJECT_ROOT + os.sep, "")
    return texto

# Todo log do Python é um objeto "LogRecord" que já vem com vários atributos internos
# (name, msg, args, levelname, pathname...). Aqui guardamos a lista desses atributos
# padrão para, mais abaixo, conseguir identificar quais campos são EXTRAS (os que nós
# mesmos passamos com extra={...}) e incluir só esses no JSON, sem repetir o resto.
_ATRIBUTOS_PADRAO = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


# ---------------------------------------------------------------------------
# 2) FORMATADOR JSON
# ---------------------------------------------------------------------------
# Um "Formatter" define COMO o log será escrito. O padrão do Python escreve texto
# simples; criamos uma subclasse que escreve em JSON.
class JsonFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON."""

    # O método format() é chamado automaticamente pelo logging para cada log emitido.
    def format(self, record: logging.LogRecord) -> str:
        # 2.1) Monta um dicionário com os campos obrigatórios do log estruturado
        payload = {
            # record.created = momento do log em segundos (epoch); convertemos para data ISO em UTC
            "timestamp": datetime.fromtimestamp(record.created 
                                                #,tz=timezone.utc # Remoção do UTC explícito, mantendo o horário Local
                                                ).isoformat(),
            "level": record.levelname,       # INFO, WARNING, ERROR...
            "logger": record.name,           # nome do logger que gerou o log
            "module": record.module,         # arquivo .py de origem (sem extensão)
            "function": record.funcName,     # função de origem
            "line": record.lineno,           # linha de origem no arquivo
            "message": record.getMessage(),  # mensagem final (já com parâmetros aplicados)
        }

        # 2.2) Acrescenta os campos EXTRAS enviados assim:
        #      logger.info("Mensagem", extra={"operador_id": 7})
        #      Percorremos todos os atributos do registro e pegamos só os que NÃO são padrão.
        for chave, valor in record.__dict__.items():
            if chave not in _ATRIBUTOS_PADRAO and not chave.startswith("_"):
                payload[chave] = _relativizar(valor)

        # 2.3) Se o log veio de uma exceção (exc_info=True), inclui o traceback completo
        if record.exc_info:
            payload["exception"] = _relativizar(self.formatException(record.exc_info))

        # 2.4) Converte o dicionário em texto JSON:
        #      ensure_ascii=False -> mantém acentos legíveis (ex.: "Água" em vez de "\u00c1gua")
        #      default=str        -> qualquer valor não serializável (datas, Decimal...) vira texto
        return json.dumps(payload, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# 3) FUNÇÃO DE CONFIGURAÇÃO DO LOGGING
# ---------------------------------------------------------------------------
def configurar_logger(nome: str = LOGGER_NAME, console: bool = False) -> logging.Logger:
    """Configura (uma única vez) o logging da aplicação e devolve o logger pedido.

    nome    : nome do logger a ser retornado (padrão: "TempH2OLogger")
    console : se True, além do arquivo, também exibe os logs no terminal
    """
    # 3.1) Pegamos o logger "raiz" (root). Todos os loggers do projeto, inclusive os criados
    #      com logging.getLogger(__name__) em outros módulos, repassam seus logs para ele.
    #      Assim, configurando só a raiz, TODO o projeto passa a gerar logs em JSON.
    raiz = logging.getLogger()

    # 3.2) Evita configurar duas vezes (o que duplicaria cada linha no arquivo).
    #      Usamos um atributo "marcador" (_estruturado) para saber se já foi feito.
    if not getattr(raiz, "_estruturado", False):
        # Define o nível mínimo: logs abaixo dele são ignorados
        raiz.setLevel(LOG_LEVEL)

        # Cria a pasta logs/ caso ainda não exista (exist_ok=True evita erro se já existir)
        os.makedirs(LOG_DIR, exist_ok=True)

        # 3.3) Handler de ARQUIVO com rotação:
        #      quando app.log atinge 5 MB, ele é renomeado para app.log.1, app.log.2...
        #      e mantemos no máximo 5 arquivos antigos (backupCount=5) - evita encher o disco.
        arquivo = RotatingFileHandler(
            os.path.join(LOG_DIR, LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        arquivo.setFormatter(JsonFormatter())  # o arquivo recebe o formato JSON
        raiz.addHandler(arquivo)

        # 3.4) Handler de CONSOLE (opcional): formato de texto, mais fácil de ler na tela
        if console:
            tela = logging.StreamHandler()
            tela.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"))
            raiz.addHandler(tela)

        # 3.5) Marca que a configuração já foi feita
        raiz._estruturado = True

    # 3.6) Retorna o logger com o nome pedido (ele herda as configurações da raiz)
    return logging.getLogger(nome)
