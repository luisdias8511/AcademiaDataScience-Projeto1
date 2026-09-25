import unittest

from src.analytics.outliers import identificar_outliers


class TestIdentificarOutliers(unittest.TestCase):
    def test_identifica_outliers_dos_dois_lados(self):
        resultado = identificar_outliers(
            valores=[-3.0, -2.0, 2.0, 6.0, 7.0],
            q1=1.0,
            q3=3.0,
        )

        self.assertEqual(resultado["iqr"], 2.0)
        self.assertEqual(resultado["limite_inferior"], -2.0)
        self.assertEqual(resultado["limite_superior"], 6.0)
        self.assertEqual(resultado["outliers"], [-3.0, 7.0])

    def test_valores_iguais_aos_limites_nao_sao_outliers(self):
        resultado = identificar_outliers(
            valores=[-2.0, 2.0, 6.0],
            q1=1.0,
            q3=3.0,
        )

        self.assertEqual(resultado["outliers"], [])


if __name__ == "__main__":
    unittest.main()