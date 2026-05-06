import json
import os
from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.config import DEFAULT_POST_HOUR, DEFAULT_POST_MINUTE, DUTY_PEOPLE, STATE_FILE


class DutyState(BaseModel):
    people: list[str] = Field(default_factory=lambda: list(DUTY_PEOPLE))
    duty_index: int = 0
    last_duty_date: Optional[str] = None
    skipped_dates: list[str] = Field(default_factory=list)
    post_hour: int = DEFAULT_POST_HOUR
    post_minute: int = DEFAULT_POST_MINUTE


def load() -> DutyState:
    try:
        with open(STATE_FILE) as f:
            return DutyState.model_validate(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return DutyState()


def save(state: DutyState) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(STATE_FILE)), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state.model_dump(), f, indent=2)


# ── Date helpers ──────────────────────────────────────────────────────────────

def is_working_day(d: date, skipped: list[str]) -> bool:
    return d.weekday() < 5 and d.isoformat() not in skipped


def next_working_day(from_date: date, skipped: list[str]) -> date:
    d = from_date + timedelta(days=1)
    while not is_working_day(d, skipped):
        d += timedelta(days=1)
    return d
