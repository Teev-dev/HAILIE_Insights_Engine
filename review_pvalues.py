#!/usr/bin/env python3
"""
P-Value Review Script for HAILIE TSM Analytics
Run this script to review correlation p-values and statistical significance
"""

import duckdb
import pandas as pd
import sys
import os


def format_pvalue(p):
    """Format p-value for display"""
    if p < 0.001:
        return f"{p:.2e} ***"
    elif p < 0.01:
        return f"{p:.4f} **"
    elif p < 0.05:
        return f"{p:.4f} *"
    else:
        return f"{p:.4f}"


def interpret_correlation(r):
    """Interpret correlation strength"""
    r_abs = abs(r)
    if r_abs >= 0.7:
        return "Strong"
    elif r_abs >= 0.4:
        return "Moderate"
    else:
        return "Weak"


def main():
    db_path = "attached_assets/hailie_analytics.duckdb"

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Error: Database not found at {db_path}")
        print(
            "Please run 'python build_analytics_db.py' first to create the analytics database."
        )
        sys.exit(1)

    try:
        # Connect to database
        conn = duckdb.connect(db_path, read_only=True)

        # Get correlation data
        correlations_df = conn.execute("""
            SELECT 
                tp_measure,
                correlation_with_tp01,
                p_value,
                sample_size
            FROM calculated_correlations
            ORDER BY tp_measure
        """).df()

        if correlations_df.empty:
            print("❌ No correlation data found in database")
            sys.exit(1)

        # Display header
        print("=" * 80)
        print("📊 P-VALUE ANALYSIS FOR TSM CORRELATIONS WITH TP01")
        print("=" * 80)
        print()

        # Display all correlations with interpretations
        print("CORRELATION RESULTS:")
        print("-" * 80)
        print(
            f"{'Measure':<10} {'Correlation':<12} {'P-Value':<15} {'Significance':<15} {'Strength':<12} {'Sample':<8}"
        )
        print("-" * 80)

        for _, row in correlations_df.iterrows():
            measure = row['tp_measure']
            corr = row['correlation_with_tp01']
            p_val = row['p_value']
            sample = row['sample_size']

            # Determine significance
            if p_val < 0.001:
                sig = "***"
                sig_text = "Highly Sig"
            elif p_val < 0.01:
                sig = "**"
                sig_text = "Very Sig"
            elif p_val < 0.05:
                sig = "*"
                sig_text = "Significant"
            else:
                sig = ""
                sig_text = "Not Sig"

            strength = interpret_correlation(corr)

            # Format p-value
            if p_val < 0.0001:
                p_display = f"{p_val:.2e}"
            else:
                p_display = f"{p_val:.6f}"

            print(
                f"{measure:<10} {corr:>+.3f} {sig:<6} {p_display:<15} {sig_text:<15} {strength:<12} {sample:<8}"
            )

        print()
        print("=" * 80)

        # Summary statistics
        print("\nSTATISTICAL SUMMARY:")
        print("-" * 80)

        highly_sig = (correlations_df['p_value'] < 0.001).sum()
        very_sig = (correlations_df['p_value'] < 0.01).sum()
        sig = (correlations_df['p_value'] < 0.05).sum()
        not_sig = (correlations_df['p_value'] >= 0.05).sum()

        print(f"Total measures analyzed: {len(correlations_df)}")
        print(f"Highly significant (p < 0.001): {highly_sig} measures ***")
        print(f"Very significant (p < 0.01): {very_sig} measures **")
        print(f"Significant (p < 0.05): {sig} measures *")
        print(f"Not significant (p ≥ 0.05): {not_sig} measures")

        print()
        print("CORRELATION STRENGTH DISTRIBUTION:")
        print("-" * 80)

        strong = (correlations_df['correlation_with_tp01'].abs() >= 0.7).sum()
        moderate = (
            (correlations_df['correlation_with_tp01'].abs() >= 0.4) &
            (correlations_df['correlation_with_tp01'].abs() < 0.7)).sum()
        weak = (correlations_df['correlation_with_tp01'].abs() < 0.4).sum()

        print(f"Strong correlations (|r| ≥ 0.7): {strong} measures")
        print(f"Moderate correlations (0.4 ≤ |r| < 0.7): {moderate} measures")
        print(f"Weak correlations (|r| < 0.4): {weak} measures")

        print()
        print("P-VALUE RANGE:")
        print("-" * 80)
        min_p = correlations_df['p_value'].min()
        max_p = correlations_df['p_value'].max()
        print(f"Minimum p-value: {min_p:.2e}")
        print(f"Maximum p-value: {max_p:.2e}")

        print()
        print("=" * 80)
        print("\n📚 INTERPRETATION GUIDE:")
        print("-" * 80)
        print(f"""
P-VALUE SIGNIFICANCE LEVELS:
  *** p < 0.001  : Extremely strong evidence against null hypothesis
  **  p < 0.01   : Very strong evidence against null hypothesis
  *   p < 0.05   : Strong evidence against null hypothesis
      p ≥ 0.05   : Insufficient evidence (could be due to chance)

CORRELATION STRENGTH:
  Strong   : |r| ≥ 0.7  - Strong linear relationship
  Moderate : 0.4 ≤ |r| < 0.7 - Moderate linear relationship
  Weak     : |r| < 0.4  - Weak linear relationship

WHAT THIS MEANS:
- Lower p-values = more confident the correlation is real (not random)
- Higher correlation values = stronger relationship between measures
- Sample size of {correlations_df['sample_size'].iloc[0]} providers gives reliable results
""")

        print()
        print("=" * 80)
        print("\n💡 EXPORT DATA:")
        print("-" * 80)

        # Create export dataframe
        export_df = correlations_df.copy()
        export_df['significance'] = export_df['p_value'].apply(
            lambda p: 'Highly Significant' if p < 0.001 else 'Very Significant'
            if p < 0.01 else 'Significant' if p < 0.05 else 'Not Significant')
        export_df['strength'] = export_df['correlation_with_tp01'].apply(
            interpret_correlation)

        # Save to CSV
        output_file = "pvalue_analysis.csv"
        export_df.to_csv(output_file, index=False)
        print(f"✅ Full analysis exported to: {output_file}")

        print()
        print("=" * 80)

        conn.close()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()