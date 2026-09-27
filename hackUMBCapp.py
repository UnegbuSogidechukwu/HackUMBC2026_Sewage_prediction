import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

st.set_page_config(page_title="Maryland Sewage Discharge Forecast", layout="wide")


@st.cache_data
def get_base64(bin_file):
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = get_base64("hackumbc_background.webp")

# st.markdown(
#     f"""
#     <style>
#         .stApp {{
#             background-image: url("data:image/webp;base64,{img_base64}");
#             background-size: cover;
#             background-position: center;
#             background-attachment: fixed;
#         }}

#         .header {{
#             background: linear-gradient(90deg, #166534, #15803d);
#             padding: 30px;
#             border-radius: 15px;
#             color: white;
#             margin-bottom: 20px;
#         }}

#         .content-box {{
#             background-color: rgba(255,255,255,0.92);
#             padding: 20px;
#             border-radius: 15px;
#             box-shadow: 0 4px 12px rgba(0,0,0,0.1);
#         }}

#         button[data-baseweb="tab"] {{
#             font-size: 16px;
#             font-weight: 600;
#             border-radius: 8px;
#         }}

#         button[data-baseweb="tab"][aria-selected="true"] {{
#             background-color: #166534;
#             color: white;
#         }}

#         .status-success {{
#             background-color: #E8F5E9;
#             color: #14532D;
#             padding: 15px;
#             border-radius: 8px;
#             border-left: 5px solid #15883D;
#         }}
#     </style>
#     """,
#     unsafe_allow_html=True
# )
st.markdown(
    f"""
    <style>
        /* ------------------------------
           GLOBAL BACKGROUND
        ------------------------------ */
        .stApp {{
            background-image: url("data:image/webp;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* ------------------------------
           HEADER
        ------------------------------ */
        .header {{
            background: linear-gradient(90deg, #14532D, #166534, #15803d);
            padding: 32px;
            border-radius: 18px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin: 0;
        }}

        /* ------------------------------
           CONTENT BOX (Glassmorphism)
        ------------------------------ */
        .content-box {{
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            padding: 22px;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            margin-bottom: 20px;
        }}

        /* ------------------------------
           TABS
        ------------------------------ */
        button[data-baseweb="tab"] {{
            font-size: 17px;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 10px;
            background-color: rgba(255,255,255,0.6);
            color: #14532D;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            background-color: #166534;
            color: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        }}

        /* ------------------------------
           STATUS BOXES
        ------------------------------ */
        .status-success {{
            background-color: #E8F5E9;
            color: #14532D;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #15803d;
            font-weight: 600;
        }}

        .status-error {{
            background-color: #FEE2E2;
            color: #7F1D1D;
            padding: 15px;
            border-radius: 10px;
            border-left: 6px solid #DC2626;
            font-weight: 600;
        }}

        /* ------------------------------
           SLIDER LABEL FIX
        ------------------------------ */
        .stSlider > label {{
            font-size: 16px;
            font-weight: 600;
            color: #14532D;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_forecast():
    return pd.read_csv("forecast1.csv", parse_dates=["ds"])

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
    if source_type == "actual":
        df = actual.copy()
    else:
        df = forecast.copy()

    # DATE RANGE BASED ON SELECTED DATA
    min_date = df['ds'].min()
    max_date = df['ds'].max()

    # DATE SLIDER
    selected_date = st.slider(
        "Select a date",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=max_date.to_pydatetime(),
        format="YYYY-MM-DD",
        key = key
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

# (uses the Forecast tab's own slider selection)
current_val = visible_forecast['yhat_gallons'].iloc[-1] if len(visible_forecast) else 0
if current_val > THRESHOLD:
    st.error(f"Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold")
else:
    st.success(f"Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold")
