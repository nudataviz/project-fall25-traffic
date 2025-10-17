"""
Purpose:
    Generate simple synthetic traffic simulation data for two scenarios:
        1. "Early Merge"  drivers merge early, leading to smoother flow.
        2. "Late Merge"   drivers merge late, causing longer waits.

    The output dataset includes per-vehicle arrival times, wait times, and
    departure times for both scenarios. This script uses a simple queue model
    to simulate traffic flow and is designed to be self-contained, reproducible,
    and easy to understand.

Output:
    traffic_sim_basic.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)


N = 200


arrival_times = np.cumsum(np.random.exponential(scale=2.0, size=N))


service_early = np.random.normal(1.8, 0.2, N)   
service_late  = np.random.normal(2.5, 0.6, N) 

extra_early = np.random.exponential(0.2, N)    
extra_late  = np.random.exponential(1.0, N)     

def simulate(arrivals, service, extra, label):
    """
    Simulate a simple single-lane queue for one scenario.

    Parameters
    arrivals : array
        Sorted arrival times of vehicles (seconds).
    service : array
        Time each vehicle needs to pass the intersection (seconds).
    extra : array
        Additional delay before merging (seconds).
    label : str
        Scenario name ("Early Merge" or "Late Merge").

    Returns
    pandas.DataFrame
        A dataset with per-vehicle information:
        [scenario, car_id, arrival_time, wait_time, departure_time]
    """
    results = []
    last_depart = 0
    for i in range(len(arrivals)):
        start = max(arrivals[i], last_depart) + extra[i]  
        depart = start + service[i]
        wait = start - arrivals[i]
        last_depart = depart
        results.append([label, i+1, arrivals[i], wait, depart])
    return pd.DataFrame(results, columns=["scenario", "car_id", "arrival_time", "wait_time", "departure_time"])


early_df = simulate(arrival_times, service_early, extra_early, "Early Merge")
late_df  = simulate(arrival_times, service_late,  extra_late,  "Late Merge")


df = pd.concat([early_df, late_df], ignore_index=True)
df.to_csv("traffic_sim_basic.csv", index=False)

print("data has saved as traffic_sim_basic.csv")
print(df.head())

