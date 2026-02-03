
import os
import pandas as pd
import pyodbc

# -------------------------------
# 1. SQL Server connection
# -------------------------------
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-1BCJTC8\\SQLEXPRESS01;"
    "DATABASE=ml_database;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

print("✅ Connected to SQL Server successfully")

# -------------------------------
# 2. Tables to fetch
# -------------------------------
tables = ["products", "store_sales_header"]

# -------------------------------
# 3. Create folder if not exists
# -------------------------------
raw_data_path = os.path.join("data", "raw_sql")
os.makedirs(raw_data_path, exist_ok=True)

print(f"📁 Data folder ready: {raw_data_path}")

# -------------------------------
# 4. Fetch tables and save as CSV
# -------------------------------
for table in tables:
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, conn)

    file_path = os.path.join(raw_data_path, f"{table}.csv")
    df.to_csv(file_path, index=False, encoding="utf-8")

    print(f"✅ Saved {table} → {file_path}")

# -------------------------------
# 5. Close connection (ONLY HERE)
# -------------------------------
conn.close()

print("🎯 Data ingestion completed successfully")








































