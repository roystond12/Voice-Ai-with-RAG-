import { useEffect, useRef, useState } from "react";

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
 * Live microphone input level, for the "Speak" tab's waveform — separate
 * from @ricky0123/vad-web's internal stream/VAD logic, this just taps the
 * mic purely for visualization while `active` is true.
 */
export function useMicLevel(active) {
  const [bars, setBars] = useState(() => new Array(BAR_COUNT).fill(0));
  const streamRef = useRef(null);
  const ctxRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    if (!active) {
      setBars(new Array(BAR_COUNT).fill(0));
      return;
    }

    let cancelled = false;

    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;

        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        ctxRef.current = ctx;
        const source = ctx.createMediaStreamSource(stream);
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        const freqData = new Uint8Array(analyser.frequencyBinCount);

        const tick = () => {
          rafRef.current = requestAnimationFrame(tick);
          analyser.getByteFrequencyData(freqData);
          setBars(downsample(freqData, BAR_COUNT));
        };
        tick();
      } catch {
        // Mic access already requested/handled by the VAD flow; ignore
        // failures here since this hook is visualization-only.
      }
    })();

    return () => {
      cancelled = true;
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
      ctxRef.current?.close();
      streamRef.current = null;
      ctxRef.current = null;
    };
  }, [active]);

  return bars;
}
