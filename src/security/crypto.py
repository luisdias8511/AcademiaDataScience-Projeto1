"""
CRIPTOGRAFIA REVERSÍVEL (requisito 3.2 do PDF - LGPD)
=====================================================
Usada para dados pessoais que PRECISAM ser recuperados no futuro (ex.: e-mail e
telefone do operador, para contato). Diferente do hash, aqui é possível voltar ao
valor original - mas SOMENTE quem possui a chave secreta (FERNET_KEY) consegue.

Algoritmo: Fernet (biblioteca `cryptography`)
    - Criptografa com AES-128 (modo CBC)
    - Garante integridade com HMAC-SHA256 (se alguém alterar o texto cifrado, a
      descriptografia falha em vez de devolver um valor corrompido)
    - Cada criptografia gera um resultado diferente, mesmo para o mesmo valor
      (usa um vetor aleatório + data/hora), o que dificulta ataques por comparação.

Fluxo:
    "maria@empresa.com" --criptografar()--> "gAAAAABq..." --descriptografar()--> "maria@empresa.com"
"""
import hashlib
import os                         # leitura da variável FERNET_KEY
from typing import Optional       # Optional[str] = pode ser um texto OU None

from cryptography.fernet import Fernet, InvalidToken  # Fernet = algoritmo; InvalidToken = erro de token inválido
from dotenv import load_dotenv                        # carrega o arquivo .env

from src.config import logger     # logger estruturado (JSON) do projeto

# Carrega as variáveis do .env (FERNET_KEY) para o ambiente do processo
load_dotenv()


def gerar_chave() -> str:
    """
    Gera uma NOVA chave Fernet aleatória.

    Use apenas uma vez, para criar a chave, e guarde o resultado no .env como FERNET_KEY.
    ATENÇÃO: se a chave for perdida ou trocada, os dados já criptografados não poderão
    mais ser lidos.
    """
    # generate_key() retorna bytes; .decode("utf-8") converte para texto (str)
    return Fernet.generate_key().decode("utf-8")



def _obter_cipher(chave: Optional[str] = None) -> Fernet:
    """Cria o objeto Fernet (o "cofre") que faz a criptografia/descriptografia.

    O "_" no início do nome indica que a função é de uso interno deste módulo.
    """
    # 1) Usa a chave recebida por parâmetro; se não vier nenhuma, lê a FERNET_KEY do .env
    chave = chave or os.getenv("FERNET_KEY")

    print(f"Usando chave Fernet: {chave}")

    # 2) Sem chave não há como criptografar: interrompe com mensagem clara
    if not chave:
        raise RuntimeError("Variável de ambiente FERNET_KEY não configurada.")

    # 3) O Fernet espera a chave em bytes; se ela veio como texto, convertemos com encode()
    return Fernet(chave.encode("utf-8") if isinstance(chave, str) else chave)



def anonimizar(valorC: Optional[str]) -> Optional[str]:
    """Gera um hash SHA-256, tornando-o irreversivelmente anônimo."""
    if not valorC:  # verificação se o parametro está vazio; se estiver o retorno é None;
        return None
    return hashlib.sha256(valorC.strip().encode('utf-8')).hexdigest()  # e se não estiver vazio



def criptografar(valor: Optional[str], chave: Optional[str] = None) -> Optional[str]:
    """Criptografa um texto e devolve o resultado cifrado (também em texto)."""
    # 1) Valores vazios não são criptografados: devolvemos None (campo nulo no banco)
    if valor is None or str(valor) == "":
        return None

    # 2) Passo a passo da linha abaixo:
    #    str(valor).encode("utf-8") -> converte o texto em bytes (o Fernet trabalha com bytes)
    #    .encrypt(...)              -> criptografa os bytes usando a chave
    #    .decode("utf-8")           -> converte o resultado de volta em texto, para gravar no banco/arquivo
    return _obter_cipher(chave).encrypt(str(valor).encode("utf-8")).decode("utf-8")


def descriptografar(token: Optional[str], chave: Optional[str] = None) -> Optional[str]:
    """Recupera o valor original a partir do texto criptografado ("token")."""
    # 1) Nada para descriptografar: devolve None
    if token is None or str(token) == "":
        return None

    try:
        # 2) Caminho inverso da função criptografar():
        #    texto -> bytes -> .decrypt() -> bytes originais -> texto original
        return _obter_cipher(chave).decrypt(str(token).encode("utf-8")).decode("utf-8")

    
    except InvalidToken:
        # 3) Acontece quando a chave está errada ou o token foi alterado/corrompido.
        #    SEGURANÇA: não colocamos o token na mensagem para não vazar dado sensível no log.
        logger.error("Falha ao descriptografar: token inválido ou chave incorreta")
        # 4) Repassa o erro para quem chamou decidir o que fazer
        raise
