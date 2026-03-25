import { useEffect, useMemo, useState } from "react";

function VisualEvidence({ evidence, imageSrc, text, apiBase }) {
  const frames = useMemo(() => {
    if (!evidence) return [];
    const hero = {
      id: "hero",
      label: text.visualTitle,
      image_url: evidence.image_url,
      frame_index: evidence.frame_index,
      angles: evidence.angles,
      side: evidence.side,
      width: evidence.width,
      height: evidence.height
    };
    return [hero, ...(Array.isArray(evidence.key_frames) ? evidence.key_frames : [])];
  }, [evidence, text.visualTitle]);

  const [activeId, setActiveId] = useState("hero");
  useEffect(() => {
    setActiveId("hero");
  }, [evidence?.image_url]);

  if (!evidence || !imageSrc || frames.length === 0) return null;

  const active = frames.find((f) => f.id === activeId) || frames[0];
  const activeSrc = `${apiBase}${active.image_url}`;
  const ratioStyle = getRatioStyle(active.width, active.height);

  return (
    <section className="panel evidence-panel">
      <div className="evidence-head">
        <h2>{text.visualTitle}</h2>
        <div className="evidence-chips">
          <span>{text.frameLabel}: {active.frame_index}</span>
          <span>{text.sideLabel}: {active.side === "left" ? text.left : text.right}</span>
          <span>{text.kneeAngle}: {Math.round(active.angles?.knee_deg || 0)} deg</span>
          <span>{text.ankleAngle}: {Math.round(active.angles?.ankle_deg || 0)} deg</span>
        </div>
      </div>
      <div className="evidence-image-wrap" style={ratioStyle}>
        <img src={activeSrc} alt="Annotated gait frame with measured joints and angles" className="evidence-image" />
      </div>
      <div className="evidence-actions">
        <a href={activeSrc} download={`gaitfit_evidence_frame_${active.frame_index}.jpg`} className="mini-cta">
          {text.downloadEvidence}
        </a>
      </div>

      {frames.length > 1 && (
        <div className="key-frames">
          <h3>{text.keyFramesTitle}</h3>
          <p className="muted key-note">{text.clickToFocus}</p>
          <div className="key-grid">
            {frames.slice(1).map((k) => {
              const ksrc = `${apiBase}${k.image_url}`;
              const activeClass = activeId === k.id ? "active" : "";
              return (
                <article key={k.id} className={`key-card ${activeClass}`}>
                  <button className="key-select" onClick={() => setActiveId(k.id)}>
                    <div className="key-img-wrap" style={getRatioStyle(k.width, k.height)}>
                      <img src={ksrc} alt={`${k.label} evidence`} className="key-img" />
                    </div>
                  </button>
                  <div className="key-meta">
                    <strong>{k.label}</strong>
                    <span>{text.frameLabel}: {k.frame_index}</span>
                    <a href={ksrc} download={`gaitfit_${k.id}_frame_${k.frame_index}.jpg`} className="mini-cta">
                      {text.downloadEvidence}
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}

function getRatioStyle(width, height) {
  if (!width || !height) return {};
  return { aspectRatio: `${width} / ${height}` };
}

export default VisualEvidence;
