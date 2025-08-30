# HAILIE Insights Engine

A Streamlit web application for processing UK government TSM (Tenant Satisfaction Measures) data and generating executive dashboards for social housing providers.

## Features

- **Your Rank**: Position vs similar providers with color-coded quartile indicators
- **Your Momentum**: 12-month performance trajectory using directional arrows  
- **Your Priority**: Single most critical area to improve based on data correlation analysis

## Installation

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install streamlit pandas numpy openpyxl scipy plotly
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py --server.port 5000
   ```

2. Upload your TSM Excel data file containing TP01-TP12 satisfaction measures

3. Enter your provider code

4. View your executive dashboard with key performance insights

## Data Format

The application supports UK government TSM datasets with:
- TP01-TP12 satisfaction measure codes
- Provider identification columns
- Multi-sheet Excel workbooks
- Standard government dataset formats

## Technical Architecture

- **Data Processing**: Multi-sheet Excel parsing with TP-code validation
- **Analytics**: Statistical ranking, trend analysis, and correlation-based priorities  
- **Dashboard**: Executive-friendly interface optimized for non-technical users
- **Styling**: Professional color scheme with quartile-based visual indicators

## Color Scheme

- Primary: #2E5BBA (professional blue)
- Success: #22C55E (green for top quartile) 
- Warning: #F59E0B (amber for middle)
- Danger: #EF4444 (red for bottom quartile)
- Background: #F8FAFC (light grey)
- Text: #1E293B (dark slate)

## License

This project is licensed under CC-BY 4.0 - see the LICENSE file for details.

## Support

For issues with data processing or dashboard functionality, please check:
1. Excel file contains TP01-TP12 measures
2. Provider code exists in the dataset
3. Data quality report for completeness metrics
