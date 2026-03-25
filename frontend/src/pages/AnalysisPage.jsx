import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fetchStatus } from "../api/gaitfit";
import ProgressStepper from "../components/ProgressStepper";
import SiteFooter from "../components/SiteFooter";
import { content } from "./content";

function AnalysisPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState({ progress: 0, message: "Queued" });
  const lang = localStorage.getItem("lang") || "en";
  const t = content[lang];

  useEffect(() => {
    let intervalId;
    const poll = async () => {
      try {
        const s = await fetchStatus(jobId);
        setStatus(s);
        if (s.status === "done") {
          clearInterval(intervalId);
          navigate(`/results/${jobId}`);
        }
        if (s.status === "failed") {
          clearInterval(intervalId);
        }
      } catch (_e) {
        clearInterval(intervalId);
      }
    };
    poll();
    intervalId = setInterval(poll, 1800);
    return () => clearInterval(intervalId);
  }, [jobId, navigate]);

  return (
    <main className="page">
      <ProgressStepper progress={status.progress || 0} message={status.message} text={t} />
      {status.status === "failed" && (
        <section className="panel fail-panel">
          <p className="error">{status.error || t.failedProcess}</p>
          <ul className="fail-list">
            <li>{t.failTip1}</li>
            <li>{t.failTip2}</li>
            <li>{t.failTip3}</li>
          </ul>
          <Link className="mini-cta" to="/upload">{t.retryUpload}</Link>
        </section>
      )}
      <SiteFooter text={t} />
    </main>
  );
}

export default AnalysisPage;
