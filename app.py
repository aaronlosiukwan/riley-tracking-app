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

# Custom Mobile & Dark/Light Mode Responsive CSS
st.markdown("""
    <style>
    /* Equal height and width highlight cards */
    .highlight-card {
        background-color: rgba(128, 128, 128, 0.07);
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 14px 16px;
        min-height: 125px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .highlight-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }
    .highlight-body {
        font-size: 0.88rem;
        opacity: 0.88;
        line-height: 1.35;
    }
    .highlight-sub {
        font-size: 0.78rem;
        opacity: 0.65;
        margin-top: 4px;
    }

    /* Grey default range indicator text */
    .default-range-text {
        color: #888888;
        font-size: 0.85rem;
        font-style: italic;
        margin-top: 4px;
        display: inline-block;
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

    /* Streamlit Padding Fixes */
    .stApp {
        padding-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍼 Riley Growth Log")

# ==========================================
# 2. GOOGLE SHEET CONNECTOR & AUTO SYNC
# ==========================================
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

# Fetch Google Sheet data in real time (5-second cache)
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

# Master Emoji Normalization for all data rows
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

# Mobile-friendly Plotly Styling Helper
def style_plotly_figure(fig, height=520):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=70, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.5,
            title_text=""
        ),
        font=dict(family="sans-serif", size=12),
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
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

# Sync refresh button top header
top_col1, top_col2 = st.columns([3, 1])
with top_col2:
    if st.button("🔄 Sync Sheet Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 4. HIGHLIGHTS & SUMMARY CARDS
# ==========================================

# --- A. TODAY'S HIGHLIGHTS (Always Visible, Focused Strictly on Today) ---
today_date = max(datetime.now().date(), max_data_date)
today_df = df[df['Date'] == today_date]

st.markdown(f"### ✨ Today's Highlights (`{today_date.strftime('%b %d, %Y')}`)")

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

# Calculate Last Feeding globally across entire dataset
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

# Display Equal Height Highlight Cards Grid for Today
th_col1, th_col2, th_col3, th_col4 = st.columns(4)

with th_col1:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">🍼 Milk Intake Today</div>
                <div class="highlight-body">Total <b>{int(t_milk):,} mL</b> across <b>{t_feed_cnt}</b> feeds.</div>
            </div>
            <div class="highlight-sub">Avg Feed: ~{int(t_avg_feed)} mL (Formula: {int(t_formula):,}mL, BM: {int(t_bm):,}mL)</div>
        </div>
    """, unsafe_allow_html=True)

with th_col2:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">⏰ Last Feeding</div>
                <div class="highlight-body"><b>{last_feed_delta}</b></div>
            </div>
            <div class="highlight-sub">{last_feed_sub}</div>
        </div>
    """, unsafe_allow_html=True)

with th_col3:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">🚽 Diaper Output Today</div>
                <div class="highlight-body">Total <b>{t_wet + t_poop}</b> diaper changes logged.</div>
            </div>
            <div class="highlight-sub">💧 Wet: {t_wet} | 💩 Poop: {t_poop}</div>
        </div>
    """, unsafe_allow_html=True)

with th_col4:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">🧴 Pumping & Tummy Time</div>
                <div class="highlight-body">Pumped <b>{int(t_pumping):,} mL</b> | 🛟 <b>{int(t_tummy)} mins</b> tummy.</div>
            </div>
            <div class="highlight-sub">{len(today_df[today_df['Event Type'].str.contains("Pumping", case=False, na=False)])} pumping sessions today</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

th_row2_c1, th_row2_c2, th_row2_c3, th_row2_c4 = st.columns(4)

with th_row2_c1:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">🛌 Rest & Sleep Today</div>
                <div class="highlight-body">Logged <b>{int(t_sleep)} hrs</b> rest today.</div>
            </div>
            <div class="highlight-sub">{len(today_df[today_df['Event Type'].str.contains("Sleep", case=False, na=False)])} sleep periods today</div>
        </div>
    """, unsafe_allow_html=True)

with th_row2_c2:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">💊 Medication Today</div>
                <div class="highlight-body">Logged <b>{t_meds}</b> doses today.</div>
            </div>
            <div class="highlight-sub">Doses tracked today</div>
        </div>
    """, unsafe_allow_html=True)

t_temp_df = today_df[today_df['Event Type'].str.contains("Temp", case=False, na=False)]
t_latest_temp = t_temp_df.iloc[0]['Value (Optional)'] if not t_temp_df.empty else None
t_temp_str = f"<b>{t_latest_temp:.1f} °C</b>" if t_latest_temp else "No readings today"

with th_row2_c3:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">🌡️ Latest Temp Today</div>
                <div class="highlight-body">{t_temp_str}</div>
            </div>
            <div class="highlight-sub">{len(t_temp_df)} temperature logs today</div>
        </div>
    """, unsafe_allow_html=True)

with th_row2_c4:
    st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-title">📊 Total Events Today</div>
                <div class="highlight-body"><b>{len(today_df):,}</b> entries logged today.</div>
            </div>
            <div class="highlight-sub">Date: {today_date.strftime('%Y-%m-%d')}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# --- B. PERIOD HIGHLIGHTS (Toggled Hidden Position) ---
period_headers = {
    "Daily": "Daily Range Highlights",
    "Weekly": "Weekly Highlights",
    "Monthly": "Monthly Highlights",
    "All Time": "All-Time Highlights"
}

with st.expander(f"✨ {period_headers[granularity]} ({start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}) (Click to expand)", expanded=False):
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
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">🍼 Milk ({granularity})</div>
                    <div class="highlight-body">Total <b>{int(p_milk):,} mL</b> across <b>{p_feed_cnt}</b> feeds.</div>
                </div>
                <div class="highlight-sub">Avg Feed: ~{int(p_avg_feed)} mL (Formula: {int(p_formula):,}mL, BM: {int(p_bm):,}mL)</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c2:
        st.markdown(f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">🚽 Diapers ({granularity})</div>
                    <div class="highlight-body">Total <b>{p_wet + p_poop}</b> diaper changes.</div>
                </div>
                <div class="highlight-sub">💧 Wet: {p_wet} | 💩 Poop: {p_poop}</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c3:
        st.markdown(f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">🧴 Pumping & Tummy Time</div>
                    <div class="highlight-body">Pumped <b>{int(p_pumping):,} mL</b> | 🛟 <b>{int(p_tummy)} mins</b> tummy time.</div>
                </div>
                <div class="highlight-sub">{len(filtered_df[filtered_df['Event Type'].str.contains("Pumping", case=False, na=False)])} sessions in selected period</div>
            </div>
        """, unsafe_allow_html=True)

    with pr1_c4:
        st.markdown(f"""
            <div class="highlight-card">
                <div>
                    <div class="highlight-title">🛌 Sleep & Meds</div>
                    <div class="highlight-body">Rest: <b>{int(p_sleep)} hrs</b> | Meds: <b>{p_meds} doses</b>.</div>
                </div>
                <div class="highlight-sub">Total {len(filtered_df):,} events in selected range</div>
            </div>
        """, unsafe_allow_html=True)

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
st.subheader("📊 Analytics & Insights")

tab1, tab2, tab3, tab4 = st.tabs([
    "🍼 Milk Intake & Feed Count", 
    "🚽 Diaper Output", 
    "🧴 Pumping & Activities", 
    "📈 Event Timeline"
])

# TAB 1: Milk Intake Stacked + Dual Axis Feeding Counts
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
                    x=df_f[group_col],
                    y=df_f['Value (Optional)'],
                    marker_color=COLOR_MAP['🍼 Formula (mL)']
                ),
                secondary_y=False
            )
            
        df_bm = grouped_vol[grouped_vol['Category'] == '🤱 Breast Milk (mL)']
        if not df_bm.empty:
            fig_milk.add_trace(
                go.Bar(
                    name='🤱 Breast Milk (mL)',
                    x=df_bm[group_col],
                    y=df_bm['Value (Optional)'],
                    marker_color=COLOR_MAP['🤱 Breast Milk (mL)']
                ),
                secondary_y=False
            )
            
        fig_milk.add_trace(
            go.Scatter(
                name='🔢 Total Feeds Count',
                x=grouped_count[group_col],
                y=grouped_count['Total Feeds Count'],
                mode='lines+markers+text',
                text=grouped_count['Total Feeds Count'],
                textposition="top center",
                line=dict(color='#10b981', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True
        )

        fig_milk.update_layout(
            barmode='stack',
            title=f"Milk Intake Volume (Stacked Bars) & Total Feed Count (Line) — {granularity}",
            height=540,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=70, b=30),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="center",
                x=0.5,
                title_text=""
            ),
            font=dict(family="sans-serif", size=12),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            hovermode="x unified"
        )
        
        fig_milk.update_yaxes(title_text="Volume (mL)", secondary_y=False, showgrid=True, gridcolor="rgba(128,128,128,0.15)")
        fig_milk.update_yaxes(title_text="Number of Feeds", secondary_y=True, showgrid=False)
        
        st.plotly_chart(fig_milk, use_container_width=True)
        st.caption(f"ℹ️ *This dual-axis visualization combines total stacked **Formula and Breast Milk volume (mL)** on the left axis with total **Feeding Event Counts** (green line) on the right axis grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
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

# TAB 3: Pumping & All Activities
with tab3:
    act_choices = st.multiselect(
        "🏷️ Select Event Types to Graph:",
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
                title=f"Activities & Measurements Summary ({granularity})",
                barmode="group",
                color_discrete_map=COLOR_MAP,
                labels={"Value (Optional)": "Aggregated Value", group_col: granularity}
            )
            fig_act = style_plotly_figure(fig_act, height=500)
            st.plotly_chart(fig_act, use_container_width=True)
            st.caption(f"ℹ️ *Displays recorded metrics for selected activity categories grouped **{granularity.lower()}** from **{start_date}** to **{end_date}**.*")
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
        st.caption(f"ℹ️ *Individual event occurrence scatter plot from **{start_date}** to **{end_date}**.*")
    else:
        render_empty_state("No Events Logged in this period")

st.markdown("---")

# ==========================================
# 6. EXPANDED RAW DATA LOGS TABLE
# ==========================================
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

if selected_events:
    table_df = table_df[table_df['Event Type'].isin(selected_events)]

if search_query:
    search_mask = table_df.astype(str).apply(
        lambda row: row.str.contains(search_query, case=False, na=False).any(), axis=1
    )
    table_df = table_df[search_mask]

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
        height=720,
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
    st.caption(f"Showing **{len(display_df)}** entries matching your criteria.")
else:
    render_empty_state("No Raw Data Rows Match Your Search Criteria")
