---
status_note: Runnable prototype; in a personal pilot
updated: 2026-09-24
flow: Snapshot and parse sources | Keyword index + semantic index | Hybrid retrieval | Evidence window | Cited streaming answer
---

## Why I built it

My notes were spread across several libraries, so answering one question often meant searching in multiple places. The material is private, so I did not want to send it to an online service. I built a locally run knowledge assistant that keeps source files on the machine and requires answers to include citations that lead back to the original text.

## Design

- **Two retrieval paths:** SQLite FTS5 finds exact terms; a local 384-dimensional embedding model with Chroma finds paraphrases. Reciprocal Rank Fusion (RRF) combines the results.
- **Evidence windows:** Complete evidence chunks are kept within a token budget, and citation numbers in answers point back to source locations.
- **Source changes invalidate old evidence:** If an original file is changed, deleted, or unreadable, its old version and related citations become invalid. Past answers show that status instead of silently falling back to stale content.
- **Local-first:** The service binds only to the local machine. Model calls to external services and online collection are disabled by default. The project also includes personal notes, backup export and recovery, a read-only MCP server, and Windows EXE packaging.

## My role

Separated source parsing, retrieval, answering, and citations into verifiable stages; defined behavior for source changes and local permissions; and recorded retrieval performance on a frozen query set while stating which acceptance work remains.

## How it was validated

- Froze 40 queries against the old wiki baseline: 30 answerable queries (exact terms, paraphrases, and cross-document questions), 5 with no answer, and 5 unauthorized queries. Ten were used for tuning; the remaining 30 were reserved for a single acceptance run.
- Results: among 20 positive cases in the retained set, 19 retrieved at least one expected document in the top five chunks, and 17 retrieved all expected documents. Unauthorized results: 0.
- Scope of these numbers: this is a lexical retrieval baseline. Hit@5 means an expected document appears among the first five chunks; it does not measure answer accuracy. A new query set based on the original source materials has not yet been frozen.
- Regression tests cover permission boundaries, version invalidation, and backup recovery.

## Current state

- **Available:** keyword retrieval, hybrid search, streaming multi-turn Q&A, source citations and invalidation notices, personal notes, and backup export and recovery.
- **Still incomplete:** end-to-end validation of semantic retrieval, automatic ingestion of images with OCR, MCP integration with a real client, and installation checks on a clean computer.
- **Not open source yet:** licensing and model distribution terms have not been settled.
