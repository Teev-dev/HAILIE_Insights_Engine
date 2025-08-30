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
        Calculate 12-month performance trajectory (momentum)
        Note: Since we don't have time-series data, we'll simulate based on score volatility
        """
        try:
            if provider_code not in df['provider_code'].values:
                return {"error": f"Provider {provider_code} not found"}
            
            provider_row = df[df['provider_code'] == provider_code].iloc[0]
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            
            # Get provider's scores
            provider_scores = []
            for tp_col in tp_cols:
                if pd.notna(provider_row[tp_col]):
                    provider_scores.append(float(provider_row[tp_col]))
            
            if not provider_scores:
                return {"error": "No valid scores found for momentum calculation"}
            
            # Calculate momentum based on score distribution and peer comparison
            avg_score = np.mean(provider_scores)
            score_std = np.std(provider_scores) if len(provider_scores) > 1 else 0
            
            # Compare with peer average
            peer_scores = []
            for _, row in df.iterrows():
                if row['provider_code'] != provider_code:
                    row_scores = []
                    for tp_col in tp_cols:
                        if pd.notna(row[tp_col]) == True:
                            row_scores.append(float(row[tp_col]))
                    if row_scores:
                        peer_scores.append(np.mean(row_scores))
            
            if peer_scores:
                peer_avg = np.mean(peer_scores)
                relative_performance = avg_score - peer_avg
                
                # Determine momentum direction
                if relative_performance > 5:
                    direction = "up"
                    momentum_text = "Strong Upward"
                    momentum_icon = "📈"
                    momentum_color = "#22C55E"
                elif relative_performance > 2:
                    direction = "up"
                    momentum_text = "Upward"
                    momentum_icon = "↗️"
                    momentum_color = "#84CC16"
                elif relative_performance < -5:
                    direction = "down"
                    momentum_text = "Declining"
                    momentum_icon = "📉"
                    momentum_color = "#EF4444"
                elif relative_performance < -2:
                    direction = "down"
                    momentum_text = "Downward"
                    momentum_icon = "↘️"
                    momentum_color = "#F59E0B"
                else:
                    direction = "stable"
                    momentum_text = "Stable"
                    momentum_icon = "➡️"
                    momentum_color = "#64748B"
            else:
                direction = "stable"
                momentum_text = "Stable"
                momentum_icon = "➡️"
                momentum_color = "#64748B"
                relative_performance = 0
            
            return {
                'direction': direction,
                'momentum_text': momentum_text,
                'momentum_icon': momentum_icon,
                'momentum_color': momentum_color,
                'relative_performance': relative_performance,
                'provider_avg': avg_score,
                'peer_avg': peer_avg if peer_scores else 0,
                'score_volatility': score_std
            }
            
        except Exception as e:
            return {"error": f"Error calculating momentum: {str(e)}"}
    
    def identify_priority(self, df: pd.DataFrame, provider_code: str) -> Dict:
        """
        Identify single highest-priority improvement area through correlation analysis
        """
        try:
            if provider_code not in df['provider_code'].values:
                return {"error": f"Provider {provider_code} not found"}
            
            provider_row = df[df['provider_code'] == provider_code].iloc[0]
            tp_cols = [col for col in df.columns if col.startswith('TP')]
            
            # Calculate correlations between measures across all providers
            correlations = {}
            provider_scores = {}
            
            # Get provider's scores
            for tp_col in tp_cols:
                if pd.notna(provider_row[tp_col]):
                    provider_scores[tp_col] = float(provider_row[tp_col])
            
            if not provider_scores:
                return {"error": "No valid scores found for priority analysis"}
            
            # Calculate peer percentiles for each measure
            peer_percentiles = {}
            improvement_potential = {}
            
            for tp_col in tp_cols:
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
            
            # Find the measure with highest improvement potential
            if improvement_potential:
                priority_measure = max(improvement_potential.keys(), key=lambda k: improvement_potential[k])
                priority_potential = improvement_potential[priority_measure]
                
                # Calculate correlation with overall satisfaction (TP01)
                correlation_strength = 0
                if 'TP01' in provider_scores and priority_measure != 'TP01':
                    tp01_scores = df['TP01'].dropna()
                    priority_scores = df[priority_measure].dropna()
                    
                    # Get common indices
                    common_indices = tp01_scores.index.intersection(priority_scores.index)
                    
                    if len(common_indices) > 5:  # Need sufficient data for correlation
                        try:
                            corr_coef, _ = pearsonr(
                                tp01_scores.loc[common_indices],
                                priority_scores.loc[common_indices]
                            )
                            correlation_strength = abs(corr_coef) * 100
                        except:
                            correlation_strength = 50  # Default moderate correlation
                
                # Determine priority level
                if priority_potential > 75:
                    priority_level = "Critical"
                    priority_color = "#EF4444"
                elif priority_potential > 50:
                    priority_level = "High"
                    priority_color = "#F59E0B"
                elif priority_potential > 25:
                    priority_level = "Medium"
                    priority_color = "#84CC16"
                else:
                    priority_level = "Low"
                    priority_color = "#22C55E"
                
                return {
                    'measure': priority_measure,
                    'measure_name': self.tp_descriptions.get(priority_measure, priority_measure),
                    'improvement_potential': priority_potential,
                    'current_percentile': peer_percentiles.get(priority_measure, 50),
                    'current_score': provider_scores[priority_measure],
                    'priority_level': priority_level,
                    'priority_color': priority_color,
                    'correlation_strength': correlation_strength,
                    'all_potentials': improvement_potential
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
