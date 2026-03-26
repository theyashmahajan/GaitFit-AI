import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { API_BASE, fetchResults, reportPdfUrl } from "../api/gaitfit";
import GaitReportCard from "../components/GaitReportCard";
import ShoeCard from "../components/ShoeCard";
import SiteFooter from "../components/SiteFooter";
import VisualEvidence from "../components/VisualEvidence";
import { content } from "./content";

function ResultsPage() {
  const { jobId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const lang = localStorage.getItem("lang") || "en";
  const t = content[lang];
  const evidencePath = data?.evidence?.image_url || "";
  const evidenceSrc = evidencePath ? `${API_BASE}${evidencePath}` : "";

  useEffect(() => {
    fetchResults(jobId).then(setData).catch((e) => setError(e.message || "Failed to load result"));
  }, [jobId]);

  const downloadJsonReport = () => {
    if (!data) return;
    const payload = {
      exported_at: new Date().toISOString(),
      ...data
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gaitfit_report_${jobId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (error) return <main className="page"><p className="error">{error}</p></main>;
  if (!data) return <main className="page"><p className="muted">{t.working}</p></main>;

  return (
    <main className="page results">
      <VisualEvidence evidence={data.evidence} imageSrc={evidenceSrc} text={t} apiBase={API_BASE} />
      <GaitReportCard
        profile={data.gait_profile}
        summary={data.summary}
        text={t}
        trend={data?.evidence?.quality_trend || []}
        sizeEstimate={data?.shoe_size_estimate || null}
      />
      <div className="action-row">
        <button className="mini-cta" onClick={downloadJsonReport}>
          {t.downloadJson}
        </button>
        <a href={reportPdfUrl(jobId)} className="mini-cta">
          {t.downloadPdf}
        </a>
      </div>
      <section className="panel">
        <h2>{t.recs}</h2>
        <div className="cards">
          {data.recommendations.map((rec, idx) => (
            <ShoeCard key={rec.shoe_type} rec={rec} index={idx} text={t} />
          ))}
        </div>
      </section>
      <Link to="/upload" className="cta">
        {t.back}
      </Link>
      <SiteFooter text={t} />
    </main>
  );
}

export default ResultsPage;
