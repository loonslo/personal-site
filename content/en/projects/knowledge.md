---
status_note: Runnable prototype, in a personal pilot; a read-only sample on the web needs no sign-up
updated: 2026-10-14
flow: Snapshot and parse sources | Keyword index + semantic index | Hybrid retrieval | Evidence window | Cited streaming answer
---

![The Knowledge online sample: a search for rank fusion, highlighted matches, and the original passage with its revision and lines opened under the result](/shots/knowledge-demo.en.png)
*The online sample: search a word, get the matching passages, and open the original with its revision and lines. It searches nine fictional synthetic documents only.*

## Why I built it

My notes were spread across several libraries, so answering one question often meant searching in multiple places. The material is private, so I did not want to send it to an online service. I built a local knowledge base that keeps source files on the machine and requires answers to include citations that lead back to the original text.

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
- **Online sample** (2026-10-14, live): the first result for each of the four example questions is the expected document; management, upload and chat paths return 403; keyword search only. Safari, Firefox and real devices were not tried.

## Current state

- **Available:** keyword retrieval, hybrid search, streaming multi-turn Q&A, source citations and invalidation notices, personal notes, and backup export and recovery.
- **Still incomplete:** end-to-end validation of semantic retrieval, automatic ingestion of images with OCR, MCP integration with a real client, and installation checks on a clean computer.
- **Distribution and licence:** PolyForm Noncommercial 1.0.0; the source remains private and no public download Release is available. The portable base package is for internal acceptance and includes no local models. Semantic retrieval and generation require ready dependencies and models.
- **Online sample:** open, read-only and no sign-up. It searches nine original synthetic documents (confirmed by the maintainer to contain nothing personal or third-party before release) by keyword only: no uploads, no sign-in, no vector search, no generated answers. It is not the complete local application.

## Read more

See [hybrid RAG retrieval](/en/writing/rag-hybrid-search/) for the retrieval chain, failure diagnosis and a synthetic ranking example, and [moving from testing to AI development](/en/writing/testing-to-ai-development/) for project validation.
