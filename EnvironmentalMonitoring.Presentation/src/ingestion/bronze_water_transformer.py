import json
from datetime import datetime
from src.models.parameter import Parameter
from .blob_paths import BlobPaths
from src.models.reading import Reading
from src.models.reading_value import ReadingValue

def build_bronze_document_water(
    orinal_reading_json: dict,
    metadata: dict,
    allowed_parameters: list[Parameter]
) -> tuple[dict, list[ReadingValue]] | None:
    pollutants = []
    readingValues =[]

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
        readingValues.append(ReadingValue(
            parameter_code=allowed.code,
            value=source_pollutant["value"]
        ))

    if not pollutants:
        return None

    return {
        "metadata": metadata,
        "payload": {
            "datetime": orinal_reading_json["datetime"],
            "pollutants": pollutants,
        },
    }, readingValues

def build_bronze_documents_water(
    original_page_json: str,
    metadata: dict,
    station_id: int,
    allowed_parameters: list[Parameter]
) -> tuple[list[Reading], list[dict]]:
    response = json.loads(original_page_json)
    readings = []
    documents = []

    for value in response["values"]:
        built = build_bronze_document_water(value, metadata, allowed_parameters)
        if built is None:
            continue

        document, reading_values = built
        blob_name = BlobPaths.build_blob_reading_name(metadata["station"]["code"], value["datetime"])
        timestamp = datetime.fromisoformat(value["datetime"])
        readings.append(Reading(station_id=station_id, timestamp=timestamp, values=tuple(reading_values)))
        documents.append({"blob_name": blob_name, "document": document})

    return readings, documents
