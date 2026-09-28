"""
Module: visualization.py
Generates the FOUR primary challenge visualizations and the Decision Tree diagram.
Saves high-resolution publication-quality PNG charts in visualizations/.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def set_custom_style():
    """
    Sets clean, modern aesthetic styling for all plots.
    """
    sns.set_theme(style="whitegrid", font="sans-serif")
    plt.rcParams.update({
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 11,
        "figure.titlesize": 15,
        "figure.autolayout": True,
        "lines.linewidth": 2.0
    })


def plot_soil_moisture_trend(df, output_path="visualizations/01_soil_moisture_trend.png"):
    """
    Visualization 1: Soil Moisture Trend over Time
    Displays daily average moisture across all farms with crop stage boundaries and stress zone.
    """
    set_custom_style()
    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    
    # Aggregate by date
    daily_stats = df.groupby("Date")["Soil_Moisture"].agg(["mean", "std", "min", "max"]).reset_index()
    daily_stats["Date_Str"] = pd.to_datetime(daily_stats["Date"])
    
    # Plot mean and variation band
    ax.plot(daily_stats["Date_Str"], daily_stats["mean"], color="#1b7837", label="Daily Mean Soil Moisture (%)", linewidth=2.5)
    ax.fill_between(
        daily_stats["Date_Str"],
        daily_stats["mean"] - daily_stats["std"],
        daily_stats["mean"] + daily_stats["std"],
        color="#a6dba0",
        alpha=0.45,
        label="±1 Std Deviation Range"
    )
    
    # Stage Boundaries
    stage_dates = df.groupby("Crop_Stage")["Timestamp"].agg(["min", "max"]).reset_index()
    
    # Mark critical stress zone (< 24%)
    ax.axhline(24.0, color="#d73027", linestyle="--", linewidth=1.8, label="Flowering Stress Threshold (24%)")
    ax.axhline(30.0, color="#4575b4", linestyle=":", linewidth=1.5, label="Adequate Moisture Level (30%)")
    
    # Stage shaded regions
    veg_end = pd.to_datetime(df[df["Crop_Stage"] == "Vegetative"]["Timestamp"].max())
    flow_end = pd.to_datetime(df[df["Crop_Stage"] == "Flowering"]["Timestamp"].max())
    mat_end = pd.to_datetime(df[df["Crop_Stage"] == "Maturity"]["Timestamp"].max())
    start = pd.to_datetime(df["Timestamp"].min())
    
    ax.axvspan(start, veg_end, color="#f7fcf5", alpha=0.6)
    ax.axvspan(veg_end, flow_end, color="#fff5f0", alpha=0.6)
    ax.axvspan(flow_end, mat_end, color="#f7f7f7", alpha=0.6)
    
    # Add Stage Labels
    ax.text(start + (veg_end - start)/2, 44, "Vegetative Stage", ha="center", fontweight="bold", color="#2ca25f", fontsize=11)
    ax.text(veg_end + (flow_end - veg_end)/2, 44, "Flowering Stage (High Water Demand)", ha="center", fontweight="bold", color="#cb181d", fontsize=11)
    ax.text(flow_end + (mat_end - flow_end)/2, 44, "Maturity Stage", ha="center", fontweight="bold", color="#636363", fontsize=11)
    
    ax.set_title("Primary Visualization 1: Soil Moisture Trend Across 90-Day Growing Season", pad=15)
    ax.set_xlabel("Observation Date")
    ax.set_ylabel("Soil Moisture (%)")
    ax.set_ylim(8, 48)
    ax.legend(loc="lower left", frameon=True, facecolor="white", framealpha=0.9)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_rainfall_vs_soil_moisture(df, output_path="visualizations/02_rainfall_vs_soil_moisture.png"):
    """
    Visualization 2: Rainfall vs Soil Moisture
    Scatter and density plot highlighting moisture recharge and crop outcomes under different rain levels.
    """
    set_custom_style()
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    
    palette = {"Optimal": "#2ca25f", "Moderate": "#2b8cbe", "Stressed": "#e34a33"}
    
    sns.scatterplot(
        data=df,
        x="Rainfall",
        y="Soil_Moisture",
        hue="Crop_Outcome",
        palette=palette,
        style="Crop_Stage",
        alpha=0.75,
        s=60,
        ax=ax
    )
    
    # Add annotations and threshold guidelines
    ax.axhline(24.0, color="#d73027", linestyle="--", alpha=0.7, label="Critical Moisture Threshold (24%)")
    ax.axvline(5.0, color="#3182bd", linestyle=":", alpha=0.8, label="Significant Rainfall Cutoff (5 mm)")
    
    ax.set_title("Primary Visualization 2: Rainfall vs. Soil Moisture by Crop Outcome & Stage", pad=15)
    ax.set_xlabel("Rainfall (mm)")
    ax.set_ylabel("Soil Moisture (%)")
    ax.set_xlim(-0.5, df["Rainfall"].max() + 1.5)
    ax.set_ylim(8, 48)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0.0)
    
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_irrigation_analysis(df, output_path="visualizations/03_irrigation_analysis.png"):
    """
    Visualization 3: Irrigation vs Soil Moisture & Rainfall
    Evaluates historical calendar irrigation events against actual moisture levels,
    illustrating potentially unnecessary irrigation events.
    """
    set_custom_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Subplot A: Soil Moisture distribution by Irrigation Status
    palette_irr = {"Not Irrigated": "#74a9cf", "Irrigated": "#fdae6b"}
    sns.boxplot(
        data=df,
        x="Irrigation_Status",
        y="Soil_Moisture",
        palette=palette_irr,
        ax=ax1,
        width=0.45,
        boxprops=dict(alpha=0.85)
    )
    sns.stripplot(
        data=df.sample(min(400, len(df)), random_state=42),
        x="Irrigation_Status",
        y="Soil_Moisture",
        color="black",
        alpha=0.2,
        jitter=0.2,
        size=4,
        ax=ax1
    )
    ax1.axhline(30.0, color="#d95f02", linestyle="--", linewidth=1.5, label="Adequate Soil Moisture (>=30%)")
    ax1.set_title("(A) Soil Moisture Distribution by Irrigation Status", pad=10)
    ax1.set_xlabel("Irrigation Status")
    ax1.set_ylabel("Soil Moisture (%)")
    ax1.legend(loc="lower right")
    
    # Subplot B: Potentially unnecessary irrigation breakdown by Crop Stage
    irr_df = df[df["Irrigation_Status"] == "Irrigated"].copy()
    irr_df["Irrigation_Category"] = np.where(
        (irr_df["Soil_Moisture"] >= 30.0) | (irr_df["Rainfall"] >= 3.0),
        "Potentially Unnecessary",
        "Justified (Moisture Deficit)"
    )
    
    category_counts = irr_df.groupby(["Crop_Stage", "Irrigation_Category"]).size().unstack(fill_value=0)
    category_counts.plot(
        kind="bar",
        stacked=True,
        color={"Potentially Unnecessary": "#fc8d62", "Justified (Moisture Deficit)": "#66c2a5"},
        ax=ax2,
        width=0.55,
        edgecolor="black",
        linewidth=0.8
    )
    ax2.set_title("(B) Calendar Irrigation Breakdown: Justified vs Potentially Unnecessary", pad=10)
    ax2.set_xlabel("Crop Stage")
    ax2.set_ylabel("Number of Irrigation Events")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)
    ax2.legend(title="Irrigation Evaluation", loc="upper right")
    
    plt.suptitle("Primary Visualization 3: Analysis of Fixed-Schedule Irrigation Practices", y=1.02, fontsize=15, fontweight="bold")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_crop_stage_outcome(df, output_path="visualizations/04_crop_stage_outcome.png"):
    """
    Visualization 4: Crop Stage, Irrigation, and Crop Outcome
    Visualizes health outcomes across crop stages and irrigation states.
    """
    set_custom_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    outcome_palette = {"Optimal": "#2ca25f", "Moderate": "#43a2ca", "Stressed": "#de2d26"}
    
    # Subplot A: Crop Outcome proportion by Crop Stage
    stage_outcome = pd.crosstab(df["Crop_Stage"], df["Crop_Outcome"], normalize="index") * 100
    stage_outcome = stage_outcome[["Optimal", "Moderate", "Stressed"]]
    stage_outcome.plot(
        kind="bar",
        stacked=True,
        color=outcome_palette,
        ax=ax1,
        width=0.5,
        edgecolor="black",
        linewidth=0.8
    )
    ax1.set_title("(A) Crop Outcome Distribution Across Crop Stages", pad=10)
    ax1.set_xlabel("Crop Stage")
    ax1.set_ylabel("Percentage of Observations (%)")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
    ax1.set_ylim(0, 105)
    ax1.legend(title="Crop Outcome", loc="upper right")
    
    # Subplot B: Average Soil Moisture across Stages by Outcome
    sns.barplot(
        data=df,
        x="Crop_Stage",
        y="Soil_Moisture",
        hue="Crop_Outcome",
        palette=outcome_palette,
        ax=ax2,
        capsize=0.08,
        err_kws={"linewidth": 1.2},
        edgecolor="black",
        linewidth=0.8
    )
    ax2.set_title("(B) Mean Soil Moisture by Crop Stage & Crop Outcome", pad=10)
    ax2.set_xlabel("Crop Stage")
    ax2.set_ylabel("Mean Soil Moisture (%)")
    ax2.legend(title="Crop Outcome", loc="lower right")
    
    plt.suptitle("Primary Visualization 4: Crop Stage Vulnerability and Outcome Relationships", y=1.02, fontsize=15, fontweight="bold")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_visualizations(df):
    """
    Executes and generates all four primary visualizations.
    """
    print("Generating Primary Visualizations...")
    plot_soil_moisture_trend(df)
    plot_rainfall_vs_soil_moisture(df)
    plot_irrigation_analysis(df)
    plot_crop_stage_outcome(df)
    print("All 4 Primary Visualizations created successfully.")


if __name__ == "__main__":
    from data_cleaning import load_dataset, validate_and_clean_data
    df = load_dataset()
    cleaned_df, _ = validate_and_clean_data(df)
    generate_all_visualizations(cleaned_df)
