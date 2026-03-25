import SiteFooter from "../components/SiteFooter";
import { content } from "./content";

function ContactPage() {
  const lang = localStorage.getItem("lang") || "en";
  const t = content[lang];

  return (
    <main className="page">
      <section className="panel contact-panel">
        <h1>{t.contactPage}</h1>
        <p className="muted">{t.contactIntro}</p>
        <div className="contact-items">
          <div>
            <span>{t.address}</span>
            <strong>Bangalore, India</strong>
          </div>
          <div>
            <span>Email</span>
            <a href="mailto:gyash724@gmail.com">gyash724@gmail.com</a>
          </div>
          <div>
            <span>Website</span>
            <a href="https://theyashmahajan.vercel.app/" target="_blank" rel="noreferrer">
              theyashmahajan.vercel.app
            </a>
          </div>
          <div>
            <span>GitHub</span>
            <a href="https://github.com/theyashmahajan" target="_blank" rel="noreferrer">
              github.com/theyashmahajan
            </a>
          </div>
          <div>
            <span>LinkedIn</span>
            <a href="https://www.linkedin.com/in/theyashmahajan/" target="_blank" rel="noreferrer">
              linkedin.com/in/theyashmahajan
            </a>
          </div>
        </div>
      </section>
      <SiteFooter text={t} />
    </main>
  );
}

export default ContactPage;

