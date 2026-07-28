import { useEffect, useRef } from "react";

/**
 * The animated talking face — sits where the BuildHub screenshot has a
 * static swirl graphic. Mouth openness and ring glow are driven by real
 * playback amplitude (level), not a fake animation loop.
 */
export default function TalkingFace({ isSpeaking, level, size = "lg" }) {
  const mouthRef = useRef(null);

  useEffect(() => {
    if (!mouthRef.current) return;
    const openness = 4 + level * 26;
    mouthRef.current.setAttribute(
      "d",
      `M 32 65 Q 50 ${65 + openness} 68 65 Q 50 ${65 - openness * 0.4} 32 65 Z`
    );
  }, [level]);

  return (
    <div className={`talking-face talking-face--${size}`}>
      <div className={`talking-face__ring ${isSpeaking ? "is-speaking" : ""}`} />
      <div className={`talking-face__core ${isSpeaking ? "is-speaking" : ""}`}>
        <svg viewBox="0 0 100 100">
          <path className="talking-face__brow" d="M 26 32 Q 34 27 42 32" />
          <path className="talking-face__brow" d="M 58 32 Q 66 27 74 32" />
          <ellipse className="talking-face__eye" cx="34" cy="42" rx="4.5" ry="6" />
          <ellipse className="talking-face__eye talking-face__eye--right" cx="66" cy="42" rx="4.5" ry="6" />
          <path
            ref={mouthRef}
            className="talking-face__mouth"
            d="M 32 65 Q 50 65 68 65 Q 50 65 32 65 Z"
          />
        </svg>
      </div>
    </div>
  );
}
