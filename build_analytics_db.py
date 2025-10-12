#!/usr/bin/env python3
"""
Offline ETL Pipeline for HAILIE Analytics Database
This script reads raw TSM data from Excel, performs all calculations,
and stores the results in a DuckDB database for fast retrieval.
"""

import pandas as pd
import duckdb
import numpy as np
from scipy import stats
from scipy.stats import spearmanr, percentileofscore
from data_processor import TSMDataProcessor
import os
import sys
from datetime import datetime


class AnalyticsETL:
    """ETL pipeline for pre-calculating TSM analytics"""
    
    def __init__(self):
        self.data_processor = TSMDataProcessor(silent_mode=True)
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]
        self.db_path = "attached_assets/hailie_analytics.duckdb"
        self.year = 2024  # Default year for the dataset
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def extract_data(self):
        """Extract data from the default Excel file"""
        self.log("📂 Loading raw TSM data from Excel...")
        
        # Load the default dataset
        df = self.data_processor.load_default_data()
        
        if df is None or df.empty:
            raise ValueError("Failed to load TSM data from Excel file")
        
        self.log(f"✅ Loaded {len(df)} providers with {len(df.columns)} columns")
        return df
        
    def transform_to_long_format(self, df):
        """Transform wide format data to long format"""
        self.log("🔄 Transforming data to long format...")
        
        # Prepare data for unpivoting
        id_vars = ['provider_code', 'provider_name'] if 'provider_name' in df.columns else ['provider_code']
        
        # Get TP measure columns
        tp_cols = [col for col in df.columns if col.startswith('TP')]
        
        # Melt the dataframe
        raw_scores_df = pd.melt(
            df[id_vars + tp_cols],
            id_vars=id_vars,
            value_vars=tp_cols,
            var_name='tp_measure',
            value_name='score'
        )
        
        # Add year column
        raw_scores_df['year'] = self.year
        
        # Remove rows with null scores
        raw_scores_df = raw_scores_df.dropna(subset=['score'])
        
        # Ensure provider_name exists (create empty if not present)
        if 'provider_name' not in raw_scores_df.columns:
            raw_scores_df['provider_name'] = ''
        
        self.log(f"✅ Transformed to {len(raw_scores_df)} score records")
        return raw_scores_df
        
    def calculate_percentiles(self, raw_scores_df):
        """Calculate percentile ranks for each provider/measure combination"""
        self.log("📊 Calculating percentiles for all measures...")
        
        percentile_results = []
        
        # Group by measure
        for tp_measure in self.tp_codes:
            measure_data = raw_scores_df[raw_scores_df['tp_measure'] == tp_measure]
            
            if len(measure_data) == 0:
                continue
                
            # Get all scores for this measure
            all_scores = measure_data['score'].values
            
            # Calculate percentile for each provider's score
            for _, row in measure_data.iterrows():
                provider_code = row['provider_code']
                score = row['score']
                
                # Calculate percentile using scipy
                percentile_rank = percentileofscore(all_scores, score)
                
                percentile_results.append({
                    'provider_code': provider_code,
                    'year': self.year,
                    'tp_measure': tp_measure,
                    'percentile_rank': percentile_rank
                })
        
        calculated_percentiles_df = pd.DataFrame(percentile_results)
        self.log(f"✅ Calculated {len(calculated_percentiles_df)} percentile records")
        return calculated_percentiles_df
        
    def calculate_correlations(self, df):
        """Calculate Spearman correlations between each measure and TP01"""
        self.log("🔗 Calculating Spearman correlations with TP01...")
        
        correlation_results = []
        
        # Get TP01 scores
        if 'TP01' not in df.columns:
            self.log("⚠️ TP01 column not found, skipping correlation calculation")
            return pd.DataFrame(correlation_results)
        
        tp01_scores = df['TP01'].dropna()
        
        # Calculate correlation for each other measure
        for tp_measure in self.tp_codes[1:]:  # Skip TP01 itself
            if tp_measure not in df.columns:
                continue
                
            measure_scores = df[tp_measure].dropna()
            
            # Get common indices for correlation
            common_indices = tp01_scores.index.intersection(measure_scores.index)
            
            if len(common_indices) > 5:  # Need sufficient data
                try:
                    # Calculate Spearman correlation
                    corr_coef, p_value = spearmanr(
                        tp01_scores.loc[common_indices],
                        measure_scores.loc[common_indices]
                    )
                    
                    correlation_results.append({
                        'year': self.year,
                        'tp_measure': tp_measure,
                        'correlation_with_tp01': corr_coef,
                        'p_value': p_value,
                        'sample_size': len(common_indices)
                    })
                except Exception as e:
                    self.log(f"⚠️ Error calculating correlation for {tp_measure}: {str(e)}")
        
        calculated_correlations_df = pd.DataFrame(correlation_results)
        self.log(f"✅ Calculated correlations for {len(calculated_correlations_df)} measures")
        return calculated_correlations_df
        
    def load_to_duckdb(self, raw_scores_df, calculated_percentiles_df, calculated_correlations_df):
        """Load all DataFrames into DuckDB database"""
        self.log(f"💾 Writing to DuckDB database: {self.db_path}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect to DuckDB
        con = duckdb.connect(self.db_path)
        
        try:
            # Create or replace tables
            con.execute("CREATE OR REPLACE TABLE raw_scores AS SELECT * FROM raw_scores_df")
            self.log(f"  ✓ Created raw_scores table with {len(raw_scores_df)} records")
            
            con.execute("CREATE OR REPLACE TABLE calculated_percentiles AS SELECT * FROM calculated_percentiles_df")
            self.log(f"  ✓ Created calculated_percentiles table with {len(calculated_percentiles_df)} records")
            
            con.execute("CREATE OR REPLACE TABLE calculated_correlations AS SELECT * FROM calculated_correlations_df")
            self.log(f"  ✓ Created calculated_correlations table with {len(calculated_correlations_df)} records")
            
            # Create indexes for faster queries
            con.execute("CREATE INDEX IF NOT EXISTS idx_raw_scores_provider ON raw_scores(provider_code)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_percentiles_provider ON calculated_percentiles(provider_code)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_correlations_measure ON calculated_correlations(tp_measure)")
            self.log("  ✓ Created database indexes")
            
            # Verify the data
            result = con.execute("SELECT COUNT(*) FROM raw_scores").fetchone()
            if result:
                row_count = result[0]
                self.log(f"  ✓ Verified: {row_count} rows in raw_scores table")
            
        finally:
            con.close()
        
        self.log(f"✅ Database created successfully at {self.db_path}")
        
    def run(self):
        """Execute the complete ETL pipeline"""
        self.log("🚀 Starting HAILIE Analytics ETL Pipeline")
        self.log("=" * 60)
        
        try:
            # Phase 1: Extract
            df = self.extract_data()
            
            # Phase 2: Transform
            raw_scores_df = self.transform_to_long_format(df)
            
            # Phase 3: Calculate analytics
            calculated_percentiles_df = self.calculate_percentiles(raw_scores_df)
            calculated_correlations_df = self.calculate_correlations(df)
            
            # Phase 4: Load
            self.load_to_duckdb(raw_scores_df, calculated_percentiles_df, calculated_correlations_df)
            
            self.log("=" * 60)
            self.log("🎉 ETL Pipeline completed successfully!")
            
            # Print summary statistics
            self.log("\n📈 Summary Statistics:")
            self.log(f"  - Total providers: {df['provider_code'].nunique()}")
            self.log(f"  - Total measures: {len(self.tp_codes)}")
            self.log(f"  - Total score records: {len(raw_scores_df)}")
            self.log(f"  - Total percentile calculations: {len(calculated_percentiles_df)}")
            self.log(f"  - Total correlation calculations: {len(calculated_correlations_df)}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ ETL Pipeline failed: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False


def main():
    """Main entry point for the ETL script"""
    etl = AnalyticsETL()
    success = etl.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()