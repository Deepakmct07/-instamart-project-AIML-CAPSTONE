"""Part C: input validation + PII redaction. Rules run in the order R1 -> R2 -> R3."""
import re
from dataclasses import dataclass
try:                                                    # exact token count when the tokenizer is available
    import tiktoken; _enc = tiktoken.get_encoding("cl100k_base"); count_tokens = lambda t: len(_enc.encode(t))
except Exception:                                       # offline fallback: ~4 characters per token
    count_tokens = lambda t: len(t) // 4 + 1
MAX_TOKENS = 200                                        # normal tickets are ~30 tokens; the long ones ~600+
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
ORDER = re.compile(r"\bORD-\d{3,}\b", re.I)

@dataclass
class Result:
    status: str                 # "ok" | "blocked"
    reason: str
    cleaned_text: str = ""
    order_ids: tuple = ()       # extracted BEFORE redaction, kept server-side only (never put in prompts)
    pii_found: tuple = ()

def redact(text):
    ids, found = tuple(m.upper() for m in ORDER.findall(text)), []
    for name, pat, tag in [("email", EMAIL, "[EMAIL]"), ("phone", PHONE, "[PHONE]"), ("order_id", ORDER, "[ORDER_ID]")]:
        if pat.search(text): found.append(name)
        text = pat.sub(tag, text)
    return text, ids, tuple(found)

def validate_and_sanitize(text, max_tokens=MAX_TOKENS) -> Result:
    if text is None or not str(text).strip():                       # R1
        return Result("blocked", "empty_or_whitespace")
    text = str(text).strip()
    if count_tokens(text) > max_tokens:                             # R2
        return Result("blocked", "token_limit_exceeded")
    cleaned, ids, found = redact(text)                              # R3
    return Result("ok", "passed", cleaned, ids, found)
