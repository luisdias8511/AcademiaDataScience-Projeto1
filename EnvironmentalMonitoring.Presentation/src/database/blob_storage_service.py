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

    def download_text(self, blob_name: str) -> str:
        """Baixa conteúdo de texto de um blob.
        
        Args:
            blob_name: Nome do blob.
            
        Returns:
            str: Conteúdo do blob como texto.
            
        Raises:
            Exception: Se blob não existe ou falha ao baixar.
        """
        blob_client = self._container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        return download_stream.readall().decode('utf-8')

    def append_line_to_jsonl(
        self,
        blob_name: str,
        line_data: dict
    ) -> None:
        """Adiciona uma linha (JSON) a um arquivo JSONL existente ou novo.
        
        Se o blob não existe, cria um novo. Se existe, lê o conteúdo e
        adiciona a nova linha no final.
        
        Args:
            blob_name: Nome do blob (arquivo JSONL).
            line_data: Dicionário a ser adicionado como nova linha JSON.
        """
        new_line = json.dumps(line_data, ensure_ascii=False)
        
        try:
            # Tenta ler o conteúdo existente
            existing_content = self.download_text(blob_name)
            updated_content = existing_content + "\n" + new_line
        except Exception:
            # Se blob não existe ou erro ao ler, começa do zero
            updated_content = new_line
        
        blob_client = self._container_client.get_blob_client(blob_name)
        blob_client.upload_blob(updated_content, overwrite=True)
