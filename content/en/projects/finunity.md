---
status_note: All three parts run; the web client is publicly deployed. Signed Android builds, real-device checks, and live market data remain unverified.
updated: 2026-10-03
flow: Enter data in the app or web client | Calculate the ledger on the server | Per-currency and three-bucket snapshot | Display and confirm on both clients
---

## Why I built it

If every page calculates balances independently, the overview and transaction details can disagree; across currencies and accounts it also becomes hard to say which bucket a given amount currently belongs to. I built Hengcang so the server calculates these figures once and both the Android app and the web workbench read the same result.

## Design

- **One ledger snapshot:** The FastAPI service reads accounts, holdings, transactions, and targets in one database read transaction. The Android app and the web workbench share that summary instead of recalculating it.
- **Three-bucket planning:** Assets are grouped as growth, stable, and defensive, with target allocation, reserved funds, rebalancing, risk limits, and drawdown tiers to show the current structure.
- **Explicit currency and amount rules:** Cash balances are calculated from opening balances and transactions, then combined with holding market values. Currencies are shown separately and are not added together when an exchange rate is missing. The server uses `Decimal` for amounts.
- **Review before importing screenshots:** Holding screenshots are sent to the server for parsing only after the user confirms, and data is written only after that confirmation. The original image is used only during the recognition request.
- **Visible failure boundaries:** When prices, cost data, or live market-data integration are missing, the interface shows an estimate or an unconfigured state instead of presenting reference data as live quotes.

## My role

Designed the ledger rules and business APIs shared by the three parts; implemented the web interactions, the Android interface, and the server logic; unified the calculation rules for accounts, holdings, cash flows, and three-bucket settings; and handled input validation, version conflicts, and market-data refresh failures.

## How it was validated

The test counts below come from the project review recorded on 2026-10-02; the three test suites were not rerun for this update. On 2026-10-03, the public Android repository and web entry page were checked and were reachable. A reachable public page does not establish end-to-end sign-in or ledger validation.

- **Android:** The debug build passes and 146 JVM unit tests pass. Signed APK/AAB builds and real-device install and upgrade remain unverified.
- **Server:** 83 tests pass inside the production image, and importing a synthetic holding screenshot through a real model succeeds. Market data is currently a fixed reference sample that the interface marks as reference or stale; no live market-data provider is connected.
- **Web:** The deployed static version was updated on 2026-10-02. The production build and lint pass, along with 12 tests. The English privacy and terms pages and the API readiness check return HTTP 200, and HTTP redirects to HTTPS.
- **Still unverified:** end-to-end sign-in and language-preference flows, real holding-screenshot imports, the production certificate chain, market-data synchronisation, and off-site backup and monitoring.

## Current state

The Android app is [open source](https://github.com/loonslo/FinUnity), and the [web workbench](https://finunity.halfopen.dev/) is publicly deployed behind a sign-in. All three parts support accounts, holdings, cash flows, three-bucket settings, and screenshot recognition. Market data is still reference data, and signed app packages and real-device acceptance are not done yet, so this page states both what has passed and where the boundaries are.
