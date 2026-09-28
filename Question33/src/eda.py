"""
Module: eda.py
Performs Exploratory Data Analysis, descriptive statistics, water stress analysis,
unnecessary irrigation quantification, and rainfall impact evaluation.
"""

import pandas as pd
import numpy as np


def calculate_descriptive_statistics(df):
    """
    Calculates detailed summary statistics for all numerical columns.
    """
    numerical_cols = ["Soil_Moisture", "Temperature", "Humidity", "Rainfall"]
    stats_df = df[numerical_cols].describe().T
    stats_df["median"] = df[numerical_cols].median()
    stats_df = stats_df.rename(columns={"50%": "median_dup"})
    stats_df = stats_df[["count", "mean", "std", "min", "25%", "median", "75%", "max"]]
    return stats_df.round(2)


def calculate_grouped_statistics(df):
    """
    Computes key grouped domain statistics.
    """
    grouped_results = {}
    
    # 1. Average Soil Moisture by Crop Stage
    grouped_results["moisture_by_stage"] = df.groupby("Crop_Stage")["Soil_Moisture"].agg(
        ["count", "mean", "median", "std", "min", "max"]
    ).round(2)
    
    # 2. Average Soil Moisture by Irrigation Status
    grouped_results["moisture_by_irrigation"] = df.groupby("Irrigation_Status")["Soil_Moisture"].agg(
        ["count", "mean", "median", "std"]
    ).round(2)
    
    # 3. Average Rainfall by Irrigation Status
    grouped_results["rainfall_by_irrigation"] = df.groupby("Irrigation_Status")["Rainfall"].agg(
        ["count", "mean", "median", "max"]
    ).round(2)
    
    # 4. Crop Outcome Distribution
    grouped_results["crop_outcome_dist"] = pd.DataFrame({
        "Count": df["Crop_Outcome"].value_counts(),
        "Percentage": (df["Crop_Outcome"].value_counts(normalize=True) * 100).round(2)
    })
    
    # 5. Irrigation Frequency by Farm
    grouped_results["irrigation_by_farm"] = df.groupby("Farm_ID")["Irrigation_Status"].apply(
        lambda s: (s == "Irrigated").sum()
    ).to_frame(name="Irrigation_Count")
    grouped_results["irrigation_by_farm"]["Total_Observations"] = df.groupby("Farm_ID").size()
    grouped_results["irrigation_by_farm"]["Irrigation_Rate_%"] = (
        (grouped_results["irrigation_by_farm"]["Irrigation_Count"] / grouped_results["irrigation_by_farm"]["Total_Observations"]) * 100
    ).round(2)
    
    # 6. Irrigation Frequency by Crop Stage
    grouped_results["irrigation_by_stage"] = df.groupby("Crop_Stage")["Irrigation_Status"].apply(
        lambda s: (s == "Irrigated").sum()
    ).to_frame(name="Irrigation_Count")
    grouped_results["irrigation_by_stage"]["Total_Observations"] = df.groupby("Crop_Stage").size()
    grouped_results["irrigation_by_stage"]["Irrigation_Rate_%"] = (
        (grouped_results["irrigation_by_stage"]["Irrigation_Count"] / grouped_results["irrigation_by_stage"]["Total_Observations"]) * 100
    ).round(2)
    
    return grouped_results


def analyze_water_stress(df):
    """
    Analyzes environmental and soil conditions associated with Crop_Outcome == 'Stressed'.
    """
    stress_analysis = {}
    
    # Profile metrics across outcomes
    outcome_profile = df.groupby("Crop_Outcome")[["Soil_Moisture", "Temperature", "Humidity", "Rainfall"]].agg(
        ["mean", "median", "min", "max"]
    ).round(2)
    stress_analysis["outcome_profile"] = outcome_profile
    
    # Distribution of Stressed outcomes by Crop Stage
    stress_by_stage = df[df["Crop_Outcome"] == "Stressed"].groupby("Crop_Stage").size().to_frame(name="Stressed_Count")
    total_by_stage = df.groupby("Crop_Stage").size()
    stress_by_stage["Total_Records"] = total_by_stage
    stress_by_stage["Stress_Rate_%"] = ((stress_by_stage["Stressed_Count"] / stress_by_stage["Total_Records"]) * 100).round(2)
    stress_analysis["stress_by_stage"] = stress_by_stage
    
    # Environmental envelope of stressed state
    stressed_df = df[df["Crop_Outcome"] == "Stressed"]
    stress_analysis["summary"] = {
        "total_stressed_records": len(stressed_df),
        "percentage_of_all_records": round(len(stressed_df) / len(df) * 100, 2),
        "mean_soil_moisture": round(stressed_df["Soil_Moisture"].mean(), 2),
        "max_soil_moisture": round(stressed_df["Soil_Moisture"].max(), 2),
        "mean_temperature": round(stressed_df["Temperature"].mean(), 2),
        "mean_humidity": round(stressed_df["Humidity"].mean(), 2),
        "mean_rainfall": round(stressed_df["Rainfall"].mean(), 2)
    }
    
    return stress_analysis


def analyze_unnecessary_irrigation(df, moisture_threshold=30.0, rainfall_threshold=3.0):
    """
    Identifies and quantifies irrigation events that occurred under conditions
    suggesting water was already adequate (Soil Moisture >= threshold OR Rainfall >= threshold).
    """
    irr_df = df[df["Irrigation_Status"] == "Irrigated"].copy()
    
    # Criteria definition
    high_moisture_cond = irr_df["Soil_Moisture"] >= moisture_threshold
    rain_cond = irr_df["Rainfall"] >= rainfall_threshold
    
    unnecessary_mask = high_moisture_cond | rain_cond
    irr_df["Potentially_Unnecessary"] = unnecessary_mask
    
    total_irr_events = len(irr_df)
    unnecessary_events = int(unnecessary_mask.sum())
    unnecessary_pct = round((unnecessary_events / total_irr_events) * 100, 2)
    
    # Breakdown by reason
    high_moisture_only = int((high_moisture_cond & (~rain_cond)).sum())
    rain_only = int(((~high_moisture_cond) & rain_cond).sum())
    both_reasons = int((high_moisture_cond & rain_cond).sum())
    
    # Breakdown by Farm
    by_farm = irr_df.groupby("Farm_ID")["Potentially_Unnecessary"].agg(
        Total_Irrigations="count",
        Unnecessary_Irrigations="sum"
    )
    by_farm["Unnecessary_Rate_%"] = ((by_farm["Unnecessary_Irrigations"] / by_farm["Total_Irrigations"]) * 100).round(2)
    
    # Breakdown by Crop Stage
    by_stage = irr_df.groupby("Crop_Stage")["Potentially_Unnecessary"].agg(
        Total_Irrigations="count",
        Unnecessary_Irrigations="sum"
    )
    by_stage["Unnecessary_Rate_%"] = ((by_stage["Unnecessary_Irrigations"] / by_stage["Total_Irrigations"]) * 100).round(2)
    
    return {
        "total_irrigation_events": total_irr_events,
        "unnecessary_irrigation_events": unnecessary_events,
        "unnecessary_percentage": unnecessary_pct,
        "breakdown": {
            "high_moisture_alone": high_moisture_only,
            "rain_active_alone": rain_only,
            "both_high_moisture_and_rain": both_reasons
        },
        "by_farm": by_farm,
        "by_stage": by_stage
    }


def analyze_rainfall_impact(df):
    """
    Analyzes the quantitative impact of rainfall on soil moisture and irrigation scheduling.
    """
    df = df.copy()
    
    # Categorize rainfall
    def categorize_rain(r):
        if r == 0:
            return "No Rain (0 mm)"
        elif r <= 5.0:
            return "Light Rain (0.1 - 5.0 mm)"
        else:
            return "Moderate/Heavy Rain (> 5.0 mm)"
            
    df["Rainfall_Category"] = df["Rainfall"].apply(categorize_rain)
    
    rain_impact = df.groupby("Rainfall_Category").agg(
        Record_Count=("Soil_Moisture", "count"),
        Avg_Soil_Moisture=("Soil_Moisture", "mean"),
        Median_Soil_Moisture=("Soil_Moisture", "median"),
        Irrigation_Count=("Irrigation_Status", lambda s: (s == "Irrigated").sum())
    ).round(2)
    rain_impact["Irrigation_Rate_%"] = ((rain_impact["Irrigation_Count"] / rain_impact["Record_Count"]) * 100).round(2)
    
    return rain_impact


if __name__ == "__main__":
    from data_cleaning import load_dataset, validate_and_clean_data
    df = load_dataset()
    cleaned_df, _ = validate_and_clean_data(df)
    
    print("=== DESCRIPTIVE STATISTICS ===")
    print(calculate_descriptive_statistics(cleaned_df))
    
    print("\n=== GROUPED STATISTICS ===")
    grp = calculate_grouped_statistics(cleaned_df)
    print("Moisture by Crop Stage:\n", grp["moisture_by_stage"])
    
    print("\n=== WATER STRESS ANALYSIS ===")
    stress = analyze_water_stress(cleaned_df)
    print("Summary:", stress["summary"])
    print("Stress by Stage:\n", stress["stress_by_stage"])
    
    print("\n=== UNNECESSARY IRRIGATION ANALYSIS ===")
    unnec = analyze_unnecessary_irrigation(cleaned_df)
    print(f"Unnecessary Irrigation: {unnec['unnecessary_irrigation_events']} / {unnec['total_irrigation_events']} ({unnec['unnecessary_percentage']}%)")
    print("By Crop Stage:\n", unnec["by_stage"])
    
    print("\n=== RAINFALL IMPACT ===")
    print(analyze_rainfall_impact(cleaned_df))
