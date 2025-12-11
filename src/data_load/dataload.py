"""
Data loading and ingestion module.
Loads MNB, KSH, and ingatlan.com data from CSV files.
"""

import pandas as pd
from pathlib import Path
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings


def load_mnb_data():
    """Load and normalize MNB lakásárindex data"""
    cfg = load_settings()
    raw_dir = Path(cfg["data"]["raw_dir"])
    processed_dir = Path(cfg["data"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    mnb_file = raw_dir / "mnb_lakasarindex.csv"
    if not mnb_file.exists():
        print(f"⚠️  MNB file {mnb_file} not found. Creating dummy data for demo.")
        # Create dummy data for demonstration
        import numpy as np
        dates = pd.date_range('2020-01-01', '2025-12-01', freq='Q')
        df = pd.DataFrame({
            'date': dates,
            'region': 'National',
            'price_index': 100 + np.cumsum(np.random.randn(len(dates)) * 2),
            'source': 'MNB'
        })
    else:
        df = pd.read_csv(mnb_file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        df['source'] = 'MNB'

    df.to_csv(processed_dir / "mnb_lakasarindex_normalized.csv", index=False)
    print(f"✓ MNB data loaded: {len(df)} rows")
    return df


def load_ksh_data():
    """Load and normalize KSH lakásárindex data"""
    cfg = load_settings()
    raw_dir = Path(cfg["data"]["raw_dir"])
    processed_dir = Path(cfg["data"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    ksh_file = raw_dir / "ksh_lakasarindex.csv"
    if not ksh_file.exists():
        print(f"⚠️  KSH file {ksh_file} not found. Creating dummy data for demo.")
        import numpy as np
        dates = pd.date_range('2020-01-01', '2025-12-01', freq='Q')
        df = pd.DataFrame({
            'date': dates,
            'region': 'National',
            'price_index': 100 + np.cumsum(np.random.randn(len(dates)) * 1.5),
            'source': 'KSH'
        })
    else:
        df = pd.read_csv(ksh_file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        df['source'] = 'KSH'

    df.to_csv(processed_dir / "ksh_lakasarindex_normalized.csv", index=False)
    print(f"✓ KSH data loaded: {len(df)} rows")
    return df


def load_ingatlan_com_data():
    """Load and normalize ingatlan.com monthly index data"""
    cfg = load_settings()
    raw_dir = Path(cfg["data"]["raw_dir"])
    processed_dir = Path(cfg["data"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    ic_file = raw_dir / "ingatlancom_monthly_index.csv"
    if not ic_file.exists():
        print(f"⚠️  ingatlan.com file {ic_file} not found. Creating dummy data for demo.")
        import numpy as np
        dates = pd.date_range('2020-01-01', '2025-12-01', freq='MS')
        cities = ['Budapest', 'Debrecen', 'Győr']
        segments = ['panel_3szoba', 'csaladi_haz', 'tegla_lakas']
        
        data = []
        for city in cities:
            for segment in segments:
                for date in dates:
                    data.append({
                        'date': date,
                        'region': city,
                        'segment': segment,
                        'price_index': 100 + np.random.randn() * 5,
                        'source': 'ingatlan.com'
                    })
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(ic_file)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        df['source'] = 'ingatlan.com'

    df.to_csv(processed_dir / "ingatlancom_index_normalized.csv", index=False)
    print(f"✓ ingatlan.com data loaded: {len(df)} rows")
    return df


def unify_datasets():
    """Merge all normalized datasets into one"""
    cfg = load_settings()
    processed_dir = Path(cfg["data"]["processed_dir"])
    unified_path = Path(cfg["data"]["unified_file"])

    files = [
        processed_dir / "mnb_lakasarindex_normalized.csv",
        processed_dir / "ksh_lakasarindex_normalized.csv",
        processed_dir / "ingatlancom_index_normalized.csv",
    ]

    dfs = []
    for f in files:
        if f.exists():
            dfs.append(pd.read_csv(f))
        else:
            print(f"⚠️  {f} missing, skipping.")

    if not dfs:
        raise RuntimeError("No normalized files found.")

    df = pd.concat(dfs, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])
    
    # Fill NaN segments with 'all'
    df['segment'] = df['segment'].fillna('all')
    
    df = df.sort_values(['region', 'segment', 'date'], na_position='last')
    df.to_csv(unified_path, index=False)
    print(f"✓ Unified dataset: {len(df)} rows → {unified_path}")
    return df


if __name__ == "__main__":
    print("Loading MNB data...")
    load_mnb_data()
    print("\nLoading KSH data...")
    load_ksh_data()
    print("\nLoading ingatlan.com data...")
    load_ingatlan_com_data()
    print("\nUnifying datasets...")
    unify_datasets()
    print("\n✓ All data loaded and unified!")
