from pathlib import Path
from dotenv import load_dotenv
import os
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.a2a import A2ARequest
from app.analyzer import analyze_contract
from app.agent_card import agent_card
from app.telex_client import send_telex_update

# Load .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Telex Contract Checker Agent")


@app.get("/")
def root():
    return {"status": "running", "agent": "Contract Risk Analyzer"}


@app.get("/agent.json")
def get_agent_card():
    return JSONResponse(agent_card)


@app.post("/a2a/contract-checker")
async def handle_a2a_request(a2a: A2ARequest, background_tasks: BackgroundTasks):
    """
    Handles A2A messages from Telex, analyzes the contract clause,
    and sends the result both via webhook (async) and directly in the HTTP response.
    """
    try:
        # Extract the text from the Telex message
        message = a2a.params.message.parts[0].text
        print(f"📩 Received contract clause: {message}")

        # Analyze the clause using Gemini + fallback logic
        result = analyze_contract(message)
        print(f"✅ Analysis completed. Sending back result to Telex...")

        # Send async webhook update to Telex
        background_tasks.add_task(send_telex_update, a2a, result)

        # ✅ Also return the same payload to Telex (ensures visible message in UI)
        return {
            "jsonrpc": "2.0",
            "id": a2a.id,
            "result": {
                "kind": "task",
                "id": a2a.params.message.taskId or "task-auto",
                "status": {
                    "state": "completed",
                    "message": {
                        "kind": "message",
                        "messageId": str(uuid.uuid4()),
                        "role": "agent",
                        "parts": [
                            {"kind": "text", "text": result.strip()}
                        ],
                    },
                },
                "artifacts": [],
            },
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": getattr(a2a, "id", str(uuid.uuid4())),
            "error": {"message": str(e)},
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
