"""Qualidade de documentos Bronze já aprovados no contrato.

Não acessa Azure, banco ou API. Duplicidades são verificadas somente no lote.
Um documento rejeitado não reserva chaves de medição para os seguintes.
"""

from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import math


# Decisões provisórias do projeto, revisáveis pelo grupo.
DEFAULT_FUTURE_TOLERANCE = timedelta(minutes=5)

PARAMETER_RULES = {
    "AIR_TEMPERATURE": {"category": "weather", "unit": "°C", "minimum": None, "maximum": None},
    "CONDUCTIVITY": {"category": "water", "unit": "µS/cm (25°C)", "minimum": 0, "maximum": None},
    "HARDNESS": {"category": "water", "unit": "°f", "minimum": 0, "maximum": None},
    "TURBIDITY": {"category": "water", "unit": "NFU", "minimum": 0, "maximum": None},
    "PH": {"category": "water", "unit": "pH unity", "minimum": 0, "maximum": 14},
    "WATER_TEMPERATURE": {"category": "water", "unit": "°C", "minimum": None, "maximum": None},
}


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Aplique a validação do contrato antes: data sem fuso.")
    return parsed.astimezone(timezone.utc)


def _number(value) -> bool:
    return (
        isinstance(value, (int, float, Decimal))
        and not isinstance(value, bool)
        and (value.is_finite() if isinstance(value, Decimal) else
             math.isfinite(value) if isinstance(value, float) else True)
    )


def _issue(code: str, path: str, reason: str) -> dict:
    return {"error_code": code, "field_path": path, "reason": reason}


def assess_data_quality(
    documents: list[dict],
    category: str,
    *,
    rules: dict | None = None,
    mode: str = "historical",
    future_tolerance: timedelta | None = DEFAULT_FUTURE_TOLERANCE,
    maximum_delay: timedelta | None = None,
) -> dict:
    """Retorna resultados por documento e indicadores do lote.

    Pré-condição: documentos aprovados pelo contrato da categoria.
    mode: historical (inclui backfill) ou realtime.
    Datas futuras: padrão de cinco minutos em relação ao horário de ingestão.
    O limite exato é aceito; acima dele, rejeita em ambos os modos.
    Passe future_tolerance=None para desativar a rejeição e manter apenas alerta.
    Atraso: somente alerta, em realtime e com maximum_delay configurado.
    A chave provisória é estação + instante UTC + parâmetro.
    Esta função não mede acurácia nem verifica duplicatas no banco.
    """
    if category not in {"water", "weather"}:
        raise ValueError("Categoria deve ser water ou weather.")
    if mode not in {"historical", "realtime"}:
        raise ValueError("mode deve ser historical ou realtime.")
    for duration in (future_tolerance, maximum_delay):
        if duration is not None and (
            not isinstance(duration, timedelta) or duration < timedelta(0)
        ):
            raise ValueError("Tolerâncias devem ser timedelta não negativo ou None.")

    selected = deepcopy(PARAMETER_RULES if rules is None else rules)
    if set(selected) != set(PARAMETER_RULES):
        raise ValueError("A configuração deve conter exatamente os seis parâmetros.")
    for code, rule in selected.items():
        if rule["category"] != PARAMETER_RULES[code]["category"]:
            raise ValueError("Categoria de parâmetro incompatível com a configuração.")
        if not isinstance(rule["unit"], str) or not rule["unit"].strip():
            raise ValueError("Unidade configurada deve ser um texto não vazio.")
        minimum, maximum = rule["minimum"], rule["maximum"]
        if any(v is not None and not _number(v) for v in (minimum, maximum)):
            raise ValueError("Limites devem ser números finitos ou None.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Limite mínimo maior que o máximo.")

    collection = "parameters" if category == "weather" else "pollutants"
    seen = {}
    results = []
    for index, document in enumerate(documents):
        metadata = document["metadata"]
        station = metadata["station"]["code"]
        reading_time = _utc(document["payload"]["datetime"])
        ingestion_time = _utc(metadata["ingestion_datetime"])
        measurements = document["payload"][collection]
        errors, warnings, unchecked = [], [], []
        staged = {}
        if not station.strip():
            errors.append(_issue("DQ_EMPTY_STATION", "/metadata/station/code", "Identificação da estação contém apenas espaços."))

        delay = ingestion_time - reading_time
        if delay < timedelta(0):
            future = -delay
            if future_tolerance is None:
                warnings.append(_issue("DQ_FUTURE_READING", "/payload/datetime", "Leitura posterior à ingestão; tolerância não configurada."))
            elif future > future_tolerance:
                errors.append(_issue("DQ_FUTURE_READING", "/payload/datetime", "Leitura excede a tolerância de futuro configurada."))
        if mode == "realtime" and maximum_delay is not None and delay > maximum_delay:
            warnings.append(_issue("DQ_DELAYED_READING", "/payload/datetime", "Atraso maior que o prazo configurado."))
        if future_tolerance is None:
            unchecked.append("future_tolerance_not_configured")
        if mode == "historical":
            unchecked.append("delivery_delay_not_applied_in_historical_mode")
        elif maximum_delay is None:
            unchecked.append("maximum_delay_not_configured")

        for position, item in enumerate(measurements):
            path = f"/payload/{collection}/{position}"
            code, value, unit = item["parameter_code"], item["value"], item["unit"]
            rule = selected.get(code)
            if rule is None or rule["category"] != category:
                errors.append(_issue("DQ_PARAMETER_NOT_ALLOWED", path + "/parameter_code", "Parâmetro não permitido nesta categoria."))
                continue
            if unit != rule["unit"]:
                errors.append(_issue("DQ_UNIT_MISMATCH", path + "/unit", "Unidade diferente da configuração do parâmetro."))
            if not _number(value):
                errors.append(_issue("DQ_INVALID_NUMBER", path + "/value", "Valor deve ser numérico e finito; booleanos não são aceitos."))
                continue
            numeric = Decimal(str(value))
            for bound, comparison in (("minimum", lambda a, b: a < b), ("maximum", lambda a, b: a > b)):
                limit = rule[bound]
                if limit is None:
                    unchecked.append(f"{code}.{bound}_not_configured")
                elif comparison(numeric, Decimal(str(limit))):
                    errors.append(_issue("DQ_OUT_OF_RANGE", path + "/value", "Valor fora do limite configurado para o parâmetro."))
            key = (station, reading_time, code)
            previous = staged.get(key, seen.get(key))
            current = (numeric, unit)
            if previous is not None:
                duplicate_code = "DQ_DUPLICATE_MEASUREMENT" if previous == current else "DQ_CONFLICTING_MEASUREMENT"
                errors.append(_issue(duplicate_code, path, "Medição repetida ou conflitante na chave estação, instante e parâmetro."))
            else:
                staged[key] = current

        approved = not errors
        if approved:
            seen.update(staged)
        results.append({
            "document_index": index,
            "approved": approved,
            "action": "ACCEPT_DOCUMENT" if approved else "REJECT_DOCUMENT",
            "errors": errors,
            "warnings": warnings,
            "unchecked_rules": sorted(set(unchecked)),
            "delay_seconds": delay.total_seconds(),
        })

    return {
        "results": results,
        "summary": {
            "received_documents": len(results),
            "approved_documents": sum(result["approved"] for result in results),
            "rejected_documents": sum(not result["approved"] for result in results),
            "documents_with_warnings": sum(bool(result["warnings"]) for result in results),
            "documents_with_unchecked_rules": sum(bool(result["unchecked_rules"]) for result in results),
            "error_occurrences_by_code": dict(Counter(e["error_code"] for r in results for e in r["errors"])),
            "warning_occurrences_by_code": dict(Counter(w["error_code"] for r in results for w in r["warnings"])),
        },
    }


def build_data_quality_audit_events(
    document: dict,
    result: dict,
    *,
    execution_id: str,
    document_id: str,
    category: str,
) -> list[dict]:
    """Cria eventos de rejeição; alertas permanecem no resultado da avaliação."""
    from uuid import uuid4

    if category not in {"water", "weather"}:
        raise ValueError("Categoria deve ser water ou weather.")
    for value in (execution_id, document_id):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Identificadores devem ser textos não vazios.")
    if result["approved"]:
        if result["errors"]:
            raise ValueError("Resultado aprovado não pode conter erros de rejeição.")
        return []
    if not result["errors"]:
        raise ValueError("Resultado rejeitado deve conter os motivos.")
    metadata = document["metadata"]
    timestamp = datetime.now(timezone.utc).isoformat()
    return [{
        "event_id": str(uuid4()),
        "timestamp": timestamp,
        "level": "WARNING",
        "message": "Documento rejeitado por regra de qualidade de dados.",
        "event_type": "DATA_QUALITY_VALIDATION_FAILED",
        "execution_id": execution_id,
        "document_id": document_id,
        "category": category,
        "contract_version": metadata.get("contract_version"),
        "station_code": metadata["station"]["code"],
        "rule": issue["error_code"],
        **issue,
        "action": "REJECT_DOCUMENT",
    } for issue in result["errors"]]
