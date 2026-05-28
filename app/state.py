from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.config import DEFAULT_POST_HOUR, DEFAULT_POST_MINUTE, DUTY_PEOPLE
from app.db import get_conn


class DutyState(BaseModel):
    people: list[str] = Field(default_factory=lambda: list(DUTY_PEOPLE))
    duty_index: int = 0
    last_duty_date: Optional[str] = None
    skipped_dates: list[str] = Field(default_factory=list)
    post_hour: int = DEFAULT_POST_HOUR
    post_minute: int = DEFAULT_POST_MINUTE


def load() -> DutyState:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT people, duty_index, last_duty_date, skipped_dates, post_hour, post_minute"
                " FROM duty_state WHERE id = 1"
            )
            row = cur.fetchone()
    if row is None:
        return DutyState()
    people, duty_index, last_duty_date, skipped_dates, post_hour, post_minute = row
    return DutyState(
        people=list(people),
        duty_index=duty_index,
        last_duty_date=last_duty_date,
        skipped_dates=list(skipped_dates or []),
        post_hour=post_hour,
        post_minute=post_minute,
    )


def save(state: DutyState) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO duty_state
                    (id, people, duty_index, last_duty_date, skipped_dates, post_hour, post_minute)
                VALUES (1, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    people         = EXCLUDED.people,
                    duty_index     = EXCLUDED.duty_index,
                    last_duty_date = EXCLUDED.last_duty_date,
                    skipped_dates  = EXCLUDED.skipped_dates,
                    post_hour      = EXCLUDED.post_hour,
                    post_minute    = EXCLUDED.post_minute
                """,
                (
                    state.people,
                    state.duty_index,
                    state.last_duty_date,
                    state.skipped_dates,
                    state.post_hour,
                    state.post_minute,
                ),
            )
        conn.commit()


# ── Date helpers ──────────────────────────────────────────────────────────────

def is_working_day(d: date, skipped: list[str]) -> bool:
    return d.weekday() < 5 and d.isoformat() not in skipped


def next_working_day(from_date: date, skipped: list[str]) -> date:
    d = from_date + timedelta(days=1)
    while not is_working_day(d, skipped):
        d += timedelta(days=1)
    return d
