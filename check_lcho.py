import duckdb

# Connect to the database
conn = duckdb.connect("hailie_analytics_v2.duckdb", read_only=True)

# Check LCHO provider names
result = conn.execute("""
    SELECT DISTINCT provider_name, provider_code, dataset_type 
    FROM provider_summary 
    WHERE dataset_type = 'LCHO'
    LIMIT 5
""").fetchall()

print("LCHO Providers in database:")
for row in result:
    print(f"  Name: {row[0]}, Code: {row[1]}, Dataset: {row[2]}")

# Check what Housing 21 looks like
result2 = conn.execute("""
    SELECT provider_name, provider_code, dataset_type 
    FROM provider_summary 
    WHERE provider_code = 'L0055'
""").fetchall()

print("\nHousing 21 (L0055) in database:")
for row in result2:
    print(f"  Name: {row[0]}, Code: {row[1]}, Dataset: {row[2]}")

conn.close()