"""Exceções simples da aplicação."""


class StationNotFoundError(Exception):
    """Nenhuma estação cadastrada para as coordenadas informadas."""


class InvalidDateRangeError(Exception):
    """Intervalo de datas inválido."""


class UnsupportedUnitSystemError(Exception):
    """Sistema de unidades não suportado nesta versão."""


class DatabaseQueryError(Exception):
    """Falha ao executar uma consulta no banco de dados."""
