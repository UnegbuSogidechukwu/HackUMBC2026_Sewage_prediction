# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go

# st.set_page_config(page_title="Maryland Sewage Discharge Forecast", layout="wide")

# @st.cache_data
# def load_forecast():
#     return pd.read_csv("forecast.csv", parse_dates=["ds"])

# @st.cache_data
# def load_actual():
#     df = pd.read_csv("actual.csv", parse_dates=["date"])
#     df = df.rename(columns={"date": "ds"})
#     return df

# forecast = load_forecast()
# actual = load_actual()

# st.title("Maryland Sewage Discharge — Trend & Forecast")
# st.caption(
#     "Threshold: 10,000 gallons — Maryland's public-reporting trigger for sanitary sewer "
#     "overflows under COMAR 26.08.10 (Clean Water Act / MDE water-quality regulation, "
#     "not a Clean Air Act State Implementation Plan)."
# )

# THRESHOLD = 10_000  # gallons — COMAR 26.08.10 public reporting trigger

# def slider(type):
#     {# Slider range spans whichever file has the wider date coverage,
#     # so neither chart gets cut off early.
#     min_date = min(forecast['ds'].min(), type['ds'].min())
#     max_date = max(forecast['ds'].max(), type['ds'].max())


#     selected_date = st.slider(
#         "Select a date",
#         min_value=min_date.to_pydatetime(),
#         max_value=max_date.to_pydatetime(),
#         value=max_date.to_pydatetime(),
#         format="YYYY-MM-DD"
#     )

#     # Filter each source independently — no merge needed since each
#     # tab only ever plots one series at a time.
#     if (type == actual)
#     {
#         visible_actual = actual[actual["ds"] <= selected_date]
#     else
#         visible_forecast = forecast[forecast["ds"] <= selected_date]
#     }
# }

# def add_threshold(fig):
#     fig.add_hline(
#         y=THRESHOLD, line_dash="dash", line_color="orange",
#         annotation_text="Reporting threshold (10,000 gal)"
#     )
#     fig.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=550)
#     return fig


# tab_actual, tab_forecast, tab_upper, tab_lower, tab_info = st.tabs(
#     ["Actual", "Forecast", "Upper Bound", "Lower Bound", "Information"]
# )

# with tab_actual:
#     slider("actual")
#     st.subheader("Actual Discharge Volume")
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=visible_actual['ds'], y=visible_actual['discharge_volume_clean'],
#         mode='markers', name='Actual', marker=dict(size=4, color='#4B6EF5')
#     ))
#     st.plotly_chart(add_threshold(fig), use_container_width=True)

# with tab_forecast:
#     slider("forecast")
#     st.subheader("Forecast")
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=visible_forecast['ds'], y=visible_forecast['yhat_gallons'],
#         mode='lines', name='Forecast', line=dict(color='red')
#     ))
#     st.plotly_chart(add_threshold(fig), use_container_width=True)

# with tab_upper:
#     slider("forecast")
#     st.subheader("Upper Bound (yhat_upper_gallons)")
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=visible_forecast['ds'], y=visible_forecast['yhat_upper_gallons'],
#         mode='lines', name='Upper bound', line=dict(color='#B98CFF')
#     ))
#     st.plotly_chart(add_threshold(fig), use_container_width=True)

# with tab_lower:
#     slider("forecast")
#     st.subheader("Lower Bound (yhat_lower_gallons)")
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=visible_forecast['ds'], y=visible_forecast['yhat_lower_gallons'],
#         mode='lines', name='Lower bound', line=dict(color='#6FCF97')
#     ))
#     st.plotly_chart(add_threshold(fig), use_container_width=True)

# with tab_info:
#     st.subheader("About this model")
#     st.write(
#         "Forecast generated with Prophet, trained on log-transformed weekly statewide "
#         "sewage discharge volume. Threshold reflects COMAR 26.08.10's 10,000-gallon "
#         "public reporting trigger for sanitary sewer overflows."
#     )

# # ---- Status readout (forecast-based, independent of actual.csv) ----
# current_val = visible_forecast['yhat_gallons'].iloc[-1] if len(visible_forecast) else 0
# if current_val > THRESHOLD:
#     st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold")
# else:
#     st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Maryland Sewage Discharge Forecast", layout="wide")

@st.cache_data
def load_forecast():
    return pd.read_csv("forecast.csv", parse_dates=["ds"])

@st.cache_data
def load_actual():
    df = pd.read_csv("actual.csv", parse_dates=["date"])
    df = df.rename(columns={"date": "ds"})
    return df

forecast = load_forecast()
actual = load_actual()

st.title("Maryland Sewage Discharge — Trend & Forecast")
st.caption(
    "Threshold: 10,000 gallons — Maryland's public-reporting trigger for sanitary sewer "
    "overflows under COMAR 26.08.10 (Clean Water Act / MDE water-quality regulation, "
    "not a Clean Air Act State Implementation Plan)."
)

THRESHOLD = 10_000  # gallons — COMAR 26.08.10 public reporting trigger


def slider(source_type, key):
    """Renders a date slider and returns the filtered dataframe for the
    requested source ('actual' or 'forecast'). `key` must be unique per
    call so Streamlit doesn't collide multiple sliders with the same label."""
    df = actual if source_type == "actual" else forecast

    min_date = min(forecast['ds'].min(), actual['ds'].min())
    max_date = max(forecast['ds'].max(), actual['ds'].max())

    selected_date = st.slider(
        "Select a date",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=max_date.to_pydatetime(),
        format="YYYY-MM-DD",
        key=key
    )

    return df[df["ds"] <= selected_date]


def add_threshold(fig):
    fig.add_hline(
        y=THRESHOLD, line_dash="dash", line_color="orange",
        annotation_text="Reporting threshold (10,000 gal)"
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Gallons", height=550)
    return fig


tab_actual, tab_forecast, tab_upper, tab_lower, tab_info = st.tabs(
    ["Actual", "Forecast", "Upper Bound", "Lower Bound", "Information"]
)

with tab_actual:
    visible_actual = slider("actual", key="slider_actual")
    st.subheader("Actual Discharge Volume")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_actual['ds'], y=visible_actual['discharge_volume_clean'],
        mode='markers', name='Actual', marker=dict(size=4, color='#4B6EF5')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_forecast:
    visible_forecast = slider("forecast", key="slider_forecast")
    st.subheader("Forecast")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_forecast['ds'], y=visible_forecast['yhat_gallons'],
        mode='lines', name='Forecast', line=dict(color='red')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_upper:
    visible_upper = slider("forecast", key="slider_upper")
    st.subheader("Upper Bound (yhat_upper_gallons)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_upper['ds'], y=visible_upper['yhat_upper_gallons'],
        mode='lines', name='Upper bound', line=dict(color='#B98CFF')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_lower:
    visible_lower = slider("forecast", key="slider_lower")
    st.subheader("Lower Bound (yhat_lower_gallons)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_lower['ds'], y=visible_lower['yhat_lower_gallons'],
        mode='lines', name='Lower bound', line=dict(color='#6FCF97')
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

with tab_info:
    st.subheader("About this model")
    st.write(
        "Forecast generated with Prophet, trained on log-transformed weekly statewide "
        "sewage discharge volume. Threshold reflects COMAR 26.08.10's 10,000-gallon "
        "public reporting trigger for sanitary sewer overflows."
    )

# ---- Status readout (uses the Forecast tab's own slider selection) ----
current_val = visible_forecast['yhat_gallons'].iloc[-1] if len(visible_forecast) else 0
if current_val > THRESHOLD:
    st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold")
else:
    st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold")
