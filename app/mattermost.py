import httpx

from app.config import MM_WEBHOOK_URL


async def post_to_channel(text: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(MM_WEBHOOK_URL, json={"text": text}, timeout=10)
