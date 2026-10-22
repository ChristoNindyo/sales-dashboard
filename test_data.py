"""Logic tests. Run with:  pytest"""
import pandas as pd

from data import (
    PRODUCTS,
    REGIONS,
    compute_kpis,
    filter_data,
    generate_data,
    revenue_by_product,
    revenue_over_time,
)


def test_generate_data_shape_and_columns():
    df = generate_data(days=30)
    assert len(df) == 30 * len(REGIONS) * len(PRODUCTS)
    assert set(df.columns) == {"date", "region", "product", "units", "unit_price", "revenue"}
    assert df["revenue"].equals(df["units"] * df["unit_price"])
    assert (df["units"] >= 0).all()


def test_generate_data_is_reproducible():
    assert generate_data(days=10).equals(generate_data(days=10))


def test_filter_by_date_region_product():
    df = generate_data(days=30)
    out = filter_data(df, "2026-01-05", "2026-01-10", ["North"], ["Laptop"])
    assert len(out) == 6  # 6 days x 1 region x 1 product
    assert (out["region"] == "North").all()
    assert (out["product"] == "Laptop").all()
    assert out["date"].min() == pd.Timestamp("2026-01-05")
    assert out["date"].max() == pd.Timestamp("2026-01-10")


def test_filter_with_nothing_selected_returns_empty():
    df = generate_data(days=30)
    assert filter_data(df, "2026-01-01", "2026-01-30", [], PRODUCTS).empty


def test_kpis_match_manual_calculation():
    df = generate_data(days=30)
    k = compute_kpis(df)
    assert k["total_revenue"] == int(df["revenue"].sum())
    assert k["total_units"] == int(df["units"].sum())
    assert k["top_product"] in PRODUCTS


def test_kpis_on_empty_data():
    empty = generate_data(days=5).iloc[0:0]
    assert compute_kpis(empty)["total_revenue"] == 0
    assert compute_kpis(empty)["top_product"] == "-"


def test_revenue_over_time_totals_are_preserved():
    df = generate_data(days=60)
    for freq in ["D", "W", "MS"]:
        assert revenue_over_time(df, freq).sum() == df["revenue"].sum()


def test_revenue_by_product_sorted_and_complete():
    df = generate_data(days=30)
    s = revenue_by_product(df)
    assert set(s.index) == set(PRODUCTS)
    assert s.is_monotonic_decreasing
