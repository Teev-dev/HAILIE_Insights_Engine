import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
import openpyxl
from io import BytesIO
import os
import traceback
import re
import time
from contextlib import contextmanager

class TSMDataProcessor:
    """
    Handles loading, cleaning, and validation of UK government TSM data
    """
    
    def __init__(self, silent_mode=False):
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]  # TP01 to TP12
        self.required_columns = ['provider_code', 'provider_name'] + self.tp_codes
        self.default_data_path = "attached_assets/2024_TSM_Full_Data_v1.1_FINAL_1756577982265.xlsx"
        self.silent_mode = silent_mode
        self.mobile_timeout_seconds = 30
        self.desktop_timeout_seconds = 60
        
    def _log_info(self, msg):
        """Log info message if not in silent mode"""
        if not self.silent_mode:
            st.info(msg)
            
    def _log_warning(self, msg):
        """Log warning message if not in silent mode"""
        if not self.silent_mode:
            st.warning(msg)
            
    def _log_success(self, msg):
        """Log success message if not in silent mode"""
        if not self.silent_mode:
            st.success(msg)
            
    def _log_error(self, msg):
        """Always show errors regardless of silent mode"""
        st.error(msg)
    
    @contextmanager
    def _timeout_handler(self, operation_name: str):
        """Context manager for handling timeouts with mobile-friendly messages"""
        start_time = time.time()
        is_mobile = self._detect_mobile_device()
        timeout_limit = self.mobile_timeout_seconds if is_mobile else self.desktop_timeout_seconds
        
        try:
            yield
            elapsed = time.time() - start_time
            if elapsed > 10:  # Log slow operations
                device_type = "mobile" if is_mobile else "desktop"
                self._log_info(f"⏱️ {operation_name} completed in {elapsed:.1f}s on {device_type}")
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > timeout_limit:
                if is_mobile:
                    self._log_error(f"📱 Mobile Timeout: {operation_name} is taking longer than expected on mobile. Try using WiFi or a faster connection.")
                    st.info("💡 **Mobile Performance Tip**: Large data files may load slowly on mobile devices. Consider using a desktop computer for better performance.")
                else:
                    self._log_error(f"⏱️ Timeout: {operation_name} took too long to complete. Please check your internet connection.")
                st.info("🔄 **Retry Options**: Refresh the page or try selecting a different provider.")
            raise e
    
    def _detect_mobile_device(self) -> bool:
        """Detect if user is on a mobile device based on Streamlit user agent"""
        try:
            # Check if we're in a mobile-like environment
            # This is a simple heuristic - in production you'd use proper user agent detection
            if hasattr(st, 'session_state') and 'user_agent' in st.session_state:
                user_agent = st.session_state.user_agent.lower()
                mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
                return any(indicator in user_agent for indicator in mobile_indicators)
            return False
        except:
            return False
    
    def _get_cached_excel_file(self):
        """
        Get cached Excel file object or create new one with timeout protection
        """
        if 'excel_file_cache' not in st.session_state:
            if not os.path.exists(self.default_data_path):
                return None
            with self._timeout_handler("Loading Excel file metadata"):
                st.session_state.excel_file_cache = pd.ExcelFile(self.default_data_path)
        return st.session_state.excel_file_cache
    
    def _get_cached_sheet_names(self) -> Optional[List[str]]:
        """
        Get cached sheet names or load them for the first time
        """
        if 'sheet_names_cache' not in st.session_state:
            xl_file = self._get_cached_excel_file()
            if xl_file is None:
                return None
            st.session_state.sheet_names_cache = xl_file.sheet_names
        return st.session_state.sheet_names_cache
        
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
            
            self._log_info(f"📋 Found {len(sheet_names)} sheets: {', '.join(sheet_names[:5])}{'...' if len(sheet_names) > 5 else ''}")
            
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
                        self._log_success(f"✅ Using sheet: '{matching_sheets[0]}'")
                        break
                    except Exception as e:
                        self._log_warning(f"⚠️ Could not read sheet '{matching_sheets[0]}': {str(e)}")
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
                    self._log_info(f"📊 Using largest sheet: '{largest_sheet}' ({max_rows} rows)")
            
            # Last resort: use first sheet
            if main_df is None:
                main_df = pd.read_excel(file_buffer, sheet_name=sheet_names[0])
                self._log_warning(f"⚠️ Using first sheet: '{sheet_names[0]}'")
            
            return main_df
            
        except Exception as e:
            self._log_error(f"❌ Error loading Excel file: {str(e)}")
            return None
    
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
            
            self._log_info(f"📋 Loaded Table Coverage data for {len(coverage_df)} providers")
            
            # Ensure we return a DataFrame or None
            if isinstance(coverage_df, pd.DataFrame):
                return coverage_df
            else:
                self._log_error("❌ Table Coverage data is not a DataFrame")
                return None
            
        except Exception as e:
            self._log_warning(f"⚠️ Could not load Table Coverage sheet: {str(e)}")
            return None

    def get_provider_options(self) -> Optional[Dict[str, str]]:
        """
        Get a dictionary of provider options for dropdown selection with caching and timeout handling
        Returns {"Provider Name (Code)": "Code"} mapping
        """
        # Check if provider options are already cached in session state
        if 'provider_options' in st.session_state:
            if not self.silent_mode:
                st.success("📋 Using cached provider options")
            return st.session_state.provider_options
        
        with self._timeout_handler("Loading provider options"):
            try:
                if not self.silent_mode:
                    st.info("📋 Loading provider options for the first time...")
                
                coverage_df = self.load_table_coverage()
                if coverage_df is None:
                    return None
                
                # Create a mapping of display names to codes
                provider_options = {}
                for _, row in coverage_df.iterrows():
                    name = str(row['landlord_name']).strip()
                    code = str(row['landlord_code']).strip()
                    if name and code and name != 'nan' and code != 'nan':
                        display_name = f"{name} ({code})"
                        provider_options[display_name] = code
                
                # Cache the results in session state
                st.session_state.provider_options = provider_options
                
                if not self.silent_mode:
                    st.success(f"✅ Loaded {len(provider_options)} provider options")
                
                return provider_options
                
            except Exception as e:
                self._log_warning(f"⚠️ Could not load provider options: {str(e)}")
                # Provide retry guidance for mobile users
                if self._detect_mobile_device():
                    st.info("📱 **Mobile Tip**: If loading is slow, try switching to WiFi or refresh the page.")
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
            self._log_warning(f"⚠️ Provider code '{provider_code}' not found in Table Coverage")
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
            self._log_warning(f"⚠️ No perception data available for provider '{provider_code}' in any TSM24 sheet")
            return provider_type, None
        
        self._log_success(f"✅ Provider '{provider_code}' found in {selected_sheet} (Type: {provider_type}, Data: {sheet_type})")
        return provider_type, selected_sheet

    def load_default_data(self, provider_code: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load the default 2024 TSM data file with caching optimization and timeout handling
        If provider_code is provided, use the appropriate TSM24 sheet for that provider type
        """
        with self._timeout_handler(f"Loading TSM data for provider {provider_code}"):
            try:
                if not os.path.exists(self.default_data_path):
                    self._log_error(f"❌ Default data file not found: {self.default_data_path}")
                    return None
                
                self._log_info("📊 Loading default 2024 TSM data...")
                
                # Get cached sheet names (much faster than reloading Excel file)
                sheet_names = self._get_cached_sheet_names()
                if sheet_names is None:
                    self._log_error("❌ Could not load sheet names from Excel file")
                    return None
                
                if not self.silent_mode:
                    st.info(f"📋 Found {len(sheet_names)} sheets in default data")
                else:
                    self._log_info(f"📋 Found {len(sheet_names)} sheets in default data")
                
                # Try to find the main data sheet
                main_df = None
                selected_sheet = None
                
                # If provider code is provided, try to determine the appropriate sheet
                if provider_code:
                    provider_type, target_sheet = self.get_provider_type_and_sheet(provider_code)
                    if target_sheet and target_sheet in sheet_names:
                        try:
                            # TSM24 sheets have a specific structure:
                            # Row 0: Sheet title
                            # Row 1: Navigation 
                            # Row 2: Headers (including TP measures)
                            # Row 3+: Data
                            if target_sheet.startswith('TSM24_'):
                                self._log_info(f"📖 Reading TSM24 sheet with special structure: '{target_sheet}'")
                                # Read with row 2 as header using cached Excel file
                                xl_file = self._get_cached_excel_file()
                                main_df = pd.read_excel(xl_file, sheet_name=target_sheet, header=2)
                                selected_sheet = target_sheet
                                self._log_success(f"✅ Using provider-specific TSM24 sheet: '{target_sheet}' for provider '{provider_code}'")
                                
                                # Log column info for debugging
                                if not self.silent_mode and main_df is not None:
                                    with st.expander("🔍 Debug: Column Analysis", expanded=False):
                                        st.write(f"Total columns loaded: {len(main_df.columns)}")
                                        tp_cols = [col for col in main_df.columns if 'TP' in str(col).upper()]
                                        st.write(f"Columns containing 'TP': {len(tp_cols)}")
                                        if tp_cols:
                                            st.write("Sample TP columns found:")
                                            for col in tp_cols[:5]:
                                                st.write(f"  - {col[:80]}...")
                            else:
                                xl_file = self._get_cached_excel_file()
                                main_df = pd.read_excel(xl_file, sheet_name=target_sheet)
                                selected_sheet = target_sheet
                                self._log_success(f"✅ Using provider-specific sheet: '{target_sheet}' for provider '{provider_code}'")
                        except Exception as e:
                            self._log_warning(f"⚠️ Could not read provider-specific sheet '{target_sheet}': {str(e)}")
                            self._log_info("🔄 Falling back to general sheet selection...")
                
                # If no provider-specific sheet was loaded, use general logic
                if main_df is None:
                    # Priority order for sheet selection
                    priority_keywords = ['data', 'tsm', 'satisfaction', 'provider', 'main', 'results']
                    
                    # First, try sheets with priority keywords
                    for keyword in priority_keywords:
                        matching_sheets = [sheet for sheet in sheet_names if keyword.lower() in sheet.lower()]
                        if matching_sheets:
                            try:
                                xl_file = self._get_cached_excel_file()
                                main_df = pd.read_excel(xl_file, sheet_name=matching_sheets[0])
                                selected_sheet = matching_sheets[0]
                                self._log_success(f"✅ Using default data sheet: '{matching_sheets[0]}'")
                                break
                            except Exception as e:
                                self._log_warning(f"⚠️ Could not read sheet '{matching_sheets[0]}': {str(e)}")
                                continue
                    
                    # If no priority sheet worked, try the largest sheet
                    if main_df is None:
                        largest_sheet = None
                        max_rows = 0
                        xl_file = self._get_cached_excel_file()
                        
                        for sheet_name in sheet_names:
                            try:
                                temp_df = pd.read_excel(xl_file, sheet_name=sheet_name, nrows=1)
                                sheet_df = pd.read_excel(xl_file, sheet_name=sheet_name)
                                
                                if len(sheet_df) > max_rows:
                                    max_rows = len(sheet_df)
                                    largest_sheet = sheet_name
                                    main_df = sheet_df
                                    
                            except Exception:
                                continue
                        
                        if main_df is not None:
                            selected_sheet = largest_sheet
                            self._log_info(f"📊 Using largest default data sheet: '{largest_sheet}' ({max_rows} rows)")
                    
                    # Last resort: use first sheet
                    if main_df is None:
                        xl_file = self._get_cached_excel_file()
                        main_df = pd.read_excel(xl_file, sheet_name=sheet_names[0])
                        selected_sheet = sheet_names[0]
                        self._log_warning(f"⚠️ Using first sheet from default data: '{sheet_names[0]}'")
                
                return main_df
                
            except Exception as e:
                self._log_error(f"❌ Error loading default data file: {str(e)}")
                return None

    # Rest of the methods remain the same - continuing from here...
    def clean_and_validate(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Clean and validate TSM data
        """
        try:
            if df is None or df.empty:
                return None
            
            self._log_info(f"🔍 Processing dataset with {len(df)} rows and {len(df.columns)} columns")
            
            # Display column names for debugging
            if not self.silent_mode:
                with st.expander("📋 Available Columns", expanded=False):
                    st.write("Available columns:")
                    st.write(list(df.columns))
            
            # Try to identify provider code columns
            provider_col = self._identify_provider_column(df)
            if provider_col is None:
                self._log_error("❌ Could not identify provider code column")
                return None
            
            self._log_info(f"📌 Found provider code column: '{provider_col}'")
            
            # Try to identify provider name column
            name_col = self._identify_name_column(df)
            if name_col:
                self._log_info(f"📌 Found provider name column: '{name_col}'")
            
            # Try to identify TP columns
            tp_columns = self._identify_tp_columns(df)
            
            if not tp_columns:
                self._log_error("❌ Could not identify any TP01-TP12 satisfaction measure columns")
                return None
            
            self._log_success(f"✅ Found {len(tp_columns)} TP satisfaction measures")
            
            # Create cleaned dataset
            cleaned_df = df.copy()
            
            # Standardize column names
            column_mapping = {provider_col: 'provider_code'}
            if name_col:
                column_mapping[name_col] = 'provider_name'
            
            # Map TP columns
            for original_col, tp_code in tp_columns.items():
                column_mapping[original_col] = tp_code
            
            # Debug: Check for duplicate mappings
            if not self.silent_mode:
                with st.expander("🔍 Debug: Column Mapping", expanded=False):
                    st.write("Column mapping:")
                    for old, new in list(column_mapping.items())[:15]:
                        st.write(f"  '{old[:50]}...' -> '{new}'")
                    
                    # Check for duplicate target names
                    target_names = list(column_mapping.values())
                    duplicates = [name for name in target_names if target_names.count(name) > 1]
                    if duplicates:
                        self._log_warning(f"Duplicate target column names found: {set(duplicates)}")
            else:
                # Still check for duplicates even in silent mode
                target_names = list(column_mapping.values())
                duplicates = [name for name in target_names if target_names.count(name) > 1]
                if duplicates:
                    self._log_warning(f"Duplicate target column names found: {set(duplicates)}")
            
            cleaned_df = cleaned_df.rename(columns=column_mapping)
            
            # Check if rename created any issues
            if cleaned_df.columns.duplicated().any():
                self._log_warning("⚠️ Duplicate column names detected after renaming!")
                duplicated_cols = cleaned_df.columns[cleaned_df.columns.duplicated()].tolist()
                if not self.silent_mode:
                    st.write(f"Duplicated columns: {duplicated_cols}")
            
            # Select only relevant columns
            relevant_cols = ['provider_code']
            if name_col:
                relevant_cols.append('provider_name')
            
            # Use unique TP column values
            unique_tp_codes = list(set(tp_columns.values()))
            relevant_cols.extend(unique_tp_codes)
            
            # Debug: Check what columns we're trying to select
            if not self.silent_mode:
                with st.expander("🔍 Debug: Column Selection", expanded=False):
                    st.write(f"Trying to select columns: {relevant_cols}")
                    st.write(f"Available columns after rename: {list(cleaned_df.columns)[:20]}...")
                    missing_cols = [col for col in relevant_cols if col not in cleaned_df.columns]
                    if missing_cols:
                        self._log_warning(f"Missing columns: {missing_cols}")
            else:
                # Still check for missing columns in silent mode
                missing_cols = [col for col in relevant_cols if col not in cleaned_df.columns]
                if missing_cols:
                    self._log_warning(f"Missing columns: {missing_cols}")
            
            # Make sure all columns exist before selecting
            relevant_cols = [col for col in relevant_cols if col in cleaned_df.columns]
            
            # Handle duplicate columns if they exist
            if cleaned_df.columns.duplicated().any():
                # Keep only first occurrence of duplicated columns
                cleaned_df = cleaned_df.loc[:, ~cleaned_df.columns.duplicated()]
                self._log_info("ℹ️ Removed duplicate columns after renaming")
            
            # Now select the columns
            cleaned_df = cleaned_df[relevant_cols]
            
            # Clean provider codes - ensure we have a DataFrame
            if isinstance(cleaned_df, pd.DataFrame):
                cleaned_df['provider_code'] = cleaned_df['provider_code'].astype(str).str.strip()
            else:
                self._log_error("❌ Data structure error: expected DataFrame but got array")
                return None
            
            # Remove rows with missing provider codes
            initial_count = len(cleaned_df)
            cleaned_df = cleaned_df.dropna(subset=['provider_code'])
            cleaned_df = cleaned_df[cleaned_df['provider_code'] != '']
            
            if len(cleaned_df) < initial_count:
                self._log_info(f"🧹 Removed {initial_count - len(cleaned_df)} rows with missing provider codes")
            
            if len(cleaned_df) == 0:
                self._log_error("❌ No valid provider data found after cleaning")
                return None
            
            # Convert TP columns to numeric
            tp_cols = [col for col in cleaned_df.columns if col.startswith('TP')]
            for col in tp_cols:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
            
            self._log_success(f"✅ Data cleaned successfully: {len(cleaned_df)} providers with {len(tp_cols)} TP measures")
            
            return cleaned_df
            
        except Exception as e:
            self._log_error(f"❌ Error cleaning data: {str(e)}")
            return None
    
    def _identify_provider_column(self, df: pd.DataFrame) -> Optional[str]:
        """Identify the provider code column"""
        provider_keywords = ['provider', 'code', 'landlord', 'organisation', 'org']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in provider_keywords):
                if 'code' in col_lower or 'id' in col_lower:
                    return col
        
        # Look for columns with provider-like patterns (e.g., H followed by numbers)
        for col in df.columns:
            sample_values = df[col].dropna().astype(str).head(10)
            if any(val.strip().startswith(('H', 'L')) and len(val.strip()) >= 4 for val in sample_values):
                return col
        
        return None
    
    def _identify_name_column(self, df: pd.DataFrame) -> Optional[str]:
        """Identify the provider name column"""
        name_keywords = ['name', 'organisation', 'org', 'landlord', 'provider']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in name_keywords):
                if 'name' in col_lower and 'code' not in col_lower:
                    return col
        
        return None
    
    def _identify_tp_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify TP satisfaction measure columns"""
        tp_columns = {}
        
        # Look for exact TP01-TP12 patterns
        for col in df.columns:
            col_str = str(col)
            # Check for exact TP patterns
            for tp_code in self.tp_codes:
                if tp_code in col_str:
                    tp_columns[col] = tp_code
                    break
        
        return tp_columns
    
    def get_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """Get data quality report (alias for generate_data_quality_report)"""
        return self.generate_data_quality_report(df)
    
    def generate_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """Generate a data quality report"""
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