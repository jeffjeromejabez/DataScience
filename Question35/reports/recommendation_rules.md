# Product Recommendation Rules & Association Analysis Report

**Challenge ID:** DS_Day01_35  
**Project:** E-Commerce Product Recommendation System  
**Technique:** Market Basket Association Analysis (Apriori Algorithm)  

---

## 1. Overview & Methodology

Market Basket Analysis uncovers hidden purchase affinities between products by analyzing co-occurrences across historical customer transaction baskets. Using the **Apriori Algorithm**, we calculate three fundamental metrics to discover meaningful cross-sell rules:

* **Support:** The proportion of total transactions that contain both Product $A$ (Antecedent) and Product $B$ (Consequent).
  $$\text{Support}(A \rightarrow B) = P(A \cap B) = \frac{\text{Count}(A \cap B)}{N_{\text{total}}}$$
* **Confidence:** The conditional probability that a customer purchases Product $B$, given that they have purchased Product $A$.
  $$\text{Confidence}(A \rightarrow B) = P(B \mid A) = \frac{\text{Support}(A \cap B)}{\text{Support}(A)}$$
* **Lift:** The ratio of observed joint purchase frequency to the expected joint purchase frequency if $A$ and $B$ were completely independent.
  $$\text{Lift}(A \rightarrow B) = \frac{\text{Confidence}(A \rightarrow B)}{\text{Support}(B)} = \frac{P(A \cap B)}{P(A) \cdot P(B)}$$
  * **$\text{Lift} > 1$:** Positive association (purchasing $A$ actively boosts the likelihood of purchasing $B$).
  * **$\text{Lift} = 1$:** Products are independent.
  * **$\text{Lift} < 1$:** Negative or substitutive association.

---

## 2. Threshold Selection & Parameter Tuning

To avoid generating thousands of trivial permutations or failing to discover niche associations, the following defensible parameter thresholds were selected:

| Parameter | Threshold | Justification |
| :--- | :---: | :--- |
| **Minimum Support** | $\ge 0.030$ ($3.0\%$) | Captures item combinations appearing in at least 5 distinct customer baskets across the active catalog. |
| **Minimum Confidence** | $\ge 0.250$ ($25.0\%$) | Guarantees that at least 1 out of 4 shoppers purchasing Product $A$ also acquire Product $B$. |
| **Minimum Lift** | $\ge 1.200$ | Filters out coincidental co-purchases driven solely by high baseline item popularity. |

---

## 3. High-Confidence Cross-Sell Recommendation Rules

The table below outlines the primary recommendation rules extracted from transaction histories:

| Anchor Product (A) | Recommended Product (B) | Support | Confidence | Lift | Business Action & Plain-English Translation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **P111: 4K Mirrorless Camera** | **P112: 128GB SDXC Memory Card** | $0.093$ ($9.3\%$) | $0.875$ ($87.5\%$) | $3.58$ | **Essential Accessory Bundle:** $87.5\%$ of mirrorless camera buyers purchase this high-speed memory card. Show as an instant 1-click bundle on camera PDP. |
| **P106: Flagship 5G Smartphone** | **P107: Armor Phone Case** | $0.113$ ($11.3\%$) | $0.850$ ($85.0\%$) | $3.42$ | **Protection Add-on:** Smartphone buyers have an $85.0\%$ probability of buying protective armor. Auto-suggest in slide-out cart. |
| **P106: Flagship 5G Smartphone** | **P108: Screen Protector (2-Pk)** | $0.107$ ($10.7\%$) | $0.800$ ($80.0\%$) | $3.25$ | **Impulse Complement:** Screen protector represents an immediate checkout impulse add-on with $>3\times$ random chance lift. |
| **P126: Espresso Coffee Machine** | **P127: Artisan Coffee Beans (1kg)**| $0.080$ ($8.0\%$) | $0.857$ ($85.7\%$) | $3.62$ | **Consumable Starter Kit:** Espresso machine buyers almost universally purchase beans ($85.7\%$). Offer a 10% discount on first bean bag. |
| **P121: Pro Running Shoes** | **P122: Athletic Socks (3-Pack)** | $0.087$ ($8.7\%$) | $0.812$ ($81.2\%$) | $3.35$ | **Footwear Complement:** Running shoes strongly trigger socks co-purchases. Position as a checkout upsell. |
| **P131: RGB Gaming Keyboard** | **P132: Precision Gaming Mouse** | $0.080$ ($8.0\%$) | $0.750$ ($75.0\%$) | $3.10$ | **Esports Battlestation:** Mechanical keyboard buyers strongly bundle with precision gaming mice. Highlight in "Complete the Setup" widget. |
| **P101: Ultrabook Laptop 14"** | **P103: Wireless Optical Mouse** | $0.087$ ($8.7\%$) | $0.722$ ($72.2\%$) | $2.95$ | **Productivity Peripheral:** 7 out of 10 laptop buyers add an ergonomic wireless mouse. Display directly under laptop specs. |
| **P101: Ultrabook Laptop 14"** | **P104: Water-Resistant Backpack** | $0.080$ ($8.0\%$) | $0.667$ ($66.7\%$) | $2.74$ | **Commuter Accessory:** Strongly associated companion item. Offer as a discounted bundled accessory kit. |
| **P111: 4K Mirrorless Camera** | **P113: Lightweight Camera Tripod** | $0.073$ ($7.3\%$) | $0.688$ ($68.8\%$) | $2.82$ | **Creator Upgrade:** Tripods are frequently bundled by enthusiast photographers seeking stable video recording. |
| **P136: Denim Slim-Fit Jacket** | **P137: Heavyweight Cotton T-Shirt** | $0.073$ ($7.3\%$) | $0.688$ ($68.8\%$) | $2.80$ | **Style Outfit Match:** Outerwear purchases strongly trigger baseline layering apparel sales. Suggest in "Wear It With" module. |

---

## 4. Multi-Item Rules (Antecedent Sets)

Higher-order itemsets reveal compound purchasing behavior:

* **$\{ \text{P106: Smartphone}, \text{P107: Phone Case} \} \rightarrow \text{P108: Screen Protector}$**
  * **Support:** $0.093$ ($9.3\%$) | **Confidence:** $0.824$ ($82.4\%$) | **Lift:** $3.35$
  * *Business Insight:* When a customer has selected both a phone and a case, they will almost always ($82.4\%$) add a screen protector if presented at checkout.
* **$\{ \text{P101: Laptop}, \text{P103: Mouse} \} \rightarrow \text{P104: Laptop Backpack}$**
  * **Support:** $0.067$ ($6.7\%$) | **Confidence:** $0.769$ ($76.9\%$) | **Lift:** $3.16$
  * *Business Insight:* Shoppers assembling a mobile workstation can be converted to high-margin carrying gear with minimal discount incentives.

---

## 5. Web Placement Implementation Matrix

| Store Area | Target Rule Type | UX Component | Primary Objective |
| :--- | :--- | :--- | :--- |
| **Product Detail Page (PDP)** | Core Hardware $\rightarrow$ Essential Accessory | "Frequently Bought Together" Checkbox Widget | Multi-item basket building |
| **Slide-Out Cart Drawer** | Primary Product $\rightarrow$ Low-cost ($<\$25$) Consumable/Protection | "Quick Add" 1-Click Carousel | Impulse conversion & AOV lift |
| **Post-Purchase Thank You Page** | High-ticket Hardware $\rightarrow$ Secondary Gear (e.g., Camera $\rightarrow$ Tripod/Bag) | "Complete Your Kit" Exclusive Offer | Re-engagement & reduced churn |
