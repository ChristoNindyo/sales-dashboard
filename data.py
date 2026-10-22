"""Data logic for the dashboard. No Streamlit code in here,
so it is easy to test on its own."""

import numpy as np
import pandas as pd

REGIONS = ["North", "South", "East", "West"]
PRODUCTS = ["Laptop", "Phone", "Tablet", "Headphones"]
PRICES = {"Laptop": 1200, "Phone": 800, "Tablet": 500, "Headphones": 150}
FREQUENCIES = {"Daily": "D", "Weekly": "W", "Monthly": "MS"}


def generate_data(days: int = 365, seed: int = 42) -> pd.DataFrame:
    """Create fake sales data: one row per date x region x product."""
    rng = np.random.default_rng(seed)  # same seed -> same data every run
    dates = pd.date_range(start="2026-01-01", periods=days, freq="D")

    index = pd.MultiIndex.from_product(
        [dates, REGIONS, PRODUCTS], names=["date", "region", "product"]
    )
    df = index.to_frame(index=False)

    # Sales slowly trend upward over time
    day_number = (df["date"] - dates[0]).dt.days.to_numpy()
    expected_units = 4 + 3 * day_number / max(days, 1)
    df["units"] = rng.poisson(lam=expected_units)

    df["unit_price"] = df["product"].map(PRICES)
    df["revenue"] = df["units"] * df["unit_price"]
    return df


def filter_data(df, start_date, end_date, regions, products) -> pd.DataFrame:
    """Keep only rows inside the date range and chosen regions/products."""
    mask = (
        (df["date"] >= pd.Timestamp(start_date))
        & (df["date"] <= pd.Timestamp(end_date))
        & (df["region"].isin(regions))
        & (df["product"].isin(products))
    )
    return df.loc[mask]


def compute_kpis(df) -> dict:
    """Headline numbers. Safe to call on an empty DataFrame."""
    if df.empty:
        return {
            "total_revenue": 0,
            "total_units": 0,
            "avg_daily_revenue": 0,
            "top_product": "-",
        }
    by_product = df.groupby("product")["revenue"].sum()
    return {
        "total_revenue": int(df["revenue"].sum()),
        "total_units": int(df["units"].sum()),
        "avg_daily_revenue": float(df.groupby("date")["revenue"].sum().mean()),
        "top_product": str(by_product.idxmax()),
    }


def revenue_over_time(df, freq: str = "D") -> pd.Series:
    """Revenue summed per day ('D'), week ('W') or month ('MS')."""
    return df.set_index("date")["revenue"].resample(freq).sum()


def revenue_by_product(df) -> pd.Series:
    return df.groupby("product")["revenue"].sum().sort_values(ascending=False)


def revenue_by_region(df) -> pd.Series:
    return df.groupby("region")["revenue"].sum().sort_values(ascending=False)
