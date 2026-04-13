# SIDE-RAG - Documento Fundamental

## 1. Proposito

O projeto SIDE-RAG nasce para ser uma camada de memoria semantica e recuperacao de contexto para agentes como Codex, Claude Code e ferramentas futuras de engenharia de software.

O objetivo nao e substituir imediatamente o `claude-mem`, que ja esta operacional nesta maquina. O objetivo e construir um sidecar independente, auditavel e evolutivo, capaz de ler transcripts, decisoes tecnicas, specs, logs e documentos do projeto, tratar essa base, indexar de forma inteligente e devolver contexto de alta qualidade com citacao de fonte.

Em termos praticos: o SIDE-RAG deve permitir que um agente recupere rapidamente "o que foi decidido", "por que foi decidido", "quais arquivos foram tocados", "qual spec estava em jogo", "qual teste validou a mudanca" e "onde esta a fonte bruta original".

## 2. Contexto de Origem

O projeto surgiu a partir da integracao entre Codex e `claude-mem` no ambiente local Windows.

Estado observado:

- O `claude-mem` esta instalado em `C:\Users\User\.claude-mem`.
- O worker do `claude-mem` foi estabilizado na porta `37778`.
- O MCP `claude-mem` foi conectado ao Codex.
- O projeto inicial de referencia e `Sis_Marcos_Inventario`.
- Uma conversa Codex grande, ID `019cd2ee-29d1-7853-bfa8-b12251459064`, foi importada com sucesso para o `claude-mem`.
- A importacao demonstrou que guardar o transcript bruto nao basta; a recuperacao melhorou de fato quando foi criada uma camada semantica tratada, com mensagens segmentadas, metadados e ponte para os chunks brutos.

Essa experiencia define a principal tese do SIDE-RAG:

> Memoria util nao e apenas armazenamento. Memoria util e dado tratado, rastreavel, pesquisavel, avaliado e retornado com fonte.

## 3. Principios de Engenharia

1. O sidecar deve ser isolado.

O SIDE-RAG nao deve depender de alterar tabelas internas do `claude-mem` para funcionar. Ele pode ler transcripts e, futuramente, ler dados do `claude-mem` em modo controlado, mas sua fonte operacional deve ser propria.

2. O bruto deve ser preservado.

Transcripts, logs e documentos originais devem continuar acessiveis por `source_path`, `source_line_start`, `source_line_end`, `source_event_type` e `source_hash`.

3. A camada semantica deve ser derivada.

Chunks semanticos, episodios, entidades e resumos sao produtos derivados do bruto. Eles podem ser recriados quando o parser melhorar.

4. Toda resposta precisa de fonte.

Busca, timeline e respostas sintetizadas devem retornar IDs e metadados de origem. O sistema nao deve incentivar respostas sem rastreabilidade.

5. O MVP deve provar ganho real.

Antes de GraphRAG, Mem0, LLMLingua, RAGAS ou outros componentes avancados, o projeto deve provar melhora objetiva com benchmark deterministico simples.

6. Menos acoplamento, mais reversibilidade.

O rollback da Fase 1 deve ser apagar ou restaurar apenas os artefatos do SIDE-RAG, sem tocar no `claude-mem` produtivo.

7. Parser customizado vence framework quando a fonte e estruturada.

Transcripts Codex em JSONL tem estrutura rigida. A primeira versao deve usar parser Python customizado. LlamaIndex pode entrar depois para splitter ou node hierarchy, se trouxer ganho mensuravel.

## 4. Escopo Inicial

O foco inicial e indexar e avaliar memoria de engenharia para o projeto:

- `Sis_Marcos_Inventario`
- AGENTS.md e instrucoes de operacao
- OpenSpec e specs ativas
- transcripts Codex em `~/.codex/sessions/**/*.jsonl`
- decisoes tecnicas
- bugfixes
- alteracoes de arquivos
- resultados de testes
- comandos de deploy e gates
- eventos relevantes de SIGEF, fundiaria, DXF/KML, tenant separation, fotos de marcos e worker DOCX

Fora do MVP:

- GraphRAG / Neo4j
- Mem0
- LLMLingua
- escrita direta no `claude-mem.db`
- agentes autonomos que escrevem memoria
- compressao de codigo, stacktrace, SQL, specs ou logs de teste

## 5. Arquitetura Alvo

Arquitetura da Fase 1:

```text
Codex JSONL / Docs / Specs
        |
        v
Parser customizado
        |
        v
Modelo canonico
        |
        +--> SQLite sidecar.db com FTS5
        |
        +--> Chroma local em namespace proprio
        |
        v
Retrieval local
        |
        v
Benchmark deterministico
```

Arquitetura futura:

```text
Fontes brutas
  -> Normalizador
  -> Chunks hierarquicos
  -> SQLite canonico
  -> FTS5 + Chroma/Qdrant
  -> RRF
  -> Reranker opcional
  -> MCP read-only
  -> Codex / Claude / outros agentes
```

## 6. Layout Inicial do Projeto

Estrutura pretendida:

```text
tools/memory-rag/
├── data/
│   ├── sidecar.db
│   └── chroma/
├── evals/
│   ├── eval_queries.json
│   └── results/
├── mcp/
├── scripts/
│   ├── ingest_codex_session.py
│   └── eval_retrieval.py
├── src/
│   ├── parsers/
│   │   └── codex_parser.py
│   ├── indexer/
│   │   └── processor.py
│   ├── retrieval/
│   │   └── search.py
│   └── schema.py
└── README.md
```

No novo projeto `SIDE-RAG`, a estrutura equivalente pode viver diretamente na raiz:

```text
SIDE-RAG/
├── data/
├── evals/
├── mcp/
├── scripts/
├── src/
├── PROJECT_FOUNDATION.md
└── README.md
```

## 7. Modelo Canonico Inicial

Entidade minima: `chunk`.

Campos obrigatorios:

```text
chunk_id
project_id
session_id
content
source_hash
source_path
source_event_type
source_line_start
source_line_end
timestamp
role
phase
prompt_number
raw_chunk_id
parser_version
created_at
```

Entidades futuras:

```text
raw_chunk
session_summary
turn
episode
decision
bugfix
file_change
test_result
spec_reference
open_question
```

Regra de ouro:

Todo item derivado deve apontar para a origem bruta. Se essa origem nao existir, o item nao deve entrar no indice principal.

## 8. Estrategia de Busca

Fase 1:

- SQLite FTS5 para busca lexical exata.
- Chroma local opcional para busca semantica.
- Fusao simples por Reciprocal Rank Fusion quando ambos estiverem ativos.
- Sem reranker obrigatorio no primeiro corte.

Fase 2:

- Reranker opcional via `sentence-transformers`.
- Baseline leve: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Alternativa multilingue/tecnica a validar: `BAAI/bge-reranker-m3`.
- Chroma continua se atender bem; Qdrant entra apenas se houver necessidade objetiva de melhor busca hibrida, filtros e performance.

## 9. Benchmark Inicial

O benchmark deve vir antes de qualquer otimizacao sofisticada.

Arquivo:

```text
evals/eval_queries.json
```

Campos sugeridos:

```json
{
  "id": "q001",
  "query": "Qual foi a decisao sobre CAPTCHA no SIGEF e estado awaiting_captcha?",
  "project": "Sis_Marcos_Inventario",
  "expected_terms": ["CAPTCHA", "awaiting_captcha", "checkpoint", "retomar"],
  "expected_files": [
    "extension_chrome/content.js",
    "extension_chrome/background.js",
    "backend/routes/sigef.js"
  ],
  "expected_chunk_ids": [],
  "required": true,
  "notes": "Testa recuperacao de decisao arquitetural e retomada segura."
}
```

Metricas iniciais:

- HitRate@5
- MRR
- latencia media
- presenca de fonte correta
- presenca de termos esperados
- numero de chunks irrelevantes no Top 5

RAGAS ou ARES ficam para depois que a recuperacao deterministica estiver estabilizada.

## 10. Casos de Benchmark do Projeto

Casos iniciais:

1. Qual foi a decisao sobre CAPTCHA no SIGEF e estado `awaiting_captcha`?
2. Qual o foco da SPEC-028 e quais arquivos/fluxos ela envolve?
3. Por que o worker Python foi escolhido para o importador DOCX?
4. Qual e a regra de isolamento multi-tenant definida no AGENTS.md?
5. Qual comando de gate local e obrigatorio antes do deploy?
6. Como o IRON-SERVER deve ser validado apos deploy?
7. Como funciona a estrategia de fotos de marcos e acesso autenticado?
8. Qual o escopo do modulo fundiario e do roteador multi-source?
9. Quais cuidados foram definidos para importacao DXF/KML?
10. Como a separacao tenant/cliente deve ser aplicada?

Cada pergunta deve aceitar `expected_terms`, `expected_files` e, quando disponivel, `expected_chunk_ids`.

## 11. Comandos Pretendidos

Dry run de ingestao:

```powershell
python scripts/ingest_codex_session.py --session-id 019cd2ee-29d1-7853-bfa8-b12251459064 --project Sis_Marcos_Inventario --dry-run
```

Ingestao real:

```powershell
python scripts/ingest_codex_session.py --session-id 019cd2ee-29d1-7853-bfa8-b12251459064 --project Sis_Marcos_Inventario
```

Avaliacao:

```powershell
python scripts/eval_retrieval.py --queries evals/eval_queries.json --top-k 5
```

## 12. Rollback

Na Fase 1, o rollback deve ser simples:

```powershell
Remove-Item -Recurse -Force .\data\sidecar.db
Remove-Item -Recurse -Force .\data\chroma
```

Nenhuma acao de rollback deve depender de restaurar o `claude-mem.db`, porque o MVP nao deve alterar o banco produtivo do `claude-mem`.

## 13. Decisoes de Backlog

Mem0:

Fica fora do MVP. Pode ser reavaliado se houver necessidade de memoria episodica dinamica inter-agentes. No momento, sobrepoe parte do papel do `claude-mem`.

GraphRAG / Neo4j:

Fica fora do MVP. Pode ser reavaliado se as perguntas exigirem relacoes complexas entre arquivos, specs, tarefas, agentes e decisoes.

LLMLingua:

Fica fora do MVP. Pode ser usado apenas em discussoes humanas longas e nao criticas. Deve ser proibido para codigo, stacktrace, SQL, specs, testes, paths e IDs.

RAGAS / ARES:

Ficam para depois do benchmark deterministico. Primeiro e preciso saber se a recuperacao encontra a fonte certa.

## 14. Definicao de Sucesso da Fase 1

A Fase 1 sera considerada bem-sucedida quando:

- O sidecar indexar uma sessao Codex grande sem tocar no `claude-mem.db`.
- O dry-run mostrar claramente quantos chunks seriam criados.
- A ingestao for idempotente.
- O SQLite FTS5 conseguir retornar resultados relevantes.
- O Chroma, se habilitado, melhorar recuperacao sem quebrar o fluxo local.
- O benchmark inicial atingir pelo menos 80% de HitRate@5 em perguntas marcadas como `required`.
- Cada resultado retornado tiver `source_path`, linhas de origem e hash.
- O rollback for apenas apagar `data/sidecar.db` e `data/chroma/`.

## 15. Norte Tecnico

O SIDE-RAG deve ser pequeno no comeco, mas correto no fundamento.

A prioridade nao e adicionar a ferramenta mais avancada. A prioridade e construir uma base confiavel:

- parse correto
- chunking rastreavel
- metadados densos
- busca medivel
- rollback simples
- MCP read-only
- evolucao guiada por benchmark

Se esse fundamento estiver correto, Qdrant, reranker, GraphRAG e outras tecnicas avancadas poderao entrar depois com clareza sobre o problema que estao resolvendo.
