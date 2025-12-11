#!/bin/bash
set -e

echo "=========================================="
echo "Training All Models"
echo "=========================================="

echo "1. Bayes Hierarchical Trend..."
python -m src.models.trend_bayes_hierarchical

echo ""
echo "2. Markov-Switching Regimes..."
python -m src.models.trend_markov_switching

echo ""
echo "3. Kalman + Theil-Sen..."
python -m src.models.trend_kalman_theilsen

echo ""
echo "4. Risk (Prospect Theory)..."
python -m src.models.risk_prospect_theory

echo ""
echo "5. Valuation (Nash + Real Options)..."
python -m src.models.valuation_nash_real_options

echo ""
echo "6. Portfolio (MPT)..."
python -m src.models.portfolio_mpt

echo ""
echo "✓ All models trained!"
