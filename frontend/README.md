# Voice AI — frontend

Vite + React (plain JS). Talks to the FastAPI backend's three endpoints
(`/api/get_context`, `/api/text_to_speech`, `/api/speech_to_text`).

## Where to make common changes

- **Colors / theme** → `src/theme.css` (CSS custom properties at the top).
- **Capability cards, greeting name, app name** → `src/config.js`.
- **API calls** → `src/api.js` — the only file that talks to the backend.
- **Component styling** → `src/app.css`.
- **Individual pieces of UI** → `src/components/`: `Sidebar.jsx`, `TopBar.jsx`,
  `TalkingFace.jsx`, `Transcript.jsx`, `InputBar.jsx`, `CapabilityCards.jsx` —
  one file per concern.
- **Mic recording / VAD** → `src/hooks/useVoiceRecorder.js`.
- **Audio playback / amplitude analysis for the face** → `src/hooks/useAudioPlayback.js`.

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
