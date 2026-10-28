# RAG

Documents are chunked (500 chars, 50 overlap), embedded and ranked by cosine similarity against the query.
Embeddings use OpenAI when `OPENAI_API_KEY` is set, otherwise a deterministic offline hashing embedder.
Send `use_rag: true` with a `workspace_id` to `/api/chat` to inject the top chunks (bounded by
`MAX_CONTEXT_CHARS`) into the system prompt. `/api/search/semantic` exposes the same ranking directly.
Chunks are embedded per request; add a vector store for large corpora.
