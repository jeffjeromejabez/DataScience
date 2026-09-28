"""
Model Training, Evaluation, and Serialization Module for DS_Day01_35
Implements leak-free Leave-One-Out holdout evaluation, computes Precision@K, Recall@K,
Hit Rate@K, and Catalog Coverage, and saves the final model with joblib.
"""

import os
import joblib
import numpy as np
import pandas as pd
from recommendation import KNNRecommender


class RecommendationEvaluator:
    """
    Evaluates recommendation models using a leak-free Leave-One-Out holdout strategy.
    """

    def __init__(self, df, random_state=42):
        self.df = df
        self.random_state = random_state
        self.train_df = None
        self.test_dict = {}  # Customer_ID -> set of held-out Product_IDs
        self.catalog = list(df["Product_ID"].unique())

    def split_holdout(self, min_items_per_cust=3):
        """
        Splits dataset by holding out 1 randomly selected item per customer for testing.
        Guarantees that test items are never seen during training or neighbor calculation.
        """
        np.random.seed(self.random_state)
        
        train_records = []
        test_records = {}
        
        # Group interactions by customer
        for cust_id, group in self.df.groupby("Customer_ID"):
            pids = list(group["Product_ID"].values)
            
            if len(pids) >= min_items_per_cust:
                # Select one product to hold out
                holdout_idx = np.random.choice(len(pids))
                holdout_pid = pids[holdout_idx]
                
                # Keep remaining records in train set
                train_group = group.iloc[[i for i in range(len(pids)) if i != holdout_idx]]
                train_records.append(train_group)
                
                test_records[cust_id] = {holdout_pid}
            else:
                train_records.append(group)
                
        self.train_df = pd.concat(train_records, ignore_index=True)
        self.test_dict = test_records
        
        print(f"Holdout Split Created:")
        print(f"  - Total Training Records: {len(self.train_df)}")
        print(f"  - Evaluated Customers with Held-out Ground Truth: {len(self.test_dict)}")
        return self.train_df, self.test_dict

    def evaluate_knn(self, k_neighbors=7, top_k_list=[3, 5, 10]):
        """
        Trains KNN on training data and computes Precision@K, Recall@K, Hit Rate@K, and Catalog Coverage.
        """
        if self.train_df is None:
            self.split_holdout()
            
        # Train recommender strictly on train_df
        recommender = KNNRecommender(n_neighbors=k_neighbors, metric="cosine", weight_by_rating=True)
        recommender.fit(self.train_df)
        
        results = {}
        
        for k in top_k_list:
            precisions = []
            recalls = []
            hits = []
            all_recommended_items = set()
            
            for cust_id, ground_truth in self.test_dict.items():
                if cust_id not in recommender.customer_ids:
                    continue
                    
                # Generate recommendations using strictly train interactions
                recs = recommender.recommend(cust_id, top_n=k)
                rec_pids = [r["Product_ID"] for r in recs]
                
                # Track unique items for coverage
                all_recommended_items.update(rec_pids)
                
                # Evaluate against ground truth
                overlap = set(rec_pids).intersection(ground_truth)
                precision = len(overlap) / float(k)
                recall = len(overlap) / float(len(ground_truth))
                hit = 1 if len(overlap) > 0 else 0
                
                precisions.append(precision)
                recalls.append(recall)
                hits.append(hit)
                
            coverage = len(all_recommended_items) / float(len(self.catalog))
            
            results[f"Top-{k}"] = {
                "Precision@K": round(float(np.mean(precisions)), 4),
                "Recall@K": round(float(np.mean(recalls)), 4),
                "Hit_Rate@K": round(float(np.mean(hits)), 4),
                "Catalog_Coverage@K": round(float(coverage), 4),
                "Evaluated_Customers": len(precisions)
            }
            
        return pd.DataFrame(results).T, recommender


def train_and_save_final_model(df, model_path="model/knn_recommendation_model.pkl", k_neighbors=7):
    """
    Trains the production model on the complete cleaned dataset and serializes it with joblib.
    """
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    final_recommender = KNNRecommender(n_neighbors=k_neighbors, metric="cosine", weight_by_rating=True)
    final_recommender.fit(df)
    
    # Bundle model object with catalog metadata
    bundle = {
        "model": final_recommender,
        "n_neighbors": k_neighbors,
        "metric": "cosine",
        "customer_ids": final_recommender.customer_ids,
        "product_ids": final_recommender.product_ids,
        "categories": df[["Product_ID", "Product_Category"]].drop_duplicates().set_index("Product_ID")["Product_Category"].to_dict()
    }
    
    joblib.dump(bundle, model_path)
    print(f"Final recommendation model successfully saved to: {model_path}")
    return final_recommender, model_path


if __name__ == "__main__":
    from data_cleaning import DataCleaner
    cleaner = DataCleaner("data/ecommerce_dataset.xlsx")
    df, _ = cleaner.clean_and_validate()
    
    evaluator = RecommendationEvaluator(df)
    metrics_df, _ = evaluator.evaluate_knn(k_neighbors=7, top_k_list=[3, 5, 10])
    print("Holdout Recommendation Evaluation Results:")
    print(metrics_df)
    
    train_and_save_final_model(df)
