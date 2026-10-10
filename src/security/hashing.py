"""
ANONIMIZAÇÃO IRREVERSÍVEL VIA HASH SHA-256 (requisito 3.2 do PDF - LGPD)
======================================================================
Usada nas CHAVES DE IDENTIFICAÇÃO PESSOAL dos Técnicos e Operadores de Campo
(CPF e Nome Completo). Um hash é uma "impressão digital" do dado:
    - Sempre tem 64 caracteres hexadecimais, independentemente do tamanho da entrada;
    - O mesmo valor de entrada SEMPRE gera o mesmo hash (permite cruzar tabelas e
      encontrar duplicados sem expor o CPF);
    - É IRREVERSÍVEL: a partir do hash não é possível descobrir o CPF original.

Por que usar "SALT"?
    Existem "apenas" ~1 bilhão de CPFs possíveis. Um atacante poderia calcular o
    SHA-256 de todos eles e comparar com os hashes vazados (ataque de dicionário /
    força bruta). Para impedir isso, juntamos ao CPF um texto secreto (o salt,
    guardado no .env como LGPD_HASH_SALT) ANTES de calcular o hash. Sem conhecer o
    salt, o atacante não consegue reproduzir os hashes.

Fluxo:
    "123.456.789-09" -> normaliza -> "12345678909" -> salt + "12345678909" -> SHA-256 -> "a3f1...9c" (64 chars)
"""
import hashlib       # biblioteca padrão do Python que implementa o SHA-256
import os            # leitura da variável LGPD_HASH_SALT
import re            # expressões regulares (usada para remover pontos e traços do CPF)
import unicodedata   # usada para remover acentos dos nomes
from typing import Optional  # Optional[str] = pode ser um texto OU None

from dotenv import load_dotenv  # carrega o arquivo .env

from src.config import logger   # logger estruturado (JSON) do projeto

# Carrega as variáveis do .env (LGPD_HASH_SALT) para o ambiente do processo
load_dotenv()


def _obter_salt() -> bytes:
    """Lê o salt secreto do .env (uso interno deste módulo)."""
    salt = os.getenv("LGPD_HASH_SALT")
    # Sem salt o hash ficaria vulnerável; por isso preferimos FALHAR do que gerar hash inseguro
    if not salt:
        raise RuntimeError("Variável de ambiente LGPD_HASH_SALT não configurada.")
    # O hashlib trabalha com bytes, então convertemos o texto em bytes
    return salt.encode("utf-8")


def normalizar_cpf(cpf: str) -> str:
    """Padroniza o CPF para que formatos diferentes gerem o MESMO hash.

    Ex.: '123.456.789-09', ' 12345678909 ' e '123456789-09' viram todos '12345678909'.
    """
    # re.sub(r"\D", "", ...) -> substitui tudo que NÃO é dígito (\D) por nada, ou seja, remove
    digitos = re.sub(r"\D", "", str(cpf))
    # Um CPF válido sempre tem 11 dígitos; caso contrário o registro é rejeitado (Data Contract)
    if len(digitos) != 11:
        raise ValueError("CPF inválido: deve conter 11 dígitos.")
    return digitos


def normalizar_nome(nome: str) -> str:
    """Padroniza o nome: sem acentos, em MAIÚSCULAS e com espaços simples.

    Ex.: 'João  da silva' -> 'JOAO DA SILVA'
    """
    # 1) normalize("NFKD") separa a letra do acento ("ã" vira "a" + "~")
    # 2) encode("ascii", "ignore") descarta os acentos (caracteres fora da tabela ASCII)
    # 3) decode("ascii") volta para texto
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode("ascii")
    # 4) upper() deixa em maiúsculas; split() + " ".join() remove espaços duplicados/nas pontas
    return " ".join(sem_acento.upper().split())


def hash_sha256(valor: Optional[str]) -> Optional[str]:
    """Calcula o hash SHA-256 (com salt) de qualquer texto. IRREVERSÍVEL."""
    # 1) Valores vazios não geram hash: devolvemos None (campo nulo)
    if valor is None or str(valor).strip() == "":
        return None
    # 2) Passo a passo da linha abaixo:
    #    _obter_salt()                     -> salt secreto em bytes
    #    str(valor).strip().encode("utf-8") -> valor sem espaços nas pontas, em bytes
    #    salt + valor                      -> junta os dois (o salt "embaralha" o resultado)
    #    hashlib.sha256(...)               -> aplica o algoritmo SHA-256
    #    .hexdigest()                      -> devolve o hash como texto hexadecimal de 64 caracteres
    return hashlib.sha256(_obter_salt() + str(valor).strip().encode("utf-8")).hexdigest()


def anonimizar_cpf(cpf: Optional[str]) -> Optional[str]:
    """Anonimiza o CPF: normaliza (só dígitos) e aplica o hash SHA-256 com salt."""
    if cpf is None or str(cpf).strip() == "":
        return None
    return hash_sha256(normalizar_cpf(cpf))


def anonimizar_nome(nome: Optional[str]) -> Optional[str]:
    """Anonimiza o nome: normaliza (sem acento, maiúsculo) e aplica o hash SHA-256 com salt."""
    if nome is None or str(nome).strip() == "":
        return None
    return hash_sha256(normalizar_nome(nome))


def verificar_hash(valor: str, hash_esperado: str, tipo: str = "cpf") -> bool:
    """Confere se um valor em claro corresponde a um hash já armazenado.

    Como o hash não pode ser revertido, a única forma de "conferir" é calcular o hash do
    valor informado e comparar com o hash guardado. Ex.: localizar um operador pelo CPF.
    """
    # Dicionário que escolhe a função correta conforme o tipo de dado
    funcoes = {"cpf": anonimizar_cpf, "nome": anonimizar_nome, "generico": hash_sha256}
    try:
        # Calcula o hash do valor informado e compara com o esperado (True = corresponde)
        return funcoes[tipo](valor) == hash_esperado
    except ValueError:
        # CPF inválido: registra um aviso SEM o valor (para não expor dado pessoal) e devolve False
        logger.warning("Valor inválido informado para verificação de hash", extra={"tipo": tipo})
        return False
