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
        
    # Known TP header patterns for dynamic detection
    TP_HEADER_PATTERNS = {
        'TP01': ['TP01', '(TP01)', 'Overall satisfaction'],
        'TP02': ['TP02', '(TP02)', 'Satisfaction with repairs'],
        'TP03': ['TP03', '(TP03)', 'Time taken to complete'],
        'TP04': ['TP04', '(TP04)', 'Satisfaction with time taken'],
        'TP05': ['TP05', '(TP05)', 'Home is well-maintained', 'well maintained'],
        'TP06': ['TP06', '(TP06)', 'Home is safe'],
        'TP07': ['TP07', '(TP07)', 'Satisfaction with neighbourhood', 'neighbourhood'],
        'TP08': ['TP08', '(TP08)', 'contribution to neighbourhood'],
        'TP09': ['TP09', '(TP09)', 'handling of complaints', 'complaints'],
        'TP10': ['TP10', '(TP10)', 'treats residents fairly', 'fairly'],
        'TP11': ['TP11', '(TP11)', "listens to residents", 'listens'],
        'TP12': ['TP12', '(TP12)', 'anti-social behaviour'],
    }

    PROVIDER_NAME_PATTERNS = ['landlord name', 'provider name', 'organisation name', 'landlord_name']
    PROVIDER_CODE_PATTERNS = ['landlord code', 'provider code', 'rsh code', 'landlord_code', 'reg. no']

    def log(self, message):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def _detect_header_row(self, df_raw, max_scan_rows=15):
        """
        Scan the first N rows of a raw (headerless) DataFrame to find the
        header row by looking for known TP column patterns.
        Returns the 0-based row index of the header, or None if not found.
        """
        for row_idx in range(min(max_scan_rows, len(df_raw))):
            row_values = [str(v).strip() for v in df_raw.iloc[row_idx].values]
            row_text = ' '.join(row_values).lower()
            # A header row should contain at least TP01 and one other TP code
            has_tp01 = any(p.lower() in row_text for p in self.TP_HEADER_PATTERNS['TP01'])
            has_other = any(
                any(p.lower() in row_text for p in patterns)
                for tp, patterns in self.TP_HEADER_PATTERNS.items()
                if tp != 'TP01'
            )
            if has_tp01 and has_other:
                return row_idx
        return None

    def _detect_column_mapping(self, df_raw, dataset_type, expected_tp_codes=None):
        """
        Dynamically detect column mapping by finding the header row and matching
        column headers to known patterns. Falls back to hard-coded mapping if
        detection fails.

        Returns (header_row_index, column_mapping_dict) where column_mapping_dict
        maps integer column indices to names like 'provider_name', 'provider_code',
        'TP01', 'TP02', etc.
        """
        if expected_tp_codes is None:
            if dataset_type == 'LCHO':
                expected_tp_codes = [tp for tp in self.tp_codes if tp not in ['TP02', 'TP03', 'TP04']]
            else:
                expected_tp_codes = self.tp_codes

        header_row = self._detect_header_row(df_raw)
        if header_row is None:
            self.log(f"  ⚠️ Could not detect header row for {dataset_type}; using hard-coded mapping")
            if dataset_type == 'LCHO':
                return self.lcho_skiprows, self.lcho_column_mapping
            else:
                return self.lcra_skiprows, self.lcra_column_mapping

        headers = [str(v).strip() for v in df_raw.iloc[header_row].values]
        headers_lower = [h.lower() for h in headers]

        mapping = {}

        # Detect provider name column
        for col_idx, h in enumerate(headers_lower):
            if any(p in h for p in self.PROVIDER_NAME_PATTERNS):
                mapping[col_idx] = 'provider_name'
                break
        # Fallback: assume column 0 is provider name
        if 'provider_name' not in mapping.values():
            mapping[0] = 'provider_name'

        # Detect provider code column
        for col_idx, h in enumerate(headers_lower):
            if col_idx in mapping:
                continue
            if any(p in h for p in self.PROVIDER_CODE_PATTERNS):
                mapping[col_idx] = 'provider_code'
                break
        if 'provider_code' not in mapping.values():
            mapping[1] = 'provider_code'

        # Detect TP columns
        for tp_code in expected_tp_codes:
            patterns = self.TP_HEADER_PATTERNS.get(tp_code, [tp_code])
            best_col = None
            for col_idx, h in enumerate(headers_lower):
                if col_idx in mapping:
                    continue
                # Prefer exact TP code match (e.g. "tp01" or "(tp01)")
                for pattern in patterns:
                    if pattern.lower() in h:
                        # Avoid matching response count columns
                        if 'response' in h or 'count' in h or 'number' in h:
                            continue
                        best_col = col_idx
                        break
                if best_col is not None:
                    break
            if best_col is not None:
                mapping[best_col] = tp_code

        detected_tps = [v for v in mapping.values() if v.startswith('TP')]
        self.log(f"  Dynamic detection for {dataset_type}: found header at row {header_row}, "
                 f"detected {len(detected_tps)}/{len(expected_tp_codes)} TP columns")

        # Validate: if we found fewer than half the expected TP columns, fall back
        if len(detected_tps) < len(expected_tp_codes) // 2:
            self.log(f"  ⚠️ Too few TP columns detected ({len(detected_tps)}); falling back to hard-coded mapping")
            if dataset_type == 'LCHO':
                return self.lcho_skiprows, self.lcho_column_mapping
            else:
                return self.lcra_skiprows, self.lcra_column_mapping

        # Compare with hard-coded mapping for safety logging
        hardcoded = self.lcho_column_mapping if dataset_type == 'LCHO' else self.lcra_column_mapping
        for col_idx, name in hardcoded.items():
            if name.startswith('TP') and name in mapping.values():
                detected_idx = [k for k, v in mapping.items() if v == name][0]
                if detected_idx != col_idx:
                    self.log(f"  ⚠️ Column shift detected: {name} expected at col {col_idx}, found at col {detected_idx}")

        # Data starts on the row after the header
        data_start_row = header_row + 1
        return data_start_row, mapping

    def _validate_tp_columns(self, df, dataset_type):
        """Validate that TP columns contain plausible percentage scores (0-100)."""
        tp_cols = [col for col in df.columns if col.startswith('TP')]
        for tp_col in tp_cols:
            numeric_vals = pd.to_numeric(df[tp_col], errors='coerce').dropna()
            if len(numeric_vals) == 0:
                self.log(f"  ⚠️ {dataset_type} column {tp_col}: no numeric values found")
                continue
            in_range = ((numeric_vals >= 0) & (numeric_vals <= 100)).sum()
            pct_valid = in_range / len(numeric_vals) * 100
            if pct_valid < 50:
                self.log(f"  ⚠️ {dataset_type} column {tp_col}: only {pct_valid:.0f}% of values in 0-100 range — possible column mismatch")
        
    def load_table_coverage(self):
        """Load the Table_Coverage sheet to identify provider types"""
        self.log("📋 Loading Table_Coverage to identify provider types...")

        try:
            # Determine year prefix for column matching
            year_suffix = str(self.year)[2:]  # e.g. "24" or "25"
            tsm_prefix = f'tsm{year_suffix}'

            # Read raw to detect header row dynamically
            df_raw = pd.read_excel(self.excel_path, sheet_name='Table_Coverage', header=None)

            # Find the header row by looking for "Landlord" or "Provider" in first column
            header_row = None
            for row_idx in range(min(15, len(df_raw))):
                cell = str(df_raw.iloc[row_idx, 0]).lower()
                if 'landlord' in cell or 'provider' in cell or 'organisation' in cell:
                    header_row = row_idx
                    break

            if header_row is None:
                # Fallback to hardcoded skiprows
                self.log("  ⚠️ Could not detect Table_Coverage header; using skiprows=3")
                header_row = 3

            # Re-read with detected header
            coverage_df = pd.read_excel(self.excel_path, sheet_name='Table_Coverage',
                                        skiprows=header_row)

            # Normalize column names for matching
            coverage_df.columns = [str(c).strip().lower().replace(' ', '_') for c in coverage_df.columns]

            # Map to standardized names
            col_renames = {}
            for col in coverage_df.columns:
                if 'landlord_name' in col or 'provider_name' in col or 'organisation' in col:
                    col_renames[col] = 'landlord_name'
                elif 'landlord_code' in col or 'provider_code' in col or 'reg' in col:
                    col_renames[col] = 'landlord_code'
                elif 'landlord_type' in col or 'provider_type' in col or 'type' in col:
                    if 'landlord_type' not in col_renames.values():
                        col_renames[col] = 'landlord_type'
                elif 'lcra_perception' in col or f'{tsm_prefix}_lcra' in col:
                    col_renames[col] = 'lcra_perception'
                elif 'lcho_perception' in col or f'{tsm_prefix}_lcho' in col:
                    col_renames[col] = 'lcho_perception'
                elif 'combined_perception' in col or f'{tsm_prefix}_combined' in col:
                    col_renames[col] = 'combined_perception'

            coverage_df = coverage_df.rename(columns=col_renames)

            # Ensure required columns exist
            for required in ['landlord_code']:
                if required not in coverage_df.columns:
                    self.log(f"  ⚠️ Required column '{required}' not found in Table_Coverage")
                    raise ValueError(f"Missing required column: {required}")

            # Clean the data
            coverage_df['landlord_code'] = coverage_df['landlord_code'].astype(str).str.strip()
            coverage_df = coverage_df.dropna(subset=['landlord_code'])
            coverage_df = coverage_df[coverage_df['landlord_code'] != '']

            # Create dataset type mapping
            lcra_col = 'lcra_perception' if 'lcra_perception' in coverage_df.columns else None
            lcho_col = 'lcho_perception' if 'lcho_perception' in coverage_df.columns else None
            combined_col = 'combined_perception' if 'combined_perception' in coverage_df.columns else None

            def determine_dataset_type(row):
                if combined_col and str(row.get(combined_col, '')).strip().lower() == 'yes':
                    return 'COMBINED'
                if lcra_col and str(row.get(lcra_col, '')).strip().lower() == 'yes':
                    return 'LCRA'
                if lcho_col and str(row.get(lcho_col, '')).strip().lower() == 'yes':
                    return 'LCHO'
                return None

            coverage_df['dataset_type'] = coverage_df.apply(determine_dataset_type, axis=1)
            
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
            df_raw = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)

            # Detect columns dynamically, with hard-coded fallback
            data_start_row, column_mapping = self._detect_column_mapping(df_raw, 'LCRA')

            # Slice data rows and select mapped columns
            df = df_raw.iloc[data_start_row:].reset_index(drop=True)
            selected_columns = list(column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [column_mapping[col] for col in selected_columns]
            
            # Clean data
            df = df[df['provider_code'].notna()]
            df['provider_code'] = df['provider_code'].astype(str).str.strip()
            
            # Convert TP columns to numeric
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            for tp_col in tp_cols:
                df[tp_col] = pd.to_numeric(df[tp_col], errors='coerce')

            # Validate extracted columns contain plausible scores
            self._validate_tp_columns(df, 'LCRA')

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
            df_raw = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)

            # Detect columns dynamically, with hard-coded fallback
            lcho_tp_codes = [tp for tp in self.tp_codes if tp not in ['TP02', 'TP03', 'TP04']]
            data_start_row, column_mapping = self._detect_column_mapping(
                df_raw, 'LCHO', expected_tp_codes=lcho_tp_codes)

            # Slice data rows and select mapped columns
            df = df_raw.iloc[data_start_row:].reset_index(drop=True)
            selected_columns = list(column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [column_mapping[col] for col in selected_columns]
            
            # Clean data
            df = df[df['provider_code'].notna()]
            df['provider_code'] = df['provider_code'].astype(str).str.strip()
            
            # Convert TP columns to numeric
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            for tp_col in tp_cols:
                df[tp_col] = pd.to_numeric(df[tp_col], errors='coerce')
            
            # Validate extracted columns contain plausible scores
            self._validate_tp_columns(df, 'LCHO')

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
            df_raw = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)

            # Detect columns dynamically (Combined uses same layout as LCRA)
            data_start_row, column_mapping = self._detect_column_mapping(df_raw, 'COMBINED')

            # Slice data rows and select mapped columns
            df = df_raw.iloc[data_start_row:].reset_index(drop=True)
            selected_columns = list(column_mapping.keys())
            df = df.iloc[:, selected_columns]
            df.columns = [column_mapping[col] for col in selected_columns]
            
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
                con.execute("DELETE FROM raw_scores WHERE year = ?", [self.year])
                con.execute("DELETE FROM calculated_percentiles WHERE year = ?", [self.year])
                con.execute("DELETE FROM calculated_correlations WHERE year = ?", [self.year])
                con.execute("DELETE FROM provider_summary WHERE year = ?", [self.year])
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
                result = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()
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
            
            # Remove COMBINED entries where provider already exists in LCRA or LCHO.
            # Providers legitimately appear in BOTH LCRA and LCHO with different
            # scores (different housing schemes) — both must be kept.
            if not combined_df.empty:
                lcra_codes = set(lcra_df['provider_code'])
                lcho_codes = set(lcho_df['provider_code'])
                before_filter = len(combined_df)
                combined_df = combined_df[
                    ~combined_df['provider_code'].isin(lcra_codes | lcho_codes)
                ]
                removed = before_filter - len(combined_df)
                if removed > 0:
                    self.log(f"  Removed {removed} COMBINED entries (already in LCRA/LCHO)")
                self.log(f"  Kept {len(combined_df)} COMBINED-only providers")

            # Combine all data — LCRA and LCHO entries for the same provider are
            # intentionally kept as separate rows (different schemes, different scores)
            all_data = pd.concat([lcra_df, lcho_df, combined_df], ignore_index=True)
            self.log(f"  Total rows after merge: {len(all_data)} "
                     f"(LCRA: {(all_data['dataset_type']=='LCRA').sum()}, "
                     f"LCHO: {(all_data['dataset_type']=='LCHO').sum()}, "
                     f"COMBINED: {(all_data['dataset_type']=='COMBINED').sum()})")

            # Add year column to wide-format data
            all_data['year'] = self.year
            
            # Phase 3: Transform to long format (from deduplicated wide data)
            all_raw_scores_parts = []
            for ds_type in all_data['dataset_type'].unique():
                ds_subset = all_data[all_data['dataset_type'] == ds_type]
                long_part = self.transform_to_long_format(ds_subset, ds_type)
                if not long_part.empty:
                    all_raw_scores_parts.append(long_part)
            all_raw_scores = pd.concat(all_raw_scores_parts, ignore_index=True)
            
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