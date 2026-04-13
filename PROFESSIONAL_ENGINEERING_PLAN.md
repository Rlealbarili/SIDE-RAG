# SIDE-RAG - Plano Profissional de Engenharia

## 1. Objetivo do Documento

Este documento define como o projeto SIDE-RAG deve ser organizado e conduzido como um projeto profissional de software.

Ele nao substitui o plano tecnico da Fase 1. Ele define a base organizacional: estrutura de pastas, documentacao, governanca tecnica, fluxo de desenvolvimento, padroes de qualidade, validacao, seguranca, releases e criterios para evolucao.

O objetivo e evitar que o SIDE-RAG vire apenas um conjunto de scripts soltos. Desde o inicio, ele deve nascer como um produto tecnico de alto nivel: rastreavel, testavel, documentado, reversivel e evolutivo.

## 2. Principios do Projeto

1. Simplicidade antes de sofisticacao.

O projeto deve comecar pequeno, mas correto. Ferramentas avancadas como GraphRAG, Mem0, RAGAS, ARES e LLMLingua so entram depois de uma necessidade comprovada.

2. Rastreabilidade sempre.

Toda informacao recuperada deve apontar para sua fonte: arquivo, linha, hash, session_id, chunk_id e origem.

3. Base bruta imutavel, indice derivado.

Transcripts, logs e documentos originais sao a fonte bruta. Chunks, vetores, entidades e resumos sao indices derivados e podem ser recriados.

4. Desenvolvimento guiado por avaliacao.

Toda melhoria em chunking, busca, reranker ou embeddings deve ser medida com benchmark. Nao basta “parecer melhor”.

5. Isolamento do claude-mem.

O SIDE-RAG deve ser capaz de funcionar sem modificar o banco interno do `claude-mem`. Integracoes com `claude-mem` devem ser explicitas, versionadas e reversiveis.

6. MCP read-only primeiro.

A primeira interface MCP deve apenas buscar e ler contexto. Escrita automatica de memoria fica fora do MVP.

7. Documentacao faz parte do codigo.

Decisoes arquiteturais, comandos, formatos e criterios de aceitacao devem viver no repositorio.

## 3. Estrutura Profissional do Repositorio

Estrutura recomendada:

```text
SIDE-RAG/
├── README.md
├── PROJECT_FOUNDATION.md
├── PROFESSIONAL_ENGINEERING_PLAN.md
├── PHASE_1_PLAN.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── retrieval-strategy.md
│   ├── evaluation.md
│   ├── operations.md
│   └── adr/
│       ├── ADR-001-sidecar-isolated-from-claude-mem.md
│       ├── ADR-002-parser-customizado-para-codex-jsonl.md
│       └── ADR-003-benchmark-deterministico-antes-de-ragas.md
├── data/
│   ├── .gitkeep
│   └── README.md
├── evals/
│   ├── eval_queries.json
│   ├── README.md
│   └── results/
│       └── .gitkeep
├── mcp/
│   ├── README.md
│   └── server.py
├── scripts/
│   ├── ingest_codex_session.py
│   ├── eval_retrieval.py
│   ├── inspect_db.py
│   └── smoke_search.py
├── src/
│   └── side_rag/
│       ├── __init__.py
│       ├── config.py
│       ├── schema.py
│       ├── db.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   └── codex_parser.py
│       ├── indexer/
│       │   ├── __init__.py
│       │   └── processor.py
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── fts.py
│       │   ├── vector.py
│       │   ├── fusion.py
│       │   └── rerank.py
│       └── eval/
│           ├── __init__.py
│           └── metrics.py
└── tests/
    ├── test_codex_parser.py
    ├── test_schema.py
    ├── test_idempotency.py
    ├── test_fts_search.py
    └── fixtures/
        └── codex_session_sample.jsonl
```

## 4. Documentos Obrigatorios

### README.md

Documento de entrada do projeto. Deve explicar:

- o que e o SIDE-RAG
- como instalar
- como rodar ingestao dry-run
- como rodar ingestao real
- como rodar benchmark
- como fazer rollback
- estado atual do projeto

### PROJECT_FOUNDATION.md

Documento conceitual. Define origem, proposito, principios e direcao estrategica.

### PHASE_1_PLAN.md

Plano executavel da Fase 1. Deve conter:

- escopo
- entregaveis
- comandos
- criterios de aceite
- riscos
- rollback
- tarefas em ordem de implementacao

### docs/architecture.md

Descreve a arquitetura:

- fontes de dados
- parser
- modelo canonico
- SQLite FTS5
- Chroma opcional
- retrieval
- benchmark
- MCP futuro

### docs/data-model.md

Define entidades, campos, tipos, chaves e regras de idempotencia.

### docs/retrieval-strategy.md

Define como a busca funciona:

- FTS lexical
- vetorial opcional
- RRF
- reranker opcional
- filtros por projeto, sessao, fonte e tipo

### docs/evaluation.md

Define benchmark:

- formato do `eval_queries.json`
- metricas
- criterios de sucesso
- como interpretar falhas

### docs/operations.md

Define operacao local:

- setup
- paths
- limpeza de indices
- backup
- restore
- comandos de diagnostico

### docs/adr/

Architecture Decision Records. Cada decisao importante deve virar um ADR curto.

Formato recomendado:

```text
# ADR-XXX - Titulo

## Status
Accepted | Proposed | Superseded

## Contexto

## Decisao

## Consequencias

## Alternativas Consideradas
```

## 5. Modelo de Trabalho

O projeto deve seguir um fluxo simples e profissional:

```text
1. Definir problema
2. Criar/atualizar plano
3. Implementar pequena fatia
4. Rodar teste unitario
5. Rodar smoke
6. Rodar benchmark
7. Atualizar documentacao
8. Registrar decisao se necessario
9. Consolidar resultado
```

Nenhuma fase deve ser considerada concluida sem:

- codigo implementado
- validacao executada
- documentacao atualizada
- risco/rollback conhecido

## 6. Fases do Produto

### Fase 1 - Fundacao

Objetivo:

Construir o ETL offline isolado, parser de JSONL Codex, modelo canonico, SQLite FTS5 e benchmark deterministico.

Entregaveis:

- estrutura do projeto
- parser customizado
- schema Pydantic
- banco SQLite proprio
- FTS5
- script de ingestao
- eval_queries.json
- script de benchmark
- smoke search

Critério de sucesso:

- ingestao idempotente
- rollback simples
- HitRate@5 >= 80% nas perguntas obrigatorias
- todo resultado com fonte rastreavel

### Fase 2 - Recuperacao Semantica

Objetivo:

Adicionar busca vetorial, fusao lexical + vetorial e reranker opcional.

Entregaveis:

- Chroma local em namespace proprio
- embeddings configuraveis
- RRF
- reranker por flag
- comparativo MiniLM vs modelo multilingue
- relatorio de ganho vs Fase 1

Critério de sucesso:

- melhora mensuravel de MRR e HitRate@5
- latencia aceitavel no ambiente local
- sem perda de rastreabilidade

### Fase 3 - Interface MCP Read-Only

Objetivo:

Expor o SIDE-RAG como ferramenta de contexto para Codex/Claude.

Entregaveis:

- MCP server read-only
- `search_memory`
- `get_chunk_context`
- `timeline`
- `answer_with_sources`
- documentacao de configuracao no Codex/Claude

Critério de sucesso:

- Codex consegue pesquisar o SIDE-RAG via MCP
- respostas trazem IDs e fontes
- ferramenta nao escreve memoria automaticamente

## 7. Padrao de Codigo

Linguagem inicial:

- Python 3.11+ ou 3.12+

Padroes:

- codigo modular
- tipagem com type hints
- Pydantic para schema
- funcoes pequenas e testaveis
- CLIs com `argparse` ou `typer`
- logs claros
- erros com mensagem acionavel

Evitar:

- scripts monoliticos gigantes
- dependencias pesadas antes de necessidade comprovada
- magia implicita
- acoplamento ao banco interno do `claude-mem`
- chamadas LLM obrigatorias na Fase 1

## 8. Dependencias

Dependencias iniciais recomendadas:

```text
pydantic
chromadb
sentence-transformers
llama-index-core
```

Observacoes:

- `sqlite3` e nativo do Python e nao deve entrar no `requirements.txt`.
- `chromadb`, `sentence-transformers` e `llama-index-core` devem ser opcionais no caminho critico inicial se atrasarem o primeiro loop.
- O parser customizado e o FTS5 devem funcionar mesmo sem embeddings.

## 9. Comandos Padrao

Instalacao local:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Dry-run de ingestao:

```powershell
python scripts/ingest_codex_session.py --session-id 019cd2ee-29d1-7853-bfa8-b12251459064 --project Sis_Marcos_Inventario --dry-run
```

Ingestao real:

```powershell
python scripts/ingest_codex_session.py --session-id 019cd2ee-29d1-7853-bfa8-b12251459064 --project Sis_Marcos_Inventario
```

Benchmark:

```powershell
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
```

Testes:

```powershell
python -m pytest
```

Smoke:

```powershell
python scripts/smoke_search.py --query "CAPTCHA SIGEF awaiting_captcha"
```

No Ubuntu, os mesmos comandos usam ativacao:

```bash
source .venv/bin/activate
```

## 10. Estrategia de Testes

Testes minimos:

- parser le JSONL valido
- parser ignora linha invalida sem quebrar execucao
- parser preserva linha de origem
- schema valida campos obrigatorios
- idempotencia por `source_hash`
- FTS retorna resultado esperado
- benchmark calcula HitRate@5
- rollback nao toca arquivos fora de `data/`

Fixtures:

- criar um JSONL pequeno em `tests/fixtures/codex_session_sample.jsonl`
- conter pelo menos:
  - uma mensagem de usuario
  - uma resposta do agente
  - uma tool call
  - um tool result
  - um output de teste
  - uma decisao tecnica

## 10.1 Rotina Profissional de Testes

O SIDE-RAG deve seguir uma rotina de testes por camadas, semelhante ao que a industria usa em produtos criticos, mas ajustada ao tamanho do projeto.

### Camada 1 - Testes Unitarios

Objetivo:

Validar funcoes pequenas e deterministicas.

Cobrir:

- parser de JSONL
- normalizacao de eventos
- calculo de `source_hash`
- validacao Pydantic
- criacao de chunks
- formatacao de metadados
- calculo de HitRate@5
- calculo de MRR
- RRF

Comando:

```powershell
python -m pytest tests/unit
```

### Camada 2 - Testes de Contrato

Objetivo:

Garantir que os formatos publicos nao quebrem.

Contratos:

- schema de `eval_queries.json`
- schema da tabela `chunks`
- output do `ingest_codex_session.py --dry-run`
- output JSON do `eval_retrieval.py`
- retorno do MCP read-only

Esses testes sao essenciais porque agentes e scripts futuros dependerao desses formatos.

### Camada 3 - Testes de Integracao Local

Objetivo:

Validar o fluxo real com banco SQLite e, quando habilitado, Chroma.

Cobrir:

- criar `data/sidecar.db`
- criar tabelas
- criar FTS5
- inserir chunks
- executar busca lexical
- executar busca vetorial opcional
- reprocessar a mesma sessao sem duplicar chunks
- apagar `data/` e reconstruir

Comando:

```powershell
python -m pytest tests/integration
```

### Camada 4 - Smoke Tests

Objetivo:

Validar o caminho feliz em poucos segundos.

Smoke inicial:

```powershell
python scripts/ingest_codex_session.py --session-id 019cd2ee-29d1-7853-bfa8-b12251459064 --project Sis_Marcos_Inventario --dry-run
python scripts/smoke_search.py --query "CAPTCHA SIGEF awaiting_captcha"
```

O smoke deve responder:

- quantos chunks existem
- se a busca retornou resultado
- se cada resultado tem fonte
- latencia da busca

### Camada 5 - Benchmark de Recuperacao

Objetivo:

Provar qualidade de busca.

Comando:

```powershell
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
```

Metricas obrigatorias:

- HitRate@5
- MRR
- latencia media
- taxa de resultados com fonte
- taxa de queries sem resultado

Falha do benchmark deve bloquear avancos em retrieval, reranker e MCP.

### Camada 6 - Regressao de Memoria

Objetivo:

Evitar que uma melhoria em parser/ranking quebre perguntas antigas.

Regra:

Toda decisao importante do projeto deve virar uma query em `eval_queries.json`.

Exemplo:

Quando a decisao sobre CAPTCHA SIGEF foi estabilizada, deve existir uma query de regressao que cobre `awaiting_captcha`, checkpoint e retomada manual segura.

### Camada 7 - Testes de Dados

Objetivo:

Validar qualidade e consistencia do corpus.

Checks:

- nenhum chunk sem `source_path`
- nenhum chunk sem `source_hash`
- nenhum chunk sem `source_line_start`
- nenhum chunk sem `project_id`
- nenhum chunk sem `session_id`
- nenhum chunk derivado sem referencia ao bruto
- nenhum arquivo de `data/` versionado por acidente

## 10.2 Gates de Qualidade

Gates locais antes de considerar uma tarefa concluida:

```powershell
python -m pytest
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
python scripts/smoke_search.py --query "CAPTCHA SIGEF awaiting_captcha"
```

Gates para mudancas no parser:

- unit tests do parser
- integracao com fixture
- reprocessamento idempotente
- benchmark comparado com baseline anterior

Gates para mudancas no retrieval:

- eval completo
- relatorio de MRR antes/depois
- latencia antes/depois
- amostra dos Top 5 para queries criticas

Gates para mudancas no MCP:

- contrato JSON das ferramentas
- read-only garantido
- timeout controlado
- retorno com IDs e fontes

## 10.3 Golden Dataset

O projeto deve manter um conjunto pequeno de perguntas de ouro.

Arquivo:

```text
evals/eval_queries.json
```

Regra:

- cada bug importante vira uma pergunta
- cada decisao arquitetural vira uma pergunta
- cada spec importante vira uma pergunta
- cada fluxo critico vira uma pergunta

Exemplo:

```json
{
  "id": "q_sigef_captcha_001",
  "query": "Qual foi a decisao sobre CAPTCHA no SIGEF e estado awaiting_captcha?",
  "project": "Sis_Marcos_Inventario",
  "expected_terms": ["CAPTCHA", "awaiting_captcha", "checkpoint", "retomar"],
  "expected_files": ["extension_chrome/content.js", "extension_chrome/background.js"],
  "required": true
}
```

No futuro, esse golden dataset pode alimentar RAGAS/ARES ou uma avaliacao LLM-as-judge. No MVP, ele deve ser deterministico.

## 10.4 Matriz de Rastreabilidade

O SIDE-RAG deve manter uma matriz simples ligando:

```text
Fonte bruta -> Chunk -> Entidade -> Query de benchmark -> Resultado de busca
```

Campos minimos:

```text
source_path
source_hash
source_line_start
source_line_end
source_event_type
chunk_id
parser_version
project_id
session_id
eval_query_id
retrieval_rank
```

Objetivo:

Quando uma resposta for retornada, deve ser possivel responder:

- de qual arquivo ela veio?
- de quais linhas?
- qual parser gerou isso?
- qual hash identifica a fonte?
- qual query validou esse comportamento?
- em qual posicao o chunk apareceu?

## 10.5 Observabilidade Moderna

Na industria, sistemas modernos usam telemetria para entender comportamento real, nao apenas logs soltos.

Para o SIDE-RAG, a evolucao natural e usar OpenTelemetry para traces, metricas e logs. A documentacao oficial define OpenTelemetry como framework aberto e vendor-neutral para gerar, coletar e exportar traces, metricas e logs.

No MVP, nao implemente ainda um coletor completo. Mas modele logs ja pensando em traces.

Campos recomendados em logs:

```text
run_id
trace_id
session_id
project_id
parser_version
query_id
chunk_id
stage
duration_ms
result_count
error_code
```

Eventos importantes:

- ingest_started
- ingest_completed
- chunk_created
- chunk_skipped_idempotent
- fts_search_completed
- vector_search_completed
- rrf_completed
- rerank_completed
- eval_query_completed
- eval_run_completed

Ferramenta futura opcional:

- Langfuse, para rastreio especifico de aplicacoes LLM, prompts, tool calls, avaliacoes e datasets.

Langfuse deve entrar apenas quando houver LLM no pipeline. No MVP deterministico, logs estruturados bastam.

## 10.6 Rastreabilidade de Supply Chain

Para um projeto profissional, tambem importa saber como o software foi construido.

Praticas recomendadas:

- `requirements.txt` versionado
- `pip freeze` ou lockfile quando estabilizar
- `.env.example` sem segredos
- `data/` gitignored
- changelog simples
- tags de release
- hashes dos arquivos fonte indexados
- registro de parser_version
- registro de embedding_model
- registro de reranker_model

Evolucao futura:

- SBOM
- assinatura de release
- SLSA como referencia de maturidade para supply chain

SLSA e um framework de controles para prevenir adulteracao, melhorar integridade e proteger pacotes e infraestrutura. Para o SIDE-RAG, isso fica como maturidade futura, nao MVP.

## 10.7 Controle de Qualidade de Dados

Antes de melhorar modelo, melhore dados.

Checks obrigatorios:

- chunks muito grandes devem ser rejeitados ou divididos
- chunks vazios devem ser descartados
- outputs repetidos devem ser deduplicados
- eventos `token_count` devem ficar fora do indice principal
- raciocinio criptografado deve ficar fora do indice principal
- tool outputs gigantes devem ser resumidos por metadados, preservando ponte ao bruto
- codigo, stacktrace e specs devem ser preservados sem compressao destrutiva

Relatorio de qualidade da ingestao:

```text
source_file
source_size_bytes
lines_read
json_errors
events_seen
chunks_created
chunks_skipped
duplicates
largest_chunk_chars
avg_chunk_chars
duration_ms
```

## 11. Avaliacao Profissional

Metricas iniciais:

- HitRate@5
- MRR
- latencia media
- quantidade de resultados sem fonte
- quantidade de resultados irrelevantes no Top 5

Relatorio minimo por benchmark:

```text
query_id
query
hit
first_relevant_rank
latency_ms
matched_terms
matched_files
top_results
failure_reason
```

Interpretacao:

- Falha por ausencia de dado: melhorar ingestao.
- Falha por dado presente mas nao recuperado: melhorar retrieval.
- Falha por resultado certo abaixo do Top 5: melhorar ranking/reranker.
- Falha por falta de fonte: corrigir schema.

## 12. Seguranca e Privacidade

O SIDE-RAG pode conter informacoes sensiveis de projetos, logs e conversas.

Regras:

- `data/` deve ser gitignored.
- `.env` deve ser gitignored.
- usar `.env.example` sem segredos.
- nunca enviar transcripts brutos para servicos externos sem aprovacao explicita.
- embeddings remotos devem ser opcionais e documentados.
- campos com secrets devem ser mascarados no parser quando possivel.

Conteudos que nao devem ser comprimidos/sumarizados por LLM:

- codigo
- SQL
- stacktrace
- paths
- IDs
- specs
- resultados de teste
- migracoes
- logs de erro
- configuracoes sensiveis

## 13. Versionamento e Commits

Padrao recomendado de commits:

```text
feat: add codex jsonl parser
test: cover parser line tracking
docs: add phase 1 plan
refactor: isolate fts retrieval
chore: add project scaffold
```

Cada commit deve ter escopo pequeno e verificavel.

Antes de merge:

- testes passam
- benchmark executa
- docs relevantes atualizados
- nao ha arquivos de `data/` versionados

## 14. Releases

Mesmo sendo local, o projeto deve ter marcos:

```text
v0.1 - scaffold + parser + schema
v0.2 - SQLite + FTS + ingestao idempotente
v0.3 - benchmark deterministico
v0.4 - Chroma opcional
v0.5 - RRF + reranker opcional
v0.6 - MCP read-only
```

Cada release deve ter:

- resumo
- comandos de validacao
- limitacoes conhecidas
- proximo passo

## 15. Definition of Ready

Uma tarefa esta pronta para implementacao quando tem:

- objetivo claro
- arquivos provaveis
- entrada e saida esperadas
- criterio de aceite
- impacto em dados
- plano de rollback, se tocar persistencia

## 16. Definition of Done

Uma tarefa esta concluida quando:

- codigo foi implementado
- testes relevantes passam
- smoke foi executado quando aplicavel
- benchmark foi executado quando afetar busca
- documentacao foi atualizada
- riscos residuais foram anotados
- nenhum dado gerado indevido ficou versionado

## 17. Riscos e Mitigacoes

Risco: overengineering.

Mitigacao: manter GraphRAG, Mem0 e LLMLingua fora do MVP.

Risco: acoplamento ao `claude-mem`.

Mitigacao: sidecar com banco proprio e MCP read-only.

Risco: busca vetorial retornar contexto bonito mas errado.

Mitigacao: benchmark deterministico, FTS lexical e fontes obrigatorias.

Risco: banco crescer demais.

Mitigacao: raw pointer em vez de duplicar tudo, compressao proibida para dados tecnicos, limpeza por parser_version.

Risco: dependencia pesada no Windows/Linux.

Mitigacao: caminho Fase 1 sem embeddings obrigatorios.

## 18. Primeira Sequencia de Implementacao

1. Criar scaffold do repo.
2. Criar `.gitignore`.
3. Criar `README.md`.
4. Criar `docs/adr/ADR-001-sidecar-isolated-from-claude-mem.md`.
5. Criar `src/side_rag/schema.py`.
6. Criar fixture JSONL pequena.
7. Criar parser customizado.
8. Criar testes do parser.
9. Criar SQLite schema e FTS5.
10. Criar ingestao dry-run.
11. Criar ingestao real idempotente.
12. Criar eval_queries.json.
13. Criar eval_retrieval.py.
14. Rodar benchmark.
15. Ajustar chunking com base no benchmark.

## 19. Norte Final

O SIDE-RAG deve ser tratado como uma infraestrutura de contexto, nao como um experimento solto.

Um projeto profissional nao nasce complexo. Ele nasce com limites claros, rastreabilidade, testes, documentacao, reversibilidade e capacidade de evoluir sem quebrar a base.

Se a Fase 1 provar que o pipeline simples recupera contexto melhor que a memoria bruta, o projeto avanca. Se nao provar, o trabalho volta para parser, chunking e benchmark antes de qualquer tecnologia nova.
