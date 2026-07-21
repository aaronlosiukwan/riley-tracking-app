import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & PAGE TITLE
# ==========================================
st.set_page_config(
    page_title="Baby Tracker Dashboard",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Mobile Styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍼 Baby Tracker Dashboard")

# ==========================================
# 2. GOOGLE SHEET CONNECTOR
# ==========================================
# Sidebar input for Google Sheet Link
st.sidebar.header("⚙️ Configuration")
sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL or ID",
    value="",
    help="Paste your published Google Sheet link or Sheet ID here."
)

# Function to extract CSV URL from Google Sheet Link
def get_csv_export_url(url_or_id):
    if not url_or_id:
        return None
    # If full URL pasted
    if "docs.google.com/spreadsheets" in url_or_id:
        sheet_id = url_or_id.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    # If only Sheet ID pasted
    return f"https://docs.google.com/spreadsheets/d/{url_or_id}/export?format=csv"

# Real-time caching: TTL set to 10 seconds to constantly grab live updates!
@st.cache_data(ttl=10)
def load_sheet_data(csv_url):
    try:
        df = pd.read_csv(csv_url)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Convert DateTime
        if 'DateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        elif 'EntryDateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['EntryDateTime'], errors='coerce')
            
        # Standardize Date column
        df['Date'] = df['DateTime'].dt.date
        
        # Ensure Value (Optional) is numeric
        if 'Value (Optional)' in df.columns:
            df['Value (Optional)'] = pd.to_numeric(df['Value (Optional)'], errors='coerce').fillna(1.0)
        else:
            df['Value (Optional)'] = 1.0
            
        # Clean Event Type column
        if 'Event Type' in df.columns:
            df['Event Type'] = df['Event Type'].astype(str).str.strip()
            
        return df.dropna(subset=['DateTime']).sort_values('DateTime', ascending=False)
    except Exception as e:
        st.error(f"Error reading Google Sheet data: {e}")
        return pd.DataFrame()

# Manual Refresh Button
col_title, col_ref = st.columns([3, 1])
with col_ref:
    if st.button("🔄 Sync Sheet", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Default fallback URL if user hasn't set one yet in sidebar
csv_url = get_csv_export_url(sheet_url_input)

if not csv_url:
    st.info("💡 **Welcome!** Please paste your Google Sheet link in the sidebar menu on the left to display your live tracker data.")
    st.stop()

df = load_sheet_data(csv_url)

if df.empty:
    st.warning("No data found in the spreadsheet. Please check your Google Sheet share permissions.")
    st.stop()

# ==========================================
# 3. DATE RANGE FILTER
# ==========================================
today = datetime.now().date()

filter_option = st.radio(
    "View Range:",
    ["Today", "Last 7 Days", "Last 30 Days", "All Time"],
    horizontal=True
)

if filter_option == "Today":
    filtered_df = df[df['Date'] == today]
elif filter_option == "Last 7 Days":
    filtered_df = df[df['Date'] >= (today - timedelta(days=7))]
elif filter_option == "Last 30 Days":
    filtered_df = df[df['Date'] >= (today - timedelta(days=30))]
else:
    filtered_df = df.copy()

# ==========================================
# 4. TODAY'S KPI SUMMARY CARDS
# ==========================================
st.subheader("⚡ Today's Quick Summary")

today_df = df[df['Date'] == today]

# Calculate Totals
formula_tot = today_df[today_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
bm_tot = today_df[today_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
wet_cnt = len(today_df[today_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
poop_cnt = len(today_df[today_df['Event Type'].str.contains("Poop", case=False, na=False)])

# Last Feeding Time
feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not feed_events.empty:
    last_feed_time = feed_events.iloc[0]['DateTime']
    time_since_feed = datetime.now() - last_feed_time
    hours_since = int(time_since_feed.total_seconds() // 3600)
    mins_since = int((time_since_feed.total_seconds() % 3600) // 60)
    last_feed_str = f"{hours_since}h {mins_since}m ago ({last_feed_time.strftime('%I:%M %p')})"
else:
    last_feed_str = "N/A"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("🍼 Formula Today", f"{int(formula_tot)} mL")
kpi2.metric("🤱 Breast Milk", f"{int(bm_tot)} mL")
kpi3.metric("💧 Wet / 💩 Poop", f"{wet_cnt} / {poop_cnt}")
kpi4.metric("⏰ Last Feed", last_feed_str)

st.divider()

# ==========================================
# 5. VISUALIZATIONS & CHARTS
# ==========================================
st.subheader("📊 Trends & Analytics")

tab1, tab2, tab3 = st.tabs(["🍼 Milk Intake", "🚽 Diapers & Output", "📈 Timeline"])

with tab1:
    # Daily Feeding Chart
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
    if not milk_df.empty:
        daily_milk = milk_df.groupby(['Date', 'Event Type'])['Value (Optional)'].sum().reset_index()
        fig_milk = px.bar(
            daily_milk,
            x="Date",
            y="Value (Optional)",
            color="Event Type",
            title="Daily Milk Intake (mL)",
            barmode="stack",
            color_discrete_map={
                "Formula (mL)": "#4DA6FF",
                "🍼 Formula (mL)": "#4DA6FF",
                "Breast Milk (mL)": "#FF80BF",
                "🤱 Breast Milk (mL)": "#FF80BF"
            }
        )
        fig_milk.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_milk, use_container_width=True)
    else:
        st.info("No feeding data in selected range.")

with tab2:
    # Daily Diapers Chart
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
    if not diaper_df.empty:
        daily_diaper = diaper_df.groupby(['Date', 'Event Type']).size().reset_index(name='Count')
        fig_diaper = px.bar(
            daily_diaper,
            x="Date",
            y="Count",
            color="Event Type",
            title="Daily Diapers Count",
            barmode="group",
            color_discrete_map={
                "Wet Diaper (Cnt)": "#3399FF",
                "💧 Wet Diaper (Cnt)": "#3399FF",
                "Poop (Cnt)": "#CC9966",
                "💩 Poop (Cnt)": "#CC9966"
            }
        )
        fig_diaper.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_diaper, use_container_width=True)
    else:
        st.info("No diaper data in selected range.")

with tab3:
    # Activity Timeline Scatter
    if not filtered_df.empty:
        fig_time = px.scatter(
            filtered_df,
            x="DateTime",
            y="Event Type",
            size="Value (Optional)",
            color="Event Type",
            title="Event Timeline",
            size_max=18
        )
        fig_time.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_time, use_container_width=True)

st.divider()

# ==========================================
# 6. RAW DATA TABLE
# ==========================================
st.subheader("📋 Raw Data Logs")

# Search and Event Filter
search_col, event_col = st.columns([2, 2])
with search_col:
    search_query = st.text_input("🔍 Search notes or values:", "")
with event_col:
    event_options = ["All"] + list(df['Event Type'].unique())
    selected_event = st.selectbox("Filter Event Type:", event_options)

table_df = filtered_df.copy()

if selected_event != "All":
    table_df = table_df[table_df['Event Type'] == selected_event]

if search_query:
    table_df = table_df[
        table_df['Event Type'].str.contains(search_query, case=False, na=False) |
        table_df['Notes / Details (Optional)'].astype(str).str.contains(search_query, case=False, na=False)
    ]

# Display columns neatly
display_cols = [c for c in ['DateTime', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)'] if c in table_df.columns]
st.dataframe(
    table_df[display_cols].style.format({'DateTime': lambda x: x.strftime('%Y-%m-%d %I:%M %p') if pd.notnull(x) else ''}),
    use_container_width=True,
    height=350
)
