import { useCallback, useEffect, useRef, useState } from "react";
import { MicVAD, utils } from "@ricky0123/vad-web";

/**
 * Records a spoken question: requests the mic with browser-level noise
 * cancellation, runs Silero VAD (ONNX/WASM) to auto-detect speech start/end
 * so recording stops on its own after you stop talking, and hands back the
 * captured clip as a WAV Blob.
 *
 * Static VAD/ONNX assets are served from /vad (copied from
 * @ricky0123/vad-web + onnxruntime-web into frontend/public/vad — see
 * frontend/README.md).
 */
export function useVoiceRecorder({ onSpeechStart, onSpeechEnd, onError } = {}) {
  const vadRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechDetected, setIsSpeechDetected] = useState(false);
  const [error, setError] = useState(null);

  // MicVAD.new(...) only ever runs once (guarded below so we don't rebuild
  // the mic/model on every render). If its callbacks closed over onSpeechEnd
  // etc. directly, they'd stay frozen to whatever those props were on that
  // first call — e.g. always seeing the conversation state from mount, so
  // every voice turn looked like the start of a brand-new conversation.
  // Refs kept fresh on every render sidestep that.
  const onSpeechStartRef = useRef(onSpeechStart);
  const onSpeechEndRef = useRef(onSpeechEnd);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onSpeechStartRef.current = onSpeechStart;
    onSpeechEndRef.current = onSpeechEnd;
    onErrorRef.current = onError;
  }, [onSpeechStart, onSpeechEnd, onError]);

  const start = useCallback(async () => {
    setError(null);
    try {
      if (!vadRef.current) {
        vadRef.current = await MicVAD.new({
          baseAssetPath: "/vad/",
          onnxWASMBasePath: "/vad/",
          additionalAudioConstraints: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
          // Raised from the library defaults (0.3 / 0.25) — the mic listens
          // continuously (including while the bot's own audio is playing
          // through the speakers), so a lower bar was picking up background
          // noise / speaker bleed-through as speech and cutting the bot off.
          positiveSpeechThreshold: 0.6,
          negativeSpeechThreshold: 0.45,
          // React only once a stretch of audio has looked like real speech
          // for this long (vs. the instant, single-frame onSpeechStart),
          // so a brief noise blip can't trigger a false barge-in.
          minSpeechMs: 500,
          onSpeechRealStart: () => {
            setIsSpeechDetected(true);
            onSpeechStartRef.current?.();
          },
          onSpeechEnd: (audioFloat32) => {
            setIsSpeechDetected(false);
            const wavBuffer = utils.encodeWAV(audioFloat32);
            const blob = new Blob([wavBuffer], { type: "audio/wav" });
            onSpeechEndRef.current?.(blob);
          },
          onVADMisfire: () => setIsSpeechDetected(false),
        });
      }
      vadRef.current.start();
      setIsListening(true);
    } catch (err) {
      setError(err.message || "Microphone access failed");
      onErrorRef.current?.(err);
    }
  }, []);

  const stop = useCallback(() => {
    vadRef.current?.pause();
    setIsListening(false);
    setIsSpeechDetected(false);
  }, []);

  useEffect(() => {
    return () => {
      vadRef.current?.destroy();
    };
  }, []);

  return { start, stop, isListening, isSpeechDetected, error };
}
