#!/usr/bin/env python3
"""
Enhanced ETL Pipeline for HAILIE Analytics Database
Processes both LCRA and LCHO datasets with proper separation
Maintains dataset isolation for accurate peer comparisons
"""

import pandas as pd
import duckdb
import numpy as np
from scipy import stats
from scipy.stats import spearmanr, percentileofscore
import os
import sys
from datetime import datetime


class EnhancedAnalyticsETL:
    """ETL pipeline for processing both LCRA and LCHO TSM data"""
    
    def __init__(self, excel_path=None, year=None):
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]
        self.db_path = "attached_assets/hailie_analytics_v2.duckdb"
        
        if excel_path is None:
            self.excel_path = "attached_assets/2024_TSM_Full_Data_v1.1_FINAL_1756577982265.xlsx"
            self.year = 2024
        else:
            self.excel_path = excel_path
            self.year = year if year is not None else 2024
        
        # Configure skiprows and column mappings based on year
        if self.year == 2025:
            self.lcra_skiprows = 10
            self.lcho_skiprows = 9
            # 2025 column mappings
            self.lcra_column_mapping = {
                0: 'provider_name',
                1: 'provider_code',
                26: 'TP01',
                33: 'TP02',
                34: 'TP03',
                35: 'TP04',
                36: 'TP05',
                37: 'TP06',
                38: 'TP07',
                39: 'TP08',
                40: 'TP09',
                41: 'TP10',
                42: 'TP11',
                43: 'TP12',
            }
            self.lcho_column_mapping = {
                0: 'provider_name',
                1: 'provider_code',
                25: 'TP01',
                32: 'TP05',
                33: 'TP06',
                34: 'TP07',
                35: 'TP08',
                36: 'TP09',
                37: 'TP10',
                38: 'TP11',
                39: 'TP12',
            }
        else:
            # 2024 and earlier - default configuration
            self.lcra_skiprows = 3
            self.lcho_skiprows = 3
            # 2024 column mappings
            self.lcra_column_mapping = {
                0: 'provider_name',
                1: 'provider_code',
                22: 'TP01',
                23: 'TP02',
                24: 'TP03',
                25: 'TP04',
                26: 'TP05',
                27: 'TP06',
                28: 'TP07',
                29: 'TP08',
                30: 'TP09',
                31: 'TP10',
                32: 'TP11',
                33: 'TP12',
            }
            self.lcho_column_mapping = {
                0: 'provider_name',
                1: 'provider_code',
                21: 'TP01',
                22: 'TP05',
                23: 'TP06',
                24: 'TP07',
                25: 'TP08',
                26: 'TP09',
                27: 'TP10',
                28: 'TP11',
                29: 'TP12',
            }
        
    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def load_table_coverage(self):
        """Load the Table_Coverage sheet to identify provider types"""
        self.log("📋 Loading Table_Coverage to identify provider types...")
        
        try:
            # Read with proper skip rows
            coverage_df = pd.read_excel(self.excel_path, sheet_name='Table_Coverage', skiprows=3)
            
            # Set column names
            coverage_df.columns = ['landlord_name', 'landlord_code', 'landlord_type', 
                                 'tsm24_lcra_perception', 'tsm24_lcho_perception', 
                                 'tsm24_combined_perception', 'tsm24_management_info',
                                 'tsm24_perception_not_inc', 'tsm24_man_info_not_inc']
            
            # Clean the data
            coverage_df['landlord_code'] = coverage_df['landlord_code'].astype(str).str.strip()
            coverage_df = coverage_df.dropna(subset=['landlord_code'])
            coverage_df = coverage_df[coverage_df['landlord_code'] != '']
            
            # Create dataset type mapping
            coverage_df['dataset_type'] = coverage_df.apply(
                lambda row: 'COMBINED' if row['tsm24_combined_perception'] == 'Yes'
                else 'LCRA' if row['tsm24_lcra_perception'] == 'Yes'
                else 'LCHO' if row['tsm24_lcho_perception'] == 'Yes'
                else None, axis=1
            )
            
            self.log(f"✅ Loaded coverage data for {len(coverage_df)} providers")
            self.log(f"  - LCRA providers: {(coverage_df['dataset_type'] == 'LCRA').sum()}")
            self.log(f"  - LCHO providers: {(coverage_df['dataset_type'] == 'LCHO').sum()}")
            self.log(f"  - Combined providers: {(coverage_df['dataset_type'] == 'COMBINED').sum()}")
            
            return coverage_df
            
        except Exception as e:
            self.log(f"❌ Error loading Table_Coverage: {str(e)}")
            raise
            
    def extract_lcra_data(self):
        """Extract LCRA perception data"""
        self.log("📂 Loading LCRA perception data...")
        
        try:
            # Construct sheet name based on year
            sheet_name = f'TSM{str(self.year)[2:]}_LCRA_Perception'
            
            # Read without headers first
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
            
            # Data starts from different rows depending on year
            df = df.iloc[self.lcra_skiprows:].reset_index(drop=True)
            
            # Select and rename columns
            selected_columns = list(self.lcra_column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [self.lcra_column_mapping[col] for col in selected_columns]
            
            # Clean data
            df = df[df['provider_code'].notna()]
            df['provider_code'] = df['provider_code'].astype(str).str.strip()
            
            # Convert TP columns to numeric
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            for tp_col in tp_cols:
                df[tp_col] = pd.to_numeric(df[tp_col], errors='coerce')
            
            # Remove providers with no data
            df = df.dropna(subset=tp_cols, how='all')
            
            # Add dataset type and suffix to provider names
            df['dataset_type'] = 'LCRA'
            df['provider_name'] = df['provider_name'] + ' - LCRA'
            
            self.log(f"✅ Loaded {len(df)} LCRA providers with {len(tp_cols)} TP measures")
            return df
            
        except Exception as e:
            self.log(f"❌ Error loading LCRA data: {str(e)}")
            raise
            
    def extract_lcho_data(self):
        """Extract LCHO perception data"""
        self.log("📂 Loading LCHO perception data...")
        
        try:
            # Construct sheet name based on year
            sheet_name = f'TSM{str(self.year)[2:]}_LCHO_Perception'
            
            # Read without headers first
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
            
            # Data starts from different rows depending on year
            df = df.iloc[self.lcho_skiprows:].reset_index(drop=True)
            
            # Select and rename columns
            selected_columns = list(self.lcho_column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [self.lcho_column_mapping[col] for col in selected_columns]
            
            # Clean data
            df = df[df['provider_code'].notna()]
            df['provider_code'] = df['provider_code'].astype(str).str.strip()
            
            # Convert TP columns to numeric
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            for tp_col in tp_cols:
                df[tp_col] = pd.to_numeric(df[tp_col], errors='coerce')
            
            # Add NA columns for TP02-TP04 (not applicable to LCHO)
            df['TP02'] = np.nan  # Repairs satisfaction - N/A for LCHO
            df['TP03'] = np.nan  # Time to complete repair - N/A for LCHO
            df['TP04'] = np.nan  # Satisfaction with time taken - N/A for LCHO
            
            # Remove providers with no data (excluding TP02-TP04)
            valid_tp_cols = [col for col in tp_cols if col not in ['TP02', 'TP03', 'TP04']]
            df = df.dropna(subset=valid_tp_cols, how='all')
            
            # Add dataset type and suffix to provider names
            df['dataset_type'] = 'LCHO'
            df['provider_name'] = df['provider_name'] + ' - LCHO'
            
            self.log(f"✅ Loaded {len(df)} LCHO providers with {len(valid_tp_cols)} applicable TP measures")
            self.log(f"  Note: TP02-TP04 marked as N/A for LCHO providers (repairs metrics don't apply)")
            return df
            
        except Exception as e:
            self.log(f"❌ Error loading LCHO data: {str(e)}")
            raise
            
    def extract_combined_data(self):
        """Extract data for providers that appear in Combined sheet"""
        self.log("📂 Loading Combined perception data...")
        
        try:
            # Construct sheet name based on year
            sheet_name = f'TSM{str(self.year)[2:]}_Combined_Perception'
            
            # Try to load combined sheet
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)
            
            # Data starts from different rows depending on year (same as LCRA)
            df = df.iloc[self.lcra_skiprows:].reset_index(drop=True)
            
            # Use LCRA mapping as base (assumes combined has all columns)
            selected_columns = list(self.lcra_column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [self.lcra_column_mapping[col] for col in selected_columns]
            
            # Clean data
            df = df[df['provider_code'].notna()]
            df['provider_code'] = df['provider_code'].astype(str).str.strip()
            
            # Convert TP columns to numeric
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            for tp_col in tp_cols:
                df[tp_col] = pd.to_numeric(df[tp_col], errors='coerce')
            
            # Remove providers with no data
            df = df.dropna(subset=tp_cols, how='all')
            
            # Add dataset type and suffix to provider names
            df['dataset_type'] = 'COMBINED'
            df['provider_name'] = df['provider_name'] + ' - COMBINED'
            
            self.log(f"✅ Loaded {len(df)} Combined providers")
            return df
            
        except Exception as e:
            self.log(f"⚠️ No Combined sheet found or error loading: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame
            
    def transform_to_long_format(self, df, dataset_type):
        """Transform wide format data to long format with dataset tracking"""
        self.log(f"🔄 Transforming {dataset_type} data to long format...")
        
        # Prepare data for unpivoting
        id_vars = ['provider_code', 'provider_name', 'dataset_type']
        
        # Get TP measure columns (only non-null for this dataset)
        if dataset_type == 'LCHO':
            # For LCHO, exclude TP02-TP04 as they're not applicable
            tp_cols = [col for col in df.columns if col.startswith('TP') and col not in ['TP02', 'TP03', 'TP04']]
        else:
            tp_cols = [col for col in df.columns if col.startswith('TP')]
        
        if not tp_cols:
            self.log(f"⚠️ No TP columns found for {dataset_type}")
            return pd.DataFrame()
        
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
        
        self.log(f"✅ Transformed {dataset_type} to {len(raw_scores_df)} score records")
        return raw_scores_df
        
    def calculate_percentiles_by_dataset(self, raw_scores_df):
        """Calculate percentile ranks separately for each dataset"""
        self.log("📊 Calculating percentiles within peer groups...")
        
        all_percentiles = []
        
        # Process each dataset separately
        for dataset_type in raw_scores_df['dataset_type'].unique():
            self.log(f"  Processing {dataset_type} percentiles...")
            dataset_scores = raw_scores_df[raw_scores_df['dataset_type'] == dataset_type]
            
            # Get unique TP measures for this dataset
            measures = dataset_scores['tp_measure'].unique()
            
            for tp_measure in measures:
                measure_data = dataset_scores[dataset_scores['tp_measure'] == tp_measure]
                
                if len(measure_data) == 0:
                    continue
                
                # Get all scores for this measure within this dataset
                all_scores = measure_data['score'].values
                
                # Calculate percentile for each provider's score
                for _, row in measure_data.iterrows():
                    percentile_rank = percentileofscore(all_scores, row['score'])
                    
                    all_percentiles.append({
                        'provider_code': row['provider_code'],
                        'year': self.year,
                        'tp_measure': tp_measure,
                        'percentile_rank': percentile_rank,
                        'dataset_type': dataset_type,
                        'peer_group_size': len(all_scores)
                    })
        
        calculated_percentiles_df = pd.DataFrame(all_percentiles)
        self.log(f"✅ Calculated {len(calculated_percentiles_df)} percentile records")
        return calculated_percentiles_df
        
    def calculate_correlations_by_dataset(self, all_data):
        """Calculate Spearman correlations separately for each dataset"""
        self.log("🔗 Calculating correlations within datasets...")
        
        all_correlations = []
        
        # Process each dataset separately
        for dataset_type in all_data['dataset_type'].unique():
            self.log(f"  Processing {dataset_type} correlations...")
            dataset_df = all_data[all_data['dataset_type'] == dataset_type].copy()
            
            if 'TP01' not in dataset_df.columns:
                self.log(f"⚠️ TP01 not found for {dataset_type}, skipping")
                continue
            
            tp01_scores = dataset_df['TP01'].dropna()
            
            # Determine which measures to correlate based on dataset
            if dataset_type == 'LCHO':
                # Skip TP02-TP04 for LCHO
                measures_to_correlate = [tp for tp in self.tp_codes[1:] if tp not in ['TP02', 'TP03', 'TP04']]
            else:
                measures_to_correlate = self.tp_codes[1:]
            
            for tp_measure in measures_to_correlate:
                if tp_measure not in dataset_df.columns:
                    continue
                
                measure_scores = dataset_df[tp_measure].dropna()
                common_indices = tp01_scores.index.intersection(measure_scores.index)
                
                if len(common_indices) > 5:
                    try:
                        corr_coef, p_value = spearmanr(
                            tp01_scores.loc[common_indices],
                            measure_scores.loc[common_indices]
                        )
                        
                        all_correlations.append({
                            'year': self.year,
                            'tp_measure': tp_measure,
                            'correlation_with_tp01': corr_coef,
                            'p_value': p_value,
                            'sample_size': len(common_indices),
                            'dataset_type': dataset_type
                        })
                    except Exception as e:
                        self.log(f"⚠️ Error calculating correlation for {tp_measure} in {dataset_type}: {str(e)}")
        
        calculated_correlations_df = pd.DataFrame(all_correlations)
        self.log(f"✅ Calculated {len(calculated_correlations_df)} correlation records")
        return calculated_correlations_df
        
    def create_provider_dataset_mapping(self, coverage_df, all_data):
        """Create a mapping table of providers to their datasets"""
        self.log("🗺️ Creating provider-dataset mapping...")
        
        # Get unique providers from the data
        providers_in_data = all_data[['provider_code', 'provider_name', 'dataset_type']].drop_duplicates()
        
        # Merge with coverage info
        mapping_df = providers_in_data.merge(
            coverage_df[['landlord_code', 'landlord_type']],
            left_on='provider_code',
            right_on='landlord_code',
            how='left'
        )
        
        # Clean up columns
        mapping_df = mapping_df[['provider_code', 'provider_name', 'dataset_type', 'landlord_type']]
        mapping_df.columns = ['provider_code', 'provider_name', 'dataset_type', 'provider_type']
        
        self.log(f"✅ Created mapping for {len(mapping_df)} providers")
        return mapping_df
        
    def load_to_duckdb(self, raw_scores_df, percentiles_df, correlations_df, mapping_df, all_data):
        """Load all DataFrames into DuckDB database with enhanced schema"""
        self.log(f"💾 Writing to DuckDB database: {self.db_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Check if database exists
        db_exists = os.path.exists(self.db_path)
        
        # Connect to DuckDB
        con = duckdb.connect(self.db_path)
        
        try:
            if not db_exists:
                self.log("📊 Creating new database with initial schema...")
                # Create enhanced tables for first time
                con.execute("CREATE TABLE raw_scores AS SELECT * FROM raw_scores_df")
                self.log(f"  ✓ Created raw_scores table with {len(raw_scores_df)} records")
                
                con.execute("CREATE TABLE calculated_percentiles AS SELECT * FROM percentiles_df")
                self.log(f"  ✓ Created calculated_percentiles table with {len(percentiles_df)} records")
                
                con.execute("CREATE TABLE calculated_correlations AS SELECT * FROM correlations_df")
                self.log(f"  ✓ Created calculated_correlations table with {len(correlations_df)} records")
                
                con.execute("CREATE TABLE provider_dataset_mapping AS SELECT * FROM mapping_df")
                self.log(f"  ✓ Created provider_dataset_mapping table with {len(mapping_df)} records")
                
                con.execute("CREATE TABLE provider_summary AS SELECT * FROM all_data")
                self.log(f"  ✓ Created provider_summary table with {len(all_data)} records")
            else:
                self.log("📊 Appending to existing database...")
                
                # Check if year column exists in provider_summary, add if needed
                summary_cols = con.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'provider_summary'").fetchdf()
                if 'year' not in summary_cols['column_name'].values:
                    self.log("  ⚙️ Migrating provider_summary to include year column...")
                    con.execute("ALTER TABLE provider_summary ADD COLUMN year INTEGER")
                    con.execute("UPDATE provider_summary SET year = 2024 WHERE year IS NULL")
                    self.log("  ✓ Migration complete")
                
                # Delete existing data for this year first (prevents duplicates if re-running)
                con.execute(f"DELETE FROM raw_scores WHERE year = {self.year}")
                con.execute(f"DELETE FROM calculated_percentiles WHERE year = {self.year}")
                con.execute(f"DELETE FROM calculated_correlations WHERE year = {self.year}")
                con.execute(f"DELETE FROM provider_summary WHERE year = {self.year}")
                self.log(f"  ✓ Removed any existing {self.year} data")
                
                # Insert new data
                con.execute("INSERT INTO raw_scores SELECT * FROM raw_scores_df")
                self.log(f"  ✓ Inserted {len(raw_scores_df)} records into raw_scores")
                
                con.execute("INSERT INTO calculated_percentiles SELECT * FROM percentiles_df")
                self.log(f"  ✓ Inserted {len(percentiles_df)} records into calculated_percentiles")
                
                # Only insert correlations if we have any
                if len(correlations_df) > 0:
                    con.execute("INSERT INTO calculated_correlations SELECT * FROM correlations_df")
                    self.log(f"  ✓ Inserted {len(correlations_df)} records into calculated_correlations")
                else:
                    self.log(f"  ⚠️ No correlations to insert (need sufficient sample size)")
                
                con.execute("INSERT INTO provider_summary SELECT * FROM all_data")
                self.log(f"  ✓ Inserted {len(all_data)} records into provider_summary")
                
                # Update provider mapping (upsert logic)
                con.execute("DELETE FROM provider_dataset_mapping WHERE provider_code IN (SELECT provider_code FROM mapping_df)")
                con.execute("INSERT INTO provider_dataset_mapping SELECT * FROM mapping_df")
                self.log(f"  ✓ Updated provider_dataset_mapping with {len(mapping_df)} providers")
            
            # Create indexes for performance
            con.execute("CREATE INDEX IF NOT EXISTS idx_raw_scores_provider ON raw_scores(provider_code, dataset_type)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_percentiles_provider ON calculated_percentiles(provider_code, dataset_type)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_correlations_dataset ON calculated_correlations(dataset_type, tp_measure)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_mapping_provider ON provider_dataset_mapping(provider_code)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_summary_provider ON provider_summary(provider_code)")
            self.log("  ✓ Created database indexes")
            
            # Create views for easy querying
            con.execute("""
                CREATE OR REPLACE VIEW v_provider_scores AS
                SELECT 
                    rs.provider_code,
                    rs.provider_name,
                    rs.dataset_type,
                    rs.tp_measure,
                    rs.score,
                    cp.percentile_rank,
                    cp.peer_group_size
                FROM raw_scores rs
                LEFT JOIN calculated_percentiles cp
                    ON rs.provider_code = cp.provider_code 
                    AND rs.tp_measure = cp.tp_measure
                    AND rs.dataset_type = cp.dataset_type
            """)
            self.log("  ✓ Created v_provider_scores view")
            
            # Verify the data
            for table in ['raw_scores', 'calculated_percentiles', 'provider_dataset_mapping']:
                result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if result:
                    self.log(f"  ✓ Verified: {result[0]} rows in {table}")
            
        finally:
            con.close()
        
        self.log(f"✅ Enhanced database created successfully at {self.db_path}")
        
    def run(self):
        """Execute the enhanced ETL pipeline"""
        self.log("🚀 Starting Enhanced HAILIE Analytics ETL Pipeline")
        self.log("=" * 60)
        
        try:
            # Phase 1: Load coverage data
            coverage_df = self.load_table_coverage()
            
            # Phase 2: Extract data from both sheets
            lcra_df = self.extract_lcra_data()
            lcho_df = self.extract_lcho_data()
            combined_df = self.extract_combined_data()
            
            # Combine all data
            all_data = pd.concat([lcra_df, lcho_df, combined_df], ignore_index=True)
            
            # Add year column to wide-format data
            all_data['year'] = self.year
            
            # Phase 3: Transform to long format
            lcra_long = self.transform_to_long_format(lcra_df, 'LCRA')
            lcho_long = self.transform_to_long_format(lcho_df, 'LCHO')
            combined_long = self.transform_to_long_format(combined_df, 'COMBINED') if not combined_df.empty else pd.DataFrame()
            
            # Combine all long format data
            all_raw_scores = pd.concat([lcra_long, lcho_long, combined_long], ignore_index=True)
            
            # Phase 4: Calculate analytics by dataset
            calculated_percentiles = self.calculate_percentiles_by_dataset(all_raw_scores)
            calculated_correlations = self.calculate_correlations_by_dataset(all_data)
            
            # Phase 5: Create provider mapping
            provider_mapping = self.create_provider_dataset_mapping(coverage_df, all_data)
            
            # Phase 6: Load to database
            self.load_to_duckdb(
                all_raw_scores,
                calculated_percentiles,
                calculated_correlations,
                provider_mapping,
                all_data
            )
            
            self.log("=" * 60)
            self.log("🎉 Enhanced ETL Pipeline completed successfully!")
            
            # Print summary statistics
            self.log("\n📈 Summary Statistics:")
            self.log(f"  - Total providers: {all_data['provider_code'].nunique()}")
            self.log(f"  - LCRA providers: {all_data[all_data['dataset_type'] == 'LCRA']['provider_code'].nunique()}")
            self.log(f"  - LCHO providers: {all_data[all_data['dataset_type'] == 'LCHO']['provider_code'].nunique()}")
            self.log(f"  - Total score records: {len(all_raw_scores)}")
            self.log(f"  - Total percentile calculations: {len(calculated_percentiles)}")
            self.log(f"  - Total correlation calculations: {len(calculated_correlations)}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Enhanced ETL Pipeline failed: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            return False


def main():
    """Main entry point for the enhanced ETL script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load TSM data into HAILIE analytics database')
    parser.add_argument('--excel-path', type=str, help='Path to Excel file')
    parser.add_argument('--year', type=int, help='Year of the data (e.g., 2024, 2025)')
    
    args = parser.parse_args()
    
    etl = EnhancedAnalyticsETL(excel_path=args.excel_path, year=args.year)
    success = etl.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()