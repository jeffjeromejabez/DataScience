"""
Dataset Generation Script for DS_Day01_35: E-Commerce Product Recommendation
Generates synthetic transaction dataset with realistic customer personas,
behavioral features (browsing time, rating, purchase count), and natural product co-purchase patterns.
"""

import os
import numpy as np
import pandas as pd

# Set random seed for perfect reproducibility
np.random.seed(42)

PRODUCT_CATALOG = [
    # Laptops & Computers (P101 - P105)
    {"Product_ID": "P101", "Product_Name": "Ultrabook Laptop 14-Inch", "Product_Category": "Laptops & Computers", "Base_Price": 899.99},
    {"Product_ID": "P102", "Product_Name": "Pro Gaming Laptop 15.6-Inch", "Product_Category": "Laptops & Computers", "Base_Price": 1299.99},
    {"Product_ID": "P103", "Product_Name": "Ergonomic Wireless Optical Mouse", "Product_Category": "Laptops & Computers", "Base_Price": 29.99},
    {"Product_ID": "P104", "Product_Name": "Water-Resistant Laptop Backpack", "Product_Category": "Laptops & Computers", "Base_Price": 49.99},
    {"Product_ID": "P105", "Product_Name": "7-in-1 USB-C Multiport Hub", "Product_Category": "Laptops & Computers", "Base_Price": 39.99},
    
    # Mobile & Accessories (P106 - P110)
    {"Product_ID": "P106", "Product_Name": "Flagship 5G Smartphone", "Product_Category": "Mobile & Accessories", "Base_Price": 799.99},
    {"Product_ID": "P107", "Product_Name": "Shockproof Armor Phone Case", "Product_Category": "Mobile & Accessories", "Base_Price": 19.99},
    {"Product_ID": "P108", "Product_Name": "Tempered Glass Screen Protector (2-Pack)", "Product_Category": "Mobile & Accessories", "Base_Price": 12.99},
    {"Product_ID": "P109", "Product_Name": "Fast Magnetic Wireless Charger", "Product_Category": "Mobile & Accessories", "Base_Price": 34.99},
    {"Product_ID": "P110", "Product_Name": "Braided Fast-Charging USB-C Cable", "Product_Category": "Mobile & Accessories", "Base_Price": 14.99},
    
    # Photography & Cameras (P111 - P115)
    {"Product_ID": "P111", "Product_Name": "Mirrorless 4K Digital Camera", "Product_Category": "Photography & Cameras", "Base_Price": 949.99},
    {"Product_ID": "P112", "Product_Name": "128GB High-Speed SDXC Memory Card", "Product_Category": "Photography & Cameras", "Base_Price": 35.99},
    {"Product_ID": "P113", "Product_Name": "Aluminum Lightweight Camera Tripod", "Product_Category": "Photography & Cameras", "Base_Price": 59.99},
    {"Product_ID": "P114", "Product_Name": "Compact Padded Camera Shoulder Bag", "Product_Category": "Photography & Cameras", "Base_Price": 42.99},
    {"Product_ID": "P115", "Product_Name": "Rechargeable Camera Battery & Dual Charger", "Product_Category": "Photography & Cameras", "Base_Price": 28.99},
    
    # Audio & Sound (P116 - P120)
    {"Product_ID": "P116", "Product_Name": "Active Noise Cancelling Over-Ear Headphones", "Product_Category": "Audio & Sound", "Base_Price": 179.99},
    {"Product_ID": "P117", "Product_Name": "True Wireless Sport Earbuds", "Product_Category": "Audio & Sound", "Base_Price": 89.99},
    {"Product_ID": "P118", "Product_Name": "Portable Waterproof Bluetooth Speaker", "Product_Category": "Audio & Sound", "Base_Price": 49.99},
    {"Product_ID": "P119", "Product_Name": "Studio USB Condenser Microphone", "Product_Category": "Audio & Sound", "Base_Price": 79.99},
    {"Product_ID": "P120", "Product_Name": "Ergonomic Headphone Desk Stand", "Product_Category": "Audio & Sound", "Base_Price": 22.99},
    
    # Fitness & Sports (P121 - P125)
    {"Product_ID": "P121", "Product_Name": "Performance Pro Running Shoes", "Product_Category": "Fitness & Sports", "Base_Price": 119.99},
    {"Product_ID": "P122", "Product_Name": "Breathable Cushioned Athletic Socks (3-Pack)", "Product_Category": "Fitness & Sports", "Base_Price": 16.99},
    {"Product_ID": "P123", "Product_Name": "Smart Fitness Tracker with Heart Rate Monitor", "Product_Category": "Fitness & Sports", "Base_Price": 69.99},
    {"Product_ID": "P124", "Product_Name": "Insulated Stainless Steel Sports Water Bottle", "Product_Category": "Fitness & Sports", "Base_Price": 24.99},
    {"Product_ID": "P125", "Product_Name": "Non-Slip High-Density Exercise Yoga Mat", "Product_Category": "Fitness & Sports", "Base_Price": 32.99},
    
    # Kitchen & Dining (P126 - P130)
    {"Product_ID": "P126", "Product_Name": "Espresso & Cappuccino Coffee Machine", "Product_Category": "Kitchen & Dining", "Base_Price": 199.99},
    {"Product_ID": "P127", "Product_Name": "Artisan Dark Roast Whole Bean Coffee (1kg)", "Product_Category": "Kitchen & Dining", "Base_Price": 21.99},
    {"Product_ID": "P128", "Product_Name": "Digital Touchscreen Air Fryer 5.8Qt", "Product_Category": "Kitchen & Dining", "Base_Price": 89.99},
    {"Product_ID": "P129", "Product_Name": "Japanese High-Carbon Chef Knife 8-Inch", "Product_Category": "Kitchen & Dining", "Base_Price": 54.99},
    {"Product_ID": "P130", "Product_Name": "High-Speed Personal Smoothie Blender", "Product_Category": "Kitchen & Dining", "Base_Price": 44.99},
    
    # Gaming & Esports (P131 - P135)
    {"Product_ID": "P131", "Product_Name": "RGB Mechanical Gaming Keyboard", "Product_Category": "Gaming & Esports", "Base_Price": 89.99},
    {"Product_ID": "P132", "Product_Name": "Ultra-Lightweight Optical Gaming Mouse", "Product_Category": "Gaming & Esports", "Base_Price": 49.99},
    {"Product_ID": "P133", "Product_Name": "7.1 Surround Sound Gaming Headset", "Product_Category": "Gaming & Esports", "Base_Price": 69.99},
    {"Product_ID": "P134", "Product_Name": "Extended Anti-Fray Cloth Gaming Mouse Mat", "Product_Category": "Gaming & Esports", "Base_Price": 19.99},
    {"Product_ID": "P135", "Product_Name": "Wireless Precision Gaming Controller", "Product_Category": "Gaming & Esports", "Base_Price": 59.99},
    
    # Fashion & Lifestyle (P136 - P140)
    {"Product_ID": "P136", "Product_Name": "Classic Denim Slim-Fit Jacket", "Product_Category": "Fashion & Lifestyle", "Base_Price": 69.99},
    {"Product_ID": "P137", "Product_Name": "100% Organic Heavyweight Cotton T-Shirt", "Product_Category": "Fashion & Lifestyle", "Base_Price": 24.99},
    {"Product_ID": "P138", "Product_Name": "Genuine Top-Grain Leather Casual Belt", "Product_Category": "Fashion & Lifestyle", "Base_Price": 29.99},
    {"Product_ID": "P139", "Product_Name": "Polarized UV400 Protection Sunglasses", "Product_Category": "Fashion & Lifestyle", "Base_Price": 39.99},
    {"Product_ID": "P140", "Product_Name": "Heavy Duty Canvas Everyday Tote Bag", "Product_Category": "Fashion & Lifestyle", "Base_Price": 22.99}
]

def get_catalog_df():
    return pd.DataFrame(PRODUCT_CATALOG)

def generate_ecommerce_data(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Define Product Catalog (40 products across 8 categories)
    catalog = PRODUCT_CATALOG
    catalog_df = pd.DataFrame(catalog)
    
    # 2. Define Customer Personas (150 unique customers C001 - C150)
    # Each persona has primary interest categories and affinity weights
    personas = [
        {"name": "Tech Enthusiast", "primary_cats": ["Laptops & Computers", "Gaming & Esports", "Audio & Sound"], "prob": 0.22},
        {"name": "Mobile Power User", "primary_cats": ["Mobile & Accessories", "Audio & Sound", "Fashion & Lifestyle"], "prob": 0.18},
        {"name": "Content Creator & Photographer", "primary_cats": ["Photography & Cameras", "Laptops & Computers", "Audio & Sound"], "prob": 0.15},
        {"name": "Fitness Enthusiast", "primary_cats": ["Fitness & Sports", "Mobile & Accessories", "Audio & Sound"], "prob": 0.16},
        {"name": "Culinary & Home Enthusiast", "primary_cats": ["Kitchen & Dining", "Fashion & Lifestyle"], "prob": 0.14},
        {"name": "Casual Lifestyle Shopper", "primary_cats": ["Fashion & Lifestyle", "Audio & Sound", "Kitchen & Dining"], "prob": 0.15}
    ]
    
    num_customers = 150
    customers = [f"C{str(i).zfill(3)}" for i in range(1, num_customers + 1)]
    
    # Assign persona to each customer
    persona_probs = [p["prob"] for p in personas]
    persona_probs = np.array(persona_probs) / sum(persona_probs)
    customer_personas = {}
    for c in customers:
        p = np.random.choice(personas, p=persona_probs)
        customer_personas[c] = p
        
    # Co-purchase affinity rules (natural basket creation)
    # When an anchor product is selected, associated products have significantly higher chance of being in customer's purchase history
    co_purchase_affinity = {
        # Laptop -> Mouse, Laptop Backpack, USB-C Hub
        "P101": [("P103", 0.72), ("P104", 0.68), ("P105", 0.62)],
        "P102": [("P103", 0.70), ("P104", 0.65), ("P131", 0.58)],
        # Phone -> Case, Screen Protector, Wireless Charger, Cable
        "P106": [("P107", 0.85), ("P108", 0.82), ("P109", 0.65), ("P110", 0.60)],
        # Camera -> SD Card, Tripod, Extra Battery, Bag
        "P111": [("P112", 0.88), ("P113", 0.74), ("P115", 0.70), ("P114", 0.55)],
        # Running Shoes -> Socks, Water Bottle, Fitness Tracker
        "P121": [("P122", 0.80), ("P124", 0.72), ("P123", 0.60)],
        # Coffee Machine -> Coffee Beans
        "P126": [("P127", 0.86)],
        # Gaming Keyboard -> Gaming Mouse, Mouse Mat, Headset
        "P131": [("P132", 0.78), ("P134", 0.75), ("P133", 0.65)],
        # Denim Jacket -> T-Shirt, Leather Belt
        "P136": [("P137", 0.70), ("P138", 0.62)]
    }
    
    records = []
    
    # Generate customer interaction records
    for cust_id in customers:
        persona = customer_personas[cust_id]
        primary_cats = persona["primary_cats"]
        
        # Decide how many distinct products this customer interacts with (between 10 and 22 items)
        num_interactions = np.random.randint(12, 22)
        
        # Calculate product selection probabilities based on customer persona
        product_probs = []
        for _, row in catalog_df.iterrows():
            cat = row["Product_Category"]
            if cat in primary_cats:
                # Primary categories have high probability weight
                weight = 5.0 / (primary_cats.index(cat) + 1.0)
            else:
                # Other categories have baseline exploration weight
                weight = 0.6
            product_probs.append(weight)
        
        product_probs = np.array(product_probs) / sum(product_probs)
        
        # Initial selected products
        selected_pids = list(np.random.choice(catalog_df["Product_ID"].values, size=num_interactions // 2, replace=False, p=product_probs))
        
        # Apply co-purchase dynamics
        current_selection = list(selected_pids)
        for anchor_pid in current_selection:
            if anchor_pid in co_purchase_affinity:
                for assoc_pid, prob in co_purchase_affinity[anchor_pid]:
                    if assoc_pid not in selected_pids and np.random.rand() < prob:
                        selected_pids.append(assoc_pid)
                        
        # Ensure total interaction count per customer stays realistic and unique per customer-product pair
        selected_pids = list(dict.fromkeys(selected_pids))
        if len(selected_pids) < 8:
            extra = [p for p in catalog_df["Product_ID"].values if p not in selected_pids]
            selected_pids.extend(list(np.random.choice(extra, size=8 - len(selected_pids), replace=False)))
            
        for pid in selected_pids:
            p_info = catalog_df[catalog_df["Product_ID"] == pid].iloc[0]
            cat = p_info["Product_Category"]
            is_primary = cat in primary_cats
            
            # Purchase History (Frequency/quantity of purchases for this product: integer 1 to 10)
            # Customers buy primary category products more frequently
            if is_primary:
                purchase_count = int(np.random.choice([1, 2, 3, 4, 5, 6, 7, 8], p=[0.15, 0.25, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02]))
            else:
                purchase_count = int(np.random.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.10, 0.05]))
                
            # Browsing Behaviour (Engagement time in minutes / page views, e.g. 5 to 65 mins)
            # Correlated with purchase frequency and category affinity
            base_browsing = 8 + (purchase_count * 4.5) + (15.0 if is_primary else 0.0)
            browsing_time = int(np.clip(np.random.normal(loc=base_browsing, scale=6.0), 4, 75))
            
            # Rating (1 to 5 stars)
            # Satisfied purchases and preferred categories yield higher ratings (mean ~4.1)
            if is_primary and purchase_count >= 2:
                rating = int(np.random.choice([3, 4, 5], p=[0.10, 0.40, 0.50]))
            elif is_primary:
                rating = int(np.random.choice([2, 3, 4, 5], p=[0.05, 0.20, 0.45, 0.30]))
            else:
                rating = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.15, 0.35, 0.30, 0.15]))
                
            records.append({
                "Customer_ID": cust_id,
                "Product_ID": pid,
                "Product_Category": cat,
                "Purchase_History": purchase_count,
                "Rating": rating,
                "Browsing_Behaviour": browsing_time
            })
            
    df = pd.DataFrame(records)
    
    # Shuffle records to simulate real transaction logs
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    # Save to Excel and CSV
    excel_path = os.path.join(output_dir, "ecommerce_dataset.xlsx")
    csv_path = os.path.join(output_dir, "ecommerce_dataset.csv")
    
    df.to_excel(excel_path, index=False, engine="openpyxl")
    df.to_csv(csv_path, index=False)
    
    print(f"Dataset generated successfully!")
    print(f"Total Records: {len(df)}")
    print(f"Unique Customers: {df['Customer_ID'].nunique()}")
    print(f"Unique Products: {df['Product_ID'].nunique()}")
    print(f"Unique Categories: {df['Product_Category'].nunique()}")
    print(f"Columns: {list(df.columns)}")
    print(f"Files saved to:\n  - {excel_path}\n  - {csv_path}")
    
    return df

if __name__ == "__main__":
    generate_ecommerce_data()
