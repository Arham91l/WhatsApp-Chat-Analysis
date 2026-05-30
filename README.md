# 💬 WhatsApp Chat Analyser v2

A fully redesigned Streamlit dashboard with support for **media and non-media** exports,
**12-hr & 24-hr** clock formats, and both **group and individual** analysis.

## Features

| Tab | What You Get |
|---|---|
| 📈 **Timeline** | Daily activity with 7-day rolling average + monthly bar chart |
| 🔥 **Heatmap** | Day × Hour activity heatmap + peak time KPIs |
| 👥 **Users** | Bar chart, donut chart, styled leaderboard |
| ☁️ **Word Cloud** | Stop-word filtered, downloadable PNG |
| 😊 **Emojis** | Top 20 emojis, bar chart + pie chart |
| 📊 **Top Words** | Most common words (Hindi + English stop-words removed) |
| 🖼️ **Media** | Type breakdown, timeline, heatmap, top senders, image gallery |

## Folder Structure

```
whatsapp_v2/
├── app.py
├── requirements.txt
├── README.md
└── utils/
    ├── __init__.py
    ├── parser.py       # Chat parser — 12hr/24hr, media/non-media
    └── analysis.py     # All analytics & chart data functions
```

## Quick Start

```bash
# Python 3.10+ required
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## How to Export WhatsApp Chat

**Android:** Chat → ⋮ → More → Export Chat → With or Without Media  
**iPhone:** Chat → Contact name → Export Chat → With or Without Media

- **Without Media** → upload the `.txt` file
- **With Media** → upload the `.zip` file (enables Image Gallery + media type analysis)

## Link
https://whatsapp-chat-analysis-mkj7fps677llcpm3ktjpxy.streamlit.app/
