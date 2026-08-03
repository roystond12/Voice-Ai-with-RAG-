import { useEffect, useState } from "react";

// Pulls a short topic phrase out of the question ("who is Michael Jackson"
// -> "Michael Jackson") so the thinking status feels specific rather than
// generic. Best-effort string heuristic — not real query understanding.
function extractTopic(query) {
  const stripped = query
    .replace(/^(who|what|when|where|why|how)\s+(is|are|was|were|did|do|does|can|could)\b\s*/i, "")
    .replace(/^(tell me about|explain|describe)\b\s*/i, "")
    .replace(/[?.!]+$/, "")
    .trim();
  return stripped || query;
}

export default function ThinkingIndicator({ query }) {
  const topic = extractTopic(query);
  const steps = [
    `Thinking about ${topic}...`,
    "Searching the knowledge base...",
    "Reading the relevant sections...",
    "Putting together an answer...",
  ];
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    setStepIndex(0);
    const interval = setInterval(() => {
      // Stop at the last step rather than looping — the moment real tokens
      // start streaming in, this component unmounts anyway.
      setStepIndex((i) => (i + 1 < steps.length ? i + 1 : i));
    }, 1400);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  return (
    <div className="thinking-indicator">
      <span className="thinking-indicator__text" key={stepIndex}>
        {steps[stepIndex]}
      </span>
      <span className="typing-dots" aria-label="Thinking">
        <span />
        <span />
        <span />
      </span>
    </div>
  );
}
