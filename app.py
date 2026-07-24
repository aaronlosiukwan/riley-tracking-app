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
