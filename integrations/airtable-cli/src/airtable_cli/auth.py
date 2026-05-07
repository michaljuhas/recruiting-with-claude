import os


def load_token(explicit: str | None = None) -> str:
    token = (explicit or os.environ.get("AIRTABLE_TOKEN") or "").strip()
    if not token:
        msg = "Missing token: set AIRTABLE_TOKEN or pass --token"
        raise ValueError(msg)
    return token


def load_base_id(explicit: str | None = None) -> str | None:
    bid = (explicit or os.environ.get("AIRTABLE_BASE_ID") or "").strip()
    return bid or None
