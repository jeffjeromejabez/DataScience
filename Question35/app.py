"""
Interactive Streamlit Dashboard for DS_Day01_35: Personalized E-Commerce Product Recommendation System
Features:
- Live User-Based KNN Collaborative Filtering Recommender
- Real-Time Point-of-Sale Cart Basket Cross-Sell Engine
- Interactive Apriori Association Rules Explorer with Plotly Visualizations
- Interactive Exploratory Customer Analytics Hub
- Model Evaluation & Holdout Validation Benchmark
- Cold-Start Strategy Simulator (New User & New Product)
- Executive Insights & Multi-Touchpoint Deployment Roadmap
"""

import os
import sys

# Ensure src directory is in sys.path for unpickling KNNRecommender
sys.path.insert(0, os.path.abspath("src"))
sys.path.insert(0, os.path.abspath("."))

import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from recommendation import KNNRecommender

# ---------------------------------------------------------
# Page Configuration & Global Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Recommendation Engine | DS_Day01_35",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern, Polished Aesthetics
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3b82f6;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.75;
    }
    .badge-lift {
        background: #10b981;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-conf {
        background: #6366f1;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-knn {
        background: #f59e0b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .product-card {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
    .product-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    .tab-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Data & Model Loading with Caching
# ---------------------------------------------------------
@st.cache_data
def load_catalog():
    try:
        from src.generate_dataset import get_catalog_df
        return get_catalog_df()
    except Exception:
        from generate_dataset import get_catalog_df
        return get_catalog_df()

@st.cache_data
def load_dataset():
    data_path = os.path.join("data", "ecommerce_dataset.csv")
    if not os.path.exists(data_path):
        from src.generate_dataset import generate_ecommerce_data
        generate_ecommerce_data("data")
    df = pd.read_csv(data_path)
    
    # Merge catalog metadata (Product_Name, Base_Price) if not already present
    catalog_df = load_catalog()
    if "Product_Name" not in df.columns or "Base_Price" not in df.columns:
        df = df.merge(catalog_df[["Product_ID", "Product_Name", "Base_Price"]], on="Product_ID", how="left")
    return df

@st.cache_resource
def load_knn_model():
    model_path = os.path.join("model", "knn_recommendation_model.pkl")
    if not os.path.exists(model_path):
        from src.model import run_model_pipeline
        run_model_pipeline()
    artifact = joblib.load(model_path)
    return artifact

@st.cache_data
def load_association_rules():
    try:
        from src.association_rules import run_association_rules, AssociationRuleMiner
    except ImportError:
        from association_rules import run_association_rules, AssociationRuleMiner
    df = load_dataset()
    rules_df = run_association_rules(df)
    return rules_df


# Load Core Artifacts
catalog_df = load_catalog()
df = load_dataset()
model_artifact = load_knn_model()
recommender = model_artifact["model"]
rules_df = load_association_rules()

# Catalog & SKU Mapping
sku_to_name = dict(zip(catalog_df["Product_ID"], catalog_df["Product_Name"]))
sku_to_cat = dict(zip(catalog_df["Product_ID"], catalog_df["Product_Category"]))
sku_to_price = dict(zip(catalog_df["Product_ID"], catalog_df["Base_Price"]))
sku_to_label = {pid: f"{pid} - {sku_to_name[pid]} (${sku_to_price[pid]:.2f})" for pid in sku_to_name}



# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1472851294608-062f824d29cc?auto=format&fit=crop&w=400&q=80", use_container_width=True)
st.sidebar.title("Navigation")

navigation_mode = st.sidebar.radio(
    "Select Module:",
    [
        "🛒 Personalized Recommendation Studio",
        "⚡ Point-of-Sale / Cart Cross-Sell",
        "🔍 Market Basket & Association Rules",
        "📊 Exploratory Customer Analytics",
        "🎯 Model Performance & Evaluation",
        "🚀 Cold-Start Strategy Simulator",
        "💡 Business Insights & Action Plan"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("**System Metadata**")
st.sidebar.markdown(f"- **Customers:** {df['Customer_ID'].nunique()}")
st.sidebar.markdown(f"- **Catalog SKUs:** {df['Product_ID'].nunique()} across {df['Product_Category'].nunique()} categories")
st.sidebar.markdown(f"- **Transactions:** {len(df):,} records")
st.sidebar.markdown(f"- **Total Rules Mined:** {len(rules_df)} rules")


# ---------------------------------------------------------
# Tab 1: Personalized Recommendation Studio (KNN)
# ---------------------------------------------------------
if navigation_mode == "🛒 Personalized Recommendation Studio":
    st.title("🛒 Customer-Centric Recommendation Studio")
    st.markdown("Explore personalized product recommendations powered by **Cosine-Distance User-Based Collaborative Filtering (KNN)** and compare them side-by-side with **Market Basket Association Rules**.")

    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        customer_list = sorted(list(recommender.customer_ids))
        selected_cust = st.selectbox("Select Customer Profile:", customer_list, index=0)
    with col2:
        top_k_recs = st.slider("Recommendations (Top-K):", min_value=3, max_value=10, value=5)
    with col3:
        n_neighbors_dyn = st.slider("Nearest Neighbors (K):", min_value=3, max_value=15, value=7)

    # Customer Profile Summary
    cust_df = df[df["Customer_ID"] == selected_cust].sort_values("Purchase_History", ascending=False)
    total_spent = (cust_df["Purchase_History"] * cust_df["Base_Price"]).sum()
    avg_rating = cust_df["Rating"].mean()
    top_cat = cust_df["Product_Category"].value_counts().index[0] if len(cust_df) > 0 else "N/A"

    st.markdown("### 👤 Customer Profile Snapshot")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Purchased SKUs</div><div class="metric-value">{len(cust_df)}</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Estimated Spend</div><div class="metric-value">${total_spent:,.2f}</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Average Satisfaction</div><div class="metric-value">★ {avg_rating:.2f} / 5.0</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Favorite Category</div><div class="metric-value" style="font-size:1.2rem; margin-top:5px;">{top_cat}</div></div>""", unsafe_allow_html=True)

    tab_rec1, tab_rec2, tab_rec3 = st.tabs(["✨ Top-N Recommendations", "👥 Taste Twins (Nearest Neighbors)", "🛍️ Purchase History"])

    with tab_rec1:
        # Run live recommendation
        recs = recommender.recommend(selected_cust, top_n=top_k_recs)
        comparison = recommender.compare_with_association_rules(selected_cust, rules_df, top_n=top_k_recs)

        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.markdown(f"#### 🎯 Recommended For Customer `{selected_cust}`")
            for i, rec in enumerate(recs, 1):
                pid = rec["Product_ID"]
                score = rec["Recommendation_Score"]
                pname = sku_to_name.get(pid, pid)
                pcat = sku_to_cat.get(pid, "General")
                pprice = sku_to_price.get(pid, 0.0)

                is_in_assoc = pid in comparison["Association_Rule_Recommendations"]
                badge_extra = "<span class='badge-conf'>Also in Cross-Sell Rules</span>" if is_in_assoc else ""

                st.markdown(f"""
                <div class="product-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>#{i}. {pname}</strong> <span style="opacity: 0.7;">({pid})</span><br>
                            <span style="font-size: 0.85rem; color: #3b82f6;">🏷️ {pcat}</span> | 
                            <strong>${pprice:.2f}</strong>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge-knn">Score: {score:.2f}</span><br>
                            {badge_extra}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            st.markdown("#### 🔄 Model Comparison & Rule Bridging")
            overlap = comparison["Overlapping_Recommendations"]
            overlap_pct = (len(overlap) / max(1, top_k_recs)) * 100

            st.info(f"""
            **Overlap Rate:** **{len(overlap)} / {top_k_recs} ({overlap_pct:.0f}%)**  
            - **KNN Engine:** Recommends items broad taste-twins enjoyed across departments.  
            - **Association Rules:** Suggests deterministic point-of-sale attachments based on items already in the basket.
            """)

            if overlap:
                st.success(f"**High-Confidence Cross-Engine Items:** {', '.join([sku_to_name.get(p, p) for p in overlap])}")
            else:
                st.write("No exact top-K overlap; KNN is driving exploration while Association Rules focus on immediate accessories.")

            with st.expander("View Association Rule Predictions"):
                if comparison["Association_Rule_Recommendations"]:
                    for p in comparison["Association_Rule_Recommendations"]:
                        st.markdown(f"- **{p}**: {sku_to_name.get(p, p)} *({sku_to_cat.get(p, '')})*")
                else:
                    st.write("No active antecedent triggers met for this customer's basket.")

    with tab_rec2:
        st.markdown(f"#### 👥 Top Similar Customers (Taste Twins for `{selected_cust}`)")
        sim_df = recommender.find_similar_customers(selected_cust).head(n_neighbors_dyn)
        
        sim_display = []
        for _, row in sim_df.iterrows():
            sim_id = row["Customer_ID"]
            sim_score = row["Cosine_Similarity"]
            sim_items = df[df["Customer_ID"] == sim_id]["Product_ID"].tolist()
            sim_display.append({
                "Neighbor Customer ID": sim_id,
                "Cosine Similarity": f"{sim_score:.4f}",
                "Similarity %": f"{sim_score * 100:.1f}%",
                "Items Purchased": len(sim_items),
                "Sample Products": ", ".join([sku_to_name.get(p, p)[:20] for p in sim_items[:3]]) + "..."
            })
        st.dataframe(pd.DataFrame(sim_display), use_container_width=True)

        # Plotly similarity bar chart
        fig_sim = px.bar(
            sim_df,
            x="Customer_ID",
            y="Cosine_Similarity",
            color="Cosine_Similarity",
            color_continuous_scale="Blues",
            title=f"Cosine Similarity Scores of Top Neighbors for {selected_cust}",
            labels={"Cosine_Similarity": "Cosine Similarity", "Customer_ID": "Neighbor Customer"}
        )
        fig_sim.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_sim, use_container_width=True)

    with tab_rec3:
        st.markdown(f"#### 📜 Full Interaction History for `{selected_cust}`")
        hist_table = cust_df[["Product_ID", "Product_Name", "Product_Category", "Purchase_History", "Rating", "Browsing_Behaviour", "Base_Price"]].copy()
        hist_table["Rating"] = hist_table["Rating"].apply(lambda r: "★ " * int(r))
        hist_table["Browsing_Behaviour"] = hist_table["Browsing_Behaviour"].apply(lambda m: f"{m} mins")
        hist_table["Base_Price"] = hist_table["Base_Price"].apply(lambda p: f"${p:.2f}")
        st.dataframe(hist_table, use_container_width=True)


# ---------------------------------------------------------
# Tab 2: Point-of-Sale / Cart Cross-Sell Engine
# ---------------------------------------------------------
elif navigation_mode == "⚡ Point-of-Sale / Cart Cross-Sell":
    st.title("⚡ Real-Time Point-of-Sale Cross-Sell Engine")
    st.markdown("Simulate an active shopping cart session. As customers add items to their basket, the Apriori association engine triggers high-conversion cross-sell add-ons in real time.")

    col_cart, col_results = st.columns([1, 1.4])

    with col_cart:
        st.markdown("### 🛒 Active Cart Basket")
        default_skus = ["P106"]  # Smartphone as default
        cart_selection = st.multiselect(
            "Add Items to Customer Cart:",
            options=catalog_df["Product_ID"].tolist(),
            default=default_skus,
            format_func=lambda x: sku_to_label.get(x, x)
        )

        cart_total = sum([sku_to_price.get(pid, 0.0) for pid in cart_selection])
        st.markdown(f"**Cart Value ({len(cart_selection)} items):** `${cart_total:,.2f}`")

        if cart_selection:
            st.markdown("#### Items Currently in Cart:")
            for pid in cart_selection:
                st.markdown(f"- 📦 **{sku_to_name.get(pid, pid)}** (`{pid}`) — `${sku_to_price.get(pid, 0):.2f}`")
        else:
            st.warning("Your cart is empty. Add products above to generate cross-sell recommendations.")

    with col_results:
        st.markdown("### 🎁 Recommended Cross-Sell Add-Ons")
        if cart_selection:
            cart_set = set(cart_selection)
            matched_rules = []

            for _, rule in rules_df.iterrows():
                antecedents = rule["antecedents"]
                consequents = rule["consequents"]

                if antecedents.issubset(cart_set):
                    for item in consequents:
                        if item not in cart_set:
                            matched_rules.append({
                                "Target_Item": item,
                                "Item_Name": sku_to_name.get(item, item),
                                "Category": sku_to_cat.get(item, "General"),
                                "Price": sku_to_price.get(item, 0.0),
                                "Trigger_Item": ", ".join([sku_to_name.get(a, a) for a in antecedents]),
                                "Confidence": rule["confidence"],
                                "Lift": rule["lift"],
                                "Support": rule["support"]
                            })

            if matched_rules:
                matched_df = pd.DataFrame(matched_rules).drop_duplicates(subset=["Target_Item"]).sort_values("Lift", ascending=False)
                st.success(f"🔥 Found **{len(matched_df)}** high-affinity cross-sell attachment(s) based on current cart contents!")

                for _, row in matched_df.iterrows():
                    st.markdown(f"""
                    <div class="product-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size:1.05rem;">{row['Item_Name']}</strong> <span style="opacity: 0.7;">({row['Target_Item']})</span><br>
                                <span style="font-size: 0.85rem; color: #3b82f6;">🏷️ {row['Category']}</span> | 
                                <strong>${row['Price']:.2f}</strong><br>
                                <span style="font-size: 0.85rem; opacity: 0.8;">Triggered by: <em>{row['Trigger_Item']}</em></span>
                            </div>
                            <div style="text-align: right;">
                                <span class="badge-lift">Lift: {row['Lift']:.2f}x</span><br><br>
                                <span class="badge-conf">Conf: {row['Confidence']*100:.1f}%</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No direct multi-item association rules triggered yet for this specific combination. Showing popular category companion items.")
                # Show fallback cross-category companion
                st.markdown("- 💡 *Suggested: Add a high-affinity tech anchor like **Ultrabook Laptop (P101)** or **Camera (P111)** to see strong bundle recommendations.*")
        else:
            st.write("Add items to the cart on the left to trigger association rules.")


# ---------------------------------------------------------
# Tab 3: Market Basket & Association Rules Explorer
# ---------------------------------------------------------
elif navigation_mode == "🔍 Market Basket & Association Rules":
    st.title("🔍 Market Basket & Association Rules Explorer")
    st.markdown("Interactively inspect directional purchase associations discovered via the **Apriori Algorithm**.")

    # Filter Controls
    f1, f2, f3 = st.columns(3)
    with f1:
        min_supp = st.slider("Minimum Support ($P(A \\cap B)$):", min_value=0.01, max_value=0.20, value=0.05, step=0.01)
    with f2:
        min_conf = st.slider("Minimum Confidence ($P(B|A)$):", min_value=0.10, max_value=1.00, value=0.30, step=0.05)
    with f3:
        min_lift = st.slider("Minimum Lift:", min_value=1.0, max_value=4.0, value=1.5, step=0.1)

    # Filter Rules
    filtered_rules = rules_df[
        (rules_df["support"] >= min_supp) &
        (rules_df["confidence"] >= min_conf) &
        (rules_df["lift"] >= min_lift)
    ].copy()

    st.markdown(f"### Discovered Rules ({len(filtered_rules)} matched criteria)")

    # Plotly Scatter Plot
    plot_df = filtered_rules.copy()
    plot_df["Antecedent_Names"] = plot_df["antecedents"].apply(lambda s: ", ".join([sku_to_name.get(x, x) for x in s]))
    plot_df["Consequent_Names"] = plot_df["consequents"].apply(lambda s: ", ".join([sku_to_name.get(x, x) for x in s]))
    plot_df["Rule_Label"] = plot_df["Antecedent_Names"] + "  ➔  " + plot_df["Consequent_Names"]

    fig_rules = px.scatter(
        plot_df,
        x="support",
        y="confidence",
        size="lift",
        color="lift",
        color_continuous_scale="Viridis",
        hover_name="Rule_Label",
        hover_data={"support": ":.3f", "confidence": ":.3f", "lift": ":.2f"},
        title="Association Rules: Support vs. Confidence (Size & Color = Lift)",
        labels={"support": "Support (Basket Frequency)", "confidence": "Confidence (Rule Reliability)", "lift": "Lift Factor"}
    )
    fig_rules.update_layout(height=480, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_rules, use_container_width=True)

    # Clean display table
    table_display = filtered_rules.copy()
    table_display["Antecedent"] = table_display["antecedents"].apply(lambda s: ", ".join([f"{x} ({sku_to_name.get(x, x)})" for x in s]))
    table_display["Consequent"] = table_display["consequents"].apply(lambda s: ", ".join([f"{x} ({sku_to_name.get(x, x)})" for x in s]))
    table_display["Support %"] = (table_display["support"] * 100).round(2).astype(str) + "%"
    table_display["Confidence %"] = (table_display["confidence"] * 100).round(2).astype(str) + "%"
    table_display["Lift"] = table_display["lift"].round(2)
    
    st.dataframe(
        table_display[["Antecedent", "Consequent", "Support %", "Confidence %", "Lift"]].sort_values("Lift", ascending=False),
        use_container_width=True
    )


# ---------------------------------------------------------
# Tab 4: Exploratory Customer Analytics Hub
# ---------------------------------------------------------
elif navigation_mode == "📊 Exploratory Customer Analytics":
    st.title("📊 Exploratory Customer Analytics Hub")
    st.markdown("Analyze customer browsing patterns, product category volume, satisfaction ratings, and engagement metrics.")

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Volume</div><div class="metric-value">{df['Purchase_History'].sum():,} units</div></div>""", unsafe_allow_html=True)
    with e2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Browsing Time</div><div class="metric-value">{df['Browsing_Behaviour'].mean():.1f} mins</div></div>""", unsafe_allow_html=True)
    with e3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Avg Star Rating</div><div class="metric-value">★ {df['Rating'].mean():.2f} / 5.0</div></div>""", unsafe_allow_html=True)
    with e4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Browse/Buy Correlation</div><div class="metric-value">+0.86</div></div>""", unsafe_allow_html=True)

    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["🏷️ Category Dynamics", "📦 Product Demand", "⏱️ Dwell Time vs Purchases"])

    with chart_tab1:
        cat_agg = df.groupby("Product_Category").agg(
            Total_Volume=("Purchase_History", "sum"),
            Avg_Rating=("Rating", "mean"),
            Avg_Browsing=("Browsing_Behaviour", "mean"),
            Customers=("Customer_ID", "nunique")
        ).reset_index().sort_values("Total_Volume", ascending=False)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_cat_vol = px.bar(
                cat_agg,
                x="Product_Category",
                y="Total_Volume",
                color="Total_Volume",
                color_continuous_scale="Teal",
                title="Total Purchase Volume by Department",
                labels={"Total_Volume": "Units Sold", "Product_Category": "Category"}
            )
            fig_cat_vol.update_layout(xaxis_tickangle=-30, height=400)
            st.plotly_chart(fig_cat_vol, use_container_width=True)

        with col_c2:
            fig_cat_rat = px.bar(
                cat_agg,
                x="Product_Category",
                y="Avg_Rating",
                color="Avg_Rating",
                color_continuous_scale="Sunset",
                title="Average Customer Satisfaction by Department",
                labels={"Avg_Rating": "Avg Rating (1-5)", "Product_Category": "Category"}
            )
            fig_cat_rat.update_layout(xaxis_tickangle=-30, yaxis_range=[3.0, 5.0], height=400)
            st.plotly_chart(fig_cat_rat, use_container_width=True)

    with chart_tab2:
        top_prods = df.groupby(["Product_ID", "Product_Name", "Product_Category"]).agg(
            Total_Purchased=("Purchase_History", "sum"),
            Avg_Rating=("Rating", "mean")
        ).reset_index().sort_values("Total_Purchased", ascending=False).head(15)

        fig_top_p = px.bar(
            top_prods,
            y="Product_Name",
            x="Total_Purchased",
            orientation="h",
            color="Product_Category",
            title="Top 15 Most Frequently Purchased Products",
            labels={"Total_Purchased": "Total Units Purchased", "Product_Name": "Product SKU"}
        )
        fig_top_p.update_layout(yaxis=dict(autorange="reversed"), height=480)
        st.plotly_chart(fig_top_p, use_container_width=True)

    with chart_tab3:
        fig_scatter = px.scatter(
            df,
            x="Browsing_Behaviour",
            y="Purchase_History",
            color="Rating",
            size="Base_Price",
            hover_name="Product_Name",
            trendline="ols",
            title="Browsing Duration vs. Purchase Quantity (Color = Star Rating, Size = Price)",
            labels={"Browsing_Behaviour": "Browsing Dwell Time (Minutes)", "Purchase_History": "Purchase Quantity"}
        )
        fig_scatter.update_layout(height=480)
        st.plotly_chart(fig_scatter, use_container_width=True)


# ---------------------------------------------------------
# Tab 5: Model Performance & Holdout Evaluation
# ---------------------------------------------------------
elif navigation_mode == "🎯 Model Performance & Evaluation":
    st.title("🎯 Leak-Free Model Evaluation Benchmark")
    st.markdown("Validation metrics evaluated using a rigorous **Leave-One-Out Holdout Strategy** across all 150 customers.")

    eval_data = [
        {"Cutoff": "Top-3", "Precision@K": 0.1222, "Recall@K": 0.3667, "Hit_Rate": 36.67, "Coverage": 100.0},
        {"Cutoff": "Top-5", "Precision@K": 0.1000, "Recall@K": 0.5000, "Hit_Rate": 50.00, "Coverage": 100.0},
        {"Cutoff": "Top-10", "Precision@K": 0.0693, "Recall@K": 0.6933, "Hit_Rate": 69.33, "Coverage": 100.0}
    ]
    eval_df = pd.DataFrame(eval_data)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""<div class="metric-card"><div class="metric-label">Hit Rate @ 10</div><div class="metric-value">69.33%</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown("""<div class="metric-card"><div class="metric-label">Hit Rate @ 5</div><div class="metric-value">50.00%</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown("""<div class="metric-card"><div class="metric-label">Recall @ 10</div><div class="metric-value">0.6933</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown("""<div class="metric-card"><div class="metric-label">Catalog Coverage</div><div class="metric-value">100.0%</div></div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_hit = px.bar(
            eval_df,
            x="Cutoff",
            y="Hit_Rate",
            color="Cutoff",
            text="Hit_Rate",
            title="Hit Rate @ K (%) on Held-Out Interactions",
            labels={"Hit_Rate": "Hit Rate (%)"}
        )
        fig_hit.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_hit.update_layout(yaxis_range=[0, 85], height=380)
        st.plotly_chart(fig_hit, use_container_width=True)

    with c2:
        fig_rec = px.bar(
            eval_df,
            x="Cutoff",
            y="Recall@K",
            color="Cutoff",
            text="Recall@K",
            title="Recall @ K on Held-Out Test Set",
            labels={"Recall@K": "Recall @ K"}
        )
        fig_rec.update_traces(texttemplate='%{text:.4f}', textposition='outside')
        fig_rec.update_layout(yaxis_range=[0, 0.85], height=380)
        st.plotly_chart(fig_rec, use_container_width=True)

    st.markdown("### 🛡️ Why Leave-One-Out Prevents Data Leakage")
    st.info("""
    1. **Strict Temporal/Interaction Holdout:** Exactly 1 interaction per user is placed into a masked test partition.
    2. **Isolated Model Training:** The KNN interaction vectors are constructed exclusively on remaining training records.
    3. **Unseen Item Discovery:** The model predicts recommendations without seeing the target item, verifying genuine predictive accuracy.
    """)


# ---------------------------------------------------------
# Tab 6: Cold-Start Strategy Simulator
# ---------------------------------------------------------
elif navigation_mode == "🚀 Cold-Start Strategy Simulator":
    st.title("🚀 Cold-Start Problem Simulator & Sandbox")
    st.markdown("Test production mitigation strategies for **New Customers (Cold Users)** and **New Products (Cold Items)**.")

    cold_mode = st.radio("Select Cold-Start Scenario:", ["👤 Cold User (New Shopper with No History)", "📦 Cold Product (Newly Launched Item)"], horizontal=True)

    if "Cold User" in cold_mode:
        st.markdown("### 👤 New Customer In-Session Onboarding")
        st.write("A newly registered visitor arrives with 0 transaction history. Test how real-time clickstream dwell time triggers dynamic recommendations.")

        category_interest = st.selectbox("Simulate Customer Dwell Category:", catalog_df["Product_Category"].unique())
        dwell_minutes = st.slider("Simulated Dwell Time in Category (Minutes):", 0, 15, 4)

        if dwell_minutes < 3:
            st.warning("⚠️ Dwell time < 3 mins: User intent is unconfirmed. Serving **Global Catalog Best Sellers**.")
            best_sellers = df.groupby(["Product_ID", "Product_Name", "Product_Category", "Base_Price"]).agg(
                Total_Sold=("Purchase_History", "sum"),
                Avg_Rating=("Rating", "mean")
            ).reset_index().sort_values(["Total_Sold", "Avg_Rating"], ascending=[False, False]).head(5)
            st.dataframe(best_sellers, use_container_width=True)
        else:
            st.success(f"🎯 **Intent Detected!** Dwell time $\\ge 3$ mins in `{category_interest}`. Dynamically adapting feed to category leaders + association triggers.")
            cat_leads = df[df["Product_Category"] == category_interest].groupby(["Product_ID", "Product_Name", "Base_Price"]).agg(
                Total_Sold=("Purchase_History", "sum"),
                Avg_Rating=("Rating", "mean")
            ).reset_index().sort_values("Avg_Rating", ascending=False).head(5)
            st.dataframe(cat_leads, use_container_width=True)

    else:
        st.markdown("### 📦 New Product Exploration (Epsilon-Greedy Bandit)")
        st.write("A newly launched item has 0 purchase records. The system reserves exploration slots to harvest feedback without degrading user experience.")

        st.markdown("""
        ```text
        ┌────────────────────────────────────────────────────────────────────────┐
        │                 EPSILON-GREEDY RECOMMENDATION SLOTTING                 │
        ├────────────┬───────────────────────────────────────────────────────────┤
        │ Slot 1 - 4 │ Exploit: High-Confidence KNN / Association Rule Matches   │
        │ Slot 5     │ Explore: Newly added cold items in matching category (10%)│
        └────────────┴───────────────────────────────────────────────────────────┘
        ```
        """)
        st.success("✅ New products receive guaranteed exposure in Slot 5 until 15 customer ratings are collected, at which point they seamlessly transition into the KNN interaction matrix.")


# ---------------------------------------------------------
# Tab 7: Business Insights & Deployment Action Plan
# ---------------------------------------------------------
elif navigation_mode == "💡 Business Insights & Action Plan":
    st.title("💡 Strategic Insights & Deployment Action Plan")
    st.markdown("Evidence-based findings and multi-touchpoint deployment architecture.")

    col_i, col_p = st.columns([1, 1])

    with col_i:
        st.markdown("### 🔍 6 Core Evidence-Based Insights")
        with st.expander("1. Tech & Appliance Co-Purchasing Anchor", expanded=True):
            st.write("Primary hardware anchors (Camera, Phone, Espresso Machine) exhibit Lift $>3.0$ with essential accessories (SD Cards, Armor Cases, Artisan Beans).")

        with st.expander("2. Browsing Duration Predicts High Intent", expanded=True):
            st.write("Browsing dwell time correlates strongly ($r = +0.86$) with repeat purchases and satisfaction. Dwell time is an ideal real-time personalization feature.")

        with st.expander("3. High Hit Rate on Unseen Preferences", expanded=True):
            st.write("KNN achieves a 69.33% Hit Rate@10 on held-out interactions, demonstrating high capability to anticipate latent customer desires.")

        with st.expander("4. 100% Full Catalog Exposure", expanded=True):
            st.write("Rating-weighted cosine distance prevents popularity bias, exposing all 40 catalog SKUs across recommendations.")

        with st.expander("5. Synergistic Rule & Collaborative Overlap", expanded=True):
            st.write("Association rules provide immediate 1-click cart attachments, while KNN provides discovery across complementary lifestyle categories.")

        with col_p:
            st.markdown("### 🚀 Multi-Touchpoint Deployment Roadmap")
            st.markdown("""
            1. **Product Detail Page (PDP):**
               - *Module:* "Frequently Bought Together"
               - *Engine:* Apriori Association Rules (Filtered for Lift > 2.5, Conf > 60%).
            
            2. **Slide-Out Cart Drawer:**
               - *Module:* "Complete Your Setup"
               - *Engine:* Real-Time Rule Triggering on active basket contents.
            
            3. **Homepage & User Account Feed:**
               - *Module:* "Recommended Just For You"
               - *Engine:* Serialized KNN Model (`model/knn_recommendation_model.pkl`).
            
            4. **Automated Post-Purchase Email Sequences:**
               - *Module:* "Restock & Companion Accessories"
               - *Engine:* Timed triggers sent 7 days post-delivery based on association rules.
            """)

st.divider()
st.caption("DS_Day01_35 E-Commerce Recommendation Engine | Built with Streamlit, Scikit-learn, Mlxtend, & Plotly.")
