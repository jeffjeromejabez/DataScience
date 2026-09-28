"""
Data Cleaning and Validation Module for DS_Day01_35
Performs structural validation, missing value detection, duplicate checks,
data type checking, categorical consistency, and numerical range verification.
"""

import pandas as pd
import numpy as np


class DataCleaner:
    """
    Performs data cleaning, validation, and structural checks on the e-commerce dataset.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.raw_df = None
        self.cleaned_df = None
        self.validation_report = {}

    def load_data(self):
        """Loads dataset from Excel or CSV file."""
        if self.filepath.endswith(".xlsx") or self.filepath.endswith(".xls"):
            self.raw_df = pd.read_excel(self.filepath, engine="openpyxl")
        else:
            self.raw_df = pd.read_csv(self.filepath)
        self.cleaned_df = self.raw_df.copy()
        return self.raw_df

    def validate_structure(self):
        """Checks rows, columns, names, and types."""
        expected_columns = [
            "Customer_ID",
            "Product_ID",
            "Product_Category",
            "Purchase_History",
            "Rating",
            "Browsing_Behaviour",
        ]
        
        actual_columns = list(self.cleaned_df.columns)
        missing_cols = [c for c in expected_columns if c not in actual_columns]
        
        self.validation_report["shape"] = self.cleaned_df.shape
        self.validation_report["columns"] = actual_columns
        self.validation_report["expected_columns_present"] = (len(missing_cols) == 0)
        self.validation_report["missing_expected_columns"] = missing_cols
        self.validation_report["dtypes"] = {col: str(dtype) for col, dtype in self.cleaned_df.dtypes.items()}
        
        return self.validation_report

    def check_missing_and_duplicates(self):
        """Calculates missing values and duplicate rows."""
        missing_counts = self.cleaned_df.isnull().sum().to_dict()
        duplicate_count = int(self.cleaned_df.duplicated().sum())
        
        # Check customer-product pair uniqueness
        cust_prod_duplicates = int(self.cleaned_df.duplicated(subset=["Customer_ID", "Product_ID"]).sum())
        
        self.validation_report["missing_values"] = missing_counts
        self.validation_report["duplicate_rows"] = duplicate_count
        self.validation_report["customer_product_duplicates"] = cust_prod_duplicates
        
        return {
            "missing_values": missing_counts,
            "duplicate_rows": duplicate_count,
            "cust_prod_duplicates": cust_prod_duplicates
        }

    def validate_categoricals(self):
        """Validates categorical columns for consistency."""
        cat_summary = {}
        for col in ["Customer_ID", "Product_ID", "Product_Category"]:
            if col in self.cleaned_df.columns:
                unique_vals = self.cleaned_df[col].dropna().unique()
                cat_summary[col] = {
                    "num_unique": len(unique_vals),
                    "sample_values": list(unique_vals[:5]),
                    "has_empty_strings": bool((self.cleaned_df[col].astype(str).str.strip() == "").sum() > 0)
                }
        self.validation_report["categorical_validation"] = cat_summary
        return cat_summary

    def validate_numericals(self):
        """Checks numerical ranges for Rating, Purchase_History, and Browsing_Behaviour."""
        num_summary = {}
        
        # Rating check (1 to 5)
        if "Rating" in self.cleaned_df.columns:
            invalid_ratings = self.cleaned_df[(self.cleaned_df["Rating"] < 1) | (self.cleaned_df["Rating"] > 5)]
            num_summary["Rating"] = {
                "min": float(self.cleaned_df["Rating"].min()),
                "max": float(self.cleaned_df["Rating"].max()),
                "invalid_count": len(invalid_ratings)
            }
            
        # Purchase_History check (>= 0)
        if "Purchase_History" in self.cleaned_df.columns:
            invalid_purchases = self.cleaned_df[self.cleaned_df["Purchase_History"] < 0]
            num_summary["Purchase_History"] = {
                "min": float(self.cleaned_df["Purchase_History"].min()),
                "max": float(self.cleaned_df["Purchase_History"].max()),
                "invalid_count": len(invalid_purchases)
            }
            
        # Browsing_Behaviour check (>= 0)
        if "Browsing_Behaviour" in self.cleaned_df.columns:
            invalid_browsing = self.cleaned_df[self.cleaned_df["Browsing_Behaviour"] < 0]
            num_summary["Browsing_Behaviour"] = {
                "min": float(self.cleaned_df["Browsing_Behaviour"].min()),
                "max": float(self.cleaned_df["Browsing_Behaviour"].max()),
                "invalid_count": len(invalid_browsing)
            }
            
        self.validation_report["numerical_validation"] = num_summary
        return num_summary

    def clean_and_validate(self):
        """Runs the full cleaning pipeline and returns validated dataframe & report."""
        self.load_data()
        self.validate_structure()
        self.check_missing_and_duplicates()
        self.validate_categoricals()
        self.validate_numericals()
        
        # Handle duplicates if present (drop exact duplicates preserving first)
        if self.validation_report["duplicate_rows"] > 0:
            self.cleaned_df = self.cleaned_df.drop_duplicates().reset_index(drop=True)
            print(f"Removed {self.validation_report['duplicate_rows']} duplicate records.")
            
        return self.cleaned_df, self.validation_report


if __name__ == "__main__":
    cleaner = DataCleaner("data/ecommerce_dataset.xlsx")
    df, report = cleaner.clean_and_validate()
    print("Data Cleaning Report Summary:")
    print(f"- Shape: {report['shape']}")
    print(f"- Missing Values: {report['missing_values']}")
    print(f"- Duplicate Records: {report['duplicate_rows']}")
    print(f"- Columns Validated: {report['columns']}")
