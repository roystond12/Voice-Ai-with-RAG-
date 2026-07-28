import { VOICE_OPTIONS, THEME_OPTIONS } from "../config";

export default function VoicePanel({ voice, onVoiceChange, theme, onThemeChange }) {
  return (
    <aside className="voice-panel">
      <div className="voice-panel__section">
        <div className="voice-panel__label">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 14v-4a2 2 0 0 1 2-2h2l5-4v16l-5-4H6a2 2 0 0 1-2-2z" strokeLinejoin="round" />
          </svg>
          Voice settings
        </div>

        <label className="voice-panel__field">
          <span>Voice</span>
          <select value={voice} onChange={(e) => onVoiceChange(e.target.value)}>
            {VOICE_OPTIONS.map((v) => (
              <option key={v.id} value={v.id}>
                {v.label} — {v.tone}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="voice-panel__section">
        <div className="voice-panel__label">Theme</div>
        <div className="voice-panel__swatches">
          {THEME_OPTIONS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`swatch ${theme === t.id ? "is-active" : ""}`}
              style={{ background: t.accent }}
              onClick={() => onThemeChange(t.id)}
              title={t.label}
              aria-label={`Theme: ${t.label}`}
            >
              {theme === t.id && (
                <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
