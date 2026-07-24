import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley's Dash",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Apple Touch Icon ONLY
components.html(
    """
    <script>
    (function() {
        const iconUrl = "https://em-content.zobj.net/source/apple/391/baby-bottle_1f37c.png";
        try { 
            let targetDoc = window.top ? window.top.document : document;
            const rels = ['apple-touch-icon', 'apple-touch-icon-precomposed', 'icon', 'shortcut icon'];
            rels.forEach(function(rel) {
                let link = targetDoc.querySelector("link[rel='" + rel + "']");
                if (!link) {
                    link = targetDoc.createElement('link');
                    link.rel = rel;
                    targetDoc.head.appendChild(link);
                }
                link.href = iconUrl;
            });
        } catch(e) {}
    })();
    </script>
    """,
    height=0,
    width=0
)

# Responsive & Adaptive CSS overrides
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    html { scroll-behavior: smooth; }
    [id] { scroll-margin-top: 70px; }

    /* Standard Streamlit scrolling for stable UI and native iOS compatibility */
    body, .stApp {
        color: var(--card-text) !important;
        background-color: #f8fafc !important;
    }

    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important; 
    }
    
    /* Generous bottom padding so switching tabs doesn't bounce the page */
    [data-testid="stMainBlockContainer"] {
        padding-top: calc(2.5rem + env(safe-area-inset-top)) !important;
        padding-bottom: 25rem !important; 
    }

    /* Highly Compressed Vertical Spacing Between Blocks */
    div[data-testid="stVerticalBlock"] { gap: 0.15rem !important; }

    :root {
        --card-bg: #ffffff; --card-border: #e2e8f0; --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); --card-text: #1e293b;
    }

    /* Title Styling - Forces normal wrap natively */
    .app-main-title {
        font-size: clamp(2.0rem, 5vw + 0.8rem, 2.8rem) !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        white-space: normal !important; 
        color: var(--card-text);
        margin: 0;
        padding: 0;
    }

    /* --- NATIVE STREAMLIT HEADER RESTRUCTURING --- */
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
        align-items: center !important;
        margin-top: 1rem !important;
        margin-bottom: 2.0rem !important;
    }

    /* Force Native Streamlit Buttons to adopt Custom UI styling perfectly */
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-secondary"],
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseLinkButton-secondary"] {
        height: 42px !important; min-height: 42px !important; 
        padding: 0 !important; border-radius: 8px !important;
        border: 1px solid var(--card-border) !important;
        background-color: var(--card-bg) !important;
        box-shadow: var(--card-shadow) !important; transition: all 0.15s ease;
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; text-decoration: none !important; box-sizing: border-box;
    }
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) p {
        font-weight: 600 !important; font-size: 0.95rem !important; color: #1e293b !important; margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-secondary"]:active,
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseLinkButton-secondary"]:active {
        background-color: #f1f5f9 !important; transform: scale(0.98);
    }

    /* Mobile 50/50 Split Sizing (Title 100%, Buttons 50/50 Below it) */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
            flex-wrap: wrap !important; gap: 0.5rem !important;
            flex-direction: row !important; /* Force row layout to stop stacking */
            margin-bottom: 2.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(1) {
            flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
            margin-bottom: 1.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(2) {
            flex: 0 0 calc(50% - 0.25rem) !important; width: calc(50% - 0.25rem) !important; min-width: calc(50% - 0.25rem) !important; margin-right: 0.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(3) {
            flex: 0 0 calc(50% - 0.25rem) !important; width: calc(50% - 0.25rem) !important; min-width: calc(50% - 0.25rem) !important; margin: 0 !important;
        }
    }

    /* Mobile Compact 2x2 Grid for Filters */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div > div[data-testid="stSelectbox"]) {
            flex-wrap: wrap !important;
            flex-direction: row !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div > div[data-testid="stSelectbox"]) > div[data-testid="column"] {
            width: calc(50% - 0.5rem) !important;
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
            margin-bottom: 0.5rem !important;
        }
    }

    /* Standard Elements */
    span[data-baseweb="tag"] { background-color: #e5e7eb !important; color: #1f2937 !important; border: 1px solid #d1d5db !important; font-weight: 500 !important; }
    .toc-button { display: block; width: 100%; padding: 8px 12px; margin: 4px 0; background-color: var(--card-bg); border: 1px solid var(--card-border); box-shadow: var(--card-shadow); color: var(--card-text) !important; text-decoration: none !important; border-radius: 8px; font-size: 0.9rem; font-weight: 500; transition: all 0.15s ease-in-out; }
    .toc-button:hover { background-color: #f1f5f9; border-color: #cbd5e1; text-decoration: none !important; }
    
    .sidebar-header { font-weight: 700; font-size: 1.05rem; margin-bottom: 0px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px; margin-top: 32px; }

    .cards-container { display: grid !important; grid-template-columns: repeat(12, 1fr) !important; gap: 8px !important; align-items: stretch !important; margin-bottom: 2px !important; width: 100% !important; margin-top: 8px !important; }
    .card-span-3 { grid-column: span 3 !important; } .card-span-4 { grid-column: span 4 !important; } .card-span-6 { grid-column: span 6 !important; } .card-span-12 { grid-column: span 12 !important; } 
    @media (max-width: 1024px) { .card-span-3, .card-span-4 { grid-column: span 6 !important; } .mobile-full-width { grid-column: span 12 !important; } }

    .highlight-card { background-color: var(--card-bg); border-radius: 12px; padding: 10px 12px; min-height: 118px; height: 100% !important; display: flex !important; flex-direction: column !important; justify-content: space-between !important; box-shadow: var(--card-shadow); border: 1px solid var(--card-border); box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word; color: var(--card-text) !important; transition: background-color 0.15s ease, transform 0.15s ease; }
    @media (min-width: 769px) { .highlight-card:hover { background-color: #f1f5f9 !important; transform: translateY(-2px); border-color: #cbd5e1 !important; cursor: default; } }
    
    .card-milk { border-left: 5px solid #38bdf8; } .card-feed { border-left: 5px solid #c084fc; } .card-diaper { border-left: 5px solid #0284c7; } .card-pump { border-left: 5px solid #a855f7; } .card-tummy { border-left: 5px solid #10b981; } .card-sleep { border-left: 5px solid #818cf8; } .card-meds { border-left: 5px solid #fbbf24; } .card-temp { border-left: 5px solid #f87171; } .card-events { border-left: 5px solid #94a3b8; }
    .highlight-title { font-weight: 600; font-size: 0.88rem; margin-bottom: 3px; line-height: 1.2; } .highlight-body { font-size: 0.84rem; opacity: 0.92; line-height: 1.25; } .highlight-sub { font-size: 0.74rem; opacity: 0.75; margin-top: 3px; line-height: 1.25; }

    .default-range-text { color: #64748b; font-size: 0.8rem; font-style: italic; margin-top: 1px; display: inline-block; }
    .raw-log-count-text { font-size: 0.72rem; color: #64748b; margin-top: 3px; margin-bottom: 6px; }

    .empty-data-card { background-color: var(--card-bg); border: 1.5px dashed var(--card-border); border-radius: 12px; padding: 16px; text-align: center; margin: 6px 0; color: var(--card-text); }
    .empty-data-title { font-size: 0.95rem; font-weight: 600; margin-bottom: 3px; }
    .empty-data-sub { font-size: 0.8rem; opacity: 0.75; }
    </style>
""", unsafe_allow_html=True)

# Main Title Anchor
st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. RESPONSIVE HEADER SECTION (NATIVE STREAMLIT)
# ---------------------------------------------------------
# Natively structured 60% / 20% / 20% columns ensuring buttons are <= 30% each on Desktop
h_col1, h_col2, h_col3 = st.columns([6, 2, 2], vertical_alignment="center")

with h_col1:
    st.markdown('<div class="app-main-title">🍼 Riley\'s Dash</div>', unsafe_allow_html=True)

with h_col2:
    st.link_button("➕ Add", "shortcuts://run-shortcut?name=Riley%20Tracker", use_container_width=True)

with h_col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.session_state.show_refresh_toast = True
        st.rerun()

# Executes the native Streamlit toast on reload
if st.session_state.get('show_refresh_toast', False):
    st.toast("Data successfully updated!", icon="✅")
    st.session_state.show_refresh_toast = False

# ==========================================
# 3. SIDEBAR TABLE OF CONTENTS & GSHEET SETTINGS
# ==========================================
st.sidebar.markdown("""
    <div style="margin-bottom: 12px;">
        <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 8px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px;">📌 Quick Navigation</div>
        <a href="#today" class="toc-button">✨ Today</a>
        <a href="#filters" class="toc-button">⚙️ Filters</a>
        <a href="#insights" class="toc-button">📊 Insights</a>
        <a href="#database" class="toc-button">📋 Database</a>
    </div>
""", unsafe_allow_html=True)

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"

st.sidebar.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px;'>⚙️ Configuration</div>", unsafe_allow_html=True)
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL)
tz_offset = st.sidebar.number_input("Timezone Offset (UTC Hours)", value=8, step=1)
if sheet_url_input: st.sidebar.link_button("🔗 Open Google Sheet Directly", sheet_url_input, use_container_width=True)

st.sidebar.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px;'>👶 Baby Settings</div>", unsafe_allow_html=True)
baby_dob = st.sidebar.date_input("Birth Date", value=datetime(2026, 6, 29).date())
baby_gender = st.sidebar.radio("Gender (For Growth Charts)", ["Girl", "Boy"], index=0, horizontal=True)

def get_csv_export_url(url_or_id):
    if not url_or_id: return None
    if "docs.google.com/spreadsheets" in url_or_id:
        try: return f"https://docs.google.com/spreadsheets/d/{url_or_id.split('/d/')[1].split('/')[0]}/export?format=csv"
        except IndexError: return None
    return f"https://docs.google.com/spreadsheets/d/{url_or_id}/export?format=csv"

@st.cache_data(ttl=1)
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
if not csv_url: st.stop()

df = load_sheet_data(csv_url)
if df.empty: st.stop()

max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

def standardize_event_name(event_str):
    s = str(event_str).strip()
    mapping = {
        "Formula (mL)": "🍼 Formula (mL)", "Breast Milk (mL)": "🤱 Breast Milk (mL)",
        "Wet Diaper (Cnt)": "💧 Wet Diaper (Cnt)", "Poop (Cnt)": "🚽 Poop (Cnt)",
        "Pumping (mL)": "🧴 Pumping (mL)", "Tummy Time (Mins)": "🛟 Tummy Time (Mins)",
        "Sleep (hrs)": "🛌 Sleep (hrs)", "Temp (°C)": "🌡️ Temp (°C)", "Meds (Cnt)": "💊 Meds (Cnt)",
        "Weight (kg)": "⚖️ Weight (kg)", "Height (cm)": "🏔️ Height (cm)", "Head Size (cm)": "🐷 Head Size (cm)",
        "Head (cm)": "🐷 Head Size (cm)", "Vaccine": "💉 Vaccine (Cnt)", "Vaccine (Cnt)": "💉 Vaccine (Cnt)"
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
    "⚖️ Weight (kg)": "#14b8a6", "🏔️ Height (cm)": "#0ea5e9", "🐷 Head Size (cm)": "#ec4899",
    "💉 Vaccine (Cnt)": "#f43f5e", "Other": "#6b7280"
}

def format_x_label(val):
    try: return pd.to_datetime(val).strftime('%m.%d')
    except Exception: return str(val)

def style_plotly_figure(fig, title_text="", height=460, single_point=False, is_scatter=False, x_tickformat=None, x_dtick=None, y_tickangle=None):
    layout_args = dict(
        title=dict(text=title_text, y=0.97, x=0.5, xanchor="center", yanchor="top", font=dict(size=16, weight="normal")),
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=2, r=2, t=75, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text="", font=dict(size=10)),
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

def get_unit_from_name(name):
    if "mL" in name: return " mL"
    if "Mins" in name: return " Mins"
    if "hrs" in name: return " hrs"
    if "°C" in name: return " °C"
    if "kg" in name: return " kg"
    if "cm" in name: return " cm"
    return ""

def render_insight_card(text):
    html_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    st.markdown(f"""
    <div style="background-color: #f8fafc; border-left: 4px solid #8b5cf6; padding: 12px 16px; border-radius: 8px; margin: 12px 0 24px 0; font-size: 0.88rem; color: #334155; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <strong style="color: #6d28d9;">✨ AI Insight:</strong> {html_text}
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 4. TODAY'S HIGHLIGHTS (Moved Up!)
# ==========================================
utc_now = datetime.utcnow()
current_local_time = utc_now + timedelta(hours=tz_offset)

all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_row = all_feed_events.iloc[0]
    last_feed_dt = last_feed_row['DateTime']
    total_seconds = int((current_local_time - last_feed_dt).total_seconds())
    if total_seconds < 0: total_seconds = 0
    hrs_since, mins_since = total_seconds // 3600, (total_seconds % 3600) // 60
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

def render_empty_state(title="No Data Logged", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">📋 {title}</div><div class="empty-data-sub">{subtitle}</div></div>""", unsafe_allow_html=True)

st.markdown('<div id="today"></div>', unsafe_allow_html=True)
today_date = max(current_local_time.date(), max_data_date)
today_df = df[df['Date'] == today_date]

st.subheader("✨ Today")

if today_df.empty:
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">📋 No Data Logged Today</div><div class="empty-data-sub">Waiting for new entries.</div></div>""", unsafe_allow_html=True)
else:
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
    t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
    t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None

    today_cards = []
    today_cards.append(f"""<div class="highlight-card card-feed"><div><div class="highlight-title">⏰ Last Feeding</div><div class="highlight-body"><b>{last_feed_delta}</b></div></div><div class="highlight-sub">{last_feed_sub}</div></div>""")
    if t_milk > 0 or t_feed_cnt > 0: today_cards.append(f"""<div class="highlight-card card-milk"><div><div class="highlight-title">🍼 Milk Intake</div><div class="highlight-body">Total <b>{int(t_milk):,} mL</b> across <b>{t_feed_cnt}</b> feed(s).</div></div><div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Form: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div></div>""")
    if t_wet + t_poop > 0: today_cards.append(f"""<div class="highlight-card card-diaper"><div><div class="highlight-title">🚽 Diaper Output</div><div class="highlight-body">Total <b>{t_wet + t_poop}</b> change(s).</div></div><div class="highlight-sub">💧 Wet: {t_wet} | 🚽 Poop: {t_poop}</div></div>""")
    p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    if t_pumping > 0 or p_cnt_today > 0: today_cards.append(f"""<div class="highlight-card card-pump"><div><div class="highlight-title">🧴 Pumping</div><div class="highlight-body">Pumped <b>{int(t_pumping):,} mL</b> today.</div></div><div class="highlight-sub">{p_cnt_today} pumping session(s)</div></div>""")
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


div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-secondary"]:active,
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseLinkButton-secondary"]:active {
        background-color: #f1f5f9 !important; transform: scale(0.98);
    }

    /* Mobile 50/50 Split Sizing (Title 100%, Buttons 50/50 Below it) */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
            
            flex-wrap: wrap !important; gap: 0.5rem !important;
            flex-direction: row !important; /* Force row layout to stop stacking */
            margin-bottom: 2.5rem !important;
            align-items: flex-start !important; /* Prevent flex from ignoring vertical margins */
        }
        .app-main-title {
            margin-bottom: 1.5rem !important; /* Force direct margin on the title itself */
            padding-bottom: 0.25rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(1) {
            flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(2) {
            flex: 0 0 calc(50% - 0.25rem) !important; width: calc(50% - 0.25rem) !important; min-width: calc(50% - 0.25rem) !important; margin-right: 0.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(3) {
            flex: 0 0 calc(50% - 0.25rem) !important; width: calc(50% - 0.25rem) !important; min-width: calc(50% - 0.25rem) !important; margin: 0 !important;
        }
    }

    /* Mobile Compact 2x2 Grid for Filters */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
            flex-wrap: wrap !important; gap: 0.5rem !important;
            flex-direction: row !important; /* Force row layout to stop stacking */
            margin-bottom: 2.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(1) {
            flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
            margin-bottom: 1.5rem !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) > div[data-testid="column"]:nth-child(2) {
# ... existing code ...
# ==========================================
# 5. COMPACT QUICK FILTERS (MOVED BELOW TODAY)
# ==========================================
min_str = min_data_date.strftime('%m.%d')
max_str = max_data_date.strftime('%m.%d')

if 'sd' not in st.session_state: 
    st.session_state.sd = max(min_data_date, max_data_date - timedelta(days=20))
if 'ed' not in st.session_state: 
    st.session_state.ed = max_data_date

st.markdown('<div id="filters" style="margin-top: 4rem; padding-top: 1rem;"></div>', unsafe_allow_html=True)
st.markdown("<div style='font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;'>⚙️ Date Range & Grouping Filters</div>", unsafe_allow_html=True)

# Compact 4-Column Layout (Wrapped neatly into 2x2 grid on mobile via CSS)
f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1, 1, 0.8], vertical_alignment="bottom")
# ... existing code ...
start_date = st.session_state.sd
end_date = st.session_state.ed
group_col_map = {"Daily": "Date", "Weekly": "Week", "Monthly": "Month", "All Time": "Month"}
group_col = group_col_map[granularity]
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.markdown("<div style='margin-top: 1.5rem; margin-bottom: 2.5rem; border-bottom: 1px solid rgba(128,128,128,0.15);'></div>", unsafe_allow_html=True)


# ==========================================
# 6. CHARTS & ANALYTICS
# ==========================================
# ... existing code ...
# ==========================================
# 6. CHARTS & ANALYTICS
# ==========================================
st.markdown('<div id="insights"></div>', unsafe_allow_html=True)
st.subheader("📊 Insights")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "⏰ Today", "🍼 Milk", "🚽 Diapers", "🧴 Pumping", "🛟 Tummy", "📈 Growth", "🩺 Health", "💉 Vaccine"
])

# TAB 1: FIRST TAB - "Today" 24-Hour Timeline Chart
with tab1:
    cutoff_24h = current_local_time - timedelta(hours=24)
    today_24h_df = df[(df['DateTime'] >= cutoff_24h) & (df['DateTime'] <= current_local_time)].copy()
    
    if not today_24h_df.empty:
        norm_today_df = prepare_normalized_timeline_df(today_24h_df)
        
        def get_short_name(name):
            if "Formula" in name: return "🍼 Form."
            if "Breast Milk" in name: return "🤱 BM"
            if "Wet Diaper" in name: return "💧 Wet"
            if "Poop" in name: return "🚽 Poop"
            if "Pumping" in name: return "🧴 Pump"
            if "Tummy" in name: return "🛟 Tummy"
            if "Sleep" in name: return "🛌 Sleep"
            if "Temp" in name: return "🌡️ Temp"
            if "Meds" in name: return "💊 Meds"
            if "Weight" in name: return "⚖️ Wt."
            if "Height" in name: return "🏔️ Ht."
            if "Head" in name: return "🐷 Head"
            if "Vaccine" in name: return "💉 Vac."
            return name
            
        norm_today_df['Short_Event'] = norm_today_df['Event Type'].apply(get_short_name)
        
        fig_today_timeline = px.scatter(
            norm_today_df, x="DateTime", y="Short_Event", size="CategoryBubbleSize", color="Event Type",
            color_discrete_map=COLOR_MAP, text="Value (Optional)", hover_data={"Value (Optional)": True, "CategoryBubbleSize": False, "DateTime": False, "Event Type": False}, size_max=14
        )
        
        fig_today_timeline.for_each_trace(
            lambda t: t.update(mode='markers+text', textposition='top center', textfont=dict(weight='bold'), texttemplate='%{text}' + get_unit_from_name(t.name)) if "(Cnt)" not in t.name else t.update(mode='markers', text=None)
        )
        
        fig_today_timeline.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        fig_today_timeline = style_plotly_figure(fig_today_timeline, title_text="⏰ Last 24 Hours Activity Timeline", height=450, is_scatter=True, x_tickformat="%d-%H", x_dtick=10800000, y_tickangle=-45)
        fig_today_timeline.update_layout(showlegend=False, yaxis=dict(title=dict(text=""), showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=10.5), automargin=True))
        st.plotly_chart(fig_today_timeline, use_container_width=True)
        
        st.caption("ℹ️ *Interactive scatter timeline displaying all events logged within the last 24 hours. Markers size and label text correspond to the recorded volume/duration.*")

        feed_cnt = len(today_24h_df[today_24h_df['Event Type'].str.contains("Formula|Breast Milk")])
        diaper_cnt = len(today_24h_df[today_24h_df['Event Type'].str.contains("Diaper|Poop")])
        analysis = f"Riley has had **{feed_cnt} feeds** and **{diaper_cnt} diaper changes** in the past 24 hours. "
        if feed_cnt >= 7: analysis += "Her feeding frequency is robust, which is excellent for hydration and growth!"
        elif feed_cnt > 0: analysis += "Her routine appears well-spaced and stable."
        render_insight_card(analysis)
    else: render_empty_state("No Events Logged in the Last 24 Hours")

# TAB 2: Milk Intake
with tab2:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)")
        
        grouped_vol = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        grouped_count = milk_df.groupby(group_col).size().reset_index(name='Total Feeds Count')
        
        total_per_x = milk_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        total_per_x = total_per_x.sort_values(group_col)
        total_per_x['Trend'] = total_per_x['Value (Optional)'].rolling(window=min(7, len(total_per_x)), min_periods=1).mean()

        grouped_vol[group_col] = grouped_vol[group_col].apply(format_x_label)
        grouped_count[group_col] = grouped_count[group_col].apply(format_x_label)
        total_per_x[group_col] = total_per_x[group_col].apply(format_x_label)
        is_single = len(grouped_count[group_col].unique()) == 1
        
        fig_milk = make_subplots(specs=[[{"secondary_y": True}]])
        df_f = grouped_vol[grouped_vol['Category'] == '🍼 Formula (mL)']
        if not df_f.empty: 
            fig_milk.add_trace(go.Bar(
                name='🍼 Formula (mL)', x=df_f[group_col].astype(str), y=df_f['Value (Optional)'], 
                marker_color="#38bdf8", width=0.25 if is_single else None, 
                text=df_f['Value (Optional)'], textposition='inside', textfont=dict(weight='bold', color='white'),
                hovertemplate='%{y} mL<extra></extra>'
            ), secondary_y=False)
            
        df_bm = grouped_vol[grouped_vol['Category'] == '🤱 Breast Milk (mL)']
        if not df_bm.empty: 
            fig_milk.add_trace(go.Bar(name='🤱 Breast Milk (mL)', x=df_bm[group_col].astype(str), y=df_bm['Value (Optional)'], marker_color="#9ca3af", width=0.25 if is_single else None, hovertemplate='%{y} mL<extra></extra>'), secondary_y=False)
            
        fig_milk.add_trace(go.Scatter(name='🔢 Feed Count(s)', x=grouped_count[group_col].astype(str), y=grouped_count['Total Feeds Count'], mode='lines+markers+text', text=grouped_count['Total Feeds Count'], textposition="top center", textfont=dict(size=10.5, weight='bold'), line=dict(color='#f97316', width=3, shape='spline', smoothing=1.3), marker=dict(size=10, symbol='circle', color='#f97316', line=dict(width=2, color='#ffffff')), hovertemplate='%{y} feeds<extra></extra>'), secondary_y=True)
        fig_milk.add_trace(go.Scatter(name='📈 Vol Trend', x=total_per_x[group_col].astype(str), y=total_per_x['Trend'], mode='lines', line=dict(color='#64748b', width=2, shape='spline'), hovertemplate='Avg Trend: %{y:.0f} mL<extra></extra>'), secondary_y=False)
        
        fig_milk = style_plotly_figure(fig_milk, title_text=f"🍼 Milk Intake Volume & Feed Count — {granularity}", height=490, single_point=is_single)
        fig_milk.update_layout(barmode='stack')
        fig_milk.update_yaxes(title_text="", secondary_y=False, showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickfont=dict(size=9.5), automargin=True)
        fig_milk.update_yaxes(title_text="", secondary_y=True, showgrid=False, tickfont=dict(size=9.5), automargin=True)
        st.plotly_chart(fig_milk, use_container_width=True)
        
        st.caption(f"ℹ️ *Combines stacked Formula and Breast Milk volume (mL) on left axis with Feed Count(s) (orange) on right axis. The grey line plots the 7-period rolling average.*", unsafe_allow_html=True)

        avg_vol = total_per_x['Value (Optional)'].mean()
        trend_word = "holding highly stable ⚖️"
        if len(total_per_x) > 3:
             recent_avg = total_per_x['Value (Optional)'].iloc[-3:].mean()
             if recent_avg > avg_vol * 1.05: trend_word = "trending upwards 📈, a great sign of healthy appetite growth"
             elif recent_avg < avg_vol * 0.95: trend_word = "trending slightly downwards 📉 (keep an eye on hydration)"
        render_insight_card(f"Riley's intake averages **{avg_vol:.0f} mL** per {granularity.lower().replace('ly','').replace('all time','period')}. Based on recent logs, her volume is **{trend_word}**.")
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
        
        st.caption(f"ℹ️ *Compares Wet Diapers and Poop counts grouped {granularity.lower()} from {start_date} to {end_date}.*")

        avg_diapers = len(diaper_df) / max(1, (end_date - start_date).days + 1)
        wets = len(diaper_df[diaper_df['Category'] == '💧 Wet Diaper (Cnt)'])
        poops = len(diaper_df[diaper_df['Category'] == '🚽 Poop (Cnt)'])
        render_insight_card(f"You've tracked **{wets}** wet and **{poops}** soiled diapers, averaging **{avg_diapers:.1f}** changes per day. Consistent output is an excellent indicator that Riley is digesting properly!")
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
        
        st.caption(f"ℹ️ *Displays recorded pumping volume (mL) grouped {granularity.lower()} from {start_date} to {end_date}.*")

        avg_pump = pump_df['Value (Optional)'].sum() / max(1, len(pump_df))
        render_insight_card(f"Across **{len(pump_df)}** sessions, the average yield is **{avg_pump:.0f} mL** per session. Maintaining regular pumping intervals is key to sustaining supply.")
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
        
        st.caption(f"ℹ️ *Displays recorded tummy time duration (Mins) grouped {granularity.lower()} from {start_date} to {end_date}.*")

        total_tummy = tummy_df['Value (Optional)'].sum()
        avg_tummy = total_tummy / max(1, len(tummy_df))
        render_insight_card(f"Riley achieved **{total_tummy:.0f} total minutes** of tummy time (averaging **{avg_tummy:.0f}m** per session). Regular sessions are actively building her core and neck strength!")
    else: render_empty_state("No Tummy Time Data Logged in this period")

# ==============================================================================
# TAB 6: GROWTH CHARTS
# ==============================================================================
with tab6:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; text-align: center; margin-bottom: 10px;'><a href='https://www.dh.gov.hk/english/useful/useful_HP_Growth_Chart/files/growth_charts.pdf' target='_blank' style='color: #64748b; text-decoration: none; opacity: 0.8;'>📄 Official HK Growth Charts Reference (PDF)</a></p>", unsafe_allow_html=True)

    who_option = st.radio("Select Growth Chart:", options=["⚖️ Weight", "🏔️ Height", "🐷 Head"], horizontal=True, label_visibility="collapsed")
    
    def get_who_data(gen, met):
        if "Weight" in met:
            if gen == "Boy": return np.array([3.3, 4.5, 5.6, 6.4, 7.0, 7.5, 7.9, 8.3, 8.6, 8.9, 9.2, 9.4, 9.6, 9.9, 10.1, 10.3, 10.5, 10.7, 10.9, 11.1, 11.3, 11.5, 11.8, 12.0, 12.2])
            else: return np.array([3.2, 4.2, 5.1, 5.8, 6.4, 6.9, 7.3, 7.6, 7.9, 8.2, 8.5, 8.7, 8.9, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.9, 11.1, 11.3, 11.5])
        elif "Height" in met:
            if gen == "Boy": return np.array([49.9, 54.7, 58.4, 61.4, 63.9, 65.9, 67.6, 69.2, 70.6, 72.0, 73.3, 74.5, 75.7, 76.9, 78.0, 79.1, 80.2, 81.2, 82.3, 83.2, 84.2, 85.1, 86.0, 86.9, 87.8])
            else: return np.array([49.1, 53.7, 57.1, 59.8, 62.1, 64.0, 65.7, 67.3, 68.7, 70.1, 71.5, 72.8, 74.0, 75.2, 76.4, 77.5, 78.6, 79.7, 80.7, 81.7, 82.7, 83.7, 84.6, 85.5, 86.4])
        else:
            if gen == "Boy": return np.array([34.5, 37.3, 39.1, 40.5, 41.6, 42.6, 43.3, 44.0, 44.6, 45.1, 45.5, 46.0, 46.3, 46.6, 46.9, 47.2, 47.4, 47.6, 47.8, 48.0, 48.2, 48.4, 48.5, 48.7, 48.8])
            else: return np.array([33.9, 36.5, 38.3, 39.5, 40.6, 41.5, 42.2, 42.8, 43.4, 43.8, 44.2, 44.6, 44.9, 45.2, 45.4, 45.7, 45.9, 46.1, 46.3, 46.5, 46.7, 46.9, 47.0, 47.2, 47.3])

    def get_hk_mults(met):
        if "Weight" in met: return (0.80, 0.89, 1.11, 1.20)
        if "Height" in met: return (0.95, 0.975, 1.025, 1.05)
        return (0.96, 0.98, 1.02, 1.04)

    # Use entire dataset for growth charting, bypassing the date filter
    db_keyword = "⚖️ Weight (kg)" if "Weight" in who_option else ("🏔️ Height (cm)" if "Height" in who_option else "🐷 Head Size (cm)")
    who_df = df[df['Event Type'] == db_keyword].copy()
    
    current_date = (datetime.utcnow() + timedelta(hours=tz_offset)).date()
    current_age_mo = (current_date - baby_dob).days / 30.437
    def_start = max(0, int(current_age_mo) - 1)
    def_end = min(24, def_start + 6)
    
    r_c1, r_c2 = st.columns([1, 2], vertical_alignment="center")
    with r_c1: st.markdown("##### 🔎 Select Age View (Months):")
    with r_c2: range_min, range_max = st.slider("", 0, 24, (def_start, def_end), label_visibility="collapsed")
    
    if not who_df.empty:
        who_df = who_df.sort_values('DateTime', ascending=True)
        who_df['Age_Months'] = (pd.to_datetime(who_df['Date']) - pd.to_datetime(baby_dob)).dt.days / 30.437
        who_df = who_df[who_df['Age_Months'] >= 0] 
        
        m_x = np.arange(25)
        p50 = get_who_data(baby_gender, who_option)
        m3, m15, m85, m97 = get_hk_mults(who_option)
        p3, p15, p85, p97 = p50*m3, p50*m15, p50*m85, p50*m97
        
        fine_x = np.linspace(0, 24, 241)
        fine_p97 = np.interp(fine_x, m_x, p97)
        fine_p85 = np.interp(fine_x, m_x, p85)
        fine_p50 = np.interp(fine_x, m_x, p50)
        fine_p15 = np.interp(fine_x, m_x, p15)
        fine_p3 = np.interp(fine_x, m_x, p3)
        
        def estimate_pct(row):
            if row['Age_Months'] > 24: return 50
            local_p50 = np.interp(row['Age_Months'], m_x, p50)
            local_p3 = np.interp(row['Age_Months'], m_x, p3)
            local_p97 = np.interp(row['Age_Months'], m_x, p97)
            z = (row['Value (Optional)'] - local_p50) / ((local_p97 - local_p3) / 3.76)
            return (1 / (1 + np.exp(-1.702 * z))) * 100 
            
        who_df['Est_Pct'] = who_df.apply(estimate_pct, axis=1)

        fig_who = go.Figure()
        unit_str = db_keyword.split('(')[1].replace(')','')
        
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p97, line=dict(width=0), name='97th Pct', hoverinfo='x+y+name', hovertemplate='97th: %{y:.2f} ' + unit_str + '<extra></extra>'))
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p85, fill='tonexty', fillcolor='rgba(14,165,233,0.1)', line=dict(width=0), name='85th Pct', hoverinfo='x+y+name', hovertemplate='85th: %{y:.2f} ' + unit_str + '<extra></extra>'))
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p50, fill='tonexty', fillcolor='rgba(14,165,233,0.25)', line=dict(width=0), name='50th Pct', hoverinfo='x+y+name', hovertemplate='50th: %{y:.2f} ' + unit_str + '<extra></extra>'))
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p15, fill='tonexty', fillcolor='rgba(14,165,233,0.25)', line=dict(width=0), name='15th Pct', hoverinfo='x+y+name', hovertemplate='15th: %{y:.2f} ' + unit_str + '<extra></extra>'))
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p3, fill='tonexty', fillcolor='rgba(14,165,233,0.1)', line=dict(width=0), name='3rd Pct', hoverinfo='x+y+name', hovertemplate='3rd: %{y:.2f} ' + unit_str + '<extra></extra>'))
        
        fig_who.add_trace(go.Scatter(x=fine_x, y=fine_p50, mode='lines', line=dict(color='rgba(2,132,199,0.5)', width=2, dash='dot'), showlegend=False, hoverinfo='skip'))
        
        c_code = COLOR_MAP.get(db_keyword, '#38bdf8')
        
        hover_text = []
        for _, row in who_df.iterrows():
            age, v = row['Age_Months'], row['Value (Optional)']
            lp3, lp15, lp50, lp85, lp97 = [np.interp(age, m_x, arr) for arr in [p3, p15, p50, p85, p97]]
            if v < lp3: pct = "< 3rd"
            elif v < lp15: pct = "3rd-15th"
            elif v < lp50: pct = "15th-50th"
            elif v < lp85: pct = "50th-85th"
            elif v <= lp97: pct = "85th-97th"
            else: pct = "> 97th"
            ht = f"<b>{row['Date']}</b><br><b>Value: {v:.1f} {unit_str}</b><br>Estimated Bracket: ~{pct}<extra></extra>"
            hover_text.append(ht)

        fig_who.add_trace(go.Scatter(
            x=who_df['Age_Months'], y=who_df['Value (Optional)'], mode='lines+markers',
            line=dict(color=c_code, width=3, shape='spline'),
            marker=dict(size=10, color=c_code, line=dict(width=2, color='#ffffff')),
            name=who_option.split(' ')[1],
            text=hover_text,
            hovertemplate="%{text}"
        ))
        
        x_max_buffer = range_max + 1.5
        visible_idx = (fine_x >= range_min) & (fine_x <= x_max_buffer)
        max_p97_vis = np.max(fine_p97[visible_idx])
        min_p3_vis = np.min(fine_p3[visible_idx])
        
        user_vis = who_df[(who_df['Age_Months'] >= range_min) & (who_df['Age_Months'] <= x_max_buffer)]
        u_max = user_vis['Value (Optional)'].max() if not user_vis.empty else max_p97_vis
        u_min = user_vis['Value (Optional)'].min() if not user_vis.empty else min_p3_vis
        
        y_upper = max(max_p97_vis, u_max) * 1.01
        y_lower = min(min_p3_vis, u_min) * 0.99

        fig_who.update_layout(
            title=dict(text=f"📈 {who_option.split(' ')[1]}", y=0.97, x=0.5, xanchor="center", font=dict(size=16)),
            height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=2, r=2, t=60, b=20),
            xaxis=dict(title="Age (Months)", showgrid=True, gridcolor="rgba(128,128,128,0.15)", tickformat=".0f", range=[range_min, x_max_buffer]),
            yaxis=dict(title="", showgrid=True, gridcolor="rgba(128,128,128,0.15)", range=[y_lower, y_upper]),
            showlegend=False, hovermode="x unified"
        )
        st.plotly_chart(fig_who, use_container_width=True)
        
        st.caption(f"ℹ️ *Interactive Growth Chart for {baby_gender}s based on standard HK lines. The shaded bands map the 3rd, 15th, 50th, 85th, and 97th percentiles.*")
        
        latest_data = who_df.iloc[-1]
        latest_pct = latest_data['Est_Pct']
        latest_val = latest_data['Value (Optional)']
        
        if latest_pct > 85: pct_text = "tracking in the higher percentiles 📈"
        elif latest_pct < 15: pct_text = "tracking in the lower percentiles 📉"
        else: pct_text = "tracking beautifully near the median ⚖️"
            
        render_insight_card(f"At **{latest_data['Age_Months']:.1f} months**, Riley's {who_option.split(' ')[1].lower()} is **{latest_val:.1f} {unit_str}** (~**{latest_pct:.0f}th** percentile). She is {pct_text} compared to HK standard guidelines.")
        
    else:
        render_empty_state(f"No {who_option} Data Logged")


# TAB 7: Health Charts
with tab7:
    act_option = st.radio("Select Category:", options=["🛌 Sleep (hrs)", "🌡️ Temp (°C)", "💊 Meds (Cnt)"], index=0, horizontal=True, label_visibility="collapsed")
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
        else: 
            grouped_act = act_df.groupby(group_col).size().reset_index(name='Value (Optional)')
            grouped_act[group_col] = grouped_act[group_col].apply(format_x_label)
            is_single = len(grouped_act[group_col].unique()) == 1
            fig_act = px.bar(grouped_act, x=group_col, y="Value (Optional)", color_discrete_sequence=[act_color], labels={"Value (Optional)": y_title, group_col: granularity})
            if is_single: fig_act.update_traces(width=0.25)
            fig_act.update_traces(hovertemplate=f'%{{y}} {unit}<extra></extra>')
            
        fig_act = style_plotly_figure(fig_act, title_text=f"🩺 Health — {act_option} ({granularity})", height=450, single_point=is_single)
        st.plotly_chart(fig_act, use_container_width=True)
        
        st.caption(f"ℹ️ *Displays recorded {act_option} data grouped {granularity.lower()} from {start_date} to {end_date}.*")

        avg_act = act_df['Value (Optional)'].mean()
        if keyword == "Meds":
             render_insight_card(f"Riley has logged **{len(act_df)}** medication doses in this period. Tracking these logs carefully prevents missed or double doses.")
        else:
             render_insight_card(f"Across **{len(act_df)}** records, Riley averages **{avg_act:.1f} {unit}**. Stable patterns in {act_option.split(' ')[1].lower()} are strong indicators of general wellbeing.")
        
    else: render_empty_state(f"No {act_option.split(' ')[1]} Data Logged in this period")


# TAB 8: Vaccine Milestones & Logs
with tab8:
    vac_df = df[df['Event Type'] == "💉 Vaccine (Cnt)"].copy()
    
    def get_date(keyword_regex, index):
        if vac_df.empty: return None
        matches = vac_df[vac_df['Notes / Details (Optional)'].str.contains(keyword_regex, case=False, na=False)].sort_values('DateTime')
        return matches.iloc[index]['Date'] if index < len(matches) else None

    hkcip_schedule = [
        {"Age": "0 mo", "Days": 0, "Group": "BCG", "Vaccine": "卡介苗 (BCG)", "Disease": "結核病 (Tuberculosis)", "Provider": "🏥 母嬰", "Desc": "預防結核病，初生嬰兒必打", "Optional": False, "Match": get_date("bcg|卡介苗", 0)},
        {"Age": "0 mo", "Days": 0, "Group": "Hepatitis B", "Vaccine": "乙型肝炎 第一劑 (Hep B 1st)", "Disease": "乙型肝炎 (Hepatitis B)", "Provider": "🏥 母嬰", "Desc": "預防乙型肝炎，出世即打", "Optional": False, "Match": get_date("hep|hbv|hexa|6-in|6 in|六合一|乙型肝炎|五合一", 0)},
        {"Age": "1 mo", "Days": 30, "Group": "Hepatitis B", "Vaccine": "乙型肝炎 第二劑 (Hep B 2nd)", "Disease": "乙型肝炎 (Hepatitis B)", "Provider": "🏥 母嬰", "Desc": "滿月時於母嬰健康院接種", "Optional": False, "Match": get_date("hep|hbv|hexa|6-in|6 in|六合一|乙型肝炎|五合一", 1)},
        {"Age": "2 mo", "Days": 60, "Group": "6-in-1 Combo", "Vaccine": "六合一混合 第一劑 (6-in-1 1st)", "Disease": "白喉, 破傷風, 百日咳, 小兒麻痺, 乙肝, 流感嗜血桿菌 (DTaP-IPV-HepB-Hib)", "Provider": "💰 私家 / 🏥 母嬰", "Desc": "私家六合/五合一或母嬰四合一", "Optional": False, "Match": get_date("dtap|hexa|6-in|6 in|5-in|五合一|六合一|四合一|4 in|4-in|pent", 0)},
        {"Age": "2 mo", "Days": 60, "Group": "Pneumococcal", "Vaccine": "肺炎球菌 第一劑 (PCV 1st)", "Disease": "肺炎球菌感染 (Pneumococcal)", "Provider": "🏥 母嬰", "Desc": "預防嚴重肺炎/腦膜炎", "Optional": False, "Match": get_date("pcv|pneumo|肺炎", 0)},
        {"Age": "2 mo", "Days": 60, "Group": "Rotavirus", "Vaccine": "輪狀病毒 第一劑 (Rotavirus 1st)", "Disease": "輪狀病毒腸胃炎 (Rotavirus)", "Provider": "💰 私家", "Desc": "口服疫苗，預防嚴重腸胃炎", "Optional": True, "Match": get_date("rota|輪狀", 0)},
        {"Age": "2 mo", "Days": 60, "Group": "Meningococcal B", "Vaccine": "腦膜炎雙球菌 第一劑 (Men B 1st)", "Disease": "腦膜炎雙球菌感染 (Meningococcal)", "Provider": "💰 私家", "Desc": "預防致命腦膜炎，B型最常見", "Optional": True, "Match": get_date("menb|mening|腦膜炎", 0)},
        {"Age": "4 mo", "Days": 120, "Group": "6-in-1 Combo", "Vaccine": "六合一混合 第二劑 (6-in-1 2nd)", "Disease": "白喉, 破傷風, 百日咳, 小兒麻痺, 乙肝, 流感嗜血桿菌 (DTaP-IPV-HepB-Hib)", "Provider": "💰 私家 / 🏥 母嬰", "Desc": "第二針混合疫苗", "Optional": False, "Match": get_date("dtap|hexa|6-in|6 in|5-in|五合一|六合一|四合一|4 in|4-in|pent", 1)},
        {"Age": "4 mo", "Days": 120, "Group": "Pneumococcal", "Vaccine": "肺炎球菌 第二劑 (PCV 2nd)", "Disease": "肺炎球菌感染 (Pneumococcal)", "Provider": "🏥 母嬰", "Desc": "第二針", "Optional": False, "Match": get_date("pcv|pneumo|肺炎", 1)},
        {"Age": "4 mo", "Days": 120, "Group": "Rotavirus", "Vaccine": "輪狀病毒 第二劑 (Rotavirus 2nd)", "Disease": "輪狀病毒腸胃炎 (Rotavirus)", "Provider": "💰 私家", "Desc": "第二劑口服", "Optional": True, "Match": get_date("rota|輪狀", 1)},
        {"Age": "4 mo", "Days": 120, "Group": "Meningococcal B", "Vaccine": "腦膜炎雙球菌 第二劑 (Men B 2nd)", "Disease": "腦膜炎雙球菌感染 (Meningococcal)", "Provider": "💰 私家", "Desc": "第二針", "Optional": True, "Match": get_date("menb|mening|腦膜炎", 1)},
        {"Age": "6 mo", "Days": 180, "Group": "6-in-1 Combo", "Vaccine": "六合一混合 第三劑 (6-in-1 3rd)", "Disease": "白喉, 破傷風, 百日咳, 小兒麻痺, 乙肝, 流感嗜血桿菌 (DTaP-IPV-HepB-Hib)", "Provider": "💰 私家 / 🏥 母嬰", "Desc": "第三針混合疫苗", "Optional": False, "Match": get_date("dtap|hexa|6-in|6 in|5-in|五合一|六合一|四合一|4 in|4-in|pent", 2)},
        {"Age": "6 mo", "Days": 180, "Group": "Pneumococcal", "Vaccine": "肺炎球菌 第三劑 (PCV 3rd)", "Disease": "肺炎球菌感染 (Pneumococcal)", "Provider": "🏥 母嬰", "Desc": "第三針 (部份情況可省略)", "Optional": False, "Match": get_date("pcv|pneumo|肺炎", 2)},
        {"Age": "6 mo", "Days": 180, "Group": "Rotavirus", "Vaccine": "輪狀病毒 第三劑 (Rotavirus 3rd)", "Disease": "輪狀病毒腸胃炎 (Rotavirus)", "Provider": "💰 私家", "Desc": "視乎藥廠(部份只需兩劑)", "Optional": True, "Match": get_date("rota|輪狀", 2)},
        {"Age": "6 mo", "Days": 180, "Group": "Influenza", "Vaccine": "季節性流感 (Influenza)", "Disease": "流行性感冒 (Flu)", "Provider": "💰 私家 / 🏥 診所", "Desc": "滿6個月可打，每年一針", "Optional": True, "Match": get_date("flu|流感", 0)},
        {"Age": "12 mo", "Days": 365, "Group": "MMR / MMRV", "Vaccine": "麻疹, 流行性腮腺炎, 德國麻疹 第一劑 (MMR 1st)", "Disease": "麻疹, 流行性腮腺炎, 德國麻疹 (Measles, Mumps, Rubella)", "Provider": "🏥 母嬰", "Desc": "一歲滿即打", "Optional": False, "Match": get_date("mmr|麻疹", 0)},
        {"Age": "12 mo", "Days": 365, "Group": "Pneumococcal", "Vaccine": "肺炎球菌 加強劑 (PCV Booster)", "Disease": "肺炎球菌感染 (Pneumococcal)", "Provider": "🏥 母嬰", "Desc": "加強劑", "Optional": False, "Match": get_date("pcv|pneumo|肺炎", 3)},
        {"Age": "12 mo", "Days": 365, "Group": "Varicella", "Vaccine": "水痘 第一劑 (Varicella 1st)", "Disease": "水痘 (Chickenpox)", "Provider": "🏥 母嬰", "Desc": "第一針水痘", "Optional": False, "Match": get_date("varicella|cp|chickenpox|水痘", 0)},
        {"Age": "12 mo", "Days": 365, "Group": "Hepatitis A", "Vaccine": "甲型肝炎 第一劑 (Hep A 1st)", "Disease": "甲型肝炎 (Hepatitis A)", "Provider": "💰 私家", "Desc": "預防受污染食物感染", "Optional": True, "Match": get_date("hepa|hep a|甲型", 0)},
        {"Age": "18 mo", "Days": 547, "Group": "6-in-1 Combo", "Vaccine": "六合一混合 加強劑 (6-in-1 Booster)", "Disease": "白喉, 破傷風, 百日咳, 小兒麻痺, 乙肝, 流感嗜血桿菌 (DTaP-IPV-HepB-Hib)", "Provider": "💰 私家 / 🏥 母嬰", "Desc": "加強保護力", "Optional": False, "Match": get_date("dtap|hexa|6-in|6 in|5-in|五合一|六合一|四合一|4 in|4-in|pent", 3)},
        {"Age": "18 mo", "Days": 547, "Group": "MMR / MMRV", "Vaccine": "MMRV 第二劑 (MMRV 2nd)", "Disease": "麻疹, 流行性腮腺炎, 德國麻疹, 水痘 (Measles, Mumps, Rubella, Chickenpox)", "Provider": "🏥 母嬰", "Desc": "歲半加強劑 (含水痘)", "Optional": False, "Match": get_date("mmrv|mmr|麻疹", 1)},
        {"Age": "18 mo", "Days": 547, "Group": "Hepatitis A", "Vaccine": "甲型肝炎 第二劑 (Hep A 2nd)", "Disease": "甲型肝炎 (Hepatitis A)", "Provider": "💰 私家", "Desc": "隔半年打第二針", "Optional": True, "Match": get_date("hepa|hep a|甲型", 1)},
        {"Age": "3 Years", "Days": 1095, "Group": "Influenza", "Vaccine": "流感疫苗 (Flu Vaccine)", "Disease": "流行性感冒 (Flu)", "Provider": "💰 私家 / 🏥 幼稚園", "Desc": "入學前防護", "Optional": True, "Match": get_date("flu|流感", 1)},
        {"Age": "5-6 Years", "Days": 1825, "Group": "DTaP / 6-in-1", "Vaccine": "白喉,破傷風,百日咳,小兒麻痺 加強劑 (Booster)", "Disease": "白喉, 破傷風, 百日咳, 小兒麻痺 (DTaP-IPV)", "Provider": "🏥 學校", "Desc": "小一學童接種", "Optional": False, "Match": get_date("dtap|ipv|小一|小兒麻痺", 4)},
        {"Age": "5-6 Years", "Days": 1825, "Group": "MMR / MMRV", "Vaccine": "MMRV 加強劑 (MMRV Booster)", "Disease": "麻疹, 流行性腮腺炎, 德國麻疹, 水痘 (MMRV)", "Provider": "🏥 學校", "Desc": "小一學童接種", "Optional": False, "Match": get_date("mmrv|mmr|麻疹", 2)},
        {"Age": "11-12 Years", "Days": 4015, "Group": "DTaP / 6-in-1", "Vaccine": "白喉,破傷風,百日咳 加強劑 (dTap Booster)", "Disease": "白喉, 破傷風, 百日咳 (dTap)", "Provider": "🏥 學校", "Desc": "小六學童接種", "Optional": False, "Match": get_date("dtap|小六|百日咳", 5)},
        {"Age": "11-12 Years", "Days": 4015, "Group": "HPV", "Vaccine": "子宮頸癌疫苗 第一劑 (HPV 1st)", "Disease": "子宮頸癌 (HPV)", "Provider": "🏥 學校", "Desc": "小五/小六女童接種", "Optional": False, "Match": get_date("hpv|子宮", 0)},
        {"Age": "12-15 Years", "Days": 4380, "Group": "HPV", "Vaccine": "子宮頸癌疫苗 第二劑 (HPV 2nd)", "Disease": "子宮頸癌 (HPV)", "Provider": "🏥 學校", "Desc": "第二針", "Optional": False, "Match": get_date("hpv|子宮", 1)},
        {"Age": "36 Years", "Days": 13140, "Group": "Adult", "Vaccine": "成人疫苗加強劑 (Adult Boosters)", "Disease": "百日咳/流感等 (Pertussis, Flu)", "Provider": "💰 私家", "Desc": "成人定期加強", "Optional": True, "Match": get_date("adult|成人", 0)},
    ]
    
    current_date = (datetime.utcnow() + timedelta(hours=tz_offset)).date()
    age_days = (current_date - baby_dob).days
    
    rows = []
    for s in hkcip_schedule:
        if s["Match"]: status = "✅ Done"
        elif 0 < (s["Days"] - age_days) <= 30: status = "🟡 Due Soon"
        elif age_days >= s["Days"]: status = "⚠️ Overdue"
        else: status = "⏳ Upcoming"
        
        v_name_formatted = f"(Optional) {s['Vaccine']}" if s["Optional"] else s["Vaccine"]
        
        rows.append({
            "Age": s["Age"],
            "Group": s["Group"],
            "Disease Prevented": s["Disease"],
            "Vaccine / 疫苗": v_name_formatted,
            "Type": s["Provider"],
            "Description": s["Desc"],
            "Date Injected": str(s["Match"]) if s["Match"] else "-",
            "Status": status,
            "Optional": s["Optional"],
            "Days": s["Days"]
        })
        
    styled_df = pd.DataFrame(rows)
    
    v_col1, v_col2 = st.columns([1, 1])
    with v_col1: grouping = st.radio("Sort View:", ["By Age Milestone", "By Vaccine Type"], horizontal=True, label_visibility="collapsed")
    
    if grouping == "By Vaccine Type":
        styled_df = styled_df.sort_values(by=["Group", "Days"]).reset_index(drop=True)
    else:
        styled_df = styled_df.sort_values(by="Days").reset_index(drop=True)

    def apply_vaccine_colors(row):
        if '✅' in row['Status']: return ['background-color: #dcfce7; color: #166534'] * 7
        elif '🟡' in row['Status']: return ['background-color: #fef08a; color: #854d0e'] * 7
        elif '⚠️' in row['Status']: return ['background-color: #fee2e2; color: #991b1b'] * 7
        elif '(Optional)' in row['Vaccine / 疫苗']: return ['background-color: #f1f5f9; color: #475569'] * 7
        else: return [''] * 7

    dropped_df = styled_df.drop(columns=["Days", "Group", "Optional"])
    styled_table = dropped_df.style.apply(apply_vaccine_colors, axis=1)
    
    st.dataframe(
        styled_table,
        use_container_width=True, hide_index=True, height=550,
        column_config={
            "Vaccine / 疫苗": st.column_config.TextColumn("Vaccine / 疫苗", width="medium"),
            "Disease Prevented": st.column_config.TextColumn("Disease Prevented", width="large"),
            "Description": st.column_config.TextColumn("Description", width="medium")
        }
    )
    
    st.caption("ℹ️ *Auto-matches your logged vaccines by scanning your 'Notes / Details' column for keywords (e.g. 6-in-1, PCV, Rota, BCG).*")
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📋 Riley's Vaccination History Log")
    if not vac_df.empty:
        if 'DateTime' in vac_df.columns:
            vac_df = vac_df.sort_values('DateTime', ascending=False).reset_index(drop=True)
            vac_df['DateTime_Display'] = pd.to_datetime(vac_df['DateTime']).dt.strftime('%Y-%m-%d')
            vac_df['Age at Shot'] = ((pd.to_datetime(vac_df['Date']) - pd.to_datetime(baby_dob)).dt.days / 30.437).round(1).astype(str) + " mo"
        
        desired_cols = ['DateTime_Display', 'Age at Shot', 'Event Type', 'Notes / Details (Optional)']
        display_vac = vac_df[[c for c in desired_cols if c in vac_df.columns]].copy()
        if 'DateTime_Display' in display_vac.columns: display_vac = display_vac.rename(columns={'DateTime_Display': 'Date Injected'})
            
        st.dataframe(
            display_vac, use_container_width=True, hide_index=True, height=350,
            column_config={
                "Date Injected": st.column_config.TextColumn("Date Injected", width="medium"), 
                "Age at Shot": st.column_config.TextColumn("Age at Shot", width="small"),
                "Event Type": st.column_config.TextColumn("Event", width="medium"),
                "Notes / Details (Optional)": st.column_config.TextColumn("Vaccine Type / Notes", width="large")
            }
        )
    else: render_empty_state("No Vaccine Data Logged")

# ==========================================
# 6. EXPANDED DATABASE TABLE (MOVED TO BOTTOM)
# ==========================================
st.markdown('<div id="database" style="padding-top: 3.5rem;"></div>', unsafe_allow_html=True)
st.subheader("📋 Database")

filter_c1, filter_c2 = st.columns([1, 1])
with filter_c1: selected_events = st.multiselect("🏷️ Filter Event Types:", options=ALL_EVENT_CATEGORIES, default=[], placeholder="Choose event types (Leave empty for All)")
with filter_c2: search_query = st.text_input("🔍 Search Anything:", "", placeholder="Type date (e.g. 07-21), Formula, notes...")

table_df = filtered_df.copy()
if selected_events: table_df = table_df[table_df['Event Type'].isin(selected_events)]
if search_query:
    search_mask = table_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1)
    table_df = table_df[search_mask]

if 'DateTime' in table_df.columns:
    table_df = table_df.sort_values('DateTime', ascending=False).reset_index(drop=True)
if 'Value (Optional)' in table_df.columns:
    table_df['Value (Optional)'] = pd.to_numeric(table_df['Value (Optional)'], errors='coerce')
if 'DateTime' in table_df.columns:
    table_df['DateTime_Display'] = table_df['DateTime']

desired_cols = ['DateTime_Display', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)', 'Date', 'Week', 'Month']
actual_cols = [c for c in desired_cols if c in table_df.columns or c == 'DateTime_Display']
display_df = table_df[actual_cols].copy()
if 'DateTime_Display' in display_df.columns: display_df = display_df.rename(columns={'DateTime_Display': 'DateTime'})

if not display_df.empty:
    if 'Date' in display_df.columns: display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
    if 'Week' in display_df.columns: display_df['Week'] = pd.to_datetime(display_df['Week']).dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        display_df, use_container_width=True, height=490,
        column_config={
            "DateTime": st.column_config.DatetimeColumn("DateTime", format="YYYY-MM-DD HH:mm", width="medium"),
            "Event Type": st.column_config.TextColumn("Event Type", width="medium"),
            "Value (Optional)": st.column_config.NumberColumn("Value", width="small"),
            "Notes / Details (Optional)": st.column_config.TextColumn("Notes / Details (Optional)", width="large"),
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Week": st.column_config.TextColumn("Week", width="small"),
            "Month": st.column_config.TextColumn("Month", width="small")
        }
    )
    st.markdown(f'<div class="raw-log-count-text">Showing {len(display_df)} entry(s) matching your criteria sorted in descending order.</div>', unsafe_allow_html=True)
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")

st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)
