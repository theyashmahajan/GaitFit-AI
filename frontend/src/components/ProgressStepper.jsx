function ProgressStepper({ progress, message, text }) {
  const steps = [
    { label: text.step1, gate: 25 },
    { label: text.step2, gate: 60 },
    { label: text.step3, gate: 85 }
  ];
  return (
    <div className="panel">
      <h2>{text.analyzing}</h2>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <p className="muted">{message || text.working}</p>
      <div className="steps">
        {steps.map((s) => (
          <div key={s.label} className={`step ${progress >= s.gate ? "done" : ""}`}>
            {s.label}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProgressStepper;

