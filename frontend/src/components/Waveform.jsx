/**
 * Renders a bar-per-value waveform from real amplitude data (mic input or
 * TTS playback) — no fake/random animation, bars are 0..1 values as measured.
 */
export default function Waveform({ bars, className = "" }) {
  return (
    <div className={`waveform ${className}`}>
      {bars.map((v, i) => (
        <span key={i} style={{ transform: `scaleY(${Math.max(0.06, v)})` }} />
      ))}
    </div>
  );
}
