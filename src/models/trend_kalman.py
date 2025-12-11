"""
Kalman Filter + Theil-Sen robust trend.
Filters noise and computes robust slope.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

try:
    from pykalman import KalmanFilter
except ImportError:
    KalmanFilter = None

try:
    from sklearn.linear_model import TheilSenRegressor
except ImportError:
    TheilSenRegressor = None


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["trend_kalman"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])

    mask = (df["region"] == "Budapest") & (df["segment"] == "panel_3szoba")
    df_sub = df[mask].copy().dropna(subset=["price_index"])
    df_sub = df_sub.sort_values("date")

    y = df_sub["price_index"].values

    # Kalman filter
    if KalmanFilter is not None:
        print("Applying Kalman filter...")
        try:
            kf = KalmanFilter(
                transition_matrices=[1],
                observation_matrices=[1],
                initial_state_mean=y[0],
                initial_state_covariance=1,
                observation_covariance=1,
                transition_covariance=0.1,
            )
            state_means, _ = kf.filter(y)
        except Exception as e:
            print(f"⚠️  Kalman fit failed: {e}. Using raw data.")
            state_means = y
    else:
        print("⚠️  pykalman not installed. Using raw data.")
        state_means = y

    # Theil-Sen robust slope
    if TheilSenRegressor is not None:
        print("Computing Theil-Sen slope...")
        try:
            t = np.arange(len(y)).reshape(-1, 1)
            ts_model = TheilSenRegressor()
            ts_model.fit(t, y)
            slope = ts_model.coef_[0]
        except Exception as e:
            print(f"⚠️  Theil-Sen fit failed: {e}. Using OLS.")
            slope = np.polyfit(np.arange(len(y)), y, 1)[0]
    else:
        print("⚠️  sklearn not installed. Using OLS.")
        slope = np.polyfit(np.arange(len(y)), y, 1)[0]

    out_df = df_sub[["date", "region", "segment"]].copy()
    out_df["kalman_trend"] = state_means
    out_df["theilsen_slope"] = slope

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Kalman + Theil-Sen output saved to {out_path}")


if __name__ == "__main__":
    main()
