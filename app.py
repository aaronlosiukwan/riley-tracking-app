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

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ==========================================
# 6. UNIFIED MASTER DATABASE
# ==========================================
st.markdown('<div id="database" style="padding-top: 3.5rem;"></div>', unsafe_allow_html=True)
st.subheader("📋 Master Database")
st.caption("Search, filter, and edit your logs directly. Click 'Save' below to sync with Google Sheets.")

filter_c1, filter_c2 = st.columns([1, 1])
with filter_c1: selected_events = st.multiselect("🏷️ Filter Event Types:", options=ALL_EVENT_CATEGORIES, default=[], placeholder="Choose event types (Leave empty for All)")
with filter_c2: search_query = st.text_input("🔍 Search Anything:", "", placeholder="Type date (e.g. 07-21), Formula, notes...")

# Base dataframe for editing (Maintains original index for safe merging)
master_df = df.copy().reset_index(drop=True)

# Format DateTime to string for the editor to prevent timezone serialization bugs
master_df['DateTime'] = master_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Apply Search and Filters
table_df = master_df.copy()
if selected_events: 
    table_df = table_df[table_df['Event Type'].isin(selected_events)]

if search_query:
    search_mask = pd.Series(False, index=table_df.index)
    for col in table_df.columns:
        search_mask |= table_df[col].astype(str).str.contains(search_query, case=False, na=False)
    table_df = table_df[search_mask]

# Define the exact columns that are safe to edit and push back to Google Sheets
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
        <span style="color: #7f1d1d; font-size: 0.85rem;">Saving changes overwrites the Google Sheet with your edits. If someone else logged a new entry from their phone while you had this page open, their entry could be permanently lost! <b>Always click '🔄 Refresh' at the top of the app right before editing.</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    submit_button = st.form_submit_button("💾 Save Changes to Google Sheets", type="primary", use_container_width=True)
    
    if submit_button:
        with st.spinner("Merging data and checking for conflicts..."):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # BULLETPROOF CHECK: Fetch live sheet bypassing cache
                live_df = conn.read(spreadsheet=sheet_url_input, ttl=0)
                if 'DateTime' in live_df.columns: 
                    live_max_time = pd.to_datetime(live_df['DateTime'], errors='coerce').max()
                elif 'EntryDateTime' in live_df.columns: 
                    live_max_time = pd.to_datetime(live_df['EntryDateTime'], errors='coerce').max()
                else:
                    live_max_time = None
                    
                current_max_time = df['DateTime'].max() if not df.empty else None
                    
                if current_max_time and live_max_time and live_max_time > current_max_time:
                    st.error("🚨 **CRITICAL COLLISION AVOIDED:** Someone else logged new data to the spreadsheet while you were editing! **Please click the '🔄 Refresh' button at the top of the app to sync the latest data before saving.**")
                else:
                    # SMART MERGE LOGIC: Safely merge the filtered edits back into the full database
                    # 1. Update modified cells based on original index
                    master_df.update(edited_table_df)
                    
                    # 2. Drop deleted rows
                    deleted_indices = set(table_df.index) - set(edited_table_df.index)
                    master_df = master_df.drop(index=deleted_indices)
                    
                    # 3. Add new rows
                    new_rows = edited_table_df[~edited_table_df.index.isin(table_df.index)]
                    master_df = pd.concat([master_df, new_rows])
                    
                    # 4. Extract only the original columns to push
                    push_df = master_df[edit_cols]
                    
                    conn.update(worksheet="Sheet1", data=push_df)
                    st.success("✅ Changes successfully pushed to Google Sheets! Refreshing...")
                    st.cache_data.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to update Google Sheets: {e}")

st.markdown(f'<div class="raw-log-count-text">Showing {len(table_df)} entry(s) matching your criteria.</div>', unsafe_allow_html=True)
st.markdown('<hr style="margin: 6px 0; opacity: 0.2;">', unsafe_allow_html=True)

# ==========================================
# 7. BACKGROUND AUTO-RETRY ENGINE
# ==========================================
# UI UN-FREEZER: Asynchronous JS Refresh prevents Python thread freezing while waiting for AI rate limits
if st.session_state.get('needs_auto_retry', False):
    st.session_state.needs_auto_retry = False
    components.html(
        """
        <script>
            setTimeout(function() {
                window.parent.location.reload();
            }, 3000);
        </script>
        """,
        height=0,
        width=0
    )
