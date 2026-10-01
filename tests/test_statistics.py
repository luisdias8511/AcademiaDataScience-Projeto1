import unittest #importa a ferramenta de testes da bibilteca padrão do python.

from src.analytics.statistics import calcular_estatisticas
#Importa a função

class TestCalcularEstatisticas(unittest.TestCase): #cria classe para agrupar os testes
#unitteste.TestCase oferece métodos como assertEqual e assertRaises (não conheço ambos kkkk)

    def test_calculos_basicos(self): #chama funçao
        resultado = calcular_estatisticas([1, 2, 3, 4])
        #faz a comparação de resultados, se for diferente o teste falha.

        #usei o assertEqual pq diz que pode ter diferença nas casas decimais, ai isso ajusta a precisão no computador
        self.assertEqual(resultado["media"], 2.5)
        self.assertEqual(resultado["mediana"], 2.5)
        self.assertAlmostEqual(resultado["desvio_padrao"], 1.11803398875)
        self.assertEqual(resultado["q1"], 1.75)
        self.assertEqual(resultado["q3"], 3.25)
        self.assertEqual(resultado["iqr"], 1.5)
        self.assertEqual(resultado["outliers"], [])

    def test_identifica_outlier(self): #chama funçao
        resultado = calcular_estatisticas([1, 2, 3, 4, 5, 100])
        #faz a comparação de resultados, se for diferente o teste falha. 
        self.assertEqual(resultado["outliers"], [100.0])

    def test_lista_vazia(self): #chama funçao
        with self.assertRaises(ValueError): #Aqui eu espero que a função produza lista vazia, se não produzir esse erro o teste falha
            calcular_estatisticas([])

    def test_24_temperaturas_simuladas(self):
        temperaturas = [20, 21, 22, 23] * 5 + [20, 21, 22, 40] #simula temperaturas para testes

        self.assertEqual(len(temperaturas), 24)

        resultado = calcular_estatisticas(temperaturas)

        self.assertAlmostEqual(resultado["media"], 533 / 24)
        self.assertEqual(resultado["outliers"], [40.0])

#roda os testes ate o momento se for executar esse arquivo separado (pytest), 
if __name__ == "__main__": 
    unittest.main()