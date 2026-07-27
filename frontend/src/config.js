// Copy and quick-prompt shortcuts that are easy to tweak without touching
// component code.

export const APP_NAME = "Voice AI";
export const GREETING_NAME = "there";

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
