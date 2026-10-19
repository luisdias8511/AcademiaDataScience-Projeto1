"""Testes do fluxo de cadastro/consulta de usuários com LGPD (sem banco de dados).

Executar: python -m pytest tests/test_lgpd_user.py -v
"""
import pytest
from cryptography.fernet import Fernet

from src.models.user import NewUser
from src.security import lgpd
from src.security.password_hashing import verificar_senha
from src.services import user_service


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("FERNET_KEY", Fernet.generate_key().decode())
    monkeypatch.setenv("LGPD_HASH_SALT", "salt-de-teste")


class FakeRepo:
    """Substitui o UserRepository (SQL Server) em memória."""
    def __init__(self):
        self.rows = []
    def exists_username(self, username):
        return any(r["username"] == username for r in self.rows)
    def exists_cpf_hash(self, cpf_hash):
        return any(r["cpf_hash"] == cpf_hash for r in self.rows)
    def insert_user(self, protegido):
        self.rows.append({**protegido, "id_usuario": len(self.rows) + 1})
        return len(self.rows)
    def list_users(self):
        return self.rows


def _user(**kw):
    base = dict(username="maria.souza", full_name="Maria  Souza", password="Senha@123",
                email="Maria@Empresa.com", cpf="529.982.247-25", phone="(11) 98888-7777",
                atribution="Técnica")
    base.update(kw)
    return NewUser(**base)


def test_cadastro_grava_somente_dados_protegidos():
    repo = FakeRepo()
    assert user_service.register_user(_user(), repo) == []
    gravado = repo.rows[0]
    texto = str(gravado)
    for valor_aberto in ("Maria Souza", "52998224725", "529.982.247-25", "maria@empresa.com", "98888", "Senha@123"):
        assert valor_aberto not in texto
    assert len(gravado["cpf_hash"]) == 64 and len(gravado["nome_completo_hash"]) == 64
    assert gravado["nome_completo_cripto"].startswith("gAAAA")
    assert verificar_senha("Senha@123", gravado["password_hash"])


def test_descriptografa_campos_reversiveis():
    repo = FakeRepo()
    user_service.register_user(_user(), repo)
    aberto = user_service.decrypt_user(repo.list_users()[0])
    assert aberto == {"full_name": "Maria Souza", "email": "maria@empresa.com", "phone": "(11) 98888-7777"}
    assert "cpf" not in aberto  # CPF é irreversível


def test_conferir_cpf_pelo_hash():
    repo = FakeRepo()
    user_service.register_user(_user(), repo)


def test_chave_errada_gera_erro_amigavel(monkeypatch):
    repo = FakeRepo()
    user_service.register_user(_user(), repo)
    monkeypatch.setenv("FERNET_KEY", Fernet.generate_key().decode())
    with pytest.raises(ValueError, match="FERNET_KEY"):
        user_service.decrypt_user(repo.rows[0])


def test_operador_sem_senha_mantem_comportamento():
    protegido = lgpd.proteger_operador({"id_operador": 1, "cpf": "529.982.247-25",
                                        "nome_completo": "Maria Souza", "email": "m@e.com"})
    assert "password_hash" not in protegido and "cpf" not in protegido
