---
title: Experience & Career Direction
summary: 半開's experience spans software testing, Python development, and product management, with published project validation notes and contact details for opportunities.
---

This page outlines my responsibilities, project validation results, and what remains unverified. For a short introduction, see the [home page](/en/); to request my resume, use the [email address](#contact).

## Experience and roles

- **Software testing (primary experience):** API and UI automation, performance testing, and validation of large-scale data metrics. I carry test methods, failure boundaries, and traceable evidence into my personal projects.
- **Python development (additional role):** Built tools to improve testing efficiency and automate business workflows; I continue to use Python for services and workflows in my personal projects.
- **Product management (additional role):** Contributed to requirements analysis, product prototypes, iterative delivery, and acceptance discussions.
- **AI applications and full-stack development (current direction):** Build RAG services with Python and FastAPI, organize recoverable workflows with LangGraph, and develop web clients with React and TypeScript.

## Personal projects

- [Private Knowledge Assistant](/en/projects/knowledge/): A locally run assistant for private materials with keyword and semantic retrieval and traceable sources. In a retained set from an older wiki lexical baseline, 19 of 20 positive cases retrieved at least one expected document in the top five chunks (Hit@5), and 17 retrieved all expected documents; there were zero unauthorized results. This measures retrieval, not answer accuracy. End-to-end validation of the semantic pipeline is still incomplete.
- [WorldQuant Alpha Research Toolkit](/en/projects/alpha-research/): A traceable research workflow connecting candidate generation, simulation, evaluation, and human review. Its project page describes the validation and disclosure boundaries.
- [AI Application Development Study Repo](https://github.com/loonslo/langchain-learning): Ongoing course notes and code documenting my move from testing into AI application development.
- [FinUnity Web + Server](/en/projects/finunity/): A personal finance ledger focused on consistent calculations, per-currency views, and confirmation before writing data extracted from screenshots. A consistency-fix record from September 2026 reports 35 passing backend pytest cases covering per-entry rounding, currency isolation, invalid input, version conflicts, and market-data refresh failures. The frontend production build, Oxlint, and backend Ruff also passed. That record did not cover browser interactions or live market-data integration; recent deployment and full end-to-end validation remain unverified.

The project pages explain how each result was checked and what the evidence can—and cannot—show.
