import { useState } from "react";

/**
 * Session history grouped under "Today". There's no backend persistence for
 * chat history across sessions/devices — this is in-memory only for the
 * current tab (a known scope limit, not a bug).
 */
export default function Sidebar({ history, onSelect }) {
  const [search, setSearch] = useState("");

  const filtered = history.filter((item) =>
    item.query.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="sidebar">
      <div className="sidebar__search">
        <input
          type="text"
          placeholder="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filtered.length > 0 && (
        <>
          <div className="sidebar__section-label">Today</div>
          <div className="sidebar__list">
            {filtered.map((item, i) => (
              <button
                key={i}
                className="sidebar__item"
                onClick={() => onSelect(history.indexOf(item))}
                title={item.query}
              >
                {item.query}
              </button>
            ))}
          </div>
        </>
      )}
    </aside>
  );
}
