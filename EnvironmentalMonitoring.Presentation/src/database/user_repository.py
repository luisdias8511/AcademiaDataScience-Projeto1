"""Repositório de usuários (tabela Users)."""

from src.database.reading_repository import ReadingRepository
from src.models.user import NewUser


class UserRepository:
    """Acesso ao banco para a tabela Users."""

    def insert_user(self, user: NewUser) -> None:
        """Insere um usuário na tabela Users."""
        # TODO: gerar o hash da senha. Por enquanto, a senha é gravada sem hash.
        password_hash = user.password

        query = """
            INSERT INTO Users (Username, PasswordHash, Email, Cpf, Phone, Atribution)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        db = ReadingRepository()
        db._connect()
        try:
            cursor = db.conn.cursor()
            cursor.execute(
                query,
                user.username,
                password_hash,
                user.email,
                user.cpf,
                user.phone,
                user.atribution,
            )
            db.conn.commit()
        finally:
            db._disconnect()
