def identificar_outliers(
    valores: list[float], q1: float, q3: float
) -> dict:
    """Identifica valores fora dos limites de 1,5 × IQR."""
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    return {
        "iqr": iqr,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": [
            valor
            for valor in valores
            if valor < limite_inferior or valor > limite_superior
        ],
    }