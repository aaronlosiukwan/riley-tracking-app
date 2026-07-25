import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
from streamlit_gsheets import GSheetsConnection

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

st.markdown("""
    <style>
    /* Apple System Font Stack - Excludes 'span' to fix Streamlit's native Icons! */
    html, body, div, p, a, h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        letter-spacing: -0.01em;
    }

    /* Relaxed Spacing for Breathing Room */
    div[data-testid="stVerticalBlock"] { gap: 0.75rem !important; }

    /* Premium Highlight Cards (Apple Health Style - No harsh borders, soft shadow) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #f1f5f9;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        color: #0f172a !important;
    }

    /* Empty State */
    .empty-state {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        color: #64748b;
        font-weight: 500;
    }

    /* Navigation Links */
    .toc-button {
        display: block; padding: 8px 12px; margin: 4px 0; border-radius: 8px;
        color: #334155; text-decoration: none; font-weight: 500; background-color: transparent;
        transition: all 0.2s; border: 1px solid transparent;
    }
    .toc-button:hover { background-color: #f1f5f9; border-color: #e2e8f0; }

    /* Top Header Spacing */
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) {
        align-items: center !important;
        margin-top: 1rem !important;
        margin-bottom: 2.5rem !important; 
    }
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-secondary"],
    div[data-testid="stHorizontalBlock"]:has(.app-main-title) [data-testid="baseButton-primary"] {
        height: 100% !important; padding: 12px 24px !important; margin: 0 !important;
        border-radius: 12px !important; font-weight: 600 !important; font-size: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AI ENGINE & DATA LOADER
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def call_ai(prompt_text, api_key_param, latest_data_timestamp):
    if not OPENAI_AVAILABLE: return "⚠️ **OpenAI package missing.** Please install `openai`."
    if not api_key_param: return "⚠️ **OpenRouter API Key missing.** Set `OPENROUTER_API_KEY` in Streamlit Secrets."
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key_param,
        default_headers={"HTTP-Referer": "https://streamlit.app", "X-Title": "Rileys Dash"}
    )
    
    try:
        chat_completion = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": "You are a data formatting tool. You are NOT a medical professional. Never give medical advice. Strictly summarize the numbers provided."},
                {"role": "user", "content": prompt_text}
            ],
        )
        content = chat_completion.choices[0].message.content
        if "User Safety" in content or "Unauthorized Advice" in content:
            return "⚠️ Safety Filter blocked response (Mistook for medical advice)."
        return content
    except Exception as e:
        if "429" in str(e):
            st.session_state.needs_auto_retry = True
            return "⚠️ API Busy. Auto-retrying background generation..."
        return f"⚠️ **AI Insight Error:** {e}"

@st.cache_data(ttl=600)
def load_sheet_data(url):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=url, ttl=0)
        df.columns = df.columns.astype(str).str.strip()
        
        if 'DateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
        elif 'EntryDateTime' in df.columns: df['DateTime'] = pd.to_datetime(df['EntryDateTime'], errors='coerce')
        else:
            date_cols = [c for c in df.columns if 'date' in c.lower()]
            if date_cols: df['DateTime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
        df = df.dropna(subset=['DateTime'])
        df['Date'] = df['DateTime'].dt.date
        
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
        st.error(f"Error loading Google Sheet: {e}")
        return pd.DataFrame()

# ==========================================
# 3. SIDEBAR NAVIGATION & SETTINGS
# ==========================================
st.sidebar.markdown("""
    <div style="margin-bottom: 12px;">
        <div style="font-weight: 700; font-size: 1.05rem; margin-bottom: 8px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px;">📌 Quick Navigation</div>
        <a href="#top-header" class="toc-button">✨ Today</a>
        <a href="#filters" class="toc-button">⚙️ Filters</a>
        <a href="#database" class="toc-button">📋 Database</a>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='font-weight: 700; font-size: 1.05rem; margin-bottom: 12px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 6px;'>⚙️ AI Configuration</div>", unsafe_allow_html=True)

if "ai_insights_enabled" not in st.session_state:
    st.session_state.ai_insights_enabled = False

use_ai_insights = st.sidebar.toggle("✨ Enable AI Insights", key="ai_insights_enabled")

if st.sidebar.button("🔄 Force Refresh AI Summaries", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1HV8aBFaZBPJfIeZgkicSO-zOQcPZJr8UBzRjHeyWBYw/edit?usp=sharing"
sheet_url_input = st.sidebar.text_input("Google Sheet URL", value=DEFAULT_SHEET_URL, type="password")

# ==========================================
# 4. LOAD & FILTER DATA
# ==========================================
df = load_sheet_data(sheet_url_input)
if df.empty:
    st.warning("No data found or URL is incorrect.")
    st.stop()

ALL_EVENT_CATEGORIES = sorted(df['Event Type'].dropna().unique().tolist())

st.markdown('<div id="top-header"></div>', unsafe_allow_html=True)
tc1, tc2, tc3 = st.columns([2, 1, 1])
with tc1: st.markdown('<h1 class="app-main-title" style="margin:0;">🍼 Riley\'s Dash</h1>', unsafe_allow_html=True)
with tc2: 
    if st.button("➕ Log Entry", type="primary", use_container_width=True): st.success("Use your iOS Shortcut to log new data!")
with tc3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown('<div id="filters"></div>', unsafe_allow_html=True)
date_filter = st.radio("📅 Date Range:", ["Last 7 Days", "Last 30 Days", "All Time"], index=0, horizontal=True)

today = datetime.now().date()
if date_filter == "Last 7 Days": start_date = today - timedelta(days=7)
elif date_filter == "Last 30 Days": start_date = today - timedelta(days=30)
else: start_date = df['Date'].min()

filtered_df = df[df['Date'] >= start_date]

# ==========================================
# 5. AI RENDER COMPONENT
# ==========================================
def render_insight_card(subject, context_data):
    api_key_param = st.secrets.get("OPENROUTER_API_KEY", None)
    latest_data_timestamp = df['DateTime'].max().strftime('%Y-%m-%d %H:%M:%S') if not df.empty else "None"
    
    if use_ai_insights:
        with st.spinner(f"🤖 Summarizing {subject}'s trends..."):
            prompt = f"""DATA CONTEXT:
{context_data}

ROLE: You are an automated data formatting tool. You are NOT a medical professional. Never give medical advice.
TASK: Write an analytical summary based STRICTLY on the numbers provided. The subject of this data is {subject}.

OUTPUT RESTRICTIONS:
- OUTPUT ONLY THE EXACT HTML STRUCTURE BELOW.
- DO NOT OUTPUT ANY METADATA (e.g., "User Safety: safe").
- DO NOT USE MARKDOWN (NO ** OR *).
- DO NOT ADD EXTRA BLANK LINES BETWEEN BULLET POINTS.

<b>High-Level Summary</b><br>
&bull; [Bullet point 1 highlighting a key metric]<br>
&bull; [Bullet point 2 highlighting a key metric]<br><br>
<b>Trend Analysis</b><br>
[Write a single paragraph (3-4 sentences) comparing Today vs. Recent Avg. Highlight any positive trends.]<br><br>
<b>Suggested Action</b><br>
[Write 1 brief sentence suggesting a practical next step based on the data.]
"""
            output_text = call_ai(prompt, api_key_param, latest_data_timestamp)
            
            # Markdown Cleanup & HTML Sanitization
            html_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', output_text)
            html_text = re.sub(r'^[-*]\s+(.*?)$', r'&bull; \1', html_text, flags=re.MULTILINE)
            html_text = html_text.replace('\n', '<br>').replace('<br><br><br>', '<br><br>')
            
            st.markdown(f"""
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; margin: 12px 0 24px 0; color: #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); font-size: 0.95rem; line-height: 1.5;">
                <strong style="color: #4c1d95; font-size: 1.05rem; display: block; margin-bottom: 12px;">✨ AI Insight</strong> 
                {html_text}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 12px; margin: 12px 0 24px 0; font-size: 0.9rem; color: #64748b;">
            💡 <b>Smart Tip:</b> Enable "AI Insights" in the sidebar for a detailed, AI-generated analysis of these trends!
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. DASHBOARD METRICS TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["🍼 Milk & Food", "🧻 Diapers", "🤱 Mom's Pumping"])

with tab1:
    st.subheader("Milk Intake")
    milk_df = filtered_df[filtered_df['Event Type'].str.contains('Milk|Formula', case=False, na=False)]
    if not milk_df.empty:
        total_vol = milk_df['Value (Optional)'].sum()
        count = len(milk_df)
        c1, c2 = st.columns(2)
        c1.metric("Total Volume", f"{total_vol:,.0f} mL")
        c2.metric("Total Feeds", f"{count}")
        
        context = f"Total Volume: {total_vol} mL. Total Feeds: {count}. Date Range: {start_date} to {today}"
        render_insight_card("Riley", context)
    else:
        st.markdown('<div class="empty-state">No Milk data found for this range.</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Diaper Log")
    diaper_df = filtered_df[filtered_df['Event Type'].str.contains('Diaper|Poop|Wet', case=False, na=False)]
    if not diaper_df.empty:
        total_diapers = len(diaper_df)
        st.metric("Total Changes", f"{total_diapers}")
        
        context = f"Total Diapers: {total_diapers}. Date Range: {start_date} to {today}"
        render_insight_card("Riley", context)
    else:
        st.markdown('<div class="empty-state">No Diaper data found for this range.</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("Mom's Pumping Log")
    pump_df = filtered_df[filtered_df['Event Type'].str.contains('Pump', case=False, na=False)]
    if not pump_df.empty:
        total_pump = pump_df['Value (Optional)'].sum()
        st.metric("Total Pumped", f"{total_pump:,.0f} mL")
        
        # NOTE: Passing 'Yanyi' as the subject to prevent attributing milk pumping to the baby!
        context = f"Total Pumped: {total_pump} mL. Date Range: {start_date} to {today}"
        render_insight_card("Yanyi", context)
    else:
        st.markdown('<div class="empty-state">No Pumping data found for this range.</div>', unsafe_allow_html=True)


# ==========================================
# 7. UNIFIED MASTER DATABASE & EDITOR
# ==========================================
st.markdown('<div id="database" style="padding-top: 3.5rem;"></div>', unsafe_allow_html=True)
st.subheader("📋 Master Database")
st.caption("Search, filter, and edit your logs directly. Click 'Save' below to safely merge edits with Google Sheets.")

filter_c1, filter_c2 = st.columns([1, 1])
with filter_c1: selected_events = st.multiselect("🏷️ Filter Event Types:", options=ALL_EVENT_CATEGORIES, default=[])
with filter_c2: search_query = st.text_input("🔍 Search Anything:", "", placeholder="Type notes, values, etc...")

# Maintain original index for safe merging
master_df = df.copy().reset_index(drop=True)
master_df['DateTime'] = master_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

table_df = master_df.copy()
if selected_events: 
    table_df = table_df[table_df['Event Type'].isin(selected_events)]

# SPEED UPGRADE: Vectorized Search Bar
if search_query:
    search_mask = pd.Series(False, index=table_df.index)
    for col in table_df.columns:
        search_mask |= table_df[col].astype(str).str.contains(search_query, case=False, na=False)
    table_df = table_df[search_mask]

edit_cols = ['DateTime', 'Event Type', 'Value (Optional)', 'Notes / Details (Optional)']
table_df = table_df[[c for c in edit_cols if c in table_df.columns]]

# Create the Unified Editable Table
with st.form("database_editor_form"):
    edited_table_df = st.data_editor(
        table_df, 
        use_container_width=True, 
        height=500,
        num_rows="dynamic", # Enables Row Addition & Deletion
        column_config={
            "DateTime": st.column_config.TextColumn("DateTime (YYYY-MM-DD HH:MM:SS)", width="medium"),
            "Event Type": st.column_config.TextColumn("Event Type", disabled=True, width="medium"), 
            "Value (Optional)": st.column_config.NumberColumn("Value", width="small"),
            "Notes / Details (Optional)": st.column_config.TextColumn("Notes / Details (Optional)", width="large")
        }
    )
    
    st.markdown("""
    <div style="background-color: #fef2f2; border: 1px solid #f87171; padding: 12px; border-radius: 8px; margin-top: 8px; margin-bottom: 16px;">
        <strong style="color: #991b1b;">⚠️ CRITICAL DATA WARNING:</strong><br>
        <span style="color: #7f1d1d; font-size: 0.85rem;">Saving changes overwrites the Google Sheet. If someone logged a new entry from their phone while you had this page open, their entry could be lost! <b>Always click '🔄 Refresh' at the top of the app before saving.</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    submit_button = st.form_submit_button("💾 Save Changes to Google Sheets", type="primary", use_container_width=True)
    
    if submit_button:
        with st.spinner("Merging data and checking for conflicts..."):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                live_df = conn.read(spreadsheet=sheet_url_input, ttl=0)
                
                if 'DateTime' in live_df.columns: live_max_time = pd.to_datetime(live_df['DateTime'], errors='coerce').max()
                elif 'EntryDateTime' in live_df.columns: live_max_time = pd.to_datetime(live_df['EntryDateTime'], errors='coerce').max()
                else: live_max_time = None
                    
                current_max_time = df['DateTime'].max() if not df.empty else None
                    
                if current_max_time and live_max_time and live_max_time > current_max_time:
                    st.error("🚨 **COLLISION AVOIDED:** Someone logged new data while you were editing! Click '🔄 Refresh' to sync before saving.")
                else:
                    # SMART MERGE LOGIC: Safely merge the filtered edits back into the full database
                    master_df.update(edited_table_df)
                    deleted_indices = set(table_df.index) - set(edited_table_df.index)
                    master_df = master_df.drop(index=deleted_indices)
                    new_rows = edited_table_df[~edited_table_df.index.isin(table_df.index)]
                    master_df = pd.concat([master_df, new_rows])
                    
                    conn.update(worksheet="Sheet1", data=master_df[edit_cols])
                    st.success("✅ Changes successfully pushed! Refreshing...")
                    st.cache_data.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to update Google Sheets: {e}")

st.markdown(f'<div style="color: #64748b; font-size: 0.85rem; margin-top: 8px;">Showing {len(table_df)} entry(s) matching your criteria.</div>', unsafe_allow_html=True)
st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)

# ==========================================
# 8. BACKGROUND AUTO-RETRY ENGINE
# ==========================================
# UI UN-FREEZER: Asynchronous JS Refresh prevents Python thread freezing while waiting for AI rate limits
if st.session_state.get('needs_auto_retry', False):
    st.session_state.needs_auto_retry = False
    components.html(
        """<script>setTimeout(function() { window.parent.location.reload(); }, 3000);</script>""",
        height=0, width=0
    )
