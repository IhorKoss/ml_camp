from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from gradio_styles import Seafoam
import gradio as gr
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import requests

RAG_SERVICE_URL = "http://localhost:8001/biography"
SPAM_SERVICE_URL = "http://localhost:8002/detect_spam"

def biography_req(query: str) -> str:
    try:
        response = requests.post(RAG_SERVICE_URL, json={"query": query})
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "No answer")
    except Exception as e:
        return f"Error in biography_tool: {e}"

def spam_req(query: str) -> str:
    try:
        response = requests.post(SPAM_SERVICE_URL, json={"text": query})
        response.raise_for_status()
        data = response.json()
        label = data.get("label", "Unknown")
        probability = data.get("probability")
        return f"Label: {label}, Probability: {probability:.4f}%"
    except Exception as e:
        return f"Error in spam_tool: {e}"

spam_detection_tool = Tool(
    name="SpamDetector",
    func=spam_req,
    description="Detects if text is spam or not and returns the probability.Used ONLY WHEN ASKED to detect spam. When tool is used, answer MUST include the answer AND probability in percents."
)

rag_tool = Tool(
    name="BiographySearch",
    func=biography_req,
    description="Searches for facts in a biography. Used for questions containint 'me', 'my' etc. MUST BE USED FOR ALL ANY personal questions."
)

default_tool = Tool(
    name="DefaultHandler",
    func=lambda query: "This query does not match any known tools. Please try asking something else.",
    description="Handles queries that do not match any specific tool. Not halucinate! Inform user that query does not match any known tools."
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

seafoam=Seafoam()

tools = [spam_detection_tool, rag_tool, default_tool]
agent = initialize_agent(
    tools, 
    llm, 
    agent="zero-shot-react-description", 
    verbose=True
)

def process_query(user_query):
    response = agent.run(user_query)
    return response

app = FastAPI(title="LangChain Agent Microservice")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    result = process_query(request.query)
    return QueryResponse(response=result)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
