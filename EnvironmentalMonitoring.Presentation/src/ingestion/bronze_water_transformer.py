import json

from src.models.parameter import Parameter


def build_bronze_document_water(
    orinal_reading_json: dict,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> dict | None:
    pollutants = []

    for allowed in allowed_parameters:
        source_pollutant = orinal_reading_json["pollutants"].get(allowed.code_api)
        if source_pollutant is None:
            continue

        pollutants.append({
            "parameter_code": allowed.code,
            "source_code": allowed.code_api,
            "name": source_pollutant["name"],
            "value": source_pollutant["value"],
            "unit": source_pollutant["unit"],
        })

    if not pollutants:
        return None

    return {
        "metadata": metadata,
        "payload": {
            "datetime": orinal_reading_json["datetime"],
            "pollutants": pollutants,
        },
    }

def build_bronze_documents_water(
    original_page_json: str,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> list[dict]:
    response = json.loads(original_page_json)
    documents = []

    for value in response["values"]:
        document = build_bronze_document_water(value, metadata, allowed_parameters)
        if document is not None:
            documents.append(document)

    return documents
