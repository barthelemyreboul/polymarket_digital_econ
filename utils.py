from datetime import datetime


def parse(ts: int) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

