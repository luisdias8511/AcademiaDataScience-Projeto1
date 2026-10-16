import json
from datetime import datetime
from src.models.parameter import Parameter
from .blob_paths import BlobPaths
from src.models.reading import Reading
from src.models.reading_value import ReadingValue

def build_bronze_document_weather(
    orinal_reading_json: dict,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> tuple[dict, list[ReadingValue]] | None:
    parameters = []
    readingValues =[]

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
        readingValues.append(ReadingValue(
            parameter_code=allowed.code,
            value=source_parameter["value"]
        ))

    if not parameters:
        return None

    return {
        "metadata": metadata,
        "payload": {
            "datetime": orinal_reading_json["datetime"],
            "parameters": parameters,
        },
    }, readingValues

def build_bronze_documents_weather(
    original_page_json: str,
    metadata: dict,
    station_id: int,
    allowed_parameters: list[Parameter]
) -> tuple[list[Reading], list[dict]]:
    response = json.loads(original_page_json)
    readings = []
    documents = []

    for value in response["values"]:
        built = build_bronze_document_weather(value, metadata, allowed_parameters)
        if built is None:
            continue

        document, reading_values = built
        blob_name = BlobPaths.build_blob_reading_name(metadata["station"]["code"], value["datetime"])
        timestamp = datetime.fromisoformat(value["datetime"])
        readings.append(Reading(station_id=station_id, timestamp=timestamp, values=tuple(reading_values)))
        documents.append({"blob_name": blob_name, "document": document})

    return readings, documents