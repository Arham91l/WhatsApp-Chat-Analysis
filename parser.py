import re
import pandas as pd

MEDIA_PATTERN = re.compile(
    r'<[Mm]edia omitted>|'
    r'\S+\.(jpg|jpeg|png|mp4|mkv|opus|mp3|aac|pdf|docx|gif|webp|mov|wav)\s*\(file attached\)',
    re.IGNORECASE
)

MEDIA_TYPE_MAP = {
    'image':    r'\.(jpg|jpeg|png|gif|webp)',
    'video':    r'\.(mp4|mkv|avi|mov)',
    'audio':    r'\.(opus|mp3|aac|wav)',
    'document': r'\.(pdf|docx|txt|xlsx|pptx)',
}


def get_media_type(msg: str) -> str | None:
    msg = msg.lower()
    for mtype, pat in MEDIA_TYPE_MAP.items():
        if re.search(pat, msg):
            return mtype
    if '<media omitted>' in msg:
        return 'unknown'
    return None


def parse_whatsapp_chat(text: str) -> pd.DataFrame:
    pattern = (
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"
        r",\s\d{1,2}:\d{2}"
        r"(?:[\s\u202f]?[APap][Mm])?)"
        r"\s-\s(.*?):\s(.*)"
    )
    matches = re.findall(pattern, text)
    if not matches:
        return pd.DataFrame()

    dates, users, messages = zip(*matches)
    df = pd.DataFrame({"datetime": list(dates), "user": list(users), "message": list(messages)})

    df["datetime"] = (
        df["datetime"]
        .str.replace("\u202f", " ", regex=False)
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
    )
    df["datetime"] = pd.to_datetime(df["datetime"], format="mixed", dayfirst=False)

    df["year"]       = df["datetime"].dt.year
    df["month"]      = df["datetime"].dt.month
    df["day"]        = df["datetime"].dt.day
    df["hour"]       = df["datetime"].dt.hour
    df["minute"]     = df["datetime"].dt.minute
    df["month_name"] = df["datetime"].dt.month_name()
    df["day_name"]   = df["datetime"].dt.day_name()
    df["date"]       = df["datetime"].dt.date
    df["week"]       = df["datetime"].dt.isocalendar().week.astype(int)

    # Media flags
    df["is_media"]   = df["message"].apply(lambda m: bool(MEDIA_PATTERN.search(m)))
    df["media_type"] = df["message"].apply(
        lambda m: get_media_type(m) if MEDIA_PATTERN.search(m) else None
    )

    # Drop pure system messages
    system = ["this message was deleted", "missed voice call",
              "missed video call", "you deleted this message", "null"]
    df = df[~df["message"].str.lower().isin(system)].reset_index(drop=True)

    return df
