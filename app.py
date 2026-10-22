import streamlit as st

from data import (
    FREQUENCIES,
    PRODUCTS,
    REGIONS,
    compute_kpis,
    filter_data,
    generate_data,
    revenue_by_product,
    revenue_by_region,
    revenue_over_time,
)

# 1. Page setup (must be the first Streamlit call)
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")


# 2. Load data. cache_data means it is generated once, not on every click.
@st.cache_data
def load_data():
    return generate_data()


df = load_data()

# 3. Title
st.title("📊 Sales Dashboard")
st.caption("Built with Streamlit. All data is randomly generated dummy data.")

# 4. Sidebar filters
st.sidebar.header("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
selected_regions = st.sidebar.multiselect("Region", REGIONS, default=REGIONS)
selected_products = st.sidebar.multiselect("Product", PRODUCTS, default=PRODUCTS)

# While the user is still picking a range, date_input returns only 1 date.
if len(date_range) != 2:
    st.info("Pick both a start date and an end date in the sidebar.")
    st.stop()

start_date, end_date = date_range
filtered = filter_data(df, start_date, end_date, selected_regions, selected_products)

if filtered.empty:
    st.warning("No data matches your filters. Try selecting more options.")
    st.stop()

# 5. KPI cards
kpis = compute_kpis(filtered)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total revenue", f"${kpis['total_revenue']:,.0f}")
col2.metric("Units sold", f"{kpis['total_units']:,}")
col3.metric("Avg daily revenue", f"${kpis['avg_daily_revenue']:,.0f}")
col4.metric("Top product", kpis["top_product"])

# 6. Tabs with charts and data
tab_trend, tab_breakdown, tab_data = st.tabs(["Trend", "Breakdown", "Raw data"])

with tab_trend:
    granularity = st.selectbox("Group by", list(FREQUENCIES.keys()), index=1)
    st.subheader(f"{granularity} revenue")
    st.line_chart(revenue_over_time(filtered, FREQUENCIES[granularity]))

with tab_breakdown:
    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by product")
        st.bar_chart(revenue_by_product(filtered))
    with right:
        st.subheader("Revenue by region")
        st.bar_chart(revenue_by_region(filtered))

with tab_data:
    st.write(f"{len(filtered):,} rows")
    st.dataframe(filtered)
    st.download_button(
        label="Download as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="sales_filtered.csv",
        mime="text/csv",
    )
