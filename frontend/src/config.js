// Copy, voice options, and theme presets — kept out of component code so
// they're easy to tweak without touching UI logic.

export const APP_NAME = "Voice AI";
export const TAGLINE = "Ask with your voice. Listen to the answer.";
export const GREETING_NAME = "Deepsu";

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

// Each theme is a full palette (surfaces + text + accent), swapped at
// runtime as CSS variables (see theme.css / App.jsx) — not just an accent
// color layered on one fixed background. "White" and "Black" are true
// neutral themes; the rest tint their surfaces to match their accent hue.
export const THEME_OPTIONS = [
  {
    id: "white",
    label: "White",
    dark: false,
    bg: "#f5f6fa",
    bgElevated: "#ffffff",
    panel: "#ffffff",
    panelHover: "#f0f1f7",
    border: "#e2e4ec",
    accent: "#6366f1",
    accentBright: "#4f46e5",
    accentDim: "#e0e1fb",
    text: "#1a1c26",
    textDim: "#5c5f70",
    textFaint: "#8b8ea1",
  },
  {
    id: "black",
    label: "Black",
    dark: true,
    bg: "#0a0a0f",
    bgElevated: "#101117",
    panel: "#15161e",
    panelHover: "#1c1e28",
    border: "#262832",
    accent: "#818cf8",
    accentBright: "#a5b4fc",
    accentDim: "#33366b",
    text: "#eceef2",
    textDim: "#9a9dab",
    textFaint: "#64677a",
  },
  {
    id: "indigo",
    label: "Indigo",
    dark: false,
    bg: "#f2f2fc",
    bgElevated: "#ffffff",
    panel: "#ffffff",
    panelHover: "#ececfb",
    border: "#dedef5",
    accent: "#6366f1",
    accentBright: "#4f46e5",
    accentDim: "#e0e1fb",
    text: "#1e1b3a",
    textDim: "#5b5780",
    textFaint: "#8d89ab",
  },
  {
    id: "emerald",
    label: "Emerald",
    dark: false,
    bg: "#f1faf6",
    bgElevated: "#ffffff",
    panel: "#ffffff",
    panelHover: "#e8f6f0",
    border: "#d7ede3",
    accent: "#10b981",
    accentBright: "#059669",
    accentDim: "#d7f5ea",
    text: "#0f2e24",
    textDim: "#4f6d61",
    textFaint: "#83a396",
  },
  {
    id: "sky",
    label: "Sky",
    dark: false,
    bg: "#f0f8fd",
    bgElevated: "#ffffff",
    panel: "#ffffff",
    panelHover: "#e6f3fb",
    border: "#d3e9f5",
    accent: "#0ea5e9",
    accentBright: "#0284c7",
    accentDim: "#d7f0fb",
    text: "#0d2733",
    textDim: "#4b6b78",
    textFaint: "#7fa0ad",
  },
  {
    id: "amber",
    label: "Amber",
    dark: false,
    bg: "#fdf9f0",
    bgElevated: "#ffffff",
    panel: "#ffffff",
    panelHover: "#fbf2df",
    border: "#f0e2c2",
    accent: "#f59e0b",
    accentBright: "#d97706",
    accentDim: "#fbecd0",
    text: "#332405",
    textDim: "#6b5730",
    textFaint: "#a08a5e",
  },
];
export const DEFAULT_THEME = "white";
