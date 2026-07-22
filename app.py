import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley's Growth Tracker",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Apple Touch Icon
components.html(
    """
    <script>
    (function() {
        const iconUrl = "https://em-content.zobj.net/source/apple/391/baby-bottle_1f37c.png";
        function applyAppleIcon(doc) {
            if (!doc || !doc.head) return;
            const rels = ['apple-touch-icon', 'apple-touch-icon-precomposed', 'icon', 'shortcut icon'];
            rels.forEach(function(rel) {
                let link = doc.querySelector("link[rel='" + rel + "']");
                if (!link) {
                    link = doc.createElement('link');
                    link.rel = rel;
                    doc.head.appendChild(link);
                }
                link.href = iconUrl;
            });
        }
        try { applyAppleIcon(document); } catch(e) {}
        try { applyAppleIcon(window.parent.document); } catch(e) {}
        try { applyAppleIcon(window.top.document); } catch(e) {}
    })();
    </script>
    """,
    height=0,
    width=0
)

# Responsive & Adaptive CSS
st.markdown("""
    <style>
    /* Hide Streamlit Default Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Smooth Scroll & Anchor Offsets */
    html { scroll-behavior: smooth; }
    [id] { scroll-margin-top: 70px; }

    /* ULTIMATE iOS TAP-TO-TOP SCROLL FIX: Shatters Streamlit's internal scroll boxes so Safari takes over naturally */
    html, body, #root {
        height: auto !important;
        min-height: 100vh !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        background-color: #f8fafc !important; 
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        height: auto !important;
        min-height: 0 !important;
        overflow: visible !important;
        position: static !important;
        background-color: #f8fafc !important; 
    }
    [data-testid="stHeader"] { background-color: #f8fafc !important; }

    /* Safari scrolling clearance */
    [data-testid="stMainBlockContainer"] {
        padding-top: calc(2.5rem + env(safe-area-inset-top)) !important;
        padding-bottom: calc(8rem + env(safe-area-inset-bottom)) !important;
    }

    /* Compact Vertical Spacing */
    div[data-testid="stVerticalBlock"] { gap: 0.35rem !important; }
    div[data-testid="stExpander"] { margin-bottom: 0.15rem !important; border-radius: 10px !important; }

    /* Locked Light Mode Theme Variables */
    :root {
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        --card-text: #1e293b;
    }
    body, .stApp { color: var(--card-text) !important; }

    /* Custom Mobile Header Layout: Forces Streamlit columns to 50/50 strictly on Mobile */
    @media (max-width: 768px) {
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
            width: 100% !important;
            flex: 1 1 100% !important;
            margin-bottom: 0.2rem;
        }
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="stHorizontalBlock"] > div:nth-child(2),
        div[data-testid="stVerticalBlock"] > div:first-child div[data-testid="stHorizontalBlock"] > div:nth-child(3) {
            width: calc(50% - 0.25rem) !important;
            min-width: calc(50% - 0.25rem) !important;
            flex: 0 0 calc(50% - 0.25rem) !important;
        }
    }

    /* Shrink the native Add/Refresh Streamlit buttons */
    div[data-testid="stVerticalBlock"] > div:first-child [data-testid="baseButton-secondary"] {
        min-height: 2.1rem !important;
        height: 2.1rem !important;
        padding: 0 0.5rem !important;
        border-radius: 8px !important;
    }

    /* Title Styling */
    .app-main-title {
        font-size: calc(1.3rem + 0.6vw) !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--card-text);
        margin: 0;
    }
    .section-header-single-line {
        font-size: clamp(1.05rem, 3.8vw, 1.35rem);
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
        color: var(--card-text);
    }

    /* Style Multiselect Tag Chips to Light Grey */
    span[data-baseweb="tag"] {
        background-color: #e5e7eb !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        font-weight: 500 !important;
    }

    /* Table of Contents Navigation Buttons */
    .toc-button {
        display: block;
        width: 100%;
        padding: 8px 12px;
        margin: 3px 0;
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        box-shadow: var(--card-shadow);
        color: var(--card-text) !important;
        text-decoration: none !important;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
    }
    .toc-button:hover { background-color: #f1f5f9; border-color: #cbd5e1; text-decoration: none !important; }

    /* CSS Grid Container: 12-Column System */
    .cards-container {
        display: grid !important;
        grid-template-columns: repeat(12, 1fr) !important;
        gap: 8px !important;
        align-items: stretch !important;
        margin-bottom: 2px !important;
        width: 100% !important;
    }
    .card-span-3 { grid-column: span 3 !important; }
    .card-span-4 { grid-column: span 4 !important; }
    .card-span-6 { grid-column: span 6 !important; }
    .card-span-12 { grid-column: span 12 !important; }

    @media (max-width: 1024px) {
        .card-span-3, .card-span-4 { grid-column: span 6 !important; }
        .mobile-full-width { grid-column: span 12 !important; }
    }

    /* Highlight Card Component with Flexbox Layout */
    .highlight-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 10px 12px;
        min-height: 118px;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-shadow: var(--card-shadow);
        border: 1px solid var(--card-border);
        box-sizing: border-box;
        word-wrap: break-word;
        overflow-wrap: break-word;
        color: var(--card-text) !important;
    }
    
    .card-milk { border-left: 5px solid #38bdf8; }
    .card-feed { border-left: 5px solid #c084fc; }
    .card-diaper { border-left: 5px solid #0284c7; }
    .card-pump { border-left: 5px solid #a855f7; }
    .card-tummy { border-left: 5px solid #10b981; }
    .card-sleep { border-left: 5px solid #818cf8; }
    .card-meds { border-left: 5px solid #fbbf24; }
    .card-temp { border-left: 5px solid #f87171; }
    .card-events { border-left: 5px solid #94a3b8; }

    .highlight-title { font-weight: 600; font-size: 0.88rem; margin-bottom: 3px; line-height: 1.2; }
    .highlight-body { font-size: 0.84rem; opacity: 0.92; line-height: 1.25; }
    .highlight-sub { font-size: 0.74rem; opacity: 0.75; margin-top: 3px; line-height: 1.25; }

    .default-range-text { color: #64748b; font-size: 0.8rem; font-style: italic; margin-top: 1px; display: inline-block; }
    .raw-log-count-text { font-size: 0.72rem; color: #64748b; margin-top: 3px; margin-bottom: 6px; }

    .empty-data-card {
        background-color: var(--card-bg);
        border: 1.5px dashed var(--card-border);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 6px 0;
    }
    .empty-data-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 3px; }
    .empty-data-sub { font-size: 0.8rem; opacity: 0.75; }

    /* Force disable chart interaction on mobile for smooth scrolling */
    @media (max-width: 768px) {
        div[data-testid="stPlotlyChart"] { position: relative !important; }
        div[data-testid="stPlotlyChart"] iframe { pointer-events: none !important; }
        div[data-testid="stPlotlyChart"]::after {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 50; /* Kept low so drop downs pop over it */
            background: rgba(0,0,0,0);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Anchor
st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# RESPONSIVE HEADER SECTION (NATIVE STREAMLIT)
# ---------------------------------------------------------
h_col1, h_col2, h_col3 = st.columns([0.65, 0.175, 0.175], vertical_alignment="center")

with h_col1:
    st.markdown('<div class="app-main-title">🍼 Riley\'s Growth Tracker</div>', unsafe_allow_html=True)

with h_col2:
    st.link_button("➕ Add", "shortcuts://run-shortcut?name=Riley%20Tracker", use_container_width=True)

with h_col3:
    # Native python refresh ensures the system instantly dumps cache and rebuilds cleanly
    if st.button("🔄 Refresh", key="native_refresh_btn", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('<hr style="margin: 0.35rem 0 0.6rem 0; border: none; border-top: 1px solid rgba(128,128,128,0.25);">', unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR TABLE OF CONTENTS & SETTINGS
# ==========================================
st.sidebar.markdown("""
    <div style="margin-bottom: 10px;">
        <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 6px;">📌 Navigation</div>
        <a href="#today-highlights" class="toc-button">✨ Today's Highlights</a>
        <a href="#period-highlights" class="toc-button">✨ Period Highlights</a>
        <a href="#raw-logs" class="toc-button">📋 Raw Data Logs</a>
        <a href="#analytics-charts" class="toc-button">📊 Analytics & Charts</a>
    </div>
    <hr style="margin: 10px 0; opacity: 0.2;">
""", unsafe_allow_html=True)

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"
st.sidebar.header("⚙️ Sheet Settings")
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL, help="Auto-synced to your master spreadsheet.")

tz_offset = st.sidebar.number_input("Timezone Offset (UTC Hours)", value=8, step=1)

st.sidebar.markdown('<hr style="margin: 10px 0; opacity: 0.2;">', unsafe_allow_html=True)
st.sidebar.header("👶 Profile (For WHO Charts)")
# These power the mathematical calculation of age in months and chart percentiles
birth_date = st.sidebar.date_input("Baby's Birth Date", value=datetime(2024, 1, 1))
gender = st.sidebar.radio("Gender", ["Boy", "Girl"], horizontal=True)

if sheet_url_input:
    st.sidebar.link_button("🔗 Open Google Sheet Directly", sheet_url_input, use_container_width=True)

def get_csv_export_url(url_or_id):
    if not url_or_id: return None
    if "docs.google.com/spreadsheets" in url_or_id:
        try: return f"https://docs.google.com/spreadsheets/d/{url_or_id.split('/d/')[1].split('/')[0]}/export?format=csv"
        except IndexError: return None
    return f"https://docs.google.com/spreadsheets/d/{url_or_id}/export?format=csv"

@st.cache_data(ttl=5)
def load_sheet_data(csv_url):
    try:
        df = pd.read_csv(csv_url)
        df.columns = df.columns.astype(str).str.strip()
        
        if 'DateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        elif 'EntryDateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['EntryDateTime'], errors='coerce')
        else:
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            if date_cols: df['DateTime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
        df = df.dropna(subset=['DateTime'])
        df['Date'] = df['DateTime'].dt.date
        df['Week'] = df['DateTime'].dt.to_period('W-SUN').dt.start_time.dt.date
        df['Month'] = df['DateTime'].dt.strftime('%Y-%m')
        
        if 'Value (Optional)' in df.columns: df['Value (Optional)'] = pd.to_numeric(df['Value (Optional)'], errors='coerce').fillna(1.0)
        else: df['Value (Optional)'] = 1.0

        if 'Event Type' in df.columns: df['Event Type'] = df['Event Type'].astype(str).str.strip()
            
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

# Master Emoji Normalization
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
        "Meds (Cnt)": "💊 Meds (Cnt)",
        "Weight (kg)": "⚖️ Weight (kg)",
        "Height (cm)": "🏔️ Height (cm)",
        "Head Size (cm)": "🐷 Head Size (cm)",
        "Vaccine": "💉 Vaccine (Cnt)",
        "Vaccine (Cnt)": "💉 Vaccine (Cnt)"
    }
    return mapping.get(s, s)

df['Event Type'] = df['Event Type'].apply(standardize_event_name)

ALL_EVENT_CATEGORIES = [
    "🍼 Formula (mL)", "🤱 Breast Milk (mL)", "💧 Wet Diaper (Cnt)", "🚽 Poop (Cnt)",
    "🧴 Pumping (mL)", "🛟 Tummy Time (Mins)", "🛌 Sleep (hrs)", "🌡️ Temp (°C)",
    "💊 Meds (Cnt)", "⚖️ Weight (kg)", "🏔️ Height (cm)", "🐷 Head Size (cm)", "💉 Vaccine (Cnt)", "Other"
]

COLOR_MAP = {
    "🍼 Formula (mL)": "#38bdf8", "🤱 Breast Milk (mL)": "#9ca3af", "💧 Wet Diaper (Cnt)": "#0284c7",
    "🚽 Poop (Cnt)": "#d97706", "🧴 Pumping (mL)": "#a855f7", "🛟 Tummy Time (Mins)": "#10b981",
    "🛌 Sleep (hrs)": "#6366f1", "🌡️ Temp (°C)": "#ef4444", "💊 Meds (Cnt)": "#f59e0b",
    "⚖️ Weight (kg)": "#14b8a6", "🏔️ Height (cm)": "#0ea5e9", "🐷 Head Size (cm)": "#f472b6", 
    "💉 Vaccine (Cnt)": "#f43f5e", "Other": "#6b7280"
}

def format_x_label(val):
    try: return pd.to_datetime(val).strftime('%m.%d')
    except Exception: return str(val)

def style_plotly_figure(fig, title_text="", height=460, single_point=False, is_scatter=False, x_tickformat=None, x_dtick=None, y_tickangle=None):
    layout_args = dict(
        title=dict(text=title_text, y=0.97, x=0.5, xanchor="center", yanchor="top", font=dict(size=16, weight="normal")),
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=2, r=2, t=75, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text="", font=dict(size=10)),
        font=dict(family="sans-serif", size=11),
        xaxis=dict(type=None if is_scatter else "category", tickformat=x_tickformat, dtick=x_dtick, title=dict(text=""), showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=9.5), automargin=True),
        yaxis=dict(title=dict(text=""), showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=9.5), tickangle=y_tickangle if y_tickangle is not None else 0, title_standoff=2, automargin=True),
        hovermode="closest"
    )
    if single_point: layout_args["bargap"] = 0.75
    fig.update_layout(**layout_args)
    return fig

def prepare_normalized_timeline_df(input_df):
    if input_df.empty: return input_df
    res_df = input_df.copy()
    res_df['Value_Clean'] = pd.to_numeric(res_df['Value (Optional)'], errors='coerce').fillna(1.0)
    groups = []
    for _, group in res_df.groupby('Event Type'):
        g = group.copy()
        vals = g['Value_Clean'].values
        min_v, max_v = np.nanmin(vals), np.nanmax(vals)
        if max_v == min_v or np.isnan(max_v) or np.isnan(min_v): g['CategoryBubbleSize'] = 10.0
        else: g['CategoryBubbleSize'] = 8.0 + (vals - min_v) / (max_v - min_v) * 6.0
        groups.append(g)
    if groups: res_df = pd.concat(groups, axis=0)
    else: res_df['CategoryBubbleSize'] = 10.0
    res_df['CategoryBubbleSize'] = res_df['CategoryBubbleSize'].fillna(10.0)
    return res_df

# ==========================================
# 3. EXPANDABLE FILTERS & GROUPING
# ==========================================
max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

min_str = min_data_date.strftime('%m.%d')
max_str = max_data_date.strftime('%m.%d')

with st.expander("⚙️ Filter & Grouping Settings", expanded=False):
    f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
    
    with f_col1:
        granularity = st.radio("Chart Grouping:", ["Daily", "Weekly", "Monthly", "All Time"], index=0, horizontal=True)
        range_hints = {"Daily": "Default: Last 28 Days", "Weekly": "Default: Last 8 Weeks", "Monthly": "Default: Last 6 Months", "All Time": "Default: Full Data Range"}
        st.markdown(f"<span class='default-range-text'>ℹ️ {range_hints[granularity]}</span>", unsafe_allow_html=True)
    
    if granularity == "Daily": default_start = max(min_data_date, max_data_date - timedelta(days=27))
    elif granularity == "Weekly": default_start = max(min_data_date, max_data_date - timedelta(weeks=8))
    elif granularity == "Monthly": default_start = max(min_data_date, max_data_date - timedelta(days=180))
    else: default_start = min_data_date

    with f_col2:
        start_date = st.date_input("Start Date (Inclusive)", default_start, min_value=min_data_date, max_value=max_data_date)
        st.markdown(f"<span class='default-range-text'>Min Date: {min_str}</span>", unsafe_allow_html=True)
    with f_col3:
        end_date = st.date_input("End Date (Inclusive)", max_data_date, min_value=min_data_date, max_value=max_data_date)
        st.markdown(f"<span class='default-range-text'>Max Date: {max_str}</span>", unsafe_allow_html=True)

group_col_map = {"Daily": "Date", "Weekly": "Week", "Monthly": "Month", "All Time": "Month"}
group_col = group_col_map[granularity]

filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

# ==========================================
# 4. HIGHLIGHTS & SUMMARY CARDS
# ==========================================
utc_now = datetime.utcnow()
current_local_time = utc_now + timedelta(hours=tz_offset)

all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_row = all_feed_events.iloc[0]
    last_feed_dt = last_feed_row['DateTime']
    total_seconds = max(0, int((current_local_time - last_feed_dt).total_seconds()))
    hrs_since = total_seconds // 3600
    mins_since = (total_seconds % 3600) // 60
    
    last_feed_time_str = last_feed_dt.strftime('%b %d, %H:%M')
    if hrs_since >= 24: last_feed_delta = f"{hrs_since // 24}d {hrs_since % 24}h ago"
    elif hrs_since > 0: last_feed_delta = f"{hrs_since}h {mins_since}m ago"
    else: last_feed_delta = f"{mins_since}m ago"
    
    last_f_df = df[df['Event Type'].str.contains("Formula", case=False, na=False)]
    last_bm_df = df[df['Event Type'].str.contains("Breast Milk", case=False, na=False)]
    f_str = f"{int(last_f_df.iloc[0]['Value (Optional)'])} mL" if not last_f_df.empty else "-"
    bm_str = f"{int(last_bm_df.iloc[0]['Value (Optional)'])} mL" if not last_bm_df.empty else "-"
    last_feed_sub = f"Recorded: {last_feed_time_str}<br>🍼 Form: {f_str} | 🤱 BM: {bm_str}"
else:
    last_feed_delta, last_feed_sub = "N/A", "No feed events"

# --- A. TODAY'S HIGHLIGHTS ---
st.markdown('<div id="today-highlights"></div>', unsafe_allow_html=True)
today_date = max(current_local_time.date(), max_data_date)
today_df = df[df['Date'] == today_date]

with st.expander(f"✨ Today [{today_date.strftime('%m.%d')}]", expanded=True):
    t_formula = today_df[today_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
    t_bm = today_df[today_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
    t_milk, t_feed_cnt = t_formula + t_bm, len(today_df[today_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
    t_avg_feed = (t_milk / t_feed_cnt) if t_feed_cnt > 0 else 0
    t_wet = len(today_df[today_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
    t_poop = len(today_df[today_df['Event Type'].str.contains("Poop", case=False, na=False)])
    t_pumping = today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
    t_tummy = today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()
    t_sleep = today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
    t_meds = len(today_df[today_df['Event Type'].str.contains("Meds", case=False, na=False)])
    t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
    t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None

    today_cards = []
    today_cards.append(f"""<div class="highlight-card card-feed"><div><div class="highlight-title">⏰ Last Feeding</div><div class="highlight-body"><b>{last_feed_delta}</b></div></div><div class="highlight-sub">{last_feed_sub}</div></div>""")
    if t_milk > 0 or t_feed_cnt > 0: today_cards.append(f"""<div class="highlight-card card-milk"><div><div class="highlight-title">🍼 Milk Intake</div><div class="highlight-body">Total <b>{int(t_milk):,} mL</b> across <b>{t_feed_cnt}</b> feed(s).</div></div><div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Form: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div></div>""")
    if t_wet + t_poop > 0: today_cards.append(f"""<div class="highlight-card card-diaper"><div><div class="highlight-title">🚽 Diaper Output</div><div class="highlight-body">Total <b>{t_wet + t_poop}</b> change(s) logged.</div></div><div class="highlight-sub">💧 Wet: {t_wet} | 🚽 Poop: {t_poop}</div></div>""")
    p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    if t_pumping > 0 or p_cnt_today > 0: today_cards.append(f"""<div class="highlight-card card-pump"><div><div class="highlight-title">🧴 Pumping</div><div class="highlight-body">Pumped <b>{int(t_pumping):,} mL</b> total today.</div></div><div class="highlight-sub">{p_cnt_today} pumping session(s)</div></div>""")
    tummy_cnt_today = len(today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])
    if t_tummy > 0 or tummy_cnt_today > 0: today_cards.append(f"""<div class="highlight-card card-tummy"><div><div class="highlight-title">🛟 Tummy Time</div><div class="highlight-body">Logged <b>{int(t_tummy)} min(s)</b> today.</div></div><div class="highlight-sub">{tummy_cnt_today} session(s) logged</div></div>""")
    sleep_cnt_today = len(today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)])
    if t_sleep > 0 or sleep_cnt_today > 0: today_cards.append(f"""<div class="highlight-card card-sleep"><div><div class="highlight-title">🛌 Rest & Sleep</div><div class="highlight-body">Logged <b>{int(t_sleep)} hr(s)</b> rest.</div></div><div class="highlight-sub">{sleep_cnt_today} sleep period(s)</div></div>""")
    if t_meds > 0: today_cards.append(f"""<div class="highlight-card card-meds"><div><div class="highlight-title">💊 Medication</div><div class="highlight-body">Logged <b>{t_meds}</b> dose(s).</div></div><div class="highlight-sub">Dose(s) tracked today</div></div>""")
    if t_latest_temp is not None: today_cards.append(f"""<div class="highlight-card card-temp"><div><div class="highlight-title">🌡️ Body Temp</div><div class="highlight-body"><b>{t_latest_temp:.1f} °C</b></div></div><div class="highlight-sub">{len(t_temp_df)} reading(s) logged</div></div>""")
    if len(today_df) > 0: today_cards.append(f"""<div class="highlight-card card-events"><div><div class="highlight-title">📊 Total Events</div><div class="highlight-body"><b>{len(today_df):,}</b> entry(s) logged.</div></div><div class="highlight-sub">Date: {today_date.strftime('%Y-%m-%d')}</div></div>""")

    card_count = len(today_cards)
    base_span = "card-span-3" if card_count >= 4 else ("card-span-4" if card_count == 3 else ("card-span-6" if card_count == 2 else "card-span-12"))
    
    formatted_today_cards = []
    for i, card in enumerate(today_cards):
        cls = f"highlight-card {base_span}"
        if card_count % 2 != 0 and i == 0 and card_count > 1: cls += " mobile-full-width"
        formatted_today_cards.append(card.replace('class="highlight-card', f'class="{cls}'))

    st.markdown(f'<div class="cards-container">{"".join(formatted_today_cards)}</div>', unsafe_allow_html=True)

# --- B. PERIOD HIGHLIGHTS ---
st.markdown('<div id="period-highlights"></div>', unsafe_allow_html=True)
with st.expander(f"✨ Range Highlights [{start_date.strftime('%m.%d')} – {end_date.strftime('%m.%d')}]", expanded=False):
    p_formula = filtered_df[filtered_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
    p_bm = filtered_df[filtered_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
    p_milk, p_feed_cnt = p_formula + p_bm, len(filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
    p_avg_feed = (p_milk / p_feed_cnt) if p_feed_cnt > 0 else 0
    p_wet = len(filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
    p_poop = len(filtered_df[filtered_df['Event Type'].str.contains("Poop", case=False, na=False)])
    p_pumping = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
    p_tummy = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()
    p_sleep = filtered_df[filtered_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
    p_meds = len(filtered_df[filtered_df['Event Type'].str.contains("Meds", case=False, na=False)])
    p_temp_df = filtered_df[filtered_df['Event Type'].str.contains("Temp", case=False, na=False)]
    p_latest_temp = p_temp_df.iloc[0]['Value (Optional)'] if not p_temp_df.empty else None
    p_temp_str = f"<b>{p_latest_temp:.1f} °C</b>" if p_latest_temp else "No readings"
    p_pump_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    p_tummy_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])

    period_cards = [
        f"""<div class="highlight-card card-span-3 card-milk"><div><div class="highlight-title">🍼 Milk Intake</div><div class="highlight-body">Total <b>{int(p_milk):,} mL</b> across <b>{p_feed_cnt}</b> feed(s).</div></div><div class="highlight-sub">Avg Feed: ~{int(p_avg_feed)} mL (Form: {int(p_formula):,}mL, BM: {int(p_bm):,}mL)</div></div>""",
        f"""<div class="highlight-card card-span-3 card-diaper"><div><div class="highlight-title">🚽 Diaper Output</div><div class="highlight-body">Total <b>{p_wet + p_poop}</b> diaper change(s).</div></div><div class="highlight-sub">💧 Wet: {p_wet} | 🚽 Poop: {p_poop}</div></div>""",
        f"""<div class="highlight-card card-span-3 card-pump"><div><div class="highlight-title">🧴 Pumping</div><div class="highlight-body">Pumped <b>{int(p_pumping):,} mL</b> total in range.</div></div><div class="highlight-sub">{p_pump_cnt} pumping session(s)</div></div>""",
        f"""<div class="highlight-card card-span-3 card-tummy"><div><div class="highlight-title">🛟 Tummy Time</div><div class="highlight-body">Logged <b>{int(p_tummy)} min(s)</b> total in range.</div></div><div class="highlight-sub">{p_tummy_cnt} session(s) recorded</div></div>""",
        f"""<div class="highlight-card card-span-3 card-sleep"><div><div class="highlight-title">🛌 Sleep & Rest</div><div class="highlight-body">Logged <b>{int(p_sleep)} hr(s)</b> of rest.</div></div><div class="highlight-sub">{len(filtered_df[filtered_df['Event Type'].str.contains('Sleep', case=False, na=False)])} sleep period(s)</div></div>""",
        f"""<div class="highlight-card card-span-3 card-meds"><div><div class="highlight-title">💊 Medication</div><div class="highlight-body">Logged <b>{p_meds}</b> dose(s).</div></div><div class="highlight-sub">Dose(s) tracked in log</div></div>""",
        f"""<div class="highlight-card card-span-3 card-temp"><div><div class="highlight-title">🌡️ Body Temperature</div><div class="highlight-body">{p_temp_str}</div></div><div class="highlight-sub">{len(p_temp_df)} reading(s) in period</div></div>""",
        f"""<div class="highlight-card card-span-3 card-events"><div><div class="highlight-title">📊 Total Events</div><div class="highlight-body"><b>{len(filtered_df):,}</b> entry(s) logged.</div></div><div class="highlight-sub">From {start_date} to {end_date}</div></div>"""
    ]
    st.markdown(f'<div class="cards-container">{"".join(period_cards)}</div>', unsafe_allow_html=True)

st.markdown('<hr style="margin: 4px 0; opacity: 0.2;">', unsafe_allow_html=True)

def render_empty_state(title="No Data Logged in this period", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">📋 {title}</div><div class="empty-data-sub">{subtitle}</div></div>""", unsafe_allow_html=True)

# ==========================================
# 5. EXPANDED RAW DATA LOGS TABLE
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

if selected_events: table_df = table_df[table_df['Event Type'].isin(selected_events)]
if search_query:
    search_mask = table_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
    table_df = table_df[search_mask]

# Strict Descending Datetime sorting forced with index reset
if 'DateTime' in table_df.columns:
    table_df = table_df.sort_values('DateTime', ascending=False).reset_index(drop=True)
    table_df['DateTime_Display'] = table_df['DateTime']

if 'Value (Optional)' in table_df.columns:
    table_df['Value (Optional)'] = pd.to_numeric(table_df['Value (Optional)'], errors='coerce')

desired_cols = ['DateTime_Display', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)']
actual_cols = [c for c in desired_cols if c in table_df.columns]
display_df = table_df[actual_cols].copy()
if 'DateTime_Display' in display_df.columns: display_df = display_df.rename(columns={'DateTime_Display': 'DateTime'})

if not display_df.empty:
    st.dataframe(
        display_df,
        use_container_width=True,
        height=490,
        column_config={
            "DateTime": st.column_config.DatetimeColumn("DateTime", format="YYYY-MM-DD HH:mm", width="medium"),
            "Event Type": st.column_config.TextColumn("Event Type", width="medium"),
            "Value (Optional)": st.column_config.NumberColumn("Value", width="small"),
            "Notes / Details (Optional)": st.column_config.TextColumn("Notes / Details (Optional)", width="large")
        }
    )
    st.markdown(f'<div class="raw-log-count-text">Showing {len(display_df)} entry(s) matching your criteria strictly sorted descending.</div>', unsafe_allow_html=True)
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")

st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)

# ==========================================
# 6. CHARTS & ANALYTICS
# ==========================================
st.markdown('<div id="analytics-charts"></div>', unsafe_allow_html=True)
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⏰ Today", "🍼 Milk", "🚽 Diapers", "🧴 Pumping", "🛟 Tummy", "📈 Growth (WHO)", "🩺 Health & Vaccine"
])

# TAB 1: FIRST TAB - "Today" 24-Hour Timeline Chart
with tab1:
    cutoff_24h = current_local_time - timedelta(hours=24)
    today_24h_df = df[(df['DateTime'] >= cutoff_24h) & (df['DateTime'] <= current_local_time)].copy()
    
    if not today_24h_df.empty:
        norm_today_df = prepare_normalized_timeline_df(today_24h_df)
        fig_today_timeline = px.scatter(
            norm_today_df, x="DateTime", y="Event Type", size="CategoryBubbleSize", color="Event Type",
            color_discrete_map=COLOR_MAP, hover_data={"Value (Optional)": True, "CategoryBubbleSize": False, "DateTime": False, "Event Type": False}, size_max=14
        )
        fig_today_timeline.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        fig_today_timeline = style_plotly_figure(fig_today_timeline, title_text="⏰ Last 24 Hours Activity Timeline", height=450, is_scatter=True, x_tickformat="%d-%H", x_dtick=10800000, y_tickangle=-45)
        fig_today_timeline.update_layout(showlegend=False)
        st.plotly_chart(fig_today_timeline, use_container_width=True)
    else: render_empty_state("No Events Logged in the Last 24 Hours")

# TAB 2: Milk Intake
with tab2:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)")
        grouped_vol = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        grouped_count = milk_df.groupby(group_col).size().reset_index(name='Total Feeds Count')
        grouped_vol[group_col] = grouped_vol[group_col].apply(format_x_label)
        grouped_count[group_col] = grouped_count[group_col].apply(format_x_label)
        is_single = len(grouped_count[group_col].unique()) == 1
        
        fig_milk = make_subplots(specs=[[{"secondary_y": True}]])
        
        df_f = grouped_vol[grouped_vol['Category'] == '🍼 Formula (mL)']
        if not df_f.empty: fig_milk.add_trace(go.Bar(name='🍼 Formula (mL)', x=df_f[group_col].astype(str), y=df_f['Value (Optional)'], marker_color="#38bdf8", width=0.25 if is_single else None, hovertemplate='%{y} mL<extra></extra>'), secondary_y=False)
            
        df_bm = grouped_vol[grouped_vol['Category'] == '🤱 Breast Milk (mL)']
        if not df_bm.empty: fig_milk.add_trace(go.Bar(name='🤱 Breast Milk (mL)', x=df_bm[group_col].astype(str), y=df_bm['Value (Optional)'], marker_color="#9ca3af", width=0.25 if is_single else None, hovertemplate='%{y} mL<extra></extra>'), secondary_y=False)
            
        fig_milk.add_trace(go.Scatter(name='🔢 Feed Count(s)', x=grouped_count[group_col].astype(str), y=grouped_count['Total Feeds Count'], mode='lines+markers+text', text=grouped_count['Total Feeds Count'], textposition="top center", textfont=dict(size=10.5), line=dict(color='#f97316', width=3, shape='spline', smoothing=1.3), marker=dict(size=10, symbol='circle', color='#f97316', line=dict(width=2, color='#ffffff')), hovertemplate='%{y} feeds<extra></extra>'), secondary_y=True)
        fig_milk = style_plotly_figure(fig_milk, title_text=f"🍼 Milk Intake Volume & Feed Count — {granularity}", height=490, single_point=is_single)
        fig_milk.update_layout(barmode='stack')
        fig_milk.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=9.5), automargin=True)
        fig_milk.update_yaxes(title_text="", secondary_y=True, showgrid=False, tickfont=dict(size=9.5), automargin=True)
        st.plotly_chart(fig_milk, use_container_width=True)
    else: render_empty_state("No Feeding Data Logged in this period")

# TAB 3: Diaper Output
with tab3:
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)].copy()
    if not diaper_df.empty:
        diaper_df['Category'] = diaper_df['Event Type'].apply(lambda x: "🚽 Poop (Cnt)" if "poop" in x.lower() else "💧 Wet Diaper (Cnt)")
        grouped_diaper = diaper_df.groupby([group_col, 'Category']).size().reset_index(name='Count')
        grouped_diaper[group_col] = grouped_diaper[group_col].apply(format_x_label)
        is_single = len(grouped_diaper[group_col].unique()) == 1
        fig_diaper = px.bar(grouped_diaper, x=group_col, y="Count", color="Category", barmode="group", color_discrete_map=COLOR_MAP)
        if is_single: fig_diaper.update_traces(width=0.25)
        fig_diaper.update_traces(hovertemplate='%{y}<extra></extra>')
        fig_diaper = style_plotly_figure(fig_diaper, title_text=f"🚽 Diaper Changes Count — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_diaper, use_container_width=True)
    else: render_empty_state("No Diaper Data Logged in this period")

# TAB 4: Dedicated Pumping Chart
with tab4:
    pump_df = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)].copy()
    if not pump_df.empty:
        grouped_pump = pump_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_pump[group_col] = grouped_pump[group_col].apply(format_x_label)
        is_single = len(grouped_pump[group_col].unique()) == 1
        fig_pump = px.bar(grouped_pump, x=group_col, y="Value (Optional)", color_discrete_sequence=[COLOR_MAP["🧴 Pumping (mL)"]])
        if is_single: fig_pump.update_traces(width=0.25)
        fig_pump.update_traces(hovertemplate='%{y} mL<extra></extra>')
        fig_pump = style_plotly_figure(fig_pump, title_text=f"🧴 Pumping Volume (mL) — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_pump, use_container_width=True)
    else: render_empty_state("No Pumping Data Logged in this period")

# TAB 5: Dedicated Tummy Time Chart
with tab5:
    tummy_df = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)].copy()
    if not tummy_df.empty:
        grouped_tummy = tummy_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_tummy[group_col] = grouped_tummy[group_col].apply(format_x_label)
        is_single = len(grouped_tummy[group_col].unique()) == 1
        fig_tummy = px.bar(grouped_tummy, x=group_col, y="Value (Optional)", color_discrete_sequence=[COLOR_MAP["🛟 Tummy Time (Mins)"]])
        if is_single: fig_tummy.update_traces(width=0.25)
        fig_tummy.update_traces(hovertemplate='%{y} Mins<extra></extra>')
        fig_tummy = style_plotly_figure(fig_tummy, title_text=f"🛟 Tummy Time — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_tummy, use_container_width=True)
    else: render_empty_state("No Tummy Time Data Logged in this period")

# ==============================================================================
# TAB 6: WHO GROWTH CHARTS (Weight, Height, Head Circumference)
# ==============================================================================
with tab6:
    who_option = st.radio(
        "Select Standard WHO Chart (0-24 Months):",
        options=["⚖️ Weight (kg)", "🏔️ Height (cm)", "🐷 Head Size (cm)"],
        horizontal=True, label_visibility="collapsed"
    )
    
    # Generic WHO 50th Percentile data approx based on Gender selection
    def get_who_data(gen, met):
        if met == "⚖️ Weight (kg)":
            if gen == "Boy": return np.array([3.3, 4.5, 5.6, 6.4, 7.0, 7.5, 7.9, 8.3, 8.6, 8.9, 9.2, 9.4, 9.6, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5, 11.8, 12.0, 12.2])
            else: return np.array([3.2, 4.2, 5.1, 5.8, 6.4, 6.9, 7.3, 7.6, 7.9, 8.2, 8.5, 8.7, 8.9, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.9, 11.1, 11.3, 11.5])
        elif met == "🏔️ Height (cm)":
            if gen == "Boy": return np.array([49.9, 54.7, 58.4, 61.4, 63.9, 65.9, 67.6, 69.2, 70.6, 72.0, 73.3, 74.5, 75.7, 76.9, 78.0, 79.1, 80.2, 81.2, 82.3, 83.2, 84.2, 85.1, 86.0, 86.9, 87.8])
            else: return np.array([49.1, 53.7, 57.1, 59.8, 62.1, 64.0, 65.7, 67.3, 68.7, 70.1, 71.5, 72.8, 74.0, 75.2, 76.4, 77.5, 78.6, 79.7, 80.7, 81.7, 82.7, 83.7, 84.6, 85.5, 86.4])
        else: # Head
            if gen == "Boy": return np.array([34.5, 37.3, 39.1, 40.5, 41.6, 42.6, 43.3, 44.0, 44.6, 45.1, 45.5, 46.0, 46.3, 46.6, 46.9, 47.2, 47.4, 47.6, 47.8, 48.0, 48.2, 48.4, 48.5, 48.7, 48.8])
            else: return np.array([33.9, 36.5, 38.3, 39.5, 40.6, 41.5, 42.2, 42.8, 43.4, 43.8, 44.2, 44.6, 44.9, 45.2, 45.4, 45.7, 45.9, 46.1, 46.3, 46.5, 46.7, 46.9, 47.0, 47.2, 47.3])

    def get_who_mults(met):
        if met == "⚖️ Weight (kg)": return (0.85, 0.92, 1.09, 1.18)
        if met == "🏔️ Height (cm)": return (0.95, 0.975, 1.025, 1.05)
        return (0.965, 0.98, 1.02, 1.035)

    who_df = df[df['Event Type'] == who_option].copy()
    
    if not who_df.empty:
        who_df = who_df.sort_values('DateTime', ascending=True)
        who_df['Age_Months'] = (who_df['Date'] - birth_date).dt.days / 30.437
        who_df = who_df[who_df['Age_Months'] >= 0] # Filter out pre-birth logs
        
        m_x = np.arange(25)
        p50 = get_who_data(gender, who_option)
        m10, m25, m75, m90 = get_who_mults(who_option)
        p10, p25, p75, p90 = p50*m10, p50*m25, p50*m75, p50*m90
        
        # Calculate Estimated Percentiles for User Hover Math
        def estimate_pct(row):
            if row['Age_Months'] > 24: return 50
            local_p50 = np.interp(row['Age_Months'], m_x, p50)
            local_p10 = np.interp(row['Age_Months'], m_x, p10)
            local_p90 = np.interp(row['Age_Months'], m_x, p90)
            z = (row['Value (Optional)'] - local_p50) / ((local_p90 - local_p10) / 2.56)
            return (1 / (1 + np.exp(-1.702 * z))) * 100 # Logistic Approx of CDF
            
        who_df['Est_Pct'] = who_df.apply(estimate_pct, axis=1)

        fig_who = go.Figure()
        
        # Render mathematical WHO bands using standard color alpha fill logic
        fig_who.add_trace(go.Scatter(x=m_x, y=p90, line=dict(width=0), showlegend=False, hoverinfo='skip'))
        fig_who.add_trace(go.Scatter(x=m_x, y=p75, fill='tonexty', fillcolor='rgba(14,165,233,0.1)', line=dict(width=0), name='75th-90th', hoverinfo='skip'))
        fig_who.add_trace(go.Scatter(x=m_x, y=p50, fill='tonexty', fillcolor='rgba(14,165,233,0.25)', line=dict(width=0), name='50th-75th', hoverinfo='skip'))
        fig_who.add_trace(go.Scatter(x=m_x, y=p25, fill='tonexty', fillcolor='rgba(14,165,233,0.25)', line=dict(width=0), name='25th-50th', hoverinfo='skip'))
        fig_who.add_trace(go.Scatter(x=m_x, y=p10, fill='tonexty', fillcolor='rgba(14,165,233,0.1)', line=dict(width=0), name='10th-25th', hoverinfo='skip'))
        
        # Solid dotted line for the exact 50th median
        fig_who.add_trace(go.Scatter(x=m_x, y=p50, mode='lines', line=dict(color='rgba(2,132,199,0.5)', width=2, dash='dot'), name='WHO 50th', hoverinfo='skip'))
        
        # Overlay User Data exactly over the mathematical bands
        c_code = COLOR_MAP.get(who_option, '#38bdf8')
        unit_str = who_option.split('(')[1].replace(')','')
        
        fig_who.add_trace(go.Scatter(
            x=who_df['Age_Months'], y=who_df['Value (Optional)'], mode='lines+markers',
            line=dict(color=c_code, width=3, shape='spline'),
            marker=dict(size=10, color=c_code, line=dict(width=2, color='#ffffff')),
            name=who_option.split(' ')[1],
            customdata=np.stack((who_df['Date'], who_df['Est_Pct']), axis=-1),
            hovertemplate=f"<b>Age:</b> %{{x:.1f}} mo<br><b>%{{y:.2f}} {unit_str}</b><br><b>Est. Percentile:</b> ~%{{customdata[1]:.0f}}th<br><i>%{{customdata[0]}}</i><extra></extra>"
        ))
        
        # Lock styling
        fig_who.update_layout(
            title=dict(text=f"📈 {who_option} — WHO Growth Standard", y=0.97, x=0.5, xanchor="center", font=dict(size=16)),
            height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=2, r=2, t=60, b=20),
            xaxis=dict(title="Age (Months)", showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickformat=".0f", range=[0, max(24, who_df['Age_Months'].max() + 1)]),
            yaxis=dict(title="", showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            showlegend=False, hovermode="x unified"
        )
        st.plotly_chart(fig_who, use_container_width=True)
        st.caption(f"ℹ️ *Interactive WHO 0-24 month Fan Chart for {gender}s. The shaded bands map the mathematical 10th to 90th percentiles.*")
    else:
        render_empty_state(f"No {who_option} Data Logged")


# TAB 7: Health Charts & HKCIP Vaccine Tracker
with tab7:
    act_option = st.radio("Select Category:", options=["🛌 Sleep (hrs)", "🌡️ Temp (°C)", "💊 Meds (Cnt)", "💉 HKCIP Vaccine Tracker"], horizontal=True, label_visibility="collapsed")
    
    if act_option == "💉 HKCIP Vaccine Tracker":
        vac_df = df[df['Event Type'].str.contains("Vaccine", case=False, na=False)].copy()
        
        st.markdown("##### 📌 HKCIP Official Guidelines (0-2 Years)")
        hkcip_schedule = [
            {"Milestone": "Newborn", "Vaccines Given": "BCG, Hepatitis B (Dose 1)"},
            {"Milestone": "1 Month", "Vaccines Given": "Hepatitis B (Dose 2)"},
            {"Milestone": "2 Months", "Vaccines Given": "Hexavalent / DTaP-IPV-Hib-HepB (Dose 1), Pneumococcal (Dose 1)"},
            {"Milestone": "4 Months", "Vaccines Given": "Hexavalent / DTaP-IPV-Hib-HepB (Dose 2), Pneumococcal (Dose 2)"},
            {"Milestone": "6 Months", "Vaccines Given": "Hexavalent / DTaP-IPV-Hib-HepB (Dose 3), Pneumococcal (Dose 3)"},
            {"Milestone": "12 Months", "Vaccines Given": "MMR (Dose 1), Pneumococcal (Booster), Varicella (Dose 1)"},
            {"Milestone": "18 Months", "Vaccines Given": "Hexavalent / DTaP-IPV-Hib-HepB (Booster), MMRV (Dose 2)"}
        ]
        st.table(pd.DataFrame(hkcip_schedule))
        
        st.markdown("##### 📋 Riley's Vaccination History")
        if not vac_df.empty:
            if 'DateTime' in vac_df.columns:
                vac_df = vac_df.sort_values('DateTime', ascending=True).reset_index(drop=True)
                vac_df['DateTime_Display'] = vac_df['DateTime']
                vac_df['Age at Shot'] = ((vac_df['Date'] - birth_date).dt.days / 30.437).round(1).astype(str) + " mo"
            
            desired_cols = ['DateTime_Display', 'Age at Shot', 'Event Type', 'Notes / Details (Optional)']
            display_vac = vac_df[[c for c in desired_cols if c in vac_df.columns]].copy()
            if 'DateTime_Display' in display_vac.columns: display_vac = display_vac.rename(columns={'DateTime_Display': 'Date Logged'})
                
            st.dataframe(
                display_vac,
                use_container_width=True, hide_index=True, height=350,
                column_config={"Date Logged": st.column_config.DatetimeColumn("Date Logged", format="YYYY-MM-DD", width="medium"), "Notes / Details (Optional)": st.column_config.TextColumn("Vaccine Type / Notes", width="large")}
            )
        else: render_empty_state("No Vaccine Data Logged")
            
    else:
        act_mapping = {
            "🛌 Sleep (hrs)": ("Sleep", "Duration (hrs)", COLOR_MAP["🛌 Sleep (hrs)"], "hrs"),
            "🌡️ Temp (°C)": ("Temp", "Temperature (°C)", COLOR_MAP["🌡️ Temp (°C)"], "°C"),
            "💊 Meds (Cnt)": ("Meds", "Dose Count(s)", COLOR_MAP["💊 Meds (Cnt)"], "doses")
        }
        
        keyword, y_title, act_color, unit = act_mapping[act_option]
        act_df = filtered_df[filtered_df['Event Type'].str.contains(keyword, case=False, na=False)].copy()
        
        if not act_df.empty:
            if keyword == "Temp":
                grouped_act = act_df.groupby(group_col)['Value (Optional)'].mean().reset_index()
                grouped_act[group_col] = grouped_act[group_col].apply(format_x_label)
                is_single = len(grouped_act[group_col].unique()) == 1
                fig_act = px.line(grouped_act, x=group_col, y="Value (Optional)", markers=True, color_discrete_sequence=[act_color], labels={"Value (Optional)": y_title, group_col: granularity})
                fig_act.update_traces(line=dict(width=3, shape='spline', smoothing=1.3), marker=dict(size=12 if is_single else 8, symbol='circle', line=dict(width=2, color='#ffffff')), hovertemplate=f'%{{y:.1f}} {unit}<extra></extra>')
            elif keyword == "Sleep":
                grouped_act = act_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
                grouped_act[group_col] = grouped_act[group_col].apply(format_x_label)
                is_single = len(grouped_act[group_col].unique()) == 1
                fig_act = px.bar(grouped_act, x=group_col, y="Value (Optional)", color_discrete_sequence=[act_color], labels={"Value (Optional)": y_title, group_col: granularity})
                if is_single: fig_act.update_traces(width=0.25)
                fig_act.update_traces(hovertemplate=f'%{{y}} {unit}<extra></extra>')
            else: # Meds count
                grouped_act = act_df.groupby(group_col).size().reset_index(name='Value (Optional)')
                grouped_act[group_col] = grouped_act[group_col].apply(format_x_label)
                is_single = len(grouped_act[group_col].unique()) == 1
                fig_act = px.bar(grouped_act, x=group_col, y="Value (Optional)", color_discrete_sequence=[act_color], labels={"Value (Optional)": y_title, group_col: granularity})
                if is_single: fig_act.update_traces(width=0.25)
                fig_act.update_traces(hovertemplate=f'%{{y}} {unit}<extra></extra>')
                
            fig_act = style_plotly_figure(fig_act, title_text=f"🩺 Health — {act_option} ({granularity})", height=450, single_point=is_single)
            st.plotly_chart(fig_act, use_container_width=True)
        else: render_empty_state(f"No {act_option.split(' ')[1]} Data Logged in this period")

