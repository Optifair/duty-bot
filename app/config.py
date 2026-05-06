import os

MM_WEBHOOK_URL: str = os.environ["MM_WEBHOOK_URL"]

DUTY_PEOPLE: list[str] = [
    p.strip()
    for p in os.environ.get("DUTY_PEOPLE", "@alice,@bob,@charlie").split(",")
]

STATE_FILE: str = os.environ.get("STATE_FILE", "/data/state.json")

DEFAULT_POST_HOUR: int = int(os.environ.get("POST_HOUR", "9"))
DEFAULT_POST_MINUTE: int = int(os.environ.get("POST_MINUTE", "0"))

TZ: str = os.environ.get("TZ", "Europe/Moscow")
