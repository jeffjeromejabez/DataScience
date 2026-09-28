"""
Association Rule Mining Module for DS_Day01_35
Extracts transaction baskets, applies Apriori algorithm via mlxtend,
computes Support, Confidence, and Lift, and plots the 4th primary visualization.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import apriori, association_rules


class AssociationRuleMiner:
    """
    Constructs market baskets and extracts association rules using the Apriori algorithm.
    """

    def __init__(self, df, output_dir="visualizations"):
        self.df = df
        self.output_dir = output_dir
        self.basket_df = None
        self.frequent_itemsets = None
        self.rules_df = None
        os.makedirs(self.output_dir, exist_ok=True)

    def build_transaction_baskets(self):
        """
        Transforms customer interaction records into a one-hot encoded transaction matrix.
        Rows = Customer_ID, Columns = Product_ID (1 if purchased, 0 otherwise).
        """
        basket = (
            self.df.groupby(["Customer_ID", "Product_ID"])["Purchase_History"]
            .sum()
            .unstack()
            .reset_index()
            .fillna(0)
            .set_index("Customer_ID")
        )
        
        # Convert quantities to boolean 1/0
        self.basket_df = (basket > 0).astype(bool)
        return self.basket_df

    def mine_frequent_itemsets(self, min_support=0.03):
        """
        Extracts frequent itemsets using the Apriori algorithm.
        """
        if self.basket_df is None:
            self.build_transaction_baskets()
            
        self.frequent_itemsets = apriori(
            self.basket_df,
            min_support=min_support,
            use_colnames=True
        )
        
        # Add itemset length column
        self.frequent_itemsets["length"] = self.frequent_itemsets["itemsets"].apply(lambda x: len(x))
        self.frequent_itemsets = self.frequent_itemsets.sort_values(by="support", ascending=False).reset_index(drop=True)
        return self.frequent_itemsets

    def generate_rules(self, metric="confidence", min_threshold=0.20, min_lift=1.1):
        """
        Generates association rules from frequent itemsets and filters by minimum lift.
        """
        if self.frequent_itemsets is None:
            self.mine_frequent_itemsets()
            
        rules = association_rules(
            self.frequent_itemsets,
            metric=metric,
            min_threshold=min_threshold
        )
        
        # Filter rules by positive association (lift > min_lift)
        rules = rules[rules["lift"] >= min_lift].copy()
        
        # Create readable string representations for antecedents and consequents
        rules["antecedent_str"] = rules["antecedents"].apply(lambda x: ", ".join(list(x)))
        rules["consequent_str"] = rules["consequents"].apply(lambda x: ", ".join(list(x)))
        rules["rule_str"] = rules["antecedent_str"] + " -> " + rules["consequent_str"]
        
        # Sort by lift descending
        self.rules_df = rules.sort_values(by="lift", ascending=False).reset_index(drop=True)
        return self.rules_df

    def format_rules_table(self, top_n=10):
        """
        Formats association rules into a clean business presentation table.
        """
        if self.rules_df is None:
            self.generate_rules()
            
        top_rules = self.rules_df.head(top_n).copy()
        
        formatted = pd.DataFrame({
            "Rule": top_rules["rule_str"],
            "Antecedents (Product A)": top_rules["antecedent_str"],
            "Consequents (Recommended B)": top_rules["consequent_str"],
            "Support": top_rules["support"].apply(lambda x: f"{x:.3f} ({x*100:.1f}%)"),
            "Confidence": top_rules["confidence"].apply(lambda x: f"{x:.3f} ({x*100:.1f}%)"),
            "Lift": top_rules["lift"].apply(lambda x: f"{x:.3f}"),
            "Conviction": top_rules["conviction"].apply(lambda x: f"{x:.2f}" if not np.isinf(x) else "Inf")
        })
        return formatted

    def plot_04_association_rules(self, top_n_annotate=6):
        """
        Visualization 4: Association Rules Scatter Plot (Support vs. Confidence colored by Lift).
        Saved to visualizations/04_association_rules.png
        """
        if self.rules_df is None or len(self.rules_df) == 0:
            self.generate_rules()
            
        fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
        
        scatter = ax.scatter(
            self.rules_df["support"],
            self.rules_df["confidence"],
            c=self.rules_df["lift"],
            cmap="plasma",
            s=self.rules_df["lift"] * 45,
            alpha=0.85,
            edgecolors="black",
            linewidth=0.8
        )
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Lift Metric (Association Strength)", fontsize=11, labelpad=10)
        
        # Annotate top rules
        top_rules = self.rules_df.head(top_n_annotate)
        for _, row in top_rules.iterrows():
            ax.annotate(
                row["rule_str"],
                xy=(row["support"], row["confidence"]),
                xytext=(row["support"] + 0.003, row["confidence"] + 0.015),
                fontsize=8.5,
                fontweight="bold",
                color="#1a252f",
                arrowprops=dict(arrowstyle="->", color="#e74c3c", lw=1.0)
            )
            
        ax.set_title("Product Association Rules: Support vs. Confidence (Size & Hue = Lift)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Support (Proportion of All Transactions Containing Both Items)", fontsize=12, labelpad=10)
        ax.set_ylabel("Confidence (Probability of Consequent Given Antecedent)", fontsize=12, labelpad=10)
        
        ax.axhline(0.5, color="gray", linestyle=":", alpha=0.6, label="50% Confidence Threshold")
        ax.legend(loc="lower right", frameon=True, facecolor="white", framealpha=0.9)
        
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, "04_association_rules.png")
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        print(f"Saved: {filepath}")
        return filepath


def run_association_rules(df, min_support=0.04, min_threshold=0.30, min_lift=1.2, max_len=2):
    """
    Convenience function to mine association rules from dataframe and return clean rules DataFrame.
    Filters to max_len antecedents/consequents for high quality, interpretable product associations.
    """
    miner = AssociationRuleMiner(df)
    miner.build_transaction_baskets()
    miner.mine_frequent_itemsets(min_support=min_support)
    rules_df = miner.generate_rules(min_threshold=min_threshold, min_lift=min_lift)
    
    if max_len is not None and len(rules_df) > 0:
        rules_df = rules_df[
            (rules_df["antecedents"].apply(len) <= max_len) &
            (rules_df["consequents"].apply(len) == 1)
        ].reset_index(drop=True)
        
    return rules_df


if __name__ == "__main__":
    from data_cleaning import DataCleaner
    cleaner = DataCleaner("data/ecommerce_dataset.xlsx")
    df, _ = cleaner.clean_and_validate()
    miner = AssociationRuleMiner(df)
    miner.build_transaction_baskets()
    frequent = miner.mine_frequent_itemsets(min_support=0.03)
    rules = miner.generate_rules(min_threshold=0.25, min_lift=1.2)
    miner.plot_04_association_rules()
    print("Top Association Rules Found:")
    print(miner.format_rules_table(top_n=5))
