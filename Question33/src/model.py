"""
Module: model.py
Implements the Decision Tree Machine Learning workflow:
1. Derives the smart agronomic target (Irrigation_Recommendation)
2. Performs stratified train/test split and feature encoding (without data leakage)
3. Trains a regularized DecisionTreeClassifier
4. Evaluates performance (Accuracy, Precision, Recall, F1, Confusion Matrix)
5. Extracts feature importances
6. Generates decision tree structure visualization
7. Saves the trained model pipeline with joblib
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def create_smart_target(df):
    """
    Derives the smart irrigation requirement target based on stage-specific
    moisture depletion thresholds and rainfall avoidance.
    
    Target: Irrigation_Recommendation (1: Irrigate, 0: Do Not Irrigate)
    - Vegetative: Needed when Soil_Moisture < 23.0% and Rainfall < 3.0 mm
    - Flowering: Needed when Soil_Moisture < 27.0% and Rainfall < 3.0 mm (high sensitivity)
    - Maturity: Needed when Soil_Moisture < 20.0% and Rainfall < 3.0 mm
    """
    df = df.copy()
    
    cond_veg = (df["Crop_Stage"] == "Vegetative") & (df["Soil_Moisture"] < 23.0) & (df["Rainfall"] < 3.0)
    cond_flow = (df["Crop_Stage"] == "Flowering") & (df["Soil_Moisture"] < 27.0) & (df["Rainfall"] < 3.0)
    cond_mat = (df["Crop_Stage"] == "Maturity") & (df["Soil_Moisture"] < 20.0) & (df["Rainfall"] < 3.0)
    
    df["Irrigation_Recommendation"] = np.where(cond_veg | cond_flow | cond_mat, 1, 0)
    return df


def prepare_features(df):
    """
    Encodes features and separates predictive variables from the target.
    Explicitly excludes Crop_Outcome, Irrigation_Status, and Farm_ID to prevent data leakage.
    """
    feature_df = df.copy()
    
    # One-hot encode Crop_Stage
    crop_stage_dummies = pd.get_dummies(feature_df["Crop_Stage"], prefix="Stage", dtype=int)
    
    # Feature columns
    feature_cols = ["Soil_Moisture", "Temperature", "Humidity", "Rainfall", "Hour"]
    X = pd.concat([feature_df[feature_cols], crop_stage_dummies], axis=1)
    y = feature_df["Irrigation_Recommendation"]
    
    return X, y, list(X.columns)


def train_and_evaluate_model(df, random_state=42):
    """
    Trains DecisionTreeClassifier and evaluates all key classification metrics.
    """
    df_with_target = create_smart_target(df)
    X, y, feature_names = prepare_features(df_with_target)
    
    # Stratified Train/Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=random_state, stratify=y
    )
    
    # Initialize and fit DecisionTreeClassifier with regularization to avoid overfitting
    model = DecisionTreeClassifier(
        criterion="gini",
        max_depth=4,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=random_state
    )
    model.fit(X_train, y_train)
    
    # Predict on Test Set
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Compute Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Do Not Irrigate (0)", "Irrigate (1)"])
    
    # Feature Importances
    importances = pd.Series(model.feature_importances_, index=feature_names).sort_values(ascending=False)
    
    results = {
        "model": model,
        "feature_names": feature_names,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "y_pred": y_pred,
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importances": importances,
        "df_with_target": df_with_target
    }
    
    return results


def plot_decision_tree_structure(model, feature_names, output_path="visualizations/decision_tree_structure.png"):
    """
    Renders and exports a high-resolution visualization of the decision tree rules.
    """
    plt.figure(figsize=(18, 10), dpi=300)
    plot_tree(
        model,
        feature_names=feature_names,
        class_names=["Do Not Irrigate", "Irrigate"],
        filled=True,
        rounded=True,
        fontsize=10,
        proportion=False,
        precision=2
    )
    plt.title("Intelligent Irrigation Decision Tree Structure (Rules & Thresholds)", fontsize=16, pad=15)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def save_model(model_artifacts, output_path="model/decision_tree_model.pkl"):
    """
    Persists the trained model and feature metadata using joblib.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib_payload = {
        "model": model_artifacts["model"],
        "feature_names": model_artifacts["feature_names"],
        "metrics": {
            "accuracy": model_artifacts["accuracy"],
            "precision": model_artifacts["precision"],
            "recall": model_artifacts["recall"],
            "f1_score": model_artifacts["f1_score"]
        }
    }
    joblib.dump(joblib_payload, output_path)
    print(f"Model successfully saved to {output_path}")


def run_full_ml_pipeline(df):
    """
    Executes the entire model training, evaluation, plotting, and persistence workflow.
    """
    print("Running Machine Learning Pipeline...")
    results = train_and_evaluate_model(df)
    
    print("\n--- MODEL PERFORMANCE METRICS ---")
    print(f"Accuracy:  {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    print(f"F1-Score:  {results['f1_score']:.4f}")
    print("\nConfusion Matrix:")
    print(results["confusion_matrix"])
    print("\nClassification Report:\n", results["classification_report"])
    print("\nFeature Importances:\n", results["feature_importances"])
    
    # Plot Tree
    plot_decision_tree_structure(results["model"], results["feature_names"])
    
    # Save Model
    save_model(results)
    
    return results


if __name__ == "__main__":
    from data_cleaning import load_dataset, validate_and_clean_data
    df = load_dataset()
    cleaned_df, _ = validate_and_clean_data(df)
    run_full_ml_pipeline(cleaned_df)
