"""
Risk assessment via Prospect Theory.
Computes downside probability, expected return, prospect value.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings


def prospect_value(x, alpha=0.88, beta=0.88, lamb=2.25):
    """Kahneman-Tversky prospect value function"""
    v = np.where(
        x >= 0,
        x ** alpha,
        -lamb * ((-x) ** beta)
    )
    return v


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["risk_prospect"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])

    mask = (df["region"] == "Budapest") & (df["segment"] == "panel_3szoba")
    df_sub = df[mask].copy().dropna(subset=["ret"])
    df_sub = df_sub.sort_values("date")

    recent = df_sub["ret"].dropna().tail(36)
    if len(recent) < 12:
        print("⚠️  Not enough recent returns. Using synthetic risk output.")
        expected_ret = 0.03
        downside_prob = 0.25
        exp_prospect = 1.0
    else:
        print(f"Running 5000 Monte Carlo simulations ({len(recent)} recent returns)...")
        sims = []
        n_sims = 5000
        horizon = 12

        for _ in range(n_sims):
            path = np.random.choice(recent.values, size=horizon, replace=True)
            sims.append(path.sum())
        sims = np.array(sims)

        v = prospect_value(sims)
        expected_ret = sims.mean()
        downside_prob = (sims < 0).mean()
        exp_prospect = v.mean()

    out_df = pd.DataFrame({
        "region": ["Budapest"],
        "segment": ["panel_3szoba"],
        "expected_12m_return": [expected_ret],
        "downside_prob_12m": [downside_prob],
        "expected_prospect_value": [exp_prospect],
    })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Risk (prospect theory) output saved to {out_path}")


if __name__ == "__main__":
    main()
