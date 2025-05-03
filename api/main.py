import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import ollama
from langchain_ollama import OllamaLLM
from langchain.chains import create_retrieval_chain  
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import PromptTemplate

# Initialize FastAPI
app = FastAPI()

# Enable CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurations
model_name = "zephyr:7b-beta-q4_K_S"
persist_directory = "E:/project/tax_advisor/model/taxadvisordb_v2-0"

# LLM and Vector Store Setup
llm = OllamaLLM(model=model_name, max_tokens=200)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 2})

# Async generator for streaming LLM output
async def generate_answer(query: str):
    docs = await asyncio.to_thread(retriever.invoke, query)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"You are a tax expert. Use the following information to answer the user's question:\n\n{context}\n\nQuery: {query}\nAnswer:"

    async def stream():
        async for chunk in llm.astream(prompt):
            yield chunk

    return StreamingResponse(stream(), media_type="text/plain")

# API endpoint
@app.get("/query")
async def query_llm(q: str = Query(..., description="User query for tax advice")):
    return await generate_answer(q)
