from statistics import mean, median, pstdev, quantiles
# traz as funções prontas da bibliotexca padrão do python: Mean(Média); Median (Mediana); PSTDEV(desvio padrão populacional, o "P" significa population); Quantiles (Calcula os quartis)

from .outliers import identificar_outliers
# aqui ta importando a função do arquivo outliers.py, (o "." é = procure dentro do mesmo pacote analytics)

def calcular_estatisticas(valores: list[float]) -> dict: 
# inicia uma definição de função (DEF); Valores seriam o parâmetro de entrada (exe: lista de temperaturas); o list[float] indica que se espera uma lista de números;  o comando -> Dict: fala que vai devolver um dicionário
#     
    #Calcula estatísticas para uma sequência de valores válidos.
    if not valores:
        raise ValueError("A lista de valores não pode estar vazia.") #se a lista estiver vazia, retorna erro

    valores = [float(valor) for valor in valores]

    if len(valores) < 2:
        raise ValueError("São necessários pelo menos dois valores.") #se não houver 2 elementos, erro

    q1, _, q3 = quantiles(valores, n=4, method="inclusive")
    #no caso por partes: q1, _, q3 = q1 e q3 aguardam o primeiro e terceiro
    # _,: seria referente ao q2 (mediana), mas mediana ta calcula separadamente
    # method="incluse" - define qual a regra de caluclo dos quartis sera usada

    return {
        #devolve os valores ao arquivo que chamaou a função, aqui, nosso resultado é um dicionario.
        "media": mean(valores),
        "mediana": median(valores),
        "desvio_padrao": pstdev(valores),
        "q1": q1,
        "q3": q3,
        **identificar_outliers(valores, q1, q3),
    }