# import httpx
# import os
# from dotenv import load_dotenv

# load_dotenv()

# TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

# async def send_to_telex(payload: dict):
#     if not TELEX_WEBHOOK_URL:
#         raise ValueError("Missing TELEX_WEBHOOK_URL in .env")
#     async with httpx.AsyncClient() as client:
#         response = await client.post(TELEX_WEBHOOK_URL, json=payload)
#         return response.json()

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")


async def send_to_telex(payload: dict):
    """Send payload to the default webhook URL in .env."""
    if not TELEX_WEBHOOK_URL:
        raise ValueError("Missing TELEX_WEBHOOK_URL in .env")
    async with httpx.AsyncClient() as client:
        response = await client.post(TELEX_WEBHOOK_URL, json=payload)
        return response.json()


async def send_telex_update(a2a, text: str):
    """
    Send a follow-up message to Telex using the pushNotificationConfig
    embedded in the A2A payload.
    """
    try:
        webhook_url = a2a.params.configuration.pushNotificationConfig.url
        token = a2a.params.configuration.pushNotificationConfig.token

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "jsonrpc": "2.0",
            "id": a2a.id,
            "result": {
                "id": a2a.params.message.taskId or "task-auto",
                "status": {
                    "state": "completed",
                    "message": {
                        "role": "agent",
                        "parts": [{"kind": "text", "text": text}],
                    },
                },
                "artifacts": [],
                "kind": "task",
            },
        }

        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, headers=headers, json=payload)

    except Exception as e:
        print(f"[Webhook Error] {e}")
