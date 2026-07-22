import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# WHO GROWTH STANDARDS (0-24 MONTHS)
# ==========================================
WHO_DATA = {
    "Boy": {
        "Weight": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [2.9, 3.9, 4.9, 5.7, 6.2, 7.1, 7.7, 8.2, 8.6, 9.2, 9.8, 10.8],
            "P25": [3.1, 4.2, 5.3, 6.1, 6.7, 7.5, 8.2, 8.7, 9.2, 9.8, 10.4, 11.5],
            "P50": [3.3, 4.5, 5.6, 6.4, 7.0, 7.9, 8.6, 9.2, 9.6, 10.3, 10.9, 12.2],
            "P75": [3.7, 4.9, 6.0, 6.9, 7.5, 8.4, 9.2, 9.8, 10.3, 11.0, 11.7, 13.0],
            "P90": [3.9, 5.3, 6.5, 7.4, 8.0, 9.0, 9.8, 10.4, 10.9, 11.7, 12.4, 13.8]
        },
        "Height": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [48.0, 52.8, 56.4, 59.4, 61.8, 65.5, 68.4, 71.0, 73.4, 76.6, 79.6, 84.8],
            "P25": [48.9, 53.7, 57.3, 60.4, 62.8, 66.5, 69.5, 72.1, 74.6, 77.9, 80.9, 86.2],
            "P50": [49.9, 54.7, 58.4, 61.4, 63.9, 67.6, 70.6, 73.3, 75.7, 79.1, 82.3, 87.8],
            "P75": [50.8, 55.7, 59.5, 62.5, 65.0, 68.7, 71.8, 74.5, 77.0, 80.4, 83.6, 89.3],
            "P90": [51.8, 56.7, 60.4, 63.5, 66.1, 69.8, 72.9, 75.6, 78.1, 81.7, 85.0, 90.8]
        },
        "Head Size": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [33.1, 35.8, 37.6, 38.9, 40.0, 41.7, 42.9, 43.8, 44.6, 45.4, 46.0, 47.0],
            "P25": [33.8, 36.5, 38.3, 39.7, 40.7, 42.5, 43.7, 44.6, 45.4, 46.2, 46.9, 47.9],
            "P50": [34.5, 37.3, 39.1, 40.5, 41.5, 43.3, 44.5, 45.4, 46.1, 47.0, 47.7, 48.8],
            "P75": [35.2, 38.0, 39.9, 41.3, 42.4, 44.2, 45.4, 46.3, 47.0, 47.9, 48.6, 49.7],
            "P90": [35.8, 38.7, 40.6, 42.0, 43.1, 44.9, 46.2, 47.0, 47.8, 48.7, 49.4, 50.5]
        }
    },
    "Girl": {
        "Weight": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [2.8, 3.6, 4.5, 5.2, 5.7, 6.5, 7.0, 7.5, 7.9, 8.5, 9.1, 10.2],
            "P25": [3.0, 4.0, 4.9, 5.7, 6.2, 7.1, 7.7, 8.2, 8.6, 9.3, 9.8, 10.9],
            "P50": [3.2, 4.2, 5.1, 5.8, 6.4, 7.3, 7.9, 8.5, 8.9, 9.6, 10.2, 11.5],
            "P75": [3.5, 4.6, 5.6, 6.4, 7.0, 7.9, 8.6, 9.2, 9.7, 10.4, 11.1, 12.5],
            "P90": [3.7, 4.9, 6.0, 6.8, 7.5, 8.5, 9.3, 9.9, 10.4, 11.2, 12.0, 13.5]
        },
        "Height": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [47.3, 51.7, 55.0, 57.7, 59.9, 63.5, 66.4, 69.0, 71.4, 74.8, 78.0, 83.6],
            "P25": [48.2, 52.7, 56.0, 58.7, 61.0, 64.6, 67.6, 70.3, 72.8, 76.2, 79.4, 85.1],
            "P50": [49.1, 53.7, 57.1, 59.8, 62.1, 65.7, 68.7, 71.5, 74.0, 77.5, 80.7, 86.4],
            "P75": [50.1, 54.8, 58.2, 60.9, 63.2, 66.9, 70.0, 72.8, 75.4, 78.9, 82.2, 88.0],
            "P90": [51.0, 55.8, 59.3, 62.0, 64.3, 68.1, 71.2, 74.0, 76.7, 80.3, 83.6, 89.5]
        },
        "Head Size": {
            "M": [0, 1, 2, 3, 4, 6, 8, 10, 12, 15, 18, 24],
            "P10": [32.7, 35.1, 37.0, 38.2, 39.2, 40.7, 41.9, 42.7, 43.5, 44.3, 45.0, 46.1],
            "P25": [33.3, 35.8, 37.7, 39.0, 40.0, 41.5, 42.7, 43.6, 44.4, 45.2, 45.9, 47.0],
            "P50": [33.9, 36.5, 38.3, 39.8, 40.6, 42.2, 43.4, 44.4, 45.2, 46.1, 46.8, 48.0],
            "P75": [34.5, 37.2, 39.0, 40.5, 41.3, 43.0, 44.2, 45.2, 46.0, 46.9, 47.7, 48.9],
            "P90": [35.1, 37.9, 39.8, 41.2, 42.0, 43.7, 45.0, 46.0, 46.8, 47.8, 48.5, 49.7]
        }
    }
}

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley's Growth Tracker",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Apple Touch Icon, Refresh Logic, and JS Handlers
components.html(
    """
    <script>
    (function() {
        // 1. Apple Touch Icon Injection
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
        
        // 2. Refresh Button Interactive Logic
        function setupRefreshLogic(doc, win) {
            if (!win.triggerRefresh) {
                win.triggerRefresh = function(element) {
                    element.innerHTML = '⏳ Refreshing...';
                    win.sessionStorage.setItem('reloaded', 'true');
                    // Timeout ensures state renders visually before blocking reload 
                    setTimeout(() => { win.location.reload(true); }, 200);
                };
            }
            
            // If page just loaded from a refresh, show 'Done!' for 2 seconds
            if (win.sessionStorage.getItem('reloaded')) {
                win.sessionStorage.removeItem('reloaded');
                let attempts = 0;
                const interval = setInterval(() => {
                    const btns = doc.querySelectorAll('.refresh-btn');
                    if (btns.length > 0) {
                        btns.forEach(btn => {
                            btn.innerHTML = '✅ Done!';
                            btn.style.backgroundColor = '#dcfce7'; 
                            btn.style.borderColor = '#86efac';
                            setTimeout(() => { 
                                btn.innerHTML = '🔄 Refresh'; 
                                btn.style.backgroundColor = '';
                                btn.style.borderColor = '';
                            }, 2000);
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
    /* Hide Streamlit Default Branding while preserving Sidebar Header Toggle Button */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Smooth Scroll & Anchor Offsets */
    html {
        scroll-behavior: smooth;
    }
    [id] {
        scroll-margin-top: 70px;
    }

    /* Ultimate Native iOS Tap-to-Top Scroll Fix: Force the document body to be the main scroll element */
    html, body {
        height: auto !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        height: auto !important;
        min-height: auto !important;
        overflow: visible !important;
        position: static !important;
    }

    /* Compact Vertical Spacing Across Blocks & Expanders */
    div[data-testid="stVerticalBlock"] {
        gap: 0.35rem !important;
    }
    
    div[data-testid="stExpander"] {
        margin-bottom: 0.15rem !important;
        border-radius: 10px !important;
    }

    /* Locked Light Mode Theme Variables */
    :root {
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        --card-text: #1e293b;
    }

    /* Force global text color to dark for light mode */
    body, .stApp {
        color: var(--card-text) !important;
        background-color: #f8fafc !important;
    }

    /* Seamless background for Safari translucency */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important; 
    }
    
    /* Safari scrolling clearance */
    [data-testid="stMainBlockContainer"] {
        padding-top: calc(3.5rem + env(safe-area-inset-top)) !important;
        padding-bottom: calc(8rem + env(safe-area-inset-bottom)) !important;
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

    /* ------------------------------------------------------------------------
       Pure HTML/CSS Responsive Header Configuration (Bypasses Streamlit Columns)
       ------------------------------------------------------------------------ */
    
    /* Global Custom Button Styles (Looks exactly like Streamlit buttons) */
    .custom-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: var(--card-bg) !important;
        color: #1e293b !important;
        border: 1px solid var(--card-border);
        box-shadow: var(--card-shadow);
        border-radius: 8px;
        height: 2.1rem;
        font-size: 0.85rem;
        font-weight: 500;
        text-decoration: none !important;
        transition: all 0.15s ease;
        box-sizing: border-box;
    }
    .custom-btn:active {
        background-color: #f1f5f9 !important;
        transform: scale(0.98);
    }

    /* Desktop View Layout */
    @media (min-width: 769px) {
        .custom-header-mobile { display: none !important; }
        .custom-header-desktop { display: block !important; }
        
        .desktop-header-row {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }
        .desktop-header-controls {
            display: flex;
            gap: 0.5rem;
        }
        .desktop-header-controls .custom-btn {
            padding: 0 0.8rem;
        }
    }

    /* Mobile View Layout - Forces absolute 50/50 split on the buttons */
    @media (max-width: 768px) {
        .custom-header-desktop { display: none !important; }
        .custom-header-mobile { display: block !important; width: 100%; }
        
        .mobile-header-controls {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 0.5rem;
        }
        .mobile-header-controls .custom-btn {
            flex: 1; /* Forces both buttons to split width exactly 50/50 */
            text-align: center;
        }
    }
    /* ------------------------------------------------------------------------ */

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
    .toc-button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
        text-decoration: none !important;
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

    /* CSS Grid Container: 12-Column System for Absolute Desktop/Mobile Math Layouts */
    .cards-container {
        display: grid !important;
        grid-template-columns: repeat(12, 1fr) !important;
        gap: 8px !important;
        align-items: stretch !important;
        margin-bottom: 2px !important;
        width: 100% !important;
    }

    /* Desktop View Span Logic */
    .card-span-3 { grid-column: span 3 !important; } /* 4 per row */
    .card-span-4 { grid-column: span 4 !important; } /* 3 per row */
    .card-span-6 { grid-column: span 6 !important; } /* 2 per row */
    .card-span-12 { grid-column: span 12 !important; } /* 1 per row */

    /* Mobile View Overrides (<= 1024px) */
    @media (max-width: 1024px) {
        /* Default mobile is strictly 2 per row (span 6) */
        .card-span-3, .card-span-4 { grid-column: span 6 !important; }
        
        /* Forces odd-numbered cards like 'Last Feeding' to span the full mobile screen */
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

    .highlight-title {
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 3px;
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.2;
        color: var(--card-text);
    }
    .highlight-body {
        font-size: 0.84rem;
        opacity: 0.92;
        line-height: 1.25;
        word-break: break-word;
        color: var(--card-text);
    }
    .highlight-sub {
        font-size: 0.74rem;
        opacity: 0.75;
        margin-top: 3px;
        line-height: 1.25;
        word-break: break-word;
        color: var(--card-text);
    }

    /* Grey default range indicator text */
    .default-range-text {
        color: #64748b;
        font-size: 0.8rem;
        font-style: italic;
        margin-top: 1px;
        display: inline-block;
    }

    /* Substantially reduced row count font size in Raw Data Log */
    .raw-log-count-text {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 3px;
        margin-bottom: 6px;
    }

    /* Empty state notice */
    .empty-data-card {
        background-color: var(--card-bg);
        border: 1.5px dashed var(--card-border);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 6px 0;
        color: var(--card-text);
    }
    .empty-data-title {
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 3px;
    }
    .empty-data-sub {
        font-size: 0.8rem;
        opacity: 0.75;
    }

    /* Disable chart interaction on mobile to preserve touch scrolling */
    @media (max-width: 768px) {
        div[data-testid="stPlotlyChart"] {
            position: relative !important;
        }
        div[data-testid="stPlotlyChart"] iframe {
            pointer-events: none !important;
        }
        div[data-testid="stPlotlyChart"]::after {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: 99; /* Allows dropdown portals to overlay */
            background: rgba(0,0,0,0);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Anchor
st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# RESPONSIVE HEADER SECTION (PURE HTML/CSS)
# ---------------------------------------------------------

# Desktop Header Structure
st.markdown("""
<div class="custom-header-desktop" style="margin-bottom: 0.8rem;">
    <div class="desktop-header-row">
        <div class="app-main-title">🍼 Riley's Growth Tracker</div>
        <div class="desktop-header-controls">
            <a href="shortcuts://run-shortcut?name=Riley%20Tracker" class="custom-btn">➕ Add</a>
            <a href="javascript:void(0);" onclick="window.triggerRefresh ? window.triggerRefresh(this) : window.location.reload(true);" class="custom-btn refresh-btn">🔄 Refresh</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mobile Header Structure 
st.markdown("""
<div class="custom-header-mobile" style="margin-bottom: 0.8rem;">
    <div class="app-main-title" style="margin-bottom: 0.6rem;">🍼 Riley's Growth Tracker</div>
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

sheet_url_input = st.sidebar.text_input(
    "Google Sheet URL",
    value=DEFAULT_SHEET_URL,
    help="Auto-synced to your master spreadsheet."
)

tz_offset = st.sidebar.number_input(
    "Timezone Offset (UTC Hours)",
    value=8,
    step=1,
    help="Adjust if 'Last Feed' elapsed time is offset. +8 for HKT/SGT, -5 for EST."
)

if sheet_url_input:
    st.sidebar.link_button("🔗 Open Google Sheet Directly", sheet_url_input, use_container_width=True)

st.sidebar.markdown('<hr style="margin: 10px 0; opacity: 0.2;">', unsafe_allow_html=True)

# Baby settings for precise WHO Charts & Milestone calculations
st.sidebar.header("👶 Baby Settings")
baby_gender = st.sidebar.radio("Gender (For WHO Charts)", ["Boy", "Girl"], horizontal=True)

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

# Real-time auto sync fetcher (1-second cache guarantees reload triggers fresh data)
@st.cache_data(ttl=1)
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

max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

# Add Baby DOB explicitly in sidebar (defaulting to the first recorded event date)
baby_dob = st.sidebar.date_input("Birth Date", value=min_data_date)

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
    "🍼 Formula (mL)",
    "🤱 Breast Milk (mL)",
    "💧 Wet Diaper (Cnt)",
    "🚽 Poop (Cnt)",
    "🧴 Pumping (mL)",
    "🛟 Tummy Time (Mins)",
    "🛌 Sleep (hrs)",
    "🌡️ Temp (°C)",
    "💊 Meds (Cnt)",
    "⚖️ Weight (kg)",
    "🏔️ Height (cm)",
    "🐷 Head Size (cm)",
    "💉 Vaccine (Cnt)",
    "Other"
]

COLOR_MAP = {
    "🍼 Formula (mL)": "#38bdf8",      # Sky Blue
    "🤱 Breast Milk (mL)": "#9ca3af",  # Grey
    "💧 Wet Diaper (Cnt)": "#0284c7",   # Ocean Cyan
    "🚽 Poop (Cnt)": "#d97706",         # Warm Amber
    "🧴 Pumping (mL)": "#a855f7",       # Purple
    "🛟 Tummy Time (Mins)": "#10b981", # Emerald Green
    "🛌 Sleep (hrs)": "#6366f1",        # Indigo
    "🌡️ Temp (°C)": "#ef4444",         # Crimson
    "💊 Meds (Cnt)": "#f59e0b",         # Bright Amber
    "⚖️ Weight (kg)": "#14b8a6",        # Teal
    "🏔️ Height (cm)": "#0ea5e9",        # Light Blue
    "🐷 Head Size (cm)": "#ec4899",     # Pink
    "💉 Vaccine (Cnt)": "#f43f5e",      # Rose/Red
    "Other": "#6b7280"
}

# Helper to format x-axis strings into m.DD format
def format_x_label(val):
    try:
        dt = pd.to_datetime(val)
        return dt.strftime('%m.%d')
    except Exception:
        return str(val)

# Compact Plotly Styling Helper displaying EVERY DATE on X-Axis with Unbolded Titles
def style_plotly_figure(fig, title_text="", height=460, single_point=False, is_scatter=False, x_tickformat=None, x_dtick=None, y_tickangle=None):
    layout_args = dict(
        title=dict(
            text=title_text,
            y=0.97,
            x=0.5,
            xanchor="center",
            yanchor="top",
            font=dict(size=16, weight="normal") # Enlarged unbolded title font
        ),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=2, r=2, t=75, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title_text="",
            font=dict(size=10)
        ),
        font=dict(family="sans-serif", size=11),
        xaxis=dict(
            type=None if is_scatter else "category",
            tickformat=x_tickformat if x_tickformat else None,
            dtick=x_dtick if x_dtick else None,
            title=dict(text=""), # Removed axis title labels like "DateTime" or "Daily"
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
            tickfont=dict(size=9.5),
            automargin=True
        ),
        yaxis=dict(
            title=dict(text=""), # Stripped y-axis title label
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
            tickfont=dict(size=9.5),
            tickangle=y_tickangle if y_tickangle is not None else 0,
            title_standoff=2,
            automargin=True
        ),
        hovermode="closest"
    )
    if single_point:
        layout_args["bargap"] = 0.75
    fig.update_layout(**layout_args)
    return fig

# Robust helper guaranteeing strictly numeric Bubble Sizes with zero NaNs
def prepare_normalized_timeline_df(input_df):
    if input_df.empty:
        return input_df
    
    res_df = input_df.copy()
    res_df['Value_Clean'] = pd.to_numeric(res_df['Value (Optional)'], errors='coerce').fillna(1.0)
    
    groups = []
    for _, group in res_df.groupby('Event Type'):
        g = group.copy()
        vals = g['Value_Clean'].values
        min_v, max_v = np.nanmin(vals), np.nanmax(vals)
        if max_v == min_v or np.isnan(max_v) or np.isnan(min_v):
            g['CategoryBubbleSize'] = 10.0
        else:
            g['CategoryBubbleSize'] = 8.0 + (vals - min_v) / (max_v - min_v) * 6.0
        groups.append(g)
        
    if groups:
        res_df = pd.concat(groups, axis=0)
    else:
        res_df['CategoryBubbleSize'] = 10.0
        
    res_df['CategoryBubbleSize'] = res_df['CategoryBubbleSize'].fillna(10.0)
    return res_df

# ==========================================
# 3. EXPANDABLE FILTERS & GROUPING
# ==========================================
min_str = min_data_date.strftime('%m.%d')
max_str = max_data_date.strftime('%m.%d')

with st.expander("⚙️ Filter & Grouping Settings", expanded=False):
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
        st.markdown(f"<span class='default-range-text'>Min Date: {min_str}</span>", unsafe_allow_html=True)
    with f_col3:
        end_date = st.date_input("End Date (Inclusive)", max_data_date, min_value=min_data_date, max_value=max_data_date)
        st.markdown(f"<span class='default-range-text'>Max Date: {max_str}</span>", unsafe_allow_html=True)

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

# --- Accurate Current Time and Last Feed Metrics Calculation ---
utc_now = datetime.utcnow()
current_local_time = utc_now + timedelta(hours=tz_offset)

all_feed_events = df[df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]
if not all_feed_events.empty:
    last_feed_row = all_feed_events.iloc[0]
    last_feed_dt = last_feed_row['DateTime']
    
    time_diff = current_local_time - last_feed_dt
    total_seconds = int(time_diff.total_seconds())
    
    if total_seconds < 0:
        current_local_time = last_feed_dt
        total_seconds = 0

    hrs_since = total_seconds // 3600
    mins_since = (total_seconds % 3600) // 60
    
    last_feed_time_str = last_feed_dt.strftime('%b %d, %H:%M')
    if hrs_since >= 24:
        last_feed_delta = f"{hrs_since // 24}d {hrs_since % 24}h ago"
    elif hrs_since > 0:
        last_feed_delta = f"{hrs_since}h {mins_since}m ago"
    else:
        last_feed_delta = f"{mins_since}m ago"
    
    # Get last recorded formula and breast milk volumes separately
    last_f_df = df[df['Event Type'].str.contains("Formula", case=False, na=False)]
    last_bm_df = df[df['Event Type'].str.contains("Breast Milk", case=False, na=False)]
    
    f_str = f"{int(last_f_df.iloc[0]['Value (Optional)'])} mL" if not last_f_df.empty else "-"
    bm_str = f"{int(last_bm_df.iloc[0]['Value (Optional)'])} mL" if not last_bm_df.empty else "-"
    
    # Clean subtext strictly under recorded time
    last_feed_sub = f"Recorded: {last_feed_time_str}<br>🍼 Form: {f_str} | 🤱 BM: {bm_str}"
else:
    last_feed_delta = "N/A"
    last_feed_sub = "No feed events"

# --- A. TODAY'S HIGHLIGHTS ---
st.markdown('<div id="today-highlights"></div>', unsafe_allow_html=True)

today_date = max(current_local_time.date(), max_data_date)
today_df = df[df['Date'] == today_date]

formatted_today_code = today_date.strftime('%m.%d')

# Today's highlights wrapped in a toggled expander box (default open)
with st.expander(f"✨ Today [{formatted_today_code}]", expanded=True):
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

    # Build Active Cards list for Today
    today_cards = []

    today_cards.append(f"""<div class="highlight-card card-feed">
    <div>
        <div class="highlight-title">⏰ Last Feeding</div>
        <div class="highlight-body"><b>{last_feed_delta}</b></div>
    </div>
    <div class="highlight-sub">{last_feed_sub}</div>
</div>""")

    if t_milk > 0 or t_feed_cnt > 0:
        today_cards.append(f"""<div class="highlight-card card-milk">
    <div>
        <div class="highlight-title">🍼 Milk Intake</div>
        <div class="highlight-body">Total <b>{int(t_milk):,} mL</b> across <b>{t_feed_cnt}</b> feed(s).</div>
    </div>
    <div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Form: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div>
</div>""")

    if t_wet + t_poop > 0:
        today_cards.append(f"""<div class="highlight-card card-diaper">
    <div>
        <div class="highlight-title">🚽 Diaper Output</div>
        <div class="highlight-body">Total <b>{t_wet + t_poop}</b> change(s) logged.</div>
    </div>
    <div class="highlight-sub">💧 Wet: {t_wet} | 🚽 Poop: {t_poop}</div>
</div>""")

    p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    if t_pumping > 0 or p_cnt_today > 0:
        today_cards.append(f"""<div class="highlight-card card-pump">
    <div>
        <div class="highlight-title">🧴 Pumping</div>
        <div class="highlight-body">Pumped <b>{int(t_pumping):,} mL</b> total today.</div>
    </div>
    <div class="highlight-sub">{p_cnt_today} pumping session(s)</div>
</div>""")

    tummy_cnt_today = len(today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])
    if t_tummy > 0 or tummy_cnt_today > 0:
        today_cards.append(f"""<div class="highlight-card card-tummy">
    <div>
        <div class="highlight-title">🛟 Tummy Time</div>
        <div class="highlight-body">Logged <b>{int(t_tummy)} min(s)</b> today.</div>
    </div>
    <div class="highlight-sub">{tummy_cnt_today} session(s) logged</div>
</div>""")

    sleep_cnt_today = len(today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)])
    if t_sleep > 0 or sleep_cnt_today > 0:
        today_cards.append(f"""<div class="highlight-card card-sleep">
    <div>
        <div class="highlight-title">🛌 Rest & Sleep</div>
        <div class="highlight-body">Logged <b>{int(t_sleep)} hr(s)</b> rest.</div>
    </div>
    <div class="highlight-sub">{sleep_cnt_today} sleep period(s)</div>
</div>""")

    if t_meds > 0:
        today_cards.append(f"""<div class="highlight-card card-meds">
    <div>
        <div class="highlight-title">💊 Medication</div>
        <div class="highlight-body">Logged <b>{t_meds}</b> dose(s).</div>
    </div>
    <div class="highlight-sub">Dose(s) tracked today</div>
</div>""")

    if t_latest_temp is not None:
        today_cards.append(f"""<div class="highlight-card card-temp">
    <div>
        <div class="highlight-title">🌡️ Body Temp</div>
        <div class="highlight-body"><b>{t_latest_temp:.1f} °C</b></div>
    </div>
    <div class="highlight-sub">{len(t_temp_df)} reading(s) logged</div>
</div>""")

    if len(today_df) > 0:
        today_cards.append(f"""<div class="highlight-card card-events">
    <div>
        <div class="highlight-title">📊 Total Events</div>
        <div class="highlight-body"><b>{len(today_df):,}</b> entry(s) logged.</div>
    </div>
    <div class="highlight-sub">Date: {today_date.strftime('%Y-%m-%d')}</div>
</div>""")

    # --- Responsive Layout Logic for Today's Cards ---
    card_count = len(today_cards)
    base_span = "card-span-3" # Default 4 per row
    if card_count == 3: base_span = "card-span-4"
    elif card_count == 2: base_span = "card-span-6"
    elif card_count == 1: base_span = "card-span-12"

    formatted_today_cards = []
    for i, card in enumerate(today_cards):
        # Inject the computed base span class
        cls = f"highlight-card {base_span}"
        
        # If mobile and total cards are odd, force the FIRST card (Last Feeding) to stretch full width mathematically
        if card_count % 2 != 0 and i == 0 and card_count > 1:
            cls += " mobile-full-width"
            
        formatted_today_cards.append(card.replace('class="highlight-card', f'class="{cls}'))

    # Render Today Cards via CSS Grid Container
    st.markdown(f'<div class="cards-container">{"".join(formatted_today_cards)}</div>', unsafe_allow_html=True)

# --- B. PERIOD HIGHLIGHTS ---
st.markdown('<div id="period-highlights"></div>', unsafe_allow_html=True)

start_code = start_date.strftime('%m.%d')
end_code = end_date.strftime('%m.%d')

with st.expander(f"✨ Range Highlights [{start_code} – {end_code}]", expanded=False):
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
    p_temp_str = f"<b>{p_latest_temp:.1f} °C</b>" if p_latest_temp else "No readings"

    p_pump_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    p_tummy_cnt = len(filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])

    # Period highlight cards are fixed to 8, so we hardcode card-span-3 to enforce 4-per-row on desktop natively
    period_cards = [
        f"""<div class="highlight-card card-span-3 card-milk">
    <div>
        <div class="highlight-title">🍼 Milk Intake</div>
        <div class="highlight-body">Total <b>{int(p_milk):,} mL</b> across <b>{p_feed_cnt}</b> feed(s).</div>
    </div>
    <div class="highlight-sub">Avg Feed: ~{int(p_avg_feed)} mL (Form: {int(p_formula):,}mL, BM: {int(p_bm):,}mL)</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-diaper">
    <div>
        <div class="highlight-title">🚽 Diaper Output</div>
        <div class="highlight-body">Total <b>{p_wet + p_poop}</b> diaper change(s).</div>
    </div>
    <div class="highlight-sub">💧 Wet: {p_wet} | 🚽 Poop: {p_poop}</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-pump">
    <div>
        <div class="highlight-title">🧴 Pumping</div>
        <div class="highlight-body">Pumped <b>{int(p_pumping):,} mL</b> total in range.</div>
    </div>
    <div class="highlight-sub">{p_pump_cnt} pumping session(s)</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-tummy">
    <div>
        <div class="highlight-title">🛟 Tummy Time</div>
        <div class="highlight-body">Logged <b>{int(p_tummy)} min(s)</b> total in range.</div>
    </div>
    <div class="highlight-sub">{p_tummy_cnt} session(s) recorded</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-sleep">
    <div>
        <div class="highlight-title">🛌 Sleep & Rest</div>
        <div class="highlight-body">Logged <b>{int(p_sleep)} hr(s)</b> of rest.</div>
    </div>
    <div class="highlight-sub">{len(filtered_df[filtered_df['Event Type'].str.contains('Sleep', case=False, na=False)])} sleep period(s)</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-meds">
    <div>
        <div class="highlight-title">💊 Medication</div>
        <div class="highlight-body">Logged <b>{p_meds}</b> dose(s).</div>
    </div>
    <div class="highlight-sub">Dose(s) tracked in log</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-temp">
    <div>
        <div class="highlight-title">🌡️ Body Temperature</div>
        <div class="highlight-body">{p_temp_str}</div>
    </div>
    <div class="highlight-sub">{len(p_temp_df)} reading(s) in period</div>
</div>""",
        f"""<div class="highlight-card card-span-3 card-events">
    <div>
        <div class="highlight-title">📊 Total Events</div>
        <div class="highlight-body"><b>{len(filtered_df):,}</b> entry(s) logged.</div>
    </div>
    <div class="highlight-sub">From {start_date} to {end_date}</div>
</div>"""
    ]

    st.markdown(f'<div class="cards-container">{"".join(period_cards)}</div>', unsafe_allow_html=True)

st.markdown('<hr style="margin: 4px 0; opacity: 0.2;">', unsafe_allow_html=True)

def render_empty_state(title="No Data Logged in this period", subtitle="Try picking a wider date range or logging new entries."):
    st.markdown(f"""<div class="empty-data-card">
    <div class="empty-data-title">📋 {title}</div>
    <div class="empty-data-sub">{subtitle}</div>
</div>""", unsafe_allow_html=True)

# ==========================================
# 5. EXPANDED RAW DATA LOGS TABLE (MOVED UP)
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
    table_df = table_df.sort_values('DateTime', ascending=False).reset_index(drop=True)

# Ensure Value remains numeric for accurate math sorting in the UI
if 'Value (Optional)' in table_df.columns:
    table_df['Value (Optional)'] = pd.to_numeric(table_df['Value (Optional)'], errors='coerce')

# Keep DateTime pure for sorting, but duplicate mapping into columns
if 'DateTime' in table_df.columns:
    table_df['DateTime_Display'] = table_df['DateTime']

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
    # Reduced height from 700 to 490 (Shrunk by 30%)
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
    st.markdown(f'<div class="raw-log-count-text">Showing {len(display_df)} entry(s) matching your criteria sorted in descending order.</div>', unsafe_allow_html=True)
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")

st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)

# ==========================================
# 6. CHARTS & ANALYTICS (MOVED DOWN)
# ==========================================
st.markdown('<div id="analytics-charts"></div>', unsafe_allow_html=True)
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⏰ Today",
    "🍼 Milk", 
    "🚽 Diapers", 
    "🧴 Pumping",
    "🛟 Tummy",
    "📈 Growth (WHO)", 
    "🩺 Health & Vaccine"
])

# TAB 1: FIRST TAB - "Today" 24-Hour Timeline Chart with "%d-%H" x-axis formatting
with tab1:
    cutoff_24h = current_local_time - timedelta(hours=24)
    today_24h_df = df[(df['DateTime'] >= cutoff_24h) & (df['DateTime'] <= current_local_time)].copy()
    
    if not today_24h_df.empty:
        norm_today_df = prepare_normalized_timeline_df(today_24h_df)
        fig_today_timeline = px.scatter(
            norm_today_df,
            x="DateTime",
            y="Event Type",
            size="CategoryBubbleSize",
            color="Event Type",
            color_discrete_map=COLOR_MAP,
            hover_data={"Value (Optional)": True, "CategoryBubbleSize": False, "DateTime": False, "Event Type": False},
            size_max=14
        )
        fig_today_timeline.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        fig_today_timeline = style_plotly_figure(
            fig_today_timeline,
            title_text="⏰ Last 24 Hours Activity Timeline",
            height=450,
            is_scatter=True,
            x_tickformat="%d-%H",
            x_dtick=10800000, # 3 hours in milliseconds
            y_tickangle=-45   # Tilt Y-axis text
        )
        fig_today_timeline.update_layout(showlegend=False)
        st.plotly_chart(fig_today_timeline, use_container_width=True)
        st.caption("ℹ️ *Interactive scatter timeline displaying all events logged within the last 24 hours using exact DateTime.*")
    else:
        render_empty_state("No Events Logged in the Last 24 Hours")

# TAB 2: Milk Intake (Formula = Sky Blue #38bdf8, BM = Grey #9ca3af, Count = Orange #f97316)
with tab2:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(
            lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)"
        )
        
        grouped_vol = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        grouped_count = milk_df.groupby(group_col).size().reset_index(name='Total Feeds Count')
        
        grouped_vol[group_col] = grouped_vol[group_col].apply(format_x_label)
        grouped_count[group_col] = grouped_count[group_col].apply(format_x_label)
        
        is_single = len(grouped_count[group_col].unique()) == 1
        
        fig_milk = make_subplots(specs=[[{"secondary_y": True}]])
        
        df_f = grouped_vol[grouped_vol['Category'] == '🍼 Formula (mL)']
        if not df_f.empty:
            fig_milk.add_trace(
                go.Bar(
                    name='🍼 Formula (mL)',
                    x=df_f[group_col].astype(str),
                    y=df_f['Value (Optional)'],
                    marker_color="#38bdf8",
                    width=0.25 if is_single else None,
                    hovertemplate='%{y} mL<extra></extra>'
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
                    marker_color="#9ca3af",
                    width=0.25 if is_single else None,
                    hovertemplate='%{y} mL<extra></extra>'
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
                line=dict(color='#f97316', width=3, shape='spline', smoothing=1.3),
                marker=dict(size=10, symbol='circle', color='#f97316', line=dict(width=2, color='#ffffff')),
                hovertemplate='%{y} feeds<extra></extra>'
            ),
            secondary_y=True
        )

        fig_milk = style_plotly_figure(
            fig_milk,
            title_text=f"🍼 Milk Intake Volume & Feed Count — {granularity}",
            height=490,
            single_point=is_single
        )
        
        fig_milk.update_layout(barmode='stack')
        
        fig_milk.update_yaxes(
            title_text="",
            secondary_y=False,
            showgrid=True,
            gridcolor="rgba(128,128,128,0.15)",
            tickfont=dict(size=9.5),
            automargin=True
        )
        fig_milk.update_yaxes(
            title_text="",
            secondary_y=True,
            showgrid=False,
            tickfont=dict(size=9.5),
            automargin=True
        )
        
        st.plotly_chart(fig_milk, use_container_width=True)
        st.caption(f"ℹ️ *Combines stacked **Formula and Breast Milk volume (mL)** on the left axis with total **Feed Count(s)** (orange line) on the right axis grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Feeding Data Logged in this period")

# TAB 3: Diaper Output
with tab3:
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)].copy()
    if not diaper_df.empty:
        diaper_df['Category'] = diaper_df['Event Type'].apply(
            lambda x: "🚽 Poop (Cnt)" if "poop" in x.lower() else "💧 Wet Diaper (Cnt)"
        )
        grouped_diaper = diaper_df.groupby([group_col, 'Category']).size().reset_index(name='Count')
        grouped_diaper[group_col] = grouped_diaper[group_col].apply(format_x_label)
        is_single = len(grouped_diaper[group_col].unique()) == 1
        
        fig_diaper = px.bar(
            grouped_diaper,
            x=group_col,
            y="Count",
            color="Category",
            barmode="group",
            color_discrete_map=COLOR_MAP,
            labels={"Count": "Diaper Count(s)", group_col: granularity}
        )
        if is_single:
            fig_diaper.update_traces(width=0.25)
        fig_diaper.update_traces(hovertemplate='%{y}<extra></extra>')
        fig_diaper = style_plotly_figure(fig_diaper, title_text=f"🚽 Diaper Changes Count — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_diaper, use_container_width=True)
        st.caption(f"ℹ️ *Compares Wet Diapers and Poop counts grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Diaper Data Logged in this period")

# TAB 4: Dedicated Pumping Chart
with tab4:
    pump_df = filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)].copy()
    if not pump_df.empty:
        grouped_pump = pump_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_pump[group_col] = grouped_pump[group_col].apply(format_x_label)
        is_single = len(grouped_pump[group_col].unique()) == 1
        
        fig_pump = px.bar(
            grouped_pump,
            x=group_col,
            y="Value (Optional)",
            color_discrete_sequence=[COLOR_MAP["🧴 Pumping (mL)"]],
            labels={"Value (Optional)": "Volume (mL)", group_col: granularity}
        )
        if is_single:
            fig_pump.update_traces(width=0.25)
        fig_pump.update_traces(hovertemplate='%{y} mL<extra></extra>')
        fig_pump = style_plotly_figure(fig_pump, title_text=f"🧴 Pumping Volume (mL) — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_pump, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded pumping volume (mL) grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Pumping Data Logged in this period")

# TAB 5: Dedicated Tummy Time Chart
with tab5:
    tummy_df = filtered_df[filtered_df['Event Type'].str.contains("Tummy Time", case=False, na=False)].copy()
    if not tummy_df.empty:
        grouped_tummy = tummy_df.groupby(group_col)['Value (Optional)'].sum().reset_index()
        grouped_tummy[group_col] = grouped_tummy[group_col].apply(format_x_label)
        is_single = len(grouped_tummy[group_col].unique()) == 1
        
        fig_tummy = px.bar(
            grouped_tummy,
            x=group_col,
            y="Value (Optional)",
            color_discrete_sequence=[COLOR_MAP["🛟 Tummy Time (Mins)"]],
            labels={"Value (Optional)": "Duration (Mins)", group_col: granularity}
        )
        if is_single:
            fig_tummy.update_traces(width=0.25)
        fig_tummy.update_traces(hovertemplate='%{y} Mins<extra></extra>')
        fig_tummy = style_plotly_figure(fig_tummy, title_text=f"🛟 Tummy Time — {granularity}", height=450, single_point=is_single)
        st.plotly_chart(fig_tummy, use_container_width=True)
        st.caption(f"ℹ️ *Displays recorded tummy time duration (Mins) grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Tummy Time Data Logged in this period")

# TAB 6: Health, Advanced WHO Charts, and Milestone Tracking
with tab6:
    act_option = st.radio(
        "Select Health Module:",
        options=[
            "⚖️ Weight (WHO)",
            "🏔️ Height (WHO)",
            "🐷 Head Size (WHO)"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- ADVANCED WHO GROWTH CHARTS LOGIC ---
    if "Weight" in act_option:
        metric_name, unit, color = "Weight", "kg", COLOR_MAP["⚖️ Weight (kg)"]
        db_keyword = "⚖️ Weight (kg)"
    elif "Height" in act_option:
        metric_name, unit, color = "Height", "cm", COLOR_MAP["🏔️ Height (cm)"]
        db_keyword = "🏔️ Height (cm)"
    else:
        metric_name, unit, color = "Head Size", "cm", COLOR_MAP["🐷 Head Size (cm)"]
        db_keyword = "🐷 Head Size (cm)"

    wh_df = df[df['Event Type'] == db_keyword].copy()

    if wh_df.empty:
        render_empty_state(f"No {metric_name} Data Logged")
    else:
        # Vectorized Pandas math for Safe Age calculation
        wh_df['Age_Months'] = (pd.to_datetime(wh_df['Date']) - pd.to_datetime(baby_dob)).dt.days / 30.437
        wh_df = wh_df[(wh_df['Age_Months'] >= 0) & (wh_df['Age_Months'] <= 24)]

        if wh_df.empty:
            render_empty_state(f"No {metric_name} Data within 0-24 Months")
        else:
            who_d = WHO_DATA[baby_gender][metric_name]
            fig_who = go.Figure()
            m_arr = who_d["M"]

            # Plot shaded WHO Percentile background bands
            fig_who.add_trace(go.Scatter(x=m_arr, y=who_d["P90"], mode='lines', line=dict(width=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            fig_who.add_trace(go.Scatter(x=m_arr, y=who_d["P75"], mode='lines', fill='tonexty', fillcolor='rgba(200,200,200,0.2)', line=dict(width=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            fig_who.add_trace(go.Scatter(x=m_arr, y=who_d["P50"], mode='lines', fill='tonexty', fillcolor='rgba(180,180,180,0.3)', line=dict(width=2, color='rgba(0,0,0,0.15)'), showlegend=False, hoverinfo='skip'))
            fig_who.add_trace(go.Scatter(x=m_arr, y=who_d["P25"], mode='lines', fill='tonexty', fillcolor='rgba(150,150,150,0.4)', line=dict(width=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            fig_who.add_trace(go.Scatter(x=m_arr, y=who_d["P10"], mode='lines', fill='tonexty', fillcolor='rgba(180,180,180,0.3)', line=dict(width=1, color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))

            # Build rich custom hover text calculating exact interpolated percentiles
            hover_text = []
            for _, row in wh_df.iterrows():
                age, v = row['Age_Months'], row['Value (Optional)']
                p10, p25, p50, p75, p90 = [np.interp(age, m_arr, who_d[p]) for p in ['P10', 'P25', 'P50', 'P75', 'P90']]
                
                if v < p10: pct = "< 10th"
                elif v < p25: pct = "10th-25th"
                elif v < p50: pct = "25th-50th"
                elif v < p75: pct = "50th-75th"
                elif v <= p90: pct = "75th-90th"
                else: pct = "> 90th"
                
                ht = f"<b>{row['Date']}</b> (Age: {age:.1f}mo)<br><br><b>Value: {v:.1f} {unit}</b><br>Percentile Bracket: {pct}<br>---<br>WHO 90th: {p90:.1f}<br>WHO 75th: {p75:.1f}<br>WHO 50th: {p50:.1f}<br>WHO 25th: {p25:.1f}<br>WHO 10th: {p10:.1f}"
                hover_text.append(ht)

            # Plot baby's actual scatter line
            fig_who.add_trace(go.Scatter(
                x=wh_df['Age_Months'], y=wh_df['Value (Optional)'], mode='lines+markers', name=metric_name,
                text=hover_text, hovertemplate="%{text}<extra></extra>",
                marker=dict(size=10, color=color, line=dict(width=2, color='white')),
                line=dict(width=3, color=color)
            ))

            fig_who.update_layout(
                title=dict(text=f"WHO 0-24 Months {metric_name} Chart ({baby_gender})", x=0.5, font=dict(size=15)),
                xaxis_title="Baby's Age (Months)", yaxis_title=f"{metric_name} ({unit})", height=480,
                margin=dict(l=10, r=10, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            fig_who.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)", tick0=0, dtick=3)
            fig_who.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
            st.plotly_chart(fig_who, use_container_width=True)
            st.caption(f"ℹ️ *Showing your recorded {metric_name} against WHO Standard percentiles. Shaded bands represent the 10th, 25th, 50th, 75th, and 90th percentiles.*")

# TAB 7: Health Charts & HKCIP Vaccine Tracker
with tab7:
    act_option = st.radio("Select Category:", options=["🛌 Sleep (hrs)", "🌡️ Temp (°C)", "💊 Meds (Cnt)", "💉 HKCIP Vaccine Tracker"], horizontal=True, label_visibility="collapsed")
    
    if act_option == "💉 HKCIP Vaccine Tracker":
        st.markdown("<h4 style='text-align: center; margin-bottom: 0.5rem;'>💉 HKCIP Milestone Tracker</h4>", unsafe_allow_html=True)
        
        vac_df = df[df['Event Type'] == "💉 Vaccine (Cnt)"].copy()
        
        # Match keywords in the "Notes / Details" column to intelligently auto-tick the timeline!
        def get_date(keyword_regex, index):
            if vac_df.empty: return None
            matches = vac_df[vac_df['Notes / Details (Optional)'].str.contains(keyword_regex, case=False, na=False)].sort_values('DateTime')
            return matches.iloc[index]['Date'] if index < len(matches) else None

        hkcip_schedule = [
            {"Age": "Newborn", "Days": 0, "Vaccine": "BCG", "Match": get_date("bcg", 0)},
            {"Age": "Newborn", "Days": 0, "Vaccine": "Hepatitis B (1st)", "Match": get_date("hep|hbv|hexa|6-in|6 in", 0)},
            {"Age": "1 Month", "Days": 30, "Vaccine": "Hepatitis B (2nd)", "Match": get_date("hep|hbv|hexa|6-in|6 in", 1)},
            {"Age": "2 Months", "Days": 60, "Vaccine": "DTaP-IPV-Hib-HepB (1st)", "Match": get_date("dtap|hexa|6-in|6 in|5-in|pent", 0)},
            {"Age": "2 Months", "Days": 60, "Vaccine": "Pneumococcal (1st)", "Match": get_date("pcv|pneumo", 0)},
            {"Age": "2 Months", "Days": 60, "Vaccine": "Rotavirus (1st)", "Match": get_date("rota", 0)},
            {"Age": "4 Months", "Days": 120, "Vaccine": "DTaP-IPV-Hib-HepB (2nd)", "Match": get_date("dtap|hexa|6-in|6 in|5-in|pent", 1)},
            {"Age": "4 Months", "Days": 120, "Vaccine": "Pneumococcal (2nd)", "Match": get_date("pcv|pneumo", 1)},
            {"Age": "4 Months", "Days": 120, "Vaccine": "Rotavirus (2nd)", "Match": get_date("rota", 1)},
            {"Age": "6 Months", "Days": 180, "Vaccine": "DTaP-IPV-Hib-HepB (3rd)", "Match": get_date("dtap|hexa|6-in|6 in|5-in|pent", 2)},
            {"Age": "6 Months", "Days": 180, "Vaccine": "Pneumococcal (3rd)", "Match": get_date("pcv|pneumo", 2)},
            {"Age": "6 Months", "Days": 180, "Vaccine": "Rotavirus (3rd)", "Match": get_date("rota", 2)},
            {"Age": "12 Months", "Days": 365, "Vaccine": "MMR (1st)", "Match": get_date("mmr", 0)},
            {"Age": "12 Months", "Days": 365, "Vaccine": "Pneumococcal (Booster)", "Match": get_date("pcv|pneumo", 3)},
            {"Age": "12 Months", "Days": 365, "Vaccine": "Varicella (1st)", "Match": get_date("varicella|cp|chickenpox", 0)},
            {"Age": "18 Months", "Days": 547, "Vaccine": "DTaP-IPV-Hib (Booster)", "Match": get_date("dtap|hexa|6-in|6 in|5-in|pent", 3)},
            {"Age": "18 Months", "Days": 547, "Vaccine": "MMRV (2nd)", "Match": get_date("mmr", 1)},
        ]
        
        # Fixed Timezone Safe Current Date Calculation
        current_date = (datetime.utcnow() + timedelta(hours=tz_offset)).date()
        age_days = (current_date - baby_dob).days
        
        rows = []
        for s in hkcip_schedule:
            if s["Match"]:
                status, date_str = "✅ Done", str(s["Match"])
            elif age_days >= s["Days"]:
                status, date_str = "⚠️ Overdue", "-"
            else:
                status, date_str = "⏳ Upcoming", "-"
            rows.append({"Status": status, "Age Milestone": s["Age"], "Vaccine Required": s["Vaccine"], "Logged Date": date_str})
            
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=620)
        st.caption("ℹ️ *Auto-matches your logged vaccines to the HKCIP schedule by intelligently scanning your 'Notes / Details' column for keywords (e.g. DTaP, PCV, Rota, BCG).*")
        
        st.markdown("##### 📋 Riley's Vaccination History")
        if not vac_df.empty:
            if 'DateTime' in vac_df.columns:
                vac_df = vac_df.sort_values('DateTime', ascending=True).reset_index(drop=True)
                vac_df['DateTime_Display'] = vac_df['DateTime']
                # Wrapped in pd.to_datetime to protect against AttributeError during safe division
                vac_df['Age at Shot'] = ((pd.to_datetime(vac_df['Date']) - pd.to_datetime(baby_dob)).dt.days / 30.437).round(1).astype(str) + " mo"
            
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

