import { useEffect, useRef } from "react";
import Waveform from "./Waveform";
import Transcript from "./Transcript";
import TalkingFace from "./TalkingFace";

const STATUS_LABEL = {
  idle: "Idle",
  listening: "Listening",
  thinking: "Thinking",
  speaking: "Speaking",
};

export default function ConversationCard({
  history,
  isListening,
  micBars,
  isSpeaking,
  ttsBars,
  ttsLevel,
  progress,
  onSeek,
  onReplay,
  status,
}) {
  const hasContent = history.length > 0 || isListening;
  const bodyRef = useRef(null);

  useEffect(() => {
    const el = bodyRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [history.length, isListening]);

  return (
    <div className="conversation-card">
      <div className="conversation-card__header">
        <span className="conversation-card__title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 5h16M4 12h10M4 19h13" strokeLinecap="round" />
          </svg>
          Conversation
        </span>
        <span className={`status-pill status-pill--${status}`}>
          <span className="status-pill__dot" />
          {STATUS_LABEL[status] || "Idle"}
        </span>
      </div>

      <div className="conversation-card__body" ref={bodyRef}>
        {!hasContent && (
          <div className="conversation-card__empty">
            Press the mic and ask a question — or switch to typing below.
          </div>
        )}

        {history.map((item, i) => {
          const isLastAssistant = i === history.length - 1;
          return (
            <div className="message-group" id={`msg-${item.id}`} key={item.id}>
              <div className="message message--user">
                <div className="message__avatar message__avatar--user">You</div>
                <div className="message__bubble">
                  <div className="message__meta">
                    <span>You</span>
                  </div>
                  <div className="message__text">{item.query}</div>
                </div>
              </div>

              <div className="message message--assistant">
                <div className="message__avatar">
                  <TalkingFace
                    size="sm"
                    isSpeaking={isLastAssistant && isSpeaking}
                    level={isLastAssistant ? ttsLevel : 0}
                  />
                </div>
                <div className="message__bubble">
                  <div className="message__meta">
                    <span>Assistant</span>
                    <div className="message__actions">
                      <button
                        type="button"
                        className="message__icon-btn"
                        onClick={() => onReplay(item)}
                        title="Replay answer"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M5 12a7 7 0 1 1 2 5" strokeLinecap="round" />
                          <path d="M5 12V7M5 12h5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        className="message__icon-btn"
                        onClick={() => navigator.clipboard?.writeText(item.answer)}
                        title="Copy answer"
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="11" height="11" rx="2" />
                          <path d="M5 15V5a2 2 0 0 1 2-2h10" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  {isLastAssistant && isSpeaking ? (
                    <>
                      <Waveform bars={ttsBars} className="waveform--assistant" />
                      <Transcript text={item.answer} progress={progress} onSeek={onSeek} />
                    </>
                  ) : (
                    <div className="message__text">{item.answer}</div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {isListening && (
          <div className="message message--user">
            <div className="message__avatar message__avatar--user">You</div>
            <div className="message__bubble">
              <div className="message__meta">
                <span>You</span>
                <span className="message__live">Speaking...</span>
              </div>
              <Waveform bars={micBars} className="waveform--user" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
