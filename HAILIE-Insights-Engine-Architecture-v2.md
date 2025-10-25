# HAILIE Insights Engine - Architecture v2.0
**Author:** TS  
**Date:** October 2025  
**Status:** Current Production Architecture  

## Executive Summary

The HAILIE Insights Engine is a specialized analytics platform that transforms UK Government TSM (Tenant Satisfaction Measures) data into actionable executive insights for social housing providers. Built on Streamlit and DuckDB, it delivers three core insights: provider rankings, performance momentum, and improvement priorities through an executive-friendly dashboard.

## System Overview

### Architecture Style
**Monolithic Analytics Application** - A unified Python application combining data processing, analytics computation, and web presentation layers with an embedded analytics database.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Streamlit Web App)                     │
│                      Port 5000                           │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │  Analytics   │  │     Data     │  │
│  │  Components  │  │    Engine    │  │  Processor   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Storage Layer                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │            DuckDB Analytics Database               │ │
│  │   • raw_scores                                     │ │
│  │   • calculated_percentiles                         │ │
│  │   • calculated_correlations                        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Source                           │
│         UK Government TSM Excel Dataset                  │
│            (Annual Publication)                          │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Layer - Streamlit Web Application

**Purpose:** Delivers interactive executive dashboards with data visualizations

**Technology:** Streamlit 1.x with custom CSS styling

**Key Features:**
- Single-page application with sidebar navigation
- Three-metric executive summary (Rank, Momentum, Priority)
- Interactive Plotly charts for data visualization
- Responsive design for desktop and tablet viewing
- Custom CSS for professional branding

**Implementation Files:**
- `app.py` - Main application entry point
- `dashboard.py` - Executive dashboard rendering
- `styles.py` - Custom CSS styling and themes
- `tooltip_definitions.py` - Help text and user guidance
- `mobile_utils.py` - Mobile responsiveness detection and adaptive layouts

### 2. Analytics Engine

**Purpose:** Performs statistical analysis and generates insights from pre-calculated data

**Technology:** Python with NumPy, SciPy, Pandas

**Core Capabilities:**
- **Ranking Analysis:** Quartile-based peer comparison using percentiles
- **Momentum Tracking:** Year-over-year performance trend analysis (ready for 2026)
- **Priority Identification:** Correlation-based improvement area detection
- **Statistical Methods:** Spearman correlation, percentile rankings, weighted scoring

**Implementation Files:**
- `analytics_refactored.py` - Core analytics algorithms
- Pre-calculated metrics retrieved from DuckDB for instant analysis

### 3. Data Processing Layer

**Purpose:** Manages all database interactions and data retrieval

**Technology:** DuckDB Python client with connection pooling

**Responsibilities:**
- Database connection management
- Query execution and result formatting
- Data validation and error handling
- Cache management for frequently accessed data

**Implementation Files:**
- `data_processor_enhanced.py` - Enhanced database access layer with LCRA/LCHO support
- SQL queries optimized for columnar storage

### 4. ETL Pipeline

**Purpose:** Transforms raw Excel data into optimized analytics database

**Technology:** Python with Pandas, OpenPyXL

**Process Flow:**
1. **Extract:** Read TSM Excel file from government dataset
2. **Transform:** 
   - Parse TP01-TP12 satisfaction measures
   - Convert wide format to long format
   - Calculate percentile ranks for each measure
   - Compute Spearman correlations with overall satisfaction
3. **Load:** Create optimized DuckDB database with pre-calculated analytics

**Implementation Files:**
- `build_analytics_db.py` - Complete ETL pipeline for LCRA dataset
- `build_analytics_db_v2.py` - Enhanced ETL pipeline with LCRA/LCHO support
- Processes 355 LCRA providers + 56 LCHO providers with full dataset isolation

### 5. Diagnostic and Maintenance Tools

**Purpose:** Data quality monitoring, integrity checking, and database inspection

**Technology:** Python with Pandas, DuckDB

**Utilities:**
- **Database Viewer:** Inspect database contents and schema
- **Duplicate Diagnosis:** Identify and resolve data duplication issues
- **Statistical Review:** Analyze p-values and correlation significance

**Implementation Files:**
- `db_view_script.py` - Interactive database content viewer
- `diagnose_duplicates.py` - Data integrity and duplication checker
- `review_pvalues.py` - Statistical significance analysis for correlations

### 6. Data Storage - DuckDB Analytics Database

**Purpose:** High-performance analytics database with pre-calculated metrics

**Technology:** DuckDB 0.10.x embedded database

**Schema Design:**

```sql
-- Core data table with all TSM scores
CREATE TABLE raw_scores (
    provider_code VARCHAR,
    provider_name VARCHAR,
    year INTEGER,
    tp_measure VARCHAR,  -- TP01 through TP12
    score FLOAT
);

-- Pre-calculated percentile rankings
CREATE TABLE calculated_percentiles (
    provider_code VARCHAR,
    tp_measure VARCHAR,
    percentile_rank FLOAT,  -- 0-100 percentile
    calculation_date DATE
);

-- Pre-calculated correlations with TP01
CREATE TABLE calculated_correlations (
    tp_measure VARCHAR,
    correlation_with_tp01 FLOAT,  -- Spearman correlation
    p_value FLOAT,
    sample_size INTEGER,
    calculation_date DATE
);
```

**Storage Characteristics:**
- Columnar storage format optimized for analytics
- File size: ~2MB for complete dataset
- Query performance: <100ms for complex aggregations
- Location: `attached_assets/hailie_analytics_v2.duckdb`

## Data Flow Architecture

### 1. One-Time ETL Process (Annual)
```
Government Excel Dataset
        │
        ▼
   ETL Pipeline
   (build_analytics_db.py)
        │
        ├─→ Extract TSM Data
        ├─→ Calculate Percentiles
        ├─→ Compute Correlations
        └─→ Load to DuckDB
```

### 2. Runtime Query Flow
```
User Selects Provider
        │
        ▼
   Dashboard Request
        │
        ▼
   Analytics Engine
        │
        ├─→ Retrieve Pre-calculated Percentiles
        ├─→ Retrieve Correlations
        ├─→ Calculate Composite Scores
        └─→ Generate Insights
        │
        ▼
   Render Dashboard
```

## Technical Stack

### Core Dependencies
- **Python 3.11** - Primary programming language
- **Streamlit** - Web application framework
- **DuckDB** - Embedded analytics database
- **Pandas** - Data manipulation and ETL
- **NumPy** - Numerical computations
- **SciPy** - Statistical analysis
- **Plotly** - Interactive visualizations
- **OpenPyXL** - Excel file processing

### Deployment Environment
- **Platform:** Replit
- **Server:** Streamlit server on port 5000
- **Configuration:** `.streamlit/config.toml`
- **Workflow:** `streamlit run app.py --server.port 5000`

## Performance Characteristics

### Database Performance
- **Initial Load:** 5-10 seconds for ETL pipeline
- **Query Response:** <100ms for pre-calculated metrics
- **Concurrent Users:** Supports 10-20 simultaneous users
- **Memory Usage:** ~50MB resident memory

### Application Performance
- **Page Load:** <2 seconds initial load
- **Interaction Response:** <500ms for dashboard updates
- **Chart Rendering:** <1 second for complex visualizations

## Data Model

### TSM Measures
The system processes 12 government-defined satisfaction measures:

| Code | Description |
|------|-------------|
| TP01 | Overall satisfaction |
| TP02 | Satisfaction with repairs |
| TP03 | Time taken to complete most recent repair |
| TP04 | Satisfaction with time taken for repair |
| TP05 | Satisfaction that home is well-maintained |
| TP06 | Satisfaction that home is safe |
| TP07 | Satisfaction with neighbourhood |
| TP08 | Landlord's contribution to neighbourhood |
| TP09 | Approach to handling complaints |
| TP10 | Agreement that landlord treats residents fairly |
| TP11 | Landlord listens to residents' views |
| TP12 | Approach to handling anti-social behaviour |

### Provider Data Structure
- **Provider Code:** Unique government identifier
- **Provider Name:** Organization name
- **TSM Scores:** Percentage values for each TP measure
- **Calculated Metrics:** Percentiles, rankings, correlations

## Key Design Decisions

### 1. Pre-Calculated Analytics
**Decision:** Calculate all metrics during ETL rather than runtime  
**Rationale:** Instant query response, reduced computational overhead  
**Trade-off:** Increased storage (minimal impact at current scale)

### 2. Embedded Database
**Decision:** Use DuckDB instead of client-server database  
**Rationale:** Zero configuration, optimal for read-heavy analytics  
**Trade-off:** Single-machine constraint

### 3. Monolithic Architecture
**Decision:** Single Python application vs microservices  
**Rationale:** Simplified deployment, easier maintenance  
**Trade-off:** Less granular scaling options

### 4. Streamlit Framework
**Decision:** Streamlit over traditional web frameworks  
**Rationale:** Rapid development, built-in data components  
**Trade-off:** Less customization flexibility

## Error Handling Strategy

### Data Validation
- Excel format verification during ETL
- Null value handling for missing scores
- Percentile calculation validation
- Correlation significance testing

### Runtime Errors
- Database connection retry logic
- Graceful degradation for missing data
- User-friendly error messages
- Detailed logging for debugging

### Data Quality
- Provider code validation
- Score range verification (0-100%)
- Duplicate detection and handling
- Missing data interpolation rules

## Security Considerations

### Current Implementation
- Read-only database access in production
- No user authentication (single-tenant)
- No PII data storage
- Local file system for data storage

### Data Protection
- Government public dataset (no sensitive data)
- No user-generated content
- No external API connections
- No credential storage required

## Logging and Monitoring

### Application Logs
- Streamlit console output
- ETL pipeline execution logs
- Database query logging
- Error stack traces

### Performance Metrics
- Query execution times
- Page load durations  
- Memory usage tracking
- User interaction patterns

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | Aug 2025 | Initial AWS cloud-native design |
| 2.0 | Oct 2025 | Pivot to Streamlit/DuckDB architecture |

## Appendix: File Structure

```
project/
├── app.py                      # Main Streamlit application
├── dashboard.py                # Dashboard rendering components
├── analytics_refactored.py     # Analytics calculations
├── data_processor_enhanced.py  # Enhanced database access layer
├── build_analytics_db.py       # ETL pipeline for LCRA dataset
├── build_analytics_db_v2.py    # Enhanced ETL pipeline with LCRA/LCHO support
├── styles.py                   # CSS styling
├── tooltip_definitions.py      # User help text
├── mobile_utils.py            # Mobile responsiveness utilities
├── db_view_script.py          # Database inspection tool
├── diagnose_duplicates.py     # Data integrity checker
├── review_pvalues.py          # Statistical significance analyzer
├── attached_assets/
│   ├── hailie_analytics_v2.duckdb # Analytics database
│   └── *.xlsx                  # Source TSM data
├── ADRs/
│   └── ADR-001-pivot-to-streamlit-duckdb.md # Architecture decision
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── README.md                  # Project documentation
├── HAILIE-Insights-Engine-Architecture-v2.md # Architecture document
├── replit.md                  # Replit-specific documentation
└── pyproject.toml             # Python dependencies