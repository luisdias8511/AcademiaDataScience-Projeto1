import datetime
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.reading_repository import ReadingRepository
from src.database.blob_storage_service import BlobStorageService
from src.ingestion.data_parser import DataParser
from src.ingestion.api_client import APIClient
from src.models import Station
from src.constants import SERVICES

service = SERVICES["weather"]

# Inicializa o repositório conexao com o banco de dados
repository = ReadingRepository()
# Obtem os parâmetros permitidos para parâmetros de água
allowed_parameters = repository.get_parameters_by_CategoryCode(service["category_code"])
dataParser = DataParser()
# Inicializa o serviço de armazenamento de blobs
blob_service = BlobStorageService(service["blob_container"])
# Inicializa o cliente da API
weather_client = APIClient()

ingestion_datetime = datetime.datetime.now(datetime.timezone.utc).isoformat()
meersens_json_list = weather_client.fetch_readings(Station(1, "FR_PARIS_488566_23522", "Estação Paris", 48.8566, -0.1278),"2026-10-12 00:00:00Z","2026-10-12 06:00:00Z",service["api_url_env"])

# Chamada para método de Construção dos documentos bronze para parâmetros de clima
for meersens_json in meersens_json_list:
    if not meersens_json:
        continue
    metadata = {
        "contract_version": "1.0",
        "source": {"type": "api", "provider": "meersens"},
        "ingestion_datetime": ingestion_datetime,
        "station": {
            "code": "FR_PARIS_488566_23522",
            "name": "Estação Paris",
            "latitude": 48.8566,
            "longitude": -0.1278,
        },
    }
    readings, documents = dataParser.build_documents_readings(service["specifications_name"], meersens_json, metadata, 1, allowed_parameters)
    for reading in readings:
        print(reading)
        # Impressão e armazenamento dos documentos bronze construídos usando dump JSON para melhor visualização na tela
    for item in documents:
        print(f"Blob name: {item['blob_name']}")
        print(f"Document:")
        print(json.dumps(item["document"], indent=2, ensure_ascii=False, default=str))
        # Verifica se o blob já existe e armazena o documento bronze no serviço de armazenamento de blobs
        if blob_service.blob_exists(item['blob_name']): 
            print(f"Blob já existe: {item['blob_name']}")  #TODO: Gerar log de backfill
        blob_service.upload_json(item['blob_name'], item["document"])