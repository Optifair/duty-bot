import re

from app import state as st
from app.mattermost import post_to_channel
from app.scheduler import scheduler


async def handle_time(arg: str) -> str:
    arg = arg.strip()

    if not arg:
        s = st.load()
        return f"⏰ Текущее время ежедневного сообщения: **{s.post_hour:02d}:{s.post_minute:02d}**"

    if not re.fullmatch(r"\d{1,2}:\d{2}", arg):
        return "⚠️ Неверный формат. Используй `HH:MM`, например: `/duty time 09:30`"

    h, m = map(int, arg.split(":"))
    if not (0 <= h < 24 and 0 <= m < 60):
        return "⚠️ Недопустимое время. Часы 0–23, минуты 0–59."

    s = st.load()
    old_h, old_m = s.post_hour, s.post_minute
    s.post_hour = h
    s.post_minute = m
    st.save(s)

    scheduler.reschedule_job(
        "daily_duty",
        trigger="cron",
        day_of_week="mon-fri",
        hour=h,
        minute=m,
    )

    msg = f"⏰ Время ежедневного сообщения изменено: {old_h:02d}:{old_m:02d} → **{h:02d}:{m:02d}**"
    await post_to_channel(msg)
    return msg
