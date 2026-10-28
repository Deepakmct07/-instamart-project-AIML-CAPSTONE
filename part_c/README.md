# Part C: Guardrails & Input Validation
## What the code does
`guardrails.py` provides `validate_and_sanitize(text)`. Rules run in order:

| # | Rule | Action | Why |
|---|------|--------|-----|
| R1 | Empty / whitespace / None | Block `empty_or_whitespace` | No wasted model calls |
| R2 | More than 200 tokens (tiktoken `cl100k_base`; fallback ~4 chars per token if offline) | Block `token_limit_exceeded` | Cost and context control; normal tickets are ~30 tokens, planted long ones ~600 |
| R3a | Email | Replace with `[EMAIL]` | Privacy |
| R3b | Indian mobile (10 digits starting 6-9, optional +91) | Replace with `[PHONE]` | Privacy |
| R3c | Order ID `ORD-<digits>` | Replace with `[ORDER_ID]`; ID kept server-side only | The LLM never sees it; the backend can still look the order up |

`prompts.py` has **zero-shot** and **few-shot** classification prompts (billing, delivery, technical, fraud). `run_pipeline.py` sends every ticket through the guardrails, then classifies it with Gemini few-shot if `GEMINI_API_KEY` is set, otherwise with a keyword baseline so the evaluation always runs. `llm.py` is the shared LLM wrapper.
## Run
```bash
pip install pandas tiktoken httpx python-dotenv pytest
cd part_c && python run_pipeline.py && pytest
```
Optional environment variable: `GEMINI_API_KEY`.
## Key findings
- All 8 bad tickets were blocked (4 empty, 4 too long); 156 passed.
- 0 PII leaks after redaction (asserted in `run_pipeline.py`); `outputs/guardrail_report.csv` has per-ticket results.
- The keyword baseline scores 100% on passed tickets, but only because the synthetic tickets use a few templates; treat it as a sanity check, not a real accuracy claim. The few-shot LLM path is the one meant for real text.
- 5 unit tests pass.
