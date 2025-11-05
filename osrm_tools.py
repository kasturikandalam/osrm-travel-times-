"""
OSRM Travel Time Tools
======================

Lightweight tools for computing travel times and distances using OSRM.

Author: Kasturi Kandalam
Date: February 2025
"""

import pandas as pd
import numpy as np
import requests
import time
from typing import List, Tuple, Optional


def osrm_table_matrix(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]],
    profile: str = "driving"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compute many-to-many travel-time matrix using OSRM /table API.
    
    Parameters
    ----------
    origins : List[Tuple[float, float]]
        List of (latitude, longitude) tuples for origin points
    destinations : List[Tuple[float, float]]
        List of (latitude, longitude) tuples for destination points
    profile : str
        Transportation mode: 'driving', 'walking', or 'cycling'
        
    Returns
    -------
    durations_df : pd.DataFrame
        Travel times in minutes (origins as rows, destinations as columns)
    distances_df : pd.DataFrame
        Distances in kilometers (origins as rows, destinations as columns)
        
    Notes
    -----
    Uses OSRM /table endpoint which is optimized for many-to-many calculations.
    More efficient than multiple individual route requests.
    """
    
    # Convert coordinates to OSRM format (lon,lat)
    # Note: OSRM uses longitude first, opposite of common (lat,lon) convention
    all_coords = origins + destinations
    coord_strings = [f"{lon},{lat}" for lat, lon in all_coords]
    coords_param = ";".join(coord_strings)
    
    # Build API URL
    base_url = "http://router.project-osrm.org/table/v1"
    url = f"{base_url}/{profile}/{coords_param}"
    
    # Specify which are sources (origins) and destinations
    n_origins = len(origins)
    n_dests = len(destinations)
    
    params = {
        'sources': ';'.join(str(i) for i in range(n_origins)),
        'destinations': ';'.join(str(i) for i in range(n_origins, n_origins + n_dests))
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['code'] != 'Ok':
            raise ValueError(f"OSRM API error: {data['code']}")
        
        # Extract duration matrix (in seconds) and distance matrix (in meters)
        durations_sec = np.array(data['durations'])
        distances_m = np.array(data['distances'])
        
        # Convert to minutes and kilometers
        durations_min = durations_sec / 60
        distances_km = distances_m / 1000
        
        # Create DataFrames
        origin_labels = [f"Origin_{i+1}" for i in range(n_origins)]
        dest_labels = [f"Dest_{i+1}" for i in range(n_dests)]
        
        durations_df = pd.DataFrame(
            durations_min,
            index=origin_labels,
            columns=dest_labels
        )
        
        distances_df = pd.DataFrame(
            distances_km,
            index=origin_labels,
            columns=dest_labels
        )
        
        return durations_df, distances_df
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        raise
    except (KeyError, ValueError) as e:
        print(f"Error parsing response: {e}")
        raise


class OSRMTravelTimeCalculator:
    """
    Calculator for pairwise origin-destination travel times using OSRM /route API.
    
    Use this when you have a DataFrame of specific OD pairs rather than
    computing a full matrix.
    """
    
    def __init__(self, profile: str = "driving"):
        """
        Initialize the calculator.
        
        Parameters
        ----------
        profile : str
            Transportation mode: 'driving', 'walking', or 'cycling'
        """
        self.base_url = "http://router.project-osrm.org/route/v1"
        self.profile = profile
        
    def get_travel_time(
        self,
        origin_lon: float,
        origin_lat: float,
        dest_lon: float,
        dest_lat: float
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Get travel time and distance for a single OD pair.
        
        Parameters
        ----------
        origin_lon : float
            Origin longitude
        origin_lat : float
            Origin latitude
        dest_lon : float
            Destination longitude
        dest_lat : float
            Destination latitude
            
        Returns
        -------
        tuple : (travel_time_minutes, distance_km)
            Returns (None, None) if route cannot be found
        """
        
        coords = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        url = f"{self.base_url}/{self.profile}/{coords}"
        
        params = {
            'overview': 'false',
            'steps': 'false'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] != 'Ok':
                return None, None
            
            duration_seconds = data['routes'][0]['duration']
            distance_meters = data['routes'][0]['distance']
            
            travel_time_minutes = duration_seconds / 60
            distance_km = distance_meters / 1000
            
            return travel_time_minutes, distance_km
            
        except (requests.exceptions.RequestException, KeyError, IndexError):
            return None, None
    
    def calculate_travel_matrix(
        self,
        df: pd.DataFrame,
        origin_lat_col: str,
        origin_lon_col: str,
        dest_lat_col: str,
        dest_lon_col: str,
        delay: float = 0.5
    ) -> pd.DataFrame:
        """
        Calculate travel times for a DataFrame of OD pairs.
        
        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with origin and destination coordinates
        origin_lat_col : str
            Column name for origin latitude
        origin_lon_col : str
            Column name for origin longitude
        dest_lat_col : str
            Column name for destination latitude
        dest_lon_col : str
            Column name for destination longitude
        delay : float
            Seconds to wait between API calls (rate limiting)
            
        Returns
        -------
        pd.DataFrame
            Original dataframe with added columns:
            - travel_time_minutes
            - distance_km
        """
        
        result_df = df.copy()
        result_df['travel_time_minutes'] = np.nan
        result_df['distance_km'] = np.nan
        
        total_pairs = len(df)
        print(f"Calculating travel times for {total_pairs} OD pairs...")
        print(f"Profile: {self.profile}")
        print(f"Delay: {delay}s between requests")
        print("-" * 50)
        
        for idx, row in df.iterrows():
            origin_lat = row[origin_lat_col]
            origin_lon = row[origin_lon_col]
            dest_lat = row[dest_lat_col]
            dest_lon = row[dest_lon_col]
            
            travel_time, distance = self.get_travel_time(
                origin_lon, origin_lat,
                dest_lon, dest_lat
            )
            
            result_df.loc[idx, 'travel_time_minutes'] = travel_time
            result_df.loc[idx, 'distance_km'] = distance
            
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{total_pairs} pairs...")
            
            time.sleep(delay)
        
        print("-" * 50)
        successful = result_df['travel_time_minutes'].notna().sum()
        print(f"Complete! {successful}/{total_pairs} routes found")
        
        return result_df
