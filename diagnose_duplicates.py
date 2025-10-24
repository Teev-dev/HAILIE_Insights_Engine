
#!/usr/bin/env python3
"""
Diagnostic script to identify duplicate provider entries in the database
Focus on providers appearing in both LCRA and LCHO datasets
"""

import duckdb
import pandas as pd

def diagnose_duplicates():
    """Check for duplicate providers in the database"""
    
    db_path = "attached_assets/hailie_analytics_v2.duckdb"
    
    print("🔍 Diagnosing duplicate provider entries...")
    print("=" * 70)
    
    conn = duckdb.connect(db_path, read_only=True)
    
    # Check 1: Find providers appearing in multiple datasets
    print("\n🔍 CRITICAL CHECK: Providers in Multiple Datasets")
    cross_dataset = conn.execute("""
        SELECT 
            provider_code,
            COUNT(DISTINCT dataset_type) as dataset_count,
            GROUP_CONCAT(DISTINCT dataset_type) as datasets,
            GROUP_CONCAT(DISTINCT provider_name) as names
        FROM provider_summary
        GROUP BY provider_code
        HAVING COUNT(DISTINCT dataset_type) > 1
        ORDER BY dataset_count DESC, provider_code
    """).df()
    
    if not cross_dataset.empty:
        print(f"  ⚠️ FOUND {len(cross_dataset)} providers appearing in multiple datasets!")
        print("\n  Affected providers:")
        for _, row in cross_dataset.iterrows():
            print(f"    • {row['provider_code']}: appears in {row['datasets']}")
            print(f"      Names: {row['names']}")
        
        # For each duplicate, show the different scores
        print("\n  📊 Score differences for duplicates:")
        for _, row in cross_dataset.iterrows():
            provider_code = row['provider_code']
            print(f"\n  Provider {provider_code}:")
            
            scores = conn.execute("""
                SELECT 
                    dataset_type,
                    tp_measure,
                    score
                FROM raw_scores
                WHERE provider_code = ?
                ORDER BY tp_measure, dataset_type
            """, [provider_code]).df()
            
            # Pivot to show side-by-side comparison
            if not scores.empty:
                pivot = scores.pivot(index='tp_measure', columns='dataset_type', values='score')
                print(pivot.to_string())
    else:
        print("  ✅ No providers found in multiple datasets")
    
    # Check 2: Detailed analysis of L4004
    print("\n\n🔎 Detailed Analysis of L4004:")
    l4004_summary = conn.execute("""
        SELECT *
        FROM provider_summary
        WHERE provider_code = 'L4004'
    """).df()
    
    if not l4004_summary.empty:
        print(f"  L4004 appears {len(l4004_summary)} times in provider_summary:")
        for idx, row in l4004_summary.iterrows():
            print(f"\n  Entry {idx + 1}:")
            print(f"    Dataset: {row['dataset_type']}")
            print(f"    Name: {row['provider_name']}")
            tp_cols = [col for col in l4004_summary.columns if col.startswith('TP')]
            for tp in sorted(tp_cols):
                if pd.notna(row[tp]):
                    print(f"    {tp}: {row[tp]:.1f}%")
    
    # Check 3: Count raw_scores entries
    print("\n\n📋 Raw Scores Count for L4004:")
    raw_count = conn.execute("""
        SELECT 
            dataset_type,
            COUNT(*) as score_count,
            COUNT(DISTINCT tp_measure) as unique_measures
        FROM raw_scores
        WHERE provider_code = 'L4004'
        GROUP BY dataset_type
    """).df()
    
    if not raw_count.empty:
        print(raw_count.to_string(index=False))
    
    # Check 4: Understand the source data pattern
    print("\n\n🔍 Overall Dataset Statistics:")
    stats = conn.execute("""
        SELECT 
            dataset_type,
            COUNT(DISTINCT provider_code) as unique_providers,
            COUNT(*) as total_rows
        FROM provider_summary
        GROUP BY dataset_type
        ORDER BY dataset_type
    """).df()
    
    print(stats.to_string(index=False))
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("🎯 Diagnosis Summary:")
    if not cross_dataset.empty:
        print(f"  ⚠️ ISSUE CONFIRMED: {len(cross_dataset)} providers appear in both LCRA and LCHO")
        print("  This creates duplicate entries with different scores!")
        print("\n  💡 Solution: ETL pipeline needs deduplication logic")
        print("     - Prioritize LCRA (has all metrics including repairs)")
        print("     - Or use COMBINED dataset when available")
    else:
        print("  ✅ No cross-dataset duplicates found")

if __name__ == "__main__":
    diagnose_duplicates()
