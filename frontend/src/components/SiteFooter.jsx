import { Link } from "react-router-dom";

function SiteFooter({ text }) {
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <div className="footer-grid">
        <section>
          <h4>GaitFit AI</h4>
          <p className="muted">{text.footerTagline}</p>
        </section>
        <section>
          <h4>{text.contact}</h4>
          <a href="https://maps.google.com/?q=Bangalore" target="_blank" rel="noreferrer" className="icon-link">
            <MapPinIcon />
            <span>Bangalore, India</span>
          </a>
          <a href="mailto:gyash724@gmail.com" className="icon-link">
            <MailIcon />
            <span>gyash724@gmail.com</span>
          </a>
        </section>
        <section>
          <h4>{text.links}</h4>
          <a href="https://theyashmahajan.vercel.app/" target="_blank" rel="noreferrer" className="icon-link">
            <GlobeIcon />
            <span>Website</span>
          </a>
          <a href="https://github.com/theyashmahajan" target="_blank" rel="noreferrer" className="icon-link">
            <GitHubIcon />
            <span>GitHub</span>
          </a>
          <a href="https://www.linkedin.com/in/theyashmahajan/" target="_blank" rel="noreferrer" className="icon-link">
            <LinkedInIcon />
            <span>LinkedIn</span>
          </a>
          <Link to="/contact" className="icon-link">
            <InfoIcon />
            <span>{text.contactPage}</span>
          </Link>
        </section>
      </div>
      <div className="footer-bottom">
        <span>&copy; {year} GaitFit AI.</span>
      </div>
    </footer>
  );
}

function IconBase({ children }) {
  return (
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
      {children}
    </svg>
  );
}

function GlobeIcon() {
  return (
    <IconBase>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M3 12h18M12 3a15 15 0 0 0 0 18M12 3a15 15 0 0 1 0 18" fill="none" stroke="currentColor" strokeWidth="1.4" />
    </IconBase>
  );
}

function GitHubIcon() {
  return (
    <IconBase>
      <path d="M12 3a9 9 0 0 0-2.85 17.54c.45.08.62-.2.62-.45v-1.6c-2.52.54-3.05-1.08-3.05-1.08-.4-1.03-1-1.3-1-1.3-.8-.54.05-.53.05-.53.9.07 1.37.92 1.37.92.78 1.35 2.05.96 2.55.74.08-.58.3-.97.55-1.2-2.02-.22-4.15-1-4.15-4.52 0-.99.36-1.8.92-2.44-.1-.22-.4-1.15.1-2.39 0 0 .76-.24 2.48.92a8.4 8.4 0 0 1 4.52 0c1.7-1.16 2.47-.92 2.47-.92.5 1.24.2 2.17.1 2.39.57.64.92 1.45.92 2.44 0 3.52-2.13 4.29-4.16 4.52.32.27.6.8.6 1.62v2.4c0 .25.16.54.63.45A9 9 0 0 0 12 3Z" fill="currentColor" />
    </IconBase>
  );
}

function LinkedInIcon() {
  return (
    <IconBase>
      <rect x="4" y="4" width="16" height="16" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M8 10v6M8 8.2a.9.9 0 1 1 0 1.8.9.9 0 0 1 0-1.8ZM11.2 16v-3.2c0-1.7 2.6-1.8 2.6 0V16M11.2 12.8v-2.8h2.6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </IconBase>
  );
}

function MailIcon() {
  return (
    <IconBase>
      <rect x="3.5" y="6" width="17" height="12" rx="2" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="m4.5 7 7.5 6 7.5-6" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </IconBase>
  );
}

function MapPinIcon() {
  return (
    <IconBase>
      <path d="M12 21s-6-5.1-6-10a6 6 0 1 1 12 0c0 4.9-6 10-6 10Z" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="12" cy="11" r="2.2" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </IconBase>
  );
}

function InfoIcon() {
  return (
    <IconBase>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M12 10.2v5.3M12 7.8h.01" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </IconBase>
  );
}

export default SiteFooter;

