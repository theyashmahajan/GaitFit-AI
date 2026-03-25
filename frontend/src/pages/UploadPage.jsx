import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
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
  useEffect(() => localStorage.setItem("lang", lang), [lang]);
  const t = useMemo(() => content[lang], [lang]);

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
      <h1>{t.uploadTitle}</h1>
      <p className="muted">{t.uploadHint}</p>
      <VideoUploader onFileSelect={setFile} text={t} />
      {file && <p className="muted">{file.name}</p>}
      {error && <p className="error">{error}</p>}
      <button className="cta" onClick={submit} disabled={!file || busy}>
        {busy ? t.working : t.analyze}
      </button>
      <SiteFooter text={t} />
    </main>
  );
}

export default UploadPage;
