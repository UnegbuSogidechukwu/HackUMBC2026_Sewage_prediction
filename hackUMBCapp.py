import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import os

st.set_page_config(
    page_title="Maryland Sewage Discharge Forecast",
    page_icon="💧",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# 2. HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def get_base64(bin_file):
    """Encode a local image to base64 for CSS background injection."""
    with open(bin_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Safely load background image (falls back to a gradient if missing)
bg_image_path = "hackumbc_background.webp"
if os.path.exists(bg_image_path):
    img_base64 = get_base64(bg_image_path)
    bg_css = f'url("data:image/webp;base64,{img_base64}")'
else:
    bg_css = "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)"

# ─────────────────────────────────────────────────────────────
# 3. GLOBAL CSS INJECTION (Glassmorphism + Modern UI)
# ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <style>
        /* ---------- Import Google Font ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        /* ---------- Global Background ---------- */
        .stApp {{
            background-image: {bg_css};
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Inter', sans-serif;
        }}

        /* ---------- Hide Streamlit Default Elements ---------- */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* ---------- Header Section ---------- */
        .header-container {{
            background: linear-gradient(135deg, #14532D 0%, #166534 50%, #15803d 100%);
            padding: 36px 40px;
            border-radius: 20px;
            color: white;
            margin-bottom: 28px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.25);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .header-container h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0 0 8px 0;
            letter-spacing: -0.5px;
        }}

        .header-container p {{
            font-size: 1.05rem;
            margin: 0;
            opacity: 0.9;
            font-weight: 400;
        }}

        /* ---------- Glassmorphism Content Box ---------- */
        .content-box {{
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            padding: 24px 28px;
            border-radius: 18px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.6);
            margin-bottom: 22px;
        }}

        /* ---------- Tab Styling ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
            padding: 6px 0;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 48px;
            padding: 0 22px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 12px;
            background-color: rgba(255,255,255,0.55);
            color: #14532D;
            border: 1px solid rgba(22, 101, 52, 0.15);
            transition: all 0.25s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(255,255,255,0.8);
            border-color: rgba(22, 101, 52, 0.3);
        }}

        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #166534, #15803d) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(22, 101, 52, 0.35);
        }}

        /* ---------- Status Boxes ---------- */
        .status-success {{
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
            color: #14532D;
            padding: 16px 20px;
            border-radius: 14px;
            border-left: 6px solid #15803d;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 8px rgba(21, 128, 61, 0.12);
        }}

        .status-error {{
            background: linear-gradient(135deg, #FEE2E2, #FECACA);
            color: #7F1D1D;
            padding: 16px 20px;
            border-radius: 14px;
            border-left: 6px solid #DC2626;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.12);
        }}

        /* ---------- Slider Label ---------- */
        .stSlider > label {{
            font-size: 15px;
            font-weight: 600;
            color: #14532D;
        }}

        /* ---------- Subheader ---------- */
        .stSubheader {{
            color: #14532D;
            font-weight: 700;
            font-size: 1.3rem;
            margin-bottom: 8px;
        }}

        /* ---------- Plotly Chart Container ---------- */
        .stPlotlyChart {{
            background: rgba(255,255,255,0.5);
            border-radius: 14px;
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.4);
        }}

        /* ---------- Caption ---------- */
        .stCaption {{
            color: #475569;
            font-size: 0.9rem;
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
