import { useMemo, useState } from "react";
import { categoryTraits } from "../pages/category_traits";

function CategoryCompare({ recommendations = [], text }) {
  const top = recommendations.slice(0, 3);
  const [left, setLeft] = useState(top[0]?.shoe_type || "");
  const [right, setRight] = useState(top[1]?.shoe_type || top[0]?.shoe_type || "");
  const recMap = useMemo(() => Object.fromEntries(top.map((r) => [r.shoe_type, r])), [top]);
  if (top.length < 2) return null;

  return (
    <section className="panel">
      <h2>{text.compareTitle || "Recommendation Comparison"}</h2>
      <div className="compare-picks">
        <select value={left} onChange={(e) => setLeft(e.target.value)}>
          {top.map((r) => <option key={r.shoe_type} value={r.shoe_type}>{text[r.shoe_type] || r.shoe_type}</option>)}
        </select>
        <select value={right} onChange={(e) => setRight(e.target.value)}>
          {top.map((r) => <option key={r.shoe_type} value={r.shoe_type}>{text[r.shoe_type] || r.shoe_type}</option>)}
        </select>
      </div>
      <div className="compare-grid">
        <CompareCol item={recMap[left]} title={text[left] || left} best={top[0]?.shoe_type === left} />
        <CompareCol item={recMap[right]} title={text[right] || right} best={top[0]?.shoe_type === right} />
      </div>
    </section>
  );
}

function CompareCol({ item, title, best }) {
  if (!item) return null;
  const traits = categoryTraits[item.shoe_type] || { benefits: [], tradeoff: "" };
  return (
    <article className="compare-col">
      <div className="compare-head">
        <strong>{title}</strong>
        {best && <span className="badge">Best for your gait</span>}
      </div>
      <div className="confidence-track">
        <div className="confidence-fill" style={{ width: `${Math.round(item.match_score * 100)}%` }} />
      </div>
      <p className="muted">{Math.round(item.match_score * 100)}% match</p>
      <ul className="compare-benefits">
        {traits.benefits.map((b) => <li key={b}>{b}</li>)}
      </ul>
      <p className="muted"><strong>Trade-off:</strong> {traits.tradeoff}</p>
    </article>
  );
}

export default CategoryCompare;
