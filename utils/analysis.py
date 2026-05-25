import re
from collections import Counter

import emoji
import pandas as pd
from wordcloud import WordCloud


DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ── helpers ────────────────────────────────────────────────────────────────────

def filter_user(df: pd.DataFrame, user: str) -> pd.DataFrame:
    """Return df filtered to a single user, or the full df for 'Overall'."""
    if user and user != "Overall":
        return df[df["user"] == user].copy()
    return df.copy()


# ── stats ──────────────────────────────────────────────────────────────────────

def get_basic_stats(df: pd.DataFrame) -> dict:
    total_messages = len(df)
    total_words    = df["message"].apply(lambda m: len(m.split())).sum()
    total_media    = df["message"].str.lower().str.contains("<media omitted>").sum()
    total_links    = df["message"].apply(lambda m: len(re.findall(r"https?://\S+", m))).sum()
    return {
        "Total Messages": int(total_messages),
        "Total Words":    int(total_words),
        "Media Shared":   int(total_media),
        "Links Shared":   int(total_links),
    }


# ── active users ───────────────────────────────────────────────────────────────

def get_active_users(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    counts = df["user"].value_counts().head(top_n).reset_index()
    counts.columns = ["User", "Messages"]
    counts["Percentage"] = (counts["Messages"] / len(df) * 100).round(2)
    return counts


# ── timeline ───────────────────────────────────────────────────────────────────

def get_daily_timeline(df: pd.DataFrame) -> pd.DataFrame:
    daily = df.groupby("date")["message"].count().reset_index()
    daily.columns = ["Date", "Messages"]
    return daily


def get_monthly_timeline(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["year", "month", "month_name"])["message"]
        .count()
        .reset_index()
    )
    monthly = monthly.sort_values(["year", "month"])
    monthly["Period"] = monthly["month_name"] + " " + monthly["year"].astype(str)
    monthly.columns = [*monthly.columns[:-1], "Messages"] if "message" not in monthly.columns else monthly.columns
    monthly = monthly.rename(columns={"message": "Messages"})
    return monthly[["Period", "Messages"]]


# ── heatmap ────────────────────────────────────────────────────────────────────

def get_activity_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(
        index="day_name",
        columns="hour",
        values="message",
        aggfunc="count",
    ).reindex(DAYS_ORDER)
    pivot.columns = [f"{h:02d}:00" for h in pivot.columns]
    return pivot.fillna(0)


# ── wordcloud ──────────────────────────────────────────────────────────────────

def generate_wordcloud(df: pd.DataFrame) -> WordCloud:
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "is", "it", "this", "that", "was", "are",
        "be", "as", "i", "you", "he", "she", "we", "they", "ok", "okay",
        "yes", "no", "ha", "haha", "lol", "ye", "yep", "nope", "ya",
        "media", "omitted", "https", "http", "www",
    }
    text = " ".join(df["message"].tolist()).lower()
    words = [w for w in re.findall(r"\b[a-z]{2,}\b", text) if w not in stop_words]
    text_clean = " ".join(words)
    wc = WordCloud(
        width=900,
        height=400,
        background_color="white",
        colormap="viridis",
        min_font_size=10,
        max_words=200,
    )
    return wc.generate(text_clean or "no words")


# ── emoji ──────────────────────────────────────────────────────────────────────

def get_emoji_stats(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    all_emojis = []
    for msg in df["message"]:
        all_emojis.extend(c for c in msg if c in emoji.EMOJI_DATA)
    if not all_emojis:
        return pd.DataFrame(columns=["Emoji", "Count"])
    counts = Counter(all_emojis).most_common(top_n)
    return pd.DataFrame(counts, columns=["Emoji", "Count"])


# ── most common words ──────────────────────────────────────────────────────────

def get_common_words(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "is", "it", "this", "that", "was", "are",
        "be", "as", "i", "you", "he", "she", "we", "they", "ok", "okay",
        "yes", "no", "ha", "haha", "lol", "ye", "yep", "nope", "ya",
        "media", "omitted", "https", "http", "www",
    }
    words = []
    for msg in df["message"]:
        words.extend(
            w.lower() for w in re.findall(r"\b[a-zA-Z]{2,}\b", msg)
            if w.lower() not in stop_words
        )
    counts = Counter(words).most_common(top_n)
    return pd.DataFrame(counts, columns=["Word", "Count"])
