import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. PAGE CONFIGURATION
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

        /* Tab Styling */
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

        /*Status Boxes*/
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

        /* Slider Label */
        .stSlider > label {
            font-size: 15px;
            font-weight: 600;
            color: #BFB8AC;
        }

        /* Subheader  */
        .stSubheader, h2, h3 {
            color: #BFB8AC !important;
            font-weight: 700 !important;
        }

        /* Plotly Chart Container */
        .stPlotlyChart {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 8px;
        }

        /* Caption */
        .stCaption {
            color: #475569;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. DATA LOADING
@st.cache_data
def load_forecast():
    return pd.read_csv("forecast2.csv", parse_dates=["ds"])


@st.cache_data
def load_actual():
    df = pd.read_csv("actual1.csv", parse_dates=["date"])
    df = df.rename(columns={"date": "ds"})
    return df

forecast = load_forecast()
actual = load_actual()

# 4. HEADER SECTION
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

# 5. HELPER FUNCTIONS (Sliders, Threshold Line)
# 5. HELPER FUNCTIONS (Sliders, Threshold Line)
def slider(source_type, key):
    """
    Render a date slider and return the filtered dataframe.

    - source_type="actual"   → slider spans only actual dates, returns actual rows.
    - source_type="forecast" → slider spans only FUTURE dates (after the last
                               actual date), returns forecast rows.
    """
    # Anchor: the last date we have real observations for
    last_actual_date = actual['ds'].max()

    if source_type == "actual":
        df = actual.copy()
    else:
        # Only keep future forecast rows (drop any historical/backcast values)
        df = forecast[forecast['ds'] > last_actual_date].copy()

    if df.empty:
        st.warning(f"No data available for '{source_type}'.")
        return df

    min_date = df['ds'].min()
    max_date = df['ds'].max()

    selected_date = st.slider(
        "Show data up to",
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
        
        # FORCE DARK TEXT ON LEGEND 
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#1E293B")
        ),
        
        # FORCE DARK TEXT ON HOVER LABELS 
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
    
# 6. TABS
tab_actual, tab_forecast, tab_upper, tab_lower, tab_zip, tab_info = st.tabs(
    ["📊 Actual", "📈 Forecast", "⬆️ Upper Bound", "⬇️ Lower Bound", "🏆 Zipcode Rankings", "ℹ️ Information"]
)

# Tab 1: Actual 
with tab_actual:
    visible_actual = slider("actual", key="slider_actual")
    st.subheader("Actual Discharge Volume")
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Discharges", f"{len(visible_actual):,}")
    col2.metric("Peak Volume", f"{visible_actual['discharge_volume_clean'].max():,.0f} gal")
    col3.metric("Average Volume", f"{visible_actual['discharge_volume_clean'].mean():,.0f} gal")
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

# Tab 2: Forecast 
with tab_forecast:
    visible_forecast = slider("forecast", key="slider_forecast")
    st.subheader("Forecasted Discharge Volume")
    fig = go.Figure()
    # Main Forecast Line
    fig.add_trace(go.Scatter(
        x=visible_forecast['ds'], y=visible_forecast['yhat_gallons'],
        mode='lines', name='Forecast', line=dict(color='#DC2626', width=2.5)
    ))
    st.plotly_chart(add_threshold(fig), use_container_width=True)

# Tab 3: Upper Bound 
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

# Tab 4: Lower Bound 
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

# ── Tab 5: Zipcode Rankings ──
with tab_zip:
    st.subheader("🏆 Discharge Ranking by Zipcode")
    st.caption(
        "Cumulative sewage discharge volume aggregated by zipcode. The slider spans both "
        "actual observations and the forecast period. Rankings beyond the last actual date "
        "are **projected** using the statewide forecast trend."
    )

    # ── 1. Prepare zipcode data ──
    zip_data = actual.copy()
    zip_data['zip'] = pd.to_numeric(zip_data['zip'], errors='coerce')
    zip_data = zip_data.dropna(subset=['zip', 'discharge_volume_clean'])
    zip_data = zip_data[zip_data['discharge_volume_clean'] > 0]
    zip_data['zip'] = zip_data['zip'].astype(int).astype(str)
    zip_data['ds'] = pd.to_datetime(zip_data['ds'])

    # Aggregate daily volume per zipcode
    zip_daily = (
        zip_data.groupby(['ds', 'zip'])['discharge_volume_clean']
        .sum()
        .reset_index()
    )

    # ── 2. Date slider spanning actual + forecast ──
    min_date = zip_daily['ds'].min()
    max_date = forecast['ds'].max()

    selected_date = st.slider(
        "Select a date to see the ranking",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=min_date.to_pydatetime(),
        format="YYYY-MM-DD",
        key="slider_zip_ranking"
    )
    selected_date = pd.to_datetime(selected_date)

    last_actual_date = zip_daily['ds'].max()
    is_projected = selected_date > last_actual_date

    # ── 3. Compute ranking (actual or projected) ──
    if not is_projected:
        filtered = zip_daily[zip_daily['ds'] <= selected_date]
        totals = (
            filtered.groupby('zip')['discharge_volume_clean']
            .sum()
            .sort_values(ascending=False)
        )
        status_html = (
            f"<div class='status-success'>📊 Showing <b>actual</b> cumulative discharge "
            f"through <b>{selected_date.date()}</b></div>"
        )
        header_label = "Actual Cumulative Discharge"
    else:
        last_totals = (
            zip_daily[zip_daily['ds'] <= last_actual_date]
            .groupby('zip')['discharge_volume_clean']
            .sum()
        )

        forecast_clean = forecast[['ds', 'yhat_gallons']].copy()
        last_forecast_val = forecast_clean[
            forecast_clean['ds'] <= last_actual_date
        ]['yhat_gallons'].iloc[-1]
        selected_forecast_val = forecast_clean[
            forecast_clean['ds'] <= selected_date
        ]['yhat_gallons'].iloc[-1]

        scale = selected_forecast_val / last_forecast_val if last_forecast_val > 0 else 1
        totals = (last_totals * scale).sort_values(ascending=False)

        status_html = (
            f"<div class='status-error'>🔮 Showing <b>projected</b> ranking for "
            f"<b>{selected_date.date()}</b> — based on statewide forecast trend "
            f"(scaled by {scale:.2f}×)</div>"
        )
        header_label = "Projected Cumulative Discharge"

    st.markdown(status_html, unsafe_allow_html=True)

    # ── 4. Show top 10 as a ranked list ──
    TOP_N = 10
    top_n = totals.head(TOP_N)
    total_statewide = totals.sum()

    st.markdown(
        f"<h4 style='color:#14532D; margin-top: 24px;'>{header_label} — Top {TOP_N} Zipcodes</h4>",
        unsafe_allow_html=True
    )


    for rank, (zipcode, volume) in enumerate(top_n.items(), start=1):
        pct = (volume / total_statewide * 100) if total_statewide > 0 else 0

        bar_color = "#166534"   # Deep green

        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                background: #FFFFFF;
                border-radius: 12px;
                padding: 14px 20px;
                margin-bottom: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                border-left: 6px solid {bar_color};
            ">
                <div style="
                    font-size: 26px;
                    font-weight: 700;
                    width: 60px;
                    text-align: center;
                    color: {bar_color};
                <div style="flex: 1; padding-left: 16px;">
                    <div style="font-size: 18px; font-weight: 700; color: #14532D;">
                        Zipcode {zipcode}
                    </div>
                    <div style="font-size: 13px; color: #475569;">
                        {pct:.2f}% of statewide total
                    </div>
                </div>
                <div style="
                    font-size: 20px;
                    font-weight: 700;
                    color: #1E293B;
                    text-align: right;
                ">
                    {volume:,.0f} gal
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── 5. Key metrics below the ranking ──
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Zipcodes Reporting", f"{len(totals):,}")
    col2.metric("Statewide Total", f"{total_statewide:,.0f} gal")
    col3.metric(
        "Top Zipcode",
        str(top_n.index[0]),
        f"{top_n.values[0]:,.0f} gal"
    )
# Tab 5: Information 
with tab_info:
    st.subheader("ℹ️ About This Application")
    st.write(
        "This application is an interactive dashboard for exploring historical sewage discharge "
        "volumes in Maryland and viewing short-term forecasts. It is designed to help the public, "
        "researchers, and policymakers better understand patterns in wastewater overflows and the "
        "risks they pose to water quality. The Maryland Department of the Environment (MDE) regulatory threshold of 10,000 gallons, "
        "the state's public-reporting trigger for sanitary sewer overflows, serves as a key reference point for assessing current conditions and compliance. "
    )
    st.info(
        "**Why 10,000 gallons?** Under COMAR 26.08.10, any sanitary sewer overflow "
        "exceeding 10,000 gallons must be reported to the Maryland Department of the Environment (MDE). "
        "This threshold helps prioritize emergency response and track compliance with the Clean Water Act."
    )      
    st.markdown("---")

    # Section 1: Model 
    st.markdown("### 📈 About the Forecast Model (Prophet)")
    st.write(
        "The forecasts shown in this dashboard were generated using **Prophet**, an open-source "
        "forecasting procedure released by Facebook's Core Data Science team. Prophet is "
        "implemented in both R and Python and is available on CRAN and PyPI. It is designed to "
        "handle time series data with strong seasonal effects, missing data, and outliers; all of ehich are "
        "common characteristics of [environmental monitoring data](https://opendata.maryland.gov/Government/Reported-Sewer-Overflows-New-for-2023-/stgj-u72u/about_data)."
    )
    st.write(
        "The model decomposes a time series into three main components: **trend** (non-linear "
        "growth or decline), **seasonality** (yearly, weekly, and daily patterns), and **holiday "
        "effects**. This additive approach allows the model to capture the complex, multi-scale "
        "patterns present in sewage discharge volumes."
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

    #  Section 2: Maryland Sewage History
    st.markdown("### 📜 Unfortunate Moments in Maryland Sewage History")
    st.write(
        "Maryland has a long and complex relationship with its wastewater infrastructure. "
        "Below are some of the most significant sewage-related events that have shaped public "
        "policy and environmental awareness in the state."
    )
    st.markdown("#### January 2026 — The Potomac Interceptor Collapse")
    st.write(
        "On January 19, 2026, a catastrophic collapse of a 72-inch sewer line near Cabin John, "
        "Maryland made national news. The rupture sent approximately **244 million gallons** of "
        "raw sewage into the Potomac River over the following weeks — enough wastewater to fill "
        "the entire D.C. Tidal Basin. Many experts called it the largest sewage spill in U.S. "
        "history. The incident prompted federal and state lawsuits against DC Water, which "
        "allegedly ignored warning signs of imminent failure for at least eight years."
    )

    st.markdown("#### 2018 — A Year of Record Rainfall and Catastrophic Overflows")
    st.write(
        "2018 was one of the wettest years on record in Maryland, and the state's aging sewer "
        "systems buckled under the pressure. In **May**, torrential rains triggered destructive "
        "flash flooding in Ellicott City, rupturing a sewage main about two miles from downtown. "
        "As much as **500,000 gallons** of sewage spilled, prompting Howard County officials to "
        "issue a precautionary health alert and warn residents to stay away from affected "
        "waterways. [The flooding also claimed the life of a National Guard member who was swept "
        "away while trying to help a woman rescue her pet](https://www.cnn.com/2018/05/29/us/ellicott-city-maryland-flooding-missing-guardsman/)."
    )
    st.write(
        "The overflows continued through the summer. In **July**, historic rainfall overwhelmed "
        "Baltimore's sewer system, causing more than **45 million gallons** of sewage-"
        "contaminated stormwater to flow into the city's streams and harbor over just five days — "
        "enough to fill more than 68 Olympic swimming pools. Much of the overflow was released "
        "through structured overflows that were part of the city's sewer design over a century "
        "ago. The event underscored the urgent need for the city to complete its consent decree "
        "obligations under the Clean Water Act."
    )
    st.write(
        "Earlier that summer, in **June**, nearly **6 million gallons** of raw sewage poured into "
        "Mattawoman Creek in Charles County after multiple pump failures at a local pumping "
        "station."
    )

    st.markdown("#### August 2014 — Baltimore-Area Overflows into the Patapsco")
    st.write(
        "In August 2014, three major sanitary sewer overflows were reported in the Baltimore "
        "region during a period of near-record rainfall. The largest spill occurred at the "
        "Patapsco Wastewater Treatment Plant in Fairfield, dumping approximately **3 million "
        "gallons** of untreated, diluted wastewater into the Patapsco River. The event "
        "highlighted the vulnerability of aging combined sewer systems to extreme weather."
    )

    st.markdown("#### 2002 — Baltimore Consent Decree")
    st.write(
        "In 2002, the U.S. Justice Department sued Baltimore over chronic sewage discharges "
        "from its leaky, overloaded system. The city entered into a Consent Decree with the "
        "EPA and the Maryland Department of the Environment (MDE), pledging to end overflows "
        "and undertake a **$940 million** upgrade to its sewage treatment system. The decree "
        "estimated that **100 million gallons** of sewage had been discharged into the Patapsco "
        "River and its tributaries between 1996 and 2002. This marked a turning point in "
        "Maryland's approach to wastewater infrastructure."
    )
    st.markdown("---")

    # Section 3: Emergency Contacts 
    st.markdown("### Emergency Contacts")
    st.write(
        "If you witness a sewage overflow, discharge, or any environmental emergency in "
        "Maryland, report it immediately using the contacts below. Early reporting helps "
        "protect public health and the environment."
    )

    st.markdown("#### [Maryland Department of the Environment (MDE)](https://mde.maryland.gov/Pages/index.aspx)")
    st.markdown(
        """
        - **24-Hour Emergency Response:** 1-866-633-4686
        """,
        unsafe_allow_html=True
    )
    st.caption("[For more details on contact](https://mde.maryland.gov/Pages/contactus.aspx)")

    st.markdown("#### County-Level Contacts")
    st.markdown(
        """
        - **Washington Suburban Sanitary Commission [(WSSC)](https://www.wsscwater.com/customer-service/report-problem/emergency-water-and-sewer-problems):** 301-206-4001 
        - **After hours: MDE Emergency Response** 1-866-633-4686
        - **Anne Arundel County Utility Operations [(24-Hour Emergency)](https://www.aacounty.org/public-works/utilities/watersewer-emergency):** 410-222-8400
        """,
        unsafe_allow_html=True
    )
               
    st.caption("Sources: WSSC, Anne Arundel County")
    st.markdown("---")

    
# 8. IMAGES AT THE BOTTOM OF THE PAGE
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
