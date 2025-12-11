"""
FastAPI backend for decision support.
Serves trend, risk, valuation, and portfolio outputs.
"""

from fastapi import FastAPI, Query
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

app = FastAPI(
    title="Real Estate Decision Support API",
    version="0.1.0",
    description="ML-driven decision support for private real estate owners"
)

cfg = load_settings()
processed_dir = Path(cfg["data"]["processed_dir"])


class TrendResponse(BaseModel):
    city: str
    segment: str
    bayes_trend_mean: float | None = None
    regime: str | None = None


class RiskResponse(BaseModel):
    city: str
    segment: str
    expected_12m_return: float | None = None
    downside_prob_12m: float | None = None


class ValuationResponse(BaseModel):
    city: str
    segment: str
    nash_price: float | None = None
    option_value_wait: float | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/trend", response_model=TrendResponse)
def get_trend(
    city: str = Query("Budapest"),
    segment: str = Query("panel_3szoba")
):
    """Get trend analysis (Bayes + Markov)"""
    bayes_path = Path(cfg["models"]["trend_bayes"]["output_file"])
    markov_path = Path(cfg["models"]["trend_markov"]["output_file"])

    bayes_mean = None
    regime = None

    if bayes_path.exists():
        df_b = pd.read_csv(bayes_path, parse_dates=["date"])
        latest_b = df_b[(df_b["region"] == city) & (df_b["segment"] == segment)].sort_values("date").tail(1)
        if not latest_b.empty:
            bayes_mean = float(latest_b["bayes_trend_mean"].iloc[0])

    if markov_path.exists():
        df_m = pd.read_csv(markov_path, parse_dates=["date"])
        latest_m = df_m[(df_m["region"] == city) & (df_m["segment"] == segment)].sort_values("date").tail(1)
        if not latest_m.empty:
            regime = str(latest_m["regime"].iloc[0])

    return TrendResponse(city=city, segment=segment, bayes_trend_mean=bayes_mean, regime=regime)


@app.get("/risk", response_model=RiskResponse)
def get_risk(
    city: str = Query("Budapest"),
    segment: str = Query("panel_3szoba")
):
    """Get risk assessment (Prospect Theory)"""
    risk_path = Path(cfg["models"]["risk_prospect"]["output_file"])

    ret = None
    downside = None

    if risk_path.exists():
        df_r = pd.read_csv(risk_path)
        df_r = df_r[(df_r["region"] == city) & (df_r["segment"] == segment)]
        if not df_r.empty:
            r = df_r.iloc[0]
            ret = float(r["expected_12m_return"])
            downside = float(r["downside_prob_12m"])

    return RiskResponse(city=city, segment=segment, expected_12m_return=ret, downside_prob_12m=downside)


@app.get("/valuation", response_model=ValuationResponse)
def get_valuation(
    city: str = Query("Budapest"),
    segment: str = Query("panel_3szoba")
):
    """Get valuation (Nash bargaining)"""
    val_path = Path(cfg["models"]["valuation"]["output_file"])

    nash = None
    option = None

    if val_path.exists():
        df_v = pd.read_csv(val_path)
        df_v = df_v[(df_v["region"] == city) & (df_v["segment"] == segment)]
        if not df_v.empty:
            v = df_v.iloc[0]
            nash = float(v["nash_price"])
            option = float(v["option_value_wait"])

    return ValuationResponse(city=city, segment=segment, nash_price=nash, option_value_wait=option)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
