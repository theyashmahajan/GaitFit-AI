import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { API_BASE, fetchResults, reportPdfUrl } from "../api/gaitfit";
import CTASection from "../components/CTASection";
import CategoryCompare from "../components/CategoryCompare";
import CaptureGuide from "../components/CaptureGuide";
import FindingCard from "../components/FindingCard";
import GaitReportCard from "../components/GaitReportCard";
import ShoeCard from "../components/ShoeCard";
import SiteFooter from "../components/SiteFooter";
import TrendDashboard from "../components/TrendDashboard";
import VisualEvidence from "../components/VisualEvidence";
import { findingsLibrary } from "./findings_library";
import { content } from "./content";

function ResultsPage() {
  const { jobId } = useParams();
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [showGuide, setShowGuide] = useState(false);
  const [error, setError] = useState("");
  const lang = localStorage.getItem("lang") || "en";
  const t = content[lang];
  const evidencePath = data?.evidence?.image_url || "";
  const evidenceSrc = evidencePath ? `${API_BASE}${evidencePath}` : "";

  useEffect(() => {
    fetchResults(jobId).then(setData).catch((e) => setError(e.message || "Failed to load result"));
  }, [jobId]);

  useEffect(() => {
    if (!data) return;
    const key = "gaitfit_scan_history";
    const raw = localStorage.getItem(key);
    const current = raw ? JSON.parse(raw) : [];
    const next = [...current.filter((item) => item.job_id !== data.job_id), { ...data, ts: Date.now() }];
    localStorage.setItem(key, JSON.stringify(next.slice(-15)));
    setHistory(next.slice(-15));
  }, [data]);

  useEffect(() => {
    const raw = localStorage.getItem("gaitfit_scan_history");
    setHistory(raw ? JSON.parse(raw) : []);
  }, []);

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
  const findings = buildFindings(data);

  return (
    <main className="page results">
      <VisualEvidence evidence={data.evidence} imageSrc={evidenceSrc} text={t} apiBase={API_BASE} />
      {data?.gait_profile?.input_mode === "photo" && (
        <section className="panel">
          <p className="muted">{t.photoModeNotice || "For best accuracy, upload a walking video."}</p>
        </section>
      )}
      <GaitReportCard
        profile={data.gait_profile}
        summary={data.summary}
        text={t}
        trend={data?.evidence?.quality_trend || []}
        sizeEstimate={data?.shoe_size_estimate || null}
      />
      {findings.length > 0 && (
        <section className="panel">
          <h2>{t.explainabilityTitle || "Why these findings matter"}</h2>
          <div className="finding-grid">
            {findings.map((f) => (
              <FindingCard key={f.key} title={f.title} finding={f.finding} />
            ))}
          </div>
        </section>
      )}
      <div className="action-row">
        <button className="mini-cta" onClick={downloadJsonReport}>
          {t.downloadJson}
        </button>
        <a href={reportPdfUrl(jobId)} className="mini-cta">
          {t.downloadPdf}
        </a>
      </div>
      <section className="panel">
        <h2 id="recommendations">{t.recs}</h2>
        <div className="cards">
          {data.recommendations.map((rec, idx) => (
            <ShoeCard key={rec.shoe_type} rec={rec} index={idx} text={t} />
          ))}
        </div>
      </section>
      <CategoryCompare recommendations={data.recommendations} text={t} />
      <TrendDashboard history={history} onSelect={setData} />
      <CTASection
        onRetake={() => (window.location.href = "/upload")}
        onGuide={() => setShowGuide(true)}
        onDownload={() => window.open(reportPdfUrl(jobId), "_blank")}
        onExplore={() => document.getElementById("recommendations")?.scrollIntoView({ behavior: "smooth" })}
      />
      <Link to="/upload" className="cta">
        {t.back}
      </Link>
      <CaptureGuide text={t} open={showGuide} onClose={() => setShowGuide(false)} />
      <SiteFooter text={t} />
    </main>
  );
}

function buildFindings(data) {
  const out = [];
  const p = data.gait_profile || {};
  if (p.pronation_type && p.pronation_type !== "neutral" && findingsLibrary[p.pronation_type]) {
    out.push({ key: p.pronation_type, title: p.pronation_type, finding: findingsLibrary[p.pronation_type] });
  }
  if (p.strike_pattern === "heel" && findingsLibrary.heel) {
    out.push({ key: "heel", title: "heel strike", finding: findingsLibrary.heel });
  }
  if (p.knee_alignment && p.knee_alignment !== "normal" && findingsLibrary[p.knee_alignment]) {
    out.push({ key: p.knee_alignment, title: p.knee_alignment, finding: findingsLibrary[p.knee_alignment] });
  }
  if ((p.asymmetry_score || 0) > 15 && findingsLibrary.asymmetry) {
    out.push({ key: "asymmetry", title: "asymmetry", finding: findingsLibrary.asymmetry });
  }
  return out;
}

export default ResultsPage;
