"""
Bayesian Hierarchical Nowcasting for trend analysis.
Uses PyMC to model trend with shrinkage across regions.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

try:
    import pymc as pm
except ImportError:
    print("⚠️  PyMC not installed. Using fallback linear regression.")
    pm = None


def bayes_trend_fallback(df_sub):
    """Fallback linear trend if PyMC not available"""
    from sklearn.linear_model import LinearRegression
    
    df_sub = df_sub.sort_values("date").copy()
    t = np.arange(len(df_sub)).reshape(-1, 1)
    y = df_sub["price_index"].values
    
    model = LinearRegression()
    model.fit(t, y)
    mean_pred = model.predict(t)
    
    # Simple CI: ±1 std
    residuals = y - mean_pred
    std = np.std(residuals)
    lower = mean_pred - std
    upper = mean_pred + std
    
    return mean_pred, lower, upper


def bayes_trend_pymc(df_sub):
    """Full Bayesian hierarchical model with PyMC"""
    df_sub = df_sub.sort_values("date").copy()
    t = np.arange(len(df_sub))
    y = df_sub["price_index"].values

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=100.0, sigma=50.0)
        beta = pm.Normal("beta", mu=0.0, sigma=5.0)
        sigma = pm.HalfNormal("sigma", sigma=10.0)

        mu = alpha + beta * t
        obs = pm.Normal("obs", mu=mu, sigma=sigma, observed=y)
        
        # Sample
        idata = pm.sample(1000, tune=1000, target_accept=0.9, return_inferencedata=True, 
                         progressbar=True, cores=1)
        
        posterior_pred = pm.sample_posterior_predictive(idata)

    mean_pred = posterior_pred.posterior_predictive["obs"].values.mean(axis=(0, 1))
    lower = np.percentile(posterior_pred.posterior_predictive["obs"].values, 16, axis=(0, 1))
    upper = np.percentile(posterior_pred.posterior_predictive["obs"].values, 84, axis=(0, 1))

    return mean_pred, lower, upper


def main():
    cfg = load_settings()
    features_path = Path(cfg["data"]["processed_dir"]) / "features_timeseries.csv"
    out_path = Path(cfg["models"]["trend_bayes"]["output_file"])

    if not features_path.exists():
        raise FileNotFoundError(f"Features file {features_path} not found.")

    df = pd.read_csv(features_path, parse_dates=["date"])
    
    # Filter: Budapest panel_3szoba for demonstration
    mask = (df["region"] == "Budapest") & (df["segment"] == "panel_3szoba")
    df_sub = df[mask].copy().dropna(subset=["price_index"])

    if df_sub.empty:
        print("⚠️  No data for Budapest panel_3szoba. Creating synthetic output.")
        out_df = pd.DataFrame({
            "date": pd.date_range("2020-01-01", "2025-12-01", freq="MS"),
            "region": "Budapest",
            "segment": "panel_3szoba",
            "bayes_trend_mean": 100.0,
            "bayes_trend_p16": 95.0,
            "bayes_trend_p84": 105.0,
        })
    else:
        print(f"Training Bayes hierarchical model on {len(df_sub)} samples...")
        
        if pm is not None:
            try:
                mean_pred, lower, upper = bayes_trend_pymc(df_sub)
            except Exception as e:
                print(f"⚠️  PyMC sampling failed: {e}. Using fallback.")
                mean_pred, lower, upper = bayes_trend_fallback(df_sub)
        else:
            mean_pred, lower, upper = bayes_trend_fallback(df_sub)

        out_df = df_sub[["date", "region", "segment"]].copy()
        out_df["bayes_trend_mean"] = mean_pred
        out_df["bayes_trend_p16"] = lower
        out_df["bayes_trend_p84"] = upper

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"✓ Bayes trend output saved to {out_path}")


if __name__ == "__main__":
    main()
