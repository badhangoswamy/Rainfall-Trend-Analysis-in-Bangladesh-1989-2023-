# ======================================================
# Rainfall Trend Analysis Script
# Author: Badhan Goswamy
# Purpose: Mann–Kendall trend test + Sen’s slope (1989–2023)
# ======================================================

import pandas as pd
import numpy as np
import pymannkendall as mk
from scipy.stats import linregress
import os

# === 1. Set file path ===
input_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Rainfall_annual_1989_2023.csv"

# === 2. Load the dataset ===
print("🔹 Reading annual rainfall data...")
df = pd.read_csv(input_path)

# Ensure proper column names
df.columns = [c.strip().capitalize() for c in df.columns]

# Check required columns
required_cols = {"Station", "Year", "Rainfall"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"❌ Missing columns! Found: {list(df.columns)}")

# Sort data
df = df.sort_values(["Station", "Year"]).dropna(subset=["Rainfall"])

# === 3. Run Mann–Kendall and Sen’s slope per station ===
results = []
stations = df["Station"].unique()

print(f"📈 Running trend analysis for {len(stations)} stations...")

for st in stations:
    data = df[df["Station"] == st]
    years = data["Year"].values
    rain = data["Rainfall"].values

    if len(rain) < 10:
        continue  # skip short series

    # Mann-Kendall test
    mk_result = mk.original_test(rain)
    slope = mk_result.slope if hasattr(mk_result, 'slope') else np.nan

    # Linear regression (for comparison)
    lr = linregress(years, rain)

    results.append({
        "Station": st,
        "n_years": len(rain),
        "MK_tau": mk_result.Tau,
        "MK_p_value": mk_result.p,
        "Trend": mk_result.trend,
        "Sen_slope_mm_per_year": slope,
        "Linear_slope_mm_per_year": lr.slope,
        "Linear_p_value": lr.pvalue,
        "Mean_rainfall_mm": np.mean(rain)
    })

# === 4. Save results ===
results_df = pd.DataFrame(results)
output_dir = os.path.dirname(input_path)
output_path = os.path.join(output_dir, "Trend_results_stations.csv")
results_df.to_csv(output_path, index=False)

print(f"✅ Trend analysis completed!")
print(f"📂 Results saved at: {output_path}")
