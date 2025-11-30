from datetime import datetime


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

