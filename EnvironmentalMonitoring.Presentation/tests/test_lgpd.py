"""Testes de LGPD: hash SHA-256, criptografia reversível e logs estruturados.

Executar: python -m pytest tests/test_lgpd.py -v
"""

import json
import logging

import pandas as pd
import pytest
from cryptography.fernet import Fernet, InvalidToken

from src.security import crypto, hashing, lgpd
from src.security.structured_logging import JsonFormatter


# autouse=True -> esta fixture roda automaticamente antes de CADA teste deste arquivo.
# monkeypatch.setenv cria variáveis de ambiente temporárias (desfeitas ao fim do teste),
# assim os testes não dependem do .env real nem usam as chaves de produção.
@pytest.fixture(autouse=True)
def segredos(monkeypatch):
    monkeypatch.setenv("LGPD_HASH_SALT", "salt-de-teste")
    monkeypatch.setenv("FERNET_KEY", Fernet.generate_key().decode())


# ----- Hash SHA-256 (anonimização irreversível) -----
class TestHashing:
    def test_cpf_gera_hash_sha256_hex(self):
        resultado = hashing.anonimizar_cpf("123.456.789-09")
        assert len(resultado) == 64
        assert "12345678909" not in resultado

    def test_cpf_normalizado_gera_mesmo_hash(self):
        assert hashing.anonimizar_cpf("123.456.789-09") == hashing.anonimizar_cpf(" 12345678909 ")

    def test_nome_normalizado_gera_mesmo_hash(self):
        assert hashing.anonimizar_nome(" João  da Silva ") == hashing.anonimizar_nome("JOAO DA SILVA")

    def test_salt_altera_hash(self, monkeypatch):
        h1 = hashing.anonimizar_cpf("12345678909")
        monkeypatch.setenv("LGPD_HASH_SALT", "outro-salt")
        assert hashing.anonimizar_cpf("12345678909") != h1

    def test_cpf_invalido(self):
        with pytest.raises(ValueError):
            hashing.anonimizar_cpf("123")

    def test_vazio_retorna_none(self):
        assert hashing.anonimizar_cpf("") is None
        assert hashing.anonimizar_nome(None) is None

    def test_sem_salt_falha(self, monkeypatch):
        monkeypatch.delenv("LGPD_HASH_SALT")
        with pytest.raises(RuntimeError):
            hashing.anonimizar_cpf("12345678909")

    def test_verificar_hash(self):
        h = hashing.anonimizar_cpf("12345678909")
        assert hashing.verificar_hash("123.456.789-09", h)
        assert not hashing.verificar_hash("98765432100", h)


# ----- Criptografia reversível (Fernet) -----
class TestCrypto:
    def test_ida_e_volta(self):
        token = crypto.criptografar("tecnico@empresa.com")
        assert token != "tecnico@empresa.com"
        assert crypto.descriptografar(token) == "tecnico@empresa.com"

    def test_chave_errada_falha(self):
        token = crypto.criptografar("dado")
        with pytest.raises(InvalidToken):
            crypto.descriptografar(token, chave=crypto.gerar_chave())

    def test_vazio_retorna_none(self):
        assert crypto.criptografar(None) is None
        assert crypto.descriptografar("") is None


# ----- Política LGPD aplicada ao cadastro de Operadores -----
class TestLgpdOperadores:
    # Operador fictício usado em todos os testes da classe
    operador = {
        "id_operador": 1,
        "cpf": "123.456.789-09",
        "nome_completo": "Maria Souza",
        "email": "maria@empresa.com",
        "telefone": "11999990000",
        "funcao": "Técnica de Campo",
    }

    def test_remove_dados_em_claro(self):
        protegido = lgpd.proteger_operador(self.operador)
        for campo in ("cpf", "nome_completo", "email", "telefone"):
            assert campo not in protegido
        assert protegido["funcao"] == "Técnica de Campo"
        assert "123.456.789-09" not in json.dumps(protegido)

    def test_recupera_contato(self):
        protegido = lgpd.proteger_operador(self.operador)
        contato = lgpd.recuperar_contato(protegido)
        assert contato["email"] == "maria@empresa.com"
        assert contato["nome_completo"] == "Maria Souza"

    def test_rejeita_cpf_invalido_sem_logar_dado(self, caplog):
        invalido = {**self.operador, "cpf": "999"}  # cópia do operador com CPF inválido
        # caplog captura os logs emitidos, para conferirmos que o CPF não vazou no log
        with caplog.at_level(logging.WARNING):
            resultado = lgpd.proteger_operadores([self.operador, invalido])
        assert len(resultado) == 1
        assert "999" not in caplog.text

    def test_dataframe(self):
        df = lgpd.proteger_operadores_df(pd.DataFrame([self.operador]))
        assert {"cpf_hash", "nome_completo_hash", "email_cripto"} <= set(df.columns)
        assert "cpf" not in df.columns


# ----- Logs estruturados (JSON) -----
class TestStructuredLogging:
    def test_formato_json(self):
        # Cria um registro de log "artificial" com um campo extra (operador_id)
        # e verifica se o formatador gera um JSON com os campos obrigatórios.
        record = logging.makeLogRecord(
            {"name": "x", "levelname": "WARNING", "levelno": logging.WARNING, "msg": "teste", "operador_id": 7}
        )
        payload = json.loads(JsonFormatter().format(record))
        assert payload["level"] == "WARNING"
        assert payload["message"] == "teste"
        assert payload["operador_id"] == 7
        assert "timestamp" in payload
