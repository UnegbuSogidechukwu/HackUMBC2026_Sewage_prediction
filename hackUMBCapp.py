import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────
# 1. PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Maryland Sewage Discharge Forecast",
    page_icon="💧",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# 2. GLOBAL CSS INJECTION (Modern Clean UI)
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ---------- Import Google Font ---------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        /* ---------- Global Solid Background ---------- */
        .stApp {
            background-color: #ADD8E6 ; 
            font-family: 'Inter', sans-serif;
        }

        /* ---------- Hide Streamlit Default Elements ---------- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* ---------- Header Section ---------- */
        .header-container {
            background: linear-gradient(135deg, #14532D 0%, #166534 50%, #15803d 100%);
            padding: 36px 40px;
            border-radius: 20px;
            color: white;
            margin-bottom: 28px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-container h1 {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0 0 8px 0;
            letter-spacing: -0.5px;
            color: white;
        }

        .header-container p {
            font-size: 1.05rem;
            margin: 0;
            opacity: 0.92;
            font-weight: 400;
            color: white;
        }

        /* ---------- Clean Content Box ---------- */
        .content-box,
        [data-testid="stVerticalBlock"] > div:has(> .stPlotlyChart) {
            background:#90EE90 !important;
            padding: 24px 28px;
            border-radius: 18px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(226, 232, 240, 0.8);
            margin-bottom: 22px;
        }

        /* ---------- Tab Styling (Pills) ---------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: transparent;
            padding: 4px 0;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            padding: 0 26px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 50px !important;
            background-color: #FFFFFF !important;
            color: #14532D !important;
            border: 1px solid #E2E8F0 !important;
            transition: all 0.25s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F1F5F9 !important;
            border-color: #CBD5E1 !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #166534, #15803d) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(22, 101, 52, 0.3) !important;
        }

        /* ---------- Status Boxes ---------- */
        .status-success {
            background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
            color: #14532D;
            padding: 18px 24px;
            border-radius: 14px;
            border-left: 6px solid #15803d;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 10px rgba(21, 128, 61, 0.1);
            margin-top: 12px;
        }

        .status-error {
            background: linear-gradient(135deg, #FEE2E2, #FECACA);
            color: #7F1D1D;
            padding: 18px 24px;
            border-radius: 14px;
            border-left: 6px solid #DC2626;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 10px rgba(220, 38, 38, 0.1);
            margin-top: 12px;
        }

        /* ---------- Slider Label ---------- */
        .stSlider > label {
            font-size: 15px;
            font-weight: 600;
            color: #14532D;
        }

        /* ---------- Subheader ---------- */
        .stSubheader, h2, h3 {
            color: #14532D !important;
            font-weight: 700 !important;
        }

        /* ---------- Plotly Chart Container ---------- */
        .stPlotlyChart {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 8px;
        }

        /* ---------- Caption ---------- */
        .stCaption {
            color: #475569;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────────────────────
# 3. DATA LOADING
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
# 4. HEADER SECTION
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="header-container">
        <h1>💧 Maryland Sewage Discharge Forecast</h1>
        <p>Protecting our water &nbsp;•&nbsp; Healthy communities &nbsp;•&nbsp; A cleaner tomorrow</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Threshold: 10,000 gallons — Maryland's public-reporting trigger for sanitary sewer "
    "overflows under COMAR 26.08.10 (Clean Water Act / MDE water-quality regulation)."
)

THRESHOLD = 10_000  # gallons — COMAR 26.08.10 public reporting trigger


# ─────────────────────────────────────────────────────────────
# 5. HELPER FUNCTIONS (Sliders, Threshold Line)
# ─────────────────────────────────────────────────────────────
def slider(source_type, key):
    """Renders a date slider and returns the filtered dataframe for the
    requested source ('actual' or 'forecast'). `key` must be unique per
    call so Streamlit doesn't collide multiple sliders with the same label."""
    if source_type == "actual":
        df = actual.copy()
    else:
        df = forecast.copy()

    min_date = df['ds'].min()
    max_date = df['ds'].max()

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
    """Adds the reporting threshold line and standard layout to a Plotly figure."""
    fig.add_hline(
        y=THRESHOLD,
        line_dash="dash",
        line_color="#F59E0B",  # Golden Yellow accent
        line_width=2,
        annotation_text="Reporting threshold (10,000 gal)",
        annotation_position="top right",
        annotation_font_color="#B45309"
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Gallons",
        height=520,
        plot_bgcolor="rgba(255,255,255,0.0)",   # transparent plot area
        paper_bgcolor="rgba(255,255,255,0.0)",  # transparent outer area
        font=dict(family="Inter, sans-serif", color="#1E293B"),
        margin=dict(l=40, r=20, t=30, b=40),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


# ─────────────────────────────────────────────────────────────
# 6. TABS
# ─────────────────────────────────────────────────────────────
tab_actual, tab_forecast, tab_upper, tab_lower, tab_info = st.tabs(
    ["📊 Actual", "📈 Forecast", "⬆️ Upper Bound", "⬇️ Lower Bound", "ℹ️ Information"]
)

# ── Tab 1: Actual ──
with tab_actual:
    visible_actual = slider("actual", key="slider_actual")
    st.subheader("Actual Discharge Volume")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_actual['ds'],
        y=visible_actual['discharge_volume_clean'],
        mode='markers',
        name='Actual',
        marker=dict(size=5, color='#4B6EF5', opacity=0.75,
                    line=dict(width=1, color='white'))
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

# ── Tab 2: Forecast ──
with tab_forecast:
    visible_forecast = slider("forecast", key="slider_forecast")
    st.subheader("Forecasted Discharge Volume")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_forecast['ds'],
        y=visible_forecast['yhat_gallons'],
        mode='lines',
        name='Forecast',
        line=dict(color='#DC2626', width=2.5)
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

# ── Tab 3: Upper Bound ──
with tab_upper:
    visible_upper = slider("forecast", key="slider_upper")
    st.subheader("Upper Bound — yhat_upper_gallons")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_upper['ds'],
        y=visible_upper['yhat_upper_gallons'],
        mode='lines',
        name='Upper bound',
        line=dict(color='#8B5CF6', width=2.5)
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

# ── Tab 4: Lower Bound ──
with tab_lower:
    visible_lower = slider("forecast", key="slider_lower")
    st.subheader("Lower Bound — yhat_lower_gallons")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=visible_lower['ds'],
        y=visible_lower['yhat_lower_gallons'],
        mode='lines',
        name='Lower bound',
        line=dict(color='#10B981', width=2.5)
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

# ── Tab 5: Information ──
with tab_info:
    st.subheader("About this model")
    st.write(
        "Forecast generated with **Prophet**, trained on log-transformed weekly statewide "
        "sewage discharge volume. The threshold reflects **COMAR 26.08.10**'s 10,000-gallon "
        "public reporting trigger for sanitary sewer overflows."
    )
    st.markdown("---")
    st.markdown(
        """
        #### Color Palette Used
        *Inspired by Environmental Science & Sustainability*

        | Color | Hex | Role |
        |-------|-----|------|
        | 🟢 Deep Green | `#166534` | Primary — Trust, stability, conservation |
        | 🌿 Green | `#15803d` | Secondary — Nature, growth, renewal |
        | 🟡 Golden Yellow | `#CA8A04` | Accent — Energy, optimism, hope |
        | 🔵 Ocean Teal | `#1E6F74` | Support — Water, calm, balance |
        | 🔷 Soft Blue | `#ABDADC` | Support — Clean air, clarity, peace |
        | 🟤 Earth Brown | `#78716C` | Neutral — Soil, land, authenticity |
        | ⚪ Light Background | `#F7FAF8` | Clean, open, readable |
        """
    )


# ─────────────────────────────────────────────────────────────
# 7. FORECAST STATUS MESSAGE
# ─────────────────────────────────────────────────────────────
# Use the Forecast tab's own slider selection
current_val = visible_forecast['yhat_gallons'].iloc[-1] if len(visible_forecast) else 0

if current_val > THRESHOLD:
    st.markdown(
        f"""
        <div class="status-error">
            ⚠️ Forecasted discharge ({current_val:,.0f} gal) exceeds the 10,000-gallon reporting threshold
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div class="status-success">
            ✅ Forecasted discharge ({current_val:,.0f} gal) is within the 10,000-gallon reporting threshold
        </div>
        """,
        unsafe_allow_html=True
    )
