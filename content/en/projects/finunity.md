---
status_note: All three parts run; the web client has a sample ledger that needs no sign-up. Signed Android builds, real-device checks, and live market data remain unverified.
updated: 2026-10-14
flow: Enter data in the app or web client | Calculate the ledger on the server | Per-currency and three-bucket snapshot | Display and confirm on both clients
---

![Hengcang's sample ledger overview: total assets CN¥233,600; Growth, Balanced and Defensive hold 19.0%, 38.2% and 42.8% against targets of 40%, 40% and 20%](/shots/finunity-overview.en.png)
*The sample ledger's overview: the actual share of each of the three buckets against its target. Every number is fictional and changes are not saved.*

## Why I built it

If every page calculates balances independently, the overview and transaction details can disagree; across currencies and accounts it also becomes hard to say which bucket a given amount currently belongs to. I built Hengcang so the server calculates these figures once and both the Android app and the web workbench read the same result.

## Design

- **One ledger snapshot:** The FastAPI service reads accounts, holdings, transactions, and targets in one database read transaction. The Android app and the web workbench share that summary instead of recalculating it.
- **Three-bucket planning:** Assets are grouped as growth, balanced, and defensive, with target allocation, reserved funds, rebalancing, risk limits, and drawdown tiers to show the current structure.
- **Explicit currency and amount rules:** Cash balances are calculated from opening balances and transactions, then combined with holding market values. Currencies are shown separately and are not added together when an exchange rate is missing. The server uses `Decimal` for amounts.
- **Review before importing screenshots:** Holding screenshots are sent to the server for parsing only after the user confirms, and data is written only after that confirmation. The original image is used only during the recognition request.
- **Visible failure boundaries:** When prices, cost data, or live market-data integration are missing, the interface shows an estimate or an unconfigured state instead of presenting reference data as live quotes.
- **Try it without signing up:** Opening the web workbench while signed out starts a sample mode. A fictional household's holdings and six months of cash flow live in browser memory. You can see how far each bucket is from its target, add or edit holdings and transactions, change the targets, and walk through "recognise → review → save" with a built-in sample screenshot. The sample mode sends no requests to the server and returns to its original state on refresh; its ledger summary follows the server's rounding rules.

![Hengcang's sample screenshot import: a fictional holdings screenshot, three recognised rows, each reviewed before it is saved](/shots/finunity-import.en.png)
*"Recognise → review → save" in the sample: the screenshot and its result are prepared in advance, and the page says so. Using your own screenshots requires an account.*

## My role

Designed the ledger rules and business APIs shared by the three parts; implemented the web interactions, the Android interface, and the server logic; unified the calculation rules for accounts, holdings, cash flows, and three-bucket settings; and handled input validation, version conflicts, and market-data refresh failures.

## How it was validated

The "sample mode" item is a local result from 2026-10-14. The other test counts come from the project review recorded on 2026-10-02; the three test suites were not rerun for this update. On 2026-10-03, the public Android repository and web entry page were checked and were reachable. A reachable public page does not establish end-to-end sign-in or ledger validation.

- **Android:** The debug build passes and 146 JVM unit tests pass. Signed APK/AAB builds and real-device install and upgrade remain unverified.
- **Server:** 83 tests pass inside the production image, and importing a synthetic holding screenshot through a real model succeeds. Market data is currently a fixed reference sample that the interface marks as reference or stale; no live market-data provider is connected.
- **Web:** The deployed static version was updated on 2026-10-02. The production build and lint pass, along with 12 tests. The English privacy and terms pages and the API readiness check return HTTP 200, and HTTP redirects to HTTPS.
- **Sample mode (2026-10-14, local):** 39 web tests pass, 16 of them for the sample mode, including a check that it never calls `fetch`. I ran the server's own ledger functions against 6,000 random holdings and two months of the sample ledger and found no differences. A 12-step browser run in Chrome made zero requests to `/api`. Behaviour online is left to a later acceptance record.
- **Still unverified:** end-to-end sign-in and language-preference flows, real holding-screenshot imports, the production certificate chain, market-data synchronisation, and off-site backup and monitoring. The sample mode has only been tried in Chrome on one machine; Safari, Firefox, and real devices are untested.

## Current state

The Android app is [open source](https://github.com/loonslo/FinUnity). The [web workbench](https://finunity.halfopen.dev/) is publicly deployed: you can open the sample ledger without signing up (fictional data, nothing is saved), and your own ledger needs an account. All three parts support holdings, cash flows, three-bucket settings, and screenshot recognition. Market data is still reference data, and signed app packages and real-device acceptance are not done yet, so this page states both what has passed and where the boundaries are.
