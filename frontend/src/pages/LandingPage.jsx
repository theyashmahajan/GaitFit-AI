import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import LanguageToggle from "../components/LanguageToggle";
import SiteFooter from "../components/SiteFooter";
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
        <div className="topbar-actions">
          <a className="mini-cta ghost-mini" href="#science">{t.ourScience}</a>
          <Link className="mini-cta" to="/contact">{t.contactPage}</Link>
          <LanguageToggle lang={lang} setLang={setLang} />
        </div>
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
                <div className="pose-node n6" />
                <div className="pose-link l1" />
                <div className="pose-link l2" />
                <div className="pose-link l3" />
                <div className="pose-link l4" />
                <div className="pose-link l5" />
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
          <span className="science-badge">01</span>
          <h3>{t.computerVision}</h3>
          <p>{t.computerVisionDesc}</p>
        </article>
        <article className="science-card">
          <span className="science-badge">02</span>
          <h3>{t.biomechanics}</h3>
          <p>{t.biomechanicsDesc}</p>
        </article>
        <article className="science-card">
          <span className="science-badge">03</span>
          <h3>{t.correctiveEngine}</h3>
          <p>{t.correctiveEngineDesc}</p>
        </article>
      </section>

      <section className="how-it-works" id="process">
        <h2>{t.howItWorks}</h2>
        <div className="steps-row">
          <Step num="01" title={t.stepUpload} />
          <Step num="02" title={t.stepAnalyze} />
          <Step num="03" title={t.stepRecommend} />
        </div>
        <div className="process-actions">
          <Link to="/upload" className="cta">{t.testNow}</Link>
          <p className="muted">{t.tagline}</p>
        </div>
      </section>

      <section className="proof-showcase">
        <div className="proof-copy">
          <p className="hero-kicker">{t.visualTitle}</p>
          <h2>Evidence-First Output, Not Just Text</h2>
          <p className="muted">
            Key frames, angle overlays, and confidence-backed shoe categories make every result understandable and actionable.
          </p>
          <Link to="/upload" className="cta">Run My Scan</Link>
        </div>
        <div className="proof-grid">
          <FrameCard title="Heel Strike" angle="Ankle 51 deg" />
          <FrameCard title="Mid Stance" angle="Knee 167 deg" />
          <FrameCard title="Toe Off" angle="Ankle 43 deg" />
        </div>
      </section>
      <SiteFooter text={t} />
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

function FrameCard({ title, angle }) {
  return (
    <article className="frame-card">
      <div className="frame-image">
        <div className="frame-glow" />
        <div className="frame-joint f1" />
        <div className="frame-joint f2" />
        <div className="frame-joint f3" />
        <div className="frame-joint f4" />
        <div className="frame-line fl1" />
        <div className="frame-line fl2" />
        <div className="frame-line fl3" />
      </div>
      <div className="frame-meta">
        <strong>{title}</strong>
        <span>{angle}</span>
      </div>
    </article>
  );
}

export default LandingPage;
