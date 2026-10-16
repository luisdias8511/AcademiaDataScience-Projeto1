import json

from src.models.parameter import Parameter
from .blob_paths import BlobPaths

def build_bronze_document_weather(
    orinal_reading_json: dict,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> dict | None:
    parameters = []

    for allowed in allowed_parameters:
        source_parameter = orinal_reading_json["parameters"].get(allowed.code_api)
        if source_parameter is None:
            continue

        parameters.append({
            "parameter_code": allowed.code,
            "source_code": allowed.code_api,
            "name": source_parameter["name"],
            "value": source_parameter["value"],
            "unit": source_parameter["unit"],
        })

    if not parameters:
        return None

    return {
        "metadata": metadata,
        "payload": {
            "datetime": orinal_reading_json["datetime"],
            "parameters": parameters,
        },
    }

def build_bronze_documents_weather(
    original_page_json: str,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> list[tuple[str, dict]]:
    response = json.loads(original_page_json)
    documents = []

    for value in response["values"]:
        document = build_bronze_document_weather(value, metadata, allowed_parameters)
        if document is not None:
            blob_name = BlobPaths.build_blob_reading_name(metadata["station"]["code"], value["datetime"])
            documents.append((blob_name, document))

    return documents
