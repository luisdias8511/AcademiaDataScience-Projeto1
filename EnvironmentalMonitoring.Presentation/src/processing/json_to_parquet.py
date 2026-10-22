"""Conversão de JSON já validado para Parquet/Snappy em memória."""

import json

import pyarrow as pa
import pyarrow.parquet as pq


def json_to_parquet(data: str | bytes | dict | list[dict]) -> bytes:
    """Retorna os bytes de um arquivo Parquet com compressão Snappy.

    Aceita texto/bytes JSON, um objeto ou uma lista de objetos já interpretados.
    Um objeto representa uma linha; uma lista representa várias linhas.
    Objetos e listas internos permanecem como estruturas aninhadas no Parquet.
    Não valida contratos, não filtra registros, não converte datas textuais,
    não reorganiza medições em linhas e não acessa disco ou Blob.
    Os tipos são inferidos pelo Arrow; valores incompatíveis geram exceção.
    """
    parsed = json.loads(data) if isinstance(data, (str, bytes)) else data
    records = [parsed] if isinstance(parsed, dict) else parsed

    # A inferência considera todas as linhas, inclusive campos opcionais posteriores.
    table = (
        pa.Table.from_struct_array(pa.array(records))
        if records else pa.table({})
    )
    buffer = pa.BufferOutputStream()
    pq.write_table(table, buffer, compression="snappy")
    return buffer.getvalue().to_pybytes()
