"""Conexão com Azure SQL Database via pyodbc."""

import pyodbc

from src.config import get_settings


class DatabaseConnectionError(Exception):
    """Erro de conexão com banco de dados."""


def get_connection() -> pyodbc.Connection:
    """Abre uma nova conexão com o banco usando SQL Server Authentication."""
    settings = get_settings()

    connection_string = (
        f"DRIVER={{{settings.sql_driver}}};"
        f"SERVER={settings.sql_server};"
        f"DATABASE={settings.sql_database};"
        f"UID={settings.sql_username};"
        f"PWD={settings.sql_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        f"Connection Timeout={settings.sql_connection_timeout};"
    )

    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as exc:
        raise DatabaseConnectionError(
            "Não foi possível estabelecer conexão com o banco de dados."
        ) from exc

