# Rainfall Trend Analysis in Bangladesh (1989–2023)

This project analyzes long-term rainfall patterns across Bangladesh using **Python**.  
It applies the **Mann–Kendall trend test** and **Sen’s slope estimator** to detect and quantify changes in seasonal and annual rainfall over 35 years (1989–2023).  
All visualizations and geospatial analyses are performed using Python libraries like `pandas`, `geopandas`, `matplotlib`, and `cartopy`.

---

## Objectives
- Analyze rainfall data from 32 meteorological stations across Bangladesh (1989–2023)
- Detect long-term trends using the **Mann–Kendall test**
- Quantify rate of change using **Sen’s slope estimator**
- Visualize rainfall trends on maps (station-based and interpolated)

---

## Methodology
1. **Data Preparation**
   - Combined daily rainfall data (1989–2023)
   - Aggregated to monthly and annual totals using `pandas`

2. **Trend Analysis**
   - Applied **Mann–Kendall test** (`pymannkendall`) for statistical significance
   - Calculated **Sen’s slope** for trend magnitude (mm/year)

3. **Visualization**
   - Created:
     - Station-based trend maps (Cartopy)
     - Seasonal trend maps
     - Interpolated continuous maps (IDW)

---

##  Example Outputs
| Type | Description |
|------|--------------|
| `Trend_results_stations.csv` | Annual trend results (MK test + Sen’s slope) |
| `Trend_results_seasonal.csv` | Seasonal trend summary |
| `Rainfall_Trend_Map_Bangladesh.png` | Station-based trend map |
| `Rainfall_Trend_IDW_Masked.png` | Interpolated IDW rainfall trend map |

---



## Libraries Used
```bash
pandas
numpy
matplotlib
geopandas
cartopy
scipy
pymannkendall
shapely
pyproj
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Folder Structure
```
rainfall-trend-analysis-bangladesh/
│
├── data/           # Raw and processed rainfall data
├── scripts/        # Python scripts for analysis
├── outputs/        # Maps and results
├── README.md       # Project overview
└── requirements.txt
```

---

## 💡 About the Project
This project was developed as part of my research work in **rainfall trend analysis** for Bangladesh.  
It demonstrates the use of **Python for climatological and geospatial data analysis**.

**Author:** Badhan Goswamy  
**Tools:** Python 3.11, ArcGIS (for comparison)  
**Duration:** 1989–2023  
