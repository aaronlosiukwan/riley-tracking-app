🍼 Riley's Dash

Riley's Dash is a comprehensive, beautifully designed, and deeply analytical Streamlit dashboard built to track a baby's daily activities, growth metrics, and health milestones.

Designed for sleep-deprived parents, it pulls data directly from Google Sheets in real-time and visualizes it into actionable, AI-driven insights—all perfectly optimized for both desktop and mobile views.

✨ Features

• Real-Time Data Sync: Instantly fetches the latest logs from your Google Sheet with the click of a natively built "Refresh" button (complete with sleek toast notifications).

• Today's Highlights: An instant snapshot of the past 24 hours, displaying exact volumes, diaper outputs, pumping yields, and sleep durations. Includes a specialized 24-hour scatter timeline.

• Smart Analytics & Trends:

	• 🍼 Milk Intake: Stacked bar charts separating Formula and Breast Milk, overlaid with feed counts and 7-day rolling volume trendlines.

	• 🚽 Diapers & 🛟 Tummy Time: Daily tracking to ensure healthy digestion and motor skill development.

	• 📈 Growth Charts: Automatically plots Riley's Weight, Height, and Head Size against official HK MCHC (Department of Health) percentile lines (3rd to 97th). AI intelligently estimates her exact percentile trajectory.

• Vaccine Tracker: Automatically parses your log notes for keywords (e.g., BCG, 6-in-1, PCV) and cross-references them against the Hong Kong Childhood Immunisation Programme, displaying what's ✅ Done, 🟡 Due Soon, or ⚠️ Overdue.

• AI Insight Cards: Every chart is accompanied by an intelligent markdown summary (e.g., assessing if appetite is "trending upwards 📈" or calculating exact daily averages).

🛠️ Tech Stack

• Framework: Streamlit

• Data Manipulation: Pandas, NumPy

• Visualizations: Plotly Express & Plotly Graph Objects

• Backend / DB: Direct CSV export parsing via Google Sheets

🚀 Installation & Setup

1. Clone the repository:

[bash]
git clone [https://github.com/yourusername/rileys-dash.git](https://github.com/yourusername/rileys-dash.git)
cd rileys-dash


2. Install dependencies:
Make sure you have Python 3.9+ installed.

[bash]
pip install -r requirements.txt


3. Set up your Database (Google Sheets):

	• Create a Google Sheet with the following columns: DateTime, Event Type, Value (Optional), Notes / Details (Optional).

	• Ensure the Share Settings are set to "Anyone with the link can view".

	• You can update the DEFAULT_SHEET_URL in app.py with your sheet link.

4. Run the App:

[bash]
streamlit run app.py


📱 Mobile Integration (iOS Shortcuts)

The dashboard includes an "➕ Add" button hardcoded to trigger an iOS Shortcut (shortcuts://run-shortcut?name=Riley%20Tracker).
You can build a custom Apple Shortcut that prompts for data inputs (e.g., Milk Volume, Diaper Type) and automatically appends it as a new row to your Google Sheet using the Google Sheets API or a webhook.

📄 License

This project is open-source and available under the MIT License.
