import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.stats import pearsonr

class TSMAnalytics:
    """
    Handles analytics calculations for TSM data including rankings, momentum, and priorities
    """
    
    def __init__(self):
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
        Calculate provider rankings with quartile-based scoring
        """
        try:
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            
            if not tp_cols:
                return {"error": "No TP measures found for ranking calculation"}
            
            # Apply peer group filtering
            filtered_df = self._apply_peer_group_filter(df, peer_group_filter)
            
            # Calculate composite score for each provider
            provider_scores = {}
            
            for _, row in filtered_df.iterrows():
                provider_code = row['provider_code']
                tp_values = []
                
                for tp_col in tp_cols:
                    if pd.notna(row[tp_col]) == True:
                        tp_values.append(float(row[tp_col]))
                
                if tp_values:
                    # Calculate weighted average (equal weights for now)
                    composite_score = np.mean(tp_values)
                    provider_scores[provider_code] = {
                        'score': composite_score,
                        'measures_count': len(tp_values),
                        'individual_scores': {tp_cols[i]: tp_values[i] for i in range(len(tp_values)) if i < len(tp_cols)}
                    }
            
            # Calculate rankings and quartiles
            scores_list = [(provider, data['score']) for provider, data in provider_scores.items()]
            scores_list.sort(key=lambda x: x[1], reverse=True)  # Higher scores = better ranking
            
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
                    'total_providers': total_providers,
                    'score': score,
                    'percentile': percentile,
                    'quartile': quartile,
                    'quartile_color': quartile_color,
                    'measures_count': provider_scores[provider]['measures_count'],
                    'individual_scores': provider_scores[provider]['individual_scores']
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
        Identify highest-priority improvement area through comprehensive correlation analysis with TP01
        """
        try:
            if provider_code not in df['provider_code'].values:
                return {"error": f"Provider {provider_code} not found"}
            
            provider_row = df[df['provider_code'] == provider_code].iloc[0]
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            
            # Calculate correlations between all measures and TP01 across all providers
            correlations_with_tp01 = {}
            provider_scores = {}
            
            # Get provider's scores
            for tp_col in tp_cols:
                if pd.notna(provider_row[tp_col]):
                    provider_scores[tp_col] = float(provider_row[tp_col])
            
            if not provider_scores:
                return {"error": "No valid scores found for priority analysis"}
            
            # Calculate correlations of each measure with TP01 (overall satisfaction)
            if 'TP01' in df.columns:
                tp01_scores = df['TP01'].dropna()
                
                for tp_col in tp_cols:
                    if tp_col != 'TP01' and tp_col in df.columns:
                        measure_scores = df[tp_col].dropna()
                        
                        # Get common indices for correlation
                        common_indices = tp01_scores.index.intersection(measure_scores.index)
                        
                        if len(common_indices) > 5:  # Need sufficient data for correlation
                            try:
                                corr_coef, p_value = pearsonr(
                                    tp01_scores.loc[common_indices],
                                    measure_scores.loc[common_indices]
                                )
                                correlations_with_tp01[tp_col] = {
                                    'correlation': corr_coef,
                                    'p_value': p_value,
                                    'strength': abs(corr_coef),
                                    'sample_size': len(common_indices)
                                }
                            except:
                                correlations_with_tp01[tp_col] = {
                                    'correlation': 0,
                                    'p_value': 1,
                                    'strength': 0,
                                    'sample_size': len(common_indices)
                                }
            
            # Calculate peer percentiles and improvement potential for each measure
            peer_percentiles = {}
            improvement_potential = {}
            weighted_priorities = {}  # Combined score of improvement potential * correlation strength
            
            for tp_col in tp_cols:
                if tp_col == 'TP01': 
                    continue  # skip TP01 (overall satisfaction) to avoid self-correlation
                if tp_col in provider_scores:
                    # Get all valid scores for this measure
                    all_scores = df[tp_col].dropna()
                    
                    if len(all_scores) > 1:
                        provider_score = provider_scores[tp_col]
                        
                        # Calculate percentile
                        percentile = stats.percentileofscore(all_scores, provider_score)
                        peer_percentiles[tp_col] = percentile
                        
                        # Calculate improvement potential (inverse of percentile)
                        improvement_potential[tp_col] = 100 - percentile
                        
                        # Calculate weighted priority (improvement potential * correlation with TP01)
                        if tp_col in correlations_with_tp01:
                            correlation_weight = correlations_with_tp01[tp_col]['strength']
                        else:
                            correlation_weight = 0.5  # Default moderate correlation if not available
                        
                        # Weighted priority considers both improvement potential and correlation with overall satisfaction
                        weighted_priorities[tp_col] = improvement_potential[tp_col] * (0.5 + 0.5 * correlation_weight)
            
            # Find the measure with highest weighted priority
            if weighted_priorities:
                # Sort measures by weighted priority
                sorted_priorities = sorted(weighted_priorities.items(), key=lambda x: x[1], reverse=True)
                priority_measure = sorted_priorities[0][0]
                priority_potential = improvement_potential[priority_measure]
                
                # Get correlation info for the priority measure
                correlation_info = correlations_with_tp01.get(priority_measure, {
                    'correlation': 0,
                    'strength': 0,
                    'p_value': 1
                })
                
                # Determine priority level based on weighted priority score
                weighted_score = weighted_priorities[priority_measure]
                if weighted_score > 60:
                    priority_level = "Critical"
                    priority_color = "#EF4444"
                elif weighted_score > 40:
                    priority_level = "High"
                    priority_color = "#F59E0B"
                elif weighted_score > 20:
                    priority_level = "Medium"
                    priority_color = "#84CC16"
                else:
                    priority_level = "Low"
                    priority_color = "#22C55E"
                
                # Build comprehensive priority analysis
                return {
                    'measure': priority_measure,
                    'measure_name': self.tp_descriptions.get(priority_measure, priority_measure),
                    'improvement_potential': priority_potential,
                    'current_percentile': peer_percentiles.get(priority_measure, 50),
                    'current_score': provider_scores[priority_measure],
                    'priority_level': priority_level,
                    'priority_color': priority_color,
                    'correlation_with_tp01': correlation_info.get('correlation', 0),
                    'correlation_strength': correlation_info.get('strength', 0) * 100,
                    'correlation_p_value': correlation_info.get('p_value', 1),
                    'weighted_priority_score': weighted_score,
                    'all_potentials': improvement_potential,
                    'all_correlations': correlations_with_tp01,
                    'all_weighted_priorities': weighted_priorities,
                    'top_3_priorities': [
                        {
                            'measure': m,
                            'name': self.tp_descriptions.get(m, m),
                            'weighted_score': s,
                            'improvement_potential': improvement_potential.get(m, 0),
                            'correlation': correlations_with_tp01.get(m, {}).get('correlation', 0)
                        }
                        for m, s in sorted_priorities[:3]
                    ]
                }
            else:
                return {"error": "Could not calculate improvement priorities"}
                
        except Exception as e:
            return {"error": f"Error identifying priority: {str(e)}"}
    
    def _apply_peer_group_filter(self, df: pd.DataFrame, filter_type: str) -> pd.DataFrame:
        """
        Apply peer group filtering (placeholder implementation)
        """
        # For now, return all providers
        # In a real implementation, this would filter by size, region, type, etc.
        return df
    
    def get_detailed_performance_analysis(self, df: pd.DataFrame, provider_code: str) -> Dict:
        """
        Get detailed performance analysis for all measures
        """
        try:
            if provider_code not in df['provider_code'].values:
                return {"error": f"Provider {provider_code} not found"}
            
            provider_row = df[df['provider_code'] == provider_code].iloc[0]
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            
            detailed_analysis = {}
            
            for tp_col in tp_cols:
                if pd.notna(provider_row[tp_col]):
                    provider_score = float(provider_row[tp_col])
                    
                    # Get all valid scores for this measure
                    all_scores = df[tp_col].dropna()
                    
                    if len(all_scores) > 1:
                        percentile = stats.percentileofscore(all_scores, provider_score)
                        
                        detailed_analysis[tp_col] = {
                            'score': provider_score,
                            'percentile': percentile,
                            'description': self.tp_descriptions.get(tp_col, tp_col),
                            'peer_avg': all_scores.mean(),
                            'peer_median': all_scores.median(),
                            'top_quartile_threshold': all_scores.quantile(0.75),
                            'bottom_quartile_threshold': all_scores.quantile(0.25)
                        }
            
            return detailed_analysis
            
        except Exception as e:
            return {"error": f"Error in detailed analysis: {str(e)}"}
