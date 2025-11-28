"""
Helper functions for the BikeFit application
"""
import os
import csv
import pandas as pd
from typing import Tuple


def clear_terminal():
    """Clear the terminal screen based on the operating system"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac
        os.system('clear')


def calculate_angle_stats(knee_angles: list, hip_angles: list) -> Tuple[float, float, float, float, float, float]:
    """
    Calculate angle statistics from lists of angle measurements.

    Args:
        knee_angles: List of knee angle measurements.
        hip_angles: List of hip angle measurements.

    Returns:
        A tuple containing (knee_angle_min, knee_angle_max, knee_angle_avg,
                         hip_angle_min, hip_angle_max, hip_angle_avg).
    """
    if not knee_angles or not hip_angles:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    df = pd.DataFrame({'Knee Angle': knee_angles, 'Hip Angle': hip_angles})
    
    knee_angle_min = df['Knee Angle'].min()
    hip_angle_min = df['Hip Angle'].min()
    knee_angle_max = df['Knee Angle'].max()
    hip_angle_max = df['Hip Angle'].max()
    knee_angle_avg = df['Knee Angle'].mean()
    hip_angle_avg = df['Hip Angle'].mean()
    
    return (knee_angle_min, knee_angle_max, knee_angle_avg, hip_angle_min, hip_angle_max, hip_angle_avg)





def write_out_user(user_data: dict):
    """
    Display user bike fit profile in a formatted way
    
    Args:
        user_data: Dictionary containing user profile information
    """
    print("User Bike Fit Profile:")
    print("-" * 20)
    for key, value in user_data.items():
        # Replace underscores with spaces and capitalize for readability
        label = key.replace('_', ' ').title()
        print(f"{label}: {value}")
    print("-" * 20) 