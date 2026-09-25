from statistics import mean, median, pstdev, quantiles

from .outliers import identificar_outliers


def calcular_estatisticas(valores: list[float]) -> dict:
    """Calcula estatísticas para uma sequência de valores válidos."""
    if not valores:
        raise ValueError("A lista de valores não pode estar vazia.")

    valores = [float(valor) for valor in valores]

    if len(valores) < 2:
        raise ValueError("São necessários pelo menos dois valores.")

    q1, _, q3 = quantiles(valores, n=4, method="inclusive")

    return {
        "media": mean(valores),
        "mediana": median(valores),
        "desvio_padrao": pstdev(valores),
        "q1": q1,
        "q3": q3,
        **identificar_outliers(valores, q1, q3),
    }