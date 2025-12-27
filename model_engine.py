import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
import warnings

warnings.filterwarnings("ignore")

def train_and_forecast(country_name, steps=24):
    """
    Trains a VAR model for a specific country and forecasts future FDI.
    Returns: Historical Data + Forecast Data combined.
    """
    # 1. Load Data
    try:
        df = pd.read_csv("data/semi_synthetic_fdi.csv")
    except FileNotFoundError:
        return pd.DataFrame(), "❌ Data Missing"

    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter for specific country
    country_df = df[df['Country'] == country_name].copy()
    country_df = country_df.sort_values('Date').set_index('Date')
    
    # 2. Prepare Variables for VAR
    # UPDATE: We now look for Gold and Platinum columns to drive the SA/Zim models
    possible_cols = [
        'FDI_Inflows_MillionUSD', 
        'GDP_Growth', 
        'Inflation', 
        'Interest_Rate', 
        'Oil_Price', 
        'USD_Index', 
        'Gold_Price',       # <-- NEW
        'Platinum_Price'    # <-- NEW
    ]
    
    # Dynamic Column Selection: Only keep columns that actually exist in the CSV.
    # This prevents the app from crashing if you use an old dataset without minerals.
    valid_cols = [c for c in possible_cols if c in country_df.columns]
    
    train_df = country_df[valid_cols].dropna()
    
    # SAFETY CHECK: Ensure we have enough data
    if len(train_df) < 15:
        return pd.DataFrame(), "⚠️ Insufficient Data"

    # 3. Fit VAR Model (ROBUST FIX)
    model = VAR(train_df)
    
    # Dynamic Max Lags: Never ask for more lags than the data supports
    # Rule of thumb: We need at least 10 observations per lag roughly
    max_possible_lags = len(train_df) // 10
    safe_maxlags = min(12, max_possible_lags)
    
    # If data is really short, default to lag 1
    if safe_maxlags < 1:
        safe_maxlags = 1

    try:
        best_lag = model.select_order(maxlags=safe_maxlags).aic
        var_result = model.fit(best_lag)
    except:
        # Fallback if AIC fails: force a simple 1-month lag model
        var_result = model.fit(1)
    
    # 4. Forecast
    lag_order = var_result.k_ar
    input_data = train_df.values[-lag_order:]
    
    forecast_prediction = var_result.forecast(y=input_data, steps=steps)
    
    # 5. Structure the Forecast Output
    last_date = train_df.index[-1]
    forecast_dates = pd.date_range(start=last_date, periods=steps+1, freq='M')[1:]
    
    # Use 'valid_cols' here so the dataframe columns match the prediction shape
    forecast_df = pd.DataFrame(forecast_prediction, index=forecast_dates, columns=valid_cols)
    forecast_df['Type'] = 'Forecast'
    
    # 6. Combine History and Forecast
    history_df = train_df.copy()
    history_df['Type'] = 'History'
    
    final_df = pd.concat([history_df, forecast_df])
    
    # Signal Logic
    avg_hist = history_df['FDI_Inflows_MillionUSD'].tail(12).mean()
    avg_fcst = forecast_df['FDI_Inflows_MillionUSD'].head(12).mean()
    
    signal = "🔥 HEATING UP" if avg_fcst > avg_hist else "❄️ COOLING DOWN"
    
    return final_df, signal

# Debugging / Testing block (Only runs if you execute this script directly)
if __name__ == "__main__":
    print("🧠 Testing VAR Engine on Nigeria...")
    data, sig = train_and_forecast("Nigeria")
    print(f"Signal: {sig}")
    if not data.empty:
        print(data.tail())