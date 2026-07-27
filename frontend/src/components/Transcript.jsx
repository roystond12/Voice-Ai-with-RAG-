import { useMemo, useRef, useEffect } from "react";

/**
 * Spotify-lyrics-style word highlighting, synced to real audio playback
 * position (progress, 0..1) rather than a fake timer.
 */
export default function Transcript({ text, progress, onSeek }) {
  const words = useMemo(() => (text ? text.split(/\s+/).filter(Boolean) : []), [text]);
  const activeIndex = Math.min(
    words.length - 1,
    Math.floor(progress * words.length)
  );
  const activeRef = useRef(null);

  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [activeIndex]);

  if (!words.length) {
    return <div className="transcript transcript--empty">Ask something to get started.</div>;
  }

  return (
    <div className="transcript">
      {words.map((word, i) => (
        <span
          key={i}
          ref={i === activeIndex ? activeRef : null}
          className={
            "transcript__word " +
            (i < activeIndex ? "is-said" : i === activeIndex ? "is-active" : "")
          }
          onClick={() => onSeek?.(i / words.length)}
        >
          {word}{" "}
        </span>
      ))}
    </div>
  );
}
