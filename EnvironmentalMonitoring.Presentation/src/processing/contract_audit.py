"""Eventos de auditoria de contrato; sem conexão a serviços externos."""

import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import uuid4

from jsonschema.exceptions import ValidationError


RULES = {
    "required": ("CONTRACT_REQUIRED_FIELD", "Campo obrigatório ausente."),
    "type": ("CONTRACT_INVALID_TYPE", "Tipo de dado incompatível com o contrato."),
    "format": ("CONTRACT_INVALID_FORMAT", "Formato incompatível com o contrato."),
    "enum": ("CONTRACT_INVALID_ENUM", "Valor fora da lista permitida."),
    "const": ("CONTRACT_INVALID_CONSTANT", "Valor diferente da constante exigida."),
    "minimum": ("CONTRACT_OUT_OF_RANGE", "Valor abaixo do mínimo permitido."),
    "maximum": ("CONTRACT_OUT_OF_RANGE", "Valor acima do máximo permitido."),
    "minItems": ("CONTRACT_EMPTY_COLLECTION", "Lista com menos itens que o mínimo exigido."),
    "minLength": ("CONTRACT_TEXT_TOO_SHORT", "Texto menor que o mínimo exigido."),
    "pattern": ("CONTRACT_INVALID_PATTERN", "Texto incompatível com o padrão exigido."),
    "json_syntax": ("JSON_INVALID_SYNTAX", "Texto JSON com sintaxe inválida."),
    "json_duplicate_field": ( "JSON_DUPLICATE_FIELD", "Objeto JSON com campo repetido."),
    "json_nonfinite_number": ("JSON_NONFINITE_NUMBER", "Número não finito ou fora da representação numérica aceita."),
    "json_root_type": ("JSON_INVALID_ROOT", "A raiz deve ser um objeto JSON."),
}


def _pointer(parts: Iterable) -> str:
    """Representa um caminho como JSON Pointer; raiz é a string vazia."""
    return "".join(
        "/" + str(part).replace("~", "~0").replace("/", "~1")
        for part in parts
    )


def build_contract_audit_events(
    document: dict,
    errors: Iterable[ValidationError],
    *,
    execution_id: str,
    document_id: str,
    category: str,
    schema_name: str,
    occurred_at: datetime | None = None,
) -> list[dict]:
    """Cria um evento por erro, sem copiar o conteúdo original do documento.

    execution_id e document_id devem ser fornecidos pelo chamador.
    Campos de contexto só são aproveitados se forem textos não vazios.
    """
    context = {
        "execution_id": execution_id,
        "document_id": document_id,
        "category": category,
        "schema_name": schema_name,
    }
    for field, value in context.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} deve ser um texto não vazio.")
    if category not in {"water", "weather"}:
        raise ValueError("category deve ser water ou weather.")

    moment = occurred_at if occurred_at is not None else datetime.now(timezone.utc)
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("occurred_at deve conter fuso horário.")
    timestamp = moment.astimezone(timezone.utc).isoformat()

    metadata = document.get("metadata") if isinstance(document, dict) else None
    metadata = metadata if isinstance(metadata, dict) else {}
    station = metadata.get("station")
    station = station if isinstance(station, dict) else {}

    def text_or_none(value):
        return value if isinstance(value, str) and value.strip() else None

    events = []
    for error in errors:
        code, reason = RULES.get(
            error.validator,
            ("CONTRACT_VALIDATION_ERROR", "Documento incompatível com o contrato."),
        )
        # 'format' também pode representar outros formatos além de date-time.
        if error.validator == "format" and error.validator_value == "date-time":
            code = "CONTRACT_INVALID_DATETIME"
            reason = "Data/hora incompatível com o formato exigido pelo contrato."

        field_parts = list(error.absolute_path)
        # Para 'required', o erro aponta para o objeto pai. Detalhamos os campos ausentes.
        missing_fields = []
        if error.validator == "required" and isinstance(error.instance, dict):
            missing_fields = [
                field for field in error.validator_value
                if field not in error.instance
            ]

        events.append({
            "event_id": str(uuid4()),
            "timestamp": timestamp,
            "level": "WARNING",
            "message": "Documento rejeitado por violação do contrato Bronze.",
            "event_type": "CONTRACT_VALIDATION_FAILED",
            **context,
            "contract_version": text_or_none(metadata.get("contract_version")),
            "station_code": text_or_none(station.get("code")),
            "field_path": _pointer(field_parts),
            "schema_path": _pointer(error.absolute_schema_path),
            "missing_fields": missing_fields,
            "rule": error.validator,
            "error_code": code,
            "reason": reason,
            "action": "REJECT_DOCUMENT",
        })
    return events


def log_contract_audit_events(events: Iterable[dict], logger: logging.Logger) -> None:
    """Envia os eventos ao logger recebido; não configura handlers nem grava no Blob."""
    for event in events:
        extra = {
            key: value for key, value in event.items()
            if key not in {"timestamp", "level", "message"}
        }
        # O timestamp do evento é preservado separadamente do horário emitido pelo logger.
        extra["event_timestamp"] = event["timestamp"]
        logger.warning(event["message"], extra=extra)
