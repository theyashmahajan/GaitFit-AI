function TrendDashboard({ history = [], onSelect }) {
  if (history.length < 2) return null;
  const conf = history.map((h) => ({ x: h.ts, y: h.gait_profile?.confidence || 0 }));
  const sym = history.map((h) => ({ x: h.ts, y: h.gait_profile?.pelvic_symmetry || 0 }));
  const cad = history.map((h) => ({ x: h.ts, y: (h.gait_profile?.cadence_spm || 0) / 220 }));

  return (
    <section className="panel">
      <h2>Trend Dashboard</h2>
      <div className="trend-grid">
        <MiniSpark title="Confidence" points={conf} />
        <MiniSpark title="Symmetry" points={sym} />
        <MiniSpark title="Cadence" points={cad} />
      </div>
      <div className="history-list">
        {history.slice().reverse().map((item) => (
          <button key={item.job_id} className="history-item" onClick={() => onSelect(item)}>
            <strong>{new Date(item.ts).toLocaleString()}</strong>
            <span>{item.gait_profile?.gait_insight || "Gait scan"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function MiniSpark({ title, points }) {
  const w = 240;
  const h = 72;
  const poly = points.map((p, i) => `${(i / Math.max(1, points.length - 1)) * w},${h - Math.max(0, Math.min(1, p.y)) * h}`);
  return (
    <article className="spark-card">
      <strong>{title}</strong>
      <svg viewBox={`0 0 ${w} ${h}`} className="trend-chart" preserveAspectRatio="none">
        <polyline fill="none" stroke="rgba(34,197,94,0.95)" strokeWidth="2.4" points={poly.join(" ")} />
      </svg>
    </article>
  );
}

export default TrendDashboard;
