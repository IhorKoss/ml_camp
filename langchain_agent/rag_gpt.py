from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain import hub
import PyPDF2
import hashlib

from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

os.environ["LANGSMITH_TRACING_V2"] = "false"

def load_biography(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        bio_text = file.read()
    return bio_text


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50, 
        length_function=len
    )
    return splitter.split_text(text)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join(page.extract_text() for page in reader.pages)
    return text

bio_text = load_biography("C:\ml_camp\\bio.txt")
cv_text = extract_text_from_pdf("C:\ml_camp\CV.pdf")
combined_text = bio_text + "\n\n" + cv_text

def create_vectorstore(texts, embeddings):
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory="chroma_index"
    )
    return vectorstore

def load_vectorstore(embeddings):
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="chroma_index"
    )
    return vectorstore

def get_biography_fact(query):
    embeddings = OpenAIEmbeddings(api_key=api_key)
    
    current_text_hash = hashlib.md5(combined_text.encode()).hexdigest()
    hash_file_path = "chroma_index_hash.txt"
    
    if os.path.exists("chroma_index") and os.path.exists(hash_file_path):
        with open(hash_file_path, "r") as hash_file:
            saved_text_hash = hash_file.read().strip()
        if saved_text_hash == current_text_hash:
            print("Loaded existing Chroma vectorstore")
            vectorstore = load_vectorstore(embeddings)
        else:
            print("Creating new Chroma vectorstore with updated text")
            texts = split_text(combined_text)
            vectorstore = create_vectorstore(texts, embeddings)
            with open(hash_file_path, "w") as hash_file:
                hash_file.write(current_text_hash)
    else:
        print("Creating new Chroma vectorstore from scratch")
        texts = split_text(combined_text)
        vectorstore = create_vectorstore(texts, embeddings)
        with open(hash_file_path, "w") as hash_file:
            hash_file.write(current_text_hash)
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = hub.pull("rlm/rag-prompt")
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )
    response = qa_chain.invoke({"query": query})
    return(response["result"])

app = FastAPI(title="RAG Service")

class BiographyQuery(BaseModel):
    query: str

class BiographyResponse(BaseModel):
    answer: str

@app.post("/biography", response_model=BiographyResponse)
def biography_endpoint(request: BiographyQuery):
    answer = get_biography_fact(request.query)
    return BiographyResponse(answer=answer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)