<div align="center">
<h1>🍼 Riley's Dash</h1>
<p><b>A highly customized, mobile-optimized Streamlit dashboard for real-time baby tracking.</b></p>
</div>

Riley's Dash is a comprehensive, meticulously designed analytical dashboard built for modern, sleep-deprived parents. It acts as a unified hub to track a baby's daily activities, precise growth metrics, and health milestones.

By pulling data directly from a live Google Sheet, it visualizes raw logs into actionable, aesthetically pleasing, and AI-driven insights—all completely optimized for both mobile and desktop experiences via advanced CSS overrides.

📑 Table of Contents

• ✨ Core Features

• 📊 Dashboard Modules

• 🏗️ Data Architecture (Google Sheets)

• 🚀 Installation & Local Setup

• 📱 iOS Shortcut Integration

• ⚙️ Configuration

• 🛠️ Tech Stack

✨ Core Features

• 📱 Flawless Mobile-First Design: Extensive custom CSS intercepts Streamlit's native layout engine to guarantee an app-like experience. Features locked-width responsive buttons, single-row mobile flex boxes, and compact 2x2 grouping filters that save valuable screen real estate.

• 🔄 Bulletproof Real-Time Sync: A natively integrated "Refresh" button that clears the Streamlit cache (st.cache_data.clear()), forces a fast rerun, and provides intuitive UI feedback via spinning states and native green ✅ Data successfully updated! toast notifications.

• 🤖 Smart "AI" Insight Cards: Every analytical chart generates an automated markdown summary. It intelligently calculates rolling averages, daily frequencies, and trend direction (e.g., detecting if milk intake is "trending upwards 📈" based on 7-day rolling averages vs historical baselines).

• 🌐 Dynamic Timezone Handling: Built-in UTC offset configuration allows parents to view accurate "Last Fed" or "Last Slept" deltas, no matter where the app is hosted.

📊 Dashboard Modules

1. ✨ Today Highlights

A snapshot of the past 24 hours designed for quick glances.

• Metrics Tracked: Last Feeding (exact hours/mins ago), Total Milk Intake (Formula vs Breast Milk breakdown), Diaper Output, Pumping Yields, Tummy Time, Sleep, Meds, and latest Body Temperature.

• Smart UI: Cards dynamically scale and hide themselves gracefully if no data exists for a specific category that day.

2. 📊 Analytical Insights (Interactive Charts)

• ⏰ 24-Hour Timeline: A customized Plotly scatter plot mapping exactly when events occurred in the last day. Y-axis labels are automatically abbreviated (e.g., 🍼 Form., 🛟 Tummy) to maximize chart space on mobile.

• 🍼 Milk Intake: Stacked bar charts separating Formula and Breast Milk, overlaid with an orange line tracking Feed Counts and a grey spline tracking the 7-Period Volume Trend.

• 🚽 Output & 🛟 Activities: Dedicated grouped bar charts for Wet vs. Dirty diapers, Tummy Time minutes, and Pumping yields—aggregable by Daily, Weekly, Monthly, or All Time views.

• 🩺 Health: Selectable toggle to switch between Sleep Duration, Body Temperature (plotted as a line chart), and Medication Dose counts.

3. 📈 Growth Percentile Engine (HK MCHC Standards)

A specialized mathematical engine built into the dashboard that tracks Weight, Height, and Head Size.

• Automatically plots the baby's data against the official Hong Kong Department of Health (MCHC) growth percentile curves (3rd, 15th, 50th, 85th, and 97th percentiles).

• Uses logistic interpolation to precisely estimate the baby's current exact percentile bracket.

• Features a smart X-Axis slider that defaults to tightly framing the baby's current age ± 6 months.

4. 💉 Intelligent Vaccine Tracker

A dynamic matrix that maps standard baby logs to the Hong Kong Childhood Immunisation Programme.

• Regex Scanning: Automatically scans the Notes / Details column for keywords (e.g., BCG, 6-in-1, PCV, Rota) to check off completed milestones.

• Smart Statuses: Calculates current age in days to tag vaccines as ✅ Done, 🟡 Due Soon (within 30 days), ⚠️ Overdue, or ⏳ Upcoming.

5. 📋 Database Logs

A raw data viewer anchored at the bottom of the app. It includes a multi-select dropdown for specific Event Types and an open text box to deeply search through historical notes, formulas, or dates.

🏗️ Data Architecture (Google Sheets)

This app uses a publicly viewable CSV export link from a Google Sheet as its primary database. To build your own, your Google Sheet must have the following exact column headers (case-insensitive trimming is applied):

1. DateTime (e.g., 2026-07-24 14:30)

2. Event Type (Must match one of the expected strings below, though the app includes a standardizer function for flexibility)

3. Value (Optional) (Numeric values: mL, Mins, hrs, °C, kg, cm, or Cnt)

4. Notes / Details (Optional) (String text, essential for Vaccine keyword tracking)

Supported Event Types:
Formula (mL), Breast Milk (mL), Wet Diaper (Cnt), Poop (Cnt), Pumping (mL), Tummy Time (Mins), Sleep (hrs), Temp (°C), Meds (Cnt), Weight (kg), Height (cm), Head Size (cm), Vaccine (Cnt)

📱 iOS Shortcut Integration

The dashboard features a persistent header row with an "➕ Add" button. This button is hardcoded with a deep link to an iOS Shortcut:
shortcuts://run-shortcut?name=Riley%20Tracker

To use this:

1. Open the Apple Shortcuts app on your iPhone.

2. Create a new shortcut named exactly Riley Tracker.

3. Build the shortcut to prompt the user for an Event Type and Value, and have it securely append that data to your Google Sheet (via Google Sheets API or a webhook service like Zapier/Make).

4. Tapping "Add" in the dashboard will instantly launch the native iOS prompt.

⚙️ Configuration

The sidebar includes real-time settings that instantly recalculate the dashboard:

• Google Sheet URL: Swap databases on the fly.

• Timezone Offset: Default is 8 (HKT). Adjust to your local UTC offset to ensure the "Last Fed" timers are perfectly accurate.

• Birth Date & Gender: Essential for the Growth Chart engine to accurately calculate age-in-months and apply the correct Boy/Girl percentile curves.

🛠️ Tech Stack

• Framework: Streamlit (Frontend & Application Logic)

• Data Pipeline: Pandas, NumPy (Data cleaning, rolling averages, interpolation)

• Visualizations: Plotly Express & Plotly Graph Objects (Interactive, mobile-responsive charts)

• Styling: Deep Custom CSS injections targeting Streamlit data-testids for tailored UX.

📄 License

This project is open-source and available under the MIT License.
