import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { fetchStatus } from "../api/gaitfit";
import ProgressStepper from "../components/ProgressStepper";
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
      {status.status === "failed" && <p className="error">{status.error || "Failed to process video."}</p>}
    </main>
  );
}

export default AnalysisPage;

