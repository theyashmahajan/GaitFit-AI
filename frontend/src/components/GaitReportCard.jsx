function GaitReportCard({ profile, summary, text, trend = [], sizeEstimate = null }) {
  const confidencePct = Math.round((profile.confidence || 0) * 100);
  const symmetryPct = Math.round((profile.pelvic_symmetry || 0) * 100);
  const asymmetry = Math.round(profile.asymmetry_score || 0);
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
        <span>{text.asymmetry || "Asymmetry"}: {asymmetry}%</span>
      </div>
      <EstimatedShoeSize sizeEstimate={sizeEstimate} text={text} />
      <QualityTrend trend={trend} text={text} />
      <div className="grid2">
        <Metric label={text.pronation} value={profile.pronation_type} />
        <Metric label={text.strike} value={profile.strike_pattern} />
        <Metric label={text.knee} value={profile.knee_alignment} />
        <Metric label={text.arch} value={profile.arch_type} />
        <Metric label={text.cadence} value={`${profile.cadence_spm} spm`} />
        <Metric label={text.confidence} value={`${confidencePct}%`} />
        <Metric label={text.inputMode || "Input Mode"} value={profile.input_mode} />
        <Metric label={text.asymmetry || "Asymmetry"} value={`${asymmetry}%`} />
      </div>
      <p className="muted">{summary}</p>
    </div>
  );
}

function EstimatedShoeSize({ sizeEstimate, text }) {
  if (!sizeEstimate) return null;
  return (
    <div className="size-estimate">
      <h3>{text.estimatedShoeSize || "Estimated Shoe Size"}</h3>
      {sizeEstimate.estimated ? (
        <>
          <div className="quick-stats">
            <span>{text.footLength || "Foot Length"}: {sizeEstimate.foot_length_cm} cm</span>
            <span>UK: {sizeEstimate.uk_size}</span>
            <span>US(M): {sizeEstimate.us_men_size}</span>
            <span>US(W): {sizeEstimate.us_women_size}</span>
            <span>EU: {sizeEstimate.eu_size}</span>
            <span>{text.confidence}: {sizeEstimate.confidence}</span>
          </div>
          <p className="muted size-note">{sizeEstimate.disclaimer}</p>
        </>
      ) : (
        <p className="muted size-note">{sizeEstimate.message || (text.sizeUnavailable || "Size estimate unavailable.")}</p>
      )}
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
