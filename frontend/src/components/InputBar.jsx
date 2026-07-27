import { useRef } from "react";

export default function InputBar({
  value,
  onChange,
  onSubmit,
  onMicClick,
  isListening,
  isSpeechDetected,
  disabled,
}) {
  const textareaRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="input-bar">
      <textarea
        ref={textareaRef}
        rows={1}
        placeholder={isListening ? "Listening..." : "Type or press the mic to speak..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button
        type="button"
        className={
          "input-bar__mic " +
          (isListening ? "is-listening " : "") +
          (isSpeechDetected ? "is-speech-detected" : "")
        }
        onClick={onMicClick}
        title={isListening ? "Stop listening" : "Speak your question"}
        aria-label="Toggle voice input"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="9" y="2" width="6" height="12" rx="3" />
          <path d="M5 11a7 7 0 0 0 14 0" strokeLinecap="round" />
          <path d="M12 18v3" strokeLinecap="round" />
        </svg>
      </button>
      <button
        type="button"
        className="input-bar__send"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        aria-label="Send"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M2 21l21-9L2 3v7l15 2-15 2v7z" />
        </svg>
      </button>
    </div>
  );
}
