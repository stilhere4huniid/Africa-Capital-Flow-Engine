# 📘 User Documentation

## Getting Started
1.  **Install Dependencies:** `pip install -r requirements.txt`
2.  **Run Dashboard:** `streamlit run app.py`
3.  **Run GIS Map:** `python gis_engine.py`

## How to Use the Dashboard
### 1. Market Selection
* Use the sidebar to select a target market (e.g., "Zimbabwe").
* **Refresh Data:** Click "Refresh Live Data" to pull the latest Yahoo Finance commodity prices.

### 2. Scenario Planning
* Adjust the **Forecast Horizon** slider (12–60 months).
* *Short-Term (12m):* Best for tactical cash-flow management.
* *Long-Term (60m):* Best for strategic land banking decisions.

### 3. Interpreting the PDF Reports
* **"Heating Up":** Projected FDI growth >0%. Recommendation: *Accumulate Assets.*
* **"Cooling Down":** Projected FDI decline. Recommendation: *De-risk / Halt CapEx.*
* **KPI Grid:** Review the "6-Month Cash Flow Intensity" table to time project launches.