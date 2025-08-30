import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
import openpyxl
from io import BytesIO
import os

class TSMDataProcessor:
    """
    Handles loading, cleaning, and validation of UK government TSM data
    """
    
    def __init__(self):
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]  # TP01 to TP12
        self.required_columns = ['provider_code', 'provider_name'] + self.tp_codes
        self.default_data_path = "attached_assets/2024_TSM_Full_Data_v1.1_FINAL_1756577982265.xlsx"
        
    def load_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Load Excel file and attempt to find TSM data across multiple sheets
        """
        try:
            # Read the uploaded file into BytesIO
            file_buffer = BytesIO(uploaded_file.read())
            
            # Get all sheet names
            xl_file = pd.ExcelFile(file_buffer)
            sheet_names = xl_file.sheet_names
            
            st.info(f"📋 Found {len(sheet_names)} sheets: {', '.join(sheet_names[:5])}{'...' if len(sheet_names) > 5 else ''}")
            
            # Try to find the main data sheet
            main_df = None
            
            # Priority order for sheet selection
            priority_keywords = ['data', 'tsm', 'satisfaction', 'provider', 'main', 'results']
            
            # First, try sheets with priority keywords
            for keyword in priority_keywords:
                matching_sheets = [sheet for sheet in sheet_names if keyword.lower() in sheet.lower()]
                if matching_sheets:
                    try:
                        main_df = pd.read_excel(file_buffer, sheet_name=matching_sheets[0])
                        st.success(f"✅ Using sheet: '{matching_sheets[0]}'")
                        break
                    except Exception as e:
                        st.warning(f"⚠️ Could not read sheet '{matching_sheets[0]}': {str(e)}")
                        continue
            
            # If no priority sheet worked, try the largest sheet
            if main_df is None:
                largest_sheet = None
                max_rows = 0
                
                for sheet_name in sheet_names:
                    try:
                        temp_df = pd.read_excel(file_buffer, sheet_name=sheet_name, nrows=1)
                        sheet_df = pd.read_excel(file_buffer, sheet_name=sheet_name)
                        
                        if len(sheet_df) > max_rows:
                            max_rows = len(sheet_df)
                            largest_sheet = sheet_name
                            main_df = sheet_df
                            
                    except Exception:
                        continue
                
                if main_df is not None:
                    st.info(f"📊 Using largest sheet: '{largest_sheet}' ({max_rows} rows)")
            
            # Last resort: use first sheet
            if main_df is None:
                main_df = pd.read_excel(file_buffer, sheet_name=sheet_names[0])
                st.warning(f"⚠️ Using first sheet: '{sheet_names[0]}'")
            
            return main_df
            
        except Exception as e:
            st.error(f"❌ Error loading Excel file: {str(e)}")
            return None
    
    def clean_and_validate(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Clean and validate TSM data
        """
        try:
            if df is None or df.empty:
                return None
            
            st.info(f"🔍 Processing dataset with {len(df)} rows and {len(df.columns)} columns")
            
            # Display column names for debugging
            with st.expander("📋 Available Columns", expanded=False):
                st.write("Available columns:")
                st.write(list(df.columns))
            
            # Try to identify provider code columns
            provider_col = self._identify_provider_column(df)
            if provider_col is None:
                st.error("❌ Could not identify provider code column")
                return None
            
            # Try to identify provider name column
            name_col = self._identify_name_column(df)
            
            # Try to identify TP columns
            tp_columns = self._identify_tp_columns(df)
            
            if not tp_columns:
                st.error("❌ Could not identify any TP01-TP12 satisfaction measure columns")
                return None
            
            st.success(f"✅ Found {len(tp_columns)} TP satisfaction measures")
            
            # Create cleaned dataset
            cleaned_df = df.copy()
            
            # Standardize column names
            column_mapping = {provider_col: 'provider_code'}
            if name_col:
                column_mapping[name_col] = 'provider_name'
            
            # Map TP columns
            for original_col, tp_code in tp_columns.items():
                column_mapping[original_col] = tp_code
            
            cleaned_df = cleaned_df.rename(columns=column_mapping)
            
            # Select only relevant columns
            relevant_cols = ['provider_code']
            if name_col:
                relevant_cols.append('provider_name')
            relevant_cols.extend(tp_columns.values())
            
            cleaned_df = cleaned_df[relevant_cols]
            
            # Clean provider codes
            cleaned_df['provider_code'] = cleaned_df['provider_code'].astype(str).str.strip()
            
            # Remove rows with missing provider codes
            cleaned_df = cleaned_df.dropna(subset=['provider_code'])
            cleaned_df = cleaned_df[cleaned_df['provider_code'] != '']
            
            # Convert TP columns to numeric
            for tp_code in tp_columns.values():
                if tp_code in cleaned_df.columns:
                    cleaned_df[tp_code] = pd.to_numeric(cleaned_df[tp_code], errors='coerce')
            
            # Remove rows with all missing TP values
            tp_cols_present = [col for col in tp_columns.values() if col in cleaned_df.columns]
            cleaned_df = cleaned_df.dropna(subset=tp_cols_present, how='all')
            
            st.info(f"✅ Cleaned dataset: {len(cleaned_df)} providers with satisfaction data")
            
            return cleaned_df
            
        except Exception as e:
            st.error(f"❌ Error cleaning data: {str(e)}")
            return None
    
    def _identify_provider_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Identify the provider code column
        """
        possible_names = [
            'provider_code', 'provider code', 'providercode',
            'rsh_code', 'rsh code', 'rshcode',
            'org_code', 'org code', 'orgcode',
            'organisation_code', 'organisation code',
            'code', 'id', 'provider_id', 'provider id'
        ]
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in possible_names:
                return col
        
        # Look for columns with 'provider' and 'code' in name
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if 'provider' in col_lower and 'code' in col_lower:
                return col
        
        # Look for columns that look like codes (short strings/numbers)
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().head(10).astype(str)
                if len(sample_values) > 0:
                    avg_length = sample_values.str.len().mean()
                    if 2 <= avg_length <= 10:  # Reasonable length for provider codes
                        return col
        
        return None
    
    def _identify_name_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        Identify the provider name column
        """
        possible_names = [
            'provider_name', 'provider name', 'providername',
            'organisation_name', 'organisation name', 'organisationname',
            'org_name', 'org name', 'orgname',
            'name', 'organisation', 'provider'
        ]
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in possible_names:
                return col
        
        return None
    
    def _identify_tp_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Identify TP01-TP12 satisfaction measure columns
        """
        tp_columns = {}
        
        for col in df.columns:
            col_str = str(col).upper().strip()
            
            # Direct match (e.g., "TP01", "TP02", etc.)
            for tp_code in self.tp_codes:
                if tp_code in col_str:
                    tp_columns[col] = tp_code
                    break
            
            # Look for patterns like "TP 01", "TP-01", "TP_01"
            for i in range(1, 13):
                patterns = [
                    f"TP {i:02d}", f"TP-{i:02d}", f"TP_{i:02d}",
                    f"TP {i}", f"TP-{i}", f"TP_{i}"
                ]
                
                for pattern in patterns:
                    if pattern in col_str:
                        tp_code = f"TP{i:02d}"
                        tp_columns[col] = tp_code
                        break
        
        return tp_columns
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a data quality report
        """
        if df is None or df.empty:
            return {}
        
        tp_cols = [col for col in df.columns if col.startswith('TP')]
        
        quality_report = {
            'total_providers': len(df),
            'providers_with_data': len(df.dropna(subset=tp_cols, how='all')),
            'tp_measures_found': len(tp_cols),
            'completeness_by_measure': {},
            'data_ranges': {}
        }
        
        for col in tp_cols:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                quality_report['completeness_by_measure'][col] = {
                    'count': non_null_count,
                    'percentage': (non_null_count / len(df)) * 100
                }
                
                if non_null_count > 0:
                    quality_report['data_ranges'][col] = {
                        'min': df[col].min(),
                        'max': df[col].max(),
                        'mean': df[col].mean()
                    }
        
        return quality_report
    
    def load_table_coverage(self) -> Optional[pd.DataFrame]:
        """
        Load and parse the Table Coverage sheet to identify provider types
        """
        try:
            if not os.path.exists(self.default_data_path):
                return None
            
            # Read the Table_Coverage sheet with proper header row
            coverage_df = pd.read_excel(self.default_data_path, sheet_name='Table_Coverage', skiprows=3)
            
            # Clean the column names
            coverage_df.columns = ['landlord_name', 'landlord_code', 'landlord_type', 
                                 'tsm24_lcra_perception', 'tsm24_lcho_perception', 
                                 'tsm24_combined_perception', 'tsm24_management_info',
                                 'tsm24_perception_not_inc', 'tsm24_man_info_not_inc']
            
            # Clean the data
            coverage_df['landlord_code'] = coverage_df['landlord_code'].astype(str).str.strip()
            coverage_df = coverage_df.dropna(subset=['landlord_code'])
            coverage_df = coverage_df[coverage_df['landlord_code'] != '']
            
            st.info(f"📋 Loaded Table Coverage data for {len(coverage_df)} providers")
            
            return coverage_df
            
        except Exception as e:
            st.warning(f"⚠️ Could not load Table Coverage sheet: {str(e)}")
            return None

    def get_provider_type_and_sheet(self, provider_code: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Determine the provider type and appropriate TSM24 sheet for a given provider code
        Returns (provider_type, sheet_name) tuple
        """
        coverage_df = self.load_table_coverage()
        if coverage_df is None:
            return None, None
        
        # Find the provider in the coverage data
        provider_row = coverage_df[coverage_df['landlord_code'] == provider_code]
        
        if provider_row.empty:
            st.warning(f"⚠️ Provider code '{provider_code}' not found in Table Coverage")
            return None, None
        
        provider_row = provider_row.iloc[0]
        provider_type = provider_row['landlord_type']
        
        # Determine which TSM24 sheet to use based on available data
        if provider_row['tsm24_combined_perception'] == 'Yes':
            selected_sheet = 'TSM24_Combined_Perception'
            sheet_type = 'Combined'
        elif provider_row['tsm24_lcra_perception'] == 'Yes':
            selected_sheet = 'TSM24_LCRA_Perception'
            sheet_type = 'LCRA'
        elif provider_row['tsm24_lcho_perception'] == 'Yes':
            selected_sheet = 'TSM24_LCHO_Perception'
            sheet_type = 'LCHO'
        else:
            # Fallback - no perception data available
            st.warning(f"⚠️ No perception data available for provider '{provider_code}' in any TSM24 sheet")
            return provider_type, None
        
        st.success(f"✅ Provider '{provider_code}' found in {selected_sheet} (Type: {provider_type}, Data: {sheet_type})")
        return provider_type, selected_sheet

    def load_default_data(self, provider_code: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load the default 2024 TSM data file
        If provider_code is provided, use the appropriate TSM24 sheet for that provider type
        """
        try:
            if not os.path.exists(self.default_data_path):
                st.error(f"❌ Default data file not found: {self.default_data_path}")
                return None
            
            st.info("📊 Loading default 2024 TSM data...")
            
            # Get all sheet names
            xl_file = pd.ExcelFile(self.default_data_path)
            sheet_names = xl_file.sheet_names
            
            st.info(f"📋 Found {len(sheet_names)} sheets in default data")
            
            # Try to find the main data sheet
            main_df = None
            selected_sheet = None
            
            # If provider code is provided, try to determine the appropriate sheet
            if provider_code:
                provider_type, target_sheet = self.get_provider_type_and_sheet(provider_code)
                if target_sheet and target_sheet in sheet_names:
                    try:
                        main_df = pd.read_excel(self.default_data_path, sheet_name=target_sheet)
                        selected_sheet = target_sheet
                        st.success(f"✅ Using provider-specific sheet: '{target_sheet}' for provider '{provider_code}'")
                    except Exception as e:
                        st.warning(f"⚠️ Could not read provider-specific sheet '{target_sheet}': {str(e)}")
                        st.info("🔄 Falling back to general sheet selection...")
            
            # If no provider-specific sheet was loaded, use general logic
            if main_df is None:
                # Priority order for sheet selection
                priority_keywords = ['data', 'tsm', 'satisfaction', 'provider', 'main', 'results']
                
                # First, try sheets with priority keywords
                for keyword in priority_keywords:
                    matching_sheets = [sheet for sheet in sheet_names if keyword.lower() in sheet.lower()]
                    if matching_sheets:
                        try:
                            main_df = pd.read_excel(self.default_data_path, sheet_name=matching_sheets[0])
                            selected_sheet = matching_sheets[0]
                            st.success(f"✅ Using default data sheet: '{matching_sheets[0]}'")
                            break
                        except Exception as e:
                            st.warning(f"⚠️ Could not read sheet '{matching_sheets[0]}': {str(e)}")
                            continue
                
                # If no priority sheet worked, try the largest sheet
                if main_df is None:
                    largest_sheet = None
                    max_rows = 0
                    
                    for sheet_name in sheet_names:
                        try:
                            temp_df = pd.read_excel(self.default_data_path, sheet_name=sheet_name, nrows=1)
                            sheet_df = pd.read_excel(self.default_data_path, sheet_name=sheet_name)
                            
                            if len(sheet_df) > max_rows:
                                max_rows = len(sheet_df)
                                largest_sheet = sheet_name
                                main_df = sheet_df
                                
                        except Exception:
                            continue
                    
                    if main_df is not None:
                        selected_sheet = largest_sheet
                        st.info(f"📊 Using largest default data sheet: '{largest_sheet}' ({max_rows} rows)")
                
                # Last resort: use first sheet
                if main_df is None:
                    main_df = pd.read_excel(self.default_data_path, sheet_name=sheet_names[0])
                    selected_sheet = sheet_names[0]
                    st.warning(f"⚠️ Using first sheet from default data: '{sheet_names[0]}'")
            
            return main_df
            
        except Exception as e:
            st.error(f"❌ Error loading default data file: {str(e)}")
            return None
