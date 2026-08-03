from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForCausalLM

# --- MENTION THE MODEL NAME HERE ---
MODEL_NAME = "HuggingFaceTB/SmolLM2-360M-Instruct" 
SAVE_PATH = "./onnx_generation_output"

# This downloads the named model and converts it to ONNX format
model = ORTModelForCausalLM.from_pretrained(MODEL_NAME, export=True)
model.save_pretrained(SAVE_PATH)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.save_pretrained(SAVE_PATH)

print(f"Successfully converted {MODEL_NAME} and saved it to {SAVE_PATH}")
