import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley Growth Log",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Responsive & Adaptive CSS for Light & Dark Theme Support
st.markdown("""
    <style>
    /* Table of Contents Navigation Buttons */
    .toc-button {
        display: block;
        width: 100%;
        padding: 8px 12px;
        margin: 4px 0;
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        color: inherit !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
    }
    .toc-button:hover {
        background-color: rgba(128, 128, 128, 0.18);
        border-color: rgba(128, 128, 128, 0.3);
        text-decoration: none !important;
    }

    /* Prevent title word cutting on mobile screen width */
    .app-main-title {
        font-size: clamp(1.4rem, 5vw, 2.2rem);
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 0.5rem;
    }

    .section-header-single-line {
        font-size: clamp(1.1rem, 4vw, 1.45rem);
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
    }

    /* Custom Color-Coded Highlight Cards */
    .highlight-card {
        background-color: rgba(128, 128, 128, 0.07);
        border-radius: 12px;
        padding: 12px 14px;
        min-height: 120px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .card-milk { border-left: 5px solid #2563eb; }
    .card-feed { border-left: 5px solid #a855f7; }
    .card-diaper { border-left: 5px solid #0284c7; }
    .card-pump { border-left: 5px solid #10b981; }
    .card-sleep { border-left: 5px solid #6366f1; }
    .card-meds { border-left: 5px solid #f59e0b; }
    .card-temp { border-left: 5px solid #ef4444; }
    .card-events { border-left: 5px solid #64748b; }

    .highlight-title {
        font-weight: 600;
        font-size: 0.92rem;
        margin-bottom: 4px;
        white-space: nowrap;
    }
    .highlight-body {
        font-size: 0.86rem;
        opacity: 0.88;
        line-height: 1.3;
    }
    .highlight-sub {
        font-size: 0.76rem;
        opacity: 0.65;
        margin-top: 4px;
    }

    /* Grey default range indicator text */
    .default-range-text {
        color: #888888;
        font-size: 0.82rem;
        font-style: italic;
        margin-top: 2px;
        display: inline-block;
    }

    /* Substantially reduced row count font size in Raw Data Log */
    .raw-log-count-text {
        font-size: 0.72rem;
        color: rgba(128, 128, 128, 0.85);
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Empty state notice */
    .empty-data-card {
        background-color: rgba(128, 128, 128, 0.06);
        border: 1.5px dashed rgba(128, 128, 128, 0.25);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 12px 0;
    }
    .empty-data-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .empty-data-sub {
        font-size: 0.82rem;
        opacity: 0.7;
    }

    /* Streamlit Padding Fixes */
    .stApp {
        padding-top: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Anchor
st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)
st.markdown('<div class="app-main-title">🍼 Riley Growth Log</div>', unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR TABLE OF CONTENTS & GSHEET SETTINGS
# ==========================================
st.sidebar.markdown("""
    <div style="margin-bottom: 12px;">
        <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">📌 Navigation</div>
        <a href="#top-header" class="toc-button">🏠 Header</a>
        <a href="#today-highlights" class="toc-button">✨ Today's Highlights</a>
        <a href="#period-highlights" class="toc-button">✨ Period Highlights</a>
        <a href="#analytics-charts" class="toc-button">📊 Analytics & Charts</a>
        <a href="#raw-logs" class="toc-button">📋 Raw Data Logs</a>
    </div>
    <hr style="margin: 12px 0; opacity: 0.2;">
""", unsafe_allow_html=True)

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"

st.sidebar.header("⚙️ Sheet Settings")

sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL",
    value=DEFAULT_SHEET_URL,
    help="Auto-synced to your master spreadsheet."
)

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

# Real-time auto sync fetcher (5-second cache handles auto-update on open/refresh)
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
        
        # Calculate Date, Week (Sunday start), Month
        df['Date'] = df['DateTime'].dt.date
        df['Week'] = df['DateTime'].dt.to_period('W-SUN').dt.start_time.dt.date
        df['Month'] = df['DateTime'].dt.strftime('%Y-%m')
        
        # Numeric Value parsing
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

# Master Emoji Normalization for all data rows (🚽 Poop updated)
def standardize_event_name(event_str):
    s = str(event_str).strip()
    mapping = {
        "Formula (mL)": "🍼 Formula (mL)",
        "Breast Milk (mL)": "🤱 Breast Milk (mL)",
        "Wet Diaper (Cnt)": "💧 Wet Diaper (Cnt)",
        "Poop (Cnt)": "🚽 Poop (Cnt)",
        "Pumping (mL)": "🧴 Pumping (mL)",
        "Tummy Time (Mins)": "🛟 Tummy Time (Mins)",
        "Sleep (hrs)": "🛌 Sleep (hrs)",
        "Temp (°C)": "🌡️ Temp (°C)",
        "Meds (Cnt)": "💊 Meds (Cnt)"
    }
    return mapping.get(s, s)

df['Event Type'] = df['Event Type'].apply(standardize_event_name)

ALL_EVENT_CATEGORIES = [
    "🍼 Formula (mL)",
    "🤱 Breast Milk (mL)",
    "💧 Wet Diaper (Cnt)",
    "🚽 Poop (Cnt)",
    "🧴 Pumping (mL)",
    "🛟 Tummy Time (Mins)",
    "🛌 Sleep (hrs)",
    "🌡️ Temp (°C)",
    "💊 Meds (Cnt)",
    "Other"
]

COLOR_MAP = {
    "🍼 Formula (mL)": "#2563eb",      # Royal Blue
    "🤱 Breast Milk (mL)": "#ec4899",  # Rosy Pink
    "💧 Wet Diaper (Cnt)": "#0284c7",   # Ocean Cyan
    "🚽 Poop (Cnt)": "#d97706",         # Warm Amber
    "🧴 Pumping (mL)": "#a855f7",       # Purple
    "🛟 Tummy Time (Mins)": "#10b981", # Emerald Green
    "🛌 Sleep (hrs)": "#6366f1",        # Indigo
    "🌡️ Temp (°C)": "#ef4444",         # Crimson
    "💊 Meds (Cnt)": "#f59e0b",         # Bright Amber
    "Other": "#6b7280"
}

# Compact Plotly Styling Helper
def style_plotly_figure(fig, title_text="", height=460):
    fig.update_layout(
        title=dict(
            text=title_text,
            y=0.97,
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=14, weight="bold")
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=85, b=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=10.5)
        ),
        font=dict(family="sans-serif", size=11),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10)),
        hovermode="x unified"
    )
    return fig

# ==========================================
# 3. EXPANDABLE FILTERS & GROUPING
# ==========================================
max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

with st.expander("⚙️ Filter & Grouping Settings (Click to expand)", expanded=False):
    f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
    
    with f_col1:
        granularity = st.radio(
            "Chart Grouping:",
            ["Daily", "Weekly", "Monthly", "All Time"],
            index=0,
            horizontal=True
        )
        range_hints = {
            "Daily": "Default: Last 28 Days",
            "Weekly": "Default: Last 8 Weeks",
            "Monthly": "Default: Last 6 Months",
            "All Time": "Default: Full Data Range"
        }
        st.markdown(f"<span class='default-range-text'>ℹ️ {range_hints[granularity]}</span>", unsafe_allow_html=True)
    
    if granularity == "Daily":
        default_start = max(min_data_date, max_data_date - timedelta(days=27))
    elif granularity == "Weekly":
        default_start = max(min_data_date, max_data_date - timedelta(weeks=8))
    elif granularity == "Monthly":
        default_start = max(min_data_date, max_data_date - timedelta(days=180))
    else: # All Time
        default_start = min_data_date

    with f_col2:
        start_date = st.date_input("Start Date (Inclusive)", default_start, min_value=min_data_date, max_value=max_data_date)
    with f_col3:
        end_date = st.date_input("End Date (Inclusive)", max_data_date, min_value=min_data_date, max_value=max_data_date)

group_col_map = {
    "Daily": "Date", 
    "Weekly": "Week", 
    "Monthly": "Month", 
    "All Time": "Month"
}
group_col = group_col_map[granularity]

# Filter main dataset by inclusive date bounds
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

# ==========================================
# 4. HIGHLIGHTS & SUMMARY CARDS
# ==========================================

# --- Smart Reference Time & Timezone Offset Calculation ---
server_now = datetime.now()
max_log_dt = df['DateTime'].max()
time_diff_server = (max_log_dt - server_now).total_seconds()

if time_diff_server > 0:
    offset_hours = round(time_diff_server / 3600.0)
    current_ref_time = server_now + timedelta(hours=offset_hours)
else:
    current_ref_time = server_now

# Calculate Last Feeding time elapsed dynamically
all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_dt = all_feed_events.iloc[0]['DateTime']
    
    if current_ref_time < last_feed_dt:
        current_ref_time = last_feed_dt

    time_diff = current_ref_time - last_feed_dt
    total_seconds = max(0, int(time_diff.total_seconds()))
    hrs_since = total_seconds // 3600
    mins_since = (total_seconds % 3600) // 60
    
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

# --- A. TODAY'S HIGHLIGHTS ---
st.markdown('<div id="today-highlights"></div>', unsafe_allow_html=True)

today_date = max(current_ref_time.date(), max_data_date)
today_df = df[df['Date'] == today_date]

formatted_today_code = today_date.strftime('%m.%d')
st.markdown(f'<div class="section-header-single-line">✨ Highlights [{formatted_today_code}]</div>', unsafe_allow_html=True)

t_formula = today_df[today_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
t_bm = today_df[today_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
t_milk = t_formula + t_bm
t_feed_cnt = len(today_df[today_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
t_avg_feed = (t_milk / t_feed_cnt) if t_feed_cnt > 0 else 0

t_wet = len(today_df[today_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
t_poop = len(today_df[today_df['Event Type'].str.contains("Poop", case=False, na=False)])

t_pumping = today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
t_tummy = today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()

t_sleep = today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
t_meds = len(today_df[today_df['Event Type'].str.contains("Meds", case=False, na=False)])

th_col1, th_col2, th_col3, th_col4 = st.columns(4)

with th_col1:
    st.markdown(f"""
        <div class="highlight-card card-milk">
            <div>
                <div class="highlight-title">🍼 Milk Intake</div>
                <div class="highlight-body">Total <b>{int(t_milk):,} mL</b> across <b>{t_feed_cnt}</b> feed(s).</div>
            </div>
            <div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Formula: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div>
        </div>
    """, unsafe_allow_html=True)

with th_col2:
    st.markdown(f"""
        <div class="highlight-card card-feed">
            <div>
                <div class="highlight-title">⏰ Last Feeding</div>
                <div class="highlight-body"><b>{last_feed_delta}</b></div>
            </div>
            <div class="highlight-sub">{last_feed_sub}</div>
        </div>
    """, unsafe_allow_html=True)

with th_col3:
    st.markdown(f"""
        <div class="highlight-card card-diaper">
            <div>
                <div class="highlight-title">🚽 Diaper Output</div>
                <div class="highlight-body">Total <b>{t_wet + t_poop}</b> change(s) logged.</div>
            </div>
            <div class="highlight-sub">💧 Wet: {t_wet} | 🚽 Poop: {t_poop}</div>
        </div>
    """, unsafe_allow_html=True)

with th_col4:
    p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    st.markdown(f"""
        <div class="highlight-card card-pump">
            <div>
                <div class="highlight-title">🧴 Pumping & Tummy Time</div>
                <div class="highlight-body">Pumped <b>{int(t_pumping):,} mL</b> | 🛟 <b>{int(t_tummy)} min(s)</b> tummy.</div>
            </div>
            <div class="highlight-sub">{p_cnt_today} pumping session(s)</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

th_row2_c1, th_row2_c2, th_row2_c3, th_row2_c4 = st.columns(4)

with th_row2_c1:
    sleep_cnt_today = len(today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)])
    st.markdown(f"""
        <div class="highlight-card card-sleep">
            <div>
                <div class="highlight-title">🛌 Rest & Sleep</div>
                <div class="highlight-body">Logged <b>{int(t_sleep)} hr(s)</b> rest.</div>
            </div>
            <div class="highlight-sub">{sleep_cnt_today} sleep period(s)</div>
        </div>
    """, unsafe_allow_html=True)

with th_row2_c2:
    st.markdown(f"""
        <div class="highlight-card card-meds">
            <div>
                <div class="highlight-title">💊 Medication</div>
                <div class="highlight-body">Logged <b>{t_meds}</b> dose(s).</div>
            </div>
            <div class="highlight-sub">Dose(s) tracked in log</div>
        </div>
    """, unsafe_allow_html=True)

t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None
t_temp_str = f"<b>{t_latest_temp:.1f} °C</b>" if t_latest_temp else "No readings"

with th_row2_c3:
    st.markdown(f"""
        <div class="highlight-card card-temp">
            <div>
                <div class="highlight-title">🌡️ Latest Body Temp</div>
                <div class="highlight-body">{t_temp_str}</div>
            </div>
            <div class="highlight-sub">{len(t_temp_df)} temperature reading(s)</div>
        </div>
    """, unsafe_allow_html=True)

with th_row2_c4:
    st.markdown(f"""
        <div class="highlight-card card-events">
            <div>
                <div class="highlight-title">📊 Total Events</div>
                <div class="highlight-body"><b>{len(today_df):,}</b> entry(s) logged.</div>
            </div>
            <div class="highlight-sub">Date: {today_date.strftime('%Y-%m-%d')}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# --- B. PERIOD HIGHLIGHTS (Collapsible Box with Bottom Margin Padding) ---
st.markdown('<div id="period-highlights"></div>', unsafe_allow_html=True)

start_code = start_date.strftime('%m.%d')
end_code = end_date.strftime('%m.%d')

with st.expander(f"✨ Range Highlights [{start_code} – {end_code}] (Click to expand)", expanded=False):
    p_formula = filtered_df[filtered_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
    p_bm = filtered_df[filtered_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
    p_milk = p_formula + p_bm
    p_feed_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
    p_avg_feed = (p_milk / p_feed_cnt) if p_feed_cnt > 0 else 0

    p_wet = len(filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
    p_poop = len(filtered_df[filtered_df['Event Type'].str.contains("Poop", case=False, na=False)])

    p_pumping = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
    p_tummy = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()

    p_sleep = filtered_df[filtered_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
    p_meds = len(filtered_df[filtered_df['Event Type'].str.contains("Meds", case=False, na=False)])

    pr1_c1, pr1_c2, pr1_c3, pr1_c4 = st.columns(4)
    with pr1_c1:
        st.markdown(f"""
            <div class="highlight-card card-milk">
                <div>
                    <div class="highlight-title">🍼 Milk Intake</div>
                    <div class="highlight-body">Total <b>{int(p_milk):,} mL</b> across <b>{p_feed_cnt}</b> feed(s).</div>
                </div>
                <div class="highlight-sub">Avg Feed: ~{int(p_avg_feed)} mL (Formula: {int(p_formula):,}mL, BM: {int(p_bm):,}mL)</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c2:
        st.markdown(f"""
            <div class="highlight-card card-diaper">
                <div>
                    <div class="highlight-title">🚽 Diaper Output</div>
                    <div class="highlight-body">Total <b>{p_wet + p_poop}</b> diaper change(s).</div>
                </div>
                <div class="highlight-sub">💧 Wet: {p_wet} | 🚽 Poop: {p_poop}</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c3:
        p_pump_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)])
        st.markdown(f"""
            <div class="highlight-card card-pump">
                <div>
                    <div class="highlight-title">🧴 Pumping & Tummy Time</div>
                    <div class="highlight-body">Pumped <b>{int(p_pumping):,} mL</b> | 🛟 <b>{int(p_tummy)} min(s)</b> tummy.</div>
                </div>
                <div class="highlight-sub">{p_pump_cnt} pumping session(s)</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c4:
        st.markdown(f"""
            <div class="highlight-card card-sleep">
                <div>
                    <div class="highlight-title">🛌 Sleep & Meds</div>
                    <div class="highlight-body">Rest: <b>{int(p_sleep)} hr(s)</b> | Meds: <b>{p_meds} dose(s)</b>.</div>
                </div>
                <div class="highlight-sub">Total {len(filtered_df):,} event(s) in selected range</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div style="margin-bottom: 12px;"></div>', unsafe_allow_html=True)

st.markdown("---")

def render_empty_state(title="No Data Logged in this period", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""
        <div class="empty-data-card">
            <div class="empty-data-title">📋 {title}</div>
            <div class="empty-data-sub">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. CHARTS & ANALYTICS
# ==========================================
st.markdown('<div id="analytics-charts"></div>', unsafe_allow_html=True)
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🍼 Milk Intake", 
    "🚽 Diapers", 
    "🧴 Pumping",
    "🛟 Tummy Time",
    "🩺 Health", 
    "⏰ Today",
    "📈 Timeline"
])

# TAB 1: Milk Intake
with tab1:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(
            lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)"
        )
        
        grouped_vol = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        grouped_count = milk_df.groupby(group_col).size().reset_index(name='Total Feeds Count')
        
        fig_milk = make_subplots(specs=[[{"secondary_y": True}]])
        
        df_f = grouped_vol[grouped_vol['Category'] == '🍼 Formula (mL)']
        if not df_f.empty:
            fig_milk.add_trace(
                go.Bar(
                    name='🍼 Formula (mL)',
                    x=df_f[group_col].astype(str),
                    y=df_f['Value (Optional)'],
                    marker_color="#2563eb"
                ),
                secondary_y=False
            )
            
        df_bm = grouped_vol[grouped_vol['Category'] == '🤱 Breast Milk (mL)']
        if not df_bm.empty:
            fig_milk.add_trace(
                go.Bar(
                    name='🤱 Breast Milk (mL)',
                    x=df_bm[group_col].astype(str),
                    y=df_bm['Value (Optional)'],
                    marker_color="#ec4899"
                ),
                secondary_y=False
            )
            
        fig_milk.add_trace(
            go.Scatter(
                name='🔢 Feed Count(s)',
                x=grouped_count[group_col].astype(str),
                y=grouped_count['Total Feeds Count'],
                mode='lines+markers+text',
                text=grouped_count['Total Feeds Count'],
                textposition="top center",
                textfont=dict(size=10.5),
                line=dict(color='#10b981', width=3, shape='spline', smoothing=1.3),
                marker=dict(size=9, symbol='circle', color='#10b981', line=dict(width=2, color='#ffffff'))
            ),
            secondary_y=True
        )

        fig_milk.update_layout(
            barmode='stack',
            title=dict(
                text=f"Milk Intake Volume & Feed Count — {granularity}",
                y=0.97,
                x=0.5,
                xanchor="center",
                yanchor="top",
                font=dict(size=14, weight="bold")
            ),
            height=510,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=8, r=8, t=85, b=25),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                title_text="",
                font=dict(size=10.5)
            ),
            font=dict(family="sans-serif", size=11),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10)),
            hovermode="x unified"
        )
        
        fig_milk.update_yaxes(
            title_text="Volume (mL)",
            secondary_y=False,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
            tickfont=dict(size=10),
            title_font=dict(size=11)
        )
        fig_milk.update_yaxes(
            title_text="Feeds",
            secondary_y=True,
            showgrid=False,
            tickfont=dict(size=10),
            title_font=dict(size=11)
        )
        
        st.plotly_chart(fig_milk, use_container_width=True)
        st.caption(f"ℹ️ *Combines stacked **Formula and Breast Milk volume (mL)** on the left axis with total **Feed Count(s)** (emerald line) on the right axis grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Feeding Data Logged in this period")

# TAB 2: Diaper Output
with tab2:
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)].copy()
    if not diaper_df.empty:
        diaper_df['Category'] = diaper_df['Event Type'].apply(
            lambda x: "🚽 Poop (Cnt)" if "poop" in x.lower() else "💧 Wet Diaper (Cnt)"
        )
        grouped_diaper = diaper_df.groupby([group_col, 'Category']).size().reset_index(name='Count')
        grouped_diaper[group_col] = grouped_diaper[group_col].astype(str)
        
        fig_diaper = px.bar(
            grouped_diaper,
            x=group_col,
            y="Count",
            color="Category",
            barmode="group",
            color_discrete_map=COLOR_MAP,
            labels={"Count": "Diaper Count(s)", group_col: granularity}
        )
        fig_diaper = style_plotly_figure(fig_diaper, title_text=f"Diaper Changes Count — {granularity}", height=460)
        st.plotly_chart(fig_diaper, use_container_width=True)
        st.caption(f"ℹ️ *Compares Wet Diapers and Poop counts grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Diaper Data Logged in this period")

# TAB 3: Dedicated Pumping Chart
with tab3:
    pump_df = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)].copy()
    if not pump_df.empty:
        grouped_pump = pump_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_pump[group_col] = grouped_pump[group_col].astype(str)
        
        fig_pump = px.bar(
            grouped_pump,
            x=group_col,
            y="Value (Optional)",
            color_discrete_sequence=[COLOR_MAP["🧴 Pumping (mL)"]],
            labels={"Value (Optional)": "Volume (mL)", group_col: granularity}
        )
        fig_pump = style_plotly_figure(fig_pump, title_text=f"Pumping Volume (mL) — {granularity}", height=460)
        st.plotly_chart(fig_pump, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded pumping volume (mL) grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Pumping Data Logged in this period")

# TAB 4: Dedicated Tummy Time Chart (Updated Title to "🛟 Tummy — {granularity}")
with tab4:
    tummy_df = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)].copy()
    if not tummy_df.empty:
        grouped_tummy = tummy_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_tummy[group_col] = grouped_tummy[group_col].astype(str)
        
        fig_tummy = px.bar(
            grouped_tummy,
            x=group_col,
            y="Value (Optional)",
            color_discrete_sequence=[COLOR_MAP["🛟 Tummy Time (Mins)"]],
            labels={"Value (Optional)": "Duration (Mins)", group_col: granularity}
        )
        fig_tummy = style_plotly_figure(fig_tummy, title_text=f"🛟 Tummy — {granularity}", height=460)
        st.plotly_chart(fig_tummy, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded tummy time duration (Mins) grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Tummy Time Data Logged in this period")

# TAB 5: Health Charts (Sleep, Temp, Meds using Date on X-Axis)
with tab5:
    act_option = st.radio(
        "Select Health Activity:",
        options=[
            "🛌 Sleep (hrs)",
            "🌡️ Temp (°C)",
            "💊 Meds (Cnt)"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    act_mapping = {
        "🛌 Sleep (hrs)": ("Sleep", "Duration (hrs)", COLOR_MAP["🛌 Sleep (hrs)"]),
        "🌡️ Temp (°C)": ("Temp", "Temperature (°C)", COLOR_MAP["🌡️ Temp (°C)"]),
        "💊 Meds (Cnt)": ("Meds", "Dose Count(s)", COLOR_MAP["💊 Meds (Cnt)"])
    }
    
    keyword, y_title, act_color = act_mapping[act_option]
    act_df = filtered_df[filtered_df['Event Type'].str.contains(keyword, case=False, na=False)].copy()
    
    if not act_df.empty:
        if keyword == "Temp":
            grouped_act = act_df.groupby(group_col)['Value (Optional)'].mean().reset_index()
            grouped_act[group_col] = grouped_act[group_col].astype(str)
            fig_act = px.line(
                grouped_act,
                x=group_col,
                y="Value (Optional)",
                markers=True,
                color_discrete_sequence=[act_color],
                labels={"Value (Optional)": y_title, group_col: granularity}
            )
            fig_act.update_traces(
                line=dict(width=3, shape='spline', smoothing=1.3),
                marker=dict(size=8, symbol='circle', line=dict(width=2, color='#ffffff'))
            )
        elif keyword == "Sleep":
            grouped_act = act_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
            grouped_act[group_col] = grouped_act[group_col].astype(str)
            fig_act = px.bar(
                grouped_act,
                x=group_col,
                y="Value (Optional)",
                color_discrete_sequence=[act_color],
                labels={"Value (Optional)": y_title, group_col: granularity}
            )
        else: # Meds count
            grouped_act = act_df.groupby(group_col).size().reset_index(name='Value (Optional)')
            grouped_act[group_col] = grouped_act[group_col].astype(str)
            fig_act = px.bar(
                grouped_act,
                x=group_col,
                y="Value (Optional)",
                color_discrete_sequence=[act_color],
                labels={"Value (Optional)": y_title, group_col: granularity}
            )
            
        fig_act = style_plotly_figure(fig_act, title_text=f"🩺 Health — {act_option} ({granularity})", height=460)
        st.plotly_chart(fig_act, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded **{act_option}** data grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state(f"No {act_option} Data Logged in this period")

# TAB 6: NEW "Today" 24-Hour Timeline Chart
with tab6:
    cutoff_24h = current_ref_time - timedelta(hours=24)
    today_24h_df = df[(df['DateTime'] >= cutoff_24h) & (df['DateTime'] <= current_ref_time)].copy()
    
    if not today_24h_df.empty:
        fig_today_timeline = px.scatter(
            today_24h_df,
            x="DateTime",
            y="Event Type",
            size="Value (Optional)",
            color="Event Type",
            color_discrete_map=COLOR_MAP,
            size_max=16
        )
        fig_today_timeline = style_plotly_figure(fig_today_timeline, title_text="⏰ Last 24 Hours Activity Timeline", height=480)
        fig_today_timeline.update_layout(showlegend=False)
        st.plotly_chart(fig_today_timeline, use_container_width=True)
        st.caption("ℹ️ *Interactive scatter timeline displaying all events logged within the last 24 hours using exact DateTime.*")
    else:
        render_empty_state("No Events Logged in the Last 24 Hours")

# TAB 7: Full Period Timeline
with tab7:
    if not filtered_df.empty:
        fig_time = px.scatter(
            filtered_df,
            x="DateTime",
            y="Event Type",
            size="Value (Optional)",
            color="Event Type",
            color_discrete_map=COLOR_MAP,
            size_max=16
        )
        fig_time = style_plotly_figure(fig_time, title_text=f"Interactive Event Timeline — {granularity}", height=480)
        fig_time.update_layout(showlegend=False)
        st.plotly_chart(fig_time, use_container_width=True)
        st.caption(f"ℹ️ *Individual event occurrence scatter plot from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Events Logged in this period")

st.markdown("---")

# ==========================================
# 6. EXPANDED RAW DATA LOGS TABLE
# ==========================================
st.markdown('<div id="raw-logs"></div>', unsafe_allow_html=True)
st.subheader("📋 Raw Data Logs")

filter_c1, filter_c2 = st.columns([1, 1])

with filter_c1:
    selected_events = st.multiselect(
        "🏷️ Filter Event Types:",
        options=ALL_EVENT_CATEGORIES,
        default=[],
        placeholder="Choose event types (Leave empty for All)"
    )

with filter_c2:
    search_query = st.text_input("🔍 Search All Columns:", "", placeholder="Type date (e.g. 07-21), Formula, notes...")

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

# Strictly sort raw data log in descending order by DateTime (latest first)
if 'DateTime' in table_df.columns:
    table_df = table_df.sort_values('DateTime', ascending=False)

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

if 'DateTime' in table_df.columns:
    table_df['DateTime_Display'] = table_df['DateTime'].dt.strftime('%Y-%m-%d %I:%M %p')

# REORDER COLUMNS: DateTime and Event Type ARE STRICTLY COLUMNS 1 AND 2
desired_cols = [
    'DateTime_Display', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)',
    'Date', 'Week', 'Month', 'EntryDateTime'
]
actual_cols = [c for c in desired_cols if c in table_df.columns or c == 'DateTime_Display']

display_df = table_df[actual_cols].copy()
if 'DateTime_Display' in display_df.columns:
    display_df = display_df.rename(columns={'DateTime_Display': 'DateTime'})

if not display_df.empty:
    st.dataframe(
        display_df,
        use_container_width=True,
        height=700,
        column_config={
            "DateTime": st.column_config.TextColumn("DateTime", width="medium"),
            "Event Type": st.column_config.TextColumn("Event Type", width="medium"),
            "Value (Optional)": st.column_config.TextColumn("Value", width="small"),
            "Notes / Details (Optional)": st.column_config.TextColumn(
                "Notes / Details (Optional)",
                width="large"
            )
        }
    )
    # Substantially reduced row count font size using custom HTML styling
    st.markdown(f'<div class="raw-log-count-text">Showing {len(display_df)} entry(s) matching your criteria sorted in descending order.</div>', unsafe_allow_html=True)
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")
