"""
WhatsApp Chat Analyser v2
Supports: 12-hr & 24-hr formats | Media & Non-media exports | Group & Individual analysis
"""

import io
import zipfile

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from PIL import Image

from utils.analysis import (
    filter_user, generate_wordcloud, get_active_users,
    get_activity_heatmap, get_basic_stats, get_common_words,
    get_daily_timeline, get_emoji_stats, get_media_heatmap,
    get_media_per_user, get_media_stats, get_media_timeline,
    get_media_type_over_time, get_monthly_timeline,
)
from utils.parser import parse_whatsapp_chat

# ══════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="WhatsApp Analyser",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
# THEME & CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=Nunito:wght@400;500;600&display=swap');

:root {
    --bg:       #0f1117;
    --surface:  #1a1d27;
    --surface2: #22263a;
    --border:   #2e3250;
    --accent:   #25d366;
    --accent2:  #128c7e;
    --accent3:  #34b7f1;
    --warn:     #ffb347;
    --danger:   #ff6b6b;
    --text:     #e8eaf6;
    --muted:    #7c82a8;
    --card-r:   14px;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    color: var(--text);
}

.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f18 0%, #0f1117 100%);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em;
    color: var(--muted) !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: rgba(37,211,102,0.07) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--card-r);
    padding: 18px 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: #0a1a10 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 16px rgba(37,211,102,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(37,211,102,0.4) !important;
}

/* Custom components */
.hero {
    background: linear-gradient(135deg, #0d2318 0%, #0f1a2e 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 48px 40px;
    text-align: center;
    margin-bottom: 24px;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 12px;
}
.hero p {
    color: var(--muted);
    font-size: 1rem;
    margin: 0;
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--accent);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border-left: 3px solid var(--accent);
    padding-left: 10px;
    margin: 28px 0 14px;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--card-r);
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}
.kpi-icon { font-size: 1.6rem; margin-bottom: 8px; }
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 6px;
}

.media-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.05em;
    font-weight: 500;
}
.badge-image    { background: rgba(52,183,241,0.15); color: #34b7f1; border: 1px solid rgba(52,183,241,0.3); }
.badge-video    { background: rgba(255,107,107,0.15); color: #ff6b6b; border: 1px solid rgba(255,107,107,0.3); }
.badge-audio    { background: rgba(255,179,71,0.15);  color: #ffb347; border: 1px solid rgba(255,179,71,0.3); }
.badge-document { background: rgba(37,211,102,0.15);  color: #25d366; border: 1px solid rgba(37,211,102,0.3); }
.badge-unknown  { background: rgba(124,130,168,0.15); color: #7c82a8; border: 1px solid rgba(124,130,168,0.3); }

.chat-mode-pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
}
.pill-media    { background: rgba(37,211,102,0.15); color: var(--accent); border: 1px solid rgba(37,211,102,0.3); }
.pill-nomedia  { background: rgba(52,183,241,0.15); color: var(--accent3); border: 1px solid rgba(52,183,241,0.3); }

.plotly-bg { background: var(--surface); border-radius: var(--card-r); padding: 16px; border: 1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# PLOT HELPERS  (dark theme, consistent style)
# ══════════════════════════════════════════════════════
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(26,29,39,0.6)",
    font=dict(family="Nunito", color="#e8eaf6"),
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(gridcolor="rgba(46,50,80,0.6)", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="rgba(46,50,80,0.6)", showgrid=True, zeroline=False),
    legend=dict(bgcolor="rgba(26,29,39,0.9)", bordercolor="#2e3250", borderwidth=1),
    hovermode="x unified",
)

GREEN   = "#25d366"
BLUE    = "#34b7f1"
ORANGE  = "#ffb347"
RED     = "#ff6b6b"
PURPLE  = "#a78bfa"
PALETTE = [GREEN, BLUE, ORANGE, RED, PURPLE, "#f9a8d4", "#6ee7b7", "#fde68a"]


def apply_layout(fig, height=400, **extra):
    layout = {**PLOT_LAYOUT, "height": height, **extra}
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 16px;'>
        <div style='font-family: Syne; font-size: 1.4rem; font-weight: 800;
                    background: linear-gradient(135deg, #25d366, #34b7f1);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            💬 WA Analyser
        </div>
        <div style='font-family: DM Mono; font-size: 0.62rem; color: #7c82a8;
                    letter-spacing: 0.12em; margin-top: 4px;'>
            GROUP & INDIVIDUAL ANALYSIS
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📂 Upload Chat**")
    uploaded_file = st.file_uploader(
        "WhatsApp export (.txt or .zip)",
        type=["txt", "zip"],
        label_visibility="collapsed",
        help="Export chat → Without Media (.txt) OR With Media (.zip)",
    )

    st.markdown("""
    <div style='font-family: DM Mono; font-size: 0.62rem; color: #7c82a8;
                line-height: 1.8; margin-top: 8px;'>
    HOW TO EXPORT<br>
    ▸ Open chat → ⋮ → More<br>
    ▸ Export Chat<br>
    ▸ With or Without Media<br>
    ▸ Upload the .txt or .zip
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    selected_user = "Overall"
    date_range    = None

# ══════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════
if uploaded_file is None:
    st.markdown("""
    <div class='hero'>
        <div style='font-size:4rem; margin-bottom:16px;'>💬</div>
        <h1>WhatsApp Chat Analyser</h1>
        <p>Upload your WhatsApp export and get deep insights on messages,<br>
        media, activity patterns, emojis, and more — for the whole group or any individual.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "📈", "Timeline Analysis", "Daily & monthly message trends, busiest periods"),
        (c2, "🖼️", "Media Intelligence", "Image, video, audio & document breakdowns"),
        (c3, "🔥", "Activity Heatmaps", "Discover when your group is most active"),
    ]:
        col.markdown(f"""
        <div class='kpi-card' style='text-align:center; padding: 28px 20px;'>
            <div style='font-size:2.2rem; margin-bottom:10px;'>{icon}</div>
            <div style='font-family: Syne; font-size: 1rem; font-weight: 700;
                        color: #e8eaf6; margin-bottom: 6px;'>{title}</div>
            <div style='font-size: 0.82rem; color: #7c82a8;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
# PARSE
# ══════════════════════════════════════════════════════
media_files = {}   # filename → bytes

if uploaded_file.name.endswith(".zip"):
    with zipfile.ZipFile(uploaded_file) as z:
        names = z.namelist()
        txt_files = [n for n in names if n.endswith(".txt")]
        chat_name = next((n for n in txt_files if "_chat" in n.lower()), txt_files[0] if txt_files else None)
        if chat_name is None:
            st.error("No .txt file found inside the ZIP.")
            st.stop()
        raw_text = z.read(chat_name).decode("utf-8", errors="ignore")
        # Load media files
        img_exts = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        for name in names:
            if any(name.lower().endswith(e) for e in img_exts):
                media_files[name.split("/")[-1]] = z.read(name)
    has_media_export = True
else:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    has_media_export = False

df = parse_whatsapp_chat(raw_text)
if df.empty:
    st.error("Could not parse the chat. Make sure it's a valid WhatsApp export.")
    st.stop()

# ── Sidebar controls (after parse) ────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("**👤 Filter**")
    all_users     = sorted(df["user"].unique().tolist())
    selected_user = st.selectbox("View", ["Overall"] + all_users, label_visibility="collapsed")

    st.markdown("**📅 Date Range**")
    d_min, d_max = df["date"].min(), df["date"].max()
    date_range   = st.date_input("", value=(d_min, d_max),
                                 min_value=d_min, max_value=d_max,
                                 label_visibility="collapsed")

# Apply date filter
df_all = df.copy()
if len(date_range) == 2:
    df_all = df_all[(df_all["date"] >= date_range[0]) & (df_all["date"] <= date_range[1])]

df_view = filter_user(df_all, selected_user)

if df_view.empty:
    st.warning("No messages found for the selected filters.")
    st.stop()

# ══════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════
has_any_media = df_view["is_media"].any()
mode_pill = (
    "<span class='chat-mode-pill pill-media'>📦 WITH MEDIA</span>"
    if has_media_export else
    "<span class='chat-mode-pill pill-nomedia'>💬 TEXT ONLY</span>"
)

label = f"Group Analysis" if selected_user == "Overall" else f"{selected_user}"
st.markdown(f"""
<div style='display:flex; align-items:center; justify-content:space-between;
            padding: 20px 24px; background: var(--surface);
            border: 1px solid var(--border); border-radius: 16px; margin-bottom: 20px;'>
    <div>
        <div style='font-family: Syne; font-size: 1.6rem; font-weight: 800;'>{label}</div>
        <div style='font-family: DM Mono; font-size: 0.65rem; color: #7c82a8;
                    letter-spacing: 0.1em; margin-top: 4px;'>
            {df_all["user"].nunique()} PARTICIPANTS &nbsp;·&nbsp;
            {date_range[0] if len(date_range)==2 else d_min} → {date_range[1] if len(date_range)==2 else d_max}
        </div>
    </div>
    <div>{mode_pill}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════
stats = get_basic_stats(df_view)
icons = ["💬", "📝", "🖼️", "📖", "👥", "📅", "🔗", "⚡"]
labels = list(stats.keys())
values = list(stats.values())

cols = st.columns(4)
for i, col in enumerate(cols):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>{icons[i]}</div>
        <div class='kpi-value'>{values[i]:,}</div>
        <div class='kpi-label'>{labels[i]}</div>
    </div>
    """, unsafe_allow_html=True)

cols2 = st.columns(4)
for i, col in enumerate(cols2):
    j = i + 4
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>{icons[j]}</div>
        <div class='kpi-value'>{values[j]:,}</div>
        <div class='kpi-label'>{labels[j]}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════
tab_labels = ["📈 Timeline", "🔥 Heatmap", "👥 Users", "☁️ Word Cloud", "😊 Emojis", "📊 Top Words", "🖼️ Media"]
tabs = st.tabs(tab_labels)

# ════════════════════════════ TAB 1 — TIMELINE ════════
with tabs[0]:
    st.markdown("<div class='section-label'>Daily Message Activity</div>", unsafe_allow_html=True)
    daily = get_daily_timeline(df_view)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Messages"],
        name="Messages", line=dict(color=GREEN, width=2),
        fill="tozeroy", fillcolor="rgba(37,211,102,0.1)",
        hovertemplate="<b>%{x}</b><br>Messages: %{y}<extra></extra>",
    ))
    # 7-day rolling average
    daily["MA7"] = daily["Messages"].rolling(7, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["MA7"],
        name="7-day avg", line=dict(color=BLUE, width=1.5, dash="dot"),
        hovertemplate="<b>%{x}</b><br>7d avg: %{y:.1f}<extra></extra>",
    ))
    apply_layout(fig, height=340)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-label'>Monthly Overview</div>", unsafe_allow_html=True)
    monthly = get_monthly_timeline(df_view)
    fig2 = px.bar(monthly, x="Period", y="Messages",
                  color="Messages", color_continuous_scale="Greens",
                  text="Messages")
    fig2.update_traces(textposition="outside", textfont_size=10)
    apply_layout(fig2, height=320, xaxis_tickangle=-40, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════ TAB 2 — HEATMAP ════════
with tabs[1]:
    st.markdown("<div class='section-label'>Message Activity — Day × Hour</div>", unsafe_allow_html=True)
    hmap = get_activity_heatmap(df_view)

    fig_h, ax = plt.subplots(figsize=(18, 5))
    fig_h.patch.set_facecolor("#1a1d27")
    ax.set_facecolor("#1a1d27")
    sns.heatmap(hmap, cmap="Greens", linewidths=0.4, linecolor="#0f1117",
                ax=ax, cbar_kws={"label": "Messages", "shrink": 0.8},
                annot=False)
    ax.set_title("When Is Your Group Most Active?",
                 fontsize=13, color="#e8eaf6", fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day", color="#7c82a8", fontsize=10)
    ax.set_ylabel("Day of Week",  color="#7c82a8", fontsize=10)
    ax.tick_params(colors="#7c82a8")
    plt.setp(ax.get_xticklabels(), fontsize=8)
    plt.tight_layout()
    st.pyplot(fig_h)
    plt.close()

    flat = hmap.stack()
    if not flat.empty:
        busiest = flat.idxmax()
        c1, c2, c3 = st.columns(3)
        c1.metric("🕐 Peak Hour",    busiest[1])
        c2.metric("📅 Most Active Day", busiest[0])
        total_by_day = hmap.sum(axis=1)
        c3.metric("🏆 Top Day Overall", total_by_day.idxmax())

# ════════════════════════════ TAB 3 — USERS ══════════
with tabs[2]:
    if selected_user != "Overall":
        st.info("Switch to **Overall** to compare all participants.")
    else:
        st.markdown("<div class='section-label'>Most Active Participants</div>", unsafe_allow_html=True)
        active = get_active_users(df_all, top_n=15)

        c1, c2 = st.columns([3, 2])
        with c1:
            fig_u = px.bar(active, x="Messages", y="User", orientation="h",
                           color="Percentage", color_continuous_scale="Greens",
                           text="Percentage",
                           custom_data=["Percentage"])
            fig_u.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Messages: %{x}<br>Share: %{customdata[0]:.1f}%<extra></extra>",
            )
            apply_layout(fig_u, height=420, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_u, use_container_width=True)

        with c2:
            fig_pie = px.pie(active.head(8), names="User", values="Messages",
                             hole=0.45, color_discrete_sequence=PALETTE)
            fig_pie.update_traces(textposition="inside", textinfo="percent",
                                  hovertemplate="<b>%{label}</b><br>%{value} msgs (%{percent})<extra></extra>")
            apply_layout(fig_pie, height=420, showlegend=True,
                         legend=dict(orientation="v", x=1, y=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<div class='section-label'>Leaderboard</div>", unsafe_allow_html=True)
        styled = active.style.background_gradient(subset=["Messages", "Percentage"], cmap="Greens")
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ════════════════════════════ TAB 4 — WORDCLOUD ══════
with tabs[3]:
    st.markdown("<div class='section-label'>Word Cloud</div>", unsafe_allow_html=True)
    with st.spinner("Generating word cloud..."):
        wc = generate_wordcloud(df_view)
        fig_wc, ax_wc = plt.subplots(figsize=(14, 6))
        fig_wc.patch.set_facecolor("#1a1d27")
        ax_wc.set_facecolor("#1a1d27")
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc)

        buf = io.BytesIO()
        fig_wc.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                       facecolor="#1a1d27")
        st.download_button("⬇️ Download Word Cloud", buf.getvalue(),
                           "wordcloud.png", "image/png")
        plt.close()

# ════════════════════════════ TAB 5 — EMOJIS ═════════
with tabs[4]:
    st.markdown("<div class='section-label'>Top Emojis Used</div>", unsafe_allow_html=True)
    emoji_df = get_emoji_stats(df_view, top_n=20)

    if emoji_df.empty:
        st.info("No emojis found in the selected messages.")
    else:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.dataframe(emoji_df, use_container_width=True, hide_index=True, height=420)
        with c2:
            fig_e = px.bar(emoji_df, x="Emoji", y="Count",
                           color="Count", color_continuous_scale="Oranges",
                           text="Count")
            fig_e.update_traces(textposition="outside")
            apply_layout(fig_e, height=400)
            st.plotly_chart(fig_e, use_container_width=True)

        # Emoji pie
        st.markdown("<div class='section-label'>Emoji Share</div>", unsafe_allow_html=True)
        fig_ep = px.pie(emoji_df.head(10), names="Emoji", values="Count",
                        hole=0.4, color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig_ep.update_traces(textinfo="percent+label")
        apply_layout(fig_ep, height=340)
        st.plotly_chart(fig_ep, use_container_width=True)

# ════════════════════════════ TAB 6 — TOP WORDS ══════
with tabs[5]:
    st.markdown("<div class='section-label'>Most Common Words</div>", unsafe_allow_html=True)
    words_df = get_common_words(df_view, top_n=25)

    c1, c2 = st.columns([3, 2])
    with c1:
        fig_w = px.bar(words_df, x="Count", y="Word", orientation="h",
                       color="Count", color_continuous_scale="Blues",
                       text="Count")
        fig_w.update_traces(textposition="outside")
        apply_layout(fig_w, height=560,
                     yaxis=dict(autorange="reversed", gridcolor="rgba(46,50,80,0.4)"))
        st.plotly_chart(fig_w, use_container_width=True)
    with c2:
        styled = words_df.style.background_gradient(subset=["Count"], cmap="Blues")
        st.dataframe(styled, use_container_width=True, hide_index=True, height=560)

# ════════════════════════════ TAB 7 — MEDIA ══════════
with tabs[6]:
    if not has_any_media:
        st.markdown("""
        <div style='text-align:center; padding: 60px 20px;'>
            <div style='font-size: 3rem; margin-bottom: 12px;'>🖼️</div>
            <div style='font-family: Syne; font-size: 1.2rem; color: #e8eaf6;
                        margin-bottom: 8px;'>No Media Found</div>
            <div style='color: #7c82a8; font-size: 0.9rem;'>
                Re-export your chat with <b>With Media</b> to unlock this tab.<br>
                Media messages (photos, videos, voice notes, documents) will be analysed here.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        mstats = get_media_stats(df_view)

        # KPIs
        st.markdown("<div class='section-label'>Media Summary</div>", unsafe_allow_html=True)
        mc = st.columns(6)
        m_icons  = ["📦", "🖼️", "🎬", "🎵", "📄", "❓"]
        m_colors = ["pill-media", "badge-image", "badge-video",
                    "badge-audio", "badge-document", "badge-unknown"]
        for i, (col, (k, v)) in enumerate(zip(mc, mstats.items())):
            col.metric(f"{m_icons[i]} {k}", f"{v:,}")

        # Type breakdown pie
        st.markdown("<div class='section-label'>Media Type Breakdown</div>", unsafe_allow_html=True)
        type_data = {k: v for k, v in mstats.items() if k != "Total Media" and v > 0}
        if type_data:
            c1, c2 = st.columns([2, 3])
            with c1:
                fig_mt = px.pie(
                    names=list(type_data.keys()),
                    values=list(type_data.values()),
                    hole=0.45,
                    color_discrete_sequence=[BLUE, RED, ORANGE, GREEN, "#7c82a8"],
                )
                fig_mt.update_traces(textinfo="percent+label")
                apply_layout(fig_mt, height=320)
                st.plotly_chart(fig_mt, use_container_width=True)
            with c2:
                # Media per user
                st.markdown("<div class='section-label'>Top Media Senders</div>",
                            unsafe_allow_html=True)
                mpu = get_media_per_user(df_all if selected_user == "Overall" else df_view)
                if not mpu.empty:
                    fig_mu = px.bar(mpu, x="Media Count", y="User", orientation="h",
                                    color="Media Count", color_continuous_scale="Blues",
                                    text="Media Count")
                    fig_mu.update_traces(textposition="outside")
                    apply_layout(fig_mu, height=320,
                                 yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_mu, use_container_width=True)

        # Media timeline
        st.markdown("<div class='section-label'>Media Sharing Timeline</div>",
                    unsafe_allow_html=True)
        mt = get_media_timeline(df_view)
        if not mt.empty:
            fig_mtl = go.Figure()
            fig_mtl.add_trace(go.Scatter(
                x=mt["Date"], y=mt["Media Messages"],
                name="Media", line=dict(color=BLUE, width=2),
                fill="tozeroy", fillcolor="rgba(52,183,241,0.1)",
                hovertemplate="<b>%{x}</b><br>Media: %{y}<extra></extra>",
            ))
            apply_layout(fig_mtl, height=300)
            st.plotly_chart(fig_mtl, use_container_width=True)

        # Media heatmap
        st.markdown("<div class='section-label'>Media Activity Heatmap</div>",
                    unsafe_allow_html=True)
        mhmap = get_media_heatmap(df_view)
        if not mhmap.empty:
            fig_mh, ax_m = plt.subplots(figsize=(18, 4))
            fig_mh.patch.set_facecolor("#1a1d27")
            ax_m.set_facecolor("#1a1d27")
            sns.heatmap(mhmap, cmap="Blues", linewidths=0.4,
                        linecolor="#0f1117", ax=ax_m,
                        cbar_kws={"label": "Media Msgs", "shrink": 0.8})
            ax_m.set_title("When Is Media Shared?",
                           fontsize=12, color="#e8eaf6", fontweight="bold", pad=10)
            ax_m.tick_params(colors="#7c82a8")
            plt.tight_layout()
            st.pyplot(fig_mh)
            plt.close()

        # Image gallery (only for zip exports)
        if has_media_export and media_files:
            st.markdown("<div class='section-label'>Image Gallery</div>",
                        unsafe_allow_html=True)
            st.caption(f"{len(media_files)} images found in export")
            img_per_row = 4
            img_names   = list(media_files.keys())
            for row_start in range(0, min(len(img_names), 20), img_per_row):
                row_imgs = img_names[row_start: row_start + img_per_row]
                g_cols   = st.columns(img_per_row)
                for col, name in zip(g_cols, row_imgs):
                    try:
                        img = Image.open(io.BytesIO(media_files[name]))
                        col.image(img, caption=name, use_container_width=True)
                    except Exception:
                        col.write(name)
            if len(img_names) > 20:
                st.caption(f"Showing first 20 of {len(img_names)} images.")

# ══════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='font-family: DM Mono; font-size: 0.62rem; color: #2e3250;
            text-align: center; padding: 8px 0;'>
    WhatsApp Chat Analyser v2 &nbsp;·&nbsp; Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
