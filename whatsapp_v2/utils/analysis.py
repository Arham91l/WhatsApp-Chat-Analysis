import re
from collections import Counter

import emoji
import pandas as pd
from wordcloud import WordCloud

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","it","this","that","was","are","be","as","i","you","he","she","we",
    "they","ok","okay","yes","no","ha","haha","lol","ye","yep","nope","ya",
    "media","omitted","https","http","www","will","have","has","had","do",
    "did","not","so","if","me","my","your","our","their","am","been","just",
    "what","how","when","where","why","who","can","cant","dont","its","im",
    "bhi","hai","hain","nahi","kya","aur","toh","mein","ko","se","ki","ka",
    "ke","ho","na","hi","tha","the","par","ab","ek","jo","woh","hum","koi",
}


def filter_user(df: pd.DataFrame, user: str) -> pd.DataFrame:
    if user and user != "Overall":
        return df[df["user"] == user].copy()
    return df.copy()


def get_basic_stats(df: pd.DataFrame) -> dict:
    text_df = df[~df["is_media"]]
    return {
        "Total Messages": len(df),
        "Text Messages":  len(text_df),
        "Media Shared":   int(df["is_media"].sum()),
        "Total Words":    int(text_df["message"].apply(lambda m: len(m.split())).sum()),
        "Unique Users":   df["user"].nunique(),
        "Active Days":    df["date"].nunique(),
        "Links Shared":   int(text_df["message"].apply(lambda m: len(re.findall(r"https?://\S+", m))).sum()),
        "Avg Msg/Day":    round(len(df) / max(df["date"].nunique(), 1), 1),
    }


def get_active_users(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    counts = df["user"].value_counts().head(top_n).reset_index()
    counts.columns = ["User", "Messages"]
    counts["Percentage"] = (counts["Messages"] / len(df) * 100).round(1)
    return counts


def get_daily_timeline(df: pd.DataFrame) -> pd.DataFrame:
    daily = df.groupby("date")["message"].count().reset_index()
    daily.columns = ["Date", "Messages"]
    return daily


def get_monthly_timeline(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["year", "month", "month_name"])["message"]
        .count().reset_index()
        .sort_values(["year", "month"])
        .rename(columns={"message": "Messages"})
    )
    monthly["Period"] = monthly["month_name"] + " " + monthly["year"].astype(str)
    return monthly[["Period", "Messages"]]


def get_activity_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    pivot = df.pivot_table(
        index="day_name", columns="hour",
        values="message", aggfunc="count"
    ).reindex(DAYS).fillna(0)
    pivot.columns = [f"{h:02d}:00" for h in pivot.columns]
    return pivot


def generate_wordcloud(df: pd.DataFrame) -> WordCloud:
    text_df = df[~df["is_media"]]
    text = " ".join(text_df["message"].tolist()).lower()
    words = [w for w in re.findall(r"\b[a-zA-Z\u0900-\u097F]{2,}\b", text)
             if w.lower() not in STOP_WORDS]
    wc = WordCloud(
        width=1000, height=450, background_color="white",
        colormap="plasma", min_font_size=10, max_words=200,
        prefer_horizontal=0.85,
    )
    return wc.generate(" ".join(words) or "no words")


def get_emoji_stats(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    all_emojis = [c for msg in df["message"] for c in msg if c in emoji.EMOJI_DATA]
    if not all_emojis:
        return pd.DataFrame(columns=["Emoji", "Count"])
    return pd.DataFrame(Counter(all_emojis).most_common(top_n), columns=["Emoji", "Count"])


def get_common_words(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    text_df = df[~df["is_media"]]
    words = [
        w.lower() for msg in text_df["message"]
        for w in re.findall(r"\b[a-zA-Z]{2,}\b", msg)
        if w.lower() not in STOP_WORDS
    ]
    return pd.DataFrame(Counter(words).most_common(top_n), columns=["Word", "Count"])


# ── Media analytics ────────────────────────────────────────────────────────────

def get_media_stats(df: pd.DataFrame) -> dict:
    media_df = df[df["is_media"]]
    return {
        "Total Media":    len(media_df),
        "Images":         int((media_df["media_type"] == "image").sum()),
        "Videos":         int((media_df["media_type"] == "video").sum()),
        "Audio":          int((media_df["media_type"] == "audio").sum()),
        "Documents":      int((media_df["media_type"] == "document").sum()),
        "Unknown/Omitted":int((media_df["media_type"] == "unknown").sum()),
    }


def get_media_per_user(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    media_df = df[df["is_media"]]
    if media_df.empty:
        return pd.DataFrame(columns=["User", "Media Count"])
    counts = media_df["user"].value_counts().head(top_n).reset_index()
    counts.columns = ["User", "Media Count"]
    return counts


def get_media_timeline(df: pd.DataFrame) -> pd.DataFrame:
    media_df = df[df["is_media"]]
    if media_df.empty:
        return pd.DataFrame(columns=["Date", "Media Messages"])
    daily = media_df.groupby("date")["message"].count().reset_index()
    daily.columns = ["Date", "Media Messages"]
    return daily


def get_media_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    media_df = df[df["is_media"]]
    if media_df.empty:
        return pd.DataFrame()
    pivot = media_df.pivot_table(
        index="day_name", columns="hour",
        values="message", aggfunc="count"
    ).reindex(DAYS).fillna(0)
    pivot.columns = [f"{h:02d}:00" for h in pivot.columns]
    return pivot


def get_media_type_over_time(df: pd.DataFrame) -> pd.DataFrame:
    media_df = df[df["is_media"] & df["media_type"].notna()]
    if media_df.empty:
        return pd.DataFrame()
    grouped = (
        media_df.groupby(["month_name", "year", "media_type"])["message"]
        .count().reset_index()
        .rename(columns={"message": "Count"})
    )
    grouped["Period"] = grouped["month_name"] + " " + grouped["year"].astype(str)
    return grouped
