---
title: From software testing to AI application development: choosing and validating projects
date: 2026-10-03
summary: Turn API testing, test data and failure analysis into a complete AI project, with repeatable checks for success, failure and recovery and clear evidence boundaries.
draft: false
---

Testing experience provides a useful starting point for AI application development: understanding contracts, preparing data, diagnosing failures and deciding whether a result is reproducible. The next step is connecting requirements, data, implementation and a usable entry point, then taking responsibility for the outcome.

My [experience and projects](/en/about/) span software testing, Python tools and AI applications. This article describes how I choose personal projects and organise validation, along with a framework for preparing a comparable portfolio. It is practice advice, not a guarantee of employment or a requirement to learn every framework at once.

## 1. Pick a problem you can explain

Start with a recurring difficulty rather than a framework list. “Find original evidence in selected files” gives you an identifiable corpus, access scope, expected passages and behaviour when no answer exists.

Complete one loop first: independent sample data, import, retrieval and original-location display. Add real vectors and generation later. Each addition should address an identifiable failure.

My [Knowledge case study](/en/projects/knowledge/) focuses on retrieval, citations and revision validity. The [Alpha Research Toolkit case study](/en/projects/alpha-research/) focuses on recoverable research batches. Its public account describes engineering methods without disclosing expressions or platform-submission details.

## 2. Turn testing skills into development evidence

| Existing experience | Application to an AI project | Evidence to retain |
| --- | --- | --- |
| API testing | Define input, output and error contracts | Samples and expected behaviour |
| Test data management | Separate synthetic data, approved content and real accounts | Sources and isolation boundaries |
| Regression automation | Check stable access, revision and workflow rules | Repeatable assertions |
| Failure analysis | Separate retrieval, model, storage and UI failures | Diagnosis and repair records |
| Performance checks | Measure retrieval, generation and total latency | Comparable measurement conditions |

Explain responsibilities as well as code. In a library, the parser produces text and locations; retrievers select accessible candidates; generation receives selected evidence; the UI presents sources and failure states. Importing content, approving publication and invoking a model should be explicit operations.

## 3. Check success, failure and recovery

A useful acceptance checklist goes beyond a successful screen recording:

- **Success:** selected examples are retrievable and their original locations open.
- **No evidence:** unanswered queries do not become claims about the files.
- **Access:** anonymous or other users cannot read out-of-scope content.
- **Dependency failure:** unavailable models, timeouts and missing indexes report clear states.
- **Revision changes:** modified or deleted originals no longer count as current evidence.
- **Recovery:** interruptions and restarts leave understandable state; repeating an operation does not silently duplicate its result.

Automate deterministic access and workflow checks. Generated text needs separate review for evidence support, missing conditions and wording; HTTP 200 does not establish answer quality. Make test samples reconstructable. pytest fixtures can organise isolated setup and cleanup. [Official pytest fixture guide](https://docs.pytest.org/en/stable/how-to/fixtures.html)

## 4. State what each result measures

For every validation record, include its date, code or configuration version, sample scope, method, actual result and untested items.

“Tests pass” needs a coverage scope. “Retrieval works” needs a distinction between synthetic examples and approved real content. “Hybrid is better” needs the same query set and a baseline. “Deployed” needs an actual check of the production URL.

My public case studies retain some historical retrieval results and identify the limits of those results, including incomplete end-to-end semantic validation. Traceable evidence and remaining problems provide a better basis for discussion than an unexplained accuracy claim.

## 5. Build a discussable project in four iterations

This is an adaptable sequence, not a fixed learning timetable:

1. Write a short requirement with inputs, outputs, corpus boundaries and failure behaviour; prepare synthetic examples.
2. Complete a local loop with familiar technology, a runnable entry point and source display.
3. Add one new capability and compare it with the baseline; record unavailable dependencies and failure branches.
4. Prepare the README, architecture, repeatable checks and demo; remove real accounts, private content and credentials before deciding what can be public.

My [AI application study repository](https://github.com/loonslo/langchain-learning) indicates the learning direction; the [project cases](/en/#projects) show how I present engineering work. Repository availability depends on its current permissions, and these pages do not offer private source downloads.

For a concrete retrieval chain and a synthetic ranking example, continue with [hybrid RAG retrieval](/en/writing/rag-hybrid-search/). My responsibilities, career direction and contact details are on [experience and contact](/en/about/#contact).
