import json
import random
from datetime import datetime
from decimal import Decimal
from src.models.parameter import Parameter
from src.ingestion.blob_paths import BlobPaths
from src.models.operator import Operator
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


# ============================================================================
# CONSTANTES PARA DADOS SINTÉTICOS
# ============================================================================

# Probabilidades de decisão para cada leitura
KEEP_ORIGINAL_PROBABILITY = 0.895     # 89.5% manter valor original
NORMAL_VARIATION_PROBABILITY = 0.10   # 10% aplicar variação normal
OUTLIER_PROBABILITY = 0.005           # 0.5% gerar possível outlier

# Faixas de valores sintéticos por parâmetro
SYNTHETIC_RANGES = {
    "AIR_TEMPERATURE": {
        "variation_range": 3.0,           # ±3°C
        "min_normal": -10.0,              # mínimo normal
        "max_normal": 40.0,               # máximo normal
        "outlier_low_range": (-25.0, -12.0),   # possível outlier baixo
        "outlier_high_range": (42.0, 55.0),    # possível outlier alto
    },
    "CONDUCTIVITY": {
        "variation_percentage": 0.10,     # ±10% variação percentual
        "outlier_range": (2000.0, 5000.0),  # possível outlier
    },
    "HARDNESS": {
        "variation_range": 3.0,           # ±3°f
        "outlier_range": (60.0, 100.0),   # possível outlier
    },
    "TURBIDITY": {
        "variation_range": 1.0,           # ±1 NFU
        "outlier_range": (20.0, 100.0),   # possível outlier
    },
    "PH": {
        "variation_range": 0.4,           # ±0.4
        "min_normal": 0.0,                # mínimo pH
        "max_normal": 14.0,               # máximo pH
        "outlier_low_range": (0.5, 3.5),       # possível outlier baixo
        "outlier_high_range": (10.5, 13.5),    # possível outlier alto
    },
    "WATER_TEMPERATURE": {
        "variation_range": 2.0,           # ±2°C
        "min_normal": 0.0,                # mínimo normal
        "max_normal": 35.0,               # máximo normal
        "outlier_range": (36.0, 45.0),    # possível outlier
    },
}


class DataParser:
    """Transforma dados brutos objetos Reading e documentos para armazenamento em bronze."""
    def __init__(self) -> None:
        pass

    @staticmethod
    def _generate_synthetic_value(parameter_code: str, original_value: float) -> float:
        """Gera um valor sintético para um parâmetro.
        
        A decisão de manter, variar ou gerar outlier é aleatória:
        - 89.5% chance: retorna o valor original
        - 10% chance: aplica variação normal ao valor
        - 0.5% chance: gera um possível outlier
        
        Args:
            parameter_code: Código do parâmetro (ex: AIR_TEMPERATURE)
            original_value: Valor original da medição
        
        Returns:
            float: Valor final arredondado com até 4 casas decimais
        """
        # Decidir qual estratégia usar
        decision = random.random()  # número entre 0.0 e 1.0
        
        if decision < KEEP_ORIGINAL_PROBABILITY:
            # 89.5%: manter valor original
            final_value = original_value
        elif decision < KEEP_ORIGINAL_PROBABILITY + NORMAL_VARIATION_PROBABILITY:
            # 10%: aplicar variação normal
            final_value = DataParser._apply_normal_variation(parameter_code, original_value)
        else:
            # 0.5%: gerar possível outlier
            final_value = DataParser._generate_outlier(parameter_code)
        
        # Arredondar para no máximo 4 casas decimais
        return round(final_value, 4)

    @staticmethod
    def _apply_normal_variation(parameter_code: str, original_value: float) -> float:
        """Aplica uma variação normal ao valor baseada no parâmetro.
        
        Args:
            parameter_code: Código do parâmetro
            original_value: Valor original
        
        Returns:
            float: Valor com variação aplicada
        """
        if parameter_code not in SYNTHETIC_RANGES:
            return original_value
        
        ranges = SYNTHETIC_RANGES[parameter_code]
        
        # ===== AIR_TEMPERATURE =====
        if parameter_code == "AIR_TEMPERATURE":
            variation = random.uniform(-ranges["variation_range"], ranges["variation_range"])
            new_value = original_value + variation
            # Limitar entre -10°C e 40°C
            return max(ranges["min_normal"], min(ranges["max_normal"], new_value))
        
        # ===== CONDUCTIVITY =====
        elif parameter_code == "CONDUCTIVITY":
            # Variação percentual de até 10%
            variation_pct = random.uniform(-ranges["variation_percentage"], ranges["variation_percentage"])
            new_value = original_value * (1 + variation_pct)
            # Nunca negativo
            return max(0.0, new_value)
        
        # ===== HARDNESS =====
        elif parameter_code == "HARDNESS":
            variation = random.uniform(-ranges["variation_range"], ranges["variation_range"])
            new_value = original_value + variation
            # Nunca negativo
            return max(0.0, new_value)
        
        # ===== TURBIDITY =====
        elif parameter_code == "TURBIDITY":
            variation = random.uniform(-ranges["variation_range"], ranges["variation_range"])
            new_value = original_value + variation
            # Nunca negativo
            return max(0.0, new_value)
        
        # ===== PH =====
        elif parameter_code == "PH":
            variation = random.uniform(-ranges["variation_range"], ranges["variation_range"])
            new_value = original_value + variation
            # Limitar entre 0 e 14
            return max(ranges["min_normal"], min(ranges["max_normal"], new_value))
        
        # ===== WATER_TEMPERATURE =====
        elif parameter_code == "WATER_TEMPERATURE":
            variation = random.uniform(-ranges["variation_range"], ranges["variation_range"])
            new_value = original_value + variation
            # Limitar entre 0°C e 35°C
            return max(ranges["min_normal"], min(ranges["max_normal"], new_value))
        
        return original_value

    @staticmethod
    def _generate_outlier(parameter_code: str) -> float:
        """Gera um possível outlier para um parâmetro.
        
        Args:
            parameter_code: Código do parâmetro
        
        Returns:
            float: Valor de possível outlier
        """
        if parameter_code not in SYNTHETIC_RANGES:
            return 0.0
        
        ranges = SYNTHETIC_RANGES[parameter_code]
        
        # ===== AIR_TEMPERATURE =====
        if parameter_code == "AIR_TEMPERATURE":
            # Escolher entre outlier baixo ou alto
            if random.random() < 0.5:
                return random.uniform(ranges["outlier_low_range"][0], ranges["outlier_low_range"][1])
            else:
                return random.uniform(ranges["outlier_high_range"][0], ranges["outlier_high_range"][1])
        
        # ===== CONDUCTIVITY =====
        elif parameter_code == "CONDUCTIVITY":
            return random.uniform(ranges["outlier_range"][0], ranges["outlier_range"][1])
        
        # ===== HARDNESS =====
        elif parameter_code == "HARDNESS":
            return random.uniform(ranges["outlier_range"][0], ranges["outlier_range"][1])
        
        # ===== TURBIDITY =====
        elif parameter_code == "TURBIDITY":
            return random.uniform(ranges["outlier_range"][0], ranges["outlier_range"][1])
        
        # ===== PH =====
        elif parameter_code == "PH":
            # Escolher entre outlier baixo ou alto
            if random.random() < 0.5:
                return random.uniform(ranges["outlier_low_range"][0], ranges["outlier_low_range"][1])
            else:
                return random.uniform(ranges["outlier_high_range"][0], ranges["outlier_high_range"][1])
        
        # ===== WATER_TEMPERATURE =====
        elif parameter_code == "WATER_TEMPERATURE":
            return random.uniform(ranges["outlier_range"][0], ranges["outlier_range"][1])
        
        return 0.0

    def build_demo_document_reading(
        self,
        specifications_name: str,
        orinal_reading_json: dict,
        metadata: dict,
        allowed_parameters: list[Parameter],
        category_code: str
    ) -> tuple[dict, list[ReadingValue]] | None:
        """Constrói um documento de leitura com valores sintéticos para demonstração.
        
        Similar ao método build_document_reading, mas substitui valores originais
        por dados sintéticos aleatoriamente para fins de:
        - Demonstrações do sistema
        - Testes no Power BI
        - Geração de diferenças visíveis nos gráficos
        - Demonstração de detecção de outliers
        - Testes de média móvel, IQR e Z-Score
        
        O método mantém 89.5% dos valores originais, aplica variação normal em 10%
        dos casos e gera possíveis outliers em apenas 0.5% dos casos.
        
        Args:
            specifications_name: Nome da especificação (ex: "parameters", "pollutants")
            orinal_reading_json: Dicionário com leitura original
            metadata: Metadados da ingestão
            allowed_parameters: Lista de parâmetros permitidos
            category_code: Código da categoria (WEATHER, WATER, etc)
        
        Returns:
            Tupla (documento, reading_values) ou None se sem especificações válidas.
            O documento contém os mesmos campos que build_document_reading,
            mas com valores potencialmente modificados.
        """
        specifications = []
        readingValues = []

        for allowed in allowed_parameters:
            source_specification = orinal_reading_json[specifications_name].get(allowed.code_api)
            if source_specification is None:
                continue

            # Obter valor original
            original_value = float(source_specification["value"])
            
            # Gerar valor sintético (pode ser o original ou modificado)
            synthetic_value = self._generate_synthetic_value(allowed.code, original_value)
            
            # Criar especificação com valor potencialmente modificado
            specifications.append({
                "parameter_code": allowed.code,
                "source_code": allowed.code_api,
                "name": source_specification["name"],
                "value": synthetic_value,  # Valor sintético ao invés do original
                "unit": source_specification["unit"],
            })
            
            # Criar ReadingValue com valor sintético
            readingValues.append(ReadingValue(
                parameter_code=allowed.code,
                parameter_category_code=category_code,
                value=Decimal(str(synthetic_value))
            ))

        if not specifications:
            return None

        return {
            "metadata": metadata,
            "payload": {
                "datetime": orinal_reading_json["datetime"],
                specifications_name: specifications,
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
            built = self.build_demo_document_reading(specifications_name, value, metadata, allowed_parameters, category_code)
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
