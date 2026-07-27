import { useState } from "react";
import TopBar from "./components/TopBar";
import Sidebar from "./components/Sidebar";
import TalkingFace from "./components/TalkingFace";
import Transcript from "./components/Transcript";
import InputBar from "./components/InputBar";
import CapabilityCards from "./components/CapabilityCards";
import { useAudioPlayback } from "./hooks/useAudioPlayback";
import { useVoiceRecorder } from "./hooks/useVoiceRecorder";
import { getContext, textToSpeech, speechToText } from "./api";
import { GREETING_NAME } from "./config";
import "./theme.css";
import "./app.css";

function App() {
  const [inputValue, setInputValue] = useState("");
  const [history, setHistory] = useState([]); // [{ query, answer }]
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [status, setStatus] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  const { play, seekToFraction, isSpeaking, level, progress } = useAudioPlayback();

  const runQuery = async (query) => {
    if (!query.trim() || isBusy) return;
    setIsBusy(true);
    setInputValue("");
    setStatus("Thinking...");
    try {
      const answer = await getContext(query.trim());
      setCurrentAnswer(answer);
      setHistory((prev) => [...prev, { query: query.trim(), answer }]);

      setStatus("Speaking...");
      const audioBlob = await textToSpeech(answer);
      await play(audioBlob);
      setStatus("");
    } catch (err) {
      setStatus(err.message || "Something went wrong.");
    } finally {
      setIsBusy(false);
    }
  };

  const { start: startListening, stop: stopListening, isListening, isSpeechDetected } =
    useVoiceRecorder({
      onSpeechEnd: async (audioBlob) => {
        stopListening();
        setStatus("Transcribing...");
        try {
          const transcript = await speechToText(audioBlob);
          if (transcript && transcript.trim()) {
            setInputValue(transcript);
          } else {
            setStatus("Didn't catch that — try again.");
          }
        } catch (err) {
          setStatus(err.message || "Transcription failed.");
        } finally {
          if (status === "Transcribing...") setStatus("");
        }
      },
      onError: (err) => setStatus(err.message || "Microphone access failed."),
    });

  const handleMicClick = () => {
    if (isListening) {
      stopListening();
      setStatus("");
    } else {
      setStatus("Listening...");
      startListening();
    }
  };

  const handleSelectHistory = (index) => {
    const item = history[index];
    if (item) setCurrentAnswer(item.answer);
  };

  return (
    <div className="layout">
      <Sidebar history={history} onSelect={handleSelectHistory} />

      <main className="main-panel">
        <TopBar />

        <div className="main-panel__content">
          <TalkingFace isSpeaking={isSpeaking} level={level} />

          {!currentAnswer && (
            <>
              <h1 className="greeting">Welcome back, {GREETING_NAME}!</h1>
              <p className="greeting-subtitle">Ask a question, or press the mic to speak.</p>
            </>
          )}

          {currentAnswer && (
            <Transcript text={currentAnswer} progress={progress} onSeek={seekToFraction} />
          )}

          <div className="status-line">{status}</div>

          <InputBar
            value={inputValue}
            onChange={setInputValue}
            onSubmit={() => runQuery(inputValue)}
            onMicClick={handleMicClick}
            isListening={isListening}
            isSpeechDetected={isSpeechDetected}
            disabled={isBusy}
          />

          {!currentAnswer && (
            <CapabilityCards onPick={(prompt) => runQuery(prompt)} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
