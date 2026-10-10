"""
REGRAS DE LGPD PARA O CADASTRO DE TÉCNICOS E OPERADORES DE CAMPO (requisito 3.2 do PDF)
======================================================================================
Este módulo junta as duas técnicas (hash e criptografia) e define QUAL tratamento
cada campo pessoal recebe antes de ser gravado na camada Silver / tabela Operadores.

Política adotada:
| Campo          | Tratamento                         | Por quê?                                        |
|----------------|------------------------------------|-------------------------------------------------|
| cpf            | Hash SHA-256 (irreversível)        | Chave de identificação pessoal; nunca precisa   |
|                |                                    | ser lido de volta.                              |
| nome_completo  | Hash SHA-256 + Criptografia        | Hash para cruzar/deduplicar; criptografia para  |
|                |                                    | exibir o nome a pessoas autorizadas.            |
| email/telefone | Criptografia (reversível)          | Precisam ser recuperados para contato futuro.   |

Os campos originais (em texto aberto) são REMOVIDOS do registro protegido.

Exemplo:
  Entrada: {"id_operador": 1, "cpf": "123.456.789-09", "nome_completo": "Maria Souza",
            "email": "maria@empresa.com", "funcao": "Técnica"}
  Saída:   {"id_operador": 1, "funcao": "Técnica", "cpf_hash": "a3f1...",
            "nome_completo_hash": "77bc...", "nome_completo_cripto": "gAAAA...",
            "email_cripto": "gAAAA..."}
"""
from typing import Any, Dict, Iterable, List  # tipos usados nas assinaturas das funções

import pandas as pd  # usado para processar o cadastro em formato de tabela (DataFrame)

from src.config import logger                                      # logger estruturado (JSON)
from src.security.crypto import criptografar, descriptografar       # criptografia reversível
from src.security.hashing import anonimizar_cpf, anonimizar_nome   # hash irreversível

# ---------------------------------------------------------------------------
# 1) DEFINIÇÃO DA POLÍTICA (para incluir um novo campo sensível, basta editá-la aqui)
# ---------------------------------------------------------------------------
# Campos que recebem HASH -> dicionário {nome_do_campo: função_de_hash}
CAMPOS_HASH = {"cpf": anonimizar_cpf, "nome_completo": anonimizar_nome}
# Campos que recebem CRIPTOGRAFIA reversível
CAMPOS_CRIPTOGRAFADOS = ("nome_completo", "email", "telefone")
# União (|) dos dois conjuntos: todos os campos que NÃO podem seguir em texto aberto
CAMPOS_SENSIVEIS = set(CAMPOS_HASH) | set(CAMPOS_CRIPTOGRAFADOS)


# ---------------------------------------------------------------------------
# 2) PROTEÇÃO DE UM ÚNICO OPERADOR
# ---------------------------------------------------------------------------
def proteger_operador(registro: Dict[str, Any]) -> Dict[str, Any]:
    """Recebe UM operador (dicionário) e devolve uma CÓPIA com os dados pessoais protegidos.

    Lança ValueError se o CPF for inválido.
    """
    # 2.1) Copia apenas os campos NÃO sensíveis (id, função, etc.).
    #      Assim, CPF, nome, e-mail e telefone em texto aberto ficam de fora.
    protegido = {k: v for k, v in registro.items() if k not in CAMPOS_SENSIVEIS}

    # 2.2) Para cada campo da política de hash, cria a coluna "<campo>_hash"
    #      Ex.: "cpf" -> "cpf_hash" = anonimizar_cpf(valor_do_cpf)
    for campo, funcao in CAMPOS_HASH.items():
        if campo in registro:
            protegido[f"{campo}_hash"] = funcao(registro[campo])

    # 2.3) Para cada campo da política de criptografia, cria a coluna "<campo>_cripto"
    #      Ex.: "email" -> "email_cripto" = criptografar(valor_do_email)
    for campo in CAMPOS_CRIPTOGRAFADOS:
        if campo in registro:
            protegido[f"{campo}_cripto"] = criptografar(registro[campo])

    return protegido


# ---------------------------------------------------------------------------
# 3) PROTEÇÃO DE VÁRIOS OPERADORES (com auditoria dos rejeitados)
# ---------------------------------------------------------------------------
def proteger_operadores(registros: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Protege uma lista de operadores.

    Registros com CPF inválido são REJEITADOS (não seguem no pipeline) e registrados
    no log de auditoria, como exige o PDF.
    """
    protegidos, rejeitados = [], 0  # lista de aprovados e contador de rejeitados

    # enumerate() devolve a posição (indice) e o conteúdo (registro) de cada item
    for indice, registro in enumerate(registros):
        try:
            protegidos.append(proteger_operador(registro))
        except ValueError as erro:
            rejeitados += 1
            # SEGURANÇA: o log de auditoria guarda posição, motivo e id do operador,
            # mas NUNCA o CPF ou o nome (isso seria vazar o dado pessoal no log).
            logger.warning(
                "Operador rejeitado na anonimização",
                extra={"indice": indice, "motivo": str(erro), "operador_id": registro.get("id_operador")},
            )

    # Resumo final no log (evidência para o "Relatório de Qualidade" do projeto)
    logger.info(
        "Anonimização LGPD de operadores concluída",
        extra={"total_protegidos": len(protegidos), "total_rejeitados": rejeitados},
    )
    return protegidos


# ---------------------------------------------------------------------------
# 4) VERSÃO PARA DATAFRAME (pandas) - usada na camada Silver
# ---------------------------------------------------------------------------
def proteger_operadores_df(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe o cadastro como DataFrame e devolve um novo DataFrame já protegido."""
    # 1) df.to_dict(orient="records") -> transforma cada linha da tabela em um dicionário
    # 2) proteger_operadores(...)      -> aplica a política LGPD linha a linha
    # 3) pd.DataFrame(...)             -> monta a tabela novamente (pronta para salvar em Parquet)
    return pd.DataFrame(proteger_operadores(df.to_dict(orient="records")))


# ---------------------------------------------------------------------------
# 5) RECUPERAÇÃO DOS DADOS REVERSÍVEIS (somente processos autorizados)
# ---------------------------------------------------------------------------
def recuperar_contato(registro_protegido: Dict[str, Any]) -> Dict[str, Any]:
    """Descriptografa nome, e-mail e telefone de um operador já protegido.

    O CPF NÃO aparece aqui porque foi transformado em hash (irreversível).
    """
    # Rastreabilidade (LGPD): todo acesso a dado pessoal fica registrado no log
    logger.info("Acesso a dados pessoais criptografados", extra={"operador_id": registro_protegido.get("id_operador")})

    # Para cada campo criptografado existente, descriptografa a coluna "<campo>_cripto"
    # Resultado ex.: {"nome_completo": "Maria Souza", "email": "maria@empresa.com", ...}
    return {
        campo: descriptografar(registro_protegido.get(f"{campo}_cripto"))
        for campo in CAMPOS_CRIPTOGRAFADOS
        if f"{campo}_cripto" in registro_protegido
    }
