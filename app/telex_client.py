import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

async def send_to_telex(payload: dict):
    if not TELEX_WEBHOOK_URL:
        raise ValueError("Missing TELEX_WEBHOOK_URL in .env")
    async with httpx.AsyncClient() as client:
        response = await client.post(TELEX_WEBHOOK_URL, json=payload)
        return response.json()
