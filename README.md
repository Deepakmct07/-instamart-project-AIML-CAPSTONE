# Instamart Customer Intelligence Capstone
One repo, four folders, each with its own README.

| Folder | Topic |
|---|---|
| `part_a/` | Data preparation, EDA, SQLite |
| `part_b/` | RFM + K-Means customer segmentation |
| `part_c/` | Guardrails: validation, PII redaction, prompts |
| `part_d/` | RAG policy assistant, refund agent, React co-pilot |

Run order: A, B, C, D. Secrets live in `.env` (git-ignored); variable names are listed in `part_d/README.md`.
All data is synthetic, produced by the course-provided `part_a/generate_data.py`.
