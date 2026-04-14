#!/usr/bin/env python3
"""
Interactive script to explore HAILIE Analytics Database
"""

import duckdb
import pandas as pd
import sys
from config import DATA_DIR
import os

def main():
    # Connect to the database
    db_path = os.path.join(DATA_DIR, "hailie_analytics.duckdb")
    print(f"Connecting to database: {db_path}")

    try:
        conn = duckdb.connect(db_path)

        # Show available tables
        print("\n📊 Available tables:")
        tables = conn.execute("SHOW TABLES").df()
        print(tables)

        # View raw_scores sample
        print("\n📈 Sample of raw_scores table (first 5 rows):")
        raw_scores = conn.execute("SELECT * FROM raw_scores LIMIT 5").df()
        print(raw_scores)

        # View correlations with actual p-values
        print("\n🔗 Correlation Analysis (with full p-values):")
        correlations = conn.execute("""
            SELECT 
                tp_measure,
                correlation_with_tp01,
                p_value,
                sample_size
            FROM calculated_correlations
            ORDER BY ABS(correlation_with_tp01) DESC
        """).df()

        # Show actual p-values in scientific notation if very small
        pd.options.display.float_format = '{:.2e}'.format
        print(correlations)

        # Show p-value statistics
        print("\n📊 P-value statistics:")
        print(f"Min p-value: {correlations['p_value'].min():.6e}")
        print(f"Max p-value: {correlations['p_value'].max():.6f}")
        print(f"P-values < 0.05: {(correlations['p_value'] < 0.05).sum()} out of {len(correlations)}")
        print(f"P-values < 0.01: {(correlations['p_value'] < 0.01).sum()} out of {len(correlations)}")
        print(f"P-values < 0.001: {(correlations['p_value'] < 0.001).sum()} out of {len(correlations)}")

        # Interactive mode
        print("\n💡 Entering interactive mode. You can now query the database.")
        print("Example queries:")
        print("  conn.execute('SELECT * FROM raw_scores WHERE provider_code = \"P001\"').df()")
        print("  conn.execute('SELECT DISTINCT tp_measure FROM calculated_percentiles').df()")
        print("\nVariables available: conn, correlations, raw_scores")

        # Keep connection open for interactive use
        return conn, correlations, raw_scores

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    conn, correlations, raw_scores = main()