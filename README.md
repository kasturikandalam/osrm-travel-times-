Aim: Tools for computing travel-time and distance matrices using OSRM. Supports many-to-many routing, reproducible workflows, and local OSRM server setup for research-scale spatial analysis.

# OSRM Travel Time Tools

This repository provides tools for generating travel-time and distance matrices using the Open Source Routing Machine (OSRM).  
It takes lists of latitude/longitude coordinates and returns tidy `pandas` DataFrames with travel times (in minutes) and distances (in kilometers), using OSRM’s `/table` and `/route` APIs.

The workflow supports both:
- the public OSRM demo server (for small test queries), and
- a locally hosted OSRM server (recommended for research-scale jobs).

---

## Features

- Compute many-to-many travel-time matrices between sets of origin and destination points.
- Generate one-to-one route summaries with duration and distance.
- Handles batching/retries to avoid URL size and request limits.
- Works with `driving`, `foot`, and `bike` profiles.
- Returns results in standard `pandas` DataFrames for analysis.

---

## Installation

```bash
git clone https://github.com/<your-username>/osrm-travel-times.git
cd osrm-travel-times
pip install -r requirements.txt
