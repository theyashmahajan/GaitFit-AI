function LanguageToggle({ lang, setLang }) {
  return (
    <div className="lang-toggle">
      <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>
        EN
      </button>
      <button className={lang === "hi" ? "active" : ""} onClick={() => setLang("hi")}>
        हिंदी
      </button>
    </div>
  );
}

export default LanguageToggle;

