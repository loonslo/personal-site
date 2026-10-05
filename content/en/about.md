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
- [Hengcang](/en/projects/finunity/): A multi-currency household asset ledger where the Android app and the web workbench share one server-side ledger, focused on consistent calculations, per-currency and three-bucket views, and confirmation before writing data extracted from screenshots. 146 JVM unit tests pass on Android, 83 tests pass inside the server production image, and 12 tests pass on the web client deployed on 2026-10-02. Signed packages, real-device install and upgrade, and live market data remain unverified; market data is currently a clearly labelled reference sample.
- [Investment Dashboards](https://dashboards.halfopen.dev): Two public read-only dashboards covering index allocation and recurring-investment watch, plus A-share short-term money flow. Scheduled jobs refresh the snapshots, which ship with the code commits.
- [Character Profiles](https://character.halfopen.dev): A workspace for character creation material that keeps text profiles, reference images, and shared pose or expression templates in one place, with optional local LLM help for prompt refinement and image generation.

The test counts above are historical project validation records; those tests were not rerun for this site update. On 2026-10-03, the public GitHub account, study and Hengcang repositories, and the Hengcang, Investment Dashboards, and Character Profiles entry pages were checked. Reachable pages do not establish full business-flow acceptance. The project pages explain how each result was checked and what the evidence can—and cannot—show.
