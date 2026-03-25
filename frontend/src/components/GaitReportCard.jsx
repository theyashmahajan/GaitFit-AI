function GaitReportCard({ profile, summary, text }) {
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
        <span>Symmetry: {symmetryPct}%</span>
      </div>
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

export default GaitReportCard;
