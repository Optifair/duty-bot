from fastapi import APIRouter, Form

from app.services import duty, people, timing

router = APIRouter()

HELP_TEXT = (
    "**Команды /duty:**\n"
    "`/duty` или `/duty status` — текущий дежурный, очередь и время\n"
    "`/duty skip` — отметить сегодня нерабочим, перенести дежурство\n"
    "`/duty next` — сдвинуть очередь (пропустить текущего)\n"
    "`/duty time` — показать текущее время напоминания\n"
    "`/duty time HH:MM` — установить время, например `09:30`\n"
    "`/duty people` — показать список участников\n"
    "`/duty people set @a,@b,@c` — заменить весь список\n"
    "`/duty people add @name` — добавить участника\n"
    "`/duty people remove @name` — удалить участника\n"
    "`/duty help` — эта справка"
)


def _ephemeral(text: str) -> dict:
    return {"response_type": "ephemeral", "text": text}


@router.post("/duty")
async def slash_duty(text: str = Form(default="")):
    parts = text.strip().split(None, 1)
    sub = parts[0].lower() if parts else ""
    rest = parts[1] if len(parts) > 1 else ""

    match sub:
        case "skip":
            await duty.handle_skip()
            return _ephemeral("✅ Дежурство перенесено.")
        case "next":
            await duty.handle_next()
            return _ephemeral("✅ Очередь сдвинута.")
        case "" | "status":
            return _ephemeral(await duty.handle_status())
        case "time":
            return _ephemeral(await timing.handle_time(rest))
        case "people":
            return _ephemeral(await people.handle_people(rest))
        case _:
            return _ephemeral(HELP_TEXT)
