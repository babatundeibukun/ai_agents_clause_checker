from pathlib import Path
from dotenv import load_dotenv


import os

# Explicitly load .env from project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

print("DEBUG: GEMINI_API_KEY =", os.getenv("GEMINI_API_KEY"))

from fastapi import FastAPI

from fastapi.responses import JSONResponse
from app.models.a2a import A2ARequest
from app.analyzer import analyze_contract
from app.agent_card import agent_card




from app.models.a2a import A2ARequest
from app.analyzer import analyze_contract
from app.agent_card import agent_card

app = FastAPI(title="Telex Contract Checker Agent")

@app.get("/")
def root():
    return {"status": "running", "agent": "Contract Risk Analyzer"}

@app.get("/agent.json")
def get_agent_card():
    return JSONResponse(agent_card)

@app.post("/a2a/contract-checker")
def handle_a2a_request(a2a: A2ARequest):
    """Handle A2A messages from Telex"""
    try:
        message = a2a.params.message.parts[0].text
        result = analyze_contract(message)
        return {
            "jsonrpc": "2.0",
            "id": a2a.id,
            "result": {
                "id": a2a.params.message.taskId or "task-auto",
                "status": {
                    "state": "completed",
                    "message": {
                        "role": "agent",
                        "parts": [{"kind": "text", "text": result}],
                    },
                },
                "artifacts": [],
                "kind": "task",
            },
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": a2a.id,
            "error": {"message": str(e)},
        }

if __name__ == "_main_":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port,reload=True)