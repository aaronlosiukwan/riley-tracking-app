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

# Inject Apple Touch Icon & Refresh Logic
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
        function setupRefreshLogic(doc, win) {
            if (!win.triggerRefresh) {
                win.triggerRefresh = function(element) {
                    element.innerHTML = '⏳ Fetching...';
                    win.sessionStorage.setItem('reloaded', 'true');
                    
                    // Intuitive "Refreshing..." Toast Notification (Moved down to avoid Streamlit header)
                    let refreshToast = doc.createElement('div');
                    refreshToast.innerHTML = '⏳ Refreshing data...';
                    refreshToast.style.cssText = 'position: fixed; top: 80px; right: 20px; background: #fffbeb; color: #854d0e; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-weight: 600; z-index: 9999999; border: 1px solid #fde047; font-family: sans-serif; transition: opacity 0.2s ease;';
                    doc.body.appendChild(refreshToast);
                    
                    // Wait 600ms so the user has time to actually read the toast before reload
                    setTimeout(() => { win.location.reload(true); }, 600);
                };
            }
            if (win.sessionStorage.getItem('reloaded')) {
                win.sessionStorage.removeItem('reloaded');
                
                // Pop up Notification for "Data successfully updated"
                let toast = doc.createElement('div');
                toast.innerHTML = '✅ Data successfully updated!';
                toast.style.cssText = 'position: fixed; top: 80px; right: 20px; background: #dcfce7; color: #166534; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-weight: 600; z-index: 9999999; opacity: 0; transition: opacity 0.4s ease; border: 1px solid #86efac; font-family: sans-serif;';
                doc.body.appendChild(toast);
                setTimeout(() => { toast.style.opacity = '1'; }, 100);
                setTimeout(() => { 
                    toast.style.opacity = '0'; 
                    setTimeout(() => toast.remove(), 500);
                }, 3000);

                let attempts = 0;
                const interval = setInterval(() => {
                    const btns = doc.querySelectorAll('.refresh-btn');
                    if (btns.length > 0) {
                        btns.forEach(btn => {
                            btn.innerHTML = '🔄 Refresh'; 
                            btn.style.backgroundColor = '';
                            btn.style.borderColor = '';
                        });
                        clearInterval(interval);
                    }
                    attempts++;
                    if (attempts > 20) clearInterval(interval);
                }, 100);
            }
        }
        try { applyAppleIcon(document); } catch(e) {}
        try { applyAppleIcon(window.parent.document); setupRefreshLogic(window.parent.document, window.parent); } catch(e) {}
        try { applyAppleIcon(window.top.document); setupRefreshLogic(window.top.document, window.top); } catch(e) {}
    })();
    </script>
    """,
    height=0,
    width=0
)

# Responsive & Adaptive CSS
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

    /* Title Styling - Enforced much larger than subheaders but wraps cleanly on tiny mobile screens */
    .app-main-title {
        font-size: clamp(1.4rem, 5vw + 0.5rem, 2.4rem) !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        white-space: normal !important; /* Allows wrapping instead of cutting off */
        padding-right: 45px; /* Protects from Streamlit's hamburger menu overlapping */
        color: var(--card-text);
        margin: 0;
    }

    /* Custom Header Buttons - Locked 44px Height & Equal Widths */
    .custom-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: var(--card-bg) !important; color: #1e293b !important;
        border: 1px solid var(--card-border); box-shadow: var(--card-shadow);
        border-radius: 8px; height: 44px !important; min-height: 44px !important; 
        font-size: 0.9rem !important; font-weight: 500;
        text-decoration: none !important; transition: all 0.15s ease; box-sizing: border-box;
    }
    .custom-btn:active { background-color: #f1f5f9 !important; transform: scale(0.98); }

    /* Flawless HTML Desktop/Mobile Header Layouts */
    @media (min-width: 769px) {
        .custom-header-mobile { display: none !important; }
        .custom-header-desktop { display: block !important; margin-top: 1.5rem; margin-bottom: 1.0rem; }
        .desktop-header-row { display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 100%; }
        .desktop-header-controls { display: flex; gap: 0.5rem; }
        .desktop-header-controls .custom-btn { width: 130px; padding: 0; } /* Strict identical widths on desktop */
    }

    @media (max-width: 768px) {
        .custom-header-desktop { display: none !important; }
        /* Pushed down and robust bottom margin to prevent overlap */
        .custom-header-mobile { display: block !important; width: 100%; margin-top: 1.5rem; margin-bottom: 2.0rem !important; }
        .mobile-header-controls { display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 100%; gap: 0.5rem; }
        .mobile-header-controls .custom-btn { flex: 1; text-align: center; } /* 50/50 flex split on mobile */
    }

    span[data-baseweb="tag"] { background-color: #e5e7eb !important; color: #1f2937 !important; border: 1px solid #d1d5db !important; font-weight: 500 !important; }
    
    /* Perfect Navigation Button Spacing */
    .toc-button { 
        display: block; width: 100%; padding: 10px 14px; margin: 8px 0; 
        background-color: var(--card-bg); border: 1px solid var(--card-border); 
        box-shadow: var(--card-shadow); color: var(--card-text) !important; 
        text-decoration: none !important; border-radius: 8px; font-size: 0.95rem; 
        font-weight: 500; transition: all 0.15s ease-in-out; 
    }
    .toc-button:hover { background-color: #f1f5f9; border-color: #cbd5e1; text-decoration: none !important; }
    
    .sidebar-header { font-weight: 700; font-size: 1.05rem; margin-bottom: 8px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px; margin-top: 32px; }

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
# RESPONSIVE HEADER SECTION
# ---------------------------------------------------------
st.markdown("""
<div class="custom-header-desktop">
    <div class="desktop-header-row">
        <div class="app-main-title">🍼 Riley's Dash</div>
        <div class="desktop-header-controls">
            <a href="shortcuts://run-shortcut?name=Riley%20Tracker" class="custom-btn">➕ Add</a>
            <a href="javascript:void(0);" onclick="window.triggerRefresh ? window.triggerRefresh(this) : window.location.reload(true);" class="custom-btn refresh-btn">🔄 Refresh</a>
        </div>
    </div>
</div>
<div class="custom-header-mobile">
    <div class="app-main-title" style="margin-bottom: 0.8rem;">🍼 Riley's Dash</div>
    <div class="mobile-header-controls">
        <a href="shortcuts://run-shortcut?name=Riley%20Tracker" class="custom-btn">➕ Add</a>
        <a href="javascript:void(0);" onclick="window.triggerRefresh ? window.triggerRefresh(this) : window.location.reload(true);" class="custom-btn refresh-btn">🔄 Refresh</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR TABLE OF CONTENTS & GSHEET SETTINGS
# ==========================================
st.sidebar.markdown("""
    <div style="margin-bottom: 20px;">
        <div class="sidebar-header" style="margin-top: 0;">📌 Quick Navigation</div>
        <a href="#today" class="toc-button">✨ Today</a>
        <a href="#period-highlights" class="toc-button">📅 Range Highlights</a>
        <a href="#insights" class="toc-button">📊 Insights</a>
        <a href="#database" class="toc-button">📋 Database</a>
    </div>
""", unsafe_allow_html=True)

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"

st.sidebar.markdown('<hr style="margin: 20px 0; opacity: 0.2;">', unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-header' style='margin-top: 0;'>⚙️ Configuration</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True) 
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL)
tz_offset = st.sidebar.number_input("Timezone Offset (UTC Hours)", value=8, step=1)

if sheet_url_input: st.sidebar.link_button("🔗 Open Google Sheet Directly", sheet_url_input, use_container_width=True)

st.sidebar.markdown('<hr style="margin: 20px 0; opacity: 0.2;">', unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-header' style='margin-top: 0;'>👶 Baby Settings</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True) 
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
    <div style="background-color: #f8fafc; border-left: 4px solid #8b5cf6; padding: 12px 16px; border-radius: 8px; margin: 16px 0 24px 0; font-size: 0.88rem; color: #334155; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
        <strong style="color: #6d28d9;">✨ AI Insight:</strong> {html_text}
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. EXPANDABLE FILTERS & GROUPING
# ==========================================
min_str = min_data_date.strftime('%m.%d')
max_str = max_data_date.strftime('%m.%d')

if 'sd' not in st.session_state: 
    st.session_state.sd = max(min_data_date, max_data_date - timedelta(days=20))
if 'ed' not in st.session_state: 
    st.session_state.ed = max_data_date

cur_sd = st.session_state.sd
cur_ed = st.session_state.ed

with st.expander("⚙️ Filter & Grouping Settings", expanded=False):
    st.markdown(f"<div style='color: #64748b; font-size: 0.9rem; margin-top: 0.2rem; margin-bottom: 1.2rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(128,128,128,0.15); font-weight: 500;'>Data Aggregated from <span style='color: #334155;'>{cur_sd.strftime('%Y-%m-%d')}</span> to <span style='color: #334155;'>{cur_ed.strftime('%Y-%m-%d')}</span></div>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
    with f_col1:
        granularity = st.radio("Chart Grouping:", ["Daily", "Weekly", "Monthly", "All Time"], index=0, horizontal=True)
        range_hints = {"Daily": "Default: Last 21 Days", "Weekly": "Default: Last 8 Weeks", "Monthly": "Default: Last 6 Months", "All Time": "Default: Full Data Range"}
        st.markdown(f"<span class='default-range-text'>ℹ️ {range_hints[granularity]}</span>", unsafe_allow_html=True)
    
    def set_all_data():
        st.session_state.sd = min_data_date
        st.session_state.ed = max_data_date

    with f_col2: st.date_input("Start Date (Inclusive)", min_value=min_data_date, max_value=max_data_date, key="sd")
    with f_col3: st.date_input("End Date (Inclusive)", min_value=min_data_date, max_value=max_data_date, key="ed")
    
    st.button("🗓️ Select All Data Range", on_click=set_all_data, use_container_width=True)

start_date = st.session_state.sd
end_date = st.session_state.ed
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


# --- A. TODAY'S HIGHLIGHTS ---
st.markdown('<div id="today" style="padding-top: 3.0rem;"></div>', unsafe_allow_html=True)
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
    st.markdown(f'<div class="cards-container" style="margin-top: 10px !important;">{"".join(formatted_today_cards)}</div>', unsafe_allow_html=True)


# --- B. RANGE HIGHLIGHTS ---
st.markdown('<div id="period-highlights" style="padding-top: 3.0rem;"></div>', unsafe_allow_html=True)
st.subheader("📅 Range Highlights")

if filtered_df.empty:
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">📋 No Data Logged in this Period</div><div class="empty-data-sub">Expand date range to view aggregate highlights.</div></div>""", unsafe_allow_html=True)
else:
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
    p_temp_df = filtered_df[filtered_df['Event Type'].str.contains("Temp", case=False, na=False)]
    p_latest_temp = p_temp_df.iloc[0]['Value (Optional)'] if not p_temp_df.empty else None
    p_pump_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    p_tummy

