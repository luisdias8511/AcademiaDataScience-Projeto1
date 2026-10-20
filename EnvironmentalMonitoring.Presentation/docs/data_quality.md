# Qualidade de dados e auditoria de rejeições

## Situação da entrega

Implementação local de validação de contrato, entrada JSON, regras de qualidade,
auditoria e adaptador de gravação de eventos no Blob. Foram executados 81 testes
isolados com sucesso e uma demonstração local com armazenamento em memória.
Esses resultados não comprovam integração ao pipeline nem acesso ao Azure.

Responsável: Gabriel Diniz Silva.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/processing/bronze_contract_validator.py` | Validação do schema e do documento, interpretação estrita de texto JSON |
| `src/processing/data_quality.py` | Avaliação do lote, duplicidades locais, indicadores e eventos de rejeição de qualidade |
| `src/processing/contract_audit.py` | Eventos de contrato e encaminhamento de eventos ao logger recebido |
| `src/processing/contract_audit_storage.py` | Envio de eventos com `upload_json`, sem criar a conexão |
| `src/database/blob_storage_service.py` | Serviço existente de conexão e upload; não foi necessário alterá-lo |
| `contracts/schemas/` | Contratos Bronze existentes de água e meteorologia |
| `examples/demo_data_quality.py` | Demonstração local com seis leituras simuladas |

Os cinco arquivos de teste são `test_bronze_contract_validator.py`,
`test_contract_audit.py`, `test_contract_audit_storage.py`,
`test_json_contract_input.py` e `test_data_quality.py`, na pasta `tests/`.

## Dependências e execução

Execute da pasta `EnvironmentalMonitoring.Presentation`, com o ambiente virtual ativo:

```powershell
python -m pip install "jsonschema[format]==4.26.0" pytest
```

Mantenha `jsonschema[format]==4.26.0` no `requirements.txt` da aplicação.
O teste real do Blob também depende das bibliotecas e configurações do serviço
existente, incluindo `azure-storage-blob` e `AZURE_STORAGE_CONNECTION_STRING`.
Não versionar credenciais no Git.

Testes isolados do módulo:

```powershell
python -m pytest -q --noconftest --import-mode=importlib -o addopts= -p no:cacheprovider tests/test_bronze_contract_validator.py tests/test_contract_audit.py tests/test_contract_audit_storage.py tests/test_json_contract_input.py tests/test_data_quality.py
```

Esperado na versão atual: `81 passed`.
O comando não executa a suíte completa do projeto. O isolamento evita inicializar
serviços externos pelo pacote `src` e carregar o `conftest.py` compartilhado.
Os testes de armazenamento usam simulação, não a conexão Azure real.

Demonstração:

```powershell
python examples/demo_data_quality.py
```

Esperado: 6 documentos recebidos, 2 aprovados, 4 rejeitados, 1 documento com
alerta e 8 eventos de rejeição. Cinco eventos correspondem aos cinco parâmetros
da leitura duplicada. O prazo de atraso de uma hora é exclusivo dessa demonstração.
Os eventos ficam em memória; o script não envia auditoria ao Azure nem grava
arquivos de saída.

## Rejeição completa

Uma violação de contrato ou uma regra de qualidade que gere erro bloqueia toda a
leitura. Não há aproveitamento parcial dos parâmetros. Alertas temporais, sozinhos,
não rejeitam a leitura. O documento original não é corrigido ou alterado.
O chamador deve efetivamente separar aprovados e rejeitados e impedir o
encaminhamento dos rejeitados: retornar uma decisão não executa essa integração.
Outliers estatísticos são responsabilidade de analytics e não equivalem
automaticamente a valores inválidos.

## Contrato e entrada JSON

```python
approved, error = validate_contract(document, schema)
approved, document, error = validate_json_contract(text, schema)
```

A primeira função recebe um dicionário e retorna `(True, None)` ou `(False, error)`.
A segunda recebe texto e retorna `(True, document, None)` ou `(False, None, error)`.
O schema deve ser fornecido pelo chamador; os métodos não o carregam de arquivos.

O contrato usa JSON Schema Draft 2020-12 e verificação de formatos.
`ContractValidationError.errors` contém as violações para auditoria.
JSON malformado, campos repetidos no mesmo objeto, constantes não finitas e raiz
que não seja um objeto são rejeitados pela entrada textual. Isso não substitui a
validação das respostas brutas da API antes da transformação para Bronze.
Erros no schema e falhas inesperadas são propagados como problemas operacionais.

O contrato verifica apenas as restrições existentes no schema; não impõe campos
extras proibidos, parâmetros conhecidos ou outros limites que não estejam definidos.
Essas verificações adicionais pertencem às regras de qualidade descritas abaixo.

## Parâmetros e regras iniciais

| Código | Categoria | Unidade exata | Mínimo | Máximo |
|---|---|---|---|---|
| AIR_TEMPERATURE | weather | °C | Não configurado | Não configurado |
| CONDUCTIVITY | water | µS/cm (25°C) | 0 | Não configurado |
| HARDNESS | water | °f | 0 | Não configurado |
| TURBIDITY | water | NFU | 0 | Não configurado |
| PH | water | pH unity | 0 | 14 |
| WATER_TEMPERATURE | water | °C | Não configurado | Não configurado |

Limites configurados são inclusivos. Código e unidade precisam corresponder
exatamente à configuração; não há conversão automática ou aliases.
Os parâmetros desconhecidos ou de outra categoria são rejeitados.
Valores não numéricos, booleanos e números não finitos são rejeitados.
Não é obrigatório conter todos os seis parâmetros numa leitura; o contrato exige
pelo menos uma medição na coleção correspondente.

Os mínimos zero e a tolerância de cinco minutos são decisões iniciais do projeto,
a revisar com o grupo e a fonte. Os limites não são padrões de potabilidade nem
critérios regulatórios. Códigos numéricos de ausência utilizados pela fonte precisam
ser tratados explicitamente na integração.

## Avaliação do lote

```python
report = assess_data_quality(documents, "water")
```

Pré-condição: todos os documentos do lote passaram no contrato da categoria.
Os documentos meteorológicos usam `payload.parameters`; os de água usam
`payload.pollutants`. Cada chamada recebe uma categoria e inicia uma nova
memória de duplicidades. Não chamar individualmente por leitura se o objetivo
é detectar duplicatas entre leituras do mesmo lote.

O retorno contém `results`, na mesma ordem de entrada, e `summary`.
Cada resultado contém `document_index`, `approved`, `action`, `errors`, `warnings`,
`unchecked_rules` e `delay_seconds`.
O chamador deve manter o vínculo entre esse índice e o identificador original.
Quando filtrar documentos rejeitados no contrato, os índices se referem à lista
filtrada passada à qualidade, não ao lote bruto inicial.

Indicadores de `summary`:

- `received_documents`, `approved_documents` e `rejected_documents`;
- `documents_with_warnings` e `documents_with_unchecked_rules`;
- `error_occurrences_by_code` e `warning_occurrences_by_code`.

São indicadores da etapa de qualidade para seu lote de entrada. Rejeições
anteriores de contrato/JSON precisam ser contabilizadas pelo pipeline para
produzir totais de ponta a ponta. Ocorrências de erro não equivalem a documentos
rejeitados. A presença de regras não configuradas não rejeita por si só e impede
interpretar a aprovação como validação de todas as faixas físicas possíveis.

## Duplicidade e conflitos

Chave inicial: código da estação + instante da leitura em UTC + código do parâmetro.
O valor e a unidade distinguem repetição idêntica de conflito.

Preserva-se a primeira leitura aprovada na ordem de entrada; uma leitura posterior
com chave repetida é rejeitada inteira. A rejeição não altera leituras anteriores.
Uma leitura rejeitada não reserva as chaves de seus parâmetros para as seguintes.
Não há consulta ao banco nem memória entre chamadas. Não se garante idempotência
entre execuções apenas com essa validação. Se existirem múltiplos sensores por
parâmetro, a chave deverá incluir o sensor. O lote não é ordenado automaticamente.

## Tempo e configuração

`delay_seconds = ingestion_datetime - payload.datetime`, após conversão para UTC.
O horário de referência é o metadado de ingestão, não o relógio atual da avaliação.
Os metadados precisam ser produzidos corretamente pela ingestão.

- Futuro: até cinco minutos é aceito; acima de cinco minutos rejeita, inclusive em
  modo histórico. É possível passar outra `future_tolerance` ou `None` para manter
  somente alerta e registrar que a tolerância está desativada.
- Atraso: `maximum_delay=None` por padrão. Em `mode="realtime"`, uma diferença
  acima de um prazo configurado gera alerta, não rejeição.
- Histórico/backfill: `mode="historical"` é o padrão e não aplica o alerta de atraso
  operacional, mesmo que seja informado `maximum_delay`.

Exemplo de configuração, não padrão obrigatório:

```python
from datetime import timedelta
report = assess_data_quality(
    documents,
    "water",
    mode="realtime",
    future_tolerance=timedelta(minutes=5),
    maximum_delay=timedelta(hours=1),
)
```

Para alterar limites, faça uma cópia de `PARAMETER_RULES`, altere o parâmetro e
passe `rules=...`. Não é necessário editar o algoritmo.

## Auditoria e armazenamento

Contrato: `build_contract_audit_events(document, error.errors, ...)`.
Qualidade: `build_data_quality_audit_events(document, result, ...)`.
Ambos recebem `execution_id`, `document_id` e `category`;
o construtor de contrato também recebe `schema_name`.

Os identificadores de execução e documento vêm do chamador. O nome original
planejado do blob pode ser usado como identificador do documento.
Cada erro gera um evento com `event_id`, timestamp UTC, contexto, código,
caminho do campo, motivo e `action="REJECT_DOCUMENT"`.
Não se copia o documento completo ou o valor rejeitado para o evento.
Se o JSON não puder ser interpretado, use contexto vazio no construtor de
contrato e preserve a rastreabilidade pelos identificadores externos.

Para registrar eventos, use `log_contract_audit_events(events, logger)`.
A função também aceita os eventos de qualidade; seu nome foi mantido por
compatibilidade. O horário UTC do evento segue no campo `event_timestamp` do
log. O timestamp externo do logger depende do formatador existente.
Alertas de qualidade permanecem em `result["warnings"]` e ainda precisam ser
encaminhados pelo pipeline ao log operacional; não são eventos de rejeição.

Para gravar, crie `BlobStorageService(container_name="audit")` na integração e
passe esse serviço a `save_contract_audit_events(events, storage, logger)`.
O adaptador não cria conexão, contêiner ou credenciais.

Prefixos no contêiner `audit`:

- `contract-rejections/` para `CONTRACT_VALIDATION_FAILED`;
- `quality-rejections/` para `DATA_QUALITY_VALIDATION_FAILED`.

O particionamento usa a data UTC do evento de auditoria, categoria, hash do
identificador de execução e UUID do evento.
O serviço atual usa `overwrite=True`: repetir o envio dos MESMOS eventos mantém
os caminhos; recriar eventos com novos UUIDs produz novos arquivos.
Não são uploads atômicos. `AuditPersistenceError.saved_paths` informa os caminhos
confirmados antes da falha e `failed_path` identifica o envio que falhou.
Uma falha pode ter ocorrido depois de o servidor receber o conteúdo; o caminho
com falha tem estado incerto. Propague a falha e trate a recuperação no pipeline;
não interprete falha de auditoria como conclusão bem-sucedida da execução.

## Ordem de integração proposta

1. Identificar a execução e cada registro de origem.
2. Interpretar o JSON quando necessário e validar o contrato.
3. Auditar e separar os rejeitados no contrato; encaminhar aprovados para Bronze.
4. Ao preparar Silver, avaliar um lote de documentos aprovados no contrato.
5. Separar aprovados/rejeitados por `document_index` e auditar rejeições de qualidade.
6. Registrar alertas e resumo no logger; encaminhar somente os aprovados para Silver.
7. Confirmar gravações e tratar falhas de persistência.

Essa ordem deve ser alinhada com a implementação atual da ingestão e do pipeline.
Erros que aconteçam durante a construção do documento Bronze também precisam
ser capturados na ingestão, antes de se conseguir chamar este validador.

## Seis dimensões da qualidade

| Dimensão | Evidência atual | Limitação |
|---|---|---|
| Completude | Campos obrigatórios e coleções mínimas no contrato; código de estação sem espaços em branco | Não mede a cobertura de leituras esperadas por estação e período |
| Unicidade | Duplicatas e conflitos dentro do lote | Sem verificação entre lotes, no banco ou em reexecuções |
| Validade | Tipos, códigos, unidades, números finitos e limites configurados | Máximos de água e faixas de temperatura pendentes |
| Consistência | Categoria/unidade compatíveis e comparações de horários em UTC | Não verifica coerência entre diferentes sensores nem ordena o lote |
| Tempestividade | Atraso calculado; alerta configurável em realtime | Prazo operacional depende da frequência da fonte e não está definido por padrão |
| Acurácia | Não medida diretamente | Requer referência, calibração ou evidência externa; plausibilidade não comprova acurácia |

Não foi implementada uma pontuação ou porcentagem consolidada para cada dimensão.
Os contadores atuais não devem ser apresentados como avaliação completa das seis.

## Pendências para conclusão integrada

- Acesso Azure e confirmação de gravação real no contêiner `audit` (sem `.env`
  localizado nas duas pastas consultadas no PC do responsável).
- Integração ao fluxo atualizado da ingestão, Bronze e preparação da Silver.
- Tratamento auditável das falhas anteriores à montagem dos documentos Bronze.
- Prazo operacional de atraso e revisão das regras provisórias pelo grupo.
- Limites de temperatura e máximos dos demais parâmetros com justificativa da fonte.
- Alinhamento da chave com sensores e deduplicação/idempotência da persistência.
- Encaminhamento dos alertas e do resumo ao logging real; testes de integração
  com o formatador, storage e pipeline atuais.
