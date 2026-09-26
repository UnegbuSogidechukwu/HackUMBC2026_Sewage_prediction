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
st.caption("Threshold based on MDE penalty guidance / State Implementation Plan reference level")

THRESHOLD = 5_000_000  # replace with your actual justified number

min_date, max_date = forecast['ds'].min(), forecast['ds'].max()
selected_date = st.slider(
    "Select a date",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=max_date.to_pydatetime(),
    format="YYYY-MM-DD"
)

visible = forecast[forecast['ds'] <= selected_date]

fig = go.Figure()
fig.add_trace(go.Scatter(x=visible['ds'], y=visible['actual_gallons'], mode='markers', name='Actual', marker=dict(size=4)))
fig.add_trace(go.Scatter(x=visible['ds'], y=visible['yhat_gallons'], mode='lines', name='Forecast', line=dict(color='red')))
fig.add_trace(go.Scatter(x=visible['ds'], y=visible['yhat_upper_gallons'], mode='lines', line=dict(width=0), showlegend=False))
fig.add_trace(go.Scatter(x=visible['ds'], y=visible['yhat_lower_gallons'], mode='lines', line=dict(width=0), fill='tonexty', name='Confidence band', fillcolor='rgba(150,100,255,0.3)'))
fig.add_hline(y=THRESHOLD, line_dash="dash", line_color="orange", annotation_text="Threshold")

fig.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=550)
st.plotly_chart(fig, use_container_width=True)

current_val = visible['yhat_gallons'].iloc[-1] if len(visible) else 0
if current_val > THRESHOLD:
    st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds threshold")
else:
    st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within threshold")
