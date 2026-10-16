from azure.storage.blob import BlobServiceClient
import json
import os


class BlobStorageService:
    def __init__(
        self,
        container_name: str,
        connection_string: str | None = None,
    ):
        if connection_string:
            # Usar string customizada fornecida
            self.connection_string = connection_string
        else:
            # Carregar variáveis de ambiente e construir string
            # Tenta carregar do .env se disponível
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                # Se dotenv não estiver disponível, prossegue com variáveis do sistema
                pass
            
            # Obter variáveis de ambiente 
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

        if not connection_string:
            raise ValueError("Azure Storage connection string is not provided.")
        
        self.connection_string = connection_string

        self._container_name = container_name

        self._blob_service_client = (
            BlobServiceClient.from_connection_string(
                connection_string
            )
        )

        self._container_client = (
            self._blob_service_client.get_container_client(
                container_name
            )
        )

    def upload_json(
        self,
        blob_name: str,
        content: dict
    ) -> None:

        blob_client = self._container_client.get_blob_client(
            blob_name
        )

        blob_client.upload_blob(
            json.dumps(
                content,
                ensure_ascii=False,
                indent=2
            ),
            overwrite=True
        )

    def blob_exists(self, blob_name: str) -> bool:
        blob_client = self._container_client.get_blob_client(blob_name)
        return blob_client.exists()
