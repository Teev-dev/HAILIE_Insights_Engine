# HAILIE Insights Engine — Masterplan

## The Problem

UK social housing providers are required to collect and report Tenant Satisfaction Measures (TSM) to the Regulator of Social Housing. The government publishes this data annually, but providers have no easy way to understand what it means for them:

- **No instant context**: A score of 72% means nothing without knowing where you stand among peers.
- **No actionable guidance**: Providers can see their numbers but not which one to focus on improving.
- **No trajectory**: Year-on-year trends are buried in spreadsheets.
- **Manual effort**: Comparing yourself to 350+ other providers requires significant analyst time.

The sector needs a tool that turns raw regulatory data into decisions — not more spreadsheets.

## The Vision

**Every social housing provider in England can instantly understand their tenant satisfaction performance, see where they stand among peers, and know exactly what to improve next.**

HAILIE Insights Engine does this by transforming published government TSM data into three executive-level insights, delivered in seconds with zero configuration.

## Core Principles

1. **Insight over information** — Three answers, not twelve tables. Rank, Momentum, Priority.
2. **Peer fairness** — LCRA and LCHO providers are never compared against each other. Apples with apples.
3. **Data integrity** — Pre-calculated analytics from official government datasets. No estimates, no projections.
4. **Zero friction** — Select your provider code, get your insights. No login, no setup, no training.
5. **Open source** — The sector should own its tools. This project is open for contribution, scrutiny, and reuse.
6. **Production-grade** — Reliable, secure, and built for real-world use — not a prototype.

## What It Does Today

### Three Executive Insights

| Insight | What It Answers | How |
|---------|----------------|-----|
| **Your Rank** | "Where do I stand?" | Quartile position across all 12 TSM measures vs peer providers |
| **Your Momentum** | "Which direction am I heading?" | Year-on-year trajectory (available when multi-year data exists) |
| **Your Priority** | "What should I focus on?" | Correlation analysis identifies the single measure most likely to improve overall satisfaction |

### Data Coverage

- **LCRA**: 355 providers, 12 measures (TP01–TP12) — full satisfaction and repairs
- **LCHO**: 56 providers, 9 measures (TP01, TP05–TP12) — repairs not applicable
- **Automatic detection**: System identifies provider type and isolates peer comparisons

### Technical Foundation

- **Streamlit** web interface — responsive across desktop, tablet, mobile
- **DuckDB** embedded analytics database — pre-calculated metrics for sub-second response
- **Python** analytics engine — Spearman correlations, percentile rankings, statistical analysis
- **Self-contained** — no external API dependencies, no cloud services required

## Who It's For

- **Housing executives** who need a quick, clear picture of performance
- **Board members** preparing for regulatory discussions
- **Performance teams** identifying where to direct improvement efforts
- **Sector analysts** benchmarking across the provider landscape
- **Contributors** (developers, domain experts, housing professionals) who want to improve tools for the sector

## Where It's Heading

The roadmap (see `FEATURES_ROADMAP.md`) includes:

- **Multi-year trend analytics** — track performance trajectory as annual data accumulates
- **Peer group filtering** — compare by provider size, region, or type
- **PDF export** — downloadable executive summaries for boards
- **API layer** — integrate insights into other housing systems
- **Scenario planning** — "what if we improved TP10 by 5 points?"

These are possibilities, not commitments. The focus remains on delivering maximum value with minimal complexity.

## How to Contribute

See `guides/collaboration-protocol.md` for the full contributor framework, including:

- Contributor ladder (Observer → Maintainer)
- Domain expert (non-code) contribution paths
- AI agent constitution and guardrails
- Security disclosure process

## Project Governance

- **Architecture decisions** are recorded in `ADRs/`
- **Feature ideas** live in `FEATURES_ROADMAP.md`
- **This document** defines the why and the what — it is the north star

---

*HAILIE: Housing Analytics & Insights for Leadership Excellence*
