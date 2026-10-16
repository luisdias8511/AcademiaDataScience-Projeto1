def validate_contract(document: dict, schema: dict) -> tuple[bool, Exception | None]:
    try:
        # TODO: validar o documento contra o JSON Schema - se o documento não estiver em conformidade, lançar uma exceção especifica
        return True, None
    except Exception as error:
        return False, error