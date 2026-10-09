"""Router do endpoint público de histórico de qualidade da água."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.schemas.common import ERROR_RESPONSES
from src.schemas.water import WaterHistoryResponse
from src.security.api_key import validate_api_key
from src.services.history_service import HistoryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/environment/public/water",
    tags=["Water"],
    dependencies=[Depends(validate_api_key)],
)


@router.get(
    "/history",
    response_model=WaterHistoryResponse,
    summary="Histórico de qualidade da água",
    responses=ERROR_RESPONSES,
)
def get_water_history(
    lat: Annotated[
        Decimal,
        Query(ge=-90, le=90, description="Latitude da localização.", examples=["48.8566"]),
    ],
    lng: Annotated[
        Decimal,
        Query(ge=-180, le=180, description="Longitude da localização.", examples=["2.3522"]),
    ],
    from_date: Annotated[
        datetime | None,
        Query(
            alias="from",
            description="Início do período (ISO 8601). Padrão: 24 horas antes de 'to'.",
            examples=["2026-01-01T00:00:00Z"],
        ),
    ] = None,
    to_date: Annotated[
        datetime | None,
        Query(
            alias="to",
            description="Fim do período (ISO 8601). Padrão: início da hora atual (UTC).",
            examples=["2026-01-02T00:00:00Z"],
        ),
    ] = None,
    page: Annotated[
        int,
        Query(ge=0, description="Número da página (inicia em 0).", examples=[0]),
    ] = 0,
) -> WaterHistoryResponse:
    """Retorna o histórico de qualidade da água da estação nas coordenadas informadas."""
    logger.info(
        "water/history lat=%s lng=%s from=%s to=%s page=%s",
        lat,
        lng,
        from_date,
        to_date,
        page,
    )
    response = HistoryService().get_water_history(
        latitude=lat,
        longitude=lng,
        from_date=from_date,
        to_date=to_date,
        page=page,
    )
    logger.info("water/history retornou %s elementos", len(response.values))
    return response
