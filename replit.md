# HAILIE Insights Engine

## Overview

HAILIE Insights Engine is a Streamlit web application designed to process UK government TSM (Tenant Satisfaction Measures) data and generate executive dashboards for social housing providers. The application provides three key insights: provider rankings against peers, performance momentum over time, and priority areas for improvement. It focuses on delivering actionable intelligence through an executive-friendly interface that transforms complex TSM datasets (TP01-TP12 satisfaction measures) into clear, visual insights for non-technical stakeholders in the social housing sector.

**Version 3.0 Update (October 2025)**: Enhanced to support both LCRA and LCHO perception datasets with automatic dataset detection and peer-isolated analytics:
- **LCRA Dataset**: 355 providers with full TP01-TP12 measures  
- **LCHO Dataset**: 56 providers with TP01, TP05-TP12 (TP02-TP04 repairs metrics not applicable)
- **Automatic Detection**: Selecting any provider automatically uses the correct dataset
- **Peer Isolation**: All comparisons (rankings, percentiles) calculated within dataset type only
- **Visual Indicators**: Clear communication of which peer group is being compared

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- Streamlit-based web interface optimized for executive consumption
- Professional color scheme with quartile-based visual indicators (blue primary, green for top performance)
- Three-column layout showcasing key metrics: Your Rank, Your Momentum, Your Priority
- Custom CSS styling for metric cards with visual hierarchy and accessibility

**Database Layer (New in v2.0)**
- DuckDB analytics database storing pre-calculated metrics for instant retrieval
- ETL pipeline (build_analytics_db.py) processes Excel data into optimized database format
- Three core tables: raw_scores, calculated_percentiles, calculated_correlations
- Successfully processed 355 providers with 4,260 score records

**Data Processing Layer**
- DuckDB query client for high-performance data retrieval
- Cached provider lists and metadata for instant dropdown population
- Pre-calculated percentiles for all TP measures across all providers
- Pre-computed Spearman correlations between measures and TP01 (overall satisfaction)

**Analytics Engine**
- Statistical ranking using pre-calculated percentiles from database
- Momentum analysis ready for multi-year data (available 2026+)
- Priority identification using pre-computed correlations and percentiles
- Support for peer group filtering (future enhancement)

**Dashboard Components**
- Executive summary with three key performance indicators
- Interactive visualizations using Plotly for charts and graphs
- Color-coded performance indicators aligned with quartile positioning
- Responsive design for various screen sizes and executive presentation contexts

**Data Model**
- TSM measure codes (TP01-TP12) mapped to satisfaction descriptions
- Provider identification through codes and names
- Time-series support for momentum calculations
- Flexible schema to accommodate government dataset variations

## External Dependencies

**Python Libraries**
- Streamlit: Web application framework and user interface
- Pandas: Data manipulation and analysis
- NumPy: Numerical computing and statistical operations
- Openpyxl: Excel file reading and processing
- SciPy: Statistical analysis including correlation calculations
- Plotly: Interactive data visualization and charting

**Data Sources**
- UK Government TSM datasets in Excel format
- Multi-sheet workbook support for various government data structures
- TP01-TP12 satisfaction measure standards compliance

**Runtime Environment**
- Python 3.x runtime environment
- Streamlit server deployment on port 5000
- File upload capabilities for Excel data ingestion