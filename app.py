"""
WhatsApp Chat Analyser — Streamlit Dashboard
Supports 12-hr and 24-hr clock formats, group & individual analysis.
"""

import io

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from utils.analysis import (
    filter_user,
    generate_wordcloud,
    get_active_users,
    get_activity_heatmap,
    get_basic_stats,
    get_common_words,
    get_daily_timeline,
    get_emoji_stats,
    get_monthly_timeline,
)
from utils.parser import parse_whatsapp_chat

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WhatsApp Chat Analyser",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .metric-value { font-size: 2rem; font-weight: 700; }
        .metric-label { font-size: 0.9rem; opacity: 0.85; }
        .section-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #2d3748;
            border-left: 4px solid #667eea;
            padding-left: 12px;
            margin: 24px 0 12px;
        }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px;
            border-radius: 8px 8px 0 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg",
        width=60,
    )
    st.title("WhatsApp Analyser")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📂 Upload WhatsApp Export (.txt)",
        type=["txt"],
        help="Export your chat: Chat > ⋮ > More > Export Chat (without media)",
    )

    st.markdown("---")
    st.markdown(
        """
        **How to export:**
        1. Open WhatsApp group/chat
        2. Tap ⋮ → *More* → *Export Chat*
        3. Choose **Without Media**
        4. Share the `.txt` file here
        """
    )

# ── main ───────────────────────────────────────────────────────────────────────
if uploaded_file is None:
    st.markdown(
        """
        <div style='text-align:center; padding: 80px 20px;'>
            <div style='font-size:80px;'>💬</div>
            <h1 style='color:#667eea;'>WhatsApp Chat Analyser</h1>
            <p style='font-size:1.1rem; color:#718096;'>
                Upload your WhatsApp chat export from the sidebar to get started.<br>
                Works with both <b>12-hour</b> and <b>24-hour</b> clock formats.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── parse ──────────────────────────────────────────────────────────────────────
raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
df = parse_whatsapp_chat(raw_text)

if df.empty:
    st.error(
        "⚠️ Could not parse the chat file. "
        "Make sure you exported **without media** and the file is a valid WhatsApp export."
    )
    st.stop()

# ── sidebar controls ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filter")
    all_users = sorted(df["user"].unique().tolist())
    user_options = ["Overall"] + all_users
    selected_user = st.selectbox("Select User", user_options)

    date_min, date_max = df["date"].min(), df["date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

# Apply filters
df_all = df.copy()  # keep full df for "most active users" in overall view
if len(date_range) == 2:
    df_all = df_all[
        (df_all["date"] >= date_range[0]) & (df_all["date"] <= date_range[1])
    ]

df_view = filter_user(df_all, selected_user)

if df_view.empty:
    st.warning("No messages found for the selected filters.")
    st.stop()

# ── header ─────────────────────────────────────────────────────────────────────
analysis_label = "Group Analysis" if selected_user == "Overall" else f"Analysis for {selected_user}"
st.markdown(f"## 💬 {analysis_label}")
st.caption(
    f"Chat: **{uploaded_file.name}** • "
    f"{df_all['user'].nunique()} participants • "
    f"{date_range[0] if len(date_range)==2 else date_min} → "
    f"{date_range[1] if len(date_range)==2 else date_max}"
)

# ── KPI cards ──────────────────────────────────────────────────────────────────
stats = get_basic_stats(df_view)
cols = st.columns(4)
icons = ["💬", "📝", "🖼️", "🔗"]
for col, (label, value), icon in zip(cols, stats.items(), icons):
    col.markdown(
        f"""
        <div class='metric-card'>
            <div style='font-size:2rem;'>{icon}</div>
            <div class='metric-value'>{value:,}</div>
            <div class='metric-label'>{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Timeline", "🔥 Heatmap", "👥 Active Users", "☁️ Word Cloud", "😊 Emojis", "📊 Top Words"])

# ── TAB 1 : Timeline ──────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("<div class='section-title'>Daily Timeline</div>", unsafe_allow_html=True)
    daily = get_daily_timeline(df_view)
    fig = px.line(
        daily,
        x="Date",
        y="Messages",
        template="plotly_white",
        color_discrete_sequence=["#667eea"],
    )
    fig.update_traces(fill="tozeroy", fillcolor="rgba(102,126,234,0.15)")
    fig.update_layout(hovermode="x unified", margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>Monthly Timeline</div>", unsafe_allow_html=True)
    monthly = get_monthly_timeline(df_view)
    fig2 = px.bar(
        monthly,
        x="Period",
        y="Messages",
        template="plotly_white",
        color="Messages",
        color_continuous_scale="Purples",
    )
    fig2.update_layout(xaxis_tickangle=-45, margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB 2 : Heatmap ───────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div class='section-title'>Activity Heatmap (Day × Hour)</div>", unsafe_allow_html=True)
    heatmap_data = get_activity_heatmap(df_view)

    fig_h, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(
        heatmap_data,
        cmap="YlGnBu",
        linewidths=0.3,
        linecolor="#edf2f7",
        ax=ax,
        cbar_kws={"label": "Messages"},
    )
    ax.set_title("WhatsApp Activity Heatmap", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Day of Week", fontsize=11)
    plt.tight_layout()
    st.pyplot(fig_h)
    plt.close()

    # Busiest hour & day
    flat = heatmap_data.stack()
    if not flat.empty:
        busiest = flat.idxmax()
        c1, c2 = st.columns(2)
        c1.metric("🕐 Busiest Hour", busiest[1])
        c2.metric("📅 Busiest Day", busiest[0])

# ── TAB 3 : Active Users ──────────────────────────────────────────────────────
with tabs[2]:
    if selected_user != "Overall":
        st.info("Switch to **Overall** view to see group-level user activity.")
    else:
        st.markdown("<div class='section-title'>Most Active Users</div>", unsafe_allow_html=True)
        active = get_active_users(df_all, top_n=15)

        c1, c2 = st.columns([3, 2])
        with c1:
            fig_u = px.bar(
                active,
                x="Messages",
                y="User",
                orientation="h",
                color="Messages",
                color_continuous_scale="Viridis",
                template="plotly_white",
            )
            fig_u.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=10))
            st.plotly_chart(fig_u, use_container_width=True)

        with c2:
            fig_pie = px.pie(
                active,
                names="User",
                values="Messages",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Purples_r,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(showlegend=False, margin=dict(t=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<div class='section-title'>Leaderboard</div>", unsafe_allow_html=True)
        st.dataframe(
            active.style.background_gradient(subset=["Messages"], cmap="Purples"),
            use_container_width=True,
            hide_index=True,
        )

# ── TAB 4 : Word Cloud ────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div class='section-title'>Word Cloud</div>", unsafe_allow_html=True)
    with st.spinner("Generating word cloud..."):
        wc = generate_wordcloud(df_view)
        fig_wc, ax_wc = plt.subplots(figsize=(14, 6))
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc)
        plt.close()

        # Download button
        buf = io.BytesIO()
        fig_wc2, ax_wc2 = plt.subplots(figsize=(14, 6))
        ax_wc2.imshow(wc, interpolation="bilinear")
        ax_wc2.axis("off")
        plt.tight_layout(pad=0)
        fig_wc2.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        st.download_button("⬇️ Download Word Cloud", buf.getvalue(), "wordcloud.png", "image/png")

# ── TAB 5 : Emojis ────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div class='section-title'>Emoji Analysis</div>", unsafe_allow_html=True)
    emoji_df = get_emoji_stats(df_view)

    if emoji_df.empty:
        st.info("No emojis found in the selected messages.")
    else:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.dataframe(emoji_df, use_container_width=True, hide_index=True)

        with c2:
            fig_e = px.bar(
                emoji_df,
                x="Emoji",
                y="Count",
                color="Count",
                color_continuous_scale="Oranges",
                template="plotly_white",
            )
            fig_e.update_layout(margin=dict(t=10))
            st.plotly_chart(fig_e, use_container_width=True)

# ── TAB 6 : Top Words ─────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("<div class='section-title'>Most Common Words</div>", unsafe_allow_html=True)
    words_df = get_common_words(df_view, top_n=25)

    c1, c2 = st.columns([3, 2])
    with c1:
        fig_w = px.bar(
            words_df,
            x="Count",
            y="Word",
            orientation="h",
            color="Count",
            color_continuous_scale="Teal",
            template="plotly_white",
        )
        fig_w.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=10))
        st.plotly_chart(fig_w, use_container_width=True)

    with c2:
        st.dataframe(
            words_df.style.background_gradient(subset=["Count"], cmap="Blues"),
            use_container_width=True,
            hide_index=True,
        )

# ── footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("WhatsApp Chat Analyser • Built with Streamlit & Plotly")
