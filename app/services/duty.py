from datetime import date

from app import state as st
from app.mattermost import post_to_channel


async def run_daily_duty() -> None:
    """Scheduler job: announce today's duty person on working days."""
    s = st.load()
    today = date.today()
    today_str = today.isoformat()

    if not st.is_working_day(today, s.skipped_dates):
        return
    if s.last_duty_date == today_str:
        return

    person = s.people[s.duty_index]
    next_idx = (s.duty_index + 1) % len(s.people)
    next_person = s.people[next_idx]
    nxt = st.next_working_day(today, s.skipped_dates)

    await post_to_channel(
        f"📋 **Дежурный сегодня:** {person}\n"
        f"Задача: проверить логи 🔍\n"
        f"_Следующий рабочий день ({nxt.strftime('%d.%m')}): {next_person}_"
    )

    s.last_duty_date = today_str
    s.duty_index = next_idx
    st.save(s)


async def handle_skip() -> str:
    s = st.load()
    today = date.today()
    today_str = today.isoformat()

    if today.weekday() >= 5:
        return "⚠️ Сегодня уже выходной — скипать нечего."
    if today_str in s.skipped_dates:
        return "⚠️ Сегодня уже отмечен как нерабочий день."

    s.skipped_dates.append(today_str)

    if s.last_duty_date == today_str:
        s.duty_index = (s.duty_index - 1) % len(s.people)
        s.last_duty_date = None

    person = s.people[s.duty_index]
    nxt = st.next_working_day(today, s.skipped_dates)
    st.save(s)

    msg = (
        f"🏖️ Сегодня ({today.strftime('%d.%m.%Y')}) — нерабочий день.\n"
        f"Дежурство перенесено: **{person}** заступает {nxt.strftime('%d.%m.%Y (%A)')}"
    )
    await post_to_channel(msg)
    return msg


async def handle_next() -> str:
    s = st.load()
    today_str = date.today().isoformat()

    old_person = s.people[s.duty_index]
    s.duty_index = (s.duty_index + 1) % len(s.people)
    new_person = s.people[s.duty_index]

    if s.last_duty_date == today_str:
        s.last_duty_date = None

    st.save(s)

    msg = (
        f"⏭️ Очередь сдвинута: ~~{old_person}~~ → **{new_person}**\n"
        f"Следующее дежурство: **{new_person}**"
    )
    await post_to_channel(msg)
    return msg


async def handle_status() -> str:
    s = st.load()
    today = date.today()
    today_str = today.isoformat()

    person = s.people[s.duty_index]

    if s.last_duty_date == today_str:
        duty_line = f"Сегодня дежурит: **{person}** ✅"
    elif st.is_working_day(today, s.skipped_dates):
        duty_line = f"Ожидает объявления (в {s.post_hour:02d}:{s.post_minute:02d}): **{person}**"
    else:
        nxt = st.next_working_day(today, s.skipped_dates)
        duty_line = f"Сегодня нерабочий. Следующий: **{person}** ({nxt.strftime('%d.%m')})"

    queue_lines = "\n".join(
        f"{'→ ' if i == s.duty_index else '   '}{p}"
        for i, p in enumerate(s.people)
    )
    return (
        f"{duty_line}\n\n"
        f"**Очередь:**\n```\n{queue_lines}\n```\n"
        f"_Ежедневное сообщение: {s.post_hour:02d}:{s.post_minute:02d} по будням_"
    )
