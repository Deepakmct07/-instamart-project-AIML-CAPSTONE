import { useState, useRef, useEffect } from "react";
const API = import.meta.env.VITE_API_URL || "https://instamart-capstone-project-aiml.onrender.com";
const COLORS = { REFUND: "#1a9a4a", ESCALATE: "#d68910", DENIED: "#c0392b", NOT_FOUND: "#7f8c8d", FALLBACK: "#8e44ad", NEEDS_INFO: "#2980b9" };
const EXAMPLES = ["What is the delivery fee on small orders?", "Who must approve a refund above INR 1000?", "Someone hacked my account", "I want a refund for order ORD-100001"];
export default function App() {
  const [msgs, setMsgs] = useState([{ role: "bot", text: "Hi! I can answer policy questions and check refund requests. Enter your customer ID (e.g. C0001) for refunds." }]);
  const [input, setInput] = useState(""); const [loading, setLoading] = useState(false);
  const [cid, setCid] = useState(""); const [seg, setSeg] = useState(null); const end = useRef();
   useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);
     async function lookup() {
    if (!cid.trim()) return setSeg(null);
    try { setSeg(await (await fetch(`${API}/customer/${cid.trim()}`)).json()); } catch { setSeg({ segment: "Server unreachable" }); }
  }
  async function send(text = input) {
    text = text.trim(); if (!text) return;
    setMsgs(m => [...m, { role: "user", text }]); setInput(""); setLoading(true);
    try {
      const r = await (await fetch(`${API}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: text, customer_id: cid.trim() || null }) })).json();
      setMsgs(m => [...m, { role: "bot", text: r.answer, decision: r.decision, blocked: r.blocked, sources: r.sources, trace: r.trace, intent: r.intent }]);
    } catch { setMsgs(m => [...m, { role: "bot", text: "Server unreachable. On a free tier it may need ~1 minute to wake up; retry shortly." }]); }
    setLoading(false);
  }
  return (
    <div className="app">
      <aside>
        <h2>Customer</h2>
        <input placeholder="Customer ID, e.g. C0001" value={cid} onChange={e => setCid(e.target.value)} onBlur={lookup} />
        {seg && <div className="card"><b>{seg.segment}</b>{seg.frequency != null && <small>Last order {seg.recency} days ago · {seg.frequency} orders · INR {seg.monetary}</small>}</div>}
        <p className="hint">Segment comes from the K-Means model (Part B).</p>
        <h3>Try</h3>{EXAMPLES.map(e => <button key={e} className="ex" onClick={() => send(e)}>{e}</button>)}
      </aside>
      <main>
        <header>Instamart Support Co-pilot</header>
        <div className="chat">
          {msgs.map((m, i) => (
            <div key={i} className={`msg ${m.role} ${m.blocked ? "blocked" : ""}`}>
              <p>{m.text}</p>
              {m.decision && <span className="badge" style={{ background: COLORS[m.decision.outcome] || "#555" }}>{m.decision.outcome}{m.decision.refund_inr > 0 ? ` · INR ${m.decision.refund_inr}` : ""}</span>}
              {m.trace && <small className="trace">Agent steps: {m.trace.join(" → ")}</small>}
              {m.sources?.length > 0 && <details><summary>Sources ({m.sources.length})</summary>{m.sources.map((s, j) => <div key={j} className="src"><b>{s.doc}</b> ({s.score}) {s.text}</div>)}</details>}
            </div>))}
          {loading && <div className="msg bot"><p>Thinking…</p></div>}<div ref={end} />
        </div>
        <div className="input"><input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} placeholder="Type your question…" /><button onClick={() => send()} disabled={loading}>Send</button></div>
      </main>
    </div>);
}
