import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Model and Vector Database Configuration
model_name = "zephyr:7b-beta-q4_K_S"
llm = OllamaLLM(model=model_name, max_tokens=200)

persist_directory = "E:/project/tax_advisor/model/taxadvisor_db1"
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

retriever = vector_db.as_retriever(search_kwargs={"k": 2})

async def generate_answer(query: str):
    """ Asynchronously retrieves documents and streams LLM response """
    docs = await asyncio.to_thread(retriever.invoke, query)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = f"You are a tax expert. Use the following information to answer the user's question:\n\n{context}\n\nQuery: {query}\nAnswer:"

    # Stream response from LLM
    async def stream():
        async for chunk in llm.astream(prompt):  
            yield chunk  # Yield each chunk as it's generated

    return StreamingResponse(stream(), media_type="text/plain")

# API Route for Querying
@app.get("/query")
async def query_llm(q: str):
    return await generate_answer(q)

