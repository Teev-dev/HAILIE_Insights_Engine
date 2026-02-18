# Architecture Drift Audit Report

**Author:** Generated with Claude Code
**Date:** February 2026
**Scope:** Comparison of original architecture blueprint (Aug 2025) against current production codebase

## Summary

The current Streamlit/DuckDB monolith architecture is the **correct architecture** for this stage of the product. The pivot from the original AWS cloud-native design was deliberate, well-reasoned, and documented in ADR-001. This report confirms that finding and identifies a small number of undocumented decisions that should be formalised as ADRs for completeness.

## Documented Architecture Changes

All major architectural changes from the original blueprint are covered by existing ADRs:

| Original Blueprint (Aug 2025) | Current Implementation | Documented In |
|---|---|---|
| React.js/Vue.js frontend | Streamlit `app.py` + `dashboard.py` | ADR-001 |
| AWS Cognito auth + RBAC | No auth (single-tenant, public data) | ADR-001 |
| Node.js/Express or Python/Django API | Direct Python function calls | ADR-001 |
| PostgreSQL on AWS RDS | DuckDB embedded database | ADR-001 |
| S3 + Lambda + SQS file processing | Python ETL script (`build_analytics_db_v2.py`) | ADR-001 |
| Redis (ElastiCache) caching | DuckDB pre-calculations replace cache | ADR-001 |
| CloudFront CDN | Streamlit serves directly | ADR-001 |
| Multi-AZ deployment | Single Replit autoscale instance | ADR-001 |
| REST/GraphQL API | No API layer | ADR-001 |
| Terraform/CloudFormation IaC | No IaC | ADR-001 |
| GitHub Actions/CodePipeline CI/CD | No CI/CD pipeline | ADR-001 |
| Single dataset (LCRA only) | LCRA + LCHO with peer isolation | ADR-002 |
| Single year, replace-on-load | Multi-year append with year column | ADR-003 |

## Undocumented Decisions (Recommend New ADRs)

These decisions were made deliberately but lack formal ADR documentation:

### 1. Data Upload Removed
- **Original spec:** User-facing Excel/CSV upload with drag-and-drop interface
- **Current:** No upload UI; data is government-published and bundled via offline ETL
- **Rationale:** The TSM dataset is published by the UK government. Users should consume official data, not upload their own. This ensures data integrity and consistency.
- **Recommendation:** Create ADR-004 documenting this decision

### 2. Authentication & RBAC Deferred
- **Original spec:** AWS Cognito with user groups, JWT tokens, role-based access
- **Current:** No authentication; public-facing dashboard
- **Rationale:** All data is from publicly available government datasets with no PII. Auth adds complexity without clear benefit at current scale.
- **Recommendation:** Create ADR-005 if/when auth is reconsidered

### 3. Export/Reporting Deferred
- **Original spec:** CSV and PDF export functionality
- **Current:** Not implemented; listed on `FEATURES_ROADMAP.md`
- **Rationale:** Core analytics value delivered first; export is an enhancement
- **Recommendation:** Track on roadmap (already done)

## Architecture v2 Document Corrections

The in-repo `HAILIE-Insights-Engine-Architecture-v2.md` is mostly accurate but has minor discrepancies with the current code:

| Document Says | Code Actually Has | Fix |
|---|---|---|
| `calculation_date DATE` in schema | `year INTEGER` column (per ADR-003) | Update schema in doc |
| DuckDB 0.10.x | `duckdb>=1.4.1` in pyproject.toml | Update version in doc |
| Database ~2MB | `hailie_analytics_v2.duckdb` is 8.4MB (multi-year data) | Update size in doc |
| Momentum "ready for 2026" | Momentum is implemented and working with 2024+2025 data | Update status in doc |
| File structure shows only ADR-001 | ADR-002 and ADR-003 also exist | Add to file structure |

## Non-Functional Requirements Gap Analysis

Cross-referencing the Key Considerations document against current implementation:

| Requirement | Status | Notes |
|---|---|---|
| **Scalability** | Adequate | DuckDB handles data well; single-instance is fine for current load |
| **Accessibility** | Partial | Desktop path uses `unsafe_allow_html`; mobile path uses native Streamlit components. Future work to improve. |
| **Security** | Adequate | HTTPS via hosting; read-only DB; no PII; public data only |
| **Observability** | Gap | No error logging or monitoring. **Sentry.io integration planned.** |
| **Usability** | Strong | Executive dashboard, mobile support, tooltips |
| **Reliability** | Partial | No alerting when errors occur. **Sentry.io will address this.** |
| **Performance** | Strong | Pre-calculated analytics, <100ms queries, <2s page load |
| **Maintainability** | Good | Clear module separation, 3 ADRs, but no automated test suite |
| **Interoperability** | Not started | API layer on roadmap |

## Conclusion

The architecture is sound for the current product stage. The pivot from enterprise AWS to Streamlit/DuckDB was the right call — it enabled rapid delivery of a working product to real users. The three areas to address next are: observability (Sentry), ETL robustness (column detection), and deployment independence (Railway migration).
