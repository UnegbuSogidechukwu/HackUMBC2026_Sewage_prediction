import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Maryland Sewage Discharge Forecast", layout="wide")

@st.cache_data
def load_forecast():
    return pd.read_csv("forecast.csv", parse_dates=["ds"])

@st.cache_data
def load_actual():
    return pd.read_csv("actual.csv", parse_dates=["dates"])

forecast = load_forecast()
actual = load_actual()


st.title("Maryland Sewage Discharge — Trend & Forecast")
st.caption(
    "Threshold: 10,000 gallons — Maryland's public-reporting trigger for sanitary sewer "
    "overflows under COMAR 26.08.10 (Clean Water Act / MDE water-quality regulation, "
    "not a Clean Air Act State Implementation Plan)."
)

THRESHOLD = 10_000  

min_date, max_date = forecast['ds'].min(), forecast['ds'].max()
selected_date = st.slider(
    "Select a date",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=max_date.to_pydatetime(),
    format="YYYY-MM-DD"
)

visible = df[df["ds"] <= selected_date]


def add_threshold(fig):
    fig.add_hline(
        y=THRESHOLD, line_dash="dash", line_color="orange",
        annotation_text="Reporting threshold (10,000 gal)"
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=550)
    return fig


tab_actual, tab_forecast, tab_upper, tab_lower, tab_all = st.tabs(
    ["Actual", "Forecast", "Upper Bound", "Lower Bound", "Information"]
)

with tab_actual:
    st.subheader("Actual Discharge Volume")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible['ds'], y=visible['actual_gallons'],
        mode='markers', name='Actual', marker=dict(size=4, color='#4B6EF5')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)


with tab_forecast:
    st.subheader("Forecast")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible['ds'], y=visible['forcasted gallons'],
        mode='lines', name='Forecast', line=dict(color='red')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_upper:
    st.subheader("Upper Bound (yhat_upper_gallons)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible['ds'], y=visible['yhat_upper_gallons'],
        mode='lines', name='Upper bound', line=dict(color='#B98CFF')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_lower:
    st.subheader("Lower Bound (yhat_lower_gallons)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible['ds'], y=visible['yhat_lower_gallons'],
        mode='lines', name='Lower bound', line=dict(color='#6FCF97')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)


# ---- Status readout ----
current_val = visible['yhat_gallons'].iloc[-1] if len(visible) else 0
if current_val > THRESHOLD:
    st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold")
else:
    st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold")
