
import os
import faiss
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

VECTORSTORE = None
OPENAI_LLM = None
EMBEDDING_MODEL = None  
vector_db_path = "vectorstore_db"

def init_openai_llm():
    global OPENAI_LLM
    OPENAI_LLM = ChatOpenAI(temperature=0.1, model="gpt-4")

def get_openai_llm():
    return OPENAI_LLM

def init_embeddings():
    global EMBEDDING_MODEL
    EMBEDDING_MODEL = OpenAIEmbeddings()

def get_embeddings():
    return EMBEDDING_MODEL

def init_vectorstore():
    global VECTORSTORE
    if os.path.exists(vector_db_path):
        VECTORSTORE = FAISS.load_local(vector_db_path, embeddings=get_embeddings(), allow_dangerous_deserialization=True)
    else:
        index = faiss.IndexFlatL2(len(get_embeddings().embed_query("A new database")))

        VECTORSTORE = FAISS(
            embedding_function=get_embeddings(),
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        VECTORSTORE.save_local(vector_db_path)

def get_vectorstore():
    return VECTORSTORE

