import os
from getpass import getpass
import pyodbc
# Conexão com o banco de dados EnvironmentalMonitoring usando pyodbc para testar a conexão e consultar as primeiras 10 linhas da tabela Stations

SERVER = "sql-aca-data-science-environment-monitoring.database.windows.net"
DATABASE = "EnvironmentalMonitoring"
USERNAME = "environment_api"
PASSWORD = os.getenv("DB_PASSWORD") or getpass("Usuário: environment_api Senha: ")

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

try:
    with pyodbc.connect(connection_string) as conn:
        print("✓ Conexão estabelecida com sucesso.\n")
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 10 * FROM Parameters")

        columns = [col[0] for col in cursor.description]
        print(" | ".join(columns))
        print("-" * 80)
        for row in cursor.fetchall():
            print(" | ".join(str(value) for value in row))
except pyodbc.Error as e:
    print(f"❌ Falha na conexão ou consulta: {e}")