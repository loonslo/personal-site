---
status_note: Under active development; repository is private
updated: 2026-09-24
flow: Candidate generation | Syntax and structure checks | BRAIN simulation | Multi-metric evaluation | Bounded tuning | Report | Human-approved submission
---

## Why I built it

A good-looking single backtest on WorldQuant BRAIN does not prove that an Alpha is usable, and testing expressions one by one makes it hard to explain why a candidate passed or was dropped. I wanted to turn the research process into a traceable pipeline.

## Design

- **One workflow from start to finish:** A Python CLI connects candidate generation, local syntax and structure checks, BRAIN simulation, metric evaluation, bounded tuning, and reporting.
- **Consistent multi-metric evaluation:** Sharpe, Fitness, turnover, drawdown, and autocorrelation are assessed against a shared set of criteria. Candidates that pass the baseline metrics can then go through bounded robustness probes.
- **Recoverable batches:** Research batches are persisted and support pre-run checks and backup recovery, along with state inspection, resume, and cancellation through LangGraph.
- **People decide what gets submitted:** The tool produces reports and recommendations. A person always confirms whether to submit.

## My role

Organized the research steps into recoverable batches; defined boundaries for local checks, platform simulations, multi-metric evaluation, and bounded tuning; and kept human approval and report lookup in the workflow.

## How it was validated

- Candidates pass local syntax and structure checks before they can enter platform simulation.
- Decisions do not rely on a single in-sample backtest: bounded robustness probes follow multi-metric evaluation.
- Each batch keeps a report so the reasons for passing or dropping a candidate can be reviewed.

## What is not public

Expressions, data fields, and submission details are not disclosed. This page covers only the methods and engineering practices.
