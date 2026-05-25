import re
import pandas as pd


def parse_whatsapp_chat(file_content: str) -> pd.DataFrame:
    """
    Parse WhatsApp chat export (supports 12-hr and 24-hr formats, both iOS and Android).
    Returns a cleaned DataFrame with datetime, user, message columns + derived fields.
    """
    # Handles:
    #   12-hr: 1/1/23, 10:05 AM - User: msg
    #   12-hr (narrow no-break space \u202f): 1/1/23, 10:05\u202fAM - User: msg
    #   24-hr: 1/1/23, 22:05 - User: msg
    pattern = (
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}"   # date
        r",\s"                                      # comma + space
        r"\d{1,2}:\d{2}"                            # HH:MM
        r"(?:[\s\u202f]?[APap][Mm])?)"             # optional AM/PM (with optional narrow-nbsp)
        r"\s-\s"                                    # " - "
        r"(.*?):\s"                                 # sender:
        r"(.*)"                                     # message
    )

    matches = re.findall(pattern, file_content)

    if not matches:
        return pd.DataFrame()

    dates, users, messages = zip(*matches)

    df = pd.DataFrame({"datetime": list(dates), "user": list(users), "message": list(messages)})

    # Normalise narrow no-break space before AM/PM
    df["datetime"] = (
        df["datetime"]
        .str.replace("\u202f", " ", regex=False)
        .str.replace("\u00a0", " ", regex=False)
        .str.strip()
    )

    df["datetime"] = pd.to_datetime(df["datetime"], format="mixed", dayfirst=False)

    # Derived columns
    df["year"]       = df["datetime"].dt.year
    df["month"]      = df["datetime"].dt.month
    df["day"]        = df["datetime"].dt.day
    df["hour"]       = df["datetime"].dt.hour
    df["minute"]     = df["datetime"].dt.minute
    df["month_name"] = df["datetime"].dt.month_name()
    df["day_name"]   = df["datetime"].dt.day_name()
    df["date"]       = df["datetime"].dt.date

    # Drop system messages (media omitted, deleted, etc.)
    system_phrases = [
        "<media omitted>",
        "this message was deleted",
        "missed voice call",
        "missed video call",
        "you deleted this message",
        "null",
    ]
    mask = df["message"].str.lower().isin(system_phrases)
    df = df[~mask].reset_index(drop=True)

    return df
