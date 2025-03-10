import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFacePipeline
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Paths from environment variables
DATA_DIR = os.getenv("DATA_DIR", "E:/project/tax_advisor/data")
MODEL_DIR = os.getenv("MODEL_DIR", "E:/project/tax_advisor/model/local_model")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "E:/project/tax_advisor/model/chroma_db")

# ✅ Load and process documents
def load_docs(directory):
    loader = DirectoryLoader(directory)
    return loader.load()

docs = load_docs(DATA_DIR)

def split_docs(doc, chunk_size=512, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(doc)

docs = split_docs(docs)

# ✅ Initialize embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(docs, embeddings, persist_directory=CHROMA_DB_DIR, collection_metadata={"hnsw:space": "cosine"})
new_db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

def get_similar_docs(query, k=1, score=False):
    return new_db.similarity_search_with_score(query, k=k) if score else new_db.similarity_search(query, k=k)

# ✅ Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ Use 8-bit quantization to speed up inference & reduce memory
bnb_config = BitsAndBytesConfig(load_in_8bit=True)

print("🚀 Loading Mistral-7B-Instruct model...")

# ✅ Load model ONCE at startup & keep it in memory
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR, quantization_config=bnb_config).to(device)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

# ✅ Optimized text generation pipeline
text_generation_pipeline = pipeline(
    model=model,
    tokenizer=tokenizer,
    task="text-generation",
    temperature=0.2,
    do_sample=True,
    repetition_penalty=1.1,
    return_full_text=False,  # Prevents repeating the prompt
    max_new_tokens=512,  # Increase to allow longer responses
)

llm = HuggingFacePipeline(pipeline=text_generation_pipeline)

# ✅ Create prompt template
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="{context}\n\nProvide a clear and concise answer to the following question:\n{question}\n\nAnswer:"
)

# ✅ Preload LLM chain for faster response
chain = create_stuff_documents_chain(llm, prompt_template)

# ✅ Function to get answers
def get_answer(query):
    similar_docs = get_similar_docs(query)
    answer = chain.invoke({"context": similar_docs, "question": query})
    return answer

# ✅ FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

class QueryRequest(BaseModel):
    query: str

@app.post("/q/")
def get_answer_api(request: QueryRequest):
    result = get_answer(request.query)
    return {"query": request.query, "answer": result}

if __name__ == "__main__":
    import uvicorn
    print("🚀 API is running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
