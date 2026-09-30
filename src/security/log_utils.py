# Registro de logging para tratamento de erros
import logging
from src.config import logger


def tratar_erro(erro, contexto="Operação", encerrar=False):
    """
    Registra a exceção no log de forma padronizada.

    erro     : a exceção capturada (objeto Exception)
    contexto : texto curto dizendo onde/o que falhou
    encerrar : se True, re-lança a exceção após logar
    """
    logger.error(f"{contexto} - {type(erro).__name__}: {erro}", exc_info=True)
    if encerrar:
        raise erro