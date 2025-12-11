"""
Valuation via Nash Bargaining + Real Options.
Computes optimal contract price and option value of waiting.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

try:
    from scipy.optimize import minimize
except ImportError:
    minimize = None


def nash_product(vars, a_res, b_res):
    """Nash bargaining product: maximize (u_a) * (u_b)"""
    p = vars[0]
    u_a = p - a_res  # seller utility (higher price = higher utility)
    u_b = b_res - p  # buyer utility (lower price = higher utility)
    if u_a <= 0 or u_b <= 0:
        return 1e6
    return -(u_a * u_b)  # minimize negative product


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["valuation"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])

    mask = (df["region"] == "Budapest") & (df["segment"] == "panel_3szoba")
    df_sub = df[mask].copy().dropna(subset=["price_index"])
    df_sub = df_sub.sort_values("date")

    current_index = df_sub["price_index"].iloc[-1]
    # Mapping: index 100 ≈ 51M HUF (you calibrate this)
    base_price = 51_000_000

    seller_res = 48_000_000
    buyer_res = 52_000_000

    if minimize is not None:
        print("Solving Nash bargaining problem...")
        try:
            res = minimize(
                nash_product,
                x0=[base_price],
                args=(seller_res, buyer_res),
                bounds=[(seller_res, buyer_res)]
            )
            nash_price = float(res.x[0])
        except Exception as e:
            print(f"⚠️  Nash optimization failed: {e}. Using midpoint.")
            nash_price = (seller_res + buyer_res) / 2
    else:
        print("⚠️  scipy not installed. Using midpoint.")
        nash_price = (seller_res + buyer_res) / 2

    # Option value of waiting: proportional to volatility
    df_sub["ret"] = df_sub["price_index"].pct_change()
    vol = df_sub["ret"].dropna().std()
    option_value_wait = vol * 1_000_000

    out_df = pd.DataFrame({
        "region": ["Budapest"],
        "segment": ["panel_3szoba"],
        "current_price_guess": [base_price],
        "nash_price": [nash_price],
        "option_value_wait": [option_value_wait]
    })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Valuation output saved to {out_path}")


if __name__ == "__main__":
    main()
