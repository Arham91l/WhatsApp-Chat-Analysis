# 💬 WhatsApp Chat Analyser

A **Streamlit** dashboard for analysing WhatsApp group and individual chats.

## Features

| Feature | Details |
|---|---|
| 📊 **Overall & Individual Analysis** | Analyse the entire group or drill down to a specific member |
| ⏰ **12-hr & 24-hr Clock Support** | Auto-detects AM/PM and 24-hour formats |
| 📈 **Timeline** | Daily and monthly message activity charts |
| 🔥 **Activity Heatmap** | Day × Hour heatmap to spot when the group is most active |
| 👥 **Most Active Users** | Bar chart, pie chart, and leaderboard |
| ☁️ **Word Cloud** | Visual word frequency (common stop-words removed) |
| 😊 **Emoji Analysis** | Top emojis used, with counts |
| 📊 **Top Words** | Most common words ranked |
| 📅 **Date Filter** | Filter any analysis to a specific date range |

## Folder Structure

```
whatsapp_analyzer/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md
└── utils/
    ├── __init__.py
    ├── parser.py           # WhatsApp chat parser (12-hr + 24-hr)
    └── analysis.py         # All analytics functions
```

## Quick Start

### 1. Prerequisites
- **Python 3.10 or higher** (3.11 recommended)

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

## How to Export a WhatsApp Chat

**Android:**
1. Open the chat or group
2. Tap ⋮ (three dots) → **More** → **Export Chat**
3. Select **Without Media**
4. Save / share the `.txt` file

**iPhone:**
1. Open the chat or group
2. Tap the contact/group name → **Export Chat**
3. Select **Without Media**
4. Share the `.txt` file

## Notes

- Large chats (millions of messages) may take a few seconds to parse.
- System messages like "Media omitted", "Missed call", and deleted messages are automatically filtered out.
- The parser handles both narrow no-break space (`\u202f`) and regular space before AM/PM.

## App link
https://whatsapp-chat-analysis-zk2ekuwkuffeimtmiijysq.streamlit.app/
