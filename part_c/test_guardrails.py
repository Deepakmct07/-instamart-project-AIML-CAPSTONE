import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from guardrails import validate_and_sanitize as v
def test_empty(): assert v("   ").reason == "empty_or_whitespace" and v("").status == "blocked" and v(None).status == "blocked"
def test_long(): assert v("The same problem keeps happening. " * 80).reason == "token_limit_exceeded"
def test_pii():
    r = v("Refund ORD-100234, mail a.b@x.com, call 9876543210 or +91 9123456789")
    assert r.status == "ok" and r.order_ids == ("ORD-100234",) and set(r.pii_found) == {"email", "phone", "order_id"}
    assert "@" not in r.cleaned_text and "9876543210" not in r.cleaned_text and "ORD-1" not in r.cleaned_text
def test_clean_passthrough(): assert v("Where is my parcel?").cleaned_text == "Where is my parcel?"
def test_normal_ticket_not_blocked(): assert v("My order ORD-100001 has not arrived. Please call 9123456789.").status == "ok"
