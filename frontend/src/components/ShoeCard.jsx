function ShoeCard({ rec, index, text }) {
  return (
    <div className="card">
      <div className="badge">#{index + 1}</div>
      <h3>{text[rec.shoe_type] || rec.shoe_type}</h3>
      <p className="muted">{rec.why_this_fits}</p>
      <div className="score">{Math.round(rec.match_score * 100)}% match</div>
    </div>
  );
}

export default ShoeCard;

