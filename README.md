**Maryland Sewage Discharge Forecast**
An interactive Streamlit dashboard for exploring historical sewage discharge data in Maryland and viewing short-term forecasts of statewide discharge volumes. Built to help the public, researchers, and policymakers better understand patterns in wastewater overflows and their risks to water quality.


**Overview**
Maryland's wastewater infrastructure is aging, and sanitary sewer overflows (SSOs) pose ongoing risks to public health and the Chesapeake Bay watershed. This project combines:
- Historical discharge records from the Maryland Department of the Environment (MDE) Open Data Portal
- Time series forecasting using Meta's Prophet model
- An interactive dashboard that lets users explore trends, drill into zipcode-level rankings, and understand where forecasts sit relative to the state's regulatory threshold
- The dashboard uses a sustainability-inspired color palette (deep green, golden yellow, ocean teal, earth brown) to convey environmental responsibility and trust.

**Features**
Actual Tab
- Scatter plot of every recorded sewage discharge event
- Summary metrics: total discharges, peak volume, average volume
- Interactive date slider to filter by cutoff date

Forecast Tab
- Statewide discharge forecast using Prophet
- Faded historical data for context
- Forecast line begins exactly where actual data ends
- 10,000-gallon reporting threshold overlay (COMAR 26.08.10)

Upper Bound & Lower Bound Tabs
- Visualize the uncertainty intervals of the Prophet forecast

**Zipcode Rankings Tab**
- Cumulative discharge volume aggregated by zipcode
- Slider spans both actual and forecast periods
- Automatically switches from actual rankings (green status) to projected rankings (red status) once the slider passes the last actual date

**Information Tab**
- Model methodology (Prophet)
- Regulatory context (COMAR 26.08.10, Clean Water Act)
- Maryland sewage history (major spills and policy milestones)
- Emergency contacts (MDE, WSSC, county utilities)



Tech Stack
Layer	            Technology
Frontend	        Streamlit
Visualization	    Plotly
Data Processing	    pandas, NumPy
Forecasting	        Prophet (Meta Open Source)
Styling	            Custom CSS with glassmorphism
Hosting	            Streamlit Community Cloud
