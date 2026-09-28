"""
KNN Collaborative Filtering Recommendation Module for DS_Day01_35
Implements customer-similarity collaborative filtering using NearestNeighbors with Cosine Distance.
Generates top-N recommendations and connects findings with Market Basket Association Rules.
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class KNNRecommender:
    """
    User-Based Collaborative Filtering Recommender using Nearest Neighbors.
    """

    def __init__(self, n_neighbors=7, metric="cosine", weight_by_rating=True):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.weight_by_rating = weight_by_rating
        self.model = None
        self.interaction_matrix = None
        self.customer_ids = None
        self.product_ids = None

    def fit(self, df):
        """
        Fits the NearestNeighbors model on customer-product interaction matrix.
        """
        # Create customer-product matrix
        if self.weight_by_rating:
            # Weighted interaction = Purchase_History * (Rating / 5.0)
            interaction = (
                df.assign(weight=df["Purchase_History"] * (df["Rating"] / 5.0))
                .groupby(["Customer_ID", "Product_ID"])["weight"]
                .sum()
                .unstack()
                .fillna(0)
            )
        else:
            # Binary interaction (1 if purchased, 0 otherwise)
            interaction = (
                df.groupby(["Customer_ID", "Product_ID"])["Purchase_History"]
                .count()
                .unstack()
                .fillna(0)
            )
            interaction = (interaction > 0).astype(float)
            
        self.interaction_matrix = interaction
        self.customer_ids = list(interaction.index)
        self.product_ids = list(interaction.columns)
        
        # Initialize and fit NearestNeighbors
        # n_neighbors + 1 because query point itself is returned as distance 0
        self.model = NearestNeighbors(
            n_neighbors=self.n_neighbors + 1,
            metric=self.metric,
            algorithm="brute"
        )
        self.model.fit(self.interaction_matrix.values)
        return self

    def find_similar_customers(self, customer_id):
        """
        Returns the top K most similar customers and their cosine similarities.
        """
        if customer_id not in self.customer_ids:
            raise ValueError(f"Customer {customer_id} not found in interaction matrix.")
            
        cust_idx = self.customer_ids.index(customer_id)
        cust_vector = self.interaction_matrix.values[cust_idx].reshape(1, -1)
        
        distances, indices = self.model.kneighbors(cust_vector)
        
        # Exclude the query customer itself (index 0)
        neighbor_indices = indices[0][1:]
        neighbor_distances = distances[0][1:]
        
        similar_customers = []
        for idx, dist in zip(neighbor_indices, neighbor_distances):
            similar_cust_id = self.customer_ids[idx]
            # Convert cosine distance to cosine similarity: similarity = 1 - distance
            similarity = 1.0 - dist
            similar_customers.append({
                "Customer_ID": similar_cust_id,
                "Cosine_Distance": dist,
                "Cosine_Similarity": similarity
            })
            
        return pd.DataFrame(similar_customers)

    def recommend(self, customer_id, top_n=5):
        """
        Generates top-N unpurchased product recommendations for a target customer.
        Candidate scores are computed as similarity-weighted interaction sum.
        """
        if customer_id not in self.customer_ids:
            raise ValueError(f"Customer {customer_id} not found in training data.")
            
        cust_idx = self.customer_ids.index(customer_id)
        cust_interactions = self.interaction_matrix.iloc[cust_idx]
        already_purchased = set(cust_interactions[cust_interactions > 0].index)
        
        # Find neighbors
        similar_df = self.find_similar_customers(customer_id)
        
        product_scores = {}
        for _, row in similar_df.iterrows():
            sim_cust = row["Customer_ID"]
            sim_weight = row["Cosine_Similarity"]
            if sim_weight <= 0:
                continue
                
            sim_cust_vector = self.interaction_matrix.loc[sim_cust]
            for prod, score in sim_cust_vector.items():
                if prod not in already_purchased and score > 0:
                    product_scores[prod] = product_scores.get(prod, 0.0) + (score * sim_weight)
                    
        if not product_scores:
            # Fallback to catalog popularity if neighbors have no unpurchased items
            popular_items = self.interaction_matrix.sum().sort_values(ascending=False)
            unpurchased_popular = [p for p in popular_items.index if p not in already_purchased]
            return [{"Product_ID": p, "Recommendation_Score": float(popular_items[p]), "Source": "Popularity Fallback"} for p in unpurchased_popular[:top_n]]
            
        sorted_recommendations = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        results = []
        for prod_id, score in sorted_recommendations:
            results.append({
                "Product_ID": prod_id,
                "Recommendation_Score": round(float(score), 4),
                "Source": "KNN Collaborative Similarity"
            })
            
        return results

    def compare_with_association_rules(self, customer_id, rules_df, top_n=5):
        """
        Connects and compares KNN recommendations with Association Rule recommendations.
        """
        cust_idx = self.customer_ids.index(customer_id)
        cust_interactions = self.interaction_matrix.iloc[cust_idx]
        purchased_pids = set(cust_interactions[cust_interactions > 0].index)
        
        # 1. KNN Recommendations
        knn_recs = [r["Product_ID"] for r in self.recommend(customer_id, top_n=top_n)]
        
        # 2. Association Rule Recommendations
        assoc_recs = []
        for _, rule in rules_df.iterrows():
            antecedents = rule["antecedents"]
            consequents = rule["consequents"]
            
            # If customer purchased all antecedents, recommend consequents not already bought
            if antecedents.issubset(purchased_pids):
                for c in consequents:
                    if c not in purchased_pids and c not in assoc_recs:
                        assoc_recs.append(c)
                        
        assoc_recs_top = assoc_recs[:top_n]
        overlap = set(knn_recs).intersection(set(assoc_recs_top))
        
        return {
            "Customer_ID": customer_id,
            "Purchased_Products": list(purchased_pids),
            "KNN_Recommendations": knn_recs,
            "Association_Rule_Recommendations": assoc_recs_top,
            "Overlapping_Recommendations": list(overlap),
            "Overlap_Count": len(overlap)
        }
