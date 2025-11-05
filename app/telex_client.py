import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

async def send_telex_update(a2a, text: str):
    """
    Sends the final analysis back to Telex via its webhook (pushNotificationConfig.url).
    This structure matches Telex's display and schema expectations exactly.
    """
    try:
        # Safely access configuration (works for both dicts and objects)
        params = a2a.params if isinstance(a2a.params, dict) else vars(a2a.params)
        config = params.get("configuration", {})
        if not isinstance(config, dict):
            config = vars(config)

        push_config = config.get("pushNotificationConfig", {})
        if not isinstance(push_config, dict):
            push_config = vars(push_config)

        webhook_url = push_config.get("url")
        token = push_config.get("token")

        if not webhook_url or not token:
            raise ValueError("Missing webhook URL or token in A2A payload")

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Extract taskId safely
        message = params.get("message", {})
        if not isinstance(message, dict):
            message = vars(message)

        task_id = message.get("taskId", "task-auto")

        # ✅ Telex-compliant payload (visible in UI)
        payload = {
            "jsonrpc": "2.0",
            "id": getattr(a2a, "id", str(uuid.uuid4())),
            "result": {
                "kind": "task",
                "id": task_id,
                "status": {
                    "state": "completed",
                    "message": {
                        "kind": "message",
                        "messageId": str(uuid.uuid4()),
                        "role": "agent",
                        "parts": [
                            {"kind": "text", "text": text.strip()}
                        ],
                    },
                },
                "artifacts": [],
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ Sent to Telex successfully ({response.status_code})")
            return response.json()

    except Exception as e:
        print(f"[Webhook Error] {e}")
