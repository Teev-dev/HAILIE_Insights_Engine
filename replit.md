# HAILIE Insights Engine

## Overview

HAILIE Insights Engine is a Streamlit web application designed to process UK government TSM (Tenant Satisfaction Measures) data and generate executive dashboards for social housing providers. The application provides three key insights: provider rankings against peers, performance momentum over time, and priority areas for improvement. It focuses on delivering actionable intelligence through an executive-friendly interface that transforms complex TSM datasets (TP01-TP12 satisfaction measures) into clear, visual insights for non-technical stakeholders in the social housing sector.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture**
- Streamlit-based web interface optimized for executive consumption
- Professional color scheme with quartile-based visual indicators (blue primary, green for top performance)
- Three-column layout showcasing key metrics: Your Rank, Your Momentum, Your Priority
- Custom CSS styling for metric cards with visual hierarchy and accessibility

**Data Processing Layer**
- Multi-sheet Excel file parser with intelligent sheet detection using priority keywords
- TP-code validation system for UK government TSM datasets (TP01-TP12)
- Flexible column mapping to handle various government dataset formats
- Error handling and data quality validation with user feedback

**Analytics Engine**
- Statistical ranking system with quartile-based peer comparisons
- Trend analysis for 12-month performance momentum using directional indicators
- Correlation-based priority identification to surface critical improvement areas
- Support for peer group filtering and segmentation

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