import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import ConversationCard from "./components/ConversationCard";
import VoiceComposer from "./components/VoiceComposer";
import VoicePanel from "./components/VoicePanel";
import { useAudioPlayback } from "./hooks/useAudioPlayback";
import { useVoiceRecorder } from "./hooks/useVoiceRecorder";
import { useMicLevel } from "./hooks/useMicLevel";
import { getContext, textToSpeech, speechToText } from "./api";
import {
  DEFAULT_VOICE,
  DEFAULT_THEME,
  THEME_OPTIONS,
  MAX_HISTORY_ITEMS,
  NEW_CONVERSATION_TITLE,
} from "./config";
import "./theme.css";
import "./app.css";

function applyTheme(themeId) {
  const theme = THEME_OPTIONS.find((t) => t.id === themeId) || THEME_OPTIONS[0];
  const root = document.documentElement;
  root.style.setProperty("--accent", theme.accent);
  root.style.setProperty("--accent-bright", theme.accentBright);
  root.style.setProperty("--accent-dim", theme.accentDim);
}

function makeConversation() {
  return { id: crypto.randomUUID(), title: NEW_CONVERSATION_TITLE, messages: [] };
}

const STORAGE_KEY = "voiceai.conversations";

function loadStoredConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function App() {
  const [mode, setMode] = useState("speak"); // "speak" is the default input mode
  const [inputValue, setInputValue] = useState("");
  // Every turn of one ongoing session belongs to a single conversation; a new
  // one is only started explicitly (sidebar "+ New conversation" or a page
  // reload), not per-question. Past conversations persist across reloads.
  const [conversations, setConversations] = useState(loadStoredConversations);
  // Reloading the site always opens a fresh conversation — past ones stay
  // listed in the sidebar (loaded from storage above) and remain selectable.
  const [activeId, setActiveId] = useState(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
  }, [conversations]);
  const [voice, setVoice] = useState(DEFAULT_VOICE);
  const [theme, setTheme] = useState(DEFAULT_THEME);
  const [statusText, setStatusText] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => applyTheme(theme), [theme]);

  const activeConversation = conversations.find((c) => c.id === activeId) || null;
  const messages = activeConversation?.messages || [];

  const { play, stop, seekToFraction, isSpeaking, level, bars: ttsBars, progress } =
    useAudioPlayback();

  const ensureActiveConversation = () => {
    if (activeId && conversations.some((c) => c.id === activeId)) return activeId;
    const conv = makeConversation();
    setConversations((prev) => [...prev, conv].slice(-MAX_HISTORY_ITEMS));
    setActiveId(conv.id);
    return conv.id;
  };

  const startNewConversation = () => {
    stop(); // don't carry over audio from whatever conversation was active
    const conv = makeConversation();
    setConversations((prev) => [...prev, conv].slice(-MAX_HISTORY_ITEMS));
    setActiveId(conv.id);
    setInputValue("");
    setStatusText("");
  };

  const runQuery = async (query) => {
    if (!query.trim() || isBusy) return;
    const convId = ensureActiveConversation();
    setIsBusy(true);
    setInputValue("");
    setStatusText("Thinking...");
    try {
      const answer = await getContext(query.trim());
      const messageId = crypto.randomUUID();
      setConversations((prev) =>
        prev.map((c) =>
          c.id === convId
            ? {
                ...c,
                title: c.messages.length === 0 ? query.trim().slice(0, 48) : c.title,
                messages: [...c.messages, { id: messageId, query: query.trim(), answer }],
              }
            : c
        )
      );

      setStatusText("Speaking...");
      const audioBlob = await textToSpeech(answer, voice);
      await play(audioBlob);
      setStatusText("");
    } catch (err) {
      setStatusText(err.message || "Something went wrong.");
    } finally {
      setIsBusy(false);
    }
  };

  const {
    start: startListening,
    stop: stopListening,
    isListening,
    isSpeechDetected,
    error: micError,
  } = useVoiceRecorder({
    onSpeechEnd: async (audioBlob) => {
      stopListening();
      setStatusText("Transcribing...");
      try {
        const transcript = await speechToText(audioBlob);
        if (transcript && transcript.trim()) {
          await runQuery(transcript.trim());
        } else {
          setStatusText("Didn't catch that — try again.");
        }
      } catch (err) {
        setStatusText(err.message || "Transcription failed.");
      }
    },
    onError: (err) => setStatusText(err.message || "Microphone access failed."),
  });

  const micBars = useMicLevel(isListening);

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
      setStatusText("");
    } else {
      stop(); // don't let a still-playing answer overlap with a new recording
      setStatusText("Listening...");
      startListening();
    }
  };

  const handleReplay = async (item) => {
    setStatusText("Speaking...");
    try {
      const audioBlob = await textToSpeech(item.answer, voice);
      await play(audioBlob);
      setStatusText("");
    } catch (err) {
      setStatusText(err.message || "Couldn't replay that answer.");
    }
  };

  const handleSelectConversation = (id) => {
    if (id !== activeId) stop();
    setActiveId(id);
  };

  const status = isListening
    ? "listening"
    : isSpeaking
    ? "speaking"
    : isBusy
    ? "thinking"
    : "idle";

  return (
    <div className="layout">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelectConversation}
        onNewConversation={startNewConversation}
      />

      <main className="main-panel">
        <Header />

        <div className="main-panel__content">
          <ConversationCard
            history={messages}
            isListening={isListening}
            micBars={micBars}
            isSpeaking={isSpeaking}
            ttsBars={ttsBars}
            ttsLevel={level}
            progress={progress}
            onSeek={seekToFraction}
            onReplay={handleReplay}
            status={status}
          />

          <div className="status-line">{micError || statusText}</div>

          <VoiceComposer
            mode={mode}
            onModeChange={setMode}
            value={inputValue}
            onChange={setInputValue}
            onSubmit={() => runQuery(inputValue)}
            onMicClick={handleMicClick}
            isListening={isListening}
            isSpeechDetected={isSpeechDetected}
            micBars={micBars}
            disabled={isBusy}
          />
        </div>
      </main>

      <VoicePanel voice={voice} onVoiceChange={setVoice} theme={theme} onThemeChange={setTheme} />
    </div>
  );
}

export default App;
