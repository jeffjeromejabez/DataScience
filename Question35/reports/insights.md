# Key Evidence-Based Insights Report

**Challenge ID:** DS_Day01_35  
**Project:** Personalized E-Commerce Product Recommendation System  
**Dataset:** 1,546 customer-product interaction records | 150 unique customers | 40 products | 8 categories  

---

## Executive Summary

The following 6 evidence-based insights are derived from rigorous statistical analysis, Market Basket Association Rule Mining (Apriori), and User-Based Collaborative Filtering (KNN with Cosine Similarity). Every statistic is empirically computed from the validated dataset and verified models.

---

### Insight 1: High-Lift Co-Purchase Clustering in Electronics and Appliances
* **Observation:** The highest association lift values occur between primary hardware anchors and functional accessories. For example:
  * $\text{P111 (4K Camera)} \rightarrow \text{P112 (128GB SD Card)}$: Support = $9.3\%$, Confidence = $87.5\%$, **$\text{Lift} = 3.58$**
  * $\text{P126 (Espresso Machine)} \rightarrow \text{P127 (Coffee Beans)}$: Support = $8.0\%$, Confidence = $85.7\%$, **$\text{Lift} = 3.62$**
  * $\text{P106 (5G Smartphone)} \rightarrow \text{P107 (Armor Phone Case)}$: Support = $11.3\%$, Confidence = $85.0\%$, **$\text{Lift} = 3.42$**
  * $\text{P121 (Running Shoes)} \rightarrow \text{P122 (Athletic Socks)}$: Support = $8.7\%$, Confidence = $81.2\%$, **$\text{Lift} = 3.35$**
* **Interpretation:** Customers purchasing primary hardware have an immediate, non-discretionary requirement for companion accessories and consumable starter kits.
* **Business Implication:** Implement one-click "Frequently Bought Together" bundles on product detail pages with an automatic $5\%\text{–}10\%$ bundle discount to capture high-margin cross-sell revenue at the moment of intent.

---

### Insight 2: Browsing Engagement Strongly Predicts Purchase Volume ($r = +0.86$)
* **Observation:** Customer browsing duration (minutes) demonstrates a strong positive linear correlation of **$+0.86$** with cumulative purchase history, with browsing durations ranging from 4 to 69 minutes (mean = $31.8$ minutes).
* **Interpretation:** In-session dwell time represents active purchase consideration rather than confusion or UI friction. Longer dwell times consistently convert into larger transaction quantities and higher customer satisfaction ratings ($4.15\bigstar$ average).
* **Business Implication:** Deploy real-time session tracking to dynamically inject category-specific recommendation widgets when a user dwells $>4$ minutes in a category without adding an item to the cart.

---

### Insight 3: KNN Collaborative Filtering Recovers Held-Out User Intent (Hit Rate@10 = 69.33%)
* **Observation:** In a leak-free Leave-One-Out holdout evaluation across 150 customers, the KNN model achieved:
  * **Top-3:** Precision@3 = $0.1222$, Recall@3 = $0.3667$, Hit Rate@3 = $36.67\%$
  * **Top-5:** Precision@5 = $0.1000$, Recall@5 = $0.5000$, Hit Rate@5 = $50.00\%$
  * **Top-10:** Precision@10 = $0.0693$, Recall@10 = $0.6933$, Hit Rate@10 = $69.33\%$
* **Interpretation:** By identifying the 7 nearest taste-twin neighbors using rating-weighted cosine similarity, the model successfully places a customer's true hidden purchase within their top-10 recommendations for nearly 7 out of 10 shoppers.
* **Business Implication:** Use the KNN collaborative filtering engine to power personalized "Recommended For You" homepage feeds and automated re-engagement email campaigns.

---

### Insight 4: Complete Catalog Coverage (100%) Prevents Popularity Collapse
* **Observation:** The KNN recommendation model achieved a **$100\%$ Catalog Coverage** across top-3, top-5, and top-10 recommendation lists, recommending all 40 active SKUs across the customer base.
* **Interpretation:** Normalizing customer vectors via Cosine Distance ensures that recommendation scores reflect taste alignment rather than raw purchase volume. As a result, niche products (e.g., *Studio Microphones P119*, *Chef Knives P129*, *Yoga Mats P125*) are actively surfaced to relevant audience segments.
* **Business Implication:** The retailer avoids excess inventory accumulation and margin loss from discounting slow-moving SKUs by ensuring fair discovery across the full catalog.

---

### Insight 5: Complementary Architecture: Association Rules vs. KNN Collaborative Discovery
* **Observation:** Comparison of recommendation sets reveals a **$25\%\text{–}40\%$ overlap** between Association Rule outputs and KNN collaborative filtering recommendations for the same customer.
* **Interpretation:** 
  * *Association Rules* excel at local, deterministic item-to-item pairings (e.g., Laptop $\rightarrow$ Mouse, Camera $\rightarrow$ SD Card).
  * *KNN Collaborative Filtering* excels at global, multi-item taste discovery across related categories (e.g., recommending a Studio Microphone or Laptop Hub to a content creator who previously bought a Camera and Laptop).
* **Business Implication:** A dual-engine strategy is optimal: deploy deterministic Association Rules at checkout and cart drawers, while deploying KNN Collaborative Filtering on discovery feeds and category landing pages.

---

### Insight 6: Core Hardware Categories Drive Acquisition & Revenue Volume
* **Observation:** `Laptops & Computers` (368 units purchased across 142 customer transactions) and `Mobile & Accessories` (352 units purchased across 139 customer transactions) represent the largest revenue-generating categories, with average satisfaction ratings exceeding $4.12\bigstar$.
* **Interpretation:** Tech hardware serves as the primary customer acquisition vehicle, drawing high-intent shoppers into the ecosystem who subsequently cross-shop in `Audio & Sound`, `Gaming`, and `Lifestyle`.
* **Business Implication:** Treat primary hardware as competitive gateway products, and focus margin optimization on post-purchase accessory recommendations and warranty attachments.
