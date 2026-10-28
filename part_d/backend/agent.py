"""Refund agent: a bounded tool loop (max 6 steps). Decisions come from policy rules in code; the LLM only phrases the reply.
Policy (refund_policy.txt): completed orders only; delivered > 45 min -> full refund; <= INR 1000 auto, above -> human lead."""
import re, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"part_c"))
from llm import llm
DB = ROOT/"part_a/data/instamart.db"
MAX_STEPS, LATE_MIN, AUTO_LIMIT = 6, 45, 1000
ORDER = re.compile(r"ORD-\d+", re.I)

def lookup_order(oid):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM orders WHERE order_id=?", (oid,)).fetchone(); con.close()
    return dict(r) if r else None

def decide(order):
    if order["status"] != "completed": return "DENIED", 0.0, f"Order status is '{order['status']}', so there is nothing to refund."
    d = order["delivery_minutes"]
    if d is None or d != d: return "ESCALATE", 0.0, "Delivery time was not recorded, so a human must verify this order."
    if d <= LATE_MIN: return "DENIED", 0.0, f"Delivered in {int(d)} minutes, within the {LATE_MIN}-minute limit, so no late-delivery refund applies."
    amt = float(order["order_amount"])
    if amt <= AUTO_LIMIT: return "REFUND", round(amt, 2), f"Delivered in {int(d)} minutes (over {LATE_MIN}); full refund of INR {amt:.2f} auto-approved."
    return "ESCALATE", amt, f"Delivered in {int(d)} minutes (over {LATE_MIN}) but INR {amt:.2f} exceeds INR {AUTO_LIMIT}; a human support lead must approve."

def run_agent(message, customer_id=None, order_ids=()):
    """Tool loop: extract_order -> lookup_order -> decide. Stops at a decision or after MAX_STEPS (then FALLBACK to a human)."""
    trace, st = [], {}
    while len(trace) < MAX_STEPS:
        if "order_id" not in st:
            ids = list(order_ids) or [m.upper() for m in ORDER.findall(message)]
            st["order_id"] = ids[0] if ids else None; trace.append(f"extract_order -> {st['order_id']}")
            if not st["order_id"]: return _out("NEEDS_INFO", 0, "Please share the order ID (like ORD-100123) to check your refund.", trace)
        elif "[LOOP]" in message or "order" not in st:      # [LOOP]: simulated planner that keeps re-calling the same tool
            o = lookup_order(st["order_id"]); trace.append(f"lookup_order -> {'found' if o else 'none'}")
            if "[LOOP]" not in message:
                if not o or (customer_id and o["customer_id"] != customer_id):   # same answer for missing or someone else's order
                    return _out("NOT_FOUND", 0, "I couldn't find that order on your account.", trace)
                st["order"] = o
        else:
            oc, amt, why = decide(st["order"]); trace.append(f"decide -> {oc}")
            return _out(oc, amt, why, trace)
    summary = f"Agent hit the {MAX_STEPS}-step limit on order {st.get('order_id')} for customer {customer_id}; handing over to a human agent."
    return _out("FALLBACK", 0, summary, trace)

def _out(outcome, amount, reason, trace):
    reply = llm(f"Write a short, polite 2-sentence support reply. Do not change this decision: outcome={outcome}, refund_inr={amount}. Reason: {reason}", reason)
    return {"outcome": outcome, "refund_inr": amount, "reason": reason, "answer": reply, "trace": trace}
