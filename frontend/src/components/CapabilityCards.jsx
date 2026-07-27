import { CAPABILITY_CARDS } from "../config";

const ICONS = {
  search: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" strokeLinecap="round" />
    </svg>
  ),
  layers: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3l9 5-9 5-9-5 9-5z" strokeLinejoin="round" />
      <path d="M3 13l9 5 9-5" strokeLinejoin="round" />
    </svg>
  ),
  calc: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <path d="M8 8h8M8 12h8M8 16h4" strokeLinecap="round" />
    </svg>
  ),
};

export default function CapabilityCards({ onPick }) {
  return (
    <div className="capability-cards">
      {CAPABILITY_CARDS.map((card) => (
        <button
          key={card.title}
          className="capability-card"
          onClick={() => onPick(card.prompt)}
        >
          <span className="capability-card__icon">{ICONS[card.icon]}</span>
          <span className="capability-card__title">{card.title}</span>
          <span className="capability-card__desc">{card.description}</span>
        </button>
      ))}
    </div>
  );
}
