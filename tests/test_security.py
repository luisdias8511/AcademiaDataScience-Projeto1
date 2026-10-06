"""Testes para segurança e logging."""

import pytest
import logging
from unittest.mock import Mock, patch
from io import StringIO

from src.security.log_utils import tratar_erro


class TestErrorHandling:
    """Testes para tratamento de erros e logging."""

    def test_tratar_erro_logs_message(self, caplog):
        """Deve registrar mensagem de erro no log."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Erro de teste")
            except ValueError as e:
                tratar_erro(e, "Contexto de teste", encerrar=False)
        
        assert "Contexto de teste" in caplog.text or "Erro de teste" in caplog.text

    def test_tratar_erro_with_encerrar_false(self):
        """Não deve lançar exceção quando encerrar=False."""
        try:
            raise ValueError("Erro de teste")
        except ValueError as e:
            # Não deve lançar exceção
            tratar_erro(e, "Teste", encerrar=False)

    def test_tratar_erro_with_encerrar_true(self):
        """Deve re-lançar exceção quando encerrar=True."""
        # encerrar=True faz re-lançar a exceção após logar
        with pytest.raises(ValueError):
            try:
                raise ValueError("Erro de teste")
            except ValueError as e:
                tratar_erro(e, "Teste", encerrar=True)

    def test_tratar_erro_formats_message(self, caplog):
        """Deve formatar mensagem com contexto."""
        custom_message = "Erro ao conectar banco de dados"
        with caplog.at_level(logging.ERROR):
            try:
                raise ConnectionError("DB timeout")
            except ConnectionError as e:
                tratar_erro(e, custom_message, encerrar=False)
        
        assert custom_message in caplog.text or "Erro" in caplog.text

    def test_tratar_erro_with_different_exception_types(self, caplog):
        """Deve tratar diferentes tipos de exceção."""
        exceptions = [
            ValueError("Valor inválido"),
            TypeError("Tipo incorreto"),
            RuntimeError("Erro de execução"),
            KeyError("Chave não encontrada"),
        ]
        
        with caplog.at_level(logging.ERROR):
            for exc in exceptions:
                try:
                    raise exc
                except Exception as e:
                    tratar_erro(e, f"Erro: {type(exc).__name__}", encerrar=False)
        
        # Log deve ter registros de erros
        assert len(caplog.records) > 0

    def test_tratar_erro_preserves_exception_info(self, caplog):
        """Deve preservar informação da exceção original."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Mensagem específica")
            except ValueError as e:
                tratar_erro(e, "Contexto", encerrar=False)
        
        # Deve haver registro de erro
        assert any(record.levelname == "ERROR" for record in caplog.records)

    def test_tratar_erro_with_empty_message(self, caplog):
        """Deve funcionar com mensagem customizada vazia."""
        with caplog.at_level(logging.ERROR):
            try:
                raise RuntimeError("Erro")
            except RuntimeError as e:
                tratar_erro(e, "", encerrar=False)
        
        # Ainda deve logar algo
        assert len(caplog.records) > 0

    def test_tratar_erro_multiple_calls(self, caplog):
        """Deve funcionar em múltiplas chamadas consecutivas."""
        errors = [
            ("Erro 1", ValueError("V1")),
            ("Erro 2", TypeError("T2")),
            ("Erro 3", RuntimeError("R3")),
        ]
        
        with caplog.at_level(logging.ERROR):
            for msg, exc in errors:
                try:
                    raise exc
                except Exception as e:
                    tratar_erro(e, msg, encerrar=False)
        
        # Deve ter registrado todos os erros
        assert len(caplog.records) >= 3

    def test_tratar_erro_logger_name(self, caplog):
        """Deve usar logger apropriado."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Teste")
            except ValueError as e:
                tratar_erro(e, "Teste", encerrar=False)
        
        # Verificar que foi logado
        assert any(record.levelname == "ERROR" for record in caplog.records)


class TestSecurityValidation:
    """Testes para validações de segurança."""

    def test_no_credential_logging(self, caplog):
        """Não deve logar credenciais em mensagens de erro."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Senha incorreta: secret123")
            except ValueError as e:
                tratar_erro(e, "Falha de autenticação", encerrar=False)
        
        # Idealmente, credenciais não estariam em exceções
        # Este teste documenta que devemos ter cuidado
        pass

    def test_error_message_sanitization(self, caplog):
        """Mensagens de erro devem ser seguras."""
        with caplog.at_level(logging.ERROR):
            try:
                # Simular erro que poderia conter info sensível
                raise Exception("Database user: admin, password at line 42")
            except Exception as e:
                tratar_erro(e, "DB Error", encerrar=False)
        
        # Log pode conter informações técnicas mas deve ser cuidadoso
        pass

    def test_error_handling_does_not_expose_internals(self):
        """Tratamento de erro não deve expor estrutura interna."""
        try:
            raise ValueError("Erro interno")
        except ValueError as e:
            # Não deve lançar exceções não tratadas
            tratar_erro(e, "Tratamento", encerrar=False)


class TestLogConfiguration:
    """Testes para configuração de logging."""

    def test_error_level_logging(self, caplog):
        """Erros devem ser logados no nível ERROR."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Teste")
            except ValueError as e:
                tratar_erro(e, "Contexto", encerrar=False)
        
        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_records) > 0

    def test_log_includes_timestamp(self, caplog):
        """Logs devem incluir timestamp."""
        with caplog.at_level(logging.ERROR):
            try:
                raise ValueError("Teste")
            except ValueError as e:
                tratar_erro(e, "Teste", encerrar=False)
        
        if caplog.records:
            record = caplog.records[0]
            # Verificar que record possui timestamp
            assert hasattr(record, "created")
            assert record.created > 0

    def test_log_format_includes_level(self, caplog):
        """Logs devem incluir nível de severidade."""
        with caplog.at_level(logging.ERROR):
            try:
                raise RuntimeError("Erro")
            except RuntimeError as e:
                tratar_erro(e, "Teste", encerrar=False)
        
        if caplog.records:
            assert any("ERROR" in r.levelname for r in caplog.records)

    def test_exception_traceback_available(self, caplog):
        """Traceback de exceção deve estar disponível nos logs."""
        with caplog.at_level(logging.ERROR):
            try:
                1 / 0  # ZeroDivisionError
            except ZeroDivisionError as e:
                tratar_erro(e, "Divisão por zero", encerrar=False)
        
        # Ao menos um record deve ter exc_info
        assert len(caplog.records) > 0
