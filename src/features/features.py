"""
Feature engineering module.
Builds lag features, rolling volatility, etc.
"""

import pandas as pd
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings


def add_lags(df, group_cols, target_col, lags=(1, 3, 6, 12)):
    """Add lagged features"""
    df = df.sort_values(group_cols + ["date"])
    for l in lags:
        df[f"{target_col}_lag{l}"] = df.groupby(group_cols)[target_col].shift(l)
    return df


def add_rolling_features(df, group_cols, target_col, windows=(3, 6, 12)):
    """Add rolling standard deviation"""
    for w in windows:
        df[f"{target_col}_rolling_std_{w}"] = (
            df.groupby(group_cols)[target_col]
            .rolling(window=w, min_periods=2)
            .std()
            .reset_index(level=list(range(len(group_cols))), drop=True)
        )
    return df


def build_features():
    """Build all features from unified dataset"""
    cfg = load_settings()
    unified_path = Path(cfg["data"]["unified_file"])
    processed_dir = Path(cfg["data"]["processed_dir"])

    if not unified_path.exists():
        raise FileNotFoundError(f"Unified dataset {unified_path} not found. Run dataload.py first.")

    df = pd.read_csv(unified_path, parse_dates=["date"])
    print(f"Loaded {len(df)} rows from {unified_path}")

    # Ensure price_index is numeric
    df["price_index"] = pd.to_numeric(df["price_index"], errors='coerce')
    df = df.dropna(subset=["price_index"])

    group_cols = ["region", "segment"]

    # Add lags
    print("Adding lag features...")
    df = add_lags(df, group_cols, "price_index", lags=(1, 3, 6, 12))

    # Add rolling volatility
    print("Adding rolling volatility...")
    df = add_rolling_features(df, group_cols, "price_index", windows=(3, 6, 12))

    # Calculate returns
    print("Adding returns...")
    df = df.sort_values(group_cols + ["date"])
    df["ret"] = df.groupby(group_cols)["price_index"].pct_change()

    out_path = processed_dir / "features_timeseries.csv"
    df.to_csv(out_path, index=False)
    print(f"✓ Features saved to {out_path}")
    return df


if __name__ == "__main__":
    build_features()
