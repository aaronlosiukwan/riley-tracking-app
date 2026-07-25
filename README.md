🍼 Riley's Dash — Smart Infant Analytics DashboardRiley's Dash is a production-grade, Apple Health-inspired Streamlit web application engineered for real-time tracking, multi-dimensional data visualization, and AI-assisted analysis of infant development, nutrition, health metrics, and growth trajectories.🏗️ System Architecture 📱 iOS Shortcuts / Caregiver Input
               │
               ▼
┌──────────────────────────────────────────────┐
│  Google Sheets ("Log" Worksheet)             │
│  - Cols A–C: Auto ArrayFormulas              │
│  - Cols D–I: Event Logs & Timestamps         │
└──────────────────────┬───────────────────────┘
                       │ OAuth2 Service Account
                       ▼
┌──────────────────────────────────────────────┐
│  load_sheet_data (TTL = 600s Cache)          │ ◄── gspread Client
└──────────────────────┬───────────────────────┘
                       │ Normalized Pandas DataFrame
                       ▼
┌──────────────────────────────────────────────┐       ┌──────────────────────────────┐
│  Reactive Data Pipeline                      │ ────► │ Plotly Visualization Engine  │
│  - 09:00 AM Operational Day Cutoff           │       │ - Faceted Subplots           │
│  - Deduplicated Diaper Engine                │       │ - Rotated Annotation Engine  │
│  - WHO / HK Z-Score Percentile Calculations  │       │ - Clinical Threshold Layers  │
└──────────────────────┬───────────────────────┘       └──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Category AI Cache Engine                    │ ────► Instant Cache Hit (0ms Execution)
│  (Data Timestamp Matching per Category)      │ ────► Live OpenRouter API Call (If Data Changed)
└──────────────────────┬───────────────────────┘
🌅 The Operational Day Cutoff (The 09:00 AM Rule)Why Calendar Midnight (00:00) Fails in Infant CareStandard digital dashboards reset all metrics to zero at 00:00 midnight. For adult habit trackers, this works well. For newborn care, it creates a severe analytical paradox:The "Midnight Paradox": A night feed logged at 02:30 AM or a diaper changed at 04:15 AM belongs operational-wise to the night shift started the previous evening. Under standard midnight resetting, opening the app at 03:00 AM shows "0 mL Milk Intake Today" and "0 Diapers Today". This causes unnecessary anxiety for tired parents or night nannies checking if the baby was fed overnight.Caregiver Shift Continuity: Infant sleep-and-feed cycles operate on a continuous 24-hour continuum rather than standard calendar days. Parent and caregiver handoffs typically occur in the morning between 07:00 AM and 09:00 AM.How the Operational Cutoff Engine WorksTo reflect true caregiving workflows, Riley's Dash defines 09:00 AM local time as the operational day boundary:$$\text{Target Date} = \begin{cases} \text{Local Date} - 1 \text{ day}, & \text{if Hour} < 9 \\ \text{Local Date}, & \text{if Hour} \ge 9 \end{cases}$$   10:00 PM (Jul 24)        03:00 AM (Jul 25)         08:59 AM (Jul 25)       09:00 AM (Jul 25)
───────┬────────────────────────┬─────────────────────────┬─────────────────────────┬───────────►
       │                        │                         │                         │
       ▼                        ▼                         ▼                         ▼
Operational Day:          Operational Day:          Operational Day:          Operational Day:
  July 24 Log               July 24 Log               July 24 Log               July 25 Log
 (Night Shift)             (Night Shift)             (Night Shift End)          (Morning Shift Start)
Operational Impact on Viewer ExperienceDuring Early Morning (00:00 AM – 08:59 AM):The ✨ Today highlights and 24-hour timeline display the complete, uninterrupted log of the overnight shift and previous day (July 24).Caregivers waking up can immediately see total overnight milk volume, sleep duration, and wet diaper counts without mental math or filtering.At 09:00 AM Onward:The dashboard automatically transitions to track the active daytime shift (July 25).Strict 7-Day Baseline IsolationWhen computing historical averages for comparative analysis, including an in-progress day heavily skews mathematical moving averages (e.g., comparing a partial day with only $200\text{ mL}$ logged so far against a $750\text{ mL}$ daily average falsely triggers a "Low Feeding" alert).The engine strictly isolates the historical baseline to completed 24-hour operational cycles:$$\text{Baseline Period} = [\text{Target Date} - 7\text{ days}, \; \text{Target Date} - 1\text{ day}]$$📊 Specialized Visualization Engine (8 Analytical Tabs)TabVisualization StrategyDomain & Design Rationale⏰ Today24-Hour Scatter Activity TimelineDisplays all events logged in the last 24 hours. Category tick labels on the left Y-axis are rotated $-90^\circ$ counter-clockwise (y_tickangle=-90) for vertical scanning, while numeric event values float directly above markers horizontally (textangle=0).🍼 MilkFaceted 2-Row Subplot PanelTop panel plots stacked Formula (#0284c7) and Breast Milk (#fb7185) volume in mL with a 7-period spline trend line (#334155). Bottom panel plots daily feed counts (#8b5cf6). Total volume numbers stand vertically (textangle=-90) on top of stacked bars in dark grey (#334155, 9.5px).🚽 DiapersDeduplicated Stacked BarsEliminates double-counting simultaneous wet and soiled diapers logged at the exact same timestamp. Total bar height strictly equals total physical diaper changes, with segment counts inside bars and total change counts standing on top (#334155).🧴 PumpingBar Chart + Spline Trend LineTracks maternal express volume in mL with a 7-period rolling average line (#334155). Features an expanded $+28\%$ vertical headroom buffer (range=[0, max_pump * 1.28]) so standing labels never collide with subplot boundaries.🛟 TummyBar Chart + Spline Trend LineTracks physical activity duration in minutes with a rolling average spline overlay (#047857) to monitor neck and core strength progression.📈 GrowthWHO & HK Percentile Curve OverlayPlots Weight (kg), Height (cm), and Head Size (cm) against official Hong Kong Department of Health percentiles ($3\text{rd}$ to $97\text{th}$). Renders the baby's actual trajectory as a 3.5px Hero Spline while maintaining hover inspection across all underlying percentile bands (hovermode="x unified").🩺 HealthMulti-Mode Line/Bar ChartVisualizes Sleep duration (hrs), Medication doses, and Body Temperature (°C). Body Temperature includes a dashed red line at $37.5^\circ\text{C}$ and a light-red background shading band (#fee2e2) highlighting the clinical fever zone ($\ge 37.5^\circ\text{C}$).💉 VaccineMilestone Schedule EngineAuto-matches logged events against the HK Childhood Immunization Programme (HKCIP) schedule using regex keyword scanning. Categorizes shots into high-contrast status rows (✅ Done, 🟡 Due Soon, ⚠️ Overdue, ⏳ Upcoming).🚽 Deduplicated Diaper Stacking Engine MechanicsStandard aggregations double-count simultaneous wet and soiled diapers (e.g., logging a Wet Diaper and a Poop diaper both at 10:00 AM yields 2 bar segments totaling a height of 2, displaying 2 changes instead of 1 physical diaper change).The engine groups events by exact DateTime timestamp:dt_group = diaper_df.groupby(['DateTime', group_col]).agg(
    has_poop=('Event Type', lambda s: any('poop' in str(x).lower() for x in s)),
    has_wet=('Event Type', lambda s: any('wet' in str(x).lower() for x in s))
).reset_index()

def classify_diaper(row):
    if row['has_poop']:
        return "🚽 Poop"  # Soiled diaper takes precedent
    else:
        return "💧 Wet Diaper (Only)"
Result: Stacking 🚽 Poop on top of 💧 Wet Diaper (Only) produces a total bar height mathematically equal to physical diaper changes.📈 WHO & HK Growth Percentile Z-Score EngineGrowth curves map standard distributions ($3\text{rd}$, $15\text{th}$, $50\text{th}$, $85\text{th}$, and $97\text{th}$ percentiles) across a 0–24 month age array ($m_x \in [0, 24]$).For any recorded value $v$ at age in months $a$:Linearly interpolates reference percentiles $P_{50}(a)$, $P_3(a)$, and $P_{97}(a)$ using np.interp.Computes the normalized Z-score:$$z = \frac{v - P_{50}(a)}{(P_{97}(a) - P_3(a)) / 3.76}$$Calculates estimated percentile rank via the logistic approximation function:$$\text{Percentile Rank} = \frac{1}{1 + e^{-1.702 \cdot z}} \times 100$$Computes exact variance relative to the age-matched 50th percentile baseline:$$\Delta_{P50} = v - P_{50}(a)$$🧠 Smart AI Narrative PipelineThe dashboard features stacked Dual Insight Cards:💡 Rule-Based Insight Card (Blue accent line): Renders instantly with mathematical summaries and calculated variances.✨ AI Insight Card (Purple accent line): Appears directly below when the AI toggle is active, presenting a narrative analysis generated by OpenRouter's free LLM router.┌─────────────────────────────────────────────────────────────┐
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
In-Progress Today GuardrailsPrompt templates enforce evaluation rules to prevent LLM hallucinations or false medical alerts early in the morning:Rule 1 (Partial Data): Today's partial metrics are restricted strictly to descriptive reporting.Rule 2 (Trend Analysis): Trend evaluations must analyze full completed days (yesterday and prior) against baseline averages.Rule 3 (Actionable Guidance): Recommendations are derived strictly from completed historical full-day trends.💾 Surgical Database Synchronization & Collision ProtectionWhen editing raw logs in the Master Database Table, the application protects Google Sheet formulas and prevents data overwrites during concurrent edits (e.g., from an iOS Shortcut).       [ User Clicks 'Save Changes' ]
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
Surgical Cell Diffing (gspread.update_cells)To prevent full-table overwrites from wiping dynamic spreadsheet formulas in Columns A–C, the update engine targets modified cells row-by-row:edits_to_push = []
for idx in common_indices:
    if old_val != new_val:
        # Target coordinate: (Row, Col)
        edits_to_push.append(gspread.Cell(row=sheet_row, col=target_col, value=new_val))

sheet.update_cells(edits_to_push, value_input_option='USER_ENTERED')
📋 Data Schema SpecsGoogle Sheets Column Index MappingColField NameTypeDescriptionA–CArrayFormulasFormulaDynamic Google Sheets formulas (Read-Only)DLoggedAtStringSystem timestamp when entry was recordedEDateTimeDatetimeEvent timestamp (YYYY-MM-DD HH:MM:SS)FEvent TypeSelectStandardized category stringGValue (Optional)NumericMetric quantity (mL, mins, kg, °C, count)HNotes / DetailsStringNotes, vaccine names, or free textILast ModifiedStringSystem timestamp of last edit sync⚙️ Session State SchemaState KeyTypeDescriptionlast_ai_data_datetimedatetimeMax timestamp of dataset used for background refresh comparisonsai_refresh_keystrManual cache invalidation token toggled by "🔄 Refresh AI Summaries"ai_insights_enabledboolMaster toggle controlling LLM pipeline executionedit_modeboolToggles UI between fast read-only table and interactive editorneeds_auto_retryboolTriggers background retries when rate-limiting ($429$) occursai_retry_countintExponential backoff retry counter (capped at 3 attempts)📄 LicenseDistributed under the MIT License. See LICENSE for more information.
