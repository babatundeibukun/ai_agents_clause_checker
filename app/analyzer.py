import os
import google.generativeai as genai

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Gemini API key not found in environment.")

genai.configure(api_key=GEMINI_API_KEY)

# Fallback rule-based keywords
RISK_KEYWORDS = ["terminate", "liability", "breach", "default", "penalty", "indemnify"]

def analyze_contract(contract_text: str) -> str:
    """Try Gemini first; fallback to rule-based if it fails."""
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(f"Analyze this contract clause for risk:\n\n{contract_text}")
        return response.text.strip()
    except Exception as e:
        print(f"[Warning] Gemini failed: {e}")
        found = [kw for kw in RISK_KEYWORDS if kw in contract_text.lower()]
        if found:
            return f"⚠️ Potential risk terms detected: {', '.join(found)}"
        return "✅ No obvious risk terms found."
