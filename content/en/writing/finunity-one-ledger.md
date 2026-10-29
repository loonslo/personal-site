---
title: Building FinUnity starts with explaining the numbers
date: 2026-10-29
type: practice
project: finunity
summary: Why both clients read one ledger snapshot, and what the browser-only demo can and cannot prove.
draft: false
---

Before choosing a chart for [FinUnity](/en/projects/finunity/), I want to answer a simpler question: can someone open the details and explain the number on the overview?

Separate calculations in different screens can produce plausible results that disagree. This is a design risk, not a measured history of user incidents.

## Define the accounting rules first

When cash becomes a security holding, counting both the old cash balance and the new holding can count the same money twice. The starting balance, transactions and valuation rules need clear definitions before aggregation.

Currencies need the same care. Without an exchange rate, 100 CNY and 100 USD cannot be presented as an undifferentiated total of 200. Those figures illustrate the rule; they are not real portfolio data.

## Give both clients one snapshot

The FastAPI service reads accounts, holdings, transactions and targets within one database read transaction. Android and Web consume that ledger snapshot, with monetary calculations handled using Decimal on the server.

This gives discrepancies a common place to investigate. It also means maintaining the clients and service contract together. A common snapshot cannot fix missing exchange rates or incorrect price inputs by itself.

The three-bucket view comes after this work. Comparing growth, balanced and defensive allocations with targets depends on an explainable total. The view shows allocation differences; it does not make investment decisions for the user.

## The demo needs its own checks

The Web demo offers a fictional ledger without registration. Changes stay in browser memory and reset on refresh. Its screenshot-import flow uses prepared images and results rather than sending visitors' images to a model.

That creates another implementation to compare with the server. A local verification record from October 14, 2026 compared 6,000 randomized holdings and two months of the sample ledger against server accounting functions without finding discrepancies. The browser check also verified that the demo flow did not request `/api`.

These are bounded historical results, not a fresh test run for this article. They do not validate every real portfolio, live market data, the full login flow or physical devices. Dates and outstanding checks remain in the [product record](/en/projects/finunity/).

## Keep the order clear

Define the rules, centralize calculations, check what clients display, then choose the chart. Presentation helps explain the ledger; the ledger still needs to be traceable.

[Try the fictional ledger](https://finunity.halfopen.dev/app?from=portfolio&lang=en). Using your own ledger requires registration and login.
