"""Runs every ticket through guardrails, then classifies. Uses Gemini (few-shot) if GEMINI_API_KEY is set,
else an offline keyword baseline so the evaluation always runs. Run from anywhere."""
import re, sys
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from guardrails import validate_and_sanitize
from prompts import build_prompt, LABELS
from llm import llm
RULES = [("fraud", r"fraud|unauthori[sz]ed|hacked|never made|did not place"),
         ("technical", r"\bapp\b|crash|login|otp|error|freez"),
         ("billing", r"charged|invoice|\bbill|deducted|payment"),
         ("delivery", r"deliver|rider|late|arrive|package")]
def baseline(t):
    for lab, pat in RULES:
        if re.search(pat, t, re.I): return lab
    return "other"
def classify(cleaned):
    out = llm(build_prompt(cleaned, few_shot=True))
    if out:
        out = out.strip().lower().split()[0].strip(".,")
        if out in LABELS: return out, "llm_few_shot"
    return baseline(cleaned), "keyword_baseline"
if __name__ == "__main__":
    tk = pd.read_csv(HERE.parent/"part_a/data/raw/tickets.csv").fillna("")
    rows = []
    for r in tk.itertuples():
        g = validate_and_sanitize(r.text)
        if g.status == "blocked": rows.append((r.ticket_id, "blocked", g.reason, "", r.true_category, ""))
        else:
            lab, how = classify(g.cleaned_text); rows.append((r.ticket_id, "ok", ",".join(g.pii_found), lab, r.true_category, how))
    df = pd.DataFrame(rows, columns=["ticket_id", "status", "reason_or_pii", "predicted", "true_category", "method"])
    ok = df[df.status == "ok"]
    print("blocked:", df[df.status == "blocked"].reason_or_pii.value_counts().to_dict(), "| passed:", len(ok))
    print("method:", ok.method.value_counts().to_dict(), "| accuracy on passed tickets: %.3f" % (ok.predicted == ok.true_category).mean())
    print(pd.crosstab(ok.true_category, ok.predicted))
    df.to_csv(HERE/"outputs/guardrail_report.csv", index=False)
    leaked = [t for t in tk.text if (g := validate_and_sanitize(t)).status == "ok" and re.search(r"@|ORD-|(?<!\d)[6-9]\d{9}(?!\d)", g.cleaned_text)]
    print("PII leaks after redaction:", len(leaked)); assert not leaked
