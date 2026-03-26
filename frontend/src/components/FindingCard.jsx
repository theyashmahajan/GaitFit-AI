import { useState } from "react";

function FindingCard({ title, finding }) {
  const [open, setOpen] = useState(false);
  return (
    <article className={`finding-card ${open ? "open" : ""}`}>
      <button className="finding-toggle" onClick={() => setOpen((v) => !v)}>
        <strong>{title}</strong>
        <span>{open ? "Hide" : "Show"}</span>
      </button>
      {open && (
        <div className="finding-body">
          <p><strong>Detected:</strong> {finding.detected}</p>
          <p><strong>Why it matters:</strong> {finding.matters}</p>
          <p><strong>What to do:</strong> {finding.action}</p>
        </div>
      )}
    </article>
  );
}

export default FindingCard;
