"""
Module: data_cleaning.py
Provides robust data loading, structural validation, range verification,
and feature engineering for the Smart Agriculture dataset.
"""

import pandas as pd
import numpy as np


def load_dataset(file_path="data/DS_Day01_33_Smart_Agriculture_Synthetic_Dataset.xlsx"):
    """
    Loads the agriculture Excel dataset and converts Timestamp to datetime.
    """
    df = pd.read_excel(file_path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df


def add_time_features(df):
    """
    Extracts useful derived temporal features from Timestamp.
    """
    df = df.copy()
    df["Date"] = df["Timestamp"].dt.date
    df["Day"] = df["Timestamp"].dt.day
    df["Month"] = df["Timestamp"].dt.month
    df["Hour"] = df["Timestamp"].dt.hour
    df["Day_of_Week"] = df["Timestamp"].dt.day_name()
    return df


def validate_and_clean_data(df):
    """
    Performs comprehensive structural, numerical, and categorical validation checks.
    Returns the cleaned DataFrame along with a detailed quality summary report dictionary.
    """
    quality_report = {}
    
    # 1. Structural Checks
    quality_report["initial_shape"] = df.shape
    quality_report["columns"] = list(df.columns)
    quality_report["missing_values"] = df.isnull().sum().to_dict()
    quality_report["duplicate_rows"] = int(df.duplicated().sum())
    
    # 2. Numerical Range Validation
    # Expected ranges:
    # Soil_Moisture: 0% to 100%
    # Temperature: -10°C to 60°C
    # Humidity: 0% to 100%
    # Rainfall: >= 0 mm
    invalid_moisture = df[(df["Soil_Moisture"] < 0) | (df["Soil_Moisture"] > 100)]
    invalid_temp = df[(df["Temperature"] < -10) | (df["Temperature"] > 60)]
    invalid_humidity = df[(df["Humidity"] < 0) | (df["Humidity"] > 100)]
    invalid_rainfall = df[df["Rainfall"] < 0]
    
    quality_report["invalid_numerical_counts"] = {
        "Soil_Moisture": len(invalid_moisture),
        "Temperature": len(invalid_temp),
        "Humidity": len(invalid_humidity),
        "Rainfall": len(invalid_rainfall)
    }
    
    # 3. Categorical Validation
    expected_crop_stages = {"Vegetative", "Flowering", "Maturity"}
    expected_irrigation = {"Irrigated", "Not Irrigated"}
    expected_outcomes = {"Optimal", "Moderate", "Stressed"}
    
    actual_crop_stages = set(df["Crop_Stage"].unique())
    actual_irrigation = set(df["Irrigation_Status"].unique())
    actual_outcomes = set(df["Crop_Outcome"].unique())
    
    quality_report["categorical_validation"] = {
        "Crop_Stage_Valid": actual_crop_stages.issubset(expected_crop_stages),
        "Crop_Stage_Values": list(actual_crop_stages),
        "Irrigation_Status_Valid": actual_irrigation.issubset(expected_irrigation),
        "Irrigation_Status_Values": list(actual_irrigation),
        "Crop_Outcome_Valid": actual_outcomes.issubset(expected_outcomes),
        "Crop_Outcome_Values": list(actual_outcomes)
    }
    
    # 4. Cleaning / Corrections if any anomalies exist
    cleaned_df = df.copy()
    if quality_report["duplicate_rows"] > 0:
        cleaned_df = cleaned_df.drop_duplicates()
        
    cleaned_df = add_time_features(cleaned_df)
    quality_report["final_shape"] = cleaned_df.shape
    
    return cleaned_df, quality_report


if __name__ == "__main__":
    df = load_dataset()
    cleaned_df, report = validate_and_clean_data(df)
    print("=== DATA QUALITY REPORT ===")
    for k, v in report.items():
        print(f"{k}: {v}")
