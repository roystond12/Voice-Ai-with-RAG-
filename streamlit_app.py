import json
import os
import uuid

import requests
import streamlit as st

RAG_API_URL = os.environ.get("RAG_API_URL", "http://127.0.0.1:8000/api/get_context")

st.set_page_config(page_title="Voice AI", page_icon="🎙️", layout="centered")

if "history" not in st.session_state:
    st.session_state.history = []       # list of {"role": "user"/"assistant", "text": str}
if "pending_answer" not in st.session_state:
    st.session_state.pending_answer = ""
if "speak_token" not in st.session_state:
    st.session_state.speak_token = ""   # changes only when a NEW answer needs to be spoken


def ask_rag(query: str) -> str:
    try:
        res = requests.get(RAG_API_URL, json={"query": query}, timeout=120)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return f"Sorry, I couldn't reach the RAG service. ({e})"


st.markdown(
    """
    <style>
      #MainMenu, footer, header {visibility: hidden;}
      .block-container{padding-top:2rem; padding-bottom:1rem; max-width:760px;}
      body{background:#0b0d12;}
      .app-title{
        text-align:center; color:#8b90a3; letter-spacing:.12em;
        text-transform:uppercase; font-size:.85rem; font-weight:600; margin-bottom:0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="app-title">🎙️ Voice AI Podcast</p>', unsafe_allow_html=True)


def render_face(answer_text: str, speak_token: str, should_speak: bool):
    payload = json.dumps(answer_text or "")
    token = json.dumps(speak_token)
    autospeak = "true" if should_speak else "false"

    html = f"""
<div id="root">
  <style>
    *{{box-sizing:border-box;}}
    #root {{
      font-family:"Segoe UI", Inter, system-ui, sans-serif;
      color:#eef0f6;
      display:flex; flex-direction:column; align-items:center; gap:18px;
      padding:6px 4px 2px;
    }}
    .face-wrap{{ position:relative; width:180px; height:180px; }}
    .face-ring{{
      position:absolute; inset:0; border-radius:50%;
      background:conic-gradient(from 0deg,#7c5cff,#ff8a5c,#7c5cff);
      opacity:.32; animation:spin 7s linear infinite; transition:opacity .3s ease;
    }}
    .face-ring.speaking{{ opacity:.9; }}
    @keyframes spin{{ to{{ transform:rotate(360deg); }} }}
    .face{{
      position:absolute; inset:9px; border-radius:50%;
      background:linear-gradient(160deg,#1d212e,#12151c 70%);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), 0 16px 40px rgba(0,0,0,.5);
      display:flex; align-items:center; justify-content:center;
      transition: box-shadow .25s ease;
    }}
    .face.speaking{{
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.08), 0 0 34px 4px rgba(124,92,255,.45), 0 16px 40px rgba(0,0,0,.5);
    }}
    .face svg{{ width:68%; height:68%; }}
    .eye{{ fill:#eef0f6; transform-origin:center; animation:blink 4.2s ease-in-out infinite; }}
    .eye.right{{ animation-delay:.15s; }}
    @keyframes blink{{ 0%,92%,100%{{transform:scaleY(1);}} 95%{{transform:scaleY(.08);}} }}
    #mouth{{ fill:#ff8a5c; transition:d .05s linear; }}
    #brow-l, #brow-r{{ stroke:#8b90a3; stroke-width:2.2; stroke-linecap:round; fill:none; }}

    .status{{ font-size:.8rem; color:#8b90a3; min-height:1.1em; text-align:center; }}

    .transcript{{
      width:100%; max-width:680px; max-height:220px; overflow-y:auto;
      text-align:center; padding:6px 8px 14px; font-size:1.05rem; line-height:1.9; font-weight:600;
      scrollbar-width:none;
    }}
    .transcript::-webkit-scrollbar{{ display:none; }}
    .word{{ color:#565c70; transition: color .15s ease; }}
    .word.said{{ color:#33e0b0; }}
    .word.active{{ color:#ffffff; }}

    .controls{{ display:flex; gap:10px; }}
    .btn{{
      border:1px solid #262b3a; background:#12151c; color:#eef0f6;
      border-radius:20px; padding:6px 16px; font-size:.8rem; cursor:pointer;
    }}
    .btn:hover{{ border-color:#7c5cff; }}
  </style>

  <div class="face-wrap">
    <div class="face-ring" id="ring"></div>
    <div class="face" id="face">
      <svg viewBox="0 0 100 100">
        <path id="brow-l" d="M 26 32 Q 34 27 42 32"></path>
        <path id="brow-r" d="M 58 32 Q 66 27 74 32"></path>
        <ellipse class="eye left" cx="34" cy="42" rx="4.5" ry="6"></ellipse>
        <ellipse class="eye right" cx="66" cy="42" rx="4.5" ry="6"></ellipse>
        <path id="mouth" d="M 32 65 Q 50 65 68 65 Q 50 65 32 65 Z"></path>
      </svg>
    </div>
  </div>

  <div class="status" id="status">Ask something below to start the podcast.</div>
  <div class="transcript" id="transcript"></div>
  <div class="controls">
    <button class="btn" id="replayBtn">Replay</button>
    <button class="btn" id="stopBtn">Stop</button>
  </div>
</div>

<script>
(function(){{
  const text = {payload};
  const token = {token};
  const autospeak = {autospeak};

  const face = document.getElementById('face');
  const ring = document.getElementById('ring');
  const mouth = document.getElementById('mouth');
  const statusEl = document.getElementById('status');
  const transcriptEl = document.getElementById('transcript');
  const replayBtn = document.getElementById('replayBtn');
  const stopBtn = document.getElementById('stopBtn');

  const words = text.split(/\\s+/).filter(Boolean);
  transcriptEl.innerHTML = words.map((w, i) => `<span class="word" data-i="${{i}}">${{w}}</span>`).join(' ');
  const wordEls = Array.from(transcriptEl.querySelectorAll('.word'));

  // map each word's character start offset in `text` for boundary matching
  let offsets = [];
  {{
    let cursor = 0;
    words.forEach(w => {{
      const idx = text.indexOf(w, cursor);
      offsets.push(idx >= 0 ? idx : cursor);
      cursor = (idx >= 0 ? idx : cursor) + w.length;
    }});
  }}

  let mouthTimer = null;

  function setSpeaking(on){{
    face.classList.toggle('speaking', on);
    ring.classList.toggle('speaking', on);
    if (on) {{
      mouthTimer = setInterval(() => {{
        const o = 4 + Math.random() * 22;
        mouth.setAttribute('d', `M 32 65 Q 50 ${{65 + o}} 68 65 Q 50 ${{65 - o * 0.4}} 32 65 Z`);
      }}, 110);
    }} else {{
      clearInterval(mouthTimer);
      mouth.setAttribute('d', 'M 32 65 Q 50 65 68 65 Q 50 65 32 65 Z');
    }}
  }}

  function highlightWord(charIndex){{
    let activeIdx = 0;
    for (let i = 0; i < offsets.length; i++) {{
      if (offsets[i] <= charIndex) activeIdx = i; else break;
    }}
    wordEls.forEach((el, i) => {{
      el.classList.toggle('said', i < activeIdx);
      el.classList.toggle('active', i === activeIdx);
    }});
    const activeEl = wordEls[activeIdx];
    if (activeEl) activeEl.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
  }}

  function markAllSaid(){{
    wordEls.forEach(el => {{ el.classList.remove('active'); el.classList.add('said'); }});
  }}

  function speak(){{
    if (!text || !window.speechSynthesis) {{
      statusEl.textContent = window.speechSynthesis ? 'Nothing to say yet.' : 'Speech synthesis not supported in this browser.';
      return;
    }}
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;
    utter.pitch = 1.0;

    utter.onstart = () => {{ setSpeaking(true); statusEl.textContent = 'Speaking...'; }};
    utter.onboundary = (e) => {{
      if (typeof e.charIndex === 'number') highlightWord(e.charIndex);
    }};
    utter.onend = () => {{ setSpeaking(false); markAllSaid(); statusEl.textContent = 'Done.'; }};
    utter.onerror = () => {{ setSpeaking(false); statusEl.textContent = 'Playback error.'; }};

    window.speechSynthesis.speak(utter);
  }}

  replayBtn.onclick = speak;
  stopBtn.onclick = () => {{
    window.speechSynthesis.cancel();
    setSpeaking(false);
    statusEl.textContent = 'Stopped.';
  }};

  if (autospeak && text) {{
    // small delay lets the browser voice list settle on first load
    setTimeout(speak, 150);
  }} else if (text) {{
    markAllSaid();
    statusEl.textContent = 'Ready. Hit replay to hear it again.';
  }}
}})();
</script>
"""
    st.components.v1.html(html, height=560, scrolling=False)


query = st.chat_input("Ask your question...")

should_speak = False
if query:
    st.session_state.history.append({"role": "user", "text": query})
    with st.spinner("Thinking..."):
        answer = ask_rag(query)
    st.session_state.history.append({"role": "assistant", "text": answer})
    st.session_state.pending_answer = answer
    st.session_state.speak_token = str(uuid.uuid4())
    should_speak = True

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

render_face(
    st.session_state.pending_answer,
    st.session_state.speak_token,
    should_speak=should_speak,
)
