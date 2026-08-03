from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSequenceClassification

# 1. Define your rerank model ID (e.g., BAAI/bge-reranker-base) and save path
model_id = "BAAI/bge-reranker-base"  
save_directory = "./onnx_reranker_output"

# 2. Export and save the cross-encoder model architecture to ONNX
# The export=True parameter triggers the automated graph conversion under the hood
model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
model.save_pretrained(save_directory)

# 3. Save the matching tokenizer files to the same directory
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.save_pretrained(save_directory)

print(f"Success! ONNX rerank model and tokenizer saved to {save_directory}")
