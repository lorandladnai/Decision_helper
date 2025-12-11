# Ingatlanprojekt

## 1. Cél

A projekt magyar lakáspiaci adatokra épülő döntéstámogató rendszer magán‑ingatlantulajdonosoknak.  
Fő adatforrások:

- KSH lakáspiaci árindex, kiadványok (2018–2025) [web:59][web:63][web:61]  
- MNB lakáspiaci jelentések, hitelezési statisztikák [web:64][web:68][web:71]  
- ingatlan.com és Duna House gyorsindikátorok (árak, forgalom, panel‑piac) [web:67][web:65][web:70]  

Három fő lépés:

1. Adatbetöltés és tisztítás (raw → processed)  
2. Feature‑építés + 6 modell futtatása  
3. Streamlit dashboard indítása (vizualizáció + magyarázatok)

A teljes folyamat egy Python pipeline‑nal fut: **`run_pipeline.py`**.

---

## 2. Követelmények

- Python 3.10+  
- pip  
- Git (opcionális)

**Alap csomagok:**

```
pip install pandas numpy streamlit
```

Ha van `requirements.txt`, akkor:

```
pip install -r requirements.txt
```

---

## 3. Könyvtárstruktúra

```
decision_support/
├─ data/
│  ├─ raw/
│  │   └─ Price_Index_Nominal.csv      # KSH lakásárindex (2015=100)[1][2]
│  └─ processed/
│      ├─ Clean_Rents.csv
│      ├─ Clean_Yields.csv
│      ├─ Clean_Transactions.csv
│      ├─ Clean_Lending.csv
│      └─ price_index_normalized.csv   # feature-építés után
│
├─ models/
│  ├─ 01_bayes.csv
│  ├─ 02_markov.csv
│  ├─ 03_kalman.csv
│  ├─ 04_risk.csv
│  ├─ 05_mpt.csv
│  └─ 06_valuation.csv
│
├─ src/
│  ├─ app/
│  │   └─ dashboard.py                  # Streamlit dashboard
│  ├─ data_load/
│  │   └─ dataload.py                  # raw → processed
│  ├─ features/
│  │   └─ features.py                  # feature-építés
│  └─ models/
│      ├─ runall.py (opcionális)
│      ├─ trend_bayes_hierarchical.py
│      ├─ trend_markov_switching.py
│      ├─ trend_kalman.py
│      ├─ risk_prospect_theory.py
│      ├─ portfolio_mpt.py
│      └─ valuation_nash_real_options.py
│
└─ run_pipeline.py                      # TELJES PYTHON PIPELINE
```

---

## 4. Pipeline szkript (`run_pipeline.py`)

Hely: **`decision_support/run_pipeline.py`**
```

---

## 5. Futtatási lépések

### 5.1. Projekt gyökérbe lépés

### 5.2. Függőségek telepítése (egyszer)

```
pip install -r requirements.txt
# vagy legalább:
pip install pandas numpy streamlit
```

### 5.3. Teljes pipeline futtatása

```
python run_pipeline.py
```

A konzolon egymás után jelennek meg:

- `1) DATA LOAD – raw → processed`  
- `2) FEATURE BUILD – price_index_normalized`  
- `3.x) MODEL – ...` (hat modell egymás után)  
- `4) START DASHBOARD (Streamlit)`  

### 5.4. Dashboard megnyitása

A pipeline utolsó lépése elindítja a Streamlit szervert, a konzolban látod pl.:

```
Local URL: http://localhost:8501
```

Nyisd meg böngészőben ezt az URL‑t. Itt éred el a **dashboardot**, amely:

- megjeleníti a KSH árindexeket, bérleti díjakat, hozamokat, forgalmat és hitelezési adatokat [web:59][web:64][web:67]  
- mutatja mind a 6 modell eredményét (Bayes trend, Markov rezsimek, Kalman trend, Prospect risk, MPT portfólió, Nash értékelés)  
- összefoglaló metrikákkal segíti a döntést (országos árnövekedés, Budapest fair value, BUY/HOLD/SELL jelzés).

---
---

## 7. Mit kapsz a végén?

- Egységes, tisztított **magyar lakáspiaci adatbázist** (árak, bérletek, hozamok, forgalom, hitelek).  
- 6 különböző modellnézetet (trend, rezsim, kockázat, portfólió, fair‑value).  
- Egy Streamlit alapú dashboardot, ahol a számokhoz **magyarázat is tartozik**, így nem csak grafikonokat látsz, hanem azt is, **mit jelentenek a döntéseid szempontjából**.
```

[1](https://www.ksh.hu/s/kiadvanyok/lakaspiaci-arak-lakasarindex-2025-i-negyedev/index.html)
[2](https://www.ksh.hu/s/kiadvanyok/lakaspiaci-arak-lakasarindex-2025-ii-negyedev/index.html)
