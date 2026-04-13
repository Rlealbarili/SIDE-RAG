# **Spec de Implementação: RAG Sidecar de Memória (Fase 1 \- MVP)**

## **1\. Objetivo do Sprint**

Construir o pipeline ETL offline e o sistema de avaliação para um "Sidecar de Memória RAG". O objetivo é indexar os transcripts brutos locais do Codex (\~/.codex) em um banco de dados relacional próprio com busca lexical (SQLite FTS5), provando o valor da segmentação de contexto com um benchmark determinístico, antes de avançar para buscas vetoriais pesadas ou integrações MCP.

## **2\. Princípios e Restrições de Engenharia**

1. **Isolamento Total:** O sidecar deve viver em tools/memory-rag/. Não bloquear, alterar ou escrever no claude-mem.db existente.  
2. **Minimalismo Inicial:** Sem LlamaIndex no caminho crítico. Usar parser JSONL customizado puro em Python.  
3. **Busca Progressiva:** O baseline é busca lexical via SQLite FTS5. Embeddings e Rerankers devem ser opcionais no script, controlados por flags.  
4. **Idempotência:** A ingestão deve permitir rodar múltiplas vezes sem duplicar dados, baseando-se em source\_hash.  
5. **Atraso do MCP:** A interface MCP (read-only) só será implementada após os scripts de ingest e eval passarem nos critérios de aceite.

## **3\. Layout do Repositório**

O código deve ser construído estritamente dentro da pasta do projeto atual:

tools/memory-rag/  
├── data/                  \# SQLite próprio (sidecar.db) e Chroma DB (gitignored)  
├── evals/                 \# eval\_queries.json e resultados do benchmark  
├── mcp/                   \# (Vazio nesta fase \- aguardando aprovação do eval)  
├── src/  
│   ├── parsers/           \# Parser customizado (json, regex) para \~/.codex  
│   ├── indexer/           \# Lógica de chunking e persistência (SQLite \+ Chroma opcional)  
│   ├── retrieval/         \# Busca FTS5 (Lexical) e Vectorial/Reranker (Opcionais)  
│   └── schema.py          \# Modelos Pydantic (ChunkModel, QueryEval)  
├── scripts/  
│   ├── ingest\_codex.py    \# CLI para extração e indexação  
│   └── eval\_retrieval.py  \# CLI para rodar o benchmark  
└── requirements.txt       \# pydantic, chromadb (sqlite3 é nativo)

## **4\. Modelo Canônico de Dados (src/schema.py)**

A tabela SQLite chunks (com FTS5 ativado na coluna content) deve espelhar este schema:

class ChunkModel(BaseModel):  
    chunk\_id: str             \# UUID gerado na indexação  
    project\_id: str           \# ex: "Sis\_Marcos\_Inventario"  
    session\_id: str           \# ID original do transcript (ex: 019cd2ee-...)  
    content: str              \# O texto/código extraído do turno  
    source\_hash: str          \# MD5(content \+ session\_id \+ source\_line\_start)  
    source\_path: str          \# Caminho do arquivo bruto original  
    source\_event\_type: str    \# "user\_prompt", "agent\_tool\_call", "agent\_answer"  
    source\_line\_start: int    \# Linha de início no JSONL bruto  
    source\_line\_end: int      \# Linha de fim no JSONL bruto  
    timestamp: str            \# ISO 8601

**Regras de Imunidade a Resumos:**

Os blocos de código (\`\`\`), stacktraces (Traceback...), saídas de testes, queries SQL e tags de specs (\<spec\>) **nunca** devem sofrer sumarização durante a extração.

## **5\. Benchmark Determinístico (evals/eval\_queries.json)**

O benchmark utiliza métricas determinísticas (HitRate@5, MRR). Se os arrays expected\_terms, expected\_files ou expected\_chunk\_ids forem encontrados nos metadados ou conteúdo do Top-K, pontua.

*Exemplo de schema no JSON:*

\[  
  {  
    "id": "q001",  
    "query": "Qual foi a decisão sobre CAPTCHA no SIGEF e estado awaiting\_captcha?",  
    "expected\_files": \["src/auth/captcha.ts"\],  
    "expected\_terms": \["awaiting\_captcha", "hcaptcha"\],  
    "expected\_chunk\_ids": \[\],   
    "project": "Sis\_Marcos\_Inventario",  
    "required": true,  
    "source\_hint": "Decisão tomada na sessão 019cd2ee..."  
  },  
  {  
    "id": "q002",  
    "query": "Como o IRON-SERVER lida com reconexões falhas?",  
    "expected\_files": \["iron-server/connection.py"\],  
    "expected\_terms": \["reconnect\_backoff", "timeout"\],  
    "expected\_chunk\_ids": \[\],  
    "project": "Sis\_Marcos\_Inventario",  
    "required": false,  
    "source\_hint": "Pode não estar no histórico principal ainda."  
  }  
\]

## **6\. Comandos Executáveis (CLIs)**

**Comando 1: Ingestão**

O script deve ler o session.jsonl bruto, fazer o parse customizado agrupando interações lógicas, gerar o source\_hash e fazer o UPSERT no SQLite.

python tools/memory-rag/scripts/ingest\_codex.py \\  
  \--session-id 019cd2ee-xxxx-xxxx \\  
  \--project Sis\_Marcos\_Inventario \\  
  \--no-embeddings \\  
  \--dry-run

*(Remover \--dry-run para aplicar. O flag \--no-embeddings desliga o ChromaDB, focando apenas no SQLite FTS5 para o primeiro teste rápido).*

**Comando 2: Avaliação (Benchmark)**

python tools/memory-rag/scripts/eval\_retrieval.py \\  
  \--queries tools/memory-rag/evals/eval\_queries.json \\  
  \--top-k 5 \\  
  \--reranker none

*(Flags de reranker permitidas futuramente: none, miniLM, bge-m3).*

## **7\. Rollback e Idempotência**

* **Idempotência:** Baseada na coluna única source\_hash. Se uma linha do transcript já existir (mesmo hash), ignora. Se o conteúdo mudar (ajuste no parser), realiza UPDATE/UPSERT substituindo pelo novo chunk\_id e conteúdo.  
* **Rollback Completo:** Como o sistema é isolado, basta deletar tools/memory-rag/data/sidecar.db e a pasta tools/memory-rag/data/chroma/. Nenhum estado do claude-mem produtivo é afetado.

## **8\. Critérios de Aceite (DoD)**

1. Estrutura de pastas, schema.py e requirements.txt criados e válidos.  
2. ingest\_codex.py executa o parse customizado e popula o sidecar.db com o schema correto, preservando a rastreabilidade (source\_line\_start/end, source\_path).  
3. O script de ingestão respeita as regras de idempotência (rodar 2x na mesma sessão não duplica dados).  
4. eval\_retrieval.py executa buscando apenas no FTS5 (quando \--reranker none e sem vetores) e exibe latência média, HitRate@5 e MRR no terminal.  
5. Em nenhum momento o arquivo claude-mem.db original é modificado ou bloqueado por locks.