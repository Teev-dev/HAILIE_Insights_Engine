# HAILIE Insights Engine

A Streamlit web application that transforms UK government TSM (Tenant Satisfaction Measures) data into actionable executive insights for social housing providers.

**Live:** https://insights.housingai.org

## Overview

HAILIE Insights Engine delivers instant analytics from pre-processed TSM 2024-2025 government data, supporting both LCRA (Low Cost Rental Accommodation) and LCHO (Low Cost Home Ownership) providers with dataset-specific peer comparisons.

## Key Features

- **Your Rank**: Position vs similar providers with color-coded quartile indicators
- **Your Momentum**: 12-month performance trajectory using directional arrows (ready for 2026 when multi-year data available)
- **Your Priority**: Single most critical area to improve based on data correlation analysis

## Dataset Support

- **LCRA Providers**: 355 organizations with full TP01-TP12 satisfaction measures
- **LCHO Providers**: 56 organizations with TP01, TP05-TP12 measures (repairs metrics TP02-TP04 not applicable)
- **Automatic Detection**: System automatically identifies provider type and compares within appropriate peer group
- **Isolated Analytics**: Rankings and percentiles calculated within dataset type only

## Quick Start

### Local Development

```bash
git clone https://github.com/Teev-dev/HAILIE_Insights_Engine.git
cd HAILIE_Insights_Engine
pip install .
streamlit run app.py
```

### Docker

```bash
docker build -t hailie-insights .
docker run -p 8501:8501 -e PORT=8501 hailie-insights
```

Open http://localhost:8501, select your provider code, and view your dashboard.

## Deployment on Railway

1. Connect your GitHub repo to [Railway](https://railway.app)
2. Railway auto-detects the `Dockerfile` and `railway.toml`
3. The app binds to Railway's injected `$PORT` automatically

**Production with persistent storage:**

Set the `DATA_PATH` environment variable to a Railway persistent volume mount to store the DuckDB database independently of the container image. Without this, the baked-in database from the Docker image is used (suitable for demos and open-source use).

For full deployment instructions including persistent disk setup, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Usage

1. Select your provider code from the dropdown (auto-detects LCRA/LCHO)
2. View your executive dashboard with three key performance insights
3. Explore detailed analytics and visualizations

## Technical Architecture

- **Database**: DuckDB analytics database with pre-calculated metrics
- **ETL Pipeline**: Pre-processes government TSM data into optimized format
- **Analytics Engine**: Statistical ranking, correlation analysis, and percentile calculations
- **Dashboard**: Executive-friendly Streamlit interface with responsive design
- **Performance**: Sub-second query response from pre-calculated analytics

## Data Processing

The system uses pre-processed TSM data stored in `data/hailie_analytics_v2.duckdb`:

- **Raw Scores**: All provider satisfaction measures
- **Calculated Percentiles**: Pre-computed rankings for instant retrieval
- **Correlations**: Pre-calculated Spearman correlations with overall satisfaction (TP01)

To rebuild the database from source data:
```bash
python build_analytics_db_v2.py
```

## Diagnostic Tools

- **Database Viewer**: `python db_view_script.py` - Inspect database contents
- **Duplicate Diagnosis**: `python diagnose_duplicates.py` - Check for data integrity issues
- **P-Value Analysis**: `python review_pvalues.py` - Review statistical significance of correlations

## TSM Measures

| Code | Description |
|------|-------------|
| TP01 | Overall satisfaction |
| TP02 | Satisfaction with repairs (LCRA only) |
| TP03 | Time taken to complete most recent repair (LCRA only) |
| TP04 | Satisfaction with time taken for repair (LCRA only) |
| TP05 | Satisfaction that home is well-maintained |
| TP06 | Satisfaction that home is safe |
| TP07 | Landlord listens to residents' views |
| TP08 | Landlord keeps residents informed |
| TP09 | Landlord treats residents fairly |
| TP10 | Approach to handling complaints |
| TP11 | Communal areas clean and well-maintained |
| TP12 | Approach to handling anti-social behaviour |

## Color Scheme

- Primary: #2E5BBA (professional blue)
- Success: #22C55E (green for top quartile)
- Warning: #F59E0B (amber for middle quartiles)
- Danger: #EF4444 (red for bottom quartile)
- Background: #F8FAFC (light grey)
- Text: #1E293B (dark slate)

## Mobile Support

The application includes responsive design features:
- Adaptive layouts for mobile and tablet screens
- Touch-friendly interface elements
- Optimized chart rendering for smaller displays

## Contributing

See [guides/collaboration-protocol.md](guides/collaboration-protocol.md) for contributor guidelines, including paths for domain experts, developers, and AI agents.

## License

- **Code:** MIT License — see [LICENSE-CODE](LICENSE-CODE)
- **Documentation and data:** CC-BY 4.0 — see [LICENSE-DOCS](LICENSE-DOCS)

## Project Structure

```
├── app.py                    # Streamlit entry point
├── dashboard.py              # Executive dashboard rendering
├── analytics_refactored.py   # Core analytics engine
├── data_processor_enhanced.py # DuckDB data access layer
├── config.py                 # Data path configuration
├── data/                     # Runtime data (DuckDB)
│   └── source/               # Source xlsx files
├── Dockerfile                # Container build
├── railway.toml              # Railway deployment config
└── MASTERPLAN.md             # Project vision & principles
```

## Support

For issues with the application, please verify:
1. Database file exists at `data/hailie_analytics_v2.duckdb`
2. Your provider code is in the current TSM dataset
3. Python dependencies are correctly installed