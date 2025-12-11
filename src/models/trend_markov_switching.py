"""
Markov-Switching regime detection.
Identifies states: up, sideways, down.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

try:
    from hmmlearn.hmm import GaussianHMM
except ImportError:
    print("⚠️  hmmlearn not installed. Using fallback classification.")
    GaussianHMM = None


def markov_fallback(returns):
    """Fallback: classify based on simple thresholds"""
    regimes = []
    for ret in returns:
        if ret > 0.01:
            regimes.append("up")
        elif ret < -0.01:
            regimes.append("down")
        else:
            regimes.append("sideways")
    return regimes


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["trend_markov"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])

    # Filter
    mask = (df["region"] == "Budapest") & (df["segment"] == "panel_3szoba")
    df_sub = df[mask].copy().dropna(subset=["price_index"])
    df_sub = df_sub.sort_values("date")

    df_sub["ret"] = df_sub["price_index"].pct_change()
    returns = df_sub["ret"].dropna().values

    if len(returns) < 3:
        print("⚠️  Not enough returns data. Using synthetic regimes.")
        regimes = ["sideways"] * len(returns)
    elif GaussianHMM is not None:
        print(f"Training Markov-Switching HMM on {len(returns)} returns...")
        try:
            X = returns.reshape(-1, 1)
            model = GaussianHMM(n_components=3, covariance_type="diag", n_iter=100)
            model.fit(X)
            states = model.predict(X)

            # Map to regime names
            means = [returns[states == i].mean() if (states == i).sum() > 0 else 0 for i in range(3)]
            order = np.argsort(means)
            regime_map = {order[0]: "down", order[1]: "sideways", order[2]: "up"}
            regimes = [regime_map[s] for s in states]
        except Exception as e:
            print(f"⚠️  HMM fit failed: {e}. Using fallback.")
            regimes = markov_fallback(returns)
    else:
        regimes = markov_fallback(returns)

    out_df = pd.DataFrame({
        "date": df_sub["date"].iloc[1:].values,
        "region": "Budapest",
        "segment": "panel_3szoba",
        "regime": regimes
    })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Markov regime output saved to {out_path}")


if __name__ == "__main__":
    main()
