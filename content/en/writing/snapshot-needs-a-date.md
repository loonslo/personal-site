---
title: Development note — a snapshot needs a date
date: 2026-10-29
type: practice
series: dev-note
project: dashboards
summary: A scheduled refresh is a plan; the actual snapshot timestamp shows what data a reader is seeing.
draft: false
---

The [investment dashboards](/en/projects/dashboards/) publish read-only snapshots for index-allocation observations and A-share fund flows. They are not real-time market terminals.

Before interpreting a table, a reader should be able to identify its date and methodology. Otherwise an old state can easily look current.

A scheduled job does not prove that every refresh succeeded. Collection, computation or publication can be delayed while the previous snapshot remains visible. Its actual timestamp matters more than the planned refresh interval.

Making older data recognizable is a presentation principle I want to keep improving. This article does not revalidate data accuracy or refresh reliability. Read the timestamps and definitions in the product, and do not treat this note as a trading instruction.
