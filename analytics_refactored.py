"""
Refactored Analytics Module for Pre-calculated DuckDB Data
Uses pre-calculated analytics from DuckDB instead of on-the-fly calculations
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional


class TSMAnalytics:
    """
    Handles analytics retrieval from pre-calculated DuckDB analytics
    """
    
    def __init__(self, data_processor):
        self.data_processor = data_processor  # Instance of refactored TSMDataProcessor
        self.tp_codes = [f"TP{i:02d}" for i in range(1, 13)]
        self.tp_descriptions = {
            'TP01': 'Overall satisfaction',
            'TP02': 'Satisfaction with repairs',
            'TP03': 'Time taken to complete most recent repair',
            'TP04': 'Satisfaction with time taken to complete most recent repair',
            'TP05': 'Satisfaction that home is well-maintained',
            'TP06': 'Satisfaction that home is safe',
            'TP07': 'Satisfaction with neighbourhood',
            'TP08': 'Satisfaction with landlord\'s contribution to neighbourhood',
            'TP09': 'Satisfaction with approach to handling of complaints',
            'TP10': 'Agreement that landlord treats residents fairly',
            'TP11': 'Agreement that landlord listens to residents\' views',
            'TP12': 'Satisfaction with landlord\'s approach to handling of anti-social behaviour'
        }
    
    def calculate_rankings(self, df: pd.DataFrame, peer_group_filter: str = "All Providers") -> Dict:
        """
        Calculate provider rankings using pre-calculated percentiles
        Note: df parameter maintained for backward compatibility but not used
        """
        try:
            # Get all providers with their scores
            all_providers_df = self.data_processor.get_all_providers_with_scores()
            
            if all_providers_df.empty:
                return {"error": "No provider data available"}
            
            # Apply peer group filtering (simplified for MVP)
            filtered_df = self._apply_peer_group_filter(all_providers_df, peer_group_filter)
            
            # Calculate composite scores from the pre-calculated data
            provider_scores = {}
            
            for _, row in filtered_df.iterrows():
                provider_code = row['provider_code']
                tp_values = []
                
                for tp_col in self.tp_codes:
                    if tp_col in row:
                        value = row[tp_col]
                        if pd.notna(value) and value is not None:
                            tp_values.append(float(value))
                
                if tp_values:
                    composite_score = np.mean(tp_values)
                    provider_scores[provider_code] = {
                        'score': composite_score,
                        'measures_count': len(tp_values),
                        'individual_scores': {self.tp_codes[i]: tp_values[i] 
                                            for i in range(len(tp_values)) 
                                            if i < len(self.tp_codes) and i < len(tp_values)}
                    }
            
            # Sort and rank providers
            scores_list = [(provider, data['score']) for provider, data in provider_scores.items()]
            scores_list.sort(key=lambda x: x[1], reverse=True)
            
            total_providers = len(scores_list)
            
            rankings = {}
            for i, (provider, score) in enumerate(scores_list):
                rank = i + 1
                percentile = (total_providers - rank) / total_providers * 100
                
                # Determine quartile
                if percentile >= 75:
                    quartile = "Top"
                    quartile_color = "#22C55E"
                elif percentile >= 50:
                    quartile = "High"
                    quartile_color = "#84CC16"
                elif percentile >= 25:
                    quartile = "Mid"
                    quartile_color = "#F59E0B"
                else:
                    quartile = "Low"
                    quartile_color = "#EF4444"
                
                rankings[provider] = {
                    'rank': rank,
                    'score': score,
                    'percentile': percentile,
                    'quartile': quartile,
                    'quartile_color': quartile_color,
                    'total_providers': total_providers,
                    'measures_count': provider_scores[provider]['measures_count']
                }
            
            return rankings
            
        except Exception as e:
            return {"error": f"Error calculating rankings: {str(e)}"}
    
    def calculate_momentum(self, df: pd.DataFrame, provider_code: str) -> Dict:
        """
        Momentum feature disabled - requires multi-year data
        """
        return {
            'direction': "disabled",
            'momentum_text': "Coming in 2026",
            'momentum_icon': "⏳",
            'momentum_color': "#64748B",
            'relative_performance': 0,
            'provider_avg': 0,
            'peer_avg': 0,
            'score_volatility': 0,
            'disabled': True
        }
    
    def identify_priority(self, df: pd.DataFrame, provider_code: str) -> Dict:
        """
        Identify highest-priority improvement area using pre-calculated correlations and percentiles
        """
        try:
            # Check if provider exists
            if not self.data_processor.get_provider_exists(provider_code):
                return {"error": f"Provider {provider_code} not found"}
            
            # Get provider's scores and percentiles
            provider_scores_df = self.data_processor.get_provider_scores(provider_code)
            provider_percentiles = self.data_processor.get_provider_percentiles(provider_code)
            
            if provider_scores_df.empty:
                return {"error": "No scores found for priority analysis"}
            
            # Convert scores DataFrame to dict for easier access
            provider_scores = dict(zip(provider_scores_df['tp_measure'], provider_scores_df['score']))
            
            # Convert percentiles DataFrame to dict for easier access
            percentile_dict = {}
            if not provider_percentiles.empty:
                percentile_dict = dict(zip(provider_percentiles['tp_measure'], 
                                          provider_percentiles['percentile_rank']))
            
            # Get dataset type for the provider
            dataset_type = self.data_processor.get_provider_dataset_type(provider_code)
            if not dataset_type:
                dataset_type = 'LCRA'  # Default fallback
            
            # Get pre-calculated correlations with TP01 for the specific dataset
            correlations_df = self.data_processor.get_dataset_correlations(dataset_type)
            correlation_dict = {}
            if not correlations_df.empty:
                correlation_dict = dict(zip(correlations_df['tp_measure'], 
                                           correlations_df['correlation_with_tp01']))
            
            # Calculate priority for each measure
            priority_scores = {}
            
            for tp_measure in self.tp_codes[1:]:  # Skip TP01
                if tp_measure not in provider_scores:
                    continue
                    
                # Get percentile (or calculate if not available)
                if tp_measure in percentile_dict:
                    percentile = percentile_dict[tp_measure]
                else:
                    # Fallback: calculate percentile on the fly
                    score = provider_scores[tp_measure]
                    percentile = self.data_processor.get_percentile_for_score(tp_measure, score)
                
                # Improvement potential (lower percentile = more room for improvement)
                improvement_potential = 100 - percentile
                
                # Get correlation strength
                correlation = correlation_dict.get(tp_measure, 0)
                correlation_strength = abs(correlation)
                
                # Calculate weighted priority score
                # Higher priority = high improvement potential + high correlation with TP01
                priority_score = (improvement_potential * 0.6) + (correlation_strength * 100 * 0.4)
                
                priority_scores[tp_measure] = {
                    'measure': tp_measure,
                    'description': self.tp_descriptions.get(tp_measure, tp_measure),
                    'current_score': provider_scores[tp_measure],
                    'percentile': percentile,
                    'improvement_potential': improvement_potential,
                    'correlation': correlation,
                    'correlation_strength': correlation_strength,
                    'priority_score': priority_score
                }
            
            if not priority_scores:
                return {"error": "No measures available for priority analysis"}
            
            # Find highest priority measure
            highest_priority = max(priority_scores.values(), key=lambda x: x['priority_score'])
            
            # Determine priority level
            if highest_priority['priority_score'] > 70:
                priority_level = "Critical"
                priority_color = "#EF4444"
            elif highest_priority['priority_score'] > 50:
                priority_level = "High"
                priority_color = "#F59E0B"
            elif highest_priority['priority_score'] > 30:
                priority_level = "Medium"
                priority_color = "#EAB308"
            else:
                priority_level = "Low"
                priority_color = "#22C55E"
            
            return {
                'priority_measure': highest_priority['measure'],
                'priority_description': highest_priority['description'],
                'priority_level': priority_level,
                'priority_color': priority_color,
                'current_score': highest_priority['current_score'],
                'percentile': highest_priority['percentile'],
                'improvement_potential': highest_priority['improvement_potential'],
                'correlation_with_tp01': highest_priority['correlation'],
                'priority_score': highest_priority['priority_score'],
                'all_priorities': priority_scores
            }
            
        except Exception as e:
            return {"error": f"Error in priority identification: {str(e)}"}
    
    def _apply_peer_group_filter(self, df: pd.DataFrame, peer_group_filter: str) -> pd.DataFrame:
        """
        Apply peer group filtering (simplified for MVP)
        """
        # For MVP, we're not implementing complex peer group filtering
        # This would require additional metadata about providers
        return df
    
    def get_detailed_performance_analysis(self, df: pd.DataFrame, provider_code: str) -> Dict:
        """
        Get detailed performance analysis using pre-calculated percentiles
        """
        try:
            # Check if provider exists
            if not self.data_processor.get_provider_exists(provider_code):
                return {"error": f"Provider {provider_code} not found"}
            
            # Get provider's scores and percentiles
            provider_scores = self.data_processor.get_provider_scores(provider_code)
            provider_percentiles = self.data_processor.get_provider_percentiles(provider_code)
            
            # Convert percentiles DataFrame to dict
            percentile_dict = {}
            if not provider_percentiles.empty:
                percentile_dict = dict(zip(provider_percentiles['tp_measure'], 
                                          provider_percentiles['percentile_rank']))
            
            detailed_analysis = {}
            
            for tp_measure in self.tp_codes:
                if tp_measure not in provider_scores:
                    continue
                    
                score = provider_scores[tp_measure]
                
                # Get percentile from pre-calculated data
                percentile = percentile_dict.get(tp_measure, 0)
                
                # Get measure statistics
                stats = self.data_processor.get_measure_statistics(tp_measure)
                
                detailed_analysis[tp_measure] = {
                    'score': score,
                    'percentile': percentile,
                    'description': self.tp_descriptions.get(tp_measure, tp_measure),
                    'peer_avg': stats.get('mean_score', 0),
                    'peer_median': stats.get('median_score', 0),
                    'top_quartile_threshold': stats.get('mean_score', 0) + stats.get('std_dev', 0),
                    'bottom_quartile_threshold': stats.get('mean_score', 0) - stats.get('std_dev', 0)
                }
            
            return detailed_analysis
            
        except Exception as e:
            return {"error": f"Error in detailed analysis: {str(e)}"}