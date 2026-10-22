import json
from datetime import datetime
from src.models.parameter import Parameter
from .blob_paths import BlobPaths
from src.models.operator import Operator
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


class DataParser:
    """Transforma dados brutos objetos Reading e documentos para armazenamento em bronze."""
    def __init__(self) -> None:
        pass

    def build_document_reading(
        self,
        specifications_name: str,
        orinal_reading_json: dict,
        metadata: dict,
        allowed_parameters: list[Parameter],
        category_code: str
    ) -> tuple[dict, list[ReadingValue]] | None:
        specifications  = []
        readingValues =[]

        for allowed in allowed_parameters:
            source_specification = orinal_reading_json[specifications_name].get(allowed.code_api)
            if source_specification is None:
                continue

            specifications.append({
                "parameter_code": allowed.code,
                "source_code": allowed.code_api,
                "name": source_specification["name"],
                "value": source_specification["value"],
                "unit": source_specification["unit"],
            })
            readingValues.append(ReadingValue(
                parameter_code=allowed.code,
                parameter_category_code=category_code,
                value=source_specification["value"]
            ))

        if not specifications :
            return None

        return {
            "metadata": metadata,
            "payload": {
                "datetime": orinal_reading_json["datetime"],
                specifications_name: specifications ,
            },
        }, readingValues

    def build_documents_readings(
        self,
        specifications_name: str,
        original_page_json: str | dict,
        metadata: dict,
        station_id: int,
        operator: Operator,
        allowed_parameters: list[Parameter],
        category_code: str
    ) -> tuple[list[Reading], list[dict]]:
        if isinstance(original_page_json, str):
            response = json.loads(original_page_json)
        else:
            response = original_page_json
        readings = []
        documents = []

        for value in response["values"]:
            built = self.build_document_reading(specifications_name, value, metadata, allowed_parameters, category_code)
            if built is None:
                continue

            document, reading_values = built
            
            # Filtrar ReadingValues para manter apenas da categoria esperada
            filtered_values = [
                rv for rv in reading_values 
                if rv.parameter_category_code == category_code
            ]
            
            # Pular se nenhum valor da categoria foi encontrado
            if not filtered_values:
                continue
            
            blob_name = BlobPaths.build_blob_reading_name(metadata["station"]["code"], value["datetime"])
            timestamp = datetime.fromisoformat(value["datetime"])
            readings.append(Reading(station_id=station_id, timestamp=timestamp, values=tuple(filtered_values), operator=operator))
            documents.append({"blob_name": blob_name, "document": document})

        return readings, documents
