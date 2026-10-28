# Part D: RAG Assistant & Refund Agent
## What the code does
- `backend/rag.py`: policy documents (`part_a/data/policies/*.txt`) are chunked into 2-sentence windows with stride 1 (overlap keeps related facts together, each chunk keeps its source file). TF-IDF (1-2 grams) retrieves the top 3. If the best score is below 0.12 the assistant says it doesn't know instead of guessing. Gemini writes the grounded answer if a key is set, otherwise the best chunk is returned.
- `backend/agent.py`: refund agent as a bounded tool loop (max 6 steps, then FALLBACK to a human with a summary). Decisions are made in code from `refund_policy.txt`: completed orders only; delivered in more than 45 minutes means a full refund; up to INR 1000 is auto-approved (REFUND); above INR 1000 it is ESCALATE; cancelled or on-time orders are DENIED; unknown or someone else's order is NOT_FOUND. The LLM only phrases the reply.
- `backend/app.py` (FastAPI): guardrails (Part C), then routing to the refund agent, fraud escalation or RAG.
- `frontend/` (React + Vite): chat UI with outcome badges, agent steps, retrieved sources and the customer's Part B segment.
- `evaluate.py`: runs `policy_eval.csv` and `agent_scenarios.csv`.
Simplification: the "raise a refund within 7 days of delivery" rule is not enforced because the data is historical.
## Run
Run Parts A and B first.
```bash
cd part_d && python evaluate.py
cd backend && pip install -r requirements.txt && uvicorn app:app --reload      # API on :8000
cd part_d/frontend && npm install && npm run dev                              # UI on :5173
```
## Environment variables (copy `backend/.env.example` to `.env`, never commit it)
| Name | Where | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | backend (optional) | Enables LLM-written answers and few-shot classification |
| `VITE_API_URL` | frontend | Backend URL (default `http://localhost:8000`) |
## Deploy
Backend on Render using `render.yaml` at the repo root; frontend on Vercel with root `part_d/frontend` and `VITE_API_URL` set to the Render URL.
Live links: _add here after deploying_
## Key findings
- Policy Q&A: 14/14 pass (12 answerable questions retrieve the right document and fact in the top 3; the 2 out-of-scope questions are refused). See `outputs/rag_eval.csv`.
- Refund agent: 7/7 scenarios match the expected outcome and refund amount (REFUND x2, ESCALATE, DENIED x2, NOT_FOUND, FALLBACK). See `outputs/agent_eval.csv`.
- Customer PII never reaches the LLM: tickets are redacted first and order IDs stay server-side.
