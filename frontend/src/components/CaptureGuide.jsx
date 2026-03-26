function CaptureGuide({ text, open, onClose }) {
  if (!open) return null;
  const checks = [
    text.captureTip1 || "Full body visible",
    text.captureTip2 || "Side view",
    text.captureTip3 || "Good lighting",
    text.captureTip4 || "Steady camera",
    text.captureTip5 || "Barefoot",
    text.captureTip6 || "Flat surface",
  ];

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <section className="guide-modal panel">
        <div className="guide-head">
          <h3>{text.captureGuideTitle || "Capture Guide"}</h3>
          <button type="button" className="mini-cta" onClick={onClose}>
            {text.close || "Close"}
          </button>
        </div>
        <div className="guide-diagram">
          <svg viewBox="0 0 320 160" className="guide-svg" aria-hidden="true">
            <rect x="12" y="16" width="296" height="128" rx="12" fill="rgba(3,7,18,0.8)" stroke="rgba(147,197,253,0.4)" />
            <line x1="24" y1="120" x2="300" y2="120" stroke="rgba(34,197,94,0.6)" strokeWidth="2" />
            <circle cx="96" cy="48" r="8" fill="#22c55e" />
            <line x1="96" y1="56" x2="96" y2="84" stroke="#60a5fa" strokeWidth="3" />
            <line x1="96" y1="84" x2="76" y2="108" stroke="#60a5fa" strokeWidth="3" />
            <line x1="96" y1="84" x2="112" y2="108" stroke="#60a5fa" strokeWidth="3" />
            <line x1="96" y1="66" x2="118" y2="76" stroke="#60a5fa" strokeWidth="3" />
            <rect x="220" y="68" width="56" height="40" rx="6" fill="rgba(37,99,235,0.32)" stroke="rgba(147,197,253,0.8)" />
            <text x="222" y="64" fill="#cbd5e1" fontSize="10">Camera @ knee height</text>
          </svg>
        </div>
        <ul className="guide-list">
          {checks.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default CaptureGuide;
