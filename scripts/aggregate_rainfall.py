# ======================================================
# Rainfall Aggregation Script
# Author: Badhan Goswamy
# Purpose: Aggregate daily rainfall data (1989–2023)
#          into monthly and annual totals for each station
# ======================================================

import pandas as pd
import os

# === 1. Set file path ===
input_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Rainfall combined.csv"

# === 2. Load the dataset ===
print("🔹 Reading dataset...")
df = pd.read_csv(input_path)

# === 3. Basic cleaning ===
# Ensure consistent column names
df.columns = [c.strip().capitalize() for c in df.columns]

# Check required columns
required_cols = {"Station", "Date", "Rainfall"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"❌ Missing required columns! Found: {list(df.columns)}")

# Convert date column to datetime
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Remove invalid rows
df = df.dropna(subset=["Date", "Rainfall"])
df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors="coerce").fillna(0)

# === 4. Extract Year and Month ===
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# === 5. Aggregate data ===
print("📅 Aggregating to monthly totals...")
monthly = (
    df.groupby(["Station", "Year", "Month"])["Rainfall"]
    .sum()
    .reset_index()
    .sort_values(["Station", "Year", "Month"])
)

print("📆 Aggregating to annual totals...")
annual = (
    df.groupby(["Station", "Year"])["Rainfall"]
    .sum()
    .reset_index()
    .sort_values(["Station", "Year"])
)

# === 6. Save outputs ===
output_dir = os.path.dirname(input_path)
monthly_path = os.path.join(output_dir, "Rainfall_monthly_1989_2023.csv")
annual_path = os.path.join(output_dir, "Rainfall_annual_1989_2023.csv")

monthly.to_csv(monthly_path, index=False)
annual.to_csv(annual_path, index=False)

print(f"✅ Monthly totals saved as:\n   {monthly_path}")
print(f"✅ Annual totals saved as:\n   {annual_path}")
print("🎯 Aggregation completed successfully!")

