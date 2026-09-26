import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Maryland Sewage Discharge Forecast", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('forecast.csv', parse_dates=['ds'])
    return df

forecast = load_data()

st.title("Maryland Sewage Discharge — Trend & Forecast")
st.caption(
    "Threshold: 10,000 gallons — Maryland's public-reporting trigger for sanitary sewer "
    "overflows under COMAR 26.08.10 (Clean Water Act / MDE water-quality regulation, "
    "not a Clean Air Act State Implementation Plan)."
)

THRESHOLD = 10_000  # gallons — COMAR 26.08.10 public reporting trigger

min_date, max_date = forecast['ds'].min(), forecast['ds'].max()
selected_date = st.slider(
    "Select a date",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=max_date.to_pydatetime(),
    format="YYYY-MM-DD"
)

visible = forecast[forecast['ds'] <= selected_date]

col1, col2, col3 = st.columns(3)

# ---- Chart 1: Actual + threshold ----
with col1:
    st.subheader("Actual Discharge Volume")
    fig_actual = go.Figure()
    fig_actual.add_trace(go.Scatter(
        x=visible['ds'], y=visible['actual_gallons'],
        mode='markers', name='Actual', marker=dict(size=4, color='#4B6EF5')
    ))
    fig_actual.add_hline(
        y=THRESHOLD, line_dash="dash", line_color="orange",
        annotation_text="Reporting threshold (10,000 gal)"
    )
    fig_actual.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=500)
    st.plotly_chart(fig_actual, use_container_width=True)

# ---- Chart 2: Forecast line + threshold (no band) ----
with col2:
    st.subheader("Forecast")
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=visible['ds'], y=visible['yhat_gallons'],
        mode='lines', name='Forecast', line=dict(color='red')
    ))
    fig_forecast.add_hline(
        y=THRESHOLD, line_dash="dash", line_color="orange",
        annotation_text="Reporting threshold (10,000 gal)"
    )
    fig_forecast.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=500)
    st.plotly_chart(fig_forecast, use_container_width=True)

# ---- Chart 3: Confidence band on its own + threshold ----
with col3:
    st.subheader("Confidence Band")
    fig_conf = go.Figure()
    fig_conf.add_trace(go.Scatter(
        x=visible['ds'], y=visible['yhat_upper_gallons'],
        mode='lines', name='Upper bound', line=dict(width=0), showlegend=False
    ))
    fig_conf.add_trace(go.Scatter(
        x=visible['ds'], y=visible['yhat_lower_gallons'],
        mode='lines', name='Confidence band', line=dict(width=0), fill='tonexty',
        fillcolor='rgba(150,100,255,0.4)'
    ))
    fig_conf.add_hline(
        y=THRESHOLD, line_dash="dash", line_color="orange",
        annotation_text="Reporting threshold (10,000 gal)"
    )
    fig_conf.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=500)
    st.plotly_chart(fig_conf, use_container_width=True)

# ---- Status readout ----
current_val = visible['yhat_gallons'].iloc[-1] if len(visible) else 0
if current_val > THRESHOLD:
    st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold")
else:
    st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold")
