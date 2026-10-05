---
title: Building hybrid RAG retrieval with keywords, vectors and traceable citations
date: 2026-10-03
summary: Start with a keyword baseline, then add real vector retrieval, rank fusion, access and revision checks, evidence budgets and citation validation using a synthetic example.
draft: false
---

A fluent answer without a source and a missing exact version number are different failures. I investigate the retrieval chain before changing the prompt: keep an explainable keyword baseline, add semantic retrieval, and retain a path from each answer citation to the original text.

This walkthrough uses the approach behind my local [Knowledge project](/en/projects/knowledge/). Documents and questions below are fictional. The code demonstrates rank fusion only; it performs neither embedding nor answer generation. The [online read-only demo](https://knowledge.halfopen.dev/en/) is separate from the local application: public search stays disabled while examples are unapproved or its index is not ready.

## 1. Define the question and the accessible corpus

Imagine three notes: `install-v2` describes installation, `limits-v2` describes quotas, and `revoke-v2` describes revision invalidation. A user asks why an earlier citation stopped opening after a file changed.

Keyword retrieval may match “citation” and “revoke”; semantic retrieval may find a paraphrase about changed originals and invalid revisions. Both searches must operate within approved, accessible, current content. Store document, revision and chunk IDs alongside source identifiers and original locations. Apply access filters during retrieval and recheck current validity before returning originals or generating answers.

## 2. Establish a keyword baseline

Make exact terms, version strings and error codes recoverable first. SQLite FTS5 provides keyword search. Its `bm25()` convention ranks smaller scores ahead of larger ones, so a descending similarity sort is inappropriate here. [SQLite FTS5 documentation](https://www.sqlite.org/fts5.html#the_bm25_function)

Check tokenisation, punctuation and index coverage separately. Failure to find `v2.1` may have nothing to do with the language model. Keep fixed queries and expected evidence for exact terms, paraphrases, multiple documents, unanswered questions, inaccessible sources and invalidated revisions.

## 3. Add real vectors, then fuse ranks

Semantic retrieval requires an actual embedding model and index. Changes to the model, tokenizer, splitting parameters or corpus require corresponding index versioning. An unavailable dependency should produce a clear error or an explicitly labelled keyword mode.

Keyword scores and vector similarities need not share a scale. Reciprocal Rank Fusion adds `1 / (k + rank)` from each ranked list instead of adding raw scores. Validate `k` and candidate counts on your own queries; no fusion method guarantees improvement for every corpus. [Research on hybrid retrieval fusion](https://arxiv.org/abs/2210.11934)

This runnable example accepts **already access- and revision-filtered** chunk rankings:

```python
from collections.abc import Sequence


def rrf(rankings: Sequence[Sequence[str]], k: int = 60) -> list[str]:
    if k < 1:
        raise ValueError("k must be positive")
    scores: dict[str, float] = {}
    for ranking in rankings:
        seen: set[str] = set()
        for rank, chunk_id in enumerate(ranking, 1):
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (k + rank)
    return sorted(scores, key=lambda item: (-scores[item], item))


lexical = ["limits-v2#1", "revoke-v2#2", "install-v2#1"]
semantic = ["revoke-v2#2", "limits-v2#1"]
assert rrf([lexical, semantic])[:2] == ["limits-v2#1", "revoke-v2#2"]
```

A repeated chunk contributes once per channel; a hit from another channel adds another vote. IDs break ties deterministically. The first two chunks tie in this example, so their order does not prove relevance. A real service also needs per-document limits, weak-result handling and retrieval provenance.

## 4. Choose evidence within a context budget

Deduplicate evidence and limit any single document's share. Count the budget with the actual model tokenizer. Prefer complete evidence, or a locatable window that preserves revision details, conditions and negation.

An empty result should report that no evidence was found in the current scope. A merely related passage calls for clarification or an insufficient-evidence response. Do not turn general model knowledge into a claim about the user's files. Relevance thresholds also need validation for each model and corpus.

## 5. A valid citation is not verified truth

Map `[1]` to evidence actually included in this request, with its document, revision, chunk and location. Check that the number exists, that its text reached the model, and that access remains valid.

A legal number or lexical overlap cannot establish that every claim is supported. Read the original for important conclusions and distinguish source statements, established facts and model inference. Mark citations invalid when their sources change.

## 6. Let the failure determine the fix

| Symptom | Check first | Evidence of improvement |
| --- | --- | --- |
| Exact version missing | Tokenisation, index coverage, revision filters | The fixed query locates its original passage |
| Poor paraphrase retrieval | Model readiness, splitting, candidate counts | A separate query set improves against the keyword baseline |
| One document dominates | Duplicate windows and document limits | Necessary evidence from other sources remains |
| Answer omits a condition | Context truncation and citation mapping | Conditions survive and remain traceable |
| Citation cannot open | Current access and source validity | Explicit invalidation with no stale fallback |

Measure evidence coverage and ranking separately from answer support and citation completeness, and record latency. A top-five retrieval hit is not answer accuracy. Separate tuning queries from acceptance queries so familiar examples do not become the whole evaluation.

Read the [Knowledge case study](/en/projects/knowledge/) for project boundaries, or continue with [moving from testing to AI application development](/en/writing/testing-to-ai-development/). For project discussions and opportunities, see [experience and contact](/en/about/#contact).
