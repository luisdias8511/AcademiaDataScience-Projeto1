import unittest

from src.analytics.statistics import calcular_estatisticas


class TestCalcularEstatisticas(unittest.TestCase):
    def test_calculos_basicos(self):
        resultado = calcular_estatisticas([1, 2, 3, 4])

        self.assertEqual(resultado["media"], 2.5)
        self.assertEqual(resultado["mediana"], 2.5)
        self.assertAlmostEqual(resultado["desvio_padrao"], 1.11803398875)
        self.assertEqual(resultado["q1"], 1.75)
        self.assertEqual(resultado["q3"], 3.25)
        self.assertEqual(resultado["iqr"], 1.5)
        self.assertEqual(resultado["outliers"], [])

    def test_identifica_outlier(self):
        resultado = calcular_estatisticas([1, 2, 3, 4, 5, 100])
        self.assertEqual(resultado["outliers"], [100.0])

    def test_lista_vazia(self):
        with self.assertRaises(ValueError):
            calcular_estatisticas([])

    def test_24_temperaturas_simuladas(self):
        temperaturas = [20, 21, 22, 23] * 5 + [20, 21, 22, 40]

        self.assertEqual(len(temperaturas), 24)

        resultado = calcular_estatisticas(temperaturas)

        self.assertAlmostEqual(resultado["media"], 533 / 24)
        self.assertEqual(resultado["outliers"], [40.0])


if __name__ == "__main__":
    unittest.main()