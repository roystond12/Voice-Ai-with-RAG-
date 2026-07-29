import rag_functions
embedding_model = rag_functions.get_embedding_model()
re_rank_model = rag_functions.get_rerank_model()
client = rag_functions.get_chroma_client()
collection = rag_functions.get_or_create_collection(client)
results = rag_functions.retrieve("what awards did michael jackson win", embedding_model, re_rank_model, collection)
print(results)
