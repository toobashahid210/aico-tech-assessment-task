# 🧠 AI Webpage Summarizer & QnA with Memory  

This project allows you to:  
- Ingest webpages, summarize them, and store them in a **FAISS vector database**.  
- Interact with the knowledge base through a **FastAPI backend**.  
- Use a **Streamlit frontend** for a friendly interface.  
- Ask questions and get answers with **conversational memory** (last 3 interactions remembered).  

---

## ✨ Features  

- 🌐 **Webpage Agent** – fetches and processes webpage content.  
- 📚 **FAISS Vector Database** – stores embeddings of the webpage text for efficient retrieval.  
- 🧠 **Conversational Retrieval Chain** – uses LangChain to retrieve relevant docs and answer queries.  
- 💬 **Memory Support** – remembers last **3 interactions** to maintain context.  
- ⚡ **FastAPI Backend** – API endpoints for summarization & QnA.  
- 🎨 **Streamlit Frontend** – simple and interactive UI.  

---

## 🛠️ Tech Stack  

- Python 3.10+  
- FastAPI – backend API  
- Streamlit – frontend interface  
- LangChain – LLM orchestration  
- FAISS – vector similarity search  
- OpenAI API (or other embeddings/LLM providers)  
- Playwright – webpage scraping  

---

## 🧩 Strategy & Design Choices  

### 1. **Vector Database: FAISS**
- **Choice:** FAISS was selected for **fast similarity search** over large text embeddings.  
- **Why:**  
  - High performance for semantic search.  
  - Easy to integrate with LangChain’s retrievers.  
  - Can store embeddings locally and reload them to resume work.  
- **How:**  
  - Webpage text is chunked and converted into embeddings.  
  - Each chunk is stored in FAISS with metadata.  
  - When querying, FAISS retrieves the most relevant chunks efficiently.  

---

### 2. **LLM Chain & Conversational Memory**
- **Choice:** `ConversationalRetrievalChain` from LangChain.  
- **Why:**  
  - Integrates **retrieval and generation** seamlessly.  
  - Supports **memory buffers**, allowing multi-turn conversations.  
- **How:**  
  - Uses a **retriever** connected to FAISS.  
  - Maintains a **window memory** of the last 3 interactions (`ConversationBufferWindowMemory`) so the conversation context is preserved without overloading the model.  
  - Output key explicitly set to `"answer"` to avoid multiple output conflicts.  

---

### 3. **Webpage Agent**
- **Choice:** Playwright + custom scraper.  
- **Why:**  
  - Playwright ensures **full webpage rendering**, including dynamic content.  
  - Reliable across multiple browsers.  
- **How:**  
  - Agent fetches the URL.  
  - Extracts the textual content.  
  - Splits text into chunks.  
  - Adds chunks to FAISS vector store with metadata.  

---

### 4. **FastAPI Backend**
- **Choice:** FastAPI for API endpoints (`/summarize`, `/chat`).  
- **Why:**  
  - High performance asynchronous API framework.  
  - Easy integration with background tasks for web scraping.  
- **How:**  
  - `/summarize` → ingests webpage content, embeds, and updates FAISS.  
  - `/chat` → retrieves relevant documents and calls the LLM chain with memory.  

---

### 5. **Streamlit Frontend**
- **Choice:** Streamlit for interactive UI.  
- **Why:**  
  - Rapid prototyping and visualization.  
  - Users can ask questions and see answers in real-time.  
- **How:**  
  - Frontend sends user queries to FastAPI.  
  - Displays model responses and optionally source documents.  

---

### 6. **Why This Architecture**
- **Modular:** Each component (webpage agent, vector store, LLM chain, memory, frontend) is decoupled for maintainability.  
- **Persistent Knowledge Base:** FAISS allows saving/loading state so you can resume without retraining embeddings.  
- **Conversational Experience:** Memory buffer allows multi-turn QA without confusing the model.  
- **Scalable & Extensible:**  
  - Easy to swap embeddings/LLMs.  
  - Frontend and backend can scale independently.  
  - FAISS index can grow with more webpages.  

---

## ⚙️ Setup  

### 1. Clone the repository  
```bash
git clone https://github.com/toobashahid210/aico-tech-assessment-task.git
cd aico-tech-assessment-task
```

### 2. Create virtual enviroment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright
```bash
playwright install
```

## 🚀 Running the Apps

Add .env file to add environment variables e.g OPENAI_API_KEY
Run both FastAPI and Streamlit apps together:
```bash
./run_apps.sh
```
FastAPI → http://localhost:8000
Streamlit → http://localhost:8501

```python
http://localhost:8000/docs is where you can test all the endpoints
```