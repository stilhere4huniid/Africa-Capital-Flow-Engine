import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from model_engine import train_and_forecast
import subprocess
import sys
from fpdf import FPDF
import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="African Capital Flow Engine", layout="wide", page_icon="🌍")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #303030;
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stMetricLabel {color: #a0a0a0 !important;}
</style>
""", unsafe_allow_html=True)

# --- PDF GENERATION CLASS ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'African Capital Flow Engine - Executive Summary', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# --- ENHANCED PDF GENERATION ---
def create_pdf(country, current_fdi, predicted_fdi, delta, signal, oil_corr, df):
    pdf = PDF()
    pdf.add_page()
    
    clean_signal = signal.replace("🔥", "").replace("❄️", "").strip()
    forecast = df[df['Type'] == 'Forecast']
    
    # --- INTELLIGENCE ENGINE ---
    if delta > 100:
        momentum, stance = "extraordinary surge", "AGGRESSIVE EXPANSION"
    elif delta > 20:
        momentum, stance = "strong upward trend", "STRATEGIC ACCELERATION"
    elif delta > 0:
        momentum, stance = "stable recovery", "CAUTIOUS OPTIMISM"
    elif delta > -20:
        momentum, stance = "mild contraction", "PORTFOLIO CONSOLIDATION"
    else:
        momentum, stance = "significant downturn", "DEFENSIVE DE-RISKING"

    # --- NARRATIVE GENERATOR ---
    analysis = f"The {country} capital flow engine is currently detecting a {momentum}. "
    
    if country in ["Zimbabwe", "South Africa"]:
        analysis += f"Mineral pricing (Gold/Platinum) remains the primary support pillar, providing a buffer against local currency instability. "
    elif abs(oil_corr) > 0.6:
        impact = "benefit" if oil_corr > 0 else "volatility"
        analysis += f"The high correlation with global energy markets ({oil_corr:.2f}) suggests that portfolio performance will track {impact} in the crude sector. "

    recommendation = f"Our executive stance is {stance}. "
    if "DE-RISKING" in stance:
        recommendation += "Halt all non-essential CapEx and increase cash reserves."
    elif "EXPANSION" in stance:
        recommendation += "Leverage current liquidity to acquire prime distressed assets or fast-track ongoing developments."
    else:
        recommendation += "Focus on tenant retention and protecting USD-equivalent yields."

    # --- PDF DRAWING ---
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"Market Intelligence: {country}", 0, 1)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Horizon: {len(forecast)} Months | Delta: {delta:+.1f}%", 0, 1)
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " Strategic Executive Summary", 1, 1, 'L', fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, f"\nAnalysis: {analysis}\n\nRecommendation: {recommendation}\n")
    
    # KPI Table
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " Key Performance Indicators", 1, 1, 'L', fill=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.cell(90, 10, "Annualized Run-Rate (Current)", 1)
    pdf.cell(90, 10, f"${current_fdi:,.1f} M", 1, 1)
    
    pdf.cell(90, 10, "Projected Annual Inflow", 1)
    pdf.cell(90, 10, f"${predicted_fdi:,.1f} M", 1, 1)
    
    pdf.cell(90, 10, "Forecast Period Change (Delta)", 1)
    pdf.cell(90, 10, f"{delta:+.1f}%", 1, 1)
    
    pdf.cell(90, 10, "Oil Price Sensitivity (Correlation)", 1)
    pdf.cell(90, 10, f"{oil_corr:.2f}", 1, 1)
    
    pdf.cell(90, 10, "Model Signal Strength", 1)
    pdf.cell(90, 10, f"{clean_signal}", 1, 1)
    pdf.ln(10)

    # 6-Month Projected Cash-Flow Intensity Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 6-Month Projected Cash-Flow Intensity", 1, 1, 'L', fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 10, "Month", 1, 0, 'C')
    pdf.cell(90, 10, "Inflow Intensity (USD M)", 1, 1, 'C')
    
    pdf.set_font("Arial", "", 10)
    short_term = forecast.head(6)
    for index, row in short_term.iterrows():
        month_str = index.strftime('%B %Y')
        val = row['FDI_Inflows_MillionUSD']
        pdf.cell(90, 10, f" {month_str}", 1)
        pdf.cell(90, 10, f"${val:,.2f}", 1, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- SIDEBAR ---
st.sidebar.title("🌍 Capital Flow Engine")
st.sidebar.markdown("Predicting Cross-Border Real Estate Investment in Africa.")

# 1. REFRESH BUTTON
st.sidebar.subheader("⚙️ System Controls")
if st.sidebar.button("🔄 Refresh Live Data"):
    with st.spinner("Connecting to Yahoo Finance API & Recalibrating Models..."):
        # Use absolute path to ensure script is found
        current_dir = os.getcwd()
        script_path = os.path.join(current_dir, "data_generator.py")
        
        if os.path.exists(script_path):
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            if result.returncode == 0:
                st.sidebar.success("Data Updated Successfully!")
            else:
                st.sidebar.error("Error updating data.")
                st.sidebar.code(result.stderr)
        else:
            st.sidebar.error(f"Script not found at: {script_path}")

st.sidebar.markdown("---")

country = st.sidebar.selectbox(
    "Select Market:",
    ["Nigeria", "South Africa", "Egypt", "Kenya", "Zimbabwe"]
)

steps = st.sidebar.slider("Forecast Horizon (Months)", 12, 60, 24)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Methodology:** Vector Autoregression (VAR) Model trained on Macro-Economic Drivers (GDP, Inflation, Oil, USD, Interest Rates, Gold, Platinum)."
)

# --- MAIN LOGIC ---
st.title(f"📊 Market Intelligence: {country}")

# Run the Engine
with st.spinner(f"Running Econometric Models for {country}..."):
    df, signal = train_and_forecast(country, steps=steps)

# --- 🛑 SAFETY CHECK ---
if df.empty:
    st.error(f"⚠️ Model Failure: {signal}")
    st.warning("This usually happens if the live data feed is incomplete or the country profile needs adjustment.")
    st.stop()
# ---------------------

# Split History and Forecast for plotting
history = df[df['Type'] == 'History']
forecast = df[df['Type'] == 'Forecast']

# Multiply by 12 to get the Annual Run-Rate
current_fdi = history['FDI_Inflows_MillionUSD'].iloc[-1] * 12

if not forecast.empty:
    # This only runs if the API refresh worked
    predicted_fdi = forecast['FDI_Inflows_MillionUSD'].iloc[-1] * 12
    delta = ((predicted_fdi - current_fdi) / current_fdi) * 100
else:
    # This runs if Yahoo is blocked (Cache Mode)
    # It prevents the IndexError by giving the app "safe" numbers to show
    predicted_fdi = current_fdi
    delta = 0.0

# --- KPI ROW ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Current Annualized FDI", f"${current_fdi:,.1f}M")

with c2:
    st.metric("Forecast (End of Period)", f"${predicted_fdi:,.1f}M", f"{delta:+.1f}%")

with c3:
    if "HEAT" in signal:
        st.error(signal) 
    else:
        st.info(signal)

with c4:
    # Correlation Insight
    corr = df['FDI_Inflows_MillionUSD'].corr(df['Oil_Price'])
    strength = "Strong" if abs(corr) > 0.5 else "Weak"
    direction = "Positive" if corr > 0 else "Negative"
    st.metric("Oil Sensitivity", f"{corr:.2f}", f"{strength} {direction}")

st.divider()

# --- CHART 1: THE FORECAST ---
st.subheader("📈 Capital Flow Forecast (FDI Inflows)")

fig = go.Figure()

# Historical Line
fig.add_trace(go.Scatter(
    x=history.index, 
    y=history['FDI_Inflows_MillionUSD'],
    mode='lines',
    name='Historical Data',
    line=dict(color='#00CC96', width=2)
))

# Forecast Line (Dashed)
fig.add_trace(go.Scatter(
    x=forecast.index, 
    y=forecast['FDI_Inflows_MillionUSD'],
    mode='lines',
    name='VAR Forecast',
    line=dict(color='#AB63FA', width=3, dash='dot')
))

# Confidence Interval Look
fig.add_trace(go.Scatter(
    x=list(forecast.index) + list(forecast.index[::-1]),
    y=list(forecast['FDI_Inflows_MillionUSD'] * 1.1) + list(forecast['FDI_Inflows_MillionUSD'] * 0.9)[::-1],
    fill='toself',
    fillcolor='rgba(171, 99, 250, 0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False
))

fig.update_layout(
    template="plotly_dark",
    height=500,
    hovermode="x unified",
    title=f"Projected Real Estate Capital Inflows: {country}"
)

st.plotly_chart(fig, use_container_width=True)

# --- CHART 2: MACRO DRIVERS (Updated for Minerals) ---
st.subheader("🧩 Macro-Economic Drivers")

# Select relevant columns for the chart, including new minerals if they exist
possible_drivers = ['GDP_Growth', 'Inflation', 'Oil_Price', 'USD_Index', 'Gold_Price', 'Platinum_Price']
existing_drivers = [c for c in possible_drivers if c in df.columns]

norm_df = df[existing_drivers].copy()

# Normalize for display (0-1 scale visually)
norm_df = (norm_df - norm_df.mean()) / norm_df.std()

fig_drivers = px.line(
    norm_df, 
    x=norm_df.index, 
    y=norm_df.columns,
    title=f"Driver Correlation Matrix (Normalized Z-Scores)",
    template="plotly_dark"
)
fig_drivers.update_layout(height=400)
st.plotly_chart(fig_drivers, use_container_width=True)

# --- RAW DATA & PDF EXPORT ---
c_left, c_right = st.columns(2)

with c_left:
    with st.expander("📥 Download Raw Forecast Data (CSV)"):
        st.dataframe(forecast.head())
        csv = forecast.to_csv().encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "fdi_forecast.csv",
            "text/csv",
            key='download-csv'
        )

with c_right:
    st.write("📄 **Generate Executive Report**")
    pdf_bytes = create_pdf(country, current_fdi, predicted_fdi, delta, signal, corr, forecast)
    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=f"{country}_Market_Intelligence_Report.pdf",
        mime="application/pdf"
    )