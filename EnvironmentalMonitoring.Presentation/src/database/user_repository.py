"""Repositório de usuários (tabela Users)."""
from typing import Any, Dict, List
from src.database.reading_repository import ReadingRepository
# Colunas lidas na tela de consulta. PasswordHash NÃO é lida: a tela não precisa dela.
# ATENÇÃO: a ORDEM aqui precisa ser a mesma dos índices row[0], row[1]... em list_users().
_COLUNAS_CONSULTA = "Id, Username, PasswordHash, Cpf, FullName, Email, Phone, Atribution"
class UserRepository:
    """Acesso ao banco para a tabela Users.
    IMPORTANTE: este repositório só recebe/devolve dados JÁ PROTEGIDOS pela política
    LGPD (src/security/lgpd.py). Nenhum dado pessoal em texto aberto chega ao banco.
    Mapeamento entre as chaves geradas pelo lgpd.py e as colunas da tabela Users:
        password_hash        -> PasswordHash (PBKDF2, irreversível)
        cpf_hash             -> Cpf          (SHA-256, irreversível)
        nome_completo_cripto -> FullName     (Fernet, reversível)
        email_cripto         -> Email        (Fernet, reversível)
        telefone_cripto      -> Phone        (Fernet, reversível)
    """
    def __init__(self) -> None:
        self.db = ReadingRepository()  # reaproveita a conexão SQL Server já configurada
    # ------------------------------------------------------------------ escrita
    def insert_user(self, protegido: Dict[str, Any]) -> int:
        """Insere um usuário (já protegido) e devolve o Id gerado."""
        #  7 colunas -> 7 marcadores "?"
        query = """
            INSERT INTO Users (Username, PasswordHash, Cpf, FullName,
                                Email, Phone, Atribution)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db._connect()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                query,
                protegido["username"],
                protegido["password_hash"],
                protegido["cpf_hash"],              # CPF    -> hash SHA-256
                protegido["nome_completo_cripto"],  # Nome   -> criptografado
                protegido["email_cripto"],          # E-mail -> criptografado
                protegido.get("telefone_cripto"),   # telefone é opcional (pode ser None)
                protegido["atribution"],
            )
            user_id = int(cursor.fetchone()[0])
            self.db.conn.commit()
            return user_id
        except Exception:
            self.db.conn.rollback()
            raise
        finally:
            self.db._disconnect()

    # ------------------------------------------------------------------ leitura
    def exists_username(self, username: str) -> bool:
        """Verifica se o nome de usuário já está em uso."""
        return self._exists("SELECT 1 FROM Users WHERE Username = ?", username)

    def list_users(self) -> List[Dict[str, Any]]:
        """Devolve os usuários EXATAMENTE como estão gravados (hash/criptografados).

        As chaves seguem o padrão do lgpd.py (<campo>_hash / <campo>_cripto), para que
        o registro possa ser passado diretamente para lgpd.recuperar_usuario().
        """
        self.db._connect()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(f"SELECT {_COLUNAS_CONSULTA} FROM Users ORDER BY Id")
            return [
                                {
                    "id_usuario": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "cpf_hash": row[3],
                    "nome_completo_cripto": row[4],
                    "email_cripto": row[5],
                    "telefone_cripto": row[6],
                    "atribution": row[7],
                }
                for row in cursor.fetchall()
            ]
        finally:
            self.db._disconnect()

    # ------------------------------------------------------------------ interno
    def _exists(self, query: str, *params: Any) -> bool:
        self.db._connect()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(query, *params)
            return cursor.fetchone() is not None
        finally:
            self.db._disconnect()



    # ------------------------------------------------------------------ login
    def get_login_data(self, username: str) -> Dict[str, Any] | None:
        """Busca os dados necessários para o login (sem nenhum dado pessoal).

        Retorna None se o usuário não existir.
        A senha NÃO é comparada no banco: o hash PBKDF2 é conferido no serviço.
        """
        self.db._connect()
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT Id, Username, PasswordHash, Atribution FROM Users WHERE Username = ?",
                username,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return {
                "id_usuario": row[0],     # Id
                "username": row[1],       # Username
                "password_hash": row[2],  # PasswordHash
                "atribution": row[3],     # Atribution
            }
        finally:
            self.db._disconnect()
