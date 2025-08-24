# Agent Service (FastAPI)

A minimal question-orchestrator that returns typed steps the mobile app can render.

## Quick start

```bash
cd agent
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Test with curl:
```bash
# Create session
curl -s http://localhost:8000/sessions -X POST -H "Content-Type: application/json" -d '{}' | jq .

# Send an answer (replace SESSION_ID)
curl -s http://localhost:8000/sessions/SESSION_ID/answer -X POST -H "Content-Type: application/json" \
  -d '{"session_id":"SESSION_ID","question_id":"q_name","answer":{"kind":"free_text","value":"Roan"}}' | jq .
```
