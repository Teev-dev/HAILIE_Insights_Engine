# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Tom Stephenson (Teev-dev)

"""
Refactored Analytics Module for Pre-calculated DuckDB Data
Uses pre-calculated analytics from DuckDB instead of on-the-fly calculations
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional

from scipy.stats import percentileofscore

from tsm_measures import TP_CODES, TP_DESCRIPTIONS

# Smallest peer group (including the provider itself) a size/region filter may
# produce. Below this, percentiles and quartiles move too far on a single
# provider's result to support board reporting, so the filter is not applied
# and the full dataset peer group is used instead.
MIN_PEER_GROUP_SIZE = 10

# Latest year of TSM data. Used when no year is bound to TSMAnalytics, and as
# "the current year" for the multi-provider comparison. Update with the other
# year defaults at each annual refresh (see MAINTENANCE.md).
LATEST_DATA_YEAR = 2026

# Multi-provider (group) view limits.
MIN_COMPARE_PROVIDERS = 2
MAX_COMPARE_PROVIDERS = 3


class TSMAnalytics:
    """
    Handles analytics retrieval from pre-calculated DuckDB analytics
    """

    def __init__(self, data_processor, year: Optional[int] = None):
        """
        year binds every calculation to one year of results. Leave it unset for
        the latest year. Set it to a provider's own latest year when that
        provider is missing from the latest data, so its scores are only ever
        compared with peers, percentiles and correlations from the same year.
        """
        self.data_processor = data_processor  # Instance of refactored TSMDataProcessor
        self.year = year
        self.tp_codes = list(TP_CODES)
        self.tp_descriptions = dict(TP_DESCRIPTIONS)

    def _year_kwargs(self) -> Dict:
        """Keyword arguments that pin a data-processor call to the bound year.

        Empty when no year is bound, so the processor's own latest-year default
        applies and unbound behaviour is exactly what it was before.
        """
        return {} if self.year is None else {'year': self.year}

    def resolve_peer_group(self, provider_codes: List[str], dataset_type: str,
                           size_band: Optional[str] = None, region: Optional[str] = None) -> Dict:
        """
        Decide which peer group a size-band / region filter actually yields.

        The group is every provider in dataset_type matching the filter, plus
        the selected provider(s) themselves. If that is smaller than
        MIN_PEER_GROUP_SIZE the filter is dropped and the full dataset is used
        (fallback=True) so callers can tell the user why. The returned
        size_band / region are the ones to pass on to the other methods.
        """
        requested = {'requested_size_band': size_band, 'requested_region': region,
                     'min_peer_group_size': MIN_PEER_GROUP_SIZE}

        def group_size(band, reg):
            scores = self.data_processor.get_peer_group_scores(
                dataset_type, size_band=band, region=reg, include_provider_codes=provider_codes,
                **self._year_kwargs())
            return 0 if scores.empty else int(scores['provider_code'].nunique())

        if size_band or region:
            filtered_size = group_size(size_band, region)
            if filtered_size >= MIN_PEER_GROUP_SIZE:
                return {'size_band': size_band, 'region': region, 'is_filtered': True,
                        'fallback': False, 'peer_group_size': filtered_size, **requested}
            return {'size_band': None, 'region': None, 'is_filtered': False,
                    'fallback': True, 'filtered_group_size': filtered_size,
                    'peer_group_size': group_size(None, None), **requested}

        return {'size_band': None, 'region': None, 'is_filtered': False,
                'fallback': False, 'peer_group_size': group_size(None, None), **requested}

    def _peer_percentiles(self, provider_code: str, dataset_type: str,
                          size_band: Optional[str] = None, region: Optional[str] = None,
                          include_provider_codes: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Percentile rank per measure for a provider within its peer group.

        Unfiltered, this reads the percentiles pre-calculated by the ETL. With
        a size-band / region filter it recalculates them over the filtered
        group using the same method as the ETL (scipy percentileofscore), so
        the two agree exactly when the filter is empty.
        """
        if not size_band and not region:
            percentiles_df = self.data_processor.get_provider_percentiles(
                provider_code, dataset_type=dataset_type, **self._year_kwargs())
            if percentiles_df is None or percentiles_df.empty:
                return {}
            return dict(zip(percentiles_df['tp_measure'], percentiles_df['percentile_rank']))

        include = list(include_provider_codes or [])
        if provider_code not in include:
            include.append(provider_code)
        peer_scores = self.data_processor.get_peer_group_scores(
            dataset_type, size_band=size_band, region=region, include_provider_codes=include,
            **self._year_kwargs())
        if peer_scores is None or peer_scores.empty:
            return {}

        percentiles = {}
        for tp_measure, measure_scores in peer_scores.groupby('tp_measure'):
            own = measure_scores.loc[measure_scores['provider_code'] == provider_code, 'score']
            if own.empty:
                continue
            percentiles[tp_measure] = float(percentileofscore(measure_scores['score'].values, own.iloc[0]))
        return percentiles

    def calculate_rankings(self, df: pd.DataFrame, peer_group_filter: str = "All Providers", dataset_type: Optional[str] = None,
                           size_band: Optional[str] = None, region: Optional[str] = None,
                           include_provider_codes: Optional[List[str]] = None) -> Dict:
        """
        Calculate provider rankings using pre-calculated percentiles
        Now supports dataset-specific rankings for LCRA/LCHO isolation

        size_band / region restrict the ranking to that peer group within
        dataset_type; include_provider_codes keeps the selected provider(s) in
        the group. peer_group_filter is a legacy label and is not used.
        """
        try:
            # Get all providers with their scores, filtered by dataset and peer group
            filtered_df = self.data_processor.get_all_providers_with_scores(
                dataset_type, size_band=size_band, region=region,
                include_provider_codes=include_provider_codes, **self._year_kwargs())

            if filtered_df.empty:
                return {"error": "No provider data available"}
            
            # Calculate composite scores from the pre-calculated data
            provider_scores = {}
            
            for _, row in filtered_df.iterrows():
                provider_code = row['provider_code']
                tp_values = []
                
                for tp_col in self.tp_codes:
                    if tp_col in row.index:
                        value = row[tp_col]
                        # Use try-except to safely handle value checking and conversion
                        try:
                            # Convert to scalar if needed
                            if hasattr(value, 'item'):
                                value = value.item()
                            if value is not None and str(value) != 'nan' and str(value) != '':
                                tp_values.append(float(value))
                        except (TypeError, ValueError, AttributeError):
                            # Skip values that can't be converted
                            continue
                
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
            
            # Providers with the same average score share a rank. The providers
            # either side keep the positions they would have had anyway: two
            # providers tied at 86th are both 86th and the next is 88th. Scores
            # are compared to nine decimal places so floating-point noise in
            # the average cannot split a genuine tie.
            rankings = {}
            rank = 0
            previous_score = None
            for i, (provider, score) in enumerate(scores_list):
                tie_key = round(float(score), 9)
                if tie_key != previous_score:
                    rank = i + 1
                    previous_score = tie_key
                percentile = (total_providers - rank) / total_providers * 100
                
                # Determine quartile
                if percentile >= 75:
                    quartile = "Top"
                    quartile_color = "#1F94A3"
                elif percentile >= 50:
                    quartile = "High"
                    quartile_color = "#84CC16"
                elif percentile >= 25:
                    quartile = "Mid"
                    quartile_color = "#D8A62A"
                else:
                    quartile = "Low"
                    quartile_color = "#C85C4A"
                
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
    
    def calculate_momentum(self, df: pd.DataFrame, provider_code: str, provider_name: Optional[str] = None, dataset_type: Optional[str] = None) -> Dict:
        """
        Calculate year-over-year momentum: compare the latest year with the
        year before it. The latest year is the one bound to this instance, or
        LATEST_DATA_YEAR when none is bound.
        Identifies which measures improved/declined and overall trajectory
        """
        latest_year = self.year if self.year is not None else LATEST_DATA_YEAR
        prior_year = latest_year - 1
        try:
            if not dataset_type:
                dataset_type = self.data_processor.get_provider_dataset_type(provider_name)
            provider_prior = self.data_processor.get_provider_scores(provider_code, year=prior_year, dataset_type=dataset_type)
            provider_latest = self.data_processor.get_provider_scores(provider_code, year=latest_year, dataset_type=dataset_type)
            
            # Check if we have data for both years
            if provider_prior.empty or provider_latest.empty:
                return {
                    'direction': "insufficient_data",
                    'momentum_text': "Insufficient multi-year data",
                    'momentum_icon': "",
                    'momentum_color': "#64748B",
                    'year_over_year_change': 0,
                    'improved_measures': [],
                    'declined_measures': [],
                    'latest_year': latest_year,
                    'prior_year': prior_year,
                    'disabled': True
                }
            
            # Convert to dictionaries for easier comparison
            scores_prior = dict(zip(provider_prior['tp_measure'], provider_prior['score']))
            scores_latest = dict(zip(provider_latest['tp_measure'], provider_latest['score']))
            
            # Calculate changes for each measure
            measure_changes = {}
            for tp_measure in self.tp_codes:
                if tp_measure in scores_prior and tp_measure in scores_latest:
                    change = scores_latest[tp_measure] - scores_prior[tp_measure]
                    measure_changes[tp_measure] = {
                        'change': change,
                        'score_prior': scores_prior[tp_measure],
                        'score_latest': scores_latest[tp_measure],
                        'description': self.tp_descriptions.get(tp_measure, tp_measure)
                    }
            
            if not measure_changes:
                return {
                    'direction': "no_comparison",
                    'momentum_text': "No comparable measures",
                    'momentum_icon': "",
                    'momentum_color': "#64748B",
                    'year_over_year_change': 0,
                    'improved_measures': [],
                    'declined_measures': [],
                    'latest_year': latest_year,
                    'prior_year': prior_year,
                    'disabled': True
                }
            
            # Calculate average change
            avg_change = np.mean([m['change'] for m in measure_changes.values()])
            
            # Identify improved and declined measures (threshold: 1 point)
            improved = [(tp, data) for tp, data in measure_changes.items() if data['change'] > 1.0]
            declined = [(tp, data) for tp, data in measure_changes.items() if data['change'] < -1.0]
            
            # Sort by magnitude of change
            improved.sort(key=lambda x: x[1]['change'], reverse=True)
            declined.sort(key=lambda x: x[1]['change'])
            
            # Determine direction and messaging
            if avg_change > 0.5:
                direction = "up"
                momentum_icon = "↗️"
                momentum_color = "#1F94A3"
                momentum_text = f"Improving (+{avg_change:.1f} points avg)"
            elif avg_change < -0.5:
                direction = "down"
                momentum_icon = "↘️"
                momentum_color = "#C85C4A"
                momentum_text = f"Declining ({avg_change:.1f} points avg)"
            else:
                direction = "stable"
                momentum_icon = "→"
                momentum_color = "#D8A62A"
                momentum_text = "Stable performance"
            
            return {
                'direction': direction,
                'momentum_text': momentum_text,
                'momentum_icon': momentum_icon,
                'momentum_color': momentum_color,
                'year_over_year_change': avg_change,
                'improved_measures': [{'code': tp, 'description': data['description'], 'change': data['change']}
                                     for tp, data in improved[:3]],
                'declined_measures': [{'code': tp, 'description': data['description'], 'change': data['change']}
                                     for tp, data in declined[:3]],
                'total_measures_compared': len(measure_changes),
                'latest_year': latest_year,
                'prior_year': prior_year,
                'disabled': False
            }
            
        except Exception as e:
            return {
                'direction': "error",
                'momentum_text': f"Error: {str(e)}",
                'momentum_icon': "",
                'momentum_color': "#64748B",
                'year_over_year_change': 0,
                'improved_measures': [],
                'declined_measures': [],
                'latest_year': latest_year,
                'prior_year': prior_year,
                'disabled': True
            }
    
    def identify_priority(self, df: pd.DataFrame, provider_code: str, provider_name: Optional[str] = None, dataset_type: Optional[str] = None,
                          size_band: Optional[str] = None, region: Optional[str] = None,
                          include_provider_codes: Optional[List[str]] = None) -> Dict:
        """
        Identify highest-priority improvement area using pre-calculated correlations and percentiles

        With a size-band / region peer group, improvement potential comes from
        the provider's percentile within that group. Correlations with TP01
        always use the whole dataset: they describe what drives satisfaction
        across the sector and are too unstable to estimate on a small group.
        """
        try:
            if not self.data_processor.get_provider_exists(provider_code):
                return {"error": f"Provider {provider_code} not found"}

            if not dataset_type:
                dataset_type = self.data_processor.get_provider_dataset_type(provider_name)
            if not dataset_type:
                dataset_type = 'LCRA'  # Default fallback

            provider_scores_df = self.data_processor.get_provider_scores(
                provider_code, dataset_type=dataset_type, **self._year_kwargs())

            if provider_scores_df.empty:
                return {"error": "No scores found for priority analysis"}

            provider_scores = dict(zip(provider_scores_df['tp_measure'], provider_scores_df['score']))

            percentile_dict = self._peer_percentiles(
                provider_code, dataset_type, size_band, region, include_provider_codes)
            
            # Get pre-calculated correlations with TP01 for the specific dataset
            correlations_df = self.data_processor.get_dataset_correlations(dataset_type, **self._year_kwargs())
            correlation_dict = {}
            if not correlations_df.empty:
                correlation_dict = dict(zip(correlations_df['tp_measure'], 
                                           correlations_df['correlation_with_tp01']))
            
            # Calculate priority for each measure
            priority_scores = {}
            
            for tp_measure in self.tp_codes[1:]:  # Skip TP01
                if tp_measure not in provider_scores:
                    continue

                if tp_measure not in percentile_dict:
                    # Percentile coverage is enforced by validate_etl.py check 5.
                    # Reaching this branch means ETL drift — skip rather than invoke
                    # a nonexistent get_percentile_for_score method.
                    print(f"Skipping {tp_measure} for provider {provider_code}: no pre-calculated percentile")
                    continue

                percentile = percentile_dict[tp_measure]
                
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
                priority_color = "#C85C4A"
            elif highest_priority['priority_score'] > 50:
                priority_level = "High"
                priority_color = "#D8A62A"
            elif highest_priority['priority_score'] > 30:
                priority_level = "Medium"
                priority_color = "#E8C96B"
            else:
                priority_level = "Low"
                priority_color = "#1F94A3"
            
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
    
    def get_detailed_performance_analysis(self, df: pd.DataFrame, provider_code: str, provider_name: Optional[str] = None, dataset_type: Optional[str] = None,
                                          size_band: Optional[str] = None, region: Optional[str] = None,
                                          include_provider_codes: Optional[List[str]] = None) -> Dict:
        """
        Get detailed performance analysis using pre-calculated percentiles.

        dataset_type must be passed when the provider appears in both LCRA and
        LCHO datasets under the same provider_code (e.g. LH3827 / West Kent),
        otherwise the scores/percentiles dicts silently collapse duplicate TP
        codes and the UI renders the wrong dataset.
        """
        try:
            if not self.data_processor.get_provider_exists(provider_code):
                return {"error": f"Provider {provider_code} not found"}

            if not dataset_type:
                dataset_type = self.data_processor.get_provider_dataset_type(provider_name)
            if not dataset_type:
                return {"error": "Could not determine dataset type"}

            provider_scores_df = self.data_processor.get_provider_scores(
                provider_code, dataset_type=dataset_type, **self._year_kwargs())

            if provider_scores_df is None or provider_scores_df.empty:
                return {"error": "No scores found for this provider"}

            provider_scores = dict(zip(provider_scores_df['tp_measure'], provider_scores_df['score']))

            include = list(include_provider_codes or [])
            if provider_code not in include:
                include.append(provider_code)
            percentile_dict = self._peer_percentiles(
                provider_code, dataset_type, size_band, region, include)
            
            detailed_analysis = {}
            
            for tp_measure in self.tp_codes:
                if tp_measure not in provider_scores:
                    continue
                
                score = provider_scores[tp_measure]
                
                # Skip NaN values
                if pd.isna(score):
                    continue
                    
                # Get percentile from pre-calculated data
                percentile = percentile_dict.get(tp_measure, 0)
                
                # Get measure statistics for the same dataset type
                stats = self.data_processor.get_measure_statistics(
                    tp_measure, dataset_type, size_band=size_band, region=region,
                    include_provider_codes=include, **self._year_kwargs())
                
                if stats is None:
                    stats = {}
                
                detailed_analysis[tp_measure] = {
                    'score': score,
                    'percentile': percentile,
                    'description': self.tp_descriptions.get(tp_measure, tp_measure),
                    'peer_avg': stats.get('mean_score', 0),
                    'peer_median': stats.get('median_score', 0),
                    'top_quartile_threshold': stats.get('mean_score', 0) + stats.get('std_dev', 0),
                    'bottom_quartile_threshold': stats.get('mean_score', 0) - stats.get('std_dev', 0)
                }
            
            if not detailed_analysis:
                return {"error": "No valid performance data available"}
            
            return detailed_analysis
            
        except Exception as e:
            return {"error": f"Error in detailed analysis: {str(e)}"}

    def compare_providers(self, selections: List[Dict], size_band: Optional[str] = None,
                          region: Optional[str] = None) -> Dict:
        """
        Build a side-by-side comparison of two or three providers for group
        executives responsible for several registered providers.

        selections: dicts with provider_code, provider_name and dataset_type.
        All providers must share one dataset_type: LCRA and LCHO report
        different measures against different peer groups, so their ranks and
        percentiles are not comparable. Every provider is ranked in the same
        peer group (the dataset, or a size/region subset plus the selected
        providers), so positions can be read across the columns.

        The comparison is always of one year: the bound year, or the latest. A
        selected provider with no results for that year is not an error. It is
        listed under 'unavailable' with its own latest year and left out of
        the comparison, which is built from the remaining providers (even if
        only one). 'selection_order' keeps the order the user chose.
        """
        try:
            if len(selections) < MIN_COMPARE_PROVIDERS:
                return {"error": "too_few_providers"}
            if len(selections) > MAX_COMPARE_PROVIDERS:
                return {"error": "too_many_providers"}

            dataset_types = {sel.get('dataset_type') for sel in selections}
            if len(dataset_types) != 1 or None in dataset_types:
                return {"error": "mixed_dataset_types"}
            dataset_type = dataset_types.pop()

            selection_order = [sel['provider_code'] for sel in selections]
            if len(set(selection_order)) != len(selection_order):
                return {"error": "duplicate_providers"}

            comparison_year = self.year if self.year is not None else LATEST_DATA_YEAR
            unavailable = []
            compared = []
            for sel in selections:
                latest_year = self.data_processor.get_latest_year(sel['provider_code'], dataset_type)
                if latest_year is None or latest_year < comparison_year:
                    unavailable.append({
                        'provider_code': sel['provider_code'],
                        'provider_name': sel.get('provider_name') or sel['provider_code'],
                        'latest_year': latest_year,
                    })
                else:
                    compared.append(sel)
            selections = compared
            codes = [sel['provider_code'] for sel in selections]

            if not selections:
                return {
                    'dataset_type': dataset_type,
                    'comparison_year': comparison_year,
                    'selection_order': selection_order,
                    'unavailable': unavailable,
                    'peer_group': {},
                    'providers': [],
                    'measures': [],
                    'widest_gap': None,
                    'shared_below_median': [],
                    'shared_above_median': [],
                }

            peer_group = self.resolve_peer_group(codes, dataset_type, size_band, region)
            band, reg = peer_group['size_band'], peer_group['region']

            rankings = self.calculate_rankings(
                pd.DataFrame(), "All Providers", dataset_type,
                size_band=band, region=reg, include_provider_codes=codes)
            if "error" in rankings:
                return {"error": rankings["error"]}

            providers = []
            scores_by_provider = {}
            percentiles_by_provider = {}
            for sel in selections:
                code = sel['provider_code']
                if code not in rankings:
                    return {"error": f"No ranking data found for provider {code}"}

                scores_df = self.data_processor.get_provider_scores(
                    code, dataset_type=dataset_type, **self._year_kwargs())
                scores_by_provider[code] = {
                    tp: float(score)
                    for tp, score in zip(scores_df['tp_measure'], scores_df['score'])
                    if pd.notna(score)
                }
                percentiles_by_provider[code] = self._peer_percentiles(
                    code, dataset_type, band, reg, codes)

                providers.append({
                    'provider_code': code,
                    'provider_name': sel.get('provider_name') or code,
                    'ranking': rankings[code],
                    'momentum': self.calculate_momentum(
                        pd.DataFrame(), code, sel.get('provider_name'), dataset_type=dataset_type),
                    'priority': self.identify_priority(
                        pd.DataFrame(), code, sel.get('provider_name'), dataset_type=dataset_type,
                        size_band=band, region=reg, include_provider_codes=codes),
                })

            measures = []
            for tp_measure in self.data_processor.get_applicable_measures(dataset_type):
                values = {
                    code: {
                        'score': scores_by_provider[code].get(tp_measure),
                        'percentile': percentiles_by_provider[code].get(tp_measure),
                    }
                    for code in codes
                }
                reported = {code: v['score'] for code, v in values.items() if v['score'] is not None}
                if not reported:
                    continue
                complete = len(reported) == len(codes)
                high = max(reported.values())
                low = min(reported.values())
                measures.append({
                    'measure': tp_measure,
                    'description': self.tp_descriptions.get(tp_measure, tp_measure),
                    'values': values,
                    # Highest/lowest are only named when every provider reported
                    # the measure and the scores are not tied.
                    'highest': [c for c, sc in reported.items() if sc == high] if complete and high != low else [],
                    'lowest': [c for c, sc in reported.items() if sc == low] if complete and high != low else [],
                    'spread': (high - low) if complete else None,
                })

            # "Across the group" findings need at least two providers to compare.
            is_group = len(codes) >= MIN_COMPARE_PROVIDERS
            with_spread = [m for m in measures if m['spread'] is not None] if is_group else []
            widest_gap = max(with_spread, key=lambda m: m['spread']) if with_spread else None
            # Measures where every provider sits in the lower half of the peer group.
            shared_below_median = [
                m['measure'] for m in measures
                if is_group and all(
                    v['percentile'] is not None and v['percentile'] < 50 for v in m['values'].values())
            ]
            shared_above_median = [
                m['measure'] for m in measures
                if is_group and all(
                    v['percentile'] is not None and v['percentile'] >= 50 for v in m['values'].values())
            ]

            return {
                'dataset_type': dataset_type,
                'comparison_year': comparison_year,
                'selection_order': selection_order,
                'unavailable': unavailable,
                'peer_group': peer_group,
                'providers': providers,
                'measures': measures,
                'widest_gap': widest_gap,
                'shared_below_median': shared_below_median,
                'shared_above_median': shared_above_median,
            }

        except Exception as e:
            return {"error": f"Error comparing providers: {str(e)}"}
