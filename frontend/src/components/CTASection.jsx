function CTASection({ onRetake, onGuide, onDownload, onExplore }) {
  const items = [
    { key: "retake", label: "Retake Scan", sub: "Upload a new media file", fn: onRetake },
    { key: "guide", label: "Improve Capture", sub: "Open capture guide tips", fn: onGuide },
    { key: "download", label: "Download Full Report", sub: "Save PDF for sharing", fn: onDownload },
    { key: "explore", label: "Explore Recommendations", sub: "Jump to recommendation cards", fn: onExplore },
  ];
  return (
    <section className="panel">
      <h2>Next Actions</h2>
      <div className="cta-grid">
        {items.map((item) => (
          <button key={item.key} className="cta-tile" onClick={item.fn}>
            <strong>{item.label}</strong>
            <span>{item.sub}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

export default CTASection;
