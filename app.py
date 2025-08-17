from dotenv import load_dotenv
load_dotenv()

from conversation_agent import ConversationAgent
from webpage_agent import WebPageAgent
import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from utils import init_openai_llm, init_embeddings, init_vectorstore
from schemas import SummarizeRequest, ChatRequest
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise EnvironmentError("OPENAI_API_KEY not found in env")

app = FastAPI(title="AICO")

# Initialize components
init_openai_llm()
init_embeddings()
init_vectorstore()
logger.info("Initialized OpenAI LLM, embeddings, and vectorstore")

# In-memory caches
URL_CACHE: Dict[str, Dict[str, Any]] = {} 
SESSIONS: Dict[str, Dict[str, Any]] = {} 

def new_session_id(new_session_id=None) -> str:
    if new_session_id is None:
        new_session_id = str(uuid.uuid4())
    SESSIONS[new_session_id] = ConversationAgent()
    logger.info(f"Created new session: {new_session_id}")
    return new_session_id

# --- Endpoints ---

@app.get("/")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/summarize")
def summarize(req: SummarizeRequest):
    url = str(req.url)
    logger.info(f"Summarize requested for URL: {url}")

    if url in URL_CACHE:
        logger.info(f"Cache hit for URL: {url}")
        return URL_CACHE[url]

    try:
        webpage_agent = WebPageAgent(base_url=url)
        summary, topic = webpage_agent.process_webpage()
        logger.info(f"Successfully summarized URL: {url}")
    except Exception as e:
        logger.exception(f"Failed to summarize URL: {url}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize URL: {e}")
    
    URL_CACHE[url] = {"summary": summary, "main_topic": topic}
    return URL_CACHE[url]

@app.post("/chat")
async def chat(req: ChatRequest):
    logger.info(f"Chat requested. Session: {req.session_id}, Question: {req.question}")

    try:
        session_id = req.session_id or new_session_id()
        if session_id not in SESSIONS:
            session_id = new_session_id(session_id)
        conversation_agent = SESSIONS[session_id]
        answer = conversation_agent.ask(req.question)
        logger.info(f"Chat response: {answer.get('answer', 'No answer found')}")
        return answer.get("answer", "No answer found")
    except Exception as e:
        logger.exception("Conversation agent failed")
        raise HTTPException(status_code=500, detail=f"Conversation agent failed: {e}")
