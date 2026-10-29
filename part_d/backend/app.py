"""Part D backend (FastAPI): guardrails -> route (refund agent | fraud escalation | RAG)."""
import re, sys, sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"part_c")); sys.path.insert(0, str(Path(__file__).parent))
from guardrails import validate_and_sanitize
import rag, agent
app = FastAPI(title="Instamart Support Co-pilot")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
REFUND = re.compile(r"\b(refund|money back|reimburse)\b", re.I)
FRAUD = re.compile(r"fraud|unauthori[sz]ed|hacked|never made", re.I)
POLICY_QUESTION = re.compile(
    r"\b(who|what|when|where|why|how|which)\b.*"
    r"\b(refunds?|money back|approval|approve|policy|limit|threshold|eligible)\b",
    re.I
)
class Chat(BaseModel): message: str; customer_id: str | None = None
@app.get("/health")
def health(): return {"ok": True, "chunks": len(rag.CHUNKS)}
@app.get("/customer/{cid}")
def customer(cid: str):
    con = sqlite3.connect(agent.DB); r = con.execute("SELECT segment, Recency, Frequency, Monetary FROM rfm_segments WHERE customer_id=?", (cid.upper(),)).fetchone()
    if not r: return {"customer_id": cid, "segment": "Unknown customer"}
    return {"customer_id": cid.upper(), "segment": r[0], "recency": r[1], "frequency": r[2], "monetary": None if r[3] is None else round(r[3], 2)}
@app.post("/chat")
def chat(req: Chat):
    g = validate_and_sanitize(req.message)
    if g.status == "blocked":
        return {"blocked": True, "reason": g.reason, "answer": "Please enter a valid message (not empty, and shorter)."}
        if POLICY_QUESTION.search(g.cleaned_text):
        r = rag.answer(g.cleaned_text)
        return {"intent": "policy_qa", **r}
    cid = req.customer_id.strip().upper() if req.customer_id else None
    if REFUND.search(g.cleaned_text) or "[LOOP]" in g.cleaned_text:
        r = agent.run_agent(g.cleaned_text, cid, g.order_ids)
        return {"intent": "refund", "decision": {"outcome": r["outcome"], "refund_inr": r["refund_inr"], "reason": r["reason"]}, "trace": r["trace"],
                "answer": r["answer"], "sources": rag.retrieve("refund policy", 2)}
    if FRAUD.search(g.cleaned_text):
        return {"intent": "fraud", "answer": "This looks like a possible fraud case. It is marked high priority and will reach our security team within 2 hours.",
                "sources": rag.retrieve("fraud ticket security team", 1)}
    r = rag.answer(g.cleaned_text); return {"intent": "policy_qa", **r}
