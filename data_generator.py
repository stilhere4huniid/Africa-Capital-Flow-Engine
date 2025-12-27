import pandas as pd
import numpy as np
import yfinance as yf
import os
import datetime

# --- CONFIGURATION ---
START_DATE = "2005-01-01"
# DYNAMIC END DATE: Always fetches data up to the current moment (Today)
END_DATE = datetime.datetime.today().strftime('%Y-%m-%d')
CONFIG_FILE = "config_countries.csv"

print(f"[INFO] System Start. Fetching data from {START_DATE} to {END_DATE} (Today)...")

os.makedirs('data', exist_ok=True)

# 1. LOAD COUNTRY CONFIGURATION
print(f"[INFO] Loading Country Profiles from {CONFIG_FILE}...")

try:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Could not find {CONFIG_FILE}. Please create it first.")
    
    # Read CSV and convert to the exact dictionary format the engine expects
    config_df = pd.read_csv(CONFIG_FILE)
    
    # Verify required columns exist
    required_cols = ['Country', 'Base_FDI', 'Oil_Sensitivity', 'USD_Sensitivity', 'Stability_Vol']
    if not all(col in config_df.columns for col in required_cols):
        raise ValueError(f"CSV is missing columns. Required: {required_cols}")

    # Transform to Dictionary
    profiles = config_df.set_index('Country').to_dict('index')
    print(f"[SUCCESS] Successfully loaded profiles for: {list(profiles.keys())}")

except Exception as e:
    print(f"[CRITICAL ERROR] loading config: {e}")
    print("Stopping execution. Please fix the CSV file.")
    exit()

# 2. FETCH REAL DRIVERS
print("[INFO] Connecting to Yahoo Finance to fetch REAL market drivers...")
# CL=F: Crude Oil
# DX-Y.NYB: USD Index
# GC=F: Gold (Critical for SA/Zim)
# PL=F: Platinum (Critical for SA/Zim)
tickers = ["CL=F", "DX-Y.NYB", "GC=F", "PL=F"]

try:
    # Download data
    raw_data = yf.download(tickers, start=START_DATE, end=END_DATE, interval="1mo", progress=False)
    
    if raw_data.empty:
        raise ValueError("Yahoo Finance returned empty data.")

    # Smart Column Selection
    if 'Adj Close' in raw_data.columns:
        real_data = raw_data['Adj Close'].copy()
    elif 'Close' in raw_data.columns:
        print("[WARN] 'Adj Close' missing. Using 'Close' instead.")
        real_data = raw_data['Close'].copy()
    else:
        # Fallback
        real_data = raw_data.iloc[:, :4].copy()
        real_data.columns = ['Oil_Price', 'USD_Index', 'Gold_Price', 'Platinum_Price']

except Exception as e:
    print(f"[ERROR] Error processing Yahoo data: {e}")
    # Dummy Fallback
    dates = pd.date_range(start=START_DATE, end=END_DATE, freq='ME')
    real_data = pd.DataFrame(index=dates)
    real_data['Oil_Price'] = 70.0
    real_data['USD_Index'] = 100.0
    real_data['Gold_Price'] = 1800.0
    real_data['Platinum_Price'] = 900.0

if not real_data.empty:
    # --- RENAME COLUMNS STANDARDIZATION ---
    # Ensure columns map correctly. Yahoo sorts alphabetically: CL=F, DX-Y.NYB, GC=F, PL=F
    rename_map = {
        'CL=F': 'Oil_Price',
        'DX-Y.NYB': 'USD_Index',
        'GC=F': 'Gold_Price',
        'PL=F': 'Platinum_Price'
    }
    
    # If columns match tickers (usual case), rename them
    real_data.rename(columns=rename_map, inplace=True)
    
    # Safety Check: If renaming didn't work (unexpected format), force rename by position if 4 cols exist
    if 'Oil_Price' not in real_data.columns and real_data.shape[1] == 4:
         real_data.columns = ['Oil_Price', 'USD_Index', 'Gold_Price', 'Platinum_Price']

    # Fill missing data
    real_data = real_data.ffill().dropna()

    # --- NORMALIZE (Z-Score) ---
    # We use explicit names here so we know exactly what to call in the formula
    for col in ['Oil_Price', 'USD_Index', 'Gold_Price', 'Platinum_Price']:
        if col in real_data.columns:
            real_data[f'{col}_Norm'] = (real_data[col] - real_data[col].mean()) / real_data[col].std()

    print(f"[SUCCESS] Real Data Acquired (Oil, USD, Gold, Platinum): {real_data.shape[0]} months.")

    # 3. GENERATE SEMI-SYNTHETIC DATASET
    all_data = []
    np.random.seed(42) 

    for country, params in profiles.items():
        # Copy the real timeline
        df = real_data.copy().reset_index()
        if 'Date' not in df.columns:
            df.rename(columns={'index': 'Date'}, inplace=True)
            
        df['Country'] = country
        
        # --- GDP LOGIC (UPDATED VARIABLE NAMES) ---
        
        if country in ['South Africa', 'Zimbabwe']:
             # Economy grows when Minerals are high (Gold & Platinum)
             # Note: Using 'Gold_Price_Norm' instead of 'Gold_Norm' to match column creation above
             impact = (df['Gold_Price_Norm'] * 0.4) + (df['Platinum_Price_Norm'] * 0.4)
        else:
             # Standard Model: Economy grows based on Oil Sensitivity
             # Note: Using 'Oil_Price_Norm' instead of 'Oil_Norm'
             impact = (df['Oil_Price_Norm'] * params['Oil_Sensitivity'])

        # GDP Calculation
        # Note: Using 'USD_Index_Norm' instead of 'USD_Norm'
        noise_gdp = np.random.normal(0, 1, len(df))
        df['GDP_Growth'] = 3.0 + impact + (df['USD_Index_Norm'] * params['USD_Sensitivity']) + noise_gdp
        
        # Inflation Calculation
        noise_inf = np.random.normal(0, 1.5, len(df))
        base_inf = 15.0 if country in ['Nigeria', 'Egypt'] else 6.0
        df['Inflation'] = base_inf - (df['GDP_Growth'] * 0.5) + noise_inf
        df['Inflation'] = df['Inflation'].abs() 
        
        df['Interest_Rate'] = df['Inflation'] + 3.0 + np.random.normal(0, 0.5, len(df))
        
        # TARGET: FDI Inflows
        noise_fdi = np.random.normal(0, params['Base_FDI'] * 0.15, len(df))
        
        # We use 'Oil_Price_Norm' here for global sentiment in FDI formula
        df['FDI_Inflows_MillionUSD'] = (
            params['Base_FDI'] + 
            (df['GDP_Growth'] * 20) - 
            (df['Inflation'] * 5) + 
            (df['Oil_Price_Norm'] * params['Oil_Sensitivity'] * 50) + 
            noise_fdi
        )
        
        df['FDI_Inflows_MillionUSD'] = df['FDI_Inflows_MillionUSD'].apply(lambda x: max(x, 10))
        
        # Select Columns (Include new minerals)
        final_cols = ['Date', 'Country', 'FDI_Inflows_MillionUSD', 'GDP_Growth', 'Inflation', 'Interest_Rate', 'Oil_Price', 'USD_Index', 'Gold_Price', 'Platinum_Price']
        
        # Only keep columns that actually exist (Safety)
        final_cols = [c for c in final_cols if c in df.columns]
        
        all_data.append(df[final_cols])

    # Combine and Save
    final_df = pd.concat(all_data)
    final_df.to_csv("data/semi_synthetic_fdi.csv", index=False)

    print("\n[SUCCESS] Dataset Generated using 'config_countries.csv'")
    print(f"Saved to: data/semi_synthetic_fdi.csv")

else:
    print("[FAIL] Failed to download data. Check internet connection.")