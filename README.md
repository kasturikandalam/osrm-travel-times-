# OSRM Travel Time Tools

This repository provides lightweight tools for computing travel-time and distance measures using the Open Source Routing Machine (OSRM).  
Given latitude/longitude coordinates, the functions return `pandas` DataFrames with road-network travel times (in minutes) and distances (in kilometers).

This version is designed for small and medium-sized research tasks using the public OSRM server. For larger research-scale jobs, batch running and using docker is recommended. 

---

## Features

- Compute many-to-many travel-time matrices (`/table` API).
- Compute pairwise origin → destination travel times (`/route` API).
- Supports `driving`, `walking`, and `cycling` modes.
- Returns clean `pandas` DataFrames ready for analysis.
- No external setup required — runs entirely through the public OSRM server.

---

## Installation

```bash
git clone https://github.com/<your-username>/osrm-travel-times.git
cd osrm-travel-times
pip install -r requirements.txt
