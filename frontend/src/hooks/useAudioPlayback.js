import { useCallback, useEffect, useRef, useState } from "react";

const BAR_COUNT = 28;

function downsample(freqData, barCount) {
  const bars = new Array(barCount);
  const step = Math.floor(freqData.length / barCount) || 1;
  for (let i = 0; i < barCount; i++) {
    bars[i] = freqData[i * step] / 255;
  }
  return bars;
}

/**
 * Plays a Blob of audio through an <audio> element and exposes live
 * amplitude/per-bar frequency data (for the talking face, glow ring, and
 * waveform) plus playback progress (for word-by-word transcript
 * highlighting), all driven by the actual audio — not a fake animation.
 */
export function useAudioPlayback() {
  const audioRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const freqDataRef = useRef(null);
  const rafRef = useRef(null);
  const objectUrlRef = useRef(null);

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [level, setLevel] = useState(0); // 0..1 smoothed amplitude
  const [bars, setBars] = useState(() => new Array(BAR_COUNT).fill(0));
  const [progress, setProgress] = useState(0); // 0..1

  const ensureGraph = useCallback(() => {
    if (audioCtxRef.current) return;
    const audio = new Audio();
    audio.crossOrigin = "anonymous";
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    const source = ctx.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(ctx.destination);

    audioRef.current = audio;
    audioCtxRef.current = ctx;
    analyserRef.current = analyser;
    freqDataRef.current = new Uint8Array(analyser.frequencyBinCount);
  }, []);

  const tick = useCallback(() => {
    rafRef.current = requestAnimationFrame(tick);
    const audio = audioRef.current;
    const analyser = analyserRef.current;
    if (!audio || !analyser) return;

    if (audio.duration) {
      setProgress(audio.currentTime / audio.duration);
    }

    analyser.getByteFrequencyData(freqDataRef.current);
    const data = freqDataRef.current;
    let sum = 0;
    for (let i = 0; i < data.length; i++) sum += data[i];
    setLevel(sum / data.length / 255);
    setBars(downsample(data, BAR_COUNT));
  }, []);

  const play = useCallback(
    async (audioBlob) => {
      ensureGraph();
      const ctx = audioCtxRef.current;
      const audio = audioRef.current;
      if (ctx.state === "suspended") await ctx.resume();

      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
      const url = URL.createObjectURL(audioBlob);
      objectUrlRef.current = url;

      audio.src = url;
      audio.onplay = () => setIsSpeaking(true);
      audio.onended = () => {
        setIsSpeaking(false);
        setLevel(0);
        setBars(new Array(BAR_COUNT).fill(0));
        setProgress(1);
      };
      audio.onpause = () => setIsSpeaking(false);

      await audio.play();
      if (!rafRef.current) tick();
    },
    [ensureGraph, tick]
  );

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
  }, []);

  const replay = useCallback(async () => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = 0;
    await audio.play();
  }, []);

  const seekToFraction = useCallback((fraction) => {
    const audio = audioRef.current;
    if (audio && audio.duration) {
      audio.currentTime = fraction * audio.duration;
    }
  }, []);

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
      audioCtxRef.current?.close();
    };
  }, []);

  return { play, stop, replay, seekToFraction, isSpeaking, level, bars, progress };
}
