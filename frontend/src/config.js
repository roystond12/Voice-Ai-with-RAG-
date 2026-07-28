// Copy, voice options, and theme presets — kept out of component code so
// they're easy to tweak without touching UI logic.

export const APP_NAME = "Voice AI";
export const TAGLINE = "Ask with your voice. Listen to the answer.";
export const GREETING_NAME = "there";

// Session-only conversation cap (how many separate conversations the sidebar
// keeps). No backend persistence exists across sessions yet — this is a
// testing-phase limit; revisit once a retention policy is decided.
export const MAX_HISTORY_ITEMS = 5;

export const NEW_CONVERSATION_TITLE = "New conversation";

export const CAPABILITY_CARDS = [
  {
    icon: "search",
    title: "Ask a question",
    description: "Type or speak a question and get an answer grounded in your indexed documents.",
    prompt: "What can you help me with?",
  },
  {
    icon: "layers",
    title: "Summarize context",
    description: "Ask for a summary of a topic covered in the knowledge base.",
    prompt: "Summarize the key points from the available context.",
  },
  {
    icon: "calc",
    title: "Dig into details",
    description: "Ask a specific, detailed question and hear the answer read back to you.",
    prompt: "Give me the specific details on that.",
  },
];

// Must match tts.py's models_list — these are real Deepgram Aura-2 voice
// model ids, not decorative labels.
export const VOICE_OPTIONS = [
  { id: "aura-2-thalia-en", label: "Thalia", tone: "Warm, feminine" },
  { id: "aura-2-asteria-en", label: "Asteria", tone: "Clear, feminine" },
  { id: "aura-2-luna-en", label: "Luna", tone: "Soft, feminine" },
  { id: "aura-2-hera-en", label: "Hera", tone: "Mature, feminine" },
  { id: "aura-2-orion-en", label: "Orion", tone: "Deep, masculine" },
  { id: "aura-2-zeus-en", label: "Zeus", tone: "Bold, masculine" },
  { id: "aura-2-apollo-en", label: "Apollo", tone: "Confident, masculine" },
  { id: "aura-2-arcas-en", label: "Arcas", tone: "Calm, masculine" },
];
export const DEFAULT_VOICE = VOICE_OPTIONS[0].id;

// Each swaps the accent color CSS variables at runtime (see theme.css / App.jsx).
// A restrained, professional palette — no neon/saturated colors.
export const THEME_OPTIONS = [
  { id: "indigo", label: "Indigo", accent: "#6366f1", accentBright: "#818cf8", accentDim: "#33366b" },
  { id: "emerald", label: "Emerald", accent: "#10b981", accentBright: "#34d399", accentDim: "#0b5c47" },
  { id: "sky", label: "Sky", accent: "#0ea5e9", accentBright: "#38bdf8", accentDim: "#0a5578" },
  { id: "amber", label: "Amber", accent: "#f59e0b", accentBright: "#fbbf24", accentDim: "#7a4d06" },
];
export const DEFAULT_THEME = THEME_OPTIONS[0].id;
