"""
Enhanced Data Processor for HAILIE Analytics with LCRA/LCHO Dataset Separation
Handles automatic dataset detection and isolated peer comparisons
"""

import streamlit as st
import pandas as pd
import duckdb
import numpy as np
from typing import Optional, Dict, List, Tuple


class EnhancedTSMDataProcessor:
    """Enhanced processor for TSM data with dataset isolation"""
    
    def __init__(self, silent_mode=False):
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]  # TP01 to TP12
        # Updated to use the new enhanced database
        self.db_path = "attached_assets/hailie_analytics_v2.duckdb"
        self.silent_mode = silent_mode
        self._connection = None
        self._connect_to_db()
        
        # TP measure descriptions
        self.tp_descriptions = {
            'TP01': 'Overall satisfaction',
            'TP02': 'Satisfaction with repairs',
            'TP03': 'Time taken to complete repair',
            'TP04': 'Satisfaction with time taken',
            'TP05': 'Home well-maintained',
            'TP06': 'Home is safe',
            'TP07': 'Listens to views',
            'TP08': 'Keeps informed',
            'TP09': 'Treats fairly',
            'TP10': 'Complaints handling',
            'TP11': 'Communal areas clean',
            'TP12': 'Anti-social behaviour'
        }
        
    def _connect_to_db(self):
        """Connect to the enhanced DuckDB database"""
        try:
            self._connection = duckdb.connect(self.db_path, read_only=True)
            if not self.silent_mode:
                st.success("✅ Connected to enhanced analytics database")
        except Exception as e:
            if not self.silent_mode:
                st.error(f"❌ Failed to connect to database: {str(e)}")
            self._connection = None
            
    def _log_info(self, message):
        """Log info message"""
        if not self.silent_mode:
            st.info(message)
            
    def _log_error(self, message):
        """Log error message"""
        if not self.silent_mode:
            st.error(message)
            
    def get_provider_dataset_type(self, provider_code: str, provider_name: Optional[str] = None) -> Optional[str]:
        """
        Get the dataset type for a specific provider (LCRA, LCHO, or COMBINED)
        Now uses provider name suffix to determine dataset type when available
        """
        if not self._connection:
            return None
        
        # If provider_name is provided and has a suffix, extract dataset type from it
        if provider_name and ' - ' in provider_name:
            suffix = provider_name.split(' - ')[-1]
            if suffix in ['LCRA', 'LCHO', 'COMBINED']:
                return suffix
            
        # Otherwise, look it up in database (this shouldn't happen with new naming)
        query = """
        SELECT dataset_type 
        FROM provider_dataset_mapping 
        WHERE provider_code = ? AND dataset_type != 'COMBINED'
        ORDER BY 
            CASE 
                WHEN dataset_type = 'LCRA' THEN 1  -- Prioritize LCRA (full metrics)
                WHEN dataset_type = 'LCHO' THEN 2
                ELSE 3
            END
        LIMIT 1
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).fetchone()
            return result[0] if result else None
        except Exception as e:
            self._log_error(f"Error fetching dataset type: {str(e)}")
            return None
            
    def get_provider_percentiles(self, provider_code: str) -> pd.DataFrame:
        """
        Get pre-calculated percentile ranks for a specific provider
        Within their appropriate peer group (LCRA or LCHO)
        """
        if not self._connection:
            return pd.DataFrame()
            
        # First get the provider's dataset type
        dataset_type = self.get_provider_dataset_type(provider_code)
        if not dataset_type:
            self._log_error(f"Could not determine dataset type for provider {provider_code}")
            return pd.DataFrame()
            
        query = """
        SELECT 
            tp_measure, 
            percentile_rank,
            peer_group_size,
            dataset_type
        FROM calculated_percentiles 
        WHERE provider_code = ?
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).df()
            return result
        except Exception as e:
            self._log_error(f"Error fetching percentiles: {str(e)}")
            return pd.DataFrame()
            
    def get_dataset_correlations(self, dataset_type: str) -> pd.DataFrame:
        """
        Get correlations for a specific dataset type
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        SELECT 
            tp_measure,
            correlation_with_tp01,
            p_value,
            sample_size
        FROM calculated_correlations
        WHERE dataset_type = ?
        ORDER BY ABS(correlation_with_tp01) DESC
        """
        
        try:
            result = self._connection.execute(query, [dataset_type]).df()
            return result
        except Exception as e:
            self._log_error(f"Error fetching correlations: {str(e)}")
            return pd.DataFrame()
            
    def get_provider_exists(self, provider_code: str) -> bool:
        """Check if a provider exists in the database"""
        if not self._connection:
            return False
            
        query = "SELECT COUNT(*) FROM provider_dataset_mapping WHERE provider_code = ?"
        
        try:
            result = self._connection.execute(query, [provider_code]).fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            self._log_error(f"Error checking provider existence: {str(e)}")
            return False
            
    def get_all_provider_codes(self) -> List[Dict[str, str]]:
        """Get all unique provider codes and names with dataset info"""
        if not self._connection:
            return []
            
        query = """
        SELECT DISTINCT 
            provider_code,
            provider_name,
            dataset_type,
            provider_type
        FROM provider_dataset_mapping
        ORDER BY provider_name
        """
        
        try:
            result = self._connection.execute(query).df()
            if not result.empty:
                return result.to_dict('records')
            return []
        except Exception as e:
            self._log_error(f"Error fetching provider codes: {str(e)}")
            return []
            
    def get_provider_options(self) -> List[str]:
        """
        Get list of provider names for dropdown options
        Includes all providers from both LCRA and LCHO datasets
        """
        providers = self.get_all_provider_codes()
        
        options = []
        for provider in providers:
            name = provider.get('provider_name', 'Unknown')
            code = provider.get('provider_code', '')
            dataset = provider.get('dataset_type', '')
            # Format: "Provider Name (CODE)" - dataset type is hidden from user
            if name and name.strip():
                options.append(f"{name.strip()} ({code})")
            else:
                options.append(f"Provider {code}")
        
        return options
        
    def get_provider_scores(self, provider_code: str) -> pd.DataFrame:
        """
        Get raw scores for a specific provider
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        SELECT 
            tp_measure,
            score,
            dataset_type
        FROM raw_scores
        WHERE provider_code = ?
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).df()
            return result
        except Exception as e:
            self._log_error(f"Error fetching provider scores: {str(e)}")
            return pd.DataFrame()
            
    def get_peer_comparison_data(self, provider_code: str, tp_measure: str) -> pd.DataFrame:
        """
        Get comparison data for a specific measure within the same dataset
        """
        # Get provider's dataset type
        dataset_type = self.get_provider_dataset_type(provider_code)
        if not dataset_type:
            return pd.DataFrame()
            
        query = """
        SELECT 
            rs.provider_code,
            rs.provider_name,
            rs.score,
            cp.percentile_rank,
            rs.dataset_type
        FROM raw_scores rs
        JOIN calculated_percentiles cp
            ON rs.provider_code = cp.provider_code 
            AND rs.tp_measure = cp.tp_measure
        WHERE rs.tp_measure = ?
            AND rs.dataset_type = ?
        ORDER BY rs.score DESC
        """
        
        try:
            result = self._connection.execute(query, [tp_measure, dataset_type]).df()
            return result
        except Exception as e:
            self._log_error(f"Error fetching peer comparison data: {str(e)}")
            return pd.DataFrame()
            
    def get_dataset_summary_stats(self, dataset_type: str) -> Dict:
        """
        Get summary statistics for a specific dataset
        """
        if not self._connection:
            return {}
            
        query = """
        SELECT 
            COUNT(DISTINCT provider_code) as provider_count,
            COUNT(DISTINCT tp_measure) as measure_count,
            AVG(score) as avg_score
        FROM raw_scores
        WHERE dataset_type = ?
        """
        
        try:
            result = self._connection.execute(query, [dataset_type]).fetchone()
            if result:
                return {
                    'provider_count': result[0],
                    'measure_count': result[1],
                    'avg_score': result[2]
                }
            return {}
        except Exception as e:
            self._log_error(f"Error fetching summary stats: {str(e)}")
            return {}
            
    def get_measure_distribution(self, tp_measure: str, dataset_type: str) -> pd.DataFrame:
        """
        Get the distribution of scores for a specific measure within a dataset
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        SELECT 
            score,
            COUNT(*) as count
        FROM raw_scores
        WHERE tp_measure = ?
            AND dataset_type = ?
            AND score IS NOT NULL
        GROUP BY score
        ORDER BY score
        """
        
        try:
            result = self._connection.execute(query, [tp_measure, dataset_type]).df()
            return result
        except Exception as e:
            self._log_error(f"Error fetching measure distribution: {str(e)}")
            return pd.DataFrame()
            
    def get_all_providers_with_scores(self) -> pd.DataFrame:
        """
        Get all providers with their scores in wide format
        Needed for TSMAnalytics rankings calculation
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        PIVOT raw_scores 
        ON tp_measure 
        USING first(score) 
        GROUP BY provider_code, provider_name
        """
        
        try:
            df = self._connection.execute(query).df()
            # Ensure it's a DataFrame
            if not isinstance(df, pd.DataFrame):
                return pd.DataFrame()
            return df
        except Exception as e:
            self._log_error(f"Error fetching all providers: {str(e)}")
            return pd.DataFrame()
            
    def get_applicable_measures(self, dataset_type: str) -> List[str]:
        """
        Get the list of applicable TP measures for a dataset type
        LCHO doesn't have TP02-TP04 (repairs metrics)
        """
        if dataset_type == 'LCHO':
            return [tp for tp in self.tp_codes if tp not in ['TP02', 'TP03', 'TP04']]
        else:
            return self.tp_codes
            
    def load_default_data(self, provider_code: Optional[str] = None, provider_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load data for a specific provider with automatic dataset detection
        Now uses provider_name to determine dataset type when available
        """
        if not provider_code:
            return None
            
        # Get provider's dataset type (use provider_name if available)
        dataset_type = self.get_provider_dataset_type(provider_code, provider_name)
        if not dataset_type:
            self._log_error(f"Provider {provider_code} not found in database")
            return None
            
        # Get provider summary data for the specific dataset
        query = """
        SELECT *
        FROM provider_summary
        WHERE provider_code = ? AND dataset_type = ?
        """
        
        try:
            result = self._connection.execute(query, [provider_code, dataset_type]).df()
            if not result.empty:
                # Add metadata
                result['loaded_dataset'] = dataset_type
                result['applicable_measures'] = [self.get_applicable_measures(dataset_type)]
                
                # Log dataset info
                if not self.silent_mode:
                    st.info(f"📊 Loaded {dataset_type} data for provider {provider_code}")
                    if dataset_type == 'LCHO':
                        st.info("ℹ️ Note: Repairs metrics (TP02-TP04) are not applicable for LCHO providers")
                
                return result
            return None
        except Exception as e:
            self._log_error(f"Error loading provider data: {str(e)}")
            return None
            
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None