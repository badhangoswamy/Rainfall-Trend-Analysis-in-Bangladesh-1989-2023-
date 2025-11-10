# Rainfall_Trend_IDW_Masked_fixed.py
# ======================================================
# IDW interpolation in projected coordinates + masking (FIXED)
# ======================================================

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point
from pyproj import Transformer

# ---------------- USER SETTINGS ----------------
base_dir = r"G:\Badhan --Study material  (Geology)\0 paper\0 Rainfall trend analysis\Rainfall 1989-2023"
trend_path = os.path.join(base_dir, "Trend_results_stations.csv")
coord_path = os.path.join(base_dir, "Station coordinates (latitude, longitude).csv")
shape_path = os.path.join(base_dir, "Districtdeg.shp")

# IDW parameters
power = 2.0                 # IDW power
search_radius = 150000.0    # meters (set to None to use all stations for each cell)
grid_resolution = 3000.0    # meters between grid cells (smaller => finer)
# ------------------------------------------------

# --- 1. Load data
trend = pd.read_csv(trend_path)
coords = pd.read_csv(coord_path, encoding='latin1', engine='python')
gdf_bd = gpd.read_file(shape_path)  # boundary (district polygons)

# Normalize column names
trend.columns = [c.strip().capitalize() for c in trend.columns]
coords.columns = [c.strip().capitalize() for c in coords.columns]

# Merge trend + coords
df = pd.merge(trend, coords, on="Station", how="left")
df = df.dropna(subset=["Latitude", "Longitude", "Sen_slope_mm_per_year"])

# --- 2. Convert stations to GeoDataFrame (lon/lat)
gdf_st = gpd.GeoDataFrame(df,
                          geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]),
                          crs="EPSG:4326")

# --- 3. Project everything to a metric CRS for IDW
crs_proj = "EPSG:3857"  # web mercator (meters). You can change to local UTM if you prefer.
gdf_bd_proj = gdf_bd.to_crs(crs_proj)
gdf_st_proj = gdf_st.to_crs(crs_proj)

# bounding box in projected coordinates
minx, miny, maxx, maxy = gdf_bd_proj.total_bounds
print(f"Projected bounds (meters): {minx:.0f}, {miny:.0f}, {maxx:.0f}, {maxy:.0f}")

# --- 4. Create regular grid in projected coords
nx = int(np.ceil((maxx - minx) / grid_resolution)) + 1
ny = int(np.ceil((maxy - miny) / grid_resolution)) + 1
grid_x = np.linspace(minx, maxx, nx)
grid_y = np.linspace(miny, maxy, ny)
gx, gy = np.meshgrid(grid_x, grid_y)

# Flatten grid points for computation
grid_points = np.vstack((gx.ravel(), gy.ravel())).T

# --- 5. Prepare station coords and values
stations_xy = np.vstack((gdf_st_proj.geometry.x.values, gdf_st_proj.geometry.y.values)).T
values = gdf_st_proj["Sen_slope_mm_per_year"].values

# --- 6. Fixed IDW implementation with chunking
def idw_interpolation(grid_pts, data_pts, data_vals, power=2.0, radius=None, chunk=20000, eps=1e-12):
    """
    grid_pts: (M,2) array of points to estimate
    data_pts: (N,2) array of station coordinates
    data_vals: (N,) station values
    radius: if not None, only stations within radius (meters) are used
    returns z (M,) estimated values
    """
    M = grid_pts.shape[0]
    N = data_pts.shape[0]
    z = np.full(M, np.nan, dtype=float)

    for i0 in range(0, M, chunk):
        i1 = min(M, i0 + chunk)
        gp = grid_pts[i0:i1]  # (K,2)
        # compute distances (K,N)
        dx = gp[:, 0:1] - data_pts[:, 0][None, :]
        dy = gp[:, 1:2] - data_pts[:, 1][None, :]
        dist = np.hypot(dx, dy)  # (K,N)

        # exact station match -> take station value
        exact = dist < 1e-6
        any_exact = exact.any(axis=1)
        if any_exact.any():
            idxs = np.where(any_exact)[0]
            for j in idxs:
                z[i0 + j] = data_vals[exact[j, :]][0]

        # Apply radius mask (if provided)
        if radius is not None:
            mask_within = dist <= radius
            dist_masked = np.where(mask_within, dist, np.nan)
        else:
            mask_within = np.ones_like(dist, dtype=bool)
            dist_masked = dist.copy()

        # Compute weights: 1 / dist^power
        with np.errstate(divide='ignore', invalid='ignore'):
            w = 1.0 / (np.power(dist_masked, power) + eps)

        # sum weights per grid point
        w_sum = np.nansum(w, axis=1)  # length K

        # valid grid points which have at least one neighbor within radius (or any if radius is None)
        valid = w_sum > 0

        if valid.any():
            # compute weighted sums for valid rows
            weighted = np.nansum(w[valid, :] * data_vals[None, :], axis=1)  # length = num_valid
            z_chunk = np.full(gp.shape[0], np.nan)
            z_chunk[valid] = weighted / w_sum[valid]
            z[i0:i1] = z_chunk

    return z

# Run IDW (this will fill grid cells depending on radius)
idw_z = idw_interpolation(grid_points, stations_xy, values, power=power, radius=search_radius, chunk=20000)
zi = idw_z.reshape(gx.shape)

# --- 7. Mask grid points outside Bangladesh polygon (projected)
# create shapely mask using unary_union for performance
bd_union = gdf_bd_proj.unary_union
inside_mask = np.array([bd_union.contains(Point(px, py)) for px, py in grid_points])
zi_masked = np.where(inside_mask.reshape(gx.shape), zi, np.nan)

# --- 8. Transform masked grid back to lon/lat for plotting
transformer = Transformer.from_crs(crs_proj, "EPSG:4326", always_xy=True)
pts_proj = np.vstack((gx.ravel(), gy.ravel())).T
lon, lat = transformer.transform(pts_proj[:, 0], pts_proj[:, 1])
lon_grid = lon.reshape(gx.shape)
lat_grid = lat.reshape(gx.shape)

# --- 9. Plot with Cartopy
fig = plt.figure(figsize=(9, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
pad_deg = 0.2
ax.set_extent([gdf_bd.total_bounds[0] - pad_deg, gdf_bd.total_bounds[2] + pad_deg,
               gdf_bd.total_bounds[1] - pad_deg, gdf_bd.total_bounds[3] + pad_deg],
              crs=ccrs.PlateCarree())

ax.add_feature(cfeature.LAND, facecolor="lightgray", zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.RIVERS, linewidth=0.3)

cf = ax.contourf(lon_grid, lat_grid, zi_masked, cmap="RdBu_r", levels=20, transform=ccrs.PlateCarree())

# overlay district boundary (lon/lat)
gdf_bd.boundary.plot(ax=ax, color="black", linewidth=0.6, zorder=3)

# station points (lon/lat)
ax.scatter(gdf_st.geometry.x, gdf_st.geometry.y, color="k", s=25, edgecolor="white", transform=ccrs.PlateCarree(), zorder=4)

cbar = plt.colorbar(cf, ax=ax, orientation="vertical", pad=0.07, shrink=0.8)
cbar.set_label("Sen's slope (mm/year)")

plt.title(f"Interpolated (IDW) Sen's slope masked to Bangladesh (power={power}, radius={search_radius} m)")
plt.tight_layout()
out = os.path.join(base_dir, "Rainfall_Trend_IDW_Masked_fixed.png")
plt.savefig(out, dpi=400, bbox_inches='tight')
plt.show()

print("Saved:", out)
