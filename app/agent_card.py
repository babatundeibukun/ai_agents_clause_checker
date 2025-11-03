agent_card = {
    "name": "Contract Risk Analyzer",
    "version": "1.0.0",
    "description": "Analyzes contract clauses for potential legal or compliance risks using Gemini and rule-based fallback.",
    "author": "Ibukun Babatunde",
    "capabilities": ["analyze_contract"],
    "a2a": {
        "endpoint": "/a2a/contract-checker",
        "methods": ["message/send"]
    }
}
