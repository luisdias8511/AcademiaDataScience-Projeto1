"""Validação do contrato Bronze, sem acesso a banco ou armazenamento."""

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


class ContractValidationError(Exception):
    """Reúne todas as violações encontradas no documento."""

    def __init__(self, errors: list[ValidationError]) -> None:
        self.errors = tuple(errors)
        super().__init__(f"Documento rejeitado: {len(errors)} erro(s) de contrato.")


def validate_contract(
    document: dict,
    schema: dict,
) -> tuple[bool, Exception | None]:
    """Retorna aprovação e erro; falhas no schema são propagadas.

    Não modifica o documento e não grava logs ou arquivos.
    O chamador deve impedir o encaminhamento do documento rejeitado.
    """
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()
    if "date-time" not in checker.checkers:
        raise RuntimeError(
            "Validação de datas indisponível. Instale jsonschema[format]."
        )
    validator = Draft202012Validator(schema, format_checker=checker)

    try:
        errors = list(validator.iter_errors(document))
        if errors:
            raise ContractValidationError(errors)
        return True, None
    except ContractValidationError as error:
        return False, error


class _JsonInputViolation(ValueError):
    """Erro de entrada JSON sem armazenar o conteúdo recebido."""

    def __init__(self, rule: str) -> None:
        self.rule = rule
        super().__init__(rule)


def _unique_json_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _JsonInputViolation("json_duplicate_field")
        result[key] = value
    return result


def _reject_json_constant(value: str):
    raise _JsonInputViolation("json_nonfinite_number")


def _finite_json_float(value: str) -> float:
    import math

    number = float(value)
    if not math.isfinite(number):
        raise _JsonInputViolation("json_nonfinite_number")
    return number


def validate_json_contract(
    text: str,
    schema: dict,
) -> tuple[bool, dict | None, Exception | None]:
    """Converte texto JSON e aplica o contrato sem devolver dados rejeitados.

    Retorna (True, document, None) ou (False, None, error).
    Aceita somente texto. Falhas no schema ou de programação são propagadas.
    Rejeita chaves repetidas e números não finitos, sem corrigir a entrada.
    """
    import json

    if not isinstance(text, str):
        raise TypeError("A entrada deve ser um texto JSON.")
    Draft202012Validator.check_schema(schema)

    try:
        document = json.loads(
            text,
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
            parse_float=_finite_json_float,
        )
    except (json.JSONDecodeError, _JsonInputViolation) as source_error:
        rule = (
            "json_syntax" if isinstance(source_error, json.JSONDecodeError)
            else source_error.rule
        )
        violation = ValidationError(
            "Entrada incompatível com o formato JSON exigido.",
            validator=rule,
        )
        return False, None, ContractValidationError([violation])

    if not isinstance(document, dict):
        violation = ValidationError(
            "A raiz do documento deve ser um objeto JSON.",
            validator="json_root_type",
        )
        return False, None, ContractValidationError([violation])

    approved, error = validate_contract(document, schema)
    if not approved:
        return False, None, error
    return True, document, None
