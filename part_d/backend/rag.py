"""RAG: chunk policy documents, TF-IDF retrieval, grounded answer (Gemini if key set, else extractive)."""
import re, sys
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT/"part_c"))
from llm import llm
POLICY_DIR = ROOT/"part_a/data/policies"
MIN_SCORE = 0.12            # below this the question is treated as out-of-scope (no hallucinated answer)

def chunk_policies(window=2):
    """Sentence-window chunking: 2 sentences per chunk, stride 1 (overlap keeps facts together). Each chunk keeps its source doc."""
    chunks = []
    for f in sorted(POLICY_DIR.glob("*.txt")):
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", f.read_text().strip()) if s.strip()]
        for i in range(0, max(1, len(sents) - window + 1)):
            chunks.append({"doc": f.name, "text": " ".join(sents[i:i + window])})
    return chunks
CHUNKS = chunk_policies()
VEC = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True).fit([c["text"] for c in CHUNKS])
MAT = VEC.transform([c["text"] for c in CHUNKS])

def retrieve(q, k=3):
    s = cosine_similarity(VEC.transform([q]), MAT)[0]
    return [{**CHUNKS[i], "score": round(float(s[i]), 3)} for i in s.argsort()[::-1][:k]]

def answer(q, k=3):
    hits = retrieve(q, k)
    if not hits or hits[0]["score"] < MIN_SCORE:
        return {"answer": "I don't have information about that in our policies.", "sources": [], "grounded": False}
    ctx = "\n".join(f"[{h['doc']}] {h['text']}" for h in hits)
    ans = llm(f"Answer the question using ONLY the context. If it is not covered, say you don't know.\nContext:\n{ctx}\nQuestion: {q}", hits[0]["text"])
    return {"answer": ans, "sources": hits, "grounded": True}
