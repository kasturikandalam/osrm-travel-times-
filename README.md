# OSRM Travel Time Tools

This repository provides lightweight tools for computing travel-time and distance measures using the Open Source Routing Machine (OSRM).  
Given latitude/longitude coordinates, the functions return `pandas` DataFrames with road-network travel times (in minutes) and distances (in kilometers).

This version is designed for small and medium-sized research tasks using the public OSRM server.

---

## Features

- Compute many-to-many travel-time matrices (`/table` API)
- Compute pairwise origin → destination travel times (`/route` API)
- Supports `driving`, `walking`, and `cycling` modes
- Returns clean `pandas` DataFrames ready for analysis
- No external setup required — runs entirely through the public OSRM server

---

## Installation

```bash
git clone https://github.com/kasturikandalam/osrm-travel-times.git
cd osrm-travel-times
pip install -r requirements.txt
```

---

## Quick Start

### Example: Travel Times Between Four Landmarks in Delhi

Coordinates used (my most visited in Delhi):
* ISI Delhi: 28.68902, 77.20989
* ABCOFFEE (Malviya Nagar): 28.53074, 77.21043
* Delhi Airport (Terminal 3): 28.55616, 77.10004
* Lodhi Gardens: 28.59330, 77.21957

Run:

```bash
python demo_run.py
```

Output will appear in `results/`:

```
results/demo_durations_min.csv   # travel times (minutes)
results/demo_distances_km.csv    # distances (km)
results/demo_pairwise_results.csv # pairwise OD results
```

---

## Using the Tools in Your Own Code

### 1) Many-to-many matrix (e.g., accessibility or travel friction)

```python
from osrm_tools import osrm_table_matrix

origins = [
    (28.68902, 77.20989),  # ISI Delhi
    (28.53074, 77.21043),  # ABCOFFEE
]

destinations = [
    (28.55616, 77.10004),  # Delhi Airport
    (28.59330, 77.21957),  # Lodhi Gardens
]

dur_df, dist_df = osrm_table_matrix(origins, destinations, profile="driving")

print(dur_df.round(1))   # minutes
print(dist_df.round(2))  # km
```

**When to use:** Computing accessibility measures, market access, or full distance matrices.

### 2) Row-wise OD pairs (e.g., origin-destination table in a dataset)

```python
import pandas as pd
from osrm_tools import OSRMTravelTimeCalculator

pairs = pd.DataFrame([
    {"origin":"ISI Delhi","o_lat":28.68902,"o_lon":77.20989,
     "dest":"Lodhi Gardens","d_lat":28.59330,"d_lon":77.21957},
    {"origin":"ABCOFFEE","o_lat":28.53074,"o_lon":77.21043,
     "dest":"Airport","d_lat":28.55616,"d_lon":77.10004},
])

calc = OSRMTravelTimeCalculator(profile="driving")
res = calc.calculate_travel_matrix(
    pairs,
    origin_lat_col="o_lat", origin_lon_col="o_lon",
    dest_lat_col="d_lat", dest_lon_col="d_lon"
)

print(res)
```

**When to use:** When you have specific OD pairs in your dataset (e.g., household to nearest hospital).

---

## Repository Layout

```
osrm-travel-times/
├─ osrm_tools.py           # Core functions (matrix + pairwise)
├─ demo_run.py             # Example walkthrough
├─ demo_points.csv         # Coordinates for Delhi landmarks
├─ results/                # Output CSVs (created when you run demos)
├─ requirements.txt
└─ README.md
```

---

## Transportation Modes

```python
# Driving (default)
osrm_table_matrix(origins, dests, profile="driving")

# Walking
osrm_table_matrix(origins, dests, profile="walking")

# Cycling
osrm_table_matrix(origins, dests, profile="cycling")
```

---

## Research Applications

### Market Accessibility

```python
# Calculate travel time from villages to nearest market
villages = [(lat1, lon1), (lat2, lon2), ...]
markets = [(market_lat1, market_lon1), ...]

dur_df, dist_df = osrm_table_matrix(villages, markets, profile="driving")

# Find minimum travel time to any market for each village
min_access = dur_df.min(axis=1)
print(f"Average market access time: {min_access.mean():.1f} minutes")
```

### Migration Costs

```python
# Calculate travel times between origin and destination districts
migration_df = pd.read_csv('migration_flows.csv')

calc = OSRMTravelTimeCalculator(profile="driving")
migration_df = calc.calculate_travel_matrix(
    migration_df,
    origin_lat_col='origin_lat',
    origin_lon_col='origin_lon',
    dest_lat_col='dest_lat',
    dest_lon_col='dest_lon'
)

# Analyze relationship between distance and migration
import statsmodels.api as sm
X = sm.add_constant(migration_df['travel_time_minutes'])
y = migration_df['migration_flow']
model = sm.OLS(y, X).fit()
print(model.summary())
```

---

## Notes

* Uses the public OSRM server: `https://router.project-osrm.org`
* Suitable for small/medium-scale requests (hundreds–few thousand calls)
* For very large routing datasets, consider running a local OSRM instance
* Respects API rate limits with configurable delays

---

## Limitations

1. **Public API Rate Limits**: ~100 requests/minute. The pairwise calculator includes delays.
2. **Coverage**: Based on OpenStreetMap data. Quality varies by region.
3. **Traffic**: Returns free-flow travel times, not real-time traffic conditions.
4. **Coordinate Order**: OSRM uses (longitude, latitude) order internally, but the functions here accept standard (latitude, longitude) tuples.

---

## License

MIT License

---

## Contact

Kasturi Kandalam  
[kasturiveemohan@gmail.com](mailto:kasturiveemohan@gmail.com)  
[GitHub](https://github.com/kasturikandalam)

---
 ⭐⭐⭐
