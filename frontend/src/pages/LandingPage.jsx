import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import LanguageToggle from "../components/LanguageToggle";
import { content } from "./content";

function LandingPage() {
  const [lang, setLang] = useState(localStorage.getItem("lang") || "en");
  useEffect(() => {
    localStorage.setItem("lang", lang);
  }, [lang]);
  const t = useMemo(() => content[lang], [lang]);

  return (
    <main className="page landing">
      <header className="topbar">
        <div className="brand-mark">
          <span className="brand-icon" />
          <strong>{t.logo}</strong>
        </div>
        <LanguageToggle lang={lang} setLang={setLang} />
      </header>

      <section className="landing-hero">
        <div className="hero-overlay" />
        <div className="hero-grid">
          <div className="hero-copy">
            <p className="hero-kicker">{t.landingKicker}</p>
            <h1>{t.landingTitle}</h1>
            <p className="tagline">{t.landingSub}</p>
            <div className="hero-actions">
              <Link to="/upload" className="cta">{t.testNow}</Link>
              <a href="#science" className="cta ghost-cta">{t.ourScience}</a>
            </div>
            <div className="hero-metrics">
              <Metric value="169 deg" label={t.knee} />
              <Metric value="50 deg" label={t.ankleAngle} />
              <Metric value="< 60 sec" label={t.scanTime} />
            </div>
          </div>

          <aside className="hero-visual">
            <div className="visual-screen">
              <div className="scan-head">{t.visualDemo}</div>
              <div className="scan-body">
                <div className="scan-line" />
                <div className="pose-node n1" />
                <div className="pose-node n2" />
                <div className="pose-node n3" />
                <div className="pose-node n4" />
                <div className="pose-node n5" />
                <div className="pose-link l1" />
                <div className="pose-link l2" />
                <div className="pose-link l3" />
                <div className="pose-link l4" />
              </div>
            </div>
            <div className="visual-points">
              <span>{t.visualPoint1}</span>
              <span>{t.visualPoint2}</span>
              <span>{t.visualPoint3}</span>
            </div>
          </aside>
        </div>
      </section>

      <section id="science" className="science-grid">
        <article className="science-card">
          <h3>{t.computerVision}</h3>
          <p>{t.computerVisionDesc}</p>
        </article>
        <article className="science-card">
          <h3>{t.biomechanics}</h3>
          <p>{t.biomechanicsDesc}</p>
        </article>
        <article className="science-card">
          <h3>{t.correctiveEngine}</h3>
          <p>{t.correctiveEngineDesc}</p>
        </article>
      </section>

      <section className="how-it-works">
        <h2>{t.howItWorks}</h2>
        <div className="steps-row">
          <Step num="01" title={t.stepUpload} />
          <Step num="02" title={t.stepAnalyze} />
          <Step num="03" title={t.stepRecommend} />
        </div>
        <Link to="/upload" className="cta">{t.testNow}</Link>
      </section>
    </main>
  );
}

function Metric({ value, label }) {
  return (
    <div className="hero-chip">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function Step({ num, title }) {
  return (
    <div className="step-card">
      <strong>{num}</strong>
      <p>{title}</p>
    </div>
  );
}

export default LandingPage;
