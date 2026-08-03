// The only place in this app that talks to the backend. Base URL is
// configurable via VITE_API_BASE_URL (see .env / docker-compose build args).

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function readErrorDetail(res) {
  try {
    const body = await res.json();
    return body.detail || res.statusText;
  } catch {
    return res.statusText;
  }
}

// The backend now streams the answer as plain-text chunks as the model
// generates them (rather than one buffered JSON string), so the caller can
// render/speak-prep it incrementally. `onChunk(chunkText, fullTextSoFar)` is
// called as each piece arrives; the full answer is also the return value
// once the stream ends, for callers that just want the final text.
export async function getContext(query, onChunk) {
  const url = new URL(`${API_BASE_URL}/api/get_context`);
  url.searchParams.set("query", query);
  // GET can't carry a body in the Fetch API, so the query goes in the
  // query string; the backend also still accepts the original JSON-body form.
  const res = await fetch(url, { method: "GET" });
  if (!res.ok) {
    throw new Error(`get_context failed: ${await readErrorDetail(res)}`);
  }

  if (!res.body) {
    // Fallback for environments without a readable stream body.
    const text = await res.text();
    onChunk?.(text, text);
    return text;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let full = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    if (!chunk) continue;
    full += chunk;
    onChunk?.(chunk, full);
  }
  return full;
}

export async function textToSpeech(text, voice) {
  const url = new URL(`${API_BASE_URL}/api/text_to_speech`);
  if (voice) url.searchParams.set("model", voice);
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    throw new Error(`text_to_speech failed: ${await readErrorDetail(res)}`);
  }
  return res.blob();
}

export async function speechToText(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "clip.wav");
  const res = await fetch(`${API_BASE_URL}/api/speech_to_text`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(`speech_to_text failed: ${await readErrorDetail(res)}`);
  }
  return res.json();
}

export { API_BASE_URL };
