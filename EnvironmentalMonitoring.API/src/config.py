"""Configurações da aplicação via variáveis de ambiente."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Representa as configurações obrigatórias da API."""

    sql_server: str = Field(..., alias="SQL_SERVER")
    sql_database: str = Field(..., alias="SQL_DATABASE")
    sql_username: str = Field(..., alias="SQL_USERNAME")
    sql_password: str = Field(..., alias="SQL_PASSWORD")
    sql_driver: str = Field("ODBC Driver 18 for SQL Server", alias="SQL_DRIVER")
    sql_connection_timeout: int = Field(30, alias="SQL_CONNECTION_TIMEOUT")
    api_key: str = Field(..., alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    @field_validator(
        "sql_server",
        "sql_database",
        "sql_username",
        "sql_password",
        "sql_driver",
        "api_key",
    )
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que campos obrigatórios não estão vazios."""
        if not value or not value.strip():
            raise ValueError("Campo obrigatório não pode estar vazio.")
        return value

    @field_validator("sql_connection_timeout")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        """Valida timeout de conexão."""
        if value <= 0:
            raise ValueError("Timeout de conexão deve ser maior que zero.")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna configurações carregadas com cache local do processo."""
    return Settings()

