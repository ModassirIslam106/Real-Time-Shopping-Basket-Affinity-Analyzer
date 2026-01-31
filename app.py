import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt


if "affinity_df" not in st.session_state:
    st.session_state.affinity_df = None

if "merged_df" not in st.session_state:
    st.session_state.merged_df = None

if "baskets_df" not in st.session_state:
    st.session_state.baskets_df = None


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Shopping Basket Affinity Analyzer",
    page_icon="🛒",
    layout="wide"
)

# =====================================================
# CUSTOM CSS (HEADINGS ONLY – SIDEBAR UNCHANGED)
# =====================================================
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #2563EB;
}
.section-title {
    font-size: 28px;
    font-weight: 700;
    color: #0EA5A4;
    margin-top: 20px;
}
.sub-text {
    font-size: 16px;
    color: #1E293B;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown('<div class="main-title">🛒 Shopping Basket Affinity Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-text">Interactive analysis of products frequently bought together using association rule mining.</p>',
    unsafe_allow_html=True
)
st.divider()

# =====================================================
# BASE PATH
# =====================================================
BASE_PATH = r"D:\Shopping Basket affinity"

# =====================================================
# DATA & MODEL FUNCTIONS
# =====================================================
@st.cache_data
def load_data(base_path):
    products = pd.read_csv(f"{base_path}/data/raw/products.csv")
    line_items = pd.read_csv(f"{base_path}/data/raw/store_sales_line_items.csv")
    merged = line_items.merge(products, on="product_id")
    return merged


def build_baskets(merged_df):
    return (
        merged_df
        .groupby("transaction_id")["product_name"]
        .apply(list)
        .reset_index()
        .rename(columns={"product_name": "basket"})
    )


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

# =====================================================
# SIDEBAR CONTROLS
# =====================================================
st.sidebar.markdown("## ⚙️ Control Panel")

min_support = st.sidebar.slider(
    "Minimum Support",
    0.01, 0.2, 0.02, 0.01
)

min_confidence = st.sidebar.slider(
    "Minimum Confidence",
    0.05, 0.9, 0.3, 0.05
)

top_k = st.sidebar.selectbox(
    "Top Product Pairs",
    [5, 10, 15, 20],
    index=1
)

run_button = st.sidebar.button("🚀 Run Analysis")

# =====================================================
# MAIN EXECUTION
# =====================================================
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

    # =================================================
    # TABS
    # =================================================
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Dashboard", "🛍 Recommendations", "📈 Explainability", "📥 Data"]
    )

    # -------------------------------
    # TAB 1: DASHBOARD
    # -------------------------------
    with tab1:
        st.markdown('<div class="section-title">Dashboard Overview</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("🧾 Transactions", baskets_df.shape[0])
        col2.metric("📦 Products", merged_df["product_name"].nunique())
        col3.metric("🔗 Strong Rules", top_results.shape[0])

        st.markdown("### 📦 Top Selling Products")
        product_counts = (
            merged_df.groupby("product_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(product_counts)

        st.markdown("### 🔗 Top Product Affinities (Lift)")
        lift_chart = top_results.set_index(
            top_results["Product A"] + " → " + top_results["Product B"]
        )["Lift"]
        st.bar_chart(lift_chart)

    # -------------------------------
    # TAB 2: PRODUCT RECOMMENDATIONS
    # -------------------------------
        # -------------------------------
    # TAB 2: PRODUCT RECOMMENDATIONS
    # -------------------------------
    # -------------------------------
    # TAB 2: PRODUCT RECOMMENDATIONS (FIXED)
    # -------------------------------
    with tab2:
        st.markdown(
            '<div class="section-title">Product-Based Recommendations</div>',
            unsafe_allow_html=True
        )

        selected_product = st.selectbox(
            "Select a product",
            sorted(merged_df["product_name"].unique())
        )

        # USE FULL affinity_df (NOT top_results)
        rec_a = affinity_df[affinity_df["Product A"] == selected_product].copy()
        rec_b = affinity_df[affinity_df["Product B"] == selected_product].copy()

        # Normalize direction
        rec_a["Recommended Product"] = rec_a["Product B"]
        rec_b["Recommended Product"] = rec_b["Product A"]

        recommendations = pd.concat([rec_a, rec_b], ignore_index=True)

        # Apply thresholds HERE (dynamic)
        recommendations = recommendations[
            (recommendations["Support"] >= min_support) &
            (recommendations["Confidence"] >= min_confidence)
        ].sort_values("Lift", ascending=False)

        if recommendations.empty:
            st.warning(
                "No recommendations found for this product with current thresholds. "
                "Try lowering support or confidence."
            )
        else:
            st.success(f"Customers who buy **{selected_product}** also buy:")
            st.dataframe(
                recommendations[
                    ["Recommended Product", "Support", "Confidence", "Lift"]
                ].head(10),
                use_container_width=True
            )


    # -------------------------------
    # TAB 3: EXPLAINABILITY
    # -------------------------------
    with tab3:
        st.markdown('<div class="section-title">Insights & Explainability</div>', unsafe_allow_html=True)

        st.info("""
        **How to interpret the metrics:**

        • **Support** → How often products are bought together  
        • **Confidence** → Likelihood of buying B after A  
        • **Lift** → Strength of relationship (>1 is meaningful)
        """)

        fig, ax = plt.subplots()
        ax.scatter(affinity_df["Support"], affinity_df["Confidence"])
        ax.set_xlabel("Support")
        ax.set_ylabel("Confidence")
        ax.set_title("Support vs Confidence")
        st.pyplot(fig)

    # -------------------------------
    # TAB 4: DATA & DOWNLOAD
    # -------------------------------
    with tab4:
        st.markdown('<div class="section-title">Data Preview & Export</div>', unsafe_allow_html=True)

        st.dataframe(top_results, use_container_width=True)

        csv = top_results.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download Affinity Results",
            csv,
            "product_affinity_results.csv",
            "text/csv"
        )

else:
    st.markdown(
        "<p class='sub-text'>Adjust parameters in the sidebar and click <b>Run Analysis</b>.</p>",
        unsafe_allow_html=True
    )

st.divider()
st.caption("🚀 Hackathon Project | Shopping Basket Affinity Analyzer")
