from fastapi import APIRouter,Request,HTTPException,status
from logging import error as rag_api_error
import rag_functions

rag_router = APIRouter()
embedding_model = rag_functions.get_embedding_model()
re_rank_model = rag_functions.get_rerank_model()
client = rag_functions.get_qdrant_client()
tokenizer, gen_model = rag_functions.get_generation_model()

@rag_router.get("/api/get_context")
async def get_context(request:Request):
    """
    Input -> Query (str)
    Output -> Answer from llm (str)
    [Note : the input has to be given in json format 
        eg: {"query":"<query>"}
    the quality and efficiency of answer depends on llm model you're using
    ]
    """
    try:
        if request.headers.get("content-type","") != "application/json":
            rag_api_error("please provide json body")
            raise HTTPException(
                detail="Required body format = json",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
            )
        body = await request.json()
        query = body.get("query","").strip()
        print(query)
        if not query:
            rag_api_error("please provide the query params properly")
            raise HTTPException(
                detail="please provide the query params properly",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
            )
        
        results = rag_functions.retrieve(query,embedding_model,re_rank_model,client)
        chunks = [chunk for score, chunk in results]

        return rag_functions.generate_answer(query,chunks,tokenizer,gen_model)
    
    except Exception as e:
        rag_api_error(e)
        raise 
        
    
    
    
    