"""
Exploratory Data Analysis and Visualization Module for DS_Day01_35
Generates descriptive statistics across customer, product, and category dimensions,
and renders the primary visualizations with high-aesthetic design.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 12


class EcommerceEDA:
    """
    Performs Exploratory Data Analysis and generates visualizations.
    """

    def __init__(self, df, output_dir="visualizations"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def compute_descriptive_stats(self):
        """Calculates comprehensive descriptive statistics for numerical variables."""
        num_cols = ["Purchase_History", "Rating", "Browsing_Behaviour"]
        stats = self.df[num_cols].describe().T
        stats["median"] = self.df[num_cols].median()
        stats["skewness"] = self.df[num_cols].skew()
        return stats

    def compute_customer_metrics(self):
        """Analyzes customer-level purchase and engagement patterns."""
        cust_summary = self.df.groupby("Customer_ID").agg(
            total_purchases=("Purchase_History", "sum"),
            unique_products=("Product_ID", "nunique"),
            unique_categories=("Product_Category", "nunique"),
            avg_rating=("Rating", "mean"),
            total_browsing=("Browsing_Behaviour", "sum"),
            avg_browsing=("Browsing_Behaviour", "mean")
        ).reset_index()
        return cust_summary

    def compute_product_metrics(self):
        """Analyzes product-level demand, popularity, and satisfaction."""
        prod_summary = self.df.groupby(["Product_ID", "Product_Category"]).agg(
            customer_reach=("Customer_ID", "nunique"),
            total_purchase_volume=("Purchase_History", "sum"),
            avg_rating=("Rating", "mean"),
            avg_browsing_time=("Browsing_Behaviour", "mean")
        ).reset_index().sort_values(by="total_purchase_volume", ascending=False)
        return prod_summary

    def compute_category_metrics(self):
        """Analyzes category-level volume, reach, and rating averages."""
        cat_summary = self.df.groupby("Product_Category").agg(
            total_orders=("Purchase_History", "sum"),
            transaction_records=("Customer_ID", "count"),
            unique_customers=("Customer_ID", "nunique"),
            unique_products=("Product_ID", "nunique"),
            avg_rating=("Rating", "mean"),
            avg_browsing_mins=("Browsing_Behaviour", "mean")
        ).reset_index().sort_values(by="total_orders", ascending=False)
        return cat_summary

    def plot_01_category_popularity(self):
        """
        Visualization 1: Top Product Categories by Purchase Volume & Transaction Reach.
        Saved to visualizations/01_category_popularity.png
        """
        cat_metrics = self.compute_category_metrics()
        
        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        
        # Color palette
        colors = sns.color_palette("mako", len(cat_metrics))
        
        bars = ax.barh(
            cat_metrics["Product_Category"],
            cat_metrics["total_orders"],
            color=colors,
            edgecolor="none",
            height=0.65
        )
        
        ax.invert_yaxis()  # Highest volume on top
        ax.set_title("Total Purchase Volume by Product Category", fontsize=15, fontweight="bold", pad=15)
        ax.set_xlabel("Total Units Purchased (Purchase History)", fontsize=12, labelpad=10)
        ax.set_ylabel("Product Category", fontsize=12, labelpad=10)
        
        # Add data labels with volume and unique customer reach
        for bar, (_, row) in zip(bars, cat_metrics.iterrows()):
            width = bar.get_width()
            ax.text(
                width + 15,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width):,} units ({row['unique_customers']} customers, {row['avg_rating']:.2f}★)",
                ha="left",
                va="center",
                fontsize=9.5,
                fontweight="semibold",
                color="#2c3e50"
            )
            
        ax.set_xlim(0, max(cat_metrics["total_orders"]) * 1.35)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, "01_category_popularity.png")
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        print(f"Saved: {filepath}")
        return filepath

    def plot_02_product_popularity(self):
        """
        Visualization 2: Top Most Frequently Purchased Products.
        Saved to visualizations/02_product_popularity.png
        """
        prod_metrics = self.compute_product_metrics().head(12)
        
        fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
        
        colors = sns.color_palette("viridis", len(prod_metrics))
        
        y_labels = [f"{pid} ({cat[:15]})" for pid, cat in zip(prod_metrics["Product_ID"], prod_metrics["Product_Category"])]
        
        bars = ax.barh(
            y_labels,
            prod_metrics["total_purchase_volume"],
            color=colors,
            edgecolor="none",
            height=0.68
        )
        
        ax.invert_yaxis()
        ax.set_title("Top 12 Most Frequently Purchased Products Across All Customers", fontsize=15, fontweight="bold", pad=15)
        ax.set_xlabel("Total Purchased Quantity", fontsize=12, labelpad=10)
        ax.set_ylabel("Product ID & Category", fontsize=12, labelpad=10)
        
        for bar, (_, row) in zip(bars, prod_metrics.iterrows()):
            width = bar.get_width()
            ax.text(
                width + 5,
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)} units (Avg Rating: {row['avg_rating']:.2f}★ | Reach: {row['customer_reach']} cust)",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="semibold",
                color="#1a252f"
            )
            
        ax.set_xlim(0, max(prod_metrics["total_purchase_volume"]) * 1.35)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, "02_product_popularity.png")
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        print(f"Saved: {filepath}")
        return filepath

    def plot_03_customer_behavior(self):
        """
        Visualization 3: Browsing Engagement vs. Purchase Frequency by Rating Tier.
        Saved to visualizations/03_customer_behavior.png
        """
        fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
        
        # Create rating tier for intuitive visual segmentation
        df_plot = self.df.copy()
        df_plot["Rating_Tier"] = pd.cut(
            df_plot["Rating"],
            bins=[0, 2, 3, 5],
            labels=["Low Rating (1-2★)", "Moderate Rating (3★)", "High Rating (4-5★)"]
        )
        
        palette = {"Low Rating (1-2★)": "#e74c3c", "Moderate Rating (3★)": "#f39c12", "High Rating (4-5★)": "#27ae60"}
        
        sns.scatterplot(
            data=df_plot,
            x="Browsing_Behaviour",
            y="Purchase_History",
            hue="Rating_Tier",
            palette=palette,
            alpha=0.65,
            s=60,
            edgecolor="w",
            linewidth=0.5,
            ax=ax
        )
        
        # Add trendline
        sns.regplot(
            data=df_plot,
            x="Browsing_Behaviour",
            y="Purchase_History",
            scatter=False,
            ax=ax,
            color="#2c3e50",
            line_kws={"linestyle": "--", "linewidth": 2, "label": "Overall Trend"}
        )
        
        corr_val = self.df["Browsing_Behaviour"].corr(self.df["Purchase_History"])
        
        ax.set_title(f"Customer Browsing Behavior vs. Purchase Frequency (Correlation: +{corr_val:.2f})", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Browsing Engagement Time (Minutes)", fontsize=12, labelpad=10)
        ax.set_ylabel("Purchase Frequency / Volume", fontsize=12, labelpad=10)
        
        ax.legend(title="Customer Rating Tier", loc="upper left", frameon=True, facecolor="white", framealpha=0.9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, "03_customer_behavior.png")
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        print(f"Saved: {filepath}")
        return filepath


if __name__ == "__main__":
    from data_cleaning import DataCleaner
    cleaner = DataCleaner("data/ecommerce_dataset.xlsx")
    df, _ = cleaner.clean_and_validate()
    eda = EcommerceEDA(df)
    eda.plot_01_category_popularity()
    eda.plot_02_product_popularity()
    eda.plot_03_customer_behavior()
