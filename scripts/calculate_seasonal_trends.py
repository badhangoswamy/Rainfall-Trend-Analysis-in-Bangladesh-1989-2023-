# ======================================================
# Seasonal Rainfall Trend Analysis Script
# Author: Badhan Goswamy
# Purpose: Calculate Mann-Kendall & Sen's slope trends
#          for each station and each season (1989–2023)
# ======================================================

import pandas as pd
import numpy as np
import pymannkendall as mk
import os

# === 1. File paths ===
monthly_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Rainfall_monthly_1989_2023.csv"
output_dir = os.path.dirname(monthly_path)

# === 2. Load data ===
print("🔹 Loading monthly rainfall data...")
df = pd.read_csv(monthly_path)
df.columns = [c.strip().capitalize() for c in df.columns]

# Ensure correct data types
df["Year"] = df["Year"].astype(int)
df["Month"] = df["Month"].astype(int)
df["Rainfall"] = pd.to_numeric(df["Rainfall"], errors="coerce")

# === 3. Define seasons ===
def classify_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Pre-monsoon"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    elif month in [10, 11]:
        return "Post-monsoon"
    else:
        return None

df["Season"] = df["Month"].apply(classify_season)

# === 4. Aggregate by season ===
seasonal = (
    df.groupby(["Station", "Year", "Season"])["Rainfall"]
    .sum()
    .reset_index()
)

# === 5. Compute Mann-Kendall & Sen’s slope ===
results = []
stations = sorted(seasonal["Station"].unique())
seasons = ["Winter", "Pre-monsoon", "Monsoon", "Post-monsoon"]

print(f"📊 Calculating trends for {len(stations)} stations...")

for st in stations:
    for ss in seasons:
        data = seasonal[(seasonal["Station"] == st) & (seasonal["Season"] == ss)]
        if len(data) < 10:
            continue
        rain = data["Rainfall"].values
        if np.all(np.isnan(rain)):
            continue
        mk_res = mk.original_test(rain)
        results.append({
            "Station": st,
            "Season": ss,
            "n_years": len(rain),
            "MK_tau": mk_res.Tau,
            "MK_p_value": mk_res.p,
            "Trend": mk_res.trend,
            "Sen_slope_mm_per_year": mk_res.slope if hasattr(mk_res, "slope") else np.nan,
            "Mean_rainfall_mm": np.nanmean(rain)
        })

# === 6. Save results ===
res_df = pd.DataFrame(results)
output_file = os.path.join(output_dir, "Trend_results_seasonal.csv")
res_df.to_csv(output_file, index=False)

print(f"✅ Seasonal trend results saved at:\n{output_file}")
