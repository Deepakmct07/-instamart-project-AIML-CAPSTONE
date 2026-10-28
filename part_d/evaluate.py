"""Evaluates (1) RAG retrieval/refusal on policy_eval.csv and (2) the refund agent on agent_scenarios.csv."""
import sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE/"backend"))
import rag, agent
RAW = HERE.parent/"part_a/data/raw"; OUT = HERE/"outputs"; OUT.mkdir(exist_ok=True)
qa = pd.read_csv(RAW/"policy_eval.csv").fillna(""); rows = []
for r in qa.itertuples():
    hits = rag.retrieve(r.question, 3); out_of_scope = r.expected_doc == "NONE"
    refused = hits[0]["score"] < rag.MIN_SCORE
    ok = refused if out_of_scope else (any(r.expected_fact.lower() in h["text"].lower() for h in hits) and hits[0]["doc"] == r.expected_doc)
    rows.append((r.question, r.expected_doc, hits[0]["doc"], hits[0]["score"], ok))
qa_df = pd.DataFrame(rows, columns=["question", "expected_doc", "top_doc", "top_score", "pass"]); qa_df.to_csv(OUT/"rag_eval.csv", index=False)
print(qa_df[["question", "top_doc", "top_score", "pass"]].to_string(index=False)); print(f"RAG pass rate: {qa_df['pass'].mean():.0%}\n")
sc = pd.read_csv(RAW/"agent_scenarios.csv"); rows = []
for r in sc.itertuples():
    res = agent.run_agent(r.message, r.customer_id)
    ok = res["outcome"] == r.expected_outcome and abs(res["refund_inr"] - r.expected_refund_inr) < 0.01
    rows.append((r.scenario_id, r.expected_outcome, res["outcome"], r.expected_refund_inr, res["refund_inr"], len(res["trace"]), ok))
ag = pd.DataFrame(rows, columns=["id", "expected", "got", "exp_inr", "got_inr", "steps", "pass"]); ag.to_csv(OUT/"agent_eval.csv", index=False)
print(ag.to_string(index=False)); print(f"Agent pass rate: {ag['pass'].mean():.0%}")
