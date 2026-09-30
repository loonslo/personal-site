---
status_note: Web and server prototype; public deployment and end-to-end validation remain unverified
updated: 2026-09-05
flow: Enter accounts and holdings | Calculate ledger on the server | Per-currency snapshot | Review and confirm in the web client
---

## Why I built it

If every page calculates balances independently, the overview and transaction details can disagree. I built FinUnity Web + Server so the server calculates account, holding, and cash-flow data consistently, while a web client presents and operates on it.

## Design

- **One ledger snapshot:** The FastAPI service reads accounts, holdings, transactions, and targets in one database read transaction. The React web overview, account, holding, and settings pages all use the same summary.
- **Explicit currency and amount rules:** Cash balances are calculated from opening balances and transactions, then combined with holding market values. Currencies are shown separately and are not added together when an exchange rate is missing. The server uses `Decimal` for amounts.
- **Review before importing screenshots:** Holding screenshots can be parsed into structured records, but data is written only after user confirmation. The original image is used only during the recognition request.
- **Visible failure boundaries:** When prices, cost data, or live market-data integration are missing, the interface shows an estimate or an unconfigured state instead of presenting reference data as live quotes.

## My role

Implemented web interactions and server business APIs; clarified calculation rules for accounts, holdings, cash flows, and settings; fixed inconsistencies caused by duplicated calculations across pages; and added handling for input validation, version conflicts, and market-data refresh failures.

## How it was validated

- A consistency-fix record from September 2026 reports that the frontend production build, Oxlint, and backend Ruff passed, along with 35 passing backend pytest cases. Coverage included per-entry rounding, currency isolation, invalid input, version conflicts, and market-data refresh failures.
- That record did not include browser interactions, mobile visual checks, or live market-data integration. Recent deployment status and complete end-to-end acceptance remain unverified.

## Current state

The web and server code supports accounts, holdings, cash flows, three-bucket allocation settings, and screenshot-based holding recognition. No live market-data provider is connected; the current reference data is for integration testing. There is no verified public entry point for the Web + Server, so this page describes the design and validation boundaries only.
