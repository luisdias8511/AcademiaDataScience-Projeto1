"""Demonstração local: dados simulados, sem Azure, banco ou arquivos de saída.

Execute da pasta EnvironmentalMonitoring.Presentation:
    python examples/demo_data_quality.py
Carrega módulos diretamente para evitar inicializar serviços via src/__init__.py.
"""
import importlib.util
import json
import logging
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(
        name + "_demo", ROOT / f"src/processing/{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MemoryStorage:
    """Imita upload_json; mantém os eventos somente na memória."""

    def __init__(self):
        self.files = {}

    def upload_json(self, blob_name, content):
        self.files[blob_name] = deepcopy(content)


class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


def main():
    validator = load_module("bronze_contract_validator")
    quality = load_module("data_quality")
    audit = load_module("contract_audit")
    persistence = load_module("contract_audit_storage")
    example_path = ROOT / "contracts/examples/water-bronze-valid.json"
    schema_path = ROOT / "contracts/schemas/water-bronze.schema.json"
    base = json.loads(example_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    base["payload"]["datetime"] = "2026-10-14T00:00:00Z"
    base["metadata"]["ingestion_datetime"] = "2026-10-14T00:10:00Z"

    def case(name, timestamp, parameter=None, value=None):
        doc = deepcopy(base)
        doc["payload"]["datetime"] = timestamp
        if parameter:
            next(item for item in doc["payload"]["pollutants"]
                 if item["parameter_code"] == parameter)["value"] = value
        return name, doc

    cases = [
        case("Leitura válida", "2026-10-14T00:00:00Z"),
        case("pH inválido (18)", "2026-10-14T00:01:00Z", "PH", 18),
        case("Repetição da primeira leitura", "2026-10-14T00:00:00Z"),
        case("Turbidez negativa", "2026-10-14T00:02:00Z", "TURBIDITY", -1),
        case("Futuro: 5 minutos e 1 segundo", "2026-10-14T00:15:01Z"),
        case("Atraso de 2 horas", "2026-10-13T22:10:00Z"),
    ]
    documents = [document for _, document in cases]
    for name, document in cases:
        approved, error = validator.validate_contract(document, schema)
        if not approved:
            raise RuntimeError(f"Exemplo {name} falhou no contrato: {error}")

    # Uma hora é apenas o prazo DESTA demonstração, não um padrão do projeto.
    report = quality.assess_data_quality(
        documents, "water", mode="realtime", maximum_delay=timedelta(hours=1)
    )
    storage = MemoryStorage()
    handler = MemoryLogHandler()
    logger = logging.Logger("quality-demo", level=logging.INFO)
    logger.addHandler(handler)
    execution_id = "demo-" + str(uuid4())
    all_events = []
    for (name, document), result in zip(cases, report["results"]):
        status = "APROVADA" if result["approved"] else "REJEITADA INTEIRA"
        print(f"\n{name}: {status}")
        for issue in result["errors"]:
            print(f"  ERRO: {issue['error_code']} | {issue['field_path']}")
        for issue in result["warnings"]:
            print(f"  ALERTA: {issue['error_code']} | {issue['reason']}")
        events = quality.build_data_quality_audit_events(
            document, result, execution_id=execution_id,
            document_id=f"demo-document-{result['document_index']}", category="water",
        )
        audit.log_contract_audit_events(events, logger)
        all_events.extend(events)

    paths = persistence.save_contract_audit_events(all_events, storage, logger)
    summary = report["summary"]
    print("\nRESUMO DA DEMONSTRAÇÃO")
    print(f"Recebidos: {summary['received_documents']}")
    print(f"Aprovados: {summary['approved_documents']}")
    print(f"Rejeitados: {summary['rejected_documents']}")
    print(f"Documentos com alertas: {summary['documents_with_warnings']}")
    print(f"Eventos de rejeição: {len(all_events)}")
    print(f"Arquivos simulados em memória: {len(paths)}")
    print("\nLIMITES NÃO CONFIGURADOS (não significam verificações aprovadas)")
    pending = sorted({rule for result in report["results"] for rule in result["unchecked_rules"]})
    for rule in pending:
        print(f"  {rule}")
    if all_events:
        print("\nEXEMPLO DE EVENTO DE AUDITORIA")
        print(json.dumps(all_events[0], ensure_ascii=False, indent=2))
    print("\nSomente simulação: nenhum arquivo enviado ao Azure ou gravado em disco.")


if __name__ == "__main__":
    main()
