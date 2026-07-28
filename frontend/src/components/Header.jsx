import { GREETING_NAME, TAGLINE } from "../config";

export default function Header() {
  return (
    <header className="header">
      <div>
        <div className="header__eyebrow">Welcome back,</div>
        <h1 className="header__name">{GREETING_NAME}</h1>
        <p className="header__tagline">{TAGLINE}</p>
      </div>
      <div className="header__actions">
        <button className="header__icon-btn" type="button" aria-label="Notifications">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6" strokeLinejoin="round" />
            <path d="M10 20a2 2 0 0 0 4 0" strokeLinecap="round" />
          </svg>
        </button>
        <div className="header__avatar" aria-hidden="true" />
      </div>
    </header>
  );
}
