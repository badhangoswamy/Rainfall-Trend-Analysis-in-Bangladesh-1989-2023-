# ======================================================
# Rainfall Trend Mapping Script (Publication-ready)
# Author: Badhan Goswamy
# Purpose: Plot Sen’s slope & significance for rainfall trends (1989–2023)
# ======================================================

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as mlines
from adjustText import adjust_text
import os

# === 1. File paths ===
trend_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Trend_results_stations.csv"
coord_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Station coordinates (latitude, longitude).csv"

# === 2. Load datasets (handle encoding safely) ===
print("🔹 Loading data...")
trend = pd.read_csv(trend_path, encoding='utf-8')
coords = pd.read_csv(coord_path, encoding='latin1', engine='python')

# Clean column names
trend.columns = [c.strip().capitalize() for c in trend.columns]
coords.columns = [c.strip().capitalize() for c in coords.columns]

# Validate required columns
if not {"Station", "Latitude", "Longitude"}.issubset(coords.columns):
    raise ValueError("⚠️ Coordinate file must contain 'Station', 'Latitude', and 'Longitude'")
if "Sen_slope_mm_per_year" not in trend.columns:
    raise ValueError("⚠️ Trend file missing 'Sen_slope_mm_per_year' column")

# === 3. Merge coordinates with trend results ===
merged = pd.merge(trend, coords, on="Station", how="left")

# Drop missing coordinates if any
merged = merged.dropna(subset=["Latitude", "Longitude"])

# === 4. Convert to GeoDataFrame ===
gdf = gpd.GeoDataFrame(
    merged,
    geometry=gpd.points_from_xy(merged["Longitude"], merged["Latitude"]),
    crs="EPSG:4326"
)

# === 5. Plot map ===
fig = plt.figure(figsize=(9, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([87, 93, 20, 27], crs=ccrs.PlateCarree())

# Base features
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.RIVERS, linewidth=0.3)
ax.gridlines(draw_labels=True, linewidth=0.2, color='gray', alpha=0.5)

# === 6. Scatter plot (Sen's slope) ===
vmax = abs(gdf["Sen_slope_mm_per_year"]).max()  # symmetrical color range

sc = ax.scatter(
    gdf["Longitude"],
    gdf["Latitude"],
    c=gdf["Sen_slope_mm_per_year"],
    cmap="RdBu_r",
    vmin=-vmax, vmax=vmax,
    s=90, edgecolor="k", alpha=0.9,
    transform=ccrs.PlateCarree()
)

# Highlight significant stations (p < 0.05)
if "Mk_p_value" in gdf.columns:
    sig = gdf[gdf["Mk_p_value"] < 0.05]
    ax.scatter(sig["Longitude"], sig["Latitude"],
               facecolors='none', edgecolors='black',
               s=220, linewidth=1.4, transform=ccrs.PlateCarree())

# === 7. Add station labels (auto-adjust for overlap) ===
texts = []
for _, row in gdf.iterrows():
    texts.append(
        ax.text(row["Longitude"] + 0.05, row["Latitude"] + 0.05,
                row["Station"], fontsize=7, transform=ccrs.PlateCarree())
    )
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.4))

# === 8. Colorbar, legend, and title (Final compact version) ===
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", shrink=0.8, pad=0.07)
cbar.set_label("Sen’s slope (mm/year)", fontsize=10)

# Add legend for significance
sig_marker = mlines.Line2D([], [], color='black', marker='o', linestyle='None',
                           markersize=8, label='Significant (p < 0.05)')
ax.legend(handles=[sig_marker], loc='lower left', fontsize=8, frameon=True)

# Compact single-line title with minimal gap
plt.title(
   "Rainfall Trend in Bangladesh (1989–2023)\n"
    "Analysis: Mann–Kendall & Sen’s slope",
    fontsize=12,
    pad=8  # reduces distance between map and title
)

# Adjust layout to bring title closer
plt.tight_layout(rect=[0, 0, 1, 0.96])


# === 9. Save high-resolution output ===
output_dir = os.path.dirname(trend_path)
output_file = os.path.join(output_dir, "Rainfall_Trend_Map_Bangladesh_PublicationReady.png")
plt.savefig(output_file, dpi=500, bbox_inches='tight')
plt.show()

print(f" Map created successfully!")
print(f" Saved at: {output_file}")
