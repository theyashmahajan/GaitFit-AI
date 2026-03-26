import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import CaptureGuide from "../components/CaptureGuide";
import LanguageToggle from "../components/LanguageToggle";
import SiteFooter from "../components/SiteFooter";
import VideoUploader from "../components/VideoUploader";
import { uploadVideo } from "../api/gaitfit";
import { content } from "./content";

function UploadPage() {
  const navigate = useNavigate();
  const [lang, setLang] = useState(localStorage.getItem("lang") || "en");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showGuide, setShowGuide] = useState(true);
  useEffect(() => localStorage.setItem("lang", lang), [lang]);
  const t = useMemo(() => content[lang], [lang]);

  const handleFile = async (nextFile) => {
    if (!nextFile) return;
    setError("");
    const maxSize = 50 * 1024 * 1024;
    if (nextFile.size > maxSize) {
      setError("File exceeds 50MB limit.");
      return;
    }
    const isVideo = nextFile.type.startsWith("video/") || /\.(mp4|mov|m4v)$/i.test(nextFile.name);
    if (isVideo) {
      const duration = await readVideoDuration(nextFile).catch(() => null);
      if (duration == null) {
        setError("Could not read video metadata.");
        return;
      }
      if (duration < 3 || duration > 10) {
        setError("Video duration must be between 3 and 10 seconds.");
        return;
      }
    }
    setFile(nextFile);
  };

  const submit = async () => {
    if (!file) return;
    setError("");
    setBusy(true);
    try {
      const { job_id } = await uploadVideo(file);
      navigate(`/analysis/${job_id}`);
    } catch (e) {
      setError(e.message || "Upload failed");
      setBusy(false);
    }
  };

  return (
    <main className="page">
      <LanguageToggle lang={lang} setLang={setLang} />
      <button className="mini-cta" onClick={() => setShowGuide(true)}>{t.captureGuideTitle || "Capture Guide"}</button>
      <h1>{t.uploadTitle}</h1>
      <p className="muted">{t.uploadHint}</p>
      <VideoUploader onFileSelect={handleFile} text={t} />
      {file && <p className="muted">{file.name}</p>}
      {error && <p className="error">{error}</p>}
      <button className="cta" onClick={submit} disabled={!file || busy}>
        {busy ? t.working : t.analyze}
      </button>
      <CaptureGuide text={t} open={showGuide} onClose={() => setShowGuide(false)} />
      <SiteFooter text={t} />
    </main>
  );
}

function readVideoDuration(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.preload = "metadata";
    video.onloadedmetadata = () => {
      const d = video.duration;
      URL.revokeObjectURL(url);
      resolve(d);
    };
    video.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("metadata error"));
    };
    video.src = url;
  });
}

export default UploadPage;
