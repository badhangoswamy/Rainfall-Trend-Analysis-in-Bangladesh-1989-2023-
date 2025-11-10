# ======================================================
# Automatic Seasonal Rainfall Trend Mapping Script
# Author: Badhan Goswamy
# Purpose: Plot Mann–Kendall & Sen’s slope trends for
#          all seasons (1989–2023) with season months
# ======================================================

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.lines as mlines
import os

# === 1. File paths ===
trend_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Trend_results_seasonal.csv"
coord_path = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023\Station coordinates (latitude, longitude).csv"

# === 2. Load data ===
print("🔹 Loading data...")
trend = pd.read_csv(trend_path, encoding='utf-8')
coords = pd.read_csv(coord_path, encoding='latin1', engine='python')

# Clean column names
trend.columns = [c.strip().capitalize() for c in trend.columns]
coords.columns = [c.strip().capitalize() for c in coords.columns]

# Merge coordinates
merged = pd.merge(trend, coords, on="Station", how="left")
merged = merged.dropna(subset=["Latitude", "Longitude"])

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    merged,
    geometry=gpd.points_from_xy(merged["Longitude"], merged["Latitude"]),
    crs="EPSG:4326"
)

# === 3. Define seasons and their months ===
seasons = ["Winter", "Pre-monsoon", "Monsoon", "Post-monsoon"]
season_months = {
    "Winter": "Dec–Feb",
    "Pre-monsoon": "Mar–May",
    "Monsoon": "Jun–Sep",
    "Post-monsoon": "Oct–Nov"
}

# Compute symmetric color range (same for all maps)
vmax = abs(gdf["Sen_slope_mm_per_year"]).max()

# === 4. Loop through seasons and create maps ===
output_dir = os.path.dirname(trend_path)
for selected_season in seasons:
    print(f"📊 Generating map for: {selected_season}")

    df_season = gdf[gdf["Season"] == selected_season].copy()
    if df_season.empty:
        print(f"⚠️ No data for {selected_season}, skipping.")
        continue

    # === 5. Create map ===
    fig = plt.figure(figsize=(9, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([87, 93, 20, 27], crs=ccrs.PlateCarree())

    # Add background features
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.RIVERS, linewidth=0.3)
    ax.gridlines(draw_labels=True, linewidth=0.2, color='gray', alpha=0.5)

    # === 6. Plot Sen’s slope ===
    sc = ax.scatter(
        df_season["Longitude"],
        df_season["Latitude"],
        c=df_season["Sen_slope_mm_per_year"],
        cmap="RdBu_r",
        vmin=-vmax, vmax=vmax,
        s=90, edgecolor="k", alpha=0.9,
        transform=ccrs.PlateCarree()
    )

    # Highlight significant (p < 0.05)
    sig = df_season[df_season["Mk_p_value"] < 0.05]
    ax.scatter(sig["Longitude"], sig["Latitude"],
               facecolors='none', edgecolors='black',
               s=220, linewidth=1.4, transform=ccrs.PlateCarree())

    # === 7. Add station labels ===
    for _, row in df_season.iterrows():
        ax.text(row["Longitude"] + 0.05, row["Latitude"] + 0.05,
                row["Station"], fontsize=7, transform=ccrs.PlateCarree())

    # === 8. Colorbar & legend ===
    cbar = plt.colorbar(sc, ax=ax, orientation="vertical", shrink=0.8, pad=0.07)
    cbar.set_label("Sen’s slope (mm/year)", fontsize=10)

    sig_marker = mlines.Line2D([], [], color='black', marker='o', linestyle='None',
                               markersize=8, label='Significant (p < 0.05)')
    ax.legend(handles=[sig_marker], loc='lower left', fontsize=8, frameon=True)

    # === 9. Add title and months text ===
    plt.title(
        f"{selected_season} Rainfall Trend in Bangladesh (1989–2023)\n"
        "Analysis: Mann–Kendall & Sen’s slope",
        fontsize=12,
        pad=10
    )

    # Add months info on map (top-left corner)
    ax.text(
        87.2, 26.6,
        f"Months: {season_months.get(selected_season, '')}",
        fontsize=9,
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'),
        transform=ccrs.PlateCarree()
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # === 10. Save map ===
    output_file = os.path.join(output_dir, f"Rainfall_Trend_Map_{selected_season}_1989_2023.png")
    plt.savefig(output_file, dpi=500, bbox_inches='tight')
    plt.close(fig)

    print(f"✅ Saved: {output_file}")

print("🎯 All four seasonal maps created successfully!")
