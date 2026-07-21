import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley Growth Log",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive & Adaptive CSS for Light & Dark Theme Support
st.markdown("""
    <style>
    /* Metric Card Styling adaptable to Light & Dark Mode */
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 14px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .stApp {
        padding-top: 0.5rem;
    }

    /* Container for empty state notice */
    .empty-data-card {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1.5px dashed rgba(128, 128, 128, 0.3);
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }
    .empty-data-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .empty-data-sub {
        font-size: 0.9rem;
        opacity: 0.7;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍼 Riley Growth Log")

# ==========================================
# 2. GOOGLE SHEET CONNECTOR & AUTO SYNC
# ==========================================
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"

st.sidebar.header("⚙️ Configuration")

sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL or ID",
    value=DEFAULT_SHEET_URL,
    help="Defaulted to your master Google Sheet URL."
)

def get_csv_export_url(url_or_id):
    if not url_or_id:
        return None
    if "docs.google.com/spreadsheets" in url_or_id:
        try:
            sheet_id = url_or_id.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        except IndexingError:
            return None
    return f"https://docs.google.com/spreadsheets/d/{url_or_id}/export?format=csv"

# Fetch data directly with 5-second caching for real-time live sync
@st.cache_data(ttl=5)
def load_sheet_data(csv_url):
    try:
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        
        # Standardize DateTime
        if 'DateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        elif 'EntryDateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['EntryDateTime'], errors='coerce')
        else:
            # Fallback
            date_col = [c for c in df.columns if 'date' in c.lower()]
            if date_col:
                df['DateTime'] = pd.to_datetime(df[date_col[0]], errors='coerce')
            
        df = df.dropna(subset=['DateTime'])
        
        # Calculate Date, Week (Monday start), Month
        df['Date'] = df['DateTime'].dt.date
        df['Week'] = df['DateTime'].dt.to_period('W-SUN').dt.start_time.dt.date
        df['Month'] = df['DateTime'].dt.strftime('%Y-%m')
        
        # Ensure Numeric Values
        if 'Value (Optional)' in df.columns:
            df['Value (Optional)'] = pd.to_numeric(df['Value (Optional)'], errors='coerce').fillna(1.0)
        else:
            df['Value (Optional)'] = 1.0

        if 'Event Type' in df.columns:
            df['Event Type'] = df['Event Type'].astype(str).str.strip()
            
        return df.sort_values('DateTime', ascending=False)
    except Exception as e:
        st.error(f"Error connecting to Google Sheet: {e}")
        return pd.DataFrame()

csv_url = get_csv_export_url(sheet_url_input)

# Top Bar controls
top_col1, top_col2 = st.columns([3, 1])
with top_col2:
    if st.button("🔄 Sync Sheet Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if not csv_url:
    st.info("💡 Please provide a valid Google Sheet URL in the sidebar.")
    st.stop()

df = load_sheet_data(csv_url)

if df.empty:
    st.warning("⚠️ No data retrieved. Please make sure your Google Sheet access is set to 'Anyone with the link can view'.")
    st.stop()

# Set up Theme-aware Plotly helper
def style_plotly_figure(fig, height=520):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        font=dict(family="sans-serif", size=13),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
    )
    return fig

# ==========================================
# 3. DATE RANGE & GRANULARITY FILTERS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Filters")

range_option = st.sidebar.radio(
    "Select Range:",
    ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"]
)

min_data_date = df['Date'].min()
max_data_date = df['Date'].max()

# Custom date picker
if range_option == "Custom Range":
    start_date = st.sidebar.date_input("Start Date (Inclusive)", min_data_date, min_value=min_data_date, max_value=max_data_date)
    end_date = st.sidebar.date_input("End Date (Inclusive)", max_data_date, min_value=min_data_date, max_value=max_data_date)
else:
    if range_option == "Today":
        start_date = max_data_date
        end_date = max_data_date
    elif range_option == "Last 7 Days":
        start_date = max_data_date - timedelta(days=6)
        end_date = max_data_date
    elif range_option == "Last 30 Days":
        start_date = max_data_date - timedelta(days=29)
        end_date = max_data_date
    else: # All Time
        start_date = min_data_date
        end_date = max_data_date

# Filter DataFrame
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Chart Grouping")
granularity = st.sidebar.radio(
    "Group Charts By:",
    ["Daily", "Weekly", "Monthly"],
    index=0
)

group_col_map = {
    "Daily": "Date",
    "Weekly": "Week",
    "Monthly": "Month"
}
group_col = group_col_map[granularity]

# ==========================================
# 4. DYNAMIC QUICK SUMMARY (REACTS TO FILTER)
# ==========================================
st.markdown(f"### ⚡ Quick Summary (`{start_date.strftime('%b %d, %Y')}` to `{end_date.strftime('%b %d, %Y')}`)")

# 1. Total Formula
formula_df = filtered_df[filtered_df['Event Type'].str.contains("Formula", case=False, na=False)]
formula_tot = formula_df['Value (Optional)'].sum()

# 2. Total Breast Milk
bm_df = filtered_df[filtered_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]
bm_tot = bm_df['Value (Optional)'].sum()

# 3. Wet & Poop Counts
wet_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
poop_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Poop", case=False, na=False)])

# 4. Global Last Feed Calculation (Most recent feeding event in entire log)
all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_dt = all_feed_events.iloc[0]['DateTime']
    
    # Calculate time difference relative to current time or max dataset time
    now_ref = max(datetime.now(), df['DateTime'].max())
    time_diff = now_ref - last_feed_dt
    hrs_since = int(time_diff.total_seconds() // 3600)
    mins_since = int((time_diff.total_seconds() % 3600) // 60)
    
    last_feed_time_str = last_feed_dt.strftime('%b %d, %I:%M %p')
    if hrs_since > 24:
        last_feed_delta = f"{hrs_since // 24}d {hrs_since % 24}h ago"
    elif hrs_since > 0:
        last_feed_delta = f"{hrs_since}h {mins_since}m ago"
    else:
        last_feed_delta = f"{mins_since}m ago"
    last_feed_display = f"{last_feed_delta}"
    last_feed_sub = f"Recorded: {last_feed_time_str}"
else:
    last_feed_display = "N/A"
    last_feed_sub = "No feed events"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("🍼 Formula Intake", f"{int(formula_tot):,} mL")
kpi2.metric("🤱 Breast Milk", f"{int(bm_tot):,} mL")
kpi3.metric("💧 Wet / 💩 Poop", f"{wet_cnt} / {poop_cnt}")
kpi4.metric("⏰ Last Feeding", last_feed_display, delta=last_feed_sub, delta_color="normal")

st.markdown("---")

# Helper function for empty state UI
def render_empty_state(title="No Data Logged in this period", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""
        <div class="empty-data-card">
            <div class="empty-data-title">📋 {title}</div>
            <div class="empty-data-sub">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. CHARTS & VISUALIZATIONS
# ==========================================
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4 = st.tabs([
    "🍼 Milk Intake (Stacked)", 
    "🚽 Diaper Output", 
    "🧴 Pumping & Activities", 
    "📈 Event Timeline"
])

# Custom Color Palette
COLOR_MAP = {
    "Formula (mL)": "#3b82f6",
    "🍼 Formula (mL)": "#3b82f6",
    "Breast Milk (mL)": "#ec4899",
    "🤱 Breast Milk (mL)": "#ec4899",
    "Wet Diaper (Cnt)": "#0284c7",
    "💧 Wet Diaper (Cnt)": "#0284c7",
    "Poop (Cnt)": "#d97706",
    "💩 Poop (Cnt)": "#d97706",
    "Pumping (mL)": "#8b5cf6",
    "🧴 Pumping (mL)": "#8b5cf6",
    "Tummy Time (Mins)": "#10b981",
    "🛟 Tummy Time (Mins)": "#10b981",
    "Sleep (hrs)": "#6366f1",
    "🛌 Sleep (hrs)": "#6366f1",
    "Temp (°C)": "#ef4444",
    "🌡️ Temp (°C)": "#ef4444",
    "Meds (Cnt)": "#f59e0b",
    "💊 Meds (Cnt)": "#f59e0b"
}

# TAB 1: Milk Intake Stacked
with tab1:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
    if not milk_df.empty:
        # Standardize category labels for stacking
        milk_df['Category'] = milk_df['Event Type'].apply(
            lambda x: "Breast Milk (mL)" if "breast" in x.lower() else "Formula (mL)"
        )
        
        grouped_milk = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        
        fig_milk = px.bar(
            grouped_milk,
            x=group_col,
            y="Value (Optional)",
            color="Category",
            title=f"Total Milk Intake ({granularity}) - Stacked",
            barmode="stack",
            color_discrete_map={
                "Formula (mL)": "#3b82f6",
                "Breast Milk (mL)": "#ec4899"
            },
            labels={"Value (Optional)": "Volume (mL)", group_col: granularity}
        )
        fig_milk = style_plotly_figure(fig_milk, height=520)
        st.plotly_chart(fig_milk, use_container_width=True)
        st.caption(f"ℹ️ *This stacked chart shows the combined total volume of Formula and Breast Milk (mL) grouped **{granularity.lower()}** for the period from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Feeding Data Logged in this period")

# TAB 2: Diapers Output
with tab2:
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
    if not diaper_df.empty:
        diaper_df['Category'] = diaper_df['Event Type'].apply(
            lambda x: "Poop (Cnt)" if "poop" in x.lower() else "Wet Diaper (Cnt)"
        )
        grouped_diaper = diaper_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        
        fig_diaper = px.bar(
            grouped_diaper,
            x=group_col,
            y="Value (Optional)",
            color="Category",
            title=f"Diaper Changes Count ({granularity})",
            barmode="group",
            color_discrete_map={
                "Wet Diaper (Cnt)": "#0284c7",
                "Poop (Cnt)": "#d97706"
            },
            labels={"Value (Optional)": "Count", group_col: granularity}
        )
        fig_diaper = style_plotly_figure(fig_diaper, height=520)
        st.plotly_chart(fig_diaper, use_container_width=True)
        st.caption(f"ℹ️ *This chart compares total Wet Diapers and Poop counts grouped **{granularity.lower()}** for the period from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Diaper Data Logged in this period")

# TAB 3: Pumping & Activities
with tab3:
    act_df = filtered_df[filtered_df['Event Type'].str.contains("Pumping|Tummy|Sleep|Temp|Meds", case=False, na=False)]
    if not act_df.empty:
        grouped_act = act_df.groupby([group_col, 'Event Type'])['Value (Optional)'].sum().reset_index()
        fig_act = px.bar(
            grouped_act,
            x=group_col,
            y="Value (Optional)",
            color="Event Type",
            title=f"Activities & Pumping Summary ({granularity})",
            barmode="group",
            color_discrete_map=COLOR_MAP,
            labels={"Value (Optional)": "Total Value", group_col: granularity}
        )
        fig_act = style_plotly_figure(fig_act, height=520)
        st.plotly_chart(fig_act, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded pumping volumes, tummy time minutes, and sleep hours grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Activity Data Logged in this period")

# TAB 4: Timeline
with tab4:
    if not filtered_df.empty:
        fig_time = px.scatter(
            filtered_df,
            x="DateTime",
            y="Event Type",
            size="Value (Optional)",
            color="Event Type",
            title="Interactive Event Occurrence Timeline",
            color_discrete_map=COLOR_MAP,
            size_max=20
        )
        fig_time = style_plotly_figure(fig_time, height=550)
        fig_time.update_layout(showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True)
        st.caption(f"ℹ️ *Each dot represents a specific logged event along the timeline from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Events Logged in this period")

st.markdown("---")

# ==========================================
# 6. EXPANDED RAW DATA TABLE
# ==========================================
st.subheader("📋 Raw Data Logs")

# Search and Multi-Select Event Filter
filter_c1, filter_c2 = st.columns([2, 2])

with filter_c1:
    all_events_in_df = sorted(list(df['Event Type'].unique()))
    selected_events = st.multiselect(
        "Filter Event Types:",
        options=all_events_in_df,
        default=[],
        placeholder="Choose event types (Leave empty for All)"
    )

with filter_c2:
    search_query = st.text_input("🔍 Search notes or details:", "", placeholder="Type keywords...")

table_df = filtered_df.copy()

if selected_events:
    table_df = table_df[table_df['Event Type'].isin(selected_events)]

if search_query:
    table_df = table_df[
        table_df['Event Type'].str.contains(search_query, case=False, na=False) |
        table_df['Notes / Details (Optional)'].astype(str).str.contains(search_query, case=False, na=False)
    ]

# Format numeric values: round integers nicely while keeping temperature decimals
def format_value(val):
    if pd.isna(val):
        return ""
    if float(val).is_integer():
        return f"{int(val)}"
    return f"{float(val):.1f}"

if 'Value (Optional)' in table_df.columns:
    table_df['Value (Optional)'] = table_df['Value (Optional)'].apply(format_value)

# Format DateTime string
if 'DateTime' in table_df.columns:
    table_df['DateTime_Display'] = table_df['DateTime'].dt.strftime('%Y-%m-%d %I:%M %p')

# Reorder columns to include ALL available columns in the gsheet
desired_cols = [
    'EntryDateTime', 'DateTime_Display', 'Date', 'Week', 'Month', 
    'Event Type', 'Value (Optional)', 'Notes / Details (Optional)'
]
actual_cols = [c for c in desired_cols if c in table_df.columns or c == 'DateTime_Display']

# Rename DateTime_Display back for crisp display
display_df = table_df[actual_cols].copy()
if 'DateTime_Display' in display_df.columns:
    display_df = display_df.rename(columns={'DateTime_Display': 'DateTime'})

if not display_df.empty:
    st.dataframe(
        display_df,
        use_container_width=True,
        height=650,  # Displays 20+ rows easily without cramped scrolling
        column_config={
            "Notes / Details (Optional)": st.column_config.TextColumn(
                "Notes / Details (Optional)",
                width="large"
            ),
            "DateTime": st.column_config.TextColumn("DateTime", width="medium"),
            "Event Type": st.column_config.TextColumn("Event Type", width="medium"),
            "Value (Optional)": st.column_config.TextColumn("Value", width="small")
        }
    )
    st.caption(f"Showing **{len(display_df)}** entries recorded between **{start_date}** and **{end_date}**.")
else:
    render_empty_state("No Raw Data Rows Match Your Filter Selection")
