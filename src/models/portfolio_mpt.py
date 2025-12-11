"""
Modern Portfolio Theory (MPT) optimization.
Computes efficient frontier and optimal weights.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

try:
    import cvxpy as cp
except ImportError:
    cp = None


def mpt_fallback(rets, valid_segments):
    """Fallback: equal weights"""
    return np.ones(len(valid_segments)) / len(valid_segments)


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["portfolio"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])

    # Extract unique segments
    segments = df["segment"].unique()
    segments = [s for s in segments if s != 'all'][:3]  # Top 3

    rets = []
    valid_segments = []
    for seg in segments:
        sub = df[(df["segment"] == seg)].copy()
        sub = sub.sort_values("date")
        if sub.empty:
            continue
        sub["ret"] = sub["price_index"].pct_change()
        r = sub["ret"].dropna()
        if len(r) < 12:
            continue
        rets.append(r)
        valid_segments.append(seg)

    if len(rets) < 2:
        print("⚠️  Not enough segments for portfolio optimization.")
        weights = np.ones(len(valid_segments)) / max(1, len(valid_segments))
    else:
        print(f"Building portfolio from {len(valid_segments)} segments...")

        # Align returns by index
        rets_df = pd.concat(rets, axis=1, join="inner")
        rets_df.columns = valid_segments

        if rets_df.empty or len(rets_df) < 2:
            print("⚠️  Not enough aligned return data.")
            weights = np.ones(len(valid_segments)) / len(valid_segments)
        else:
            mu = rets_df.mean().values
            cov = np.cov(rets_df.values.T)

            if cp is not None:
                print("Using cvxpy for MPT optimization...")
                try:
                    n = len(valid_segments)
                    w = cp.Variable(n)
                    target_return = mu.mean()

                    objective = cp.Minimize(cp.quad_form(w, cov))
                    constraints = [
                        cp.sum(w) == 1,
                        w >= 0,
                        mu @ w >= target_return
                    ]
                    prob = cp.Problem(objective, constraints)
                    prob.solve(solver=cp.SCS, verbose=False)

                    weights = w.value if w.value is not None else mpt_fallback(rets_df, valid_segments)
                except Exception as e:
                    print(f"⚠️  cvxpy optimization failed: {e}. Using equal weights.")
                    weights = mpt_fallback(rets_df, valid_segments)
            else:
                print("⚠️  cvxpy not installed. Using equal weights.")
                weights = mpt_fallback(rets_df, valid_segments)

    out_df = pd.DataFrame({
        "segment": valid_segments,
        "weight": weights
    })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Portfolio weights saved to {out_path}")


if __name__ == "__main__":
    main()
