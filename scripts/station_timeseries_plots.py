"""
station_timeseries_plots.py

Produces station-wise time-series plots (annual and optional monthly)
with Mann-Kendall & Sen's slope annotations.

Outputs:
 - <Station>_annual_timeseries.png
 - optionally <Station>_monthly_timeseries.png

Edit the input paths and stations_to_plot list below if needed.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pymannkendall as mk

# ---------- User settings ----------
base_dir = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023"
annual_csv = os.path.join(base_dir, "Rainfall_annual_1989_2023.csv")
monthly_csv = os.path.join(base_dir, "Rainfall_monthly_1989_2023.csv")  # optional
trend_csv = os.path.join(base_dir, "Trend_results_stations.csv")

# Stations to plot:
# - set to "all" to make plots for every station in the annual file
# - or provide a list like ["Dhaka", "Rajshahi", "Chittagong"]
stations_to_plot = "all"

# Plot options
plot_monthly = True      # set False to skip monthly plots
save_png = True
output_dir = base_dir
dpi = 300
# ---------- end user settings ----------

# Utility: compute Sen's slope (median of pairwise slopes)
def sens_slope(years, values):
    # years and values are 1D numpy arrays, length n
    n = len(values)
    if n < 2:
        return np.nan
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            denom = (years[j] - years[i])
            if denom != 0:
                slopes.append((values[j] - values[i]) / denom)
    if len(slopes) == 0:
        return np.nan
    return float(np.median(slopes))

# Load data
print("Loading CSVs...")
df_ann = pd.read_csv(annual_csv)        # expects columns: Station, Year, Rainfall
df_ann.columns = [c.strip().capitalize() for c in df_ann.columns]

# Check monthly file only if plotting monthly
if plot_monthly:
    try:
        df_mon = pd.read_csv(monthly_csv)  # expects Station, Year, Month, Rainfall
        df_mon.columns = [c.strip().capitalize() for c in df_mon.columns]
        # create a Date column for monthly series
        if "Year" in df_mon.columns and "Month" in df_mon.columns:
            df_mon["Date"] = pd.to_datetime(df_mon["Year"].astype(int).astype(str) + "-" + df_mon["Month"].astype(int).astype(str) + "-01")
    except Exception as e:
        print("Warning: monthly CSV could not be loaded or parsed. Skipping monthly plots.")
        print(e)
        plot_monthly = False

# Station list
stations = sorted(df_ann["Station"].unique())
print(f"Found {len(stations)} stations.")

# If user set stations_to_plot == "all", use all; else verify provided names
if isinstance(stations_to_plot, str) and stations_to_plot.lower() == "all":
    selected = stations
else:
    # assume list
    selected = [s for s in stations_to_plot if s in stations]
    if not selected:
        print("No valid stations specified in stations_to_plot. Falling back to all stations.")
        selected = stations

# Create plots
for st in selected:
    print(f"Plotting station: {st}")
    s_ann = df_ann[df_ann["Station"] == st].sort_values("Year")
    if s_ann.empty:
        print(f"  -> No annual data for {st}, skipping.")
        continue

    years = s_ann["Year"].astype(int).values
    rain = s_ann["Rainfall"].astype(float).values

    # Mann-Kendall test (on annual totals)
    try:
        mk_res = mk.original_test(rain)
        mk_trend = mk_res.trend
        mk_p = mk_res.p
        mk_tau = mk_res.Tau
    except Exception:
        mk_res = None
        mk_trend = "unknown"
        mk_p = np.nan
        mk_tau = np.nan

    # Linear regression (for visual reference)
    lr = linregress(years, rain)
    lin_y = lr.intercept + lr.slope * years

    # Sen's slope (median of pairwise slopes)
    sen = sens_slope(years, rain)
    # build a Sen's line for plotting
    sen_line = sen * (years - years[0]) + rain[0]

    # --- Plot annual series ---
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.scatter(years, rain, s=30, color="tab:blue", label="Annual rainfall")
    ax.plot(years, lin_y, color="orange", lw=1.8, label=f"Linear fit (slope={lr.slope:.2f} mm/yr)")
    ax.plot(years, sen_line, color="red", lw=1.6, linestyle="--", label=f"Sen's slope={sen:.2f} mm/yr")
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual rainfall (mm)")
    ax.set_title(f"{st} — Annual rainfall (1989–2023)")
    # annotation for MK
    ann_text = f"Mann–Kendall: {mk_trend}\nTau={mk_tau:.3f}, p={mk_p:.3f}"
    ax.text(0.02, 0.95, ann_text, transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none"))

    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)

    if save_png:
        out = os.path.join(output_dir, f"{st}_annual_timeseries.png")
        plt.savefig(out, dpi=dpi, bbox_inches="tight")
        print(f"  -> Saved {out}")
    plt.close(fig)

    # --- Optional: monthly plot with 12-month rolling mean ---
    if plot_monthly:
        s_mon = df_mon[df_mon["Station"] == st].sort_values("Date")
        if not s_mon.empty:
            # ensure Date is datetime
            s_mon["Date"] = pd.to_datetime(s_mon["Date"])
            s_mon = s_mon.set_index("Date").asfreq("MS")  # ensure monthly index
            # fill missing months with NaN (do not fill values)
            rain_mon = s_mon["Rainfall"].astype(float)
            roll12 = rain_mon.rolling(window=12, min_periods=6).mean()

            fig2, ax2 = plt.subplots(figsize=(10, 3.2))
            ax2.plot(rain_mon.index, rain_mon.values, color="lightgray", lw=0.6, label="Monthly rainfall")
            ax2.plot(roll12.index, roll12.values, color="tab:blue", lw=1.6, label="12-mo rolling mean")
            ax2.set_ylabel("Rainfall (mm)")
            ax2.set_xlabel("Date")
            ax2.set_title(f"{st} — Monthly rainfall & 12-mo mean")
            ax2.grid(alpha=0.25)
            ax2.legend(fontsize=9)
            if save_png:
                out2 = os.path.join(output_dir, f"{st}_monthly_timeseries.png")
                plt.savefig(out2, dpi=dpi, bbox_inches="tight")
                print(f"  -> Saved {out2}")
            plt.close(fig2)
        else:
            print(f"  -> No monthly data for {st}, skipping monthly plot.")

print("All done.")
