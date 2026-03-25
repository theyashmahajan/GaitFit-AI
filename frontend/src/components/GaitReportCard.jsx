function GaitReportCard({ profile, summary, text, trend = [] }) {
  const confidencePct = Math.round((profile.confidence || 0) * 100);
  const symmetryPct = Math.round((profile.pelvic_symmetry || 0) * 100);
  return (
    <div className="panel">
      <h2>{text.gaitReport}</h2>
      <p className="insight">{profile.gait_insight}</p>
      <div className="confidence-strip">
        <div className="confidence-track">
          <div className="confidence-fill" style={{ width: `${confidencePct}%` }} />
        </div>
        <span>{text.confidence}: {confidencePct}%</span>
      </div>
      <div className="quick-stats">
        <span>{text.cadence}: {profile.cadence_spm} spm</span>
        <span>{text.symmetry}: {symmetryPct}%</span>
      </div>
      <QualityTrend trend={trend} text={text} />
      <div className="grid2">
        <Metric label={text.pronation} value={profile.pronation_type} />
        <Metric label={text.strike} value={profile.strike_pattern} />
        <Metric label={text.knee} value={profile.knee_alignment} />
        <Metric label={text.arch} value={profile.arch_type} />
        <Metric label={text.cadence} value={`${profile.cadence_spm} spm`} />
        <Metric label={text.confidence} value={`${confidencePct}%`} />
      </div>
      <p className="muted">{summary}</p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function QualityTrend({ trend, text }) {
  if (!Array.isArray(trend) || trend.length < 2) return null;
  const width = 320;
  const height = 88;
  const points = trend.map((p, idx) => {
    const x = (idx / Math.max(1, trend.length - 1)) * width;
    const y = height - (Math.max(0, Math.min(1, p.score || 0)) * height);
    return `${x},${y}`;
  });
  return (
    <div className="trend-wrap">
      <span className="muted">{text.trendTitle}</span>
      <svg viewBox={`0 0 ${width} ${height}`} className="trend-chart" preserveAspectRatio="none">
        <polyline fill="none" stroke="rgba(37,99,235,0.95)" strokeWidth="2.6" points={points.join(" ")} />
      </svg>
    </div>
  );
}

export default GaitReportCard;

