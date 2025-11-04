import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")


async def send_telex_update(a2a, text: str):
    """
    Send A2A task completion message to Telex via pushNotificationConfig.
    This version fully aligns with the A2A JSON-RPC 2.0 message schema.
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
                "kind": "task",  #  Telex expects top-level 'kind'
                "id": a2a.params.message.taskId or str(uuid.uuid4()),
                "contextId": str(uuid.uuid4()),
                "status": {
                    "state": "completed",
                    "message": {
                        "kind": "message",              #  REQUIRED
                        "messageId": str(uuid.uuid4()), #  REQUIRED
                        "role": "agent",                #  REQUIRED
                        "parts": [
                            {
                                "kind": "text",
                                "text": text
                            }
                        ],
                        "taskId": a2a.params.message.taskId or "task-auto"
                    },
                },
                "artifacts": [],
                "history": [],  #  Optional but recommended by Telex schema
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Sent Telex-compliant update ({response.status_code})")
            return response.json()

    except Exception as e:
        print(f"[Webhook Error] {e}")
