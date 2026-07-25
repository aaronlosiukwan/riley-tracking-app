import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
from streamlit_gsheets import GSheetsConnection
import gspread

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ==========================================
# 1. APP CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Riley's Dash",
    page_icon="🍼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive & Adaptive CSS overrides with Apple Health / Premium UI aesthetics
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    html { scroll-behavior: smooth; }
    [id] { scroll-margin-top: 70px; }

    /* Modern Typography & Native System Fonts - Excluding span so Streamlit Icons render correctly */
    body, .stApp, p, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    body, .stApp {
        color: var(--card-text) !important;
        background-color: #f8fafc !important;
    }

    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important; 
    }
    
    [data-testid="stMainBlockContainer"] {
        padding-top: calc(2.5rem + env(safe-area-inset-top)) !important;
        padding-bottom: 10rem !important; 
    }

    div[data-testid="stVerticalBlock"] { gap: 0.75rem !important; }

    :root {
        --card-bg: #ffffff; --card-border: #f1f5f9; --card-text: #1e293b;
    }

    .app-main-title {
        font-size: clamp(2.2rem, 5vw + 0.8rem, 2.8rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
        line-height: 1.3 !important;
        white-space: normal !important; 
        color: #0f172a;
        margin: 0;
        padding: 0;
    }

    div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
        align-items: center !important;
        margin-top: 1rem !important;
        margin-bottom: 3.5rem !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-secondary"],
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseLinkButton-secondary"] {
        height: 44px !important; min-height: 44px !important; 
        padding: 0 !important; border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        background-color: var(--card-bg) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important; transition: all 0.15s ease;
        display: inline-flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; text-decoration: none !important; box-sizing: border-box;
    }
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) p {
        font-weight: 600 !important; font-size: 0.95rem !important; color: #1e293b !important; margin: 0 !important;
    }

    @media (max-width: 768px) {
        .app-main-title { margin-bottom: 1.5rem !important; }
        div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
            flex-wrap: wrap !important; gap: 0.5rem !important;
            flex-direction: row !important; margin-bottom: 3rem !important;
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

    span[data-baseweb="tag"] { background-color: #e5e7eb !important; color: #1f2937 !important; border: 1px solid #d1d5db !important; font-weight: 500 !important; }
    .toc-button { display: block; width: 100%; padding: 8px 12px; margin: 4px 0; background-color: var(--card-bg); border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); color: var(--card-text) !important; text-decoration: none !important; border-radius: 8px; font-size: 0.9rem; font-weight: 500; transition: all 0.15s ease-in-out; }
    .toc-button:hover { background-color: #f1f5f9; border-color: #cbd5e1; text-decoration: none !important; }

    .cards-container { display: grid !important; grid-template-columns: repeat(12, 1fr) !important; gap: 12px !important; align-items: stretch !important; margin-bottom: 2px !important; width: 100% !important; margin-top: 8px !important; }
    .card-span-3 { grid-column: span 3 !important; } .card-span-4 { grid-column: span 4 !important; } .card-span-6 { grid-column: span 6 !important; } .card-span-12 { grid-column: span 12 !important; } 
    @media (max-width: 1024px) { .card-span-3, .card-span-4 { grid-column: span 6 !important; } .mobile-full-width { grid-column: span 12 !important; } }

   /* --- METRIC CARDS --- */
    .highlight-card { 
        background-color: var(--card-bg); 
        border-radius: 16px; 
        padding: 18px 20px; /* Slightly more breathing room */
        min-height: 125px; 
        height: 100% !important; 
        display: flex !important; flex-direction: column !important; justify-content: space-between !important; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); 
        border: 1px solid var(--card-border); 
        box-sizing: border-box; word-wrap: break-word; overflow-wrap: break-word; 
        color: var(--card-text) !important; 
        transition: transform 0.15s ease, box-shadow 0.15s ease; 
    }
    .highlight-card:hover {
        transform: translateY(-2px); /* Subtle lift interaction */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
    }
    
    /* Super-title micro-labels for cards */
    .highlight-title { 
        font-weight: 700; 
        font-size: 0.75rem; 
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px; 
        color: #64748b; 
    } 
    .highlight-body { font-size: 0.9rem; opacity: 0.95; line-height: 1.3; } 
    .highlight-sub { font-size: 0.75rem; color: #94a3b8; margin-top: 8px; line-height: 1.3; font-weight: 500; }

    /* --- EMPTY STATES --- */
    .empty-data-card { 
        background-color: #f8fafc; 
        border: 1px dashed #cbd5e1; /* Dashed border indicates 'waiting for data' */
        border-radius: 16px; 
        padding: 32px 16px; /* Taller padding for empty states */
        text-align: center; 
        margin: 6px 0; 
        color: #64748b; 
    }
    .empty-data-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; color: #475569;}
    .empty-data-sub { font-size: 0.85rem; opacity: 0.8; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)

@st.cache_resource
def get_global_ai_cache():
    return {}

global_ai_cache = get_global_ai_cache()

# ---------------------------------------------------------
# 2. RESPONSIVE HEADER SECTION
# ---------------------------------------------------------
h_col1, h_col2, h_col3 = st.columns([6, 2, 2], vertical_alignment="center")

with h_col1:
    st.markdown('<div class="app-main-title">🍼 Riley\'s Dash</div>', unsafe_allow_html=True)

with h_col2:
    st.link_button("➕ Add", "shortcuts://run-shortcut?name=Riley%20Tracker&silent=true", use_container_width=True)

DEFAULT_SHEET_URL = "[https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing)"

@st.cache_data(ttl=600)
@st.cache_data(ttl=600)
def load_sheet_data(url):
    try:
        # 1. Authenticate using native gspread (Bypasses the buggy Streamlit wrapper)
        secrets_dict = dict(st.secrets["connections"]["gsheets"])
        secrets_dict.pop("spreadsheet", None)
        secrets_dict.pop("worksheet", None)
        secrets_dict.pop("type", None)
        
        client = gspread.service_account_from_dict(secrets_dict)
        sheet = client.open_by_url(url).worksheet("Log")
        
        # 2. Fetch all data safely
        data = sheet.get_all_values()
        if not data or len(data) < 2:
            return pd.DataFrame()
        
        # 3. Convert to Pandas DataFrame
        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)
        
        # 4. Map the exact Google Sheet Row ID (df.index 0 is Row 2 in Google Sheets)
        df['SheetRow'] = df.index + 2 
        
        # 5. Clean the data
        df.columns = df.columns.astype(str).str.strip()
        df.replace("", np.nan, inplace=True) # Crucial: Converts empty string cells to NaN
        
        if 'DateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        elif 'EntryDateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['EntryDateTime'], errors='coerce')
        else:
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            if date_cols: df['DateTime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
        df = df.dropna(subset=['DateTime'])
        df['Date'] = df['DateTime'].dt.date
        df['Week'] = df['DateTime'].dt.to_period('W-SUN').dt.start_time.dt.date
        df['Month'] = df['DateTime'].dt.strftime('%Y-%m')
        
        if 'Value (Optional)' in df.columns: 
            df['Value (Optional)'] = pd.to_numeric(df['Value (Optional)'], errors='coerce')
            countable_events = ["Wet Diaper", "Poop", "Meds", "Vaccine"]
            mask = df['Event Type'].astype(str).str.contains('|'.join(countable_events), case=False, na=False) & df['Value (Optional)'].isna()
            df.loc[mask, 'Value (Optional)'] = 1.0
        else: 
            df['Value (Optional)'] = 1.0
        
        if 'Event Type' in df.columns: df['Event Type'] = df['Event Type'].astype(str).str.strip()
        return df.sort_values('DateTime', ascending=False)
        
    except Exception as e:
        st.error(f"Error fetching Google Sheet securely: {e}")
        return pd.DataFrame()

# Initialize session states for AI refresh tracking
# Initialize session states for AI refresh tracking
if "last_ai_data_datetime" not in st.session_state:
    st.session_state.last_ai_data_datetime = None
if "ai_refresh_key" not in st.session_state:
    st.session_state.ai_refresh_key = "default_key"
if "ai_retry_count" not in st.session_state:
    st.session_state.ai_retry_count = 0

with h_col3:
    if st.button("🔄 Refresh", use_container_width=True):
        with st.spinner("Checking for new data..."):
            try:
                secrets_dict = dict(st.secrets["connections"]["gsheets"])
                secrets_dict.pop("spreadsheet", None); secrets_dict.pop("worksheet", None); secrets_dict.pop("type", None)
                client = gspread.service_account_from_dict(secrets_dict)
                sheet = client.open_by_url(DEFAULT_SHEET_URL).worksheet("Log")
                
                dt_col = sheet.col_values(5) 
                live_max_dt = pd.to_datetime(dt_col[1:], errors='coerce').max() if len(dt_col) > 1 else None
                cached_max_dt = st.session_state.get('last_ai_data_datetime')
                
                if cached_max_dt and live_max_dt and live_max_dt <= cached_max_dt:
                    st.session_state.show_up_to_date_toast = True
                    st.rerun()
                
                else:
                    st.cache_data.clear()
                    current_ai_state = st.session_state.get('ai_insights_enabled', False)
                    st.session_state.last_ai_data_datetime = live_max_dt
                    
                    # DO NOT CLEAR global_ai_cache! Unmodified categories remain cached automatically.
                    st.session_state.ai_insights_enabled = current_ai_state
                    st.session_state.show_refresh_toast = True
                    st.rerun()
                    
            except Exception as e:
                st.cache_data.clear()
                st.session_state.show_refresh_toast = True
                st.rerun()

# --- Toast Notification Handlers ---
if st.session_state.get('show_up_to_date_toast', False):
    st.toast("Data is already up to date!", icon="⚡")
    st.session_state.show_up_to_date_toast = False

if st.session_state.get('show_refresh_toast', False):
    st.toast("New data synced successfully!", icon="✅")
    st.session_state.show_refresh_toast = False

# ==========================================
# 3. SIDEBAR TABLE OF CONTENTS & SETTINGS
# ==========================================

# --- PRE-LOAD VARIABLES FOR LINK BUTTONS ---
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"
clean_default_url = DEFAULT_SHEET_URL.strip("[]'\"")
active_url = st.session_state.get("sheet_url_input", clean_default_url)

# --- PRO UI CSS INJECTIONS ---
st.sidebar.markdown("""
    <style>
    /* Supertitle Section Headers */
    .pro-sidebar-header {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
        padding-left: 4px;
    }
    
    /* Sleek, borderless navigation links with micro-interactions */
    .pro-nav-item {
        display: block;
        padding: 8px 12px;
        border-radius: 8px;
        color: #334155 !important;
        text-decoration: none !important;
        font-weight: 500;
        font-size: 0.92rem;
        margin-bottom: 4px;
        transition: all 0.2s ease;
        background-color: transparent;
    }
    .pro-nav-item:hover {
        background-color: #f1f5f9;
        color: #0f172a !important;
        transform: translateX(3px);
    }
    
    /* Custom Unified Button Styling (For BOTH Action Buttons) */
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] a[data-testid="baseLinkButton-secondary"] {
        border: 1px solid #cbd5e1 !important;
        background-color: transparent !important;
        color: #334155 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    [data-testid="stSidebar"] a[data-testid="baseLinkButton-secondary"]:hover {
        background-color: #f8fafc !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SECTION 1: NAVIGATION ---
st.sidebar.markdown('<div class="pro-sidebar-header" style="margin-top: 0;">Navigation</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
    <a href="#top-header" class="pro-nav-item">✨ Today's Highlights</a>
    <a href="#filters" class="pro-nav-item">⚙️ Date Filters</a>
    <a href="#insights" class="pro-nav-item">📊 Data Insights</a>
    <a href="#database" class="pro-nav-item">📋 Master Database</a>
""", unsafe_allow_html=True)

# --- SECTION 2: ACTIONS ---
st.sidebar.markdown('<div class="pro-sidebar-header">Actions</div>', unsafe_allow_html=True)

# Removed type="primary" so it dynamically picks up our unified secondary CSS styling
if st.sidebar.button("🔄 Refresh AI Summaries", use_container_width=True, help="Forces the AI to completely re-generate insights based on the latest data."):
    st.session_state.ai_refresh_key = str(datetime.utcnow())
    global_ai_cache.clear()
    st.rerun()

if active_url:
    st.sidebar.link_button("🔗 Open Google Sheet", active_url, use_container_width=True)

# --- SECTION 3: SETTINGS ---
st.sidebar.markdown('<div class="pro-sidebar-header">Settings</div>', unsafe_allow_html=True)

with st.sidebar.expander("🧠 AI Preferences", expanded=False):
    if "ai_insights_enabled" not in st.session_state:
        st.session_state.ai_insights_enabled = True

    use_ai_insights = st.toggle(
        "✨ Enable AI Insights", 
        key="ai_insights_enabled", 
        help="Switches insights from rule-based formulas to LLM narrative analysis."
    )

with st.sidebar.expander("🔌 Data Connection", expanded=False):
    sheet_url_input = st.text_input("Google Sheet URL", value=clean_default_url, key="sheet_url_input")
    sheet_url_input = sheet_url_input.strip("[]'\"")
    tz_offset = st.number_input("Timezone Offset (UTC Hours)", value=8, step=1)

with st.sidebar.expander("👶 Baby Profile", expanded=False):
    baby_dob = st.date_input("Birth Date", value=datetime(2026, 6, 29).date())
    baby_gender = st.radio("Gender (For Growth Charts)", ["Girl", "Boy"], index=0, horizontal=True)

# ---------------------------------------------------------
# GSHEET DATA ENGINE & AI PIPELINE
# ---------------------------------------------------------
if 'needs_auto_retry' not in st.session_state:
    st.session_state.needs_auto_retry = False

df = load_sheet_data(sheet_url_input)
if df.empty: st.stop()

max_data_date = df['Date'].max()
min_data_date = df['Date'].min()

# Sync Column E Max DateTime on load
current_col_e_max = df['DateTime'].max()
if st.session_state.last_ai_data_datetime is None:
    st.session_state.last_ai_data_datetime = current_col_e_max

def call_ai(prompt_text, api_key_param, latest_data_timestamp, refresh_key):
    cache_key = hash(f"{prompt_text}_{latest_data_timestamp}_{refresh_key}")
    
    # Calculate exact local timestamp for when the AI is processing
    now_local = (datetime.utcnow() + timedelta(hours=tz_offset)).strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Check cache: Now safely handles new dicts (with generation time) and legacy data
    if cache_key in global_ai_cache:
        cached_data = global_ai_cache[cache_key]
        if isinstance(cached_data, dict):
            # Fetch generated time, defaulting to "Unknown" for dicts saved right before this update
            gen_time = cached_data.get('generated_at', "Previous Session")
            return cached_data['content'], True, cached_data['model'], gen_time
        else:
            return cached_data, True, "Legacy Cache", "Previous Session"

    if not OPENAI_AVAILABLE:
        return "⚠️ **OpenAI package missing.** Install `openai` in `requirements.txt`.", False, "N/A", "N/A"
    
    if not api_key_param:
        return "⚠️ **OpenRouter API Key missing.** Set `OPENROUTER_API_KEY` in Streamlit Secrets.", False, "N/A", "N/A"
        
    if st.session_state.get('ai_retry_count', 0) >= 3:
        return "⚠️ **API Limit Reached.** OpenRouter is overloaded. Please check back later.", False, "N/A", "N/A"
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key_param,
        default_headers={"HTTP-Referer": "https://streamlit.app", "X-Title": "Rileys Dash"}
    )
    
    try:
        chat_completion = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": "You are a data formatting tool. You are NOT a medical professional. Do NOT provide medical advice. Strictly summarize numbers."},
                {"role": "user", "content": prompt_text}
            ],
        )
        content = chat_completion.choices[0].message.content
        exact_model = chat_completion.model 
        
        content = re.sub(r'(?i)User Safety:.*?(?=\n|<br>|$)', '', content)
        content = re.sub(r'(?i)Safety Categories:.*?(?=\n|<br>|$)', '', content).strip()
        
        if "User Safety" in content or "Unauthorized Advice" in content or not content:
            st.session_state.needs_auto_retry = True
            return "⚠️ API Safety Filter tripped. Auto-retrying...", False, exact_model, now_local
            
        # Store content, exact model, AND the generation timestamp in the cache
        global_ai_cache[cache_key] = {
            'content': content, 
            'model': exact_model,
            'generated_at': now_local
        }
        st.session_state.ai_retry_count = 0
        
        return content, False, exact_model, now_local
        
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "Rate limit" in err_msg or "busy" in err_msg.lower():
            st.session_state.needs_auto_retry = True
            return f"⚠️ **Rate Limit (429):** Free API is busy. Retrying...", False, "N/A", "N/A"
        elif "401" in err_msg or "Authentication" in err_msg:
            return f"⚠️ **Auth Error (401):** Your OpenRouter API key is invalid or missing.", False, "N/A", "N/A"
        else:
            return f"⚠️ **API Error:** {err_msg}", False, "N/A", "N/A"

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
    "🍼 Formula (mL)": "#0ea5e9", "🤱 Breast Milk (mL)": "#64748b", "💧 Wet Diaper (Cnt)": "#3b82f6",
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
        title=dict(text=title_text, y=0.97, x=0.5, xanchor="center", yanchor="top", font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size=17, color="#0f172a")),
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=2, r=2, t=75, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text="", font=dict(size=10)),
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size=11),
        xaxis=dict(type=None if is_scatter else "category", tickformat=x_tickformat, dtick=x_dtick, title=dict(text=""), showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=9.5), automargin=True),
        yaxis=dict(title=dict(text=""), showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=9.5), tickangle=y_tickangle if y_tickangle is not None else 0, title_standoff=2, automargin=True),
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

def format_ai_html(output_text):
    html_text = output_text.strip()
    html_text = re.sub(r'```[a-zA-Z]*\n?', '', html_text).replace('```', '')
    html_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html_text)
    html_text = re.sub(r'^[-*]\s+(.*?)$', r'&bull; \1', html_text, flags=re.MULTILINE)
    html_text = html_text.replace('\n', '<br>')
    html_text = re.sub(r'(<br>\s*){3,}', '<br><br>', html_text)
    html_text = re.sub(r'(<br>\s*){2,}(?=&bull;)', '<br>', html_text)
    
    headers = ["High-Level Summary", "Trend Analysis", "Suggested Action"]
    for header in headers:
        pattern = rf'(?:<br>\s*)*(?:<b>|\*\*){header}(?:</b>|\*\*)(?:<br>\s*)*'
        replacement = f'<div style="margin-top: 18px; margin-bottom: 6px; font-weight: 600; color: #1e293b; letter-spacing: 0.01em;">{header}</div>'
        html_text = re.sub(pattern, replacement, html_text, flags=re.IGNORECASE)
        
    html_text = re.sub(r'(</div>)\s*(?:<br>\s*)+', r'\1', html_text)
    return html_text.replace('margin-top: 18px;', 'margin-top: 4px;', 1)


def render_insight_card(hardcoded_text, ai_prompt_context=None, category_df=None, category_key="default", subject="Riley"):
    api_key_param = st.secrets.get("OPENROUTER_API_KEY", None)
    
    # Extract max timestamp for this specific category
    if category_df is not None and not category_df.empty and 'DateTime' in category_df.columns:
        cat_max_dt = category_df['DateTime'].max()
        cat_data_ts_str = cat_max_dt.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(cat_max_dt) else "None"
    else:
        cat_data_ts_str = df['DateTime'].max().strftime('%Y-%m-%d %H:%M:%S') if not df.empty else "None"
        
    refresh_key = st.session_state.get('ai_refresh_key', 'default_key')
    now_local_str = (datetime.utcnow() + timedelta(hours=tz_offset)).strftime('%Y-%m-%d %H:%M:%S')

    # Helper function to generate standard Rule-Based Insight HTML
    def get_hardcoded_html():
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', hardcoded_text).replace('\n', '<br>')
        margin_bottom = "16px" if use_ai_insights else "24px"
        return f"""
        <div style="background-color: #ffffff; border-left: 4px solid #0ea5e9; padding: 16px 20px; border-radius: 12px; margin: 12px 0 {margin_bottom} 0; font-size: 0.92rem; color: #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #f1f5f9; line-height: 1.6;">
            <strong style="color: #0369a1; font-size: 1.05rem; letter-spacing: 0.01em; display: block; margin-bottom: 8px;">💡 Insight</strong> 
            {clean_text}
        </div>
        """

    # Helper function to generate AI Insight HTML
    def get_ai_html(content, time_display, model_used):
        formatted_content = format_ai_html(content)
        return f"""
        <div style="background-color: #ffffff; border-left: 4px solid #8b5cf6; padding: 16px 20px; border-radius: 12px; margin: 0 0 24px 0; font-size: 0.92rem; color: #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); border: 1px solid #f1f5f9; line-height: 1.5;">
            <strong style="color: #4c1d95; font-size: 1.05rem; letter-spacing: 0.01em; display: block; margin-bottom: 4px;">✨ AI Insight</strong> 
            {formatted_content}
            <div style="margin-top: 14px; padding-top: 8px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; color: #94a3b8;">
                <span>{time_display}</span>
                <span>🤖 Model: <code style="font-size: 0.70rem; color: #64748b; background-color: #f8fafc; padding: 1px 4px; border-radius: 4px;">{model_used}</code></span>
            </div>
        </div>
        """

    # 1. ALWAYS render the Rule-Based Insight Card first
    st.markdown(get_hardcoded_html(), unsafe_allow_html=True)

    # If AI Insights are disabled, stop here
    if not use_ai_insights:
        return

    # 2. Render AI Insight Card below the Hardcoded one
    ai_card_placeholder = st.empty()

    cached_entry = global_ai_cache.get(category_key)
    is_cache_valid = False

    if cached_entry and isinstance(cached_entry, dict):
        cached_ts = cached_entry.get('data_timestamp')
        cached_ref_key = cached_entry.get('refresh_key')
        
        if cached_ts == cat_data_ts_str and cached_ref_key == refresh_key:
            is_cache_valid = True

    # FAST PATH: Instant cache hit (0ms execution)
    if is_cache_valid:
        time_display = f"🕒 AI Summarized: {cached_entry['generated_at']} &bull; ⚡ Instant Cache"
        ai_card_placeholder.markdown(get_ai_html(cached_entry['content'], time_display, cached_entry['model']), unsafe_allow_html=True)
        return

    # SLOW PATH: Make live API call
    current_date_obj = datetime.utcnow().date()
    age_days = (current_date_obj - baby_dob).days
    age_months = age_days / 30.437
    
    subject_context = f"Subject: Riley (Baby Girl, Age: {age_days} days / {age_months:.1f} months old). Evaluate her trends against developmental benchmarks and Hong Kong standards for her exact age." if subject == "Riley" else f"Subject: {subject}."

    prompt_template = f"""DATA CONTEXT:
{subject_context}
{ai_prompt_context}

ROLE: You are an analytical data tool. You are NOT a medical professional. Never give medical advice.
TASK: Write a summary strictly based on the numbers provided. 

STRICT DATA EVALUATION RULES:
1. TODAY'S DATA IS PARTIAL / IN-PROGRESS: Use Today's logged metrics ONLY for factual, descriptive reporting.
2. TREND ANALYSIS MUST IGNORE TODAY: Evaluate trends strictly by comparing full completed days (Yesterday and prior completed days) against the Recent 7-Day Avg and Selected Historical Range. Absolutely DO NOT evaluate trends or draw health conclusions using Today's partial data.
3. SUGGESTED ACTION MUST IGNORE TODAY: Base your practical recommendation STRICTLY on completed full-day trends (Yesterday and earlier). Never base recommendations on Today's partial progress.

OUTPUT FORMAT RESTRICTIONS:
- DO NOT wrap the output in ```html or ```markdown code blocks.
- Provide the response in plain text using the exact section headers below (wrapped in **).

**High-Level Summary**
- [Bullet point 1: Factual/descriptive summary of Today's logged progress so far]
- [Bullet point 2: Key observation from recent full-day baselines]

**Trend Analysis**
[Write a single paragraph (3-4 sentences) evaluating full completed days (Yesterday and prior) compared against the Recent 7-Day Avg and Selected Range. Ignore today's partial numbers. Evaluate if healthy for her current age based on HK standards.]

**Suggested Action**
[Write 1 brief sentence suggesting a practical next step based STRICTLY on completed full-day historical trends (yesterday and earlier).]"""

    with st.spinner(f"🤖 Asking AI to analyze {subject}'s trends..."):
        if not OPENAI_AVAILABLE or not api_key_param or not ai_prompt_context:
            return
        
        output_text, is_cached, actual_model_used, gen_time = call_ai(prompt_template, api_key_param, cat_data_ts_str, refresh_key)
        
        global_ai_cache[category_key] = {
            'content': output_text,
            'model': actual_model_used,
            'generated_at': now_local_str,
            'data_timestamp': cat_data_ts_str,
            'refresh_key': refresh_key
        }
        
        time_display = f"🕒 AI Summarized: {now_local_str} &bull; 🚀 Live AI Call"
        ai_card_placeholder.markdown(get_ai_html(output_text, time_display, actual_model_used), unsafe_allow_html=True)

# ==========================================
# 4. TODAY'S HIGHLIGHTS & GLOBAL TREND DATAFRAMES
# ==========================================
utc_now = datetime.utcnow()
current_local_time = utc_now + timedelta(hours=tz_offset)
curr_hour = current_local_time.hour

# 1. 9:00 AM DAY CUTOFF LOGIC
if curr_hour < 9:
    # Between 00:00 and 08:59: Summarize yesterday's completed 24h data
    summary_target_date = current_local_time.date() - timedelta(days=1)
    is_morning_window = True
else:
    # 09:00 AM onwards: Summarize active today
    summary_target_date = current_local_time.date()
    is_morning_window = False

if max_data_date < summary_target_date:
    today_date = max_data_date
else:
    today_date = summary_target_date

today_df = df[df['Date'] == today_date]

# 2. RECENT 7-DAY AVERAGE LOGIC (STRICTLY EXCLUDES TODAY / TARGET DATE)
cutoff_7d_start = today_date - timedelta(days=7)
cutoff_7d_end = today_date - timedelta(days=1)
recent_7d_df = df[(df['Date'] >= cutoff_7d_start) & (df['Date'] <= cutoff_7d_end)]

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
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">{title}</div><div class="empty-data-sub">{subtitle}</div></div>""", unsafe_allow_html=True)

st.markdown('<div id="today"></div>', unsafe_allow_html=True)

today_date = max(current_local_time.date(), max_data_date)
today_df = df[df['Date'] == today_date]
cutoff_7d = today_date - timedelta(days=7)
recent_7d_df = df[(df['Date'] > cutoff_7d) & (df['Date'] <= today_date)]

st.subheader("✨ Today")

if today_df.empty:
    st.markdown(f"""<div class="empty-data-card"><div class="empty-data-title">No Data Logged Today</div><div class="empty-data-sub">Waiting for new entries.</div></div>""", unsafe_allow_html=True)
else:
    t_formula = today_df[today_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
    t_bm = today_df[today_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
    t_milk = t_formula + t_bm
    t_feed_cnt = len(today_df[today_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
    t_avg_feed = (t_milk / t_feed_cnt) if t_feed_cnt > 0 else 0
    # Deduplicate Diaper Changes by unique DateTime
    t_diaper_events = today_df[today_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
    t_diaper_changes = t_diaper_events['DateTime'].nunique() if not t_diaper_events.empty else 0
    
    t_wet = len(today_df[today_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
    t_poop = len(today_df[today_df['Event Type'].str.contains("Poop", case=False, na=False)])
    
    t_pumping = today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
    t_tummy = today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()
    t_sleep = today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
    t_meds = len(today_df[today_df['Event Type'].str.contains("Meds", case=False, na=False)])
    t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
    t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None

    today_cards = []
    c_feed = "#a855f7"
    c_milk = COLOR_MAP["🍼 Formula (mL)"]
    c_diaper = COLOR_MAP["💧 Wet Diaper (Cnt)"]
    c_pump = COLOR_MAP["🧴 Pumping (mL)"]
    c_tummy = COLOR_MAP["🛟 Tummy Time (Mins)"]
    c_sleep = COLOR_MAP["🛌 Sleep (hrs)"]
    c_meds = COLOR_MAP["💊 Meds (Cnt)"]
    c_temp = COLOR_MAP["🌡️ Temp (°C)"]
    c_events = "#64748b"

    today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">⏰ Last Feeding</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_feed}; line-height: 1.1;">{last_feed_delta}</span></div></div><div class="highlight-sub">{last_feed_sub}</div></div>""")
    if t_milk > 0 or t_feed_cnt > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🍼 Milk Intake</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_milk}; line-height: 1.1;">{int(t_milk):,} mL</span> across {t_feed_cnt} feed(s).</div></div><div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Form: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div></div>""")
    # Updated Diaper Card displaying deduplicated change count:
    if t_diaper_changes > 0: 
        today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🚽 Diaper Output</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_diaper}; line-height: 1.1;">{t_diaper_changes}</span> change(s).</div></div><div class="highlight-sub">💧 Wet: {t_wet} | 🚽 Poop: {t_poop}</div></div>""")
    p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
    if t_pumping > 0 or p_cnt_today > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🧴 Pumping</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_pump}; line-height: 1.1;">{int(t_pumping):,} mL</span> today.</div></div><div class="highlight-sub">{p_cnt_today} pumping session(s)</div></div>""")
    tummy_cnt_today = len(today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])
    if t_tummy > 0 or tummy_cnt_today > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🛟 Tummy Time</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_tummy}; line-height: 1.1;">{int(t_tummy)} min(s)</span> today.</div></div><div class="highlight-sub">{tummy_cnt_today} session(s) logged</div></div>""")
    sleep_cnt_today = len(today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)])
    if t_sleep > 0 or sleep_cnt_today > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🛌 Rest & Sleep</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_sleep}; line-height: 1.1;">{int(t_sleep)} hr(s)</span> rest.</div></div><div class="highlight-sub">{sleep_cnt_today} sleep period(s)</div></div>""")
    if t_meds > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">💊 Medication</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_meds}; line-height: 1.1;">{t_meds}</span> dose(s).</div></div><div class="highlight-sub">Dose(s) tracked today</div></div>""")
    if t_latest_temp is not None: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">🌡️ Body Temp</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_temp}; line-height: 1.1;">{t_latest_temp:.1f} °C</span></div></div><div class="highlight-sub">{len(t_temp_df)} reading(s) logged</div></div>""")
    if len(today_df) > 0: today_cards.append(f"""<div class="highlight-card"><div><div class="highlight-title">📊 Total Events</div><div class="highlight-body"><span style="font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; color: {c_events}; line-height: 1.1;">{len(today_df):,}</span> entry(s) logged.</div></div><div class="highlight-sub">Date: {today_date.strftime('%Y-%m-%d')}</div></div>""")

    card_count = len(today_cards)
    base_span = "card-span-3" if card_count >= 4 else ("card-span-4" if card_count == 3 else ("card-span-6" if card_count == 2 else "card-span-12"))

    formatted_today_cards = []
    for i, card in enumerate(today_cards):
        cls = f"highlight-card {base_span}"
        if card_count % 2 != 0 and i == 0 and card_count > 1: cls += " mobile-full-width"
        formatted_today_cards.append(card.replace('class="highlight-card', f'class="{cls}'))
    st.markdown(f'<div class="cards-container">{"".join(formatted_today_cards)}</div>', unsafe_allow_html=True)

# ==========================================
# 5. COMPACT QUICK FILTERS
# ==========================================
if 'sd' not in st.session_state: 
    st.session_state.sd = max(min_data_date, max_data_date - timedelta(days=20))
if 'ed' not in st.session_state: 
    st.session_state.ed = max_data_date

st.markdown('<div id="filters" style="margin-top: 4rem; padding-top: 1rem;"></div>', unsafe_allow_html=True)
st.markdown("<div style='font-size: 1.05rem; font-weight: 700; color: #1e293b; margin-bottom: 1.5rem;'>⚙️ Date Range & Grouping Filters</div>", unsafe_allow_html=True)

f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1, 1, 0.8], vertical_alignment="bottom")

with f_col1:
    granularity = st.selectbox("Grouping:", ["Daily", "Weekly", "Monthly", "All Time"], index=0)

def set_all_data():
    st.session_state.sd = min_data_date
    st.session_state.ed = max_data_date

with f_col2: st.date_input("Start Date", min_value=min_data_date, max_value=max_data_date, key="sd")
with f_col3: st.date_input("End Date", min_value=min_data_date, max_value=max_data_date, key="ed")
with f_col4: st.button("🗓️ All Data", on_click=set_all_data, use_container_width=True)

start_date = st.session_state.sd
end_date = st.session_state.ed
group_col_map = {"Daily": "Date", "Weekly": "Week", "Monthly": "Month", "All Time": "Month"}
group_col = group_col_map[granularity]
filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

st.markdown("<div style='margin-top: 1.5rem; margin-bottom: 2.5rem; border-bottom: 1px solid rgba(128,128,128,0.15);'></div>", unsafe_allow_html=True)

# Helper WHO growth functions
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

# DETERMINISTIC AI CONTEXT GENERATORS
def build_growth_ai_context(db_keyword, who_option_name):
    w_df = df[df['Event Type'] == db_keyword].copy()
    if w_df.empty: return f"Category: Growth ({who_option_name}). No data logged."
    w_df = w_df.sort_values('DateTime', ascending=True)
    w_df['Age_Months'] = (pd.to_datetime(w_df['Date']) - pd.to_datetime(baby_dob)).dt.days / 30.437
    w_df = w_df[w_df['Age_Months'] >= 0]
    if w_df.empty: return f"Category: Growth ({who_option_name}). No data logged."
    latest_data = w_df.iloc[-1]
    m_x = np.arange(25)
    p50 = get_who_data(baby_gender, who_option_name)
    m3, m15, m85, m97 = get_hk_mults(who_option_name)
    p3, p97 = p50*m3, p50*m97
    
    v = latest_data['Value (Optional)']
    age = latest_data['Age_Months']
    lp50 = np.interp(age, m_x, p50)
    lp3 = np.interp(age, m_x, p3)
    lp97 = np.interp(age, m_x, p97)
    z = (v - lp50) / ((lp97 - lp3) / 3.76)
    pct = (1 / (1 + np.exp(-1.702 * z))) * 100
    unit_str = db_keyword.split('(')[1].replace(')','')
    
    return f"Category: Growth ({who_option_name}). Latest {who_option_name.split(' ')[1]}: {v:.1f} {unit_str} at age {age:.1f} months (~{pct:.0f}th percentile)."

act_mapping = {
    "🛌 Sleep (hrs)": ("Sleep", "Duration (hrs)", COLOR_MAP["🛌 Sleep (hrs)"], "hrs"),
    "🌡️ Temp (°C)": ("Temp", "Temperature (°C)", COLOR_MAP["🌡️ Temp (°C)"], "°C"),
    "💊 Meds (Cnt)": ("Meds", "Dose Count(s)", COLOR_MAP["💊 Meds (Cnt)"], "doses")
}

def build_health_ai_context(act_opt):
    keyword, y_title, act_color, unit = act_mapping[act_opt]
    act_df = filtered_df[filtered_df['Event Type'].str.contains(keyword, case=False, na=False)].copy()
    if act_df.empty: return f"Category: Health ({act_opt}). No data logged in this period."
    avg_act = act_df['Value (Optional)'].mean()
    t_health_df = today_df[today_df['Event Type'].str.contains(keyword, case=False, na=False)]
    r_health_df = recent_7d_df[recent_7d_df['Event Type'].str.contains(keyword, case=False, na=False)]
    
    if keyword == "Temp":
        t_val = t_health_df['Value (Optional)'].mean() if not t_health_df.empty else 0
        r_val = r_health_df['Value (Optional)'].mean() if not r_health_df.empty else 0
        return f"Category: Body Temperature. Today's Avg: {t_val:.1f}°C. Recent 7-Day Avg: {r_val:.1f}°C. Selected Range Avg: {avg_act:.1f}°C across {len(act_df)} records."
    elif keyword == "Sleep":
        t_val = t_health_df['Value (Optional)'].sum() if not t_health_df.empty else 0
        r_val = r_health_df['Value (Optional)'].sum() / 7 if not r_health_df.empty else 0
        return f"Category: Sleep. Today: {t_val:.1f} hrs. Recent 7-Day Avg: {r_val:.1f} hrs/day. Selected Range Avg: {avg_act:.1f} hrs/record across {len(act_df)} records."
    else:
        t_val = len(t_health_df)
        r_val = len(r_health_df) / 7
        return f"Category: Medication. Today: {t_val} doses. Recent 7-Day Avg: {r_val:.1f} doses/day. Selected Range Total: {len(act_df)} doses."

# ==========================================
# 6. CHARTS & ANALYTICS
# ==========================================
st.markdown('<div id="insights"></div>', unsafe_allow_html=True)
st.subheader("📊 Insights")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "⏰ Today", "🍼 Milk", "🚽 Diapers", "🧴 Pumping", "🛟 Tummy", "📈 Growth", "🩺 Health", "💉 Vaccine"
])

# TAB 1: TODAY
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
            lambda t: t.update(mode='markers+text', marker=dict(opacity=0.75, line=dict(width=1, color='white')), textposition='top center', textfont=dict(weight='bold'), texttemplate='%{text}' + get_unit_from_name(t.name)) if "(Cnt)" not in t.name else t.update(mode='markers', marker=dict(opacity=0.75, line=dict(width=1, color='white')), text=None)
        )
        
        fig_today_timeline.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
        fig_today_timeline = style_plotly_figure(fig_today_timeline, title_text="⏰ Last 24 Hours Activity Timeline", height=450, is_scatter=True, x_tickformat="%d-%H", x_dtick=10800000, y_tickangle=-45)
        fig_today_timeline.update_layout(showlegend=False, yaxis=dict(title=dict(text=""), showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=10.5), automargin=True))
        st.plotly_chart(fig_today_timeline, use_container_width=True)
        
        st.caption("ℹ️ *Interactive scatter timeline displaying all events logged within the last 24 hours.*")

        # --- SAFELY COMPUTE 24H METRICS INSIDE TAB 1 SCOPE ---
        t_formula = today_24h_df[today_24h_df['Event Type'].str.contains("Formula", case=False, na=False)]['Value (Optional)'].sum()
        t_bm = today_24h_df[today_24h_df['Event Type'].str.contains("Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
        t_milk = t_formula + t_bm
        t_feed_cnt = len(today_24h_df[today_24h_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)])
        t_avg_feed = (t_milk / t_feed_cnt) if t_feed_cnt > 0 else 0
        
        t_diaper_events = today_24h_df[today_24h_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
        t_diaper_changes = t_diaper_events['DateTime'].nunique() if not t_diaper_events.empty else 0
        t_wet = len(today_24h_df[today_24h_df['Event Type'].str.contains("Wet Diaper", case=False, na=False)])
        t_poop = len(today_24h_df[today_24h_df['Event Type'].str.contains("Poop", case=False, na=False)])
        
        t_tummy = today_24h_df[today_24h_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()
        t_sleep = today_24h_df[today_24h_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
        t_meds = len(today_24h_df[today_24h_df['Event Type'].str.contains("Meds", case=False, na=False)])

        feed_cnt_7d = len(recent_7d_df[recent_7d_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]) / 7
        r_diaper_events = recent_7d_df[recent_7d_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
        diaper_cnt_7d = (r_diaper_events.groupby('Date')['DateTime'].nunique().sum() / 7) if not r_diaper_events.empty else 0
        
        analysis = f"""• **Milk Intake:** {int(t_milk):,} mL across {t_feed_cnt} feed(s) (Avg: ~{int(t_avg_feed)} mL | Form: {int(t_formula):,} mL, BM: {int(t_bm):,} mL)
• **Diaper Output:** {t_diaper_changes} change(s) ({t_wet} wet, {t_poop} poop)
• **Activity & Rest:** {int(t_tummy)} min tummy time | {int(t_sleep)} hrs rest | {t_meds} med dose(s)"""

        ai_context = f"Category: 24h Overview. Today: {t_feed_cnt} feeds, {t_diaper_changes} diaper changes. Recent 7-Day Avg: {feed_cnt_7d:.1f} feeds/day, {diaper_cnt_7d:.1f} diapers/day."
        render_insight_card(analysis, ai_prompt_context=ai_context, category_df=today_24h_df, category_key="today")
    else: 
        render_empty_state("No Events Logged in the Last 24 Hours")

# ==========================================
# TAB 2: MILK
# ==========================================
with tab2:
    milk_df = filtered_df[filtered_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)].copy()
    if not milk_df.empty:
        milk_df['Category'] = milk_df['Event Type'].apply(lambda x: "🤱 Breast Milk (mL)" if "breast" in x.lower() else "🍼 Formula (mL)")
        grouped_vol = milk_df.groupby([group_col, 'Category'])['Value (Optional)'].sum().reset_index()
        grouped_count = milk_df.groupby(group_col).size().reset_index(name='Total Feeds Count')
        
        total_per_x = milk_df.groupby(group_col)['Value (Optional)'].sum().reset_index().sort_values(group_col)
        total_per_x['Trend'] = total_per_x['Value (Optional)'].rolling(window=min(7, len(total_per_x)), min_periods=1).mean()

        grouped_vol[group_col] = grouped_vol[group_col].apply(format_x_label)
        grouped_count[group_col] = grouped_count[group_col].apply(format_x_label)
        total_per_x[group_col] = total_per_x[group_col].apply(format_x_label)
        is_single = len(grouped_count[group_col].unique()) == 1
        
        fig_milk = make_subplots(specs=[[{"secondary_y": True}]])
        df_f = grouped_vol[grouped_vol['Category'] == '🍼 Formula (mL)']
        if not df_f.empty: 
            fig_milk.add_trace(go.Bar(name='🍼 Formula (mL)', x=df_f[group_col].astype(str), y=df_f['Value (Optional)'], marker_color="#38bdf8", width=0.25 if is_single else None, text=df_f['Value (Optional)'], textposition='inside', textfont=dict(weight='bold', color='white'), hovertemplate='%{y} mL<extra></extra>'), secondary_y=False)
            
        df_bm = grouped_vol[grouped_vol['Category'] == '🤱 Breast Milk (mL)']
        if not df_bm.empty: 
            fig_milk.add_trace(go.Bar(name='🤱 Breast Milk (mL)', x=df_bm[group_col].astype(str), y=df_bm['Value (Optional)'], marker_color="#94a3b8", width=0.25 if is_single else None, hovertemplate='%{y} mL<extra></extra>'), secondary_y=False)
            
        fig_milk.add_trace(go.Scatter(name='🔢 Feed Count(s)', x=grouped_count[group_col].astype(str), y=grouped_count['Total Feeds Count'], mode='lines+markers+text', text=grouped_count['Total Feeds Count'], textposition="top center", textfont=dict(size=10.5, weight='bold'), line=dict(color='#f97316', width=3, shape='spline', smoothing=1.3), marker=dict(size=10, symbol='circle', color='#f97316', line=dict(width=2, color='#ffffff')), hovertemplate='%{y} feeds<extra></extra>'), secondary_y=True)
        fig_milk.add_trace(go.Scatter(name='📈 Vol Trend', x=total_per_x[group_col].astype(str), y=total_per_x['Trend'], mode='lines', line=dict(color='#64748b', width=2, shape='spline'), hovertemplate='Avg Trend: %{y:.0f} mL<extra></extra>'), secondary_y=False)
        
        fig_milk = style_plotly_figure(fig_milk, title_text=f"🍼 Milk Intake Volume & Feed Count — {granularity}", height=490, single_point=is_single)
        fig_milk.update_layout(barmode='stack')
        st.plotly_chart(fig_milk, use_container_width=True)
        
        st.caption("ℹ️ *Combines stacked Formula and Breast Milk volume (mL) with Feed Count(s).*")

        # --- LOCAL METRICS COMPUTATION ---
        avg_vol = total_per_x['Value (Optional)'].mean()
        t_milk = today_df[today_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]['Value (Optional)'].sum()
        milk_7d = recent_7d_df[recent_7d_df['Event Type'].str.contains("Formula|Breast Milk", case=False, na=False)]['Value (Optional)'].sum() / 7
        f_vol = milk_df[milk_df['Category'] == '🍼 Formula (mL)']['Value (Optional)'].sum()
        bm_vol = milk_df[milk_df['Category'] == '🤱 Breast Milk (mL)']['Value (Optional)'].sum()

        hardcoded_milk = f"""• **Intake Overview:** Total **{int(grouped_vol['Value (Optional)'].sum()):,} mL** across **{len(milk_df)}** feeds ({granularity.lower()} avg: **{avg_vol:.0f} mL**).
• **Formula vs. BM:** Formula **{int(f_vol):,} mL** | BM **{int(bm_vol):,} mL**.
• **Today's Status:** **{int(t_milk):,} mL** logged today (7-day baseline avg: ~{int(milk_7d):,} mL/day)."""

        ai_milk_context = f"Category: Milk Intake. Today: {t_milk:.0f} mL. Recent 7-Day Avg (excluding today): {milk_7d:.0f} mL/day. Selected Range ({start_date} to {end_date}) Avg: {avg_vol:.0f} mL per {granularity.lower()}."
        render_insight_card(hardcoded_milk, ai_prompt_context=ai_milk_context, category_df=milk_df, category_key="milk")
    else: 
        render_empty_state("No Feeding Data Logged in this period")


# ==========================================
# TAB 3: DIAPERS
# ==========================================
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
        
        st.caption("ℹ️ *Compares Wet Diapers and Poop counts.*")

        # --- DEDUPLICATED DIAPER METRICS COMPUTATION ---
        avg_diapers = diaper_df.groupby('Date')['DateTime'].nunique().mean()
        wets = len(diaper_df[diaper_df['Category'] == '💧 Wet Diaper (Cnt)'])
        poops = len(diaper_df[diaper_df['Category'] == '🚽 Poop (Cnt)'])
        
        t_diaper_events = today_df[today_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
        t_diaper = t_diaper_events['DateTime'].nunique() if not t_diaper_events.empty else 0
        
        r_diaper_events = recent_7d_df[recent_7d_df['Event Type'].str.contains("Wet Diaper|Poop", case=False, na=False)]
        diaper_7d = (r_diaper_events.groupby('Date')['DateTime'].nunique().sum() / 7) if not r_diaper_events.empty else 0
        
        hardcoded_diaper = f"""• **Output Breakdown:** **{wets}** wet diapers and **{poops}** poop diapers recorded across **{len(diaper_df)}** total events.
• **Daily Pace:** Averaging **{avg_diapers:.1f}** diaper changes/day over selected range.
• **Today's Status:** **{t_diaper}** change(s) today (7-day baseline avg: ~{diaper_7d:.1f} changes/day)."""

        ai_diaper_context = f"Category: Diaper Output. Today: {t_diaper} diaper changes. Recent 7-Day Avg (excluding today): {diaper_7d:.1f} changes/day. Selected Range ({start_date} to {end_date}) Avg: {avg_diapers:.1f} changes/day. (Total events in range: {wets} wet, {poops} poops)."
        render_insight_card(hardcoded_diaper, ai_prompt_context=ai_diaper_context, category_df=diaper_df, category_key="diapers")
    else: 
        render_empty_state("No Diaper Data Logged in this period")


# ==========================================
# TAB 4: PUMPING
# ==========================================
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
        
        st.caption("ℹ️ *Displays recorded pumping volume (mL).*")

        # --- LOCAL METRICS COMPUTATION ---
        avg_pump = pump_df['Value (Optional)'].sum() / max(1, len(pump_df))
        t_pump = today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum()
        p_cnt_today = len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])
        pump_7d = recent_7d_df[recent_7d_df['Event Type'].str.contains("Pumping", case=False, na=False)]['Value (Optional)'].sum() / 7

        hardcoded_pump = f"""• **Pumping Yield:** Total **{int(pump_df['Value (Optional)'].sum()):,} mL** produced across **{len(pump_df)}** sessions.
• **Session Average:** Yielding **{avg_pump:.0f} mL** per pumping session.
• **Today's Output:** **{int(t_pump):,} mL** pumped today across {p_cnt_today} session(s)."""

        ai_pump_context = f"Category: Pumping. Today: {t_pump:.0f} mL. Recent 7-Day Avg (excluding today): {pump_7d:.0f} mL/day. Selected Range ({start_date} to {end_date}): {len(pump_df)} sessions, avg {avg_pump:.0f} mL/session."
        render_insight_card(hardcoded_pump, ai_prompt_context=ai_pump_context, category_df=pump_df, category_key="pumping", subject="Yanyi")
    else: 
        render_empty_state("No Pumping Data Logged in this period")


# ==========================================
# TAB 5: TUMMY TIME
# ==========================================
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
        
        st.caption("ℹ️ *Displays recorded tummy time duration (Mins).*")

        # --- LOCAL METRICS COMPUTATION ---
        total_tummy = tummy_df['Value (Optional)'].sum()
        avg_tummy = total_tummy / max(1, len(tummy_df))
        t_tummy = today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum()
        tummy_cnt_today = len(today_df[today_df['Event Type'].str.contains("Tummy Time", case=False, na=False)])
        tummy_7d = recent_7d_df[recent_7d_df['Event Type'].str.contains("Tummy Time", case=False, na=False)]['Value (Optional)'].sum() / 7

        hardcoded_tummy = f"""• **Total Activity:** **{total_tummy:.0f} total minutes** logged across **{len(tummy_df)}** session(s).
• **Session Average:** Averaging **{avg_tummy:.1f} minutes** per tummy time session.
• **Today's Progress:** **{int(t_tummy)} min(s)** completed today ({tummy_cnt_today} session(s))."""

        ai_tummy_context = f"Category: Tummy Time. Today: {t_tummy:.0f} mins. Recent 7-Day Avg (excluding today): {tummy_7d:.0f} mins/day. Selected Range ({start_date} to {end_date}): {total_tummy:.0f} total mins, avg {avg_tummy:.0f} mins/session."
        render_insight_card(hardcoded_tummy, ai_prompt_context=ai_tummy_context, category_df=tummy_df, category_key="tummy")
    else: 
        render_empty_state("No Tummy Time Data Logged in this period")


# ==========================================
# TAB 6: GROWTH
# ==========================================
with tab6:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; text-align: center; margin-bottom: 10px;'><a href='https://www.dh.gov.hk/english/useful/useful_HP_Growth_Chart/files/growth_charts.pdf' target='_blank' style='color: #64748b; text-decoration: none; opacity: 0.8;'>📄 Official HK Growth Charts Reference (PDF)</a></p>", unsafe_allow_html=True)

    who_option = st.radio("Select Growth Chart:", options=["⚖️ Weight", "🏔️ Height", "🐷 Head"], horizontal=True, label_visibility="collapsed")
    
    # # STRICT SEQUENTIAL PRE-FETCHING FOR ALL 3 GROWTH OPTIONS
    # if use_ai_insights:
    #     for prefetch_opt in ["⚖️ Weight", "🏔️ Height", "🐷 Head"]:
    #         if prefetch_opt != who_option:
    #             p_keyword = "⚖️ Weight (kg)" if "Weight" in prefetch_opt else ("🏔️ Height (cm)" if "Height" in prefetch_opt else "🐷 Head Size (cm)")
    #             p_context = build_growth_ai_context(p_keyword, prefetch_opt)
    #             p_df = df[df['Event Type'] == p_keyword]
    #             render_insight_card("", ai_prompt_context=p_context, category_df=p_df, hidden_prefetch=True)
    
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
            name=who_option.split(' ')[1], text=hover_text, hovertemplate="%{text}"
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
            title=dict(text=f"📈 {who_option.split(' ')[1]}", y=0.97, x=0.5, xanchor="center", font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif", size=17, color="#0f172a")),
            height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=2, r=2, t=60, b=20),
            xaxis=dict(title="Age (Months)", showgrid=True, gridcolor="#f1f5f9", tickformat=".0f", range=[range_min, x_max_buffer]),
            yaxis=dict(title="", showgrid=True, gridcolor="#f1f5f9", range=[y_lower, y_upper]),
            showlegend=False, hovermode="x unified"
        )
        st.plotly_chart(fig_who, use_container_width=True)
        
        st.caption(f"ℹ️ *Interactive Growth Chart for {baby_gender}s based on standard HK lines.*")
        
        latest_data = who_df.iloc[-1]
        latest_pct = latest_data['Est_Pct']
        latest_val = latest_data['Value (Optional)']
        
        # --- RICH HARDCODED SUMMARY WITH VARIANCE FROM 50th PERCENTILE ---
        p50_val = np.interp(latest_data['Age_Months'], m_x, p50)
        diff_p50 = latest_val - p50_val
        diff_str = f"+{diff_p50:.1f}" if diff_p50 >= 0 else f"{diff_p50:.1f}"
        
        hardcoded_growth = f"""• **Latest Measurement ({latest_data['Date']}):** **{latest_val:.1f} {unit_str}** at **{latest_data['Age_Months']:.1f} months** old.
• **HK Percentile Rank:** ~**{latest_pct:.0f}th percentile** (Benchmark 50th percentile for exact age: **{p50_val:.1f} {unit_str}** | Variance: **{diff_str} {unit_str}**).
• **Growth Trajectory:** **{len(who_df)}** total data point(s) recorded in database."""

        ai_growth_context = build_growth_ai_context(db_keyword, who_option)
        growth_key = f"growth_{who_option.split(' ')[1].lower()}"
        render_insight_card(hardcoded_growth, ai_prompt_context=ai_growth_context, category_df=who_df, category_key=growth_key)
    else: 
        render_empty_state(f"No {who_option} Data Logged")


# ==========================================
# TAB 7: HEALTH
# ==========================================
with tab7:
    act_option = st.radio("Select Category:", options=["🛌 Sleep (hrs)", "🌡️ Temp (°C)", "💊 Meds (Cnt)"], index=0, horizontal=True, label_visibility="collapsed")
    
    # STRICT SEQUENTIAL PRE-FETCHING FOR ALL HEALTH OPTIONS
    # if use_ai_insights:
    #     for prefetch_opt in ["🛌 Sleep (hrs)", "🌡️ Temp (°C)", "💊 Meds (Cnt)"]:
    #         if prefetch_opt != act_option:
    #             p_context = build_health_ai_context(prefetch_opt)
    #             p_kw = act_mapping[prefetch_opt][0]
    #             p_df = filtered_df[filtered_df['Event Type'].str.contains(p_kw, case=False, na=False)]
    #             render_insight_card("", ai_prompt_context=p_context, category_df=p_df, hidden_prefetch=True)
    
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
        
        st.caption(f"ℹ️ *Displays recorded {act_option} data.*")

        # --- LOCAL METRICS COMPUTATION ---
        avg_act = act_df['Value (Optional)'].mean()
        t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
        t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None
        t_sleep = today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)]['Value (Optional)'].sum()
        t_meds = len(today_df[today_df['Event Type'].str.contains("Meds", case=False, na=False)])

        if keyword == "Temp":
            max_temp = act_df['Value (Optional)'].max()
            min_temp = act_df['Value (Optional)'].min()
            fever_status = "⚠️ Fever detected in history (>37.5°C)" if max_temp >= 37.5 else "✅ Normal limits (36.5–37.5°C)"
            hardcoded_health = f"""• **Temperature Range:** Selected range avg **{avg_act:.1f} °C** (Min: {min_temp:.1f} °C | Max: {max_temp:.1f} °C across {len(act_df)} readings).
• **Clinical Status:** {fever_status}.
• **Today's Reading:** {f"{t_latest_temp:.1f} °C" if t_latest_temp is not None else "No readings today"}."""

        elif keyword == "Sleep":
            total_sleep_hrs = act_df['Value (Optional)'].sum()
            hardcoded_health = f"""• **Sleep Duration:** Total **{total_sleep_hrs:.1f} hrs** across **{len(act_df)}** sleep period(s) (Avg: **{avg_act:.1f} hrs** per period).
• **Daily Pace:** Averaging ~**{total_sleep_hrs / max(1, (end_date - start_date).days + 1):.1f} hrs/day** over selected date range.
• **Today's Rest:** **{int(t_sleep)} hr(s)** logged today."""

        else: # Meds
            hardcoded_health = f"""• **Medication Tracking:** Total **{len(act_df)}** dose(s) administered in selected date range.
• **Daily Pace:** Averaging ~**{len(act_df) / max(1, (end_date - start_date).days + 1):.1f} dose(s)/day**.
• **Today's Status:** **{t_meds}** dose(s) recorded today."""

        ai_health_context = build_health_ai_context(act_option)
        health_key = f"health_{act_option.split(' ')[1].lower()}"
        render_insight_card(hardcoded_health, ai_prompt_context=ai_health_context, category_df=act_df, category_key=health_key)
    else: 
        render_empty_state(f"No {act_option.split(' ')[1]} Data Logged in this period")


# ==========================================
# TAB 8: VACCINE
# ==========================================
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
        {"Age": "6 mo", "Days": 180, "Group": "Pneumococcal", "Vaccine": "肺炎球菌 第三劑 (PCV 3rd)", "Disease": "肺炎球菌感染 (Pneumococcal)", "Provider": "🏥 母嬰", "Desc": "第三針", "Optional": False, "Match": get_date("pcv|pneumo|肺炎", 2)},
        {"Age": "6 mo", "Days": 180, "Group": "Rotavirus", "Vaccine": "輪狀病毒 第三劑 (Rotavirus 3rd)", "Disease": "輪狀病毒腸胃炎 (Rotavirus)", "Provider": "💰 私家", "Desc": "視乎藥廠", "Optional": True, "Match": get_date("rota|輪狀", 2)},
        {"Age": "6 mo", "Days": 180, "Group": "Influenza", "Vaccine": "季節性流感 (Influenza)", "Disease": "流行性感冒 (Flu)", "Provider": "💰 私家 / 🏥 診所", "Desc": "滿6個月可打", "Optional": True, "Match": get_date("flu|流感", 0)}
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
            "Age": s["Age"], "Group": s["Group"], "Disease Prevented": s["Disease"],
            "Vaccine / 疫苗": v_name_formatted, "Type": s["Provider"], "Description": s["Desc"],
            "Date Injected": str(s["Match"]) if s["Match"] else "-", "Status": status,
            "Optional": s["Optional"], "Days": s["Days"]
        })
        
    styled_df = pd.DataFrame(rows)
    total_vacs = len(vac_df)
    upcoming = [r for r in rows if r["Status"] == "🟡 Due Soon" or r["Status"] == "⚠️ Overdue"]
    next_due = upcoming[0]["Vaccine / 疫苗"] if upcoming else "All caught up"
    
    overdue_cnt = len([r for r in rows if r["Status"] == "⚠️ Overdue"])
    due_soon_cnt = len([r for r in rows if r["Status"] == "🟡 Due Soon"])
    
    status_summary = []
    if overdue_cnt > 0: status_summary.append(f"⚠️ {overdue_cnt} Overdue")
    if due_soon_cnt > 0: status_summary.append(f"🟡 {due_soon_cnt} Due Soon")
    status_str = " | ".join(status_summary) if status_summary else "✅ All current milestones up to date"

    hardcoded_vac = f"""• **Vaccine Progress:** **{total_vacs}** dose(s) recorded in database.
• **Immunization Status:** {status_str}.
• **Next Scheduled Milestone:** **{next_due}**."""

    ai_vac_context = f"Category: Vaccines. Total administered so far: {total_vacs}. Next scheduled action required: {next_due}. Check HK standard pediatric guidelines for a {age_days}-day-old / {age_days/30.437:.1f}-month-old baby girl. Cross-reference all administered vaccines against standard HK requirements to identify any missing, upcoming, or additional recommended shots."
    
    render_insight_card(hardcoded_vac, ai_prompt_context=ai_vac_context, category_df=vac_df, category_key="vaccines")

    v_col1, v_col2 = st.columns([1, 1])
    with v_col1: grouping = st.radio("Sort View:", ["By Age Milestone", "By Vaccine Type"], horizontal=True, label_visibility="collapsed")
    
    if grouping == "By Vaccine Type": styled_df = styled_df.sort_values(by=["Group", "Days"]).reset_index(drop=True)
    else: styled_df = styled_df.sort_values(by="Days").reset_index(drop=True)

    def apply_vaccine_colors(row):
        if '✅' in row['Status']: return ['background-color: #dcfce7; color: #166534'] * 7
        elif '🟡' in row['Status']: return ['background-color: #fef08a; color: #854d0e'] * 7
        elif '⚠️' in row['Status']: return ['background-color: #fee2e2; color: #991b1b'] * 7
        elif '(Optional)' in row['Vaccine / 疫苗']: return ['background-color: #f8fafc; color: #475569'] * 7
        else: return [''] * 7

    dropped_df = styled_df.drop(columns=["Days", "Group", "Optional"])
    styled_table = dropped_df.style.apply(apply_vaccine_colors, axis=1)
    
    st.dataframe(styled_table, use_container_width=True, hide_index=True, height=550)

# ==========================================
# 7. UNIFIED MASTER DATABASE & EDITOR
# ==========================================
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

st.markdown('<div id="database" style="padding-top: 3.5rem;"></div>', unsafe_allow_html=True)

db_c1, db_c2 = st.columns([3, 1], vertical_alignment="bottom")
with db_c1: st.subheader("📋 Master Database")
with db_c2:
    if not st.session_state.edit_mode:
        if st.button("🔓 Enable Edit Mode", use_container_width=True):
            st.cache_data.clear()
            st.session_state.edit_mode = True
            st.rerun()

master_df = df[['SheetRow', 'DateTime', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)']].copy()
master_df['DateTime'] = master_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

filter_c1, filter_c2 = st.columns([1, 1])
with filter_c1: selected_events = st.multiselect("🏷️ Filter Event Types:", options=ALL_EVENT_CATEGORIES, default=[], placeholder="Choose event types")
with filter_c2: search_query = st.text_input("🔍 Search Anything:", "", placeholder="Type date, Formula, notes...")

table_df = master_df.copy()

if selected_events: table_df = table_df[table_df['Event Type'].isin(selected_events)]

if search_query:
    search_mask = pd.Series(False, index=table_df.index)
    for col in table_df.columns:
        search_mask |= table_df[col].astype(str).str.contains(search_query, case=False, na=False)
    table_df = table_df[search_mask]

current_max_time = df['DateTime'].max() if not df.empty else None

col_config = {
    "DateTime": st.column_config.DatetimeColumn("DateTime", format="YYYY-MM-DD HH:mm", width="medium", required=True),
    "Event Type": st.column_config.SelectboxColumn("Event Type", options=ALL_EVENT_CATEGORIES, width="medium", required=True),
    "Value (Optional)": st.column_config.NumberColumn("Value", width="small"),
    "Notes / Details (Optional)": st.column_config.TextColumn("Notes / Details (Optional)", width="large")
}

display_df = table_df[['DateTime', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)']].copy()
display_df['DateTime'] = pd.to_datetime(display_df['DateTime'], errors='coerce')

if st.session_state.edit_mode:
    with st.form("database_editor_form"):
        st.markdown("""
        <div style="background-color: #fef2f2; border: 1px solid #f87171; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <strong style="color: #991b1b;">⚠️ Edit Mode Active (Surgical Sync)</strong><br>
            <span style="color: #7f1d1d; font-size: 0.85rem;">Edits target <b>Columns D through I</b> only, preserving ArrayFormulas in A, B, C.</span>
        </div>
        """, unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1: submit_button = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with btn_col2: cancel_button = st.form_submit_button("🔒 Cancel Editing", use_container_width=True)

        edited_df = st.data_editor(display_df, use_container_width=True, height=900, num_rows="dynamic", column_config=col_config)
        
        if cancel_button:
            st.session_state.edit_mode = False
            st.rerun()

        if submit_button:
            with st.spinner("Executing surgical cell updates..."):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    secrets_dict = dict(st.secrets["connections"]["gsheets"])
                    secrets_dict.pop("spreadsheet", None); secrets_dict.pop("worksheet", None); secrets_dict.pop("type", None)
                    
                    client = gspread.service_account_from_dict(secrets_dict)
                    sheet = client.open_by_url(sheet_url_input).worksheet("Log")
                    
                    # Fetch live data safely using gspread instead of conn.read
                    live_data = sheet.get_all_values()
                    live_df = pd.DataFrame(live_data[1:], columns=live_data[0]) if len(live_data) > 1 else pd.DataFrame()
                    live_df.replace("", np.nan, inplace=True)
                    
                    live_max_time = pd.to_datetime(live_df['DateTime'], errors='coerce').max() if 'DateTime' in live_df.columns else None
                        
                    if current_max_time and live_max_time and live_max_time > current_max_time:
                        st.error("🚨 **CRITICAL COLLISION:** Someone logged new data to the spreadsheet while you were editing!")
                    else:
                        now_timestamp = (datetime.utcnow() + timedelta(hours=tz_offset)).strftime('%Y-%m-%d %H:%M:%S')
                        deleted_indices = set(table_df.index) - set(edited_df.index)
                        deleted_sheet_rows = table_df.loc[list(deleted_indices), 'SheetRow'].tolist()
                        new_rows_df = edited_df[~edited_df.index.isin(table_df.index)]
                        common_indices = set(table_df.index).intersection(set(edited_df.index))
                        edits_to_push = []
                        
                        for idx in common_indices:
                            old_row, new_row = table_df.loc[idx], edited_df.loc[idx]
                            sheet_row = int(old_row['SheetRow'])
                            row_changed = False
                            
                            new_dt_str = pd.to_datetime(new_row['DateTime']).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(new_row['DateTime']) else ""
                            if str(old_row['DateTime']) != new_dt_str:
                                edits_to_push.append(gspread.Cell(row=sheet_row, col=5, value=new_dt_str)); row_changed = True
                            if str(old_row['Event Type']) != str(new_row['Event Type']):
                                edits_to_push.append(gspread.Cell(row=sheet_row, col=6, value=str(new_row['Event Type']))); row_changed = True
                            if str(old_row['Value (Optional)']) != str(new_row['Value (Optional)']):
                                edits_to_push.append(gspread.Cell(row=sheet_row, col=7, value=new_row['Value (Optional)'] if pd.notna(new_row['Value (Optional)']) else "")); row_changed = True
                            if str(old_row['Notes / Details (Optional)']) != str(new_row['Notes / Details (Optional)']):
                                edits_to_push.append(gspread.Cell(row=sheet_row, col=8, value=str(new_row['Notes / Details (Optional)']) if pd.notna(new_row['Notes / Details (Optional)']) else "")); row_changed = True
                            
                            if row_changed:
                                edits_to_push.append(gspread.Cell(row=sheet_row, col=9, value=now_timestamp))
                        
                        if edits_to_push: sheet.update_cells(edits_to_push, value_input_option='USER_ENTERED')
                        if deleted_sheet_rows:
                            for r in sorted(deleted_sheet_rows, reverse=True): sheet.delete_rows(r)
                                
                        if not new_rows_df.empty:
                            dt_col = sheet.col_values(5)
                            next_row = len(dt_col) + 1
                            new_data = []
                            for _, r in new_rows_df.iterrows():
                                dt_str = pd.to_datetime(r['DateTime']).strftime('%Y-%m-%d %H:%M:%S') if pd.notna(r['DateTime']) else now_timestamp
                                new_data.append([now_timestamp, dt_str, str(r['Event Type']), r['Value (Optional)'] if pd.notna(r['Value (Optional)']) else "", str(r['Notes / Details (Optional)']) if pd.notna(r['Notes / Details (Optional)']) else "", now_timestamp])
                            sheet.update(values=new_data, range_name=f"D{next_row}:I{next_row + len(new_data) - 1}", value_input_option='USER_ENTERED')
                            
                        st.success("✅ Updates pushed successfully!")
                        st.session_state.edit_mode = False
                        st.cache_data.clear()
                        st.rerun()
                except Exception as e: st.error(f"Failed to update Google Sheets: {e}")
else:
    st.dataframe(display_df, use_container_width=True, height=900, column_config=col_config)

st.markdown(f'<div class="raw-log-count-text">Showing {len(table_df)} entry(s) matching your criteria.</div>', unsafe_allow_html=True)
st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)

# ==========================================
# 8. BACKGROUND AUTO-RETRY ENGINE
# ==========================================
if st.session_state.get('needs_auto_retry', False):
    st.session_state.needs_auto_retry = False
    
    # Increment the retry counter
    st.session_state.ai_retry_count = st.session_state.get('ai_retry_count', 0) + 1
    
    # Only retry if we haven't hit the limit
    if st.session_state.ai_retry_count < 3:
        import time
        time.sleep(3.5) # Wait 3.5 seconds to let the rate limit clear
        st.rerun()
    else:
        st.error("🛑 **Auto-Retry Paused:** OpenRouter's free tier is currently rate-limiting your requests. Please wait a few minutes and click '🔄 Force Refresh AI Summaries' in the sidebar.")
