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
ROOT = Path(__file__).resolve().parents[1]
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
    """
    Pseudocode: BUILD dictionary — key = product_name, value = total quantity sold.

  YOUR WORK: implement using a loop or dict comprehension after groupby.
    """
    product_qty: dict[str, int] = {}
    # TODO: fill product_qty from df
    # Example pattern:
    # for row in quantity_by_product(df).itertuples():
    #     product_qty[row.product_name] = int(row.total_units)
    return product_qty


def build_store_kpi_list(df: pd.DataFrame) -> list[dict]:
    """
    Pseudocode: BUILD list of dictionaries — one dict per store with KPIs.

    Each dict should include keys like:
      store_location, total_revenue, total_units, avg_sale
    """
    store_kpis: list[dict] = []
    # TODO: loop over stores and append dicts
    return store_kpis


def flag_slow_movers(product_qty: dict[str, int], threshold: int = 8) -> list[dict]:
    """
    Pseudocode: products with quantity below threshold → overstock risk.

    Returns list of dicts: {product_name, total_units, flag}
    """
    slow_movers: list[dict] = []
    # TODO: iterate product_qty and append when below threshold
    return slow_movers


def sort_stores_by_revenue(store_kpis: list[dict]) -> list[dict]:
    """Pseudocode: SORT list of store dicts by revenue descending."""
    # TODO: return sorted(store_kpis, key=..., reverse=True)
    return store_kpis


# ---------------------------------------------------------------------------
# 5. Visualizations (>= 2 required)
# ---------------------------------------------------------------------------
def chart_revenue_by_store(store_df: pd.DataFrame) -> Path:
    """Bar chart — total revenue by store."""
    fig, ax = plt.subplots(figsize=(8, 5))
    # TODO: ax.bar(store_df['store_location'], store_df['total_revenue'], ...)
    ax.set_title("Total Revenue by Store")
    ax.set_xlabel("Store")
    ax.set_ylabel("Revenue ($)")
    plt.tight_layout()
    path = OUT / "chart1_revenue_by_store.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def chart_top_products(product_df: pd.DataFrame) -> Path:
    """Bar chart — top products by units sold."""
    fig, ax = plt.subplots(figsize=(9, 5))
    # TODO: plot product_df head
    ax.set_title("Top Products by Units Sold")
    ax.set_xlabel("Product")
    ax.set_ylabel("Units")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    path = OUT / "chart2_top_products.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


# ---------------------------------------------------------------------------
# 6. Business recommendations (console output)
# ---------------------------------------------------------------------------
def print_recommendations(
    store_kpis: list[dict],
    slow_movers: list[dict],
) -> None:
    """Translate analysis into inventory / sales actions."""
    print("\n=== INVENTORY & SALES RECOMMENDATIONS ===\n")
    # TODO: print top store, slow movers, suggested actions
    if store_kpis:
        print("Top store by revenue:", store_kpis[0])
    if slow_movers:
        print("Slow movers (review stock levels):", slow_movers)
    else:
        print("(Complete slow_movers logic in Section 4)")


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
    slow_movers = flag_slow_movers(product_qty, threshold=8)

    print("Product quantity dictionary:", product_qty)
    print("Store KPI list:", store_kpis)
    print("Slow movers:", slow_movers)

    p1 = chart_revenue_by_store(store_df)
    p2 = chart_top_products(product_df)
    print(f"\nSaved charts:\n  {p1}\n  {p2}")

    print_recommendations(store_kpis, slow_movers)


if __name__ == "__main__":
    main()
