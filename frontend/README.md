# Voice AI — frontend

Vite + React (plain JS). Talks to the FastAPI backend's three endpoints
(`/api/get_context`, `/api/text_to_speech`, `/api/speech_to_text`).

## Where to make common changes

- **Default theme colors** → `src/theme.css` (CSS custom properties at the top).
- **Capability cards, greeting name, app name, voice options, theme swatches,
  history cap** → `src/config.js`. `VOICE_OPTIONS` must stay in sync with
  `models_list` in `tts.py` — these are real Deepgram Aura-2 voice ids, not
  decorative labels.
- **API calls** → `src/api.js` — the only file that talks to the backend.
- **Component styling** → `src/app.css`.
- **Individual pieces of UI** → `src/components/`: `Sidebar.jsx`, `Header.jsx`,
  `ConversationCard.jsx`, `VoiceComposer.jsx` (the Speak/Type toggle + mic),
  `VoicePanel.jsx` (voice + theme selection), `TalkingFace.jsx`,
  `Transcript.jsx`, `Waveform.jsx`, `CapabilityCards.jsx` — one file per concern.
- **Mic recording / VAD** → `src/hooks/useVoiceRecorder.js`.
- **Live mic input waveform** → `src/hooks/useMicLevel.js`.
- **Audio playback / amplitude analysis for the assistant's waveform** →
  `src/hooks/useAudioPlayback.js`.

## Running

```bash
npm install
npm run dev          # http://localhost:5173
```

Set `VITE_API_BASE_URL` in `.env` if the backend isn't at `http://localhost:8000`.

## Known dev-server quirk: voice input needs a production build

The mic button uses Silero VAD (`@ricky0123/vad-web`, ONNX via WASM) to
auto-detect when you start/stop speaking. Its model/runtime files live in
`public/vad/` (copied from `@ricky0123/vad-web` and `onnxruntime-web` — see
below if you ever need to re-copy them after an `npm update`).

**Vite's dev server (`npm run dev`) cannot serve these correctly** — it
blocks any file under `public/` from being loaded via a JS `import()`, and
onnxruntime-web's threaded WASM backend does exactly that internally. You'll
see a console error like:

```
Encountered an error while loading model file /vad/silero_vad_legacy.onnx
```

This is a Vite dev-server-only limitation. It does **not** affect the actual
production build — `npm run build && npm run preview`, or the Docker/nginx
deployment, serve these files as plain static assets and work correctly.
Typing questions works fine under `npm run dev`; to test the mic/VAD, use:

```bash
npm run build && npm run preview   # http://localhost:4173
```

### Re-copying VAD assets (only needed after upgrading the vad-web/onnxruntime-web packages)

```bash
cp node_modules/@ricky0123/vad-web/dist/silero_vad_v5.onnx public/vad/
cp node_modules/@ricky0123/vad-web/dist/silero_vad_legacy.onnx public/vad/
cp node_modules/@ricky0123/vad-web/dist/vad.worklet.bundle.min.js public/vad/
cp node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.wasm public/vad/
cp node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.mjs public/vad/
cp node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.jsep.wasm public/vad/
cp node_modules/onnxruntime-web/dist/ort-wasm-simd-threaded.jsep.mjs public/vad/
```

## Known scope limit: chat history

The sidebar's "Today" list is in-memory for the current browser tab only —
there's no backend persistence for chat history across sessions/devices.
