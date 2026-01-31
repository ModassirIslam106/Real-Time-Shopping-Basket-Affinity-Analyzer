import streamlit as st
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
if "affinity_df" not in st.session_state:
    st.session_state.affinity_df = None
if "merged_df" not in st.session_state:
    st.session_state.merged_df = None
if "baskets_df" not in st.session_state:
    st.session_state.baskets_df = None
if "top_results" not in st.session_state:
    st.session_state.top_results = None

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Shopping Basket Affinity Analyzer",
    page_icon="🛒",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown("""
<style>
.main-title { font-size: 42px; font-weight: 800; color: #2563EB; }
.section-title { font-size: 28px; font-weight: 700; color: #0EA5A4; margin-top: 20px; }
.sub-text { font-size: 16px; color: #1E293B; }
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
    return line_items.merge(products, on="product_id")

def build_baskets(df):
    return df.groupby("transaction_id")["product_name"].apply(list).reset_index(name="basket")

def generate_pairs(baskets_df):
    pairs = []
    for basket in baskets_df["basket"]:
        basket = set(basket)
        if len(basket) > 1:
            pairs.extend(combinations(sorted(basket), 2))
    return pd.Series(pairs)

def compute_affinity_metrics(pairs, baskets_df):
    total_txn = len(baskets_df)
    pair_counts = pairs.value_counts()
    item_counts = baskets_df["basket"].explode().value_counts()

    rows = []
    for (a, b), cnt in pair_counts.items():
        support = cnt / total_txn
        confidence = cnt / item_counts[a]
        lift = confidence / (item_counts[b] / total_txn)
        rows.append([a, b, round(support,4), round(confidence,4), round(lift,4)])

    return pd.DataFrame(
        rows, columns=["Product A", "Product B", "Support", "Confidence", "Lift"]
    )

def get_top_affinities(df, min_support, min_confidence, top_k):
    return (
        df[(df["Support"] >= min_support) & (df["Confidence"] >= min_confidence)]
        .sort_values("Lift", ascending=False)
        .head(top_k)
    )

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("## ⚙️ Control Panel")

min_support = st.sidebar.slider("Minimum Support", 0.01, 0.2, 0.02, 0.01)
min_confidence = st.sidebar.slider("Minimum Confidence", 0.05, 0.9, 0.3, 0.05)
top_k = st.sidebar.selectbox("Top Product Pairs", [5, 10, 15, 20], index=1)

run_button = st.sidebar.button("🚀 Run Analysis")

# =====================================================
# RUN ANALYSIS (ONCE)
# =====================================================
if run_button:
    with st.spinner("Analyzing shopping baskets..."):
        st.session_state.merged_df = load_data(BASE_PATH)
        st.session_state.baskets_df = build_baskets(st.session_state.merged_df)
        pairs = generate_pairs(st.session_state.baskets_df)
        st.session_state.affinity_df = compute_affinity_metrics(
            pairs, st.session_state.baskets_df
        )
        st.session_state.top_results = get_top_affinities(
            st.session_state.affinity_df, min_support, min_confidence, top_k
        )

    st.success("Analysis completed successfully!")

# =====================================================
# STOP IF NOT RUN
# =====================================================
if st.session_state.affinity_df is None:
    st.info("Run the analysis from the sidebar to see results.")
    st.stop()

merged_df = st.session_state.merged_df
baskets_df = st.session_state.baskets_df
affinity_df = st.session_state.affinity_df
top_results = st.session_state.top_results

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "🛍 Recommendations", "📈 Explainability", "📥 Data"]
)

# ---------------- TAB 1 ----------------
with tab1:
    st.markdown('<div class="section-title">Dashboard Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Transactions", baskets_df.shape[0])
    c2.metric("Products", merged_df["product_name"].nunique())
    c3.metric("Strong Rules", top_results.shape[0])

    st.bar_chart(
        merged_df.groupby("product_name").size().sort_values(ascending=False).head(10)
    )

    st.bar_chart(
        top_results.set_index(
            top_results["Product A"] + " → " + top_results["Product B"]
        )["Lift"]
    )

# ---------------- TAB 2 (FIXED FOREVER) ----------------
with tab2:
    st.markdown('<div class="section-title">Product-Based Recommendations</div>', unsafe_allow_html=True)

    selected_product = st.selectbox(
        "Select a product",
        sorted(merged_df["product_name"].unique()),
        key="product_select"
    )

    rec_a = affinity_df[affinity_df["Product A"] == selected_product].copy()
    rec_b = affinity_df[affinity_df["Product B"] == selected_product].copy()

    rec_a["Recommended Product"] = rec_a["Product B"]
    rec_b["Recommended Product"] = rec_b["Product A"]

    recommendations = pd.concat([rec_a, rec_b], ignore_index=True)

    recommendations = recommendations[
        (recommendations["Support"] >= min_support) &
        (recommendations["Confidence"] >= min_confidence)
    ].sort_values("Lift", ascending=False)

    if recommendations.empty:
        st.warning("No recommendations found for current thresholds.")
    else:
        st.dataframe(
            recommendations[
                ["Recommended Product", "Support", "Confidence", "Lift"]
            ].head(top_k),
            use_container_width=True
        )

# ---------------- TAB 3 ----------------
with tab3:
    fig, ax = plt.subplots()
    ax.scatter(affinity_df["Support"], affinity_df["Confidence"])
    ax.set_xlabel("Support")
    ax.set_ylabel("Confidence")
    st.pyplot(fig)

# ---------------- TAB 4 ----------------
with tab4:
    st.dataframe(top_results, use_container_width=True)
    st.download_button(
        "⬇️ Download Results",
        top_results.to_csv(index=False),
        "affinity_results.csv",
        "text/csv"
    )

st.divider()
st.caption("🚀 Hackathon Project | Shopping Basket Affinity Analyzer")
