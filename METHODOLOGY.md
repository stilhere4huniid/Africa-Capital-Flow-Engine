# 📐 Technical Methodology

## 1. The Econometric Engine (VAR)
The core of the forecasting module uses a **Vector Autoregression (VAR)** model. Unlike simple linear regression, VAR models capture the bidirectional relationship between variables (e.g., Oil prices affect Nigerian GDP, but Nigerian GDP does not affect Oil prices).

**Key Variables Modeled:**
* `Oil_Price`: Global crude benchmark (Impacts Nigeria/Angola).
* `Gold_Price` & `Platinum_Price`: Mineral basket (Impacts Zimbabwe/South Africa).
* `USD_Index`: Measures dollar strength (Inverse correlation with Emerging Markets).
* `FDI_Inflows`: The target variable (Capital Liquidity).

**Calibration:**
* **Zimbabwe:** Calibrated to a ~$600M/year FDI baseline based on 2024 ZIDA reports.
* **Correlation Logic:**
    * *Exporters (Nigeria):* Positive correlation with Oil.
    * *Importers (Kenya):* Negative correlation with Oil.

## 2. The GIS Gap Hunter Algorithm
The site selection tool uses a **Euclidean Distance Matrix** overlaid on a Density Heatmap.

**Logic Steps:**
1.  **Supply Mapping:** Plots exact GPS coordinates of current assets and known competitors.
2.  **Demand Heatmap:** Simulates population density ("Roof Counts") in key growth nodes (e.g., Ruwa, Madokero).
3.  **Gap Detection:**
    * *Algorithm:* `Check_Viability(Site)`
    * *Condition:* `IF Distance_to_Nearest_Mall > 3.0km AND In_High_Density_Zone = TRUE`
    * *Output:* Green Star (Opportunity) vs. Grey Pin (Cannibalization Risk).