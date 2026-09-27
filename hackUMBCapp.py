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


# 2. GLOBAL CSS INJECTION (Modern Clean UI)
st.markdown(
    """
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        /* Global Solid Background */
        .stApp {
            background-color: #ADD8E6 ; 
            font-family: 'Inter', sans-serif;
        }
         /* Force standard text elements to be dark */
        p, span, div, label, .stMarkdown {
            color: #1E293B !important;
        }

        /* Header Section */
        .header-container {
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 50%, #A7F3D0 100%);
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

        /*  Clean Content Box */
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
            background: linear-gradient(135deg, #D1FAE5, #A7F3D0) !important;
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
        annotation_font_color="#B45309" # Darker amber for readability
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Gallons",
        height=520,
        plot_bgcolor="rgba(255,255,255,0.0)",   # transparent plot area
        paper_bgcolor="rgba(255,255,255,0.0)",  # transparent outer area
        font=dict(family="Inter, sans-serif", color="#1E293B"), # Global font color
        
        # --- FORCE DARK TEXT ON AXES ---
        xaxis=dict(
            title_font=dict(color="#1E293B"),
            tickfont=dict(color="#1E293B")
        ),
        yaxis=dict(
            title_font=dict(color="#1E293B"),
            tickfont=dict(color="#1E293B")
        ),
        
        # --- FORCE DARK TEXT ON LEGEND ---
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#1E293B")
        ),
        
        # --- FORCE DARK TEXT ON HOVER LABELS ---
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter, sans-serif",
            font_color="#1E293B"
        ),
        
        margin=dict(l=40, r=20, t=30, b=40),
        hovermode="x unified"
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
# ── Tab 5: Information ──
with tab_info:
    st.subheader("ℹ️ About This Application")
    st.write(
        "This application is an interactive dashboard for exploring historical sewage discharge "
        "volumes in Maryland and viewing short-term forecasts. It is designed to help the public, "
        "researchers, and policymakers better understand patterns in wastewater overflows and the "
        "risks they pose to water quality."
    )
    st.markdown("---")

    # ── Section 1: Model ──
    st.markdown("### 📈 About the Forecast Model (Prophet)")
    st.write(
        "The forecasts shown in this dashboard were generated using **Prophet**, an open-source "
        "forecasting procedure released by Facebook's Core Data Science team. Prophet is "
        "implemented in both R and Python and is available on CRAN and PyPI. It is designed to "
        "handle time series data with strong seasonal effects, missing data, and outliers — all "
        "common characteristics of environmental monitoring data.[reference:0]"
    )
    st.write(
        "The model decomposes a time series into three main components: **trend** (non-linear "
        "growth or decline), **seasonality** (yearly, weekly, and daily patterns), and **holiday "
        "effects**. This additive approach allows the model to capture the complex, multi-scale "
        "patterns present in sewage discharge volumes.[reference:1]"
    )
    st.write(
        "For this dashboard, Prophet was trained on log-transformed weekly statewide sewage "
        "discharge volume data. The log transformation helps stabilize the variance and "
        "normalizes the distribution of the data, which improves forecast accuracy. The model "
        "outputs point forecasts (`yhat_gallons`) along with uncertainty intervals "
        "(`yhat_upper_gallons` and `yhat_lower_gallons`), which are visualized in the **Forecast**, "
        "**Upper Bound**, and **Lower Bound** tabs."
    )
    st.markdown("---")

    # ── Section 2: Maryland Sewage History ──
    st.markdown("### 📜 Memorable Moments in Maryland Sewage History")
    st.write(
        "Maryland has a long and complex relationship with its wastewater infrastructure. "
        "Below are some of the most significant sewage-related events that have shaped public "
        "policy and environmental awareness in the state."
    )

    st.markdown("#### 🚨 January 2026 — The Potomac Interceptor Collapse")
    st.write(
        "On January 19, 2026, a catastrophic collapse of a 72-inch sewer line near Cabin John, "
        "Maryland made national news. The rupture sent approximately **244 million gallons** of "
        "raw sewage into the Potomac River over the following weeks — enough wastewater to fill "
        "the entire D.C. Tidal Basin. Many experts called it the largest sewage spill in U.S. "
        "history. The incident prompted federal and state lawsuits against DC Water, which "
        "allegedly ignored warning signs of imminent failure for at least eight years.[reference:2][reference:3]"
    )

    st.markdown("#### 🌊 August 2014 — Baltimore-Area Overflows into the Patapsco")
    st.write(
        "In August 2014, three major sanitary sewer overflows were reported in the Baltimore "
        "region during a period of near-record rainfall. The largest spill occurred at the "
        "Patapsco Wastewater Treatment Plant in Fairfield, dumping approximately **3 million "
        "gallons** of untreated, diluted wastewater into the Patapsco River. The event "
        "highlighted the vulnerability of aging combined sewer systems to extreme weather.[reference:4]"
    )

    st.markdown("#### 🏛️ 2002 — Baltimore Consent Decree")
    st.write(
        "In 2002, the U.S. Justice Department sued Baltimore over chronic sewage discharges "
        "from its leaky, overloaded system. The city entered into a Consent Decree with the "
        "EPA and the Maryland Department of the Environment (MDE), pledging to end overflows "
        "and undertake a **$940 million** upgrade to its sewage treatment system. The decree "
        "estimated that **100 million gallons** of sewage had been discharged into the Patapsco "
        "River and its tributaries between 1996 and 2002. This marked a turning point in "
        "Maryland's approach to wastewater infrastructure.[reference:5][reference:6]"
    )
    st.markdown("---")

    # ── Section 3: Emergency Contacts ──
    st.markdown("### 📞 Emergency Contacts")
    st.write(
        "If you witness a sewage overflow, discharge, or any environmental emergency in "
        "Maryland, report it immediately using the contacts below. Early reporting helps "
        "protect public health and the environment."
    )

    st.markdown("#### Maryland Department of the Environment (MDE)")
    st.markdown(
        """
        - **24-Hour Emergency Response:** `1-866-633-4686` (toll-free)
        - **General Information:** `1-800-633-6101`
        - **Chesapeake Bay Safety & Environmental Hotline:** `1-877-224-7229`
        - **Water Quality Monitoring:** `1-800-285-8195`
        - **Water & Wastewater Emergency Line:** `1-800-669-7080`
        """,
        unsafe_allow_html=True
    )
    st.caption("Source: State of Maryland Toll-Free Numbers Directory[reference:7]")

    st.markdown("#### County-Level Contacts")
    st.markdown(
        """
        - **Washington Suburban Sanitary Commission (WSSC):** `(301) 206-8000` (business hours) | After hours: MDE Emergency Response `1-866-633-4686`
        - **Anne Arundel County Utility Operations (24-Hour Emergency):** `410-222-8400`
        - **Talbot County Sanitary District Emergency Line:** `1-877-469-3494`
        - **Howard County Bureau of Utilities Customer Service:** `(410) 313-4900`
        """,
        unsafe_allow_html=True
    )
    st.caption("Sources: WSSC, Anne Arundel County, Talbot County, Howard County[reference:8]")
    st.markdown("---")

    # ── Section 4: Color Palette ──
    st.markdown("### 🎨 Color Palette Used")
    st.markdown(
        """
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
# 8. IMAGES AT THE BOTTOM OF THE PAGE
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("[Potomac River Sewage Spill — January 2026](https://potomacriverkeepernetwork.org/potomac-sewage-spill-data-updates/)")
st.caption(
    "Images from the catastrophic collapse of the Potomac Interceptor sewer line near "
    "Cabin John, Maryland. Approximately 244 million gallons of raw sewage flowed into "
    "the Potomac River over several weeks."
)

# Create a row of images with captions
img_col1, img_col2, img_col3 = st.columns(3)

with img_col1:
    st.image(
        "hack1_img3.webp",
        caption="Image from leakage",
        use_container_width=True
    )

with img_col2:
    st.image(
        "hack1_img1.webp",
        caption="Image from leakage",
        use_container_width=True
    )

with img_col3:
    st.image(
        "hack1_img2.webp",
        caption="Image from leakage",
        use_container_width=True
    )
