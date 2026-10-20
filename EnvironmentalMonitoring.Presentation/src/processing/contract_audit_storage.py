"""Persistência de eventos de contrato usando um serviço de Blob injetado."""

import hashlib
import logging
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID


class JsonBlobStorage(Protocol):
    """Interface já atendida por BlobStorageService."""

    def upload_json(self, blob_name: str, content: dict) -> None: ...


class AuditPersistenceError(RuntimeError):
    """Falha de envio; os arquivos anteriores podem já ter sido gravados."""

    def __init__(self, failed_path: str, saved_paths: list[str]) -> None:
        self.failed_path = failed_path
        self.saved_paths = tuple(saved_paths)
        super().__init__(
            f"Falha ao persistir auditoria. {len(saved_paths)} evento(s) "
            "confirmado(s) antes da falha."
        )


def _event_blob_path(event: dict) -> str:
    prefixes = {
        "CONTRACT_VALIDATION_FAILED": "contract-rejections",
        "DATA_QUALITY_VALIDATION_FAILED": "quality-rejections",
    }

    prefix = prefixes.get(event.get("event_type"))

    if prefix is None:
        raise ValueError("Tipo de evento de rejeição não suportado.")

    if event.get("action") != "REJECT_DOCUMENT":
        raise ValueError("Evento deve indicar REJECT_DOCUMENT.")

    category = event.get("category")
    if category not in {"water", "weather"}:
        raise ValueError("Categoria deve ser water ou weather.")

    execution_id = event.get("execution_id")
    if not isinstance(execution_id, str) or not execution_id.strip():
        raise ValueError("execution_id deve ser um texto não vazio.")

    document_id = event.get("document_id")
    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("document_id deve ser um texto não vazio.")

    event_id = str(UUID(event["event_id"]))

    timestamp = datetime.fromisoformat(
        event["timestamp"].replace("Z", "+00:00")
    )

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError(
            "Timestamp de auditoria deve conter fuso horário."
        )

    timestamp = timestamp.astimezone(timezone.utc)

    execution_key = hashlib.sha256(
        execution_id.encode("utf-8")
    ).hexdigest()

    return (
        f"{prefix}/"
        f"year={timestamp:%Y}/month={timestamp:%m}/day={timestamp:%d}/"
        f"category={category}/execution={execution_key}/{event_id}.json"
    )


def save_contract_audit_events(
    events: Iterable[dict],
    storage: JsonBlobStorage,
    logger: logging.Logger,
) -> list[str]:
    """Grava um JSON por evento e retorna os caminhos confirmados.

    O chamador deve fornecer um serviço apontando para o contêiner audit.
    Todos os caminhos são verificados antes do primeiro upload.
    Para repetir um envio, reutilize os mesmos eventos e event_ids.
    Falhas de persistência interrompem esta função e são propagadas.
    """
    planned = [(_event_blob_path(event), event) for event in events]
    paths = [path for path, _ in planned]
    if len(paths) != len(set(paths)):
        raise ValueError("Eventos repetidos no lote de auditoria.")

    saved = []
    for path, event in planned:
        try:
            storage.upload_json(path, event)
        except Exception as error:
            # Não inclui mensagem de SDK, connection string ou conteúdo do documento.
            logger.error(
                "Falha ao gravar evento de auditoria no Blob.",
                extra={
                    "event_type": "AUDIT_PERSISTENCE_FAILED",
                    "event_id": event["event_id"],
                    "execution_id": event["execution_id"],
                    "audit_blob_path": path,
                    "saved_event_count": len(saved),
                    "exception_type": type(error).__name__,
                },
            )
            raise AuditPersistenceError(path, saved) from error
        saved.append(path)

    if saved:
        logger.info(
            "Eventos de rejeição de contrato gravados no Blob.",
            extra={
                "event_type": "AUDIT_PERSISTENCE_COMPLETED",
                "saved_event_count": len(saved),
            },
        )
    return saved
