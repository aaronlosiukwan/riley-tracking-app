🍼 Riley's Dash — Smart Infant Analytics Dashboard

Riley's Dash is a production-grade, Apple Health-inspired Streamlit web application engineered for real-time tracking, multi-dimensional data visualization, and AI-assisted analysis of infant development, nutrition, health metrics, and growth trajectories.

🏗️ System Architecture

 📱 iOS Shortcuts / Caregiver Input
               │
               ▼
┌──────────────────────────────────────────────┐
│  Google Sheets ("Log" Worksheet)             │
│  - Cols A–C: Auto ArrayFormulas              │
│  - Cols D–I: Event Logs & Timestamps         │
└──────────────────────┬───────────────────────┘
                       │ OAuth2 Service Account (gspread)
                       ▼
┌──────────────────────────────────────────────┐
│  load_sheet_data (TTL = 600s Cache)          │
└──────────────────────┬───────────────────────┘
                       │ Normalized Pandas DataFrame
                       ▼
┌──────────────────────────────────────────────┐       ┌──────────────────────────────┐
│  Reactive Data Pipeline                      │ ────► │ Plotly Visualization Engine  │
│  - Deduplicated Diaper Engine                │       │ - Faceted Subplots           │
│  - WHO / HK Z-Score Percentile Calculations  │       │ - Rotated Annotation Engine  │
│  - Clinical Threshold Layers                 │       │ - Adaptive Headroom Buffers  │
└──────────────────────┬───────────────────────┘       └──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Category AI Cache Engine                    │ ────► Instant Cache Hit (0ms Execution)
│  (Data Timestamp Matching per Category)      │ ────► Live OpenRouter API Call (If Data Changed)
└──────────────────────┬───────────────────────┘


📊 Specialized Visualization Engine (8 Analytical Tabs)

Tab

Visualization Strategy

Domain & Design Rationale

⏰ Today

24-Hour Scatter Activity Timeline

Plots all events logged in the last 24 hours. Category tick labels on the left Y-axis are rotated $-90^\circ$ counter-clockwise (y_tickangle=-90) for vertical scanning, while numeric value labels float horizontally directly above markers (textangle=0).

🍼 Milk

Faceted 2-Row Subplot Panel

Top panel plots stacked Formula (#0284c7) and Breast Milk (#fb7185) volume in mL with a 7-period rolling average line (#334155). Standing total numbers (textangle=-90) appear on top of stacked bars in dark grey (#334155, 9.5px). Bottom panel plots daily feed counts (#8b5cf6).

🚽 Diapers

Deduplicated Stacked Bars

Eliminates double-counting simultaneous wet and soiled diapers logged at the exact same timestamp. Total bar height strictly equals physical diaper changes, with segment counts inside bars and total change counts standing on top (#334155).

🧴 Pumping

Bar Chart + Trend Line

Tracks maternal express volume in mL with a 7-period rolling average line (#334155). Features an expanded $+28\%$ vertical headroom buffer (range=[0, max_pump * 1.28]) so standing labels never collide with subplot headers.

🛟 Tummy

Bar Chart + Trend Line

Tracks physical activity duration in minutes with a rolling average spline overlay (#047857) to monitor neck and core strength progression.

📈 Growth

WHO & HK Percentile Curve Overlay

Plots Weight (kg), Height (cm), and Head Size (cm) against official Hong Kong Department of Health percentiles ($3\text{rd}$ to $97\text{th}$). Renders actual trajectory as a 3.5px Hero Spline while maintaining hover inspection across all underlying percentile bands (hovermode="x unified").

🩺 Health

Multi-Mode Line/Bar Chart

Visualizes Sleep duration (hrs), Medication doses, and Body Temperature (°C). Body Temperature includes a dashed red line at $37.5^\circ\text{C}$ and a light-red background shading band (#fee2e2) highlighting the clinical fever zone ($\ge 37.5^\circ\text{C}$).

💉 Vaccine

Milestone Schedule Engine

Auto-matches logged events against the HK Childhood Immunization Programme (HKCIP) schedule using regex keyword scanning. Categorizes shots into high-contrast status rows (✅ Done, 🟡 Due Soon, ⚠️ Overdue, ⏳ Upcoming).

🚽 Deduplicated Diaper Stacking Engine Mechanics

Standard aggregations double-count simultaneous wet and soiled diapers (e.g., logging a Wet Diaper and a Poop diaper both at 10:00 AM yields 2 bar segments totaling a height of 2, displaying 2 changes instead of 1 physical diaper change).

The engine groups events by exact DateTime timestamp:

dt_group = diaper_df.groupby(['DateTime', group_col]).agg(
    has_poop=('Event Type', lambda s: any('poop' in str(x).lower() for x in s)),
    has_wet=('Event Type', lambda s: any('wet' in str(x).lower() for x in s))
).reset_index()

def classify_diaper(row):
    if row['has_poop']:
        return "🚽 Poop"  # Soiled diaper takes precedent
    else:
        return "💧 Wet Diaper (Only)"


Result: Stacking 🚽 Poop on top of 💧 Wet Diaper (Only) produces a total bar height mathematically equal to physical diaper changes.

📈 WHO & HK Growth Percentile Z-Score Engine

Growth curves map standard distributions ($3\text{rd}$, $15\text{th}$, $50\text{th}$, $85\text{th}$, and $97\text{th}$ percentiles) across a 0–24 month age array ($m_x \in [0, 24]$).

For any recorded value $v$ at age in months $a$:

Linearly interpolates reference percentiles $P_{50}(a)$, $P_3(a)$, and $P_{97}(a)$ using np.interp.

Computes the normalized Z-score:


$$z = \frac{v - P_{50}(a)}{(P_{97}(a) - P_3(a)) / 3.76}$$

Calculates estimated percentile rank via the logistic approximation function:


$$\text{Percentile Rank} = \frac{1}{1 + e^{-1.702 \cdot z}} \times 100$$

Computes exact variance relative to the age-matched 50th percentile baseline:


$$\Delta_{P50} = v - P_{50}(a)$$

🧠 Smart AI Narrative Pipeline

The dashboard features stacked Dual Insight Cards:

💡 Rule-Based Insight Card (Blue accent line): Renders instantly with mathematical summaries and calculated variances.

✨ AI Insight Card (Purple accent line): Appears directly below when the AI toggle is active, presenting a narrative analysis generated by OpenRouter's free LLM router.

┌─────────────────────────────────────────────────────────────┐
│                   render_insight_card()                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
       Has category data timestamp changed OR refresh toggled?
                               │
               ┌───────────────┴───────────────┐
            NO │                               │ YES
               ▼                               ▼
    ┌────────────────────┐          ┌────────────────────┐
    │ Instant Cache Hit  │          │  Live AI API Call  │
    │  (0ms execution)   │          │ (OpenRouter Router)│
    └────────────────────┘          └─────────┬──────────┘
                                              │
                                              ▼
                                    ┌────────────────────┐
                                    │ Save Content, TS & │
                                    │ Model Metadata     │
                                    └────────────────────┘


In-Progress Today Guardrails

Prompt templates enforce evaluation rules to prevent LLM hallucinations or false medical alerts early in the day:

Rule 1 (Partial Data): Today's partial metrics are restricted strictly to descriptive reporting.

Rule 2 (Trend Analysis): Trend evaluations must analyze full completed days (yesterday and prior) against baseline averages.

Rule 3 (Actionable Guidance): Recommendations are derived strictly from completed historical full-day trends.

💾 Surgical Database Synchronization & Collision Protection

When editing raw logs in the Master Database Table, the application protects Google Sheet formulas and prevents data overwrites during concurrent edits (e.g., from an iOS Shortcut).

       [ User Clicks 'Save Changes' ]
                     │
                     ▼
   Bypass Cache: Fetch Live Max DateTime
                     │
  Live Max DateTime > Session Max DateTime?
                     │
      ┌──────────────┴──────────────┐
  YES │                             │ NO
      ▼                             ▼
🚨 ABORT SAVE               Execute Surgical Sync
Display Collision Alert     - Update Cols D–I via gspread.Cell
                            - Preserve ArrayFormulas (Cols A–C)
                            - Write 'Last Modified' Timestamp


Surgical Cell Diffing (gspread.update_cells)

To prevent full-table overwrites from wiping dynamic spreadsheet formulas in Columns A–C, the update engine targets modified cells row-by-row:

edits_to_push = []
for idx in common_indices:
    if old_val != new_val:
        # Target coordinate: (Row, Col)
        edits_to_push.append(gspread.Cell(row=sheet_row, col=target_col, value=new_val))

sheet.update_cells(edits_to_push, value_input_option='USER_ENTERED')


📋 Data Schema Specs

Google Sheets Column Index Mapping

Col

Field Name

Type

Description

A–C

ArrayFormulas

Formula

Dynamic Google Sheets formulas (Read-Only)

D

LoggedAt

String

System timestamp when entry was recorded

E

DateTime

Datetime

Event timestamp (YYYY-MM-DD HH:MM:SS)

F

Event Type

Select

Standardized category string

G

Value (Optional)

Numeric

Metric quantity (mL, mins, kg, °C, count)

H

Notes / Details

String

Notes, vaccine names, or free text

I

Last Modified

String

System timestamp of last edit sync

⚙️ Session State Schema

State Key

Type

Description

last_ai_data_datetime

datetime

Max timestamp of dataset used for background refresh comparisons

ai_refresh_key

str

Manual cache invalidation token toggled by "🔄 Refresh AI Summaries"

ai_insights_enabled

bool

Master toggle controlling LLM pipeline execution

edit_mode

bool

Toggles UI between fast read-only table and interactive editor

needs_auto_retry

bool

Triggers background retries when rate-limiting ($429$) occurs

ai_retry_count

int

Exponential backoff retry counter (capped at 3 attempts)

📄 License

Distributed under the MIT License. See LICENSE for more information.
