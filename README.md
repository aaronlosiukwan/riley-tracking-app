# 🍼 Riley's Dash — Infant Analytics Dashboard

**Riley's Dash** is a production-grade, Apple Health-inspired Streamlit web application designed for real-time tracking, visualization, and AI-driven analysis of infant growth, nutrition, health, and developmental milestones.

Powered by **Python**, **Plotly**, **Google Sheets API**, and **OpenRouter LLMs**, it combines data analytics with contextual pediatric benchmarks (such as WHO & Hong Kong Department of Health growth standard curves).

---

## 📊 Specialized Visualizations (8 Analytical Tabs)

| Tab | Visualization Strategy | Domain & Design Rationale |
| :--- | :--- | :--- |
| **⏰ Today** | 24-Hour Scatter Activity Timeline | Plots all events logged in the last 24 hours. Category tick labels on the left Y-axis are rotated -90° counter-clockwise for vertical alignment, with horizontal data labels rendered above event bubbles. |
| **🍼 Milk** | Faceted 2-Row Subplot Panel | Top panel plots stacked Formula (#0284c7) and Breast Milk (#fb7185) volume in mL with a 7-period rolling average line (#334155). Standing total numbers (-90° rotated) in dark grey (#334155) sit atop bars to prevent text overlap. Bottom panel tracks daily feed frequency. |
| **🚽 Diapers** | Deduplicated Stacked Bars | Eliminates double-counting simultaneous wet and soiled diapers logged at the exact same timestamp. Total bar height strictly equals physical diaper changes. Features 9px inner segment text and 9.5px dark grey (#334155) total labels. |
| **🧴 Pumping** | Bar Chart + Trend Line | Tracks maternal express volume in mL with a 7-period rolling average line (#334155). Features an expanded +28% vertical headroom buffer (range=[0, max_pump * 1.28]) and standing -90° rotated numeric labels. |
| **🛟 Tummy** | Bar Chart + Trend Line | Measures physical activity (minutes) with rolling trend overlays to track physical developmental stamina. |
| **📈 Growth** | WHO & HK Percentile Curves | Interactive percentile trajectories (Weight, Height, Head Circumference) for ages 0–24 months. Features exact 50th percentile variance calculation and estimated percentile rank. |
| **🩺 Health** | Line / Bar Charts + Thresholds | Tracks Sleep duration, Medication doses, and Body Temperature with a clinical 37.5°C fever baseline threshold line and shaded red alert zone. |
| **💉 Vaccine** | Immunization Status Table | HK Childhood Immunization Programme (HKCIP) schedule matching engine that categorizes doses into status chips (✅ Done, 🟡 Due Soon, ⚠️ Overdue, ⏳ Upcoming). |

---

## 🧠 Smart AI Narrative Engine & Caching

The application features a dual-layer insight engine:
1. **Rule-Based Summary (`💡 Insight`)**: Instant, deterministic mathematical calculations for the selected date range.
2. **Narrative AI Summary (`✨ AI Insight`)**: Powered by OpenRouter LLMs using strict system prompts.

### Core AI Engine Rules & Guardrails
* **Zero-Wait Category Caching (0ms)**: Calculates a unique hash using `Prompt + Category Max Timestamp + Refresh Key`. If a category's latest timestamp has not changed, the AI card renders instantly from memory without hitting the API.
* **Partial Today Rules**: Prompts enforce that today's in-progress data is used strictly for descriptive reporting. Historical trend analysis and recommendations evaluate completed full days (yesterday and prior) against 7-day baselines to prevent incomplete days from distorting averages.
* **Automatic Resilience**: Built-in rate limit handling (429 detection), safety filter bypass cleaning, and automatic retry loops with exponential backoff.

---

## ⚡ Google Sheets Surgical Sync & Collision Protection

To preserve complex spreadsheet logic, the dashboard interacts with Google Sheets via a custom `gspread` service account pipeline rather than full-table overwrites.

### Google Sheet Worksheet Schema (`Log` Sheet)

| Col Index | Sheet Column | Description | Managed By |
| :---: | :--- | :--- | :--- |
| **A–C** | *Formula Cols* | Date calculations, Day of week, etc. | Sheet `ArrayFormulas` |
| **D** | `LoggedAt` | Entry submission timestamp | App Auto-Write |
| **E** | `DateTime` | Event timestamp (`YYYY-MM-DD HH:MM:SS`) | Caregiver / App |
| **F** | `Event Type` | Category string (e.g., `🍼 Formula (mL)`, `💧 Wet Diaper (Cnt)`) | Caregiver / App |
| **G** | `Value (Optional)` | Numeric quantity (mL, mins, kg, °C) | Caregiver / App |
| **H** | `Notes / Details (Optional)` | Custom notes / Vaccine names | Caregiver / App |
| **I** | `Last Modified` | Last updated timestamp | App Auto-Write |

### Surgical Database Synchronization Logic
* **Cell-Level Diffing**: When saving in Edit Mode, the engine compares modified rows cell-by-cell and executes batch updates (`sheet.update_cells`) strictly targeting **Columns D through I**.
* **Formula Preservation**: Columns A, B, and C containing Google Sheet `ArrayFormulas` are never touched or overwritten.
* **Collision Protection**: Before pushing edits, the system fetches the live worksheet timestamp. If another caregiver logged entries while the editor was open, the edit aborts to prevent data loss.

---

## 🛠️ Tech Stack & Architecture

* **Frontend UI**: [Streamlit](https://streamlit.io/) with custom Apple Health responsive CSS styling
* **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Plotting & Graphics**: [Plotly Express & Graph Objects](https://plotly.com/python/)
* **Database Pipeline**: [Google Sheets API](https://developers.google.com/sheets/api) via `gspread`
* **AI Engine**: [OpenAI Python SDK](https://github.com/openai/openai-python) connected to [OpenRouter](https://openrouter.ai/)
