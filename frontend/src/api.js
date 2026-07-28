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

export async function getContext(query) {
  const url = new URL(`${API_BASE_URL}/api/get_context`);
  url.searchParams.set("query", query);
  // GET can't carry a body in the Fetch API, so the query goes in the
  // query string; the backend also still accepts the original JSON-body form.
  const res = await fetch(url, { method: "GET" });
  if (!res.ok) {
    throw new Error(`get_context failed: ${await readErrorDetail(res)}`);
  }
  return res.json();
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
