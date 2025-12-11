#!/usr/bin/env python
"""
FULL PIPELINE

Steps:
1) src/data_load/dataload.py
2) src/features/features.py
3) 6 model scripts in src/models
4) Start Streamlit dashboard
"""

from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).parent
PY = sys.executable  # current Python interpreter


def run(label, script_args):
    print("\n" + "=" * 60)
    print(label)
    print("=" * 60)
    cmd = [PY] + script_args
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    # 1) data load
    run("DATA LOAD", ["src/data_load/dataload.py"])

    # 2) feature build
    run("FEATURE BUILD", ["src/features/features.py"])

    # 3) models
    models = [
        ("MODEL – BAYES", ["src/models/trend_bayes_hierarchical.py"]),
        ("MODEL – MARKOV", ["src/models/trend_markov_switching.py"]),
        ("MODEL – KALMAN", ["src/models/trend_kalman.py"]),
        ("MODEL – RISK", ["src/models/risk_prospect_theory.py"]),
        ("MODEL – MPT", ["src/models/portfolio_mpt.py"]),
        ("MODEL – VALUATION", ["src/models/valuation_nash_real.py"]),
    ]
    for label, args in models:
        run(label, args)

    # 4) dashboard
    run("START DASHBOARD", ["-m", "streamlit", "run", "src/app/dashboard.py"])


if __name__ == "__main__":
    main()
