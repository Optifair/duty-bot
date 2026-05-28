import psycopg2

from app.config import DATABASE_URL


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS duty_state (
                    id          INTEGER PRIMARY KEY,
                    people      TEXT[]  NOT NULL,
                    duty_index  INTEGER NOT NULL DEFAULT 0,
                    last_duty_date TEXT,
                    skipped_dates  TEXT[] NOT NULL DEFAULT '{}',
                    post_hour   INTEGER NOT NULL DEFAULT 9,
                    post_minute INTEGER NOT NULL DEFAULT 0
                )
            """)
        conn.commit()
