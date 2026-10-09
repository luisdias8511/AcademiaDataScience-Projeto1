"""Ponto de entrada da aplicação FastAPI."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.database.connection import DatabaseConnectionError
from src.exceptions import (
    DatabaseQueryError,
    InvalidDateRangeError,
    StationNotFoundError,
    UnsupportedUnitSystemError,
)
from src.routers.water import router as water_router
from src.routers.weather import router as weather_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

INTERNAL_ERROR_MESSAGE = "Erro interno ao consultar os dados."

app = FastAPI(
    title="Environmental Monitoring API",
    version="0.1.0",
    description="API de consulta dos dados ambientais centralizados.",
    openapi_tags=[
        {"name": "Weather", "description": "Histórico meteorológico."},
        {"name": "Water", "description": "Histórico de qualidade da água."},
    ],
)

app.include_router(weather_router)
app.include_router(water_router)


@app.exception_handler(StationNotFoundError)
async def station_not_found_handler(request: Request, exc: StationNotFoundError) -> JSONResponse:
    """Retorna 404 quando não há estação nas coordenadas."""
    return JSONResponse(status_code=404, content={"detail": "Localização não encontrada."})


@app.exception_handler(InvalidDateRangeError)
@app.exception_handler(UnsupportedUnitSystemError)
async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Retorna 422 para período inválido ou sistema de unidades sem suporte."""
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Retorna 422 com 'detail' em texto simples."""
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part != "query")
        messages.append(f"{location}: {error.get('msg', 'valor inválido')}")
    return JSONResponse(status_code=422, content={"detail": "; ".join(messages)})


@app.exception_handler(DatabaseConnectionError)
@app.exception_handler(DatabaseQueryError)
async def database_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Retorna 500 sem expor detalhes do banco."""
    logger.error("Falha de banco de dados em %s: %s", request.url.path, type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": INTERNAL_ERROR_MESSAGE})


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Retorna 500 para falhas inesperadas, registrando apenas o tipo do erro."""
    logger.error("Erro inesperado em %s: %s", request.url.path, type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": INTERNAL_ERROR_MESSAGE})
