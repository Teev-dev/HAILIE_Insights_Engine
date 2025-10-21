"""
Refactored Data Processor for DuckDB-based Analytics
Reads pre-calculated analytics from DuckDB instead of processing Excel files
"""

import pandas as pd
import duckdb
import streamlit as st
from typing import Dict, List, Optional
import os
from error_handler import ErrorHandler


class TSMDataProcessor:
    """
    Handles data retrieval from pre-calculated DuckDB analytics database
    """
    
    def __init__(self, silent_mode=False):
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]  # TP01 to TP12
        self.db_path = "attached_assets/hailie_analytics.duckdb"
        self.silent_mode = silent_mode
        self._connection = None
        self._connect_to_db()
        
    def _connect_to_db(self):
        """Establish connection to DuckDB database"""
        if not os.path.exists(self.db_path):
            if not self.silent_mode:
                st.error("❌ Analytics database not found. Please ensure data is properly loaded.")
            return None
        
        try:
            self._connection = duckdb.connect(self.db_path, read_only=True)
            if not self.silent_mode:
                st.success("✅ Connected to analytics database")
        except Exception as e:
            if not self.silent_mode:
                st.error(ErrorHandler.handle_database_error(e))
            self._connection = None
            
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
        
    def get_provider_percentiles(self, provider_code: str) -> pd.DataFrame:
        """
        Get pre-calculated percentile ranks for a specific provider
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        SELECT tp_measure, percentile_rank 
        FROM calculated_percentiles 
        WHERE provider_code = ?
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).df()
            return result
        except Exception as e:
            self._log_error(ErrorHandler.handle_database_error(e))
            return pd.DataFrame()
            
    def get_all_correlations(self) -> pd.DataFrame:
        """
        Get all pre-calculated correlations with TP01
        """
        if not self._connection:
            return pd.DataFrame()
            
        query = """
        SELECT tp_measure, correlation_with_tp01, p_value
        FROM calculated_correlations
        """
        
        try:
            result = self._connection.execute(query).df()
            return result
        except Exception as e:
            self._log_error(ErrorHandler.handle_database_error(e))
            return pd.DataFrame()
            
    def get_provider_exists(self, provider_code: str) -> bool:
        """
        Check if a provider exists in the database
        """
        if not self._connection:
            return False
            
        query = """
        SELECT 1 FROM raw_scores 
        WHERE provider_code = ? 
        LIMIT 1
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).fetchone()
            return result is not None
        except Exception as e:
            self._log_error(ErrorHandler.handle_provider_error(e))
            return False
            
    def get_all_provider_codes(self) -> List[Dict[str, str]]:
        """
        Get all unique provider codes and names from the database
        """
        if not self._connection:
            return []
            
        query = """
        SELECT DISTINCT provider_code, provider_name 
        FROM raw_scores
        ORDER BY provider_name
        """
        
        try:
            result = self._connection.execute(query).df()
            return result.to_dict('records')
        except Exception as e:
            self._log_error(ErrorHandler.handle_database_error(e))
            return []
            
    def get_provider_scores(self, provider_code: str) -> Dict[str, float]:
        """
        Get all scores for a specific provider
        """
        if not self._connection:
            return {}
            
        query = """
        SELECT tp_measure, score 
        FROM raw_scores 
        WHERE provider_code = ?
        """
        
        try:
            result = self._connection.execute(query, [provider_code]).df()
            return dict(zip(result['tp_measure'], result['score']))
        except Exception as e:
            self._log_error(ErrorHandler.handle_database_error(e))
            return {}
            
    def get_all_providers_with_scores(self) -> pd.DataFrame:
        """
        Get all providers with their scores in wide format
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
            self._log_error(ErrorHandler.handle_database_error(e))
            return pd.DataFrame()
            
    def get_provider_options(self) -> List[str]:
        """
        Get list of provider names for dropdown options
        """
        providers = self.get_all_provider_codes()
        
        options = []
        for provider in providers:
            name = provider.get('provider_name', 'Unknown')
            code = provider.get('provider_code', '')
            # Format: "Provider Name (CODE)"
            if name and name.strip():
                options.append(f"{name.strip()} ({code})")
            else:
                options.append(f"Provider {code}")
        
        return options
        
    def get_measure_statistics(self, tp_measure: str) -> Dict:
        """
        Get statistics for a specific measure across all providers
        """
        if not self._connection:
            return {}
            
        query = """
        SELECT 
            avg(score) as mean_score,
            median(score) as median_score,
            min(score) as min_score,
            max(score) as max_score,
            stddev(score) as std_dev,
            count(*) as provider_count
        FROM raw_scores
        WHERE tp_measure = ?
        """
        
        try:
            result = self._connection.execute(query, [tp_measure]).df()
            if not result.empty:
                return result.iloc[0].to_dict()
            return {}
        except Exception as e:
            self._log_error(ErrorHandler.handle_database_error(e))
            return {}
            
    def get_percentile_for_score(self, tp_measure: str, score: float) -> float:
        """
        Get percentile rank for a specific score in a measure
        """
        if not self._connection:
            return 0.0
            
        query = """
        WITH scores_cte AS (
            SELECT score FROM raw_scores WHERE tp_measure = ?
        )
        SELECT 
            (SELECT COUNT(*) FROM scores_cte WHERE score <= ?) * 100.0 / 
            (SELECT COUNT(*) FROM scores_cte) as percentile
        """
        
        try:
            result = self._connection.execute(query, [tp_measure, score]).fetchone()
            if result:
                return result[0]
            return 0.0
        except Exception as e:
            self._log_error(ErrorHandler.handle_calculation_error(e))
            return 0.0
            
    def load_default_data(self, provider_code: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Load data from DuckDB in the format expected by legacy code
        This method maintains backward compatibility
        """
        if not self._connection:
            return None
            
        df = self.get_all_providers_with_scores()
        
        if provider_code and not df.empty:
            # Filter to specific provider if requested
            df = df[df['provider_code'] == provider_code]
            
        return df
        
    def close(self):
        """Close the database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            
    def __del__(self):
        """Cleanup connection on deletion"""
        self.close()