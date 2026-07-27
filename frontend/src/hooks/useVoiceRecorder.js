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
export function useVoiceRecorder({ onSpeechEnd, onError } = {}) {
  const vadRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeechDetected, setIsSpeechDetected] = useState(false);
  const [error, setError] = useState(null);

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
          onSpeechStart: () => setIsSpeechDetected(true),
          onSpeechEnd: (audioFloat32) => {
            setIsSpeechDetected(false);
            const wavBuffer = utils.encodeWAV(audioFloat32);
            const blob = new Blob([wavBuffer], { type: "audio/wav" });
            onSpeechEnd?.(blob);
          },
          onVADMisfire: () => setIsSpeechDetected(false),
        });
      }
      vadRef.current.start();
      setIsListening(true);
    } catch (err) {
      setError(err.message || "Microphone access failed");
      onError?.(err);
    }
  }, [onSpeechEnd, onError]);

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
