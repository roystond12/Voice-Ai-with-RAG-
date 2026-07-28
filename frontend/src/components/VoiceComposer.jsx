import Waveform from "./Waveform";

export default function VoiceComposer({
  mode,
  onModeChange,
  value,
  onChange,
  onSubmit,
  onMicClick,
  isListening,
  isSpeechDetected,
  micBars,
  disabled,
}) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="composer">
      <button
        type="button"
        className="composer__switch"
        onClick={() => onModeChange(mode === "speak" ? "type" : "speak")}
      >
        {mode === "speak" ? (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 20l1.5-4.5L16 5l3 3-10.5 10.5L4 20z" strokeLinejoin="round" />
            </svg>
            Type instead
          </>
        ) : (
          <>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="2" width="6" height="12" rx="3" />
              <path d="M5 11a7 7 0 0 0 14 0" strokeLinecap="round" />
            </svg>
            Speak instead
          </>
        )}
      </button>

      {mode === "speak" ? (
        <div className="composer__speak">
          <Waveform bars={micBars.slice(0, 14)} className="waveform--side" />
          <button
            type="button"
            className={`composer__mic ${isListening ? "is-listening" : ""} ${
              isSpeechDetected ? "is-speech-detected" : ""
            }`}
            onClick={onMicClick}
            disabled={disabled}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="2" width="6" height="12" rx="3" />
              <path d="M5 11a7 7 0 0 0 14 0" strokeLinecap="round" />
              <path d="M12 18v3" strokeLinecap="round" />
            </svg>
          </button>
          <Waveform bars={micBars.slice(14)} className="waveform--side" />
        </div>
      ) : (
        <div className="composer__type">
          <textarea
            rows={1}
            placeholder="Type your question..."
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            autoFocus
          />
          <button
            type="button"
            className="composer__send"
            onClick={onSubmit}
            disabled={disabled || !value.trim()}
            aria-label="Send"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M2 21l21-9L2 3v7l15 2-15 2v7z" />
            </svg>
          </button>
        </div>
      )}

      <p className="composer__hint">
        {mode === "speak"
          ? isListening
            ? "Listening — pause speaking and it'll stop automatically."
            : "Tap to speak"
          : "Press Enter to send"}
      </p>
    </div>
  );
}
