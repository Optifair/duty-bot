import re

from app import state as st
from app.mattermost import post_to_channel


async def handle_people(arg: str) -> str:
    parts = arg.strip().split(None, 1)
    sub = parts[0].lower() if parts else ""
    rest = parts[1].strip() if len(parts) > 1 else ""

    s = st.load()

    if sub in ("", "list"):
        lines = "\n".join(
            f"{'→ ' if i == s.duty_index else '   '}{p}"
            for i, p in enumerate(s.people)
        )
        return f"**Участники (очередь):**\n```\n{lines}\n```"

    if sub == "set":
        if not rest:
            return "⚠️ Укажи список: `/duty people set @alice,@bob,@charlie`"
        new_people = [p.strip() for p in re.split(r"[,\s]+", rest) if p.strip()]
        if len(new_people) < 2:
            return "⚠️ Нужно минимум 2 участника."
        s.people = new_people
        s.duty_index = 0
        st.save(s)
        msg = (
            f"👥 Список участников обновлён: {', '.join(new_people)}\n"
            f"Очередь сброшена, следующий: **{new_people[0]}**"
        )
        await post_to_channel(msg)
        return msg

    if sub == "add":
        name = rest.strip()
        if not name:
            return "⚠️ Укажи имя: `/duty people add @dave`"
        if name in s.people:
            return f"⚠️ **{name}** уже есть в списке."
        s.people.append(name)
        st.save(s)
        msg = f"➕ **{name}** добавлен в очередь (позиция {len(s.people)})."
        await post_to_channel(msg)
        return msg

    if sub == "remove":
        name = rest.strip()
        if not name:
            return "⚠️ Укажи имя: `/duty people remove @alice`"
        if name not in s.people:
            return f"⚠️ **{name}** не найден в списке."
        if len(s.people) <= 2:
            return "⚠️ Нельзя удалить: нужно минимум 2 участника."
        removed_idx = s.people.index(name)
        s.people.remove(name)
        if removed_idx < s.duty_index:
            s.duty_index -= 1
        elif s.duty_index >= len(s.people):
            s.duty_index = 0
        st.save(s)
        msg = f"➖ **{name}** удалён из очереди."
        await post_to_channel(msg)
        return msg

    return "⚠️ Неизвестная подкоманда.\nИспользуй: `set @a,@b,@c` · `add @name` · `remove @name`"
