"""
Streamlit dashboard for decision support.
Visualizes trends, risks, valuations, and portfolio recommendations.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src import load_settings

cfg = load_settings()
processed_dir = Path(cfg["data"]["processed_dir"])

# Page config
st.set_page_config(
    page_title="Ingatlan Döntéstámogató",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 Ingatlan Döntéstámogató – Prototípus")
st.markdown("ML-alapú döntéstámogató rendszer magánszemély ingatlantulajdonosoknak")

# Sidebar filters
st.sidebar.header("Szűrők")
city = st.sidebar.selectbox("Város", ["Budapest", "Debrecen", "Győr"])
segment = st.sidebar.selectbox("Szegmens", ["panel_3szoba", "csaladi_haz", "tegla_lakas"])

# Load data
bayes_path = Path(cfg["models"]["trend_bayes"]["output_file"])
markov_path = Path(cfg["models"]["trend_markov"]["output_file"])
risk_path = Path(cfg["models"]["risk_prospect"]["output_file"])
val_path = Path(cfg["models"]["valuation"]["output_file"])
port_path = Path(cfg["models"]["portfolio"]["output_file"])

# Layout
col1, col2 = st.columns(2)

# ===== TREND =====
with col1:
    st.header("📈 Trendkép")
    
    if bayes_path.exists():
        try:
            df_b = pd.read_csv(bayes_path, parse_dates=["date"])
            df_b = df_b[(df_b["region"] == city) & (df_b["segment"] == segment)]
            
            if not df_b.empty:
                st.line_chart(
                    df_b.set_index("date")[["bayes_trend_mean", "bayes_trend_p16", "bayes_trend_p84"]],
                    use_container_width=True
                )
            else:
                st.info(f"Nincs Bayes-trend: {city} / {segment}")
        except Exception as e:
            st.error(f"Error loading Bayes trend: {e}")
    else:
        st.warning("⚠️  Bayes trend output hiányzik. Futtassa: `python -m src.models.trend_bayes_hierarchical`")

    # Markov regime
    if markov_path.exists():
        try:
            df_m = pd.read_csv(markov_path, parse_dates=["date"])
            df_m = df_m[(df_m["region"] == city) & (df_m["segment"] == segment)]
            
            if not df_m.empty:
                latest_regime = df_m.sort_values("date").tail(1)["regime"].iloc[0]
                st.metric("📊 Aktuális rezsim", latest_regime.upper(), delta=None)
            else:
                st.info(f"Nincs rezsim adat: {city} / {segment}")
        except Exception as e:
            st.error(f"Error loading regime: {e}")
    else:
        st.warning("⚠️  Markov output hiányzik.")

# ===== RISK & VALUATION =====
with col2:
    st.header("⚠️  Kockázat & Értékelés")
    
    # Risk
    if risk_path.exists():
        try:
            df_r = pd.read_csv(risk_path)
            df_r = df_r[(df_r["region"] == city) & (df_r["segment"] == segment)]
            
            if not df_r.empty:
                r = df_r.iloc[0]
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(
                        "📈 Várható 12hó hozam",
                        f"{r['expected_12m_return']:.1%}"
                    )
                with c2:
                    st.metric(
                        "📉 Downside valszg.",
                        f"{r['downside_prob_12m']:.1%}",
                        delta=None
                    )
            else:
                st.info("Nincs kockázati output.")
        except Exception as e:
            st.error(f"Error loading risk: {e}")
    else:
        st.warning("⚠️  Risk output hiányzik.")

    # Valuation
    if val_path.exists():
        try:
            df_v = pd.read_csv(val_path)
            df_v = df_v[(df_v["region"] == city) & (df_v["segment"] == segment)]
            
            if not df_v.empty:
                v = df_v.iloc[0]
                c1, c2 = st.columns(2)
                with c1:
                    st.metric(
                        "💰 Nash-ár",
                        f"{v['nash_price']:,.0f} Ft"
                    )
                with c2:
                    st.metric(
                        "⏳ Opcióérték",
                        f"{v['option_value_wait']:,.0f} Ft"
                    )
            else:
                st.info("Nincs értékelési output.")
        except Exception as e:
            st.error(f"Error loading valuation: {e}")
    else:
        st.warning("⚠️  Valuation output hiányzik.")

# ===== PORTFOLIO =====
st.header("🎯 Portfólió Súlyok (MPT)")
if port_path.exists():
    try:
        df_p = pd.read_csv(port_path)
        st.dataframe(df_p, use_container_width=True)
        
        # Simple bar chart
        st.bar_chart(df_p.set_index("segment"))
    except Exception as e:
        st.error(f"Error loading portfolio: {e}")
else:
    st.warning("⚠️  Portfolio output hiányzik. Futtassa: `python -m src.models.portfolio_mpt`")

# Footer
st.divider()
st.markdown("""
**ℹ️  Információ:**
- Ez egy prototípus rendszer demonstrációs célokra.
- Az összes adat szintetikus vagy demo adatokon alapul.
- Valós döntésekhez fejlesztett, validált modellek szükségesek.
""")
