import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
import os

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Shopping Basket Affinity Analyzer",
    page_icon="🛒",
    layout="wide"
)

# ==============================
# CUSTOM CSS (Fonts & Styling)
# ==============================
st.markdown("""
<style>
/* Main page title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #2563EB; /* Bright Blue */
}

/* Section headers */
.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 30px;
    color: #0EA5A4; /* Teal */
}

/* Supporting text */
.sub-text {
    font-size: 16px;
    color: #1E293B; /* Dark slate for readability */
}

/* Buttons only (no sidebar changes) */
div.stButton > button {
    background-color: #2563EB;
    color: white;
    font-weight: 600;
    border-radius: 8px;
}

div.stButton > button:hover {
    background-color: #1D4ED8;
}
</style>
""", unsafe_allow_html=True)



# ==============================
# HEADER
# ==============================
st.markdown('<div class="main-title">🛒 Shopping Basket Affinity Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-text">Discover products frequently bought together using association rule mining.</p>',
    unsafe_allow_html=True
)

st.divider()

# ==============================
# BASE PATH
# ==============================
BASE_PATH = r"D:\Shopping Basket affinity"

# ==============================
# MODEL FUNCTIONS
# ==============================
@st.cache_data
def load_data(base_path):
    products = pd.read_csv(f"{base_path}/data/raw/products.csv")
    line_items = pd.read_csv(f"{base_path}/data/raw/store_sales_line_items.csv")
    merged = line_items.merge(products, on="product_id")
    return merged


def build_baskets(merged_df):
    baskets = (
        merged_df
        .groupby("transaction_id")["product_name"]
        .apply(list)
        .reset_index()
        .rename(columns={"product_name": "basket"})
    )
    return baskets


def generate_pairs(baskets_df):
    pairs = []
    for basket in baskets_df["basket"]:
        unique_items = set(basket)
        if len(unique_items) > 1:
            pairs.extend(combinations(sorted(unique_items), 2))
    return pd.Series(pairs)


def compute_affinity_metrics(pairs, baskets_df):
    total_transactions = len(baskets_df)
    pair_counts = pairs.value_counts()

    item_counts = (
        baskets_df["basket"]
        .explode()
        .value_counts()
    )

    results = []
    for (a, b), count in pair_counts.items():
        support = count / total_transactions
        confidence = count / item_counts[a]
        lift = confidence / (item_counts[b] / total_transactions)

        results.append({
            "Product A": a,
            "Product B": b,
            "Support": round(support, 4),
            "Confidence": round(confidence, 4),
            "Lift": round(lift, 4)
        })

    return pd.DataFrame(results)


def get_top_affinities(df, min_support, min_confidence, top_k):
    filtered = df[
        (df["Support"] >= min_support) &
        (df["Confidence"] >= min_confidence)
    ]
    return filtered.sort_values("Lift", ascending=False).head(top_k)


# ==============================
# SIDEBAR (USER INPUTS)
# ==============================
st.sidebar.markdown("## ⚙️ Control Panel")

min_support = st.sidebar.slider(
    "Minimum Support",
    min_value=0.01,
    max_value=0.2,
    value=0.02,
    step=0.01
)

min_confidence = st.sidebar.slider(
    "Minimum Confidence",
    min_value=0.05,
    max_value=0.9,
    value=0.3,
    step=0.05
)

top_k = st.sidebar.selectbox(
    "Top Product Pairs",
    options=[5, 10, 15, 20],
    index=1
)

run_button = st.sidebar.button("🚀 Run Affinity Analysis")

# ==============================
# MAIN EXECUTION
# ==============================
if run_button:
    with st.spinner("Analyzing shopping baskets..."):
        merged_df = load_data(BASE_PATH)
        baskets_df = build_baskets(merged_df)
        pairs = generate_pairs(baskets_df)
        affinity_df = compute_affinity_metrics(pairs, baskets_df)

        top_results = get_top_affinities(
            affinity_df,
            min_support,
            min_confidence,
            top_k
        )

    st.success("Analysis completed successfully!")

    # ==============================
    # METRICS
    # ==============================
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", baskets_df.shape[0])
    col2.metric("Unique Products", merged_df["product_name"].nunique())
    col3.metric("Strong Affinities Found", top_results.shape[0])

    # ==============================
    # RESULTS TABLE
    # ==============================
    st.markdown('<div class="section-title">🔍 Top Product Affinities</div>', unsafe_allow_html=True)
    st.dataframe(top_results, use_container_width=True)

    # ==============================
    # BUSINESS INSIGHT
    # ==============================
    if not top_results.empty:
        top_rule = top_results.iloc[0]
        st.info(
            f"💡 Customers who buy **{top_rule['Product A']}** "
            f"are **{top_rule['Lift']}x more likely** to buy **{top_rule['Product B']}**."
        )

else:
    st.markdown(
        "<p class='sub-text'>Adjust the parameters in the sidebar and click <b>Run Affinity Analysis</b> to see results.</p>",
        unsafe_allow_html=True
    )

# ==============================
# FOOTER
# ==============================
st.divider()
st.caption("Built for Hackathon | Shopping Basket Affinity Analyzer 🚀")
