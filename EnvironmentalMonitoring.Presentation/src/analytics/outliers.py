#  inicia uma definição de função (DEF); no nosso caso recebe os valores eos quartis Q1 e Q3 que foram calculados por stastitics.py. Ela vai devolver uma dicionario com os valores identificados como outliers.

def identificar_outliers(
    valores: list[float], q1: float, q3: float
) -> dict:
    """Identifica valores fora dos limites de 1,5 × IQR."""
    iqr = q3 - q1 # é a distancia dentre o terceio e o primeiro quartil
    limite_inferior = q1 - 1.5 * iqr #calculo de limite inferior
    limite_superior = q3 + 1.5 * iqr #calculo de limite superior

    # Aqui devolve o IQR, os limites e uma lista de outliers, percorrendo os itens no valores
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