import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

async def send_telex_update(a2a, text: str):
    """
    Send an async message back to Telex via the webhook in pushNotificationConfig.
    Fully matches A2A validation schema.
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
                "id": a2a.params.message.taskId or str(uuid.uuid4()),
                "contextId": str(uuid.uuid4()),  #  helps Telex link responses
                "status": {
                    "state": "completed",
                    "message": {
                        "kind": "message",                     #  required
                        "messageId": str(uuid.uuid4()),        #  required
                        "role": "agent",                       #  required
                        "parts": [
                            {
                                "kind": "text",
                                "text": text                   # your AI output
                            }
                        ],
                        "taskId": a2a.params.message.taskId or "task-auto",  #  for message trace
                        "kind": "message"
                    },
                },
                "artifacts": [],
                "kind": "task",
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ Telex update sent: {response.status_code}")
            return response.json()

    except Exception as e:
        print(f"[Webhook Error] {e}")
