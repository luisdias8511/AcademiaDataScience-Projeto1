def validate_parameter(value) -> tuple[bool, Exception | None]:
    try:
        # TODO: validar o valor do parâmetro
        return True, None
    except Exception as error:
        return False, error