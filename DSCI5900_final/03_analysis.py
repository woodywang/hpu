"""
Vibe Retail Capstone — Python Analysis
Group: [NUMBER]   Members: [NAMES]

Run from project root:
    python templates/analysis_template.py

Requirements:
  - Pandas manipulation
  - Lists and dictionaries (Section 4 — core skill)
  - >= 2 visualizations saved to deliverables/charts/
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "deliverables" / "charts"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Load data (relational tables)
# ---------------------------------------------------------------------------
def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load products, sales, stores CSVs."""
    products = pd.read_csv(DATA / "products.csv")
    sales = pd.read_csv(DATA / "sales.csv", parse_dates=["sale_date"])
    stores = pd.read_csv(DATA / "stores.csv")
    return products, sales, stores


# ---------------------------------------------------------------------------
# 2. SQL-equivalent join in Pandas (or load from your SQL export)
# ---------------------------------------------------------------------------
def build_sales_detail(
    products: pd.DataFrame,
    sales: pd.DataFrame,
    stores: pd.DataFrame,
) -> pd.DataFrame:
    """
    JOIN sales + products + stores.
    Add profit column.
    """
    df = sales.merge(products, on="product_id", how="left")
    df = df.merge(stores, on="store_id", how="left")
    df["profit"] = df["total_amount"] - df["cost_price"] * df["quantity"]
    return df


# ---------------------------------------------------------------------------
# 3. KPI helpers
# ---------------------------------------------------------------------------
def revenue_by_store(df: pd.DataFrame) -> pd.DataFrame:
    """aggregate total_amount and quantity by store_location."""
    return (
        df.groupby("store_location", as_index=False)
        .agg(total_revenue=("total_amount", "sum"), total_units=("quantity", "sum"))
        .sort_values("total_revenue", ascending=False)
    )


def quantity_by_product(df: pd.DataFrame) -> pd.DataFrame:
    """aggregate quantity by product_name."""
    return (
        df.groupby(["product_name", "category"], as_index=False)
        .agg(total_units=("quantity", "sum"), total_revenue=("total_amount", "sum"))
        .sort_values("total_units", ascending=False)
    )


# ---------------------------------------------------------------------------
# 4. CORE SKILL — Lists & dictionaries (from your pseudocode)
# ---------------------------------------------------------------------------
def build_product_qty_dict(df: pd.DataFrame) -> dict[str, int]:
    """Build product -> total units sold dictionary."""
    product_qty: dict[str, int] = {}
    summary = (
        df.groupby("product_name", as_index=False)
        .agg(total_units=("quantity", "sum"))
        .sort_values("total_units", ascending=False)
    )
    for row in summary.itertuples(index=False):
        product_qty[row.product_name] = int(row.total_units)
    return product_qty


def build_store_kpi_list(df: pd.DataFrame) -> list[dict]:
    """Build store summary list with revenue, units, rent, and ROI."""
    store_kpis: list[dict] = []
    store_map = (
        df[["store_location", "monthly_rent"]]
        .drop_duplicates()
        .set_index("store_location")["monthly_rent"]
        .to_dict()
    )
    summary = (
        df.groupby("store_location", as_index=False)
        .agg(total_revenue=("total_amount", "sum"), total_units=("quantity", "sum"))
        .sort_values("total_revenue", ascending=False)
    )
    for row in summary.itertuples(index=False):
        rent = float(store_map.get(row.store_location, 0.0))
        revenue = float(row.total_revenue)
        roi = round(revenue / rent, 4) if rent else 0.0
        store_kpis.append(
            {
                "store_location": row.store_location,
                "total_revenue": round(revenue, 2),
                "total_units": int(row.total_units),
                "monthly_rent": round(rent, 2),
                "roi": roi,
            }
        )
    return store_kpis


def build_product_margin_list(df: pd.DataFrame) -> list[dict]:
    """Build product margin summary as list of dicts for Q5."""
    product_margin: list[dict] = []
    summary = (
        df.assign(
            product_total_cost=df["cost_price"] * df["quantity"],
            gross_profit=df["total_amount"] - df["cost_price"] * df["quantity"],
        )
        .groupby(["product_name", "category"], as_index=False)
        .agg(
            total_units=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            total_cost=("product_total_cost", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
    )
    summary["gross_margin_rate"] = (
        summary["gross_profit"] / summary["total_revenue"]
    ).fillna(0.0)
    summary = summary.sort_values("gross_margin_rate", ascending=False)
    for row in summary.itertuples(index=False):
        product_margin.append(
            {
                "product_name": row.product_name,
                "category": row.category,
                "total_units": int(row.total_units),
                "total_revenue": round(float(row.total_revenue), 2),
                "total_cost": round(float(row.total_cost), 2),
                "gross_profit": round(float(row.gross_profit), 2),
                "gross_margin_rate": round(float(row.gross_margin_rate), 4),
            }
        )
    return product_margin


def flag_slow_movers(
    df: pd.DataFrame,
    qty_threshold: int = 3,
    cost_threshold: float = 100.0,
) -> list[dict]:
    """Flag products with low sales but relatively high stock cost."""
    slow_movers: list[dict] = []
    product_risk = (
        df.assign(product_total_cost=df["cost_price"] * df["quantity"])
        .groupby("product_name", as_index=False)
        .agg(total_units=("quantity", "sum"), total_cost=("product_total_cost", "sum"))
    )
    for row in product_risk.itertuples(index=False):
        if row.total_units <= qty_threshold and row.total_cost >= cost_threshold:
            slow_movers.append(
                {
                    "product_name": row.product_name,
                    "total_units": int(row.total_units),
                    "total_cost": round(float(row.total_cost), 2),
                    "risk_flag": "high",
                }
            )
    return slow_movers


def build_store_product_list(df: pd.DataFrame) -> list[dict]:
    """Build store-product ranking list for Q8."""
    store_product_list: list[dict] = []
    summary = (
        df.assign(
            product_total_cost=df["cost_price"] * df["quantity"],
            gross_profit=df["total_amount"] - df["cost_price"] * df["quantity"],
        )
        .groupby(["store_location", "product_name"], as_index=False)
        .agg(
            total_units=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            gross_profit=("gross_profit", "sum"),
        )
        .sort_values("total_revenue", ascending=False)
    )
    for row in summary.itertuples(index=False):
        store_product_list.append(
            {
                "store_location": row.store_location,
                "product_name": row.product_name,
                "total_units": int(row.total_units),
                "total_revenue": round(float(row.total_revenue), 2),
                "gross_profit": round(float(row.gross_profit), 2),
            }
        )
    return store_product_list


def sort_stores_by_revenue(store_kpis: list[dict]) -> list[dict]:
    """Sort store dicts by revenue descending."""
    return sorted(store_kpis, key=lambda x: x["total_revenue"], reverse=True)


def sort_products_by_margin(product_margin_list: list[dict]) -> list[dict]:
    """Sort product margin list by margin rate descending."""
    return sorted(product_margin_list, key=lambda x: x["gross_margin_rate"], reverse=True)


def sort_store_product_by_revenue(store_product_list: list[dict]) -> list[dict]:
    """Sort store-product list by revenue descending."""
    return sorted(store_product_list, key=lambda x: x["total_revenue"], reverse=True)


# ---------------------------------------------------------------------------
# 5. Visualizations (>= 2 required)
# ---------------------------------------------------------------------------
def chart_revenue_by_store(store_df: pd.DataFrame) -> Path:
    """Bar chart — total revenue by store."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(store_df["store_location"], store_df["total_revenue"], color=["#4C72B0", "#55A868", "#C44E52"])
    ax.set_title("Total Revenue by Store")
    ax.set_xlabel("Store")
    ax.set_ylabel("Revenue ($)")
    for bar, value in zip(ax.patches, store_df["total_revenue"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 10, f"${value:.2f}", ha="center", va="bottom")
    plt.tight_layout()
    path = OUT / "chart1_revenue_by_store.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def chart_top_products(product_df: pd.DataFrame) -> Path:
    """Bar chart — top products by units sold."""
    top_df = product_df.sort_values("total_units", ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(top_df["product_name"], top_df["total_units"], color="#4C78A8")
    ax.set_title("Top Products by Units Sold")
    ax.set_xlabel("Product")
    ax.set_ylabel("Units")
    for bar, value in zip(ax.patches, top_df["total_units"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", va="bottom")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    path = OUT / "chart2_top_products.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def chart_margin_by_product(product_margin: list[dict]) -> Path:
    """Bar chart — product gross margin rate comparison."""
    margin_df = pd.DataFrame(product_margin)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(margin_df["product_name"], margin_df["gross_margin_rate"], color="#2CA02C")
    ax.set_title("Product Gross Margin Rate")
    ax.set_xlabel("Product")
    ax.set_ylabel("Gross Margin Rate")
    ax.set_ylim(0, max(1.0, margin_df["gross_margin_rate"].max() * 1.2))
    for bar, value in zip(ax.patches, margin_df["gross_margin_rate"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.2%}", ha="center", va="bottom")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    path = OUT / "chart3_product_margin.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def chart_store_product_performance(store_product: list[dict]) -> Path:
    """Bar chart — store-product revenue performance."""
    perf_df = pd.DataFrame(store_product).head(8)
    labels = perf_df["store_location"] + " - " + perf_df["product_name"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, perf_df["total_revenue"], color="#FF7F0E")
    ax.set_title("Store-Product Revenue Performance")
    ax.set_xlabel("Store - Product")
    ax.set_ylabel("Revenue ($)")
    for bar, value in zip(ax.patches, perf_df["total_revenue"]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 5, f"${value:.2f}", ha="center", va="bottom")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    path = OUT / "chart4_store_product_performance.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


# ---------------------------------------------------------------------------
# 6. Business recommendations (console output)
# ---------------------------------------------------------------------------
def print_recommendations(
    store_kpis: list[dict],
    slow_movers: list[dict],
    product_margin: list[dict],
    store_product: list[dict],
) -> None:
    """Translate analysis into inventory / sales actions."""
    print("\n=== INVENTORY & SALES RECOMMENDATIONS ===\n")
    if store_kpis:
        print("Top store by revenue:", store_kpis[0])
    if slow_movers:
        print("Slow movers (review stock levels):", slow_movers)
    else:
        print("No slow movers identified under current threshold.")
    if product_margin:
        print("Highest margin product:", product_margin[0])
        print("Lowest margin product:", product_margin[-1])
    if store_product:
        print("Best store-product combo:", store_product[0])
        print("Worst store-product combo:", store_product[-1])


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    products, sales, stores = load_tables()
    detail = build_sales_detail(products, sales, stores)

    store_df = revenue_by_store(detail)
    product_df = quantity_by_product(detail)

    # Core skill: lists & dictionaries
    product_qty = build_product_qty_dict(detail)
    store_kpis = sort_stores_by_revenue(build_store_kpi_list(detail))
    product_margin = sort_products_by_margin(build_product_margin_list(detail))
    store_product = sort_store_product_by_revenue(build_store_product_list(detail))
    slow_movers = flag_slow_movers(detail)

    print("Product quantity dictionary:", product_qty)
    print("Store KPI list:", store_kpis)
    print("Product margin list:", product_margin)
    print("Store-product performance list:", store_product)
    print("Slow movers:", slow_movers)

    p1 = chart_revenue_by_store(store_df)
    p2 = chart_top_products(product_df)
    p3 = chart_margin_by_product(product_margin)
    p4 = chart_store_product_performance(store_product)
    print(f"\nSaved charts:\n  {p1}\n  {p2}\n  {p3}\n  {p4}")

    print_recommendations(store_kpis, slow_movers, product_margin, store_product)


if __name__ == "__main__":
    main()
