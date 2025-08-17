from dotenv import load_dotenv
load_dotenv()

from conversation_agent import ConversationAgent
from webpage_agent import WebPageAgent
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from utils import init_openai_llm, init_embeddings, init_vectorstore
from schemas import SummarizeRequest, ChatRequest

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in env")

app = FastAPI(title="AICO")
init_openai_llm()
init_embeddings()
init_vectorstore() 

URL_CACHE: Dict[str, Dict[str, Any]] = {} 
SESSIONS: Dict[str, Dict[str, Any]] = {} 


def new_session_id(new_session_id=None) -> str:
    if new_session_id is None:
        new_session_id = str(uuid.uuid4())
    SESSIONS[new_session_id] = ConversationAgent()
    return new_session_id

# --- Endpoints ---

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    url = str(req.url)

    if url in URL_CACHE:
        return URL_CACHE[url]

    try:
        webpage_agent = WebPageAgent(base_url=url)
        summary, topic = webpage_agent.process_webpage()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize URL: {e}")
    
    URL_CACHE[url] = {"summary": summary, "main_topic": topic}
    return URL_CACHE[url]

@app.post("/chat")
async def chat(req: ChatRequest):

    try:
        session_id = req.session_id or new_session_id()
        if session_id not in SESSIONS:
            session_id = new_session_id(session_id)
        conversation_agent = SESSIONS[session_id]
        answer = conversation_agent.ask(req.question)
        return answer.get("answer", "No answer found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation agent failed: {e}")


