import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & ADAPTIVE STYLING
# ==========================================
st.set_page_config(
    page_title="Riley Growth Log",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Mobile & Dark/Light Mode Responsive CSS
st.markdown("""
    <style>
    /* Metric & Highlight Card Styling */
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.18);
        padding: 12px 14px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .stApp {
        padding-top: 0.5rem;
    }

    /* Highlight Card Style */
    .highlight-card {
        background-color: rgba(128, 128, 128, 0.06);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .highlight-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 2px;
    }
    .highlight-body {
        font-size: 0.88rem;
        opacity: 0.85;
    }

    /* Empty state notice */
    .empty-data-card {
        background-color: rgba(128, 128, 128, 0.06);
        border: 1.5px dashed rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
    }
    .empty-data-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .empty-data-sub {
        font-size: 0.85rem;
        opacity: 0.7;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍼 Riley Growth Log")

# ==========================================
# 2. GOOGLE SHEET CONNECTOR & SIDEBAR
# ==========================================
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"

st.sidebar.header("⚙️ Sheet Settings")

sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL",
    value=DEFAULT_SHEET_URL,
    help="Auto-synced to your master spreadsheet."
)

# Direct link button to open Google Sheet
if sheet_url_input:
    st.sidebar.link_button("🔗 Open Google Sheet Directly", sheet_url_input, use_container_width=True)

def get_csv_export_url(url_or_id):
    if not url_or_id:
        return None
    if "docs.google.com/spreadsheets" in url_or_id:
        try:
            sheet_id = url_or_id.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        except IndexError:
            return None
    return f"https://docs.google.com/spreadsheets/d/{url_or_id}/export?format=csv"

# Real-time data fetcher (5-second cache)
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
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            if date_cols:
                df['DateTime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
        df = df.dropna(subset=['DateTime'])
        
        # Calculate Date, Week, Month
        df['Date'] = df['DateTime'].dt.date
        df['Week'] = df['DateTime'].dt.to_period('W-SUN').dt.start_time.dt.date
        df['Month'] = df['DateTime'].dt.strftime('%Y-%m')
        
        # Numeric Value
        if 'Value (Optional)' in df.columns:
            df['Value (Optional)'] = pd.to_numeric(df['Value (Optional)'], errors='coerce').fillna(1.0)
        else:
            df['Value (Optional)'] = 1.0

        if 'Event Type' in df.columns:
            df['Event Type'] = df['Event Type'].astype(str).str.strip()
            
        return df.sort_values('DateTime', ascending=False)
    except Exception as e:
        st.error(f"Error fetching Google Sheet: {e}")
        return pd.DataFrame()

csv_url = get_csv_export_url(sheet_url_input)

if not csv_url:
    st.info("💡 Please provide a valid Google Sheet URL in the sidebar.")
    st.stop()

df = load_sheet_data(csv_url)

if df.empty:
    st.warning("⚠️ No data retrieved. Ensure Google Sheet sharing is set to 'Anyone with the link can view'.")
    st.stop()

# Helper for adaptive mobile-friendly Plotly styling
def style_plotly_figure(fig, height=480):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=45, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            title_text=""
        ),
        font=dict(family="sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickangle=-30 if len(fig.data)>0 else 0),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        hovermode="x unified"
    )
    return fig

# All known master event categories for pickers
ALL_EVENT_CATEGORIES = [
    "🍼 Formula (mL)",
    "🤱 Breast Milk (mL)",
    "💧 Wet Diaper (Cnt)",
    "💩 Poop (Cnt)",
    "🧴 Pumping (mL)",
    "🛟 Tummy Time (Mins)",
    "🛌 Sleep (hrs)",
    "🌡️ Temp (°C)",
    "💊 Meds (Cnt)",
    "Other"
]

# Standardize Event Names with Emojis if plain text exists in data
def standardize_event_name(event_str):
    s = str(event_str).strip()
    mapping = {
        "Formula (mL)": "🍼 Formula (mL)",
        "Breast Milk (mL)": "🤱 Breast Milk (mL)",
        "Wet Diaper (Cnt)": "💧 Wet Diaper (Cnt)",
        "Poop (Cnt)": "💩 Poop (Cnt)",
        "Pumping (mL)": "🧴 Pumping (mL)",
        "Tummy Time (Mins)": "🛟 Tummy Time (Mins)",
        "Sleep (hrs)": "🛌 Sleep (hrs)",
        "Temp (°C)": "🌡️ Temp (°C)",
        "Meds (Cnt)": "💊 Meds (Cnt)"
    }
    return mapping.get(s, s)

df['Event Type'] = df['Event Type'].apply(standardize_event_name)

# ==========================================
# 3. EXPANDABLE FILTERS & GROUPING (DEFAULT HIDDEN)
# ==========================================
max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

with st.expander("⚙️ Filter & Grouping Settings (Click to expand)", expanded=False):
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    
    with f_col1:
        granularity = st.radio(
            "Chart Grouping:",
            ["Daily", "Weekly", "Monthly"],
            index=0,
            horizontal=True
        )
    
    # Calculate default range based on selected granularity
    if granularity == "Daily":
        default_start = max(min_data_date, max_data_date - timedelta(days=27)) # 28 days
    elif granularity == "Weekly":
        default_start = max(min_data_date, max_data_date - timedelta(weeks=8)) # 8 weeks
    else: # Monthly
        default_start = max(min_data_date, max_data_date - timedelta(days=180)) # 6 months
        
    with f_col2:
        start_date = st.date_input("Start Date (Inclusive)", default_start, min_value=min_data_date, max_value=max_data_date)
    with f_col3:
        end_date = st.date_input("End Date (Inclusive)", max_data_date, min_value=min_data_date, max_value=max_data_date)

group_col_map = {"Daily": "Date", "Weekly": "Week", "Monthly": "Month"}
group_col = group_col_map[granularity]

# Filter Dataset
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

# Sync refresh button top header
top_col1, top_col2 = st.columns([3, 1])
with top_col2:
    if st.button("🔄 Sync Sheet Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 4. QUICK SUMMARY & DYNAMIC HIGHLIGHTS
# ==========================================
st.markdown(f"### ⚡ Quick Summary (`{start_date.strftime('%b %d')}` – `{end_date.strftime('%b %d, %Y')}`)")

# KPI metrics
formula_df = filtered_df[filtered_df['Event Type'].str.contains("Formula", case=False, na=False)]
formula_tot = formula_df['Value (Optional)'].sum()

bm_df = filtered_df[filtered_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]
bm_tot = bm_df['Value (Optional)'].sum()

wet_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
poop_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Poop", case=False, na=False)])

# Calculate Last Feeding
all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_dt = all_feed_events.iloc[0]['DateTime']
    now_ref = max(datetime.now(), df['DateTime'].max())
    time_diff = now_ref - last_feed_dt
    hrs_since = int(time_diff.total_seconds() // 3600)
    mins_since = int((time_diff.total_seconds() % 3600) // 60)
    
    last_feed_time_str = last_feed_dt.strftime('%b %d, %I:%M %p')
    if hrs_since >= 24:
        last_feed_delta = f"{hrs_since // 24}d {hrs_since % 24}h ago"
    elif hrs_since > 0:
        last_feed_delta = f"{hrs_since}h {mins_since}m ago"
    else:
        last_feed_delta = f"{mins_since}m ago"
    last_feed_sub = f"Recorded: {last_feed_time_str}"
else:
    last_feed_delta = "N/A"
    last_feed_sub = "No feed events"

k1, k2, k3, k4 = st.columns(4)
k1.metric("🍼 Formula Intake", f"{int(formula_tot):,} mL")
k2.metric("🤱 Breast Milk", f"{int(bm_tot):,} mL")
k3.metric("💧 Wet / 💩 Poop", f"{wet_cnt} / {poop_cnt}")
k4.metric("⏰ Last Feeding", last_feed_delta, delta=last_feed_sub, delta_color="normal")

# Dynamic Highlights Header
highlight_title_map = {
    "Daily": "✨ Today's Highlights",
    "Weekly": "✨ This Week's Highlights",
    "Monthly": "✨ This Month's Highlights"
}
st.markdown(f"#### {highlight_title_map[granularity]}")

# Generate Highlights Data
h1_col, h2_col, h3_col, h4_col = st.columns(4)

total_milk = formula_tot + bm_tot
total_feeds = len(formula_df) + len(bm_df)
avg_feed_size = (total_milk / total_feeds) if total_feeds > 0 else 0

pumping_df = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)]
pumping_tot = pumping_df['Value (Optional)'].sum()

tummy_df = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]
tummy_tot = tummy_df['Value (Optional)'].sum()

with h1_col:
    st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-title">🍼 Milk Summary</div>
            <div class="highlight-body"><b>{int(total_milk):,} mL</b> total across <b>{total_feeds}</b> feeds (Avg: ~{int(avg_feed_size)} mL / feed).</div>
        </div>
    """, unsafe_allow_html=True)

with h2_col:
    st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-title">🚽 Diaper Output</div>
            <div class="highlight-body">Total <b>{wet_cnt + poop_cnt}</b> changes ({wet_cnt} wet, {poop_cnt} poop).</div>
        </div>
    """, unsafe_allow_html=True)

with h3_col:
    st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-title">🧴 Pumping Expressed</div>
            <div class="highlight-body">Pumped <b>{int(pumping_tot):,} mL</b> across {len(pumping_df)} pumping sessions.</div>
        </div>
    """, unsafe_allow_html=True)

with h4_col:
    st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-title">🛟 Active Tummy Time</div>
            <div class="highlight-body">Logged <b>{int(tummy_tot)} mins</b> of development exercise.</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Empty State Renderer Helper
def render_empty_state(title="No Data Logged in this period", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""
        <div class="empty-data-card">
            <div class="empty-data-title">📋 {title}</div>
            <div class="empty-data-sub">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

# Color Map
COLOR_MAP = {
    "🍼 Formula (mL)": "#3b82f6",
    "🤱 Breast Milk (mL)": "#ec4899",
    "💧 Wet Diaper (Cnt)": "#0284c7",
    "💩 Poop (Cnt)": "#d97706",
    "🧴 Pumping (mL)": "#8b5cf6",
    "🛟 Tummy Time (Mins)": "#10b981",
    "🛌 Sleep (hrs)": "#6366f1",
    "🌡️ Temp (°C)": "#ef4444",
    "💊 Meds (Cnt)": "#f59e0b",
    "Other": "#6b7280"
}

# ==========================================
# 5. VISUALIZATIONS & CHARTS
# ==========================================
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4 = st.tabs([
    "🍼 Milk Intake", 
    "🚽 Diaper Output", 
    "🧴 Pumping & Activities", 
    "📈 Event Timeline"
])

# TAB 1: Milk Intake
with tab1:
    milk_metric = st.radio(
        "Display Milk By:",
        ["Volume (mL)", "Feeding Count (Events)"],
        horizontal=True,
        key="milk_metric_toggle"
    )
    
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(
            lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)"
        )
        
        if milk_metric == "Volume (mL)":
            grouped_milk = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
            y_col = "Value (Optional)"
            y_label = "Volume (mL)"
        else:
            grouped_milk = milk_df.groupby([group_col, 'Category']).size().reset_index(name='Count')
            y_col = "Count"
            y_label = "Number of Feeds"

        fig_milk = px.bar(
            grouped_milk,
            x=group_col,
            y=y_col,
            color="Category",
            title=f"Total Milk Intake ({granularity}) - Stacked",
            barmode="stack",
            color_discrete_map=COLOR_MAP,
            labels={y_col: y_label, group_col: granularity}
        )
        fig_milk = style_plotly_figure(fig_milk, height=500)
        st.plotly_chart(fig_milk, use_container_width=True)
        st.caption(f"ℹ️ *Displays combined Formula and Breast Milk **{y_label.lower()}** stacked grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Feeding Data Logged in this period")

# TAB 2: Diaper Output
with tab2:
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)].copy()
    if not diaper_df.empty:
        diaper_df['Category'] = diaper_df['Event Type'].apply(
            lambda x: "💩 Poop (Cnt)" if "poop" in x.lower() else "💧 Wet Diaper (Cnt)"
        )
        grouped_diaper = diaper_df.groupby([group_col, 'Category']).size().reset_index(name='Count')
        
        fig_diaper = px.bar(
            grouped_diaper,
            x=group_col,
            y="Count",
            color="Category",
            title=f"Diaper Changes Count ({granularity})",
            barmode="group",
            color_discrete_map=COLOR_MAP,
            labels={"Count": "Diaper Count", group_col: granularity}
        )
        fig_diaper = style_plotly_figure(fig_diaper, height=500)
        st.plotly_chart(fig_diaper, use_container_width=True)
        st.caption(f"ℹ️ *Compares Wet Diapers and Poop counts grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Diaper Data Logged in this period")

# TAB 3: Pumping & Activities
with tab3:
    act_choices = st.multiselect(
        "Select Event Types to Graph:",
        options=ALL_EVENT_CATEGORIES,
        default=["🧴 Pumping (mL)", "🛟 Tummy Time (Mins)", "🛌 Sleep (hrs)", "💊 Meds (Cnt)", "🌡️ Temp (°C)"],
        key="act_multiselect"
    )
    
    if act_choices:
        act_df = filtered_df[filtered_df['Event Type'].isin(act_choices)].copy()
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
            fig_act = style_plotly_figure(fig_act, height=500)
            st.plotly_chart(fig_act, use_container_width=True)
            st.caption(f"ℹ️ *Shows recorded activity metrics grouped **{granularity.lower()}** for the period **{start_date}** to **{end_date}**.*")
        else:
            render_empty_state("No Data Logged for Selected Activity Types in this Period")
    else:
        render_empty_state("Select at least one activity type above to display graph")

# TAB 4: Timeline
with tab4:
    if not filtered_df.empty:
        fig_time = px.scatter(
            filtered_df,
            x="DateTime",
            y="Event Type",
            size="Value (Optional)",
            color="Event Type",
            title="Interactive Event Timeline",
            color_discrete_map=COLOR_MAP,
            size_max=18
        )
        fig_time = style_plotly_figure(fig_time, height=520)
        fig_time.update_layout(showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True)
        st.caption(f"ℹ️ *Individual event markers logged across the timeline from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Events Logged in this period")

st.markdown("---")

# ==========================================
# 6. EXPANDED RAW DATA LOGS TABLE
# ==========================================
st.subheader("📋 Raw Data Logs")

filter_c1, filter_c2 = st.columns([2, 2])

with filter_c1:
    selected_events = st.multiselect(
        "Filter Event Types:",
        options=ALL_EVENT_CATEGORIES,
        default=[],
        placeholder="Choose event types (Leave empty for All)"
    )

with filter_c2:
    search_query = st.text_input("🔍 Search All Columns:", "", placeholder="Search date (e.g. 07-21), formula, notes...")

table_df = filtered_df.copy()

# Event Type multiselect filter
if selected_events:
    table_df = table_df[table_df['Event Type'].isin(selected_events)]

# Global Search across ALL columns
if search_query:
    search_mask = table_df.astype(str).apply(
        lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1
    )
    table_df = table_df[search_mask]

# Format numeric values: round integers, keep temperature decimals
def format_value(val):
    if pd.isna(val):
        return ""
    try:
        f_val = float(val)
        if f_val.is_integer():
            return f"{int(f_val)}"
        return f"{f_val:.1f}"
    except ValueError:
        return str(val)

if 'Value (Optional)' in table_df.columns:
    table_df['Value (Optional)'] = table_df['Value (Optional)'].apply(format_value)

# Format DateTime display string
if 'DateTime' in table_df.columns:
    table_df['DateTime_Display'] = table_df['DateTime'].dt.strftime('%Y-%m-%d %I:%M %p')

desired_cols = [
    'EntryDateTime', 'DateTime_Display', 'Date', 'Week', 'Month', 
    'Event Type', 'Value (Optional)', 'Notes / Details (Optional)'
]
actual_cols = [c for c in desired_cols if c in table_df.columns or c == 'DateTime_Display']

display_df = table_df[actual_cols].copy()
if 'DateTime_Display' in display_df.columns:
    display_df = display_df.rename(columns={'DateTime_Display': 'DateTime'})

if not display_df.empty:
    st.dataframe(
        display_df,
        use_container_width=True,
        height=700, # Large vertical size displaying 20+ rows easily
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
    st.caption(f"Showing **{len(display_df)}** entries matching your filters.")
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")
