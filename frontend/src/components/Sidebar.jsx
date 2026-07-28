import { useState } from "react";
import { APP_NAME } from "../config";

/**
 * Lists conversations (each a full back-and-forth session), not individual
 * questions — one "+ New conversation" starts a fresh thread; clicking a
 * past conversation switches back to it. Session-only (no backend
 * persistence across browser sessions yet).
 */
export default function Sidebar({ conversations, activeId, onSelect, onNewConversation }) {
  const [search, setSearch] = useState("");

  const ordered = [...conversations].reverse();
  const filtered = ordered.filter((c) => c.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__brand-mark">V</span>
        <div>
          <div className="sidebar__brand-name">{APP_NAME}</div>
          <div className="sidebar__brand-sub">Voice assistant</div>
        </div>
      </div>

      <button className="sidebar__new-btn" type="button" onClick={onNewConversation}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 5v14M5 12h14" strokeLinecap="round" />
        </svg>
        New conversation
      </button>

      <div className="sidebar__search">
        <input
          type="text"
          placeholder="Search conversations"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="sidebar__section-label">Conversations</div>
      <div className="sidebar__list">
        {filtered.length === 0 && (
          <div className="sidebar__empty">No conversations yet this session.</div>
        )}
        {filtered.map((c) => (
          <button
            key={c.id}
            className={`sidebar__item ${c.id === activeId ? "is-active" : ""}`}
            onClick={() => onSelect(c.id)}
            title={c.title}
          >
            {c.title}
          </button>
        ))}
      </div>
    </aside>
  );
}
