import re
from fastapi import HTTPException
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser
# from langchain.agents import AgentExecutor, create_openai_tools_agent
# from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from utils import get_vectorstore, get_openai_llm, get_embeddings

class WebPageAgent:
    def __init__(self, base_url):
        self.base_url = base_url
        self.llm = get_openai_llm()
        self.embeddings = get_embeddings()
        self.vectorstore = get_vectorstore()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)

        self.sync_browser = create_sync_playwright_browser()
        self.toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=self.sync_browser)
        self.tools = self.toolkit.get_tools()
        self.tools_by_name = {tool.name: tool for tool in self.tools}

    @staticmethod
    def clean_text(txt: str) -> str:
        return re.sub(r"\s+", " ", txt).strip()

    def fetch_page_text(self) -> str:
        try:
            self.tools_by_name['navigate_browser'].run({"url": self.base_url})
            # Wait for the page to load and extract text
            self.tools_by_name['get_elements'].run({"selector": "body"})
            text = self.tools_by_name['extract_text'].run({})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract text from {self.base_url}: {e}")
        return self.clean_text(text)

    def split_docs(self, text: str):
        doc = Document(page_content=text)
        chunked_docs = self.text_splitter.split_documents([doc])
        return chunked_docs

    def summarize(self, docs):
        prompt = """You are an expert at summarizing webpages. 
            Read the following webpage text and summarize it in a clear, concise way, focusing only on the main article or content.  

            Important instructions:
            - Focus on the main article or content of the page. It should be very concise, informative, and to the point.
            - Include all key details relevant to the main topic.  
            - Ignore navigation menus, sidebars, footers, advertisements, cookie notices, or any unrelated sections.  
            - **NEVER** add information that is not present in the text.  
            - Your summary should reflect only the actual subject matter of the page.  

            {text}"""
        
        summary = ""
        for doc in docs:
            try:
                _prompt = prompt.format(text=doc.page_content)
                out = self.llm.invoke(_prompt)
                summary += self.clean_text(out.content) + "\n\n"
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to summarize document: {e}")
        return self.clean_text(summary)

    def extract_topic(self, summary: str) -> str:
        prompt = f"Summarize the main topic of this text in max 5 words:\n{summary}\n\nTopic:"
        try:
            out = self.llm.invoke(prompt)
            return self.clean_text(out.content)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to extract topic from summary.")
    
    def process_webpage(self):
        try:
            text = self.fetch_page_text()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Fetch failed: {e}")

        docs = self.split_docs(text)
        try:
            summary = self.summarize(docs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")
        
        topic = self.extract_topic(summary)

        docs = [Document(page_content=f"{topic}\n\n{summary}", metadata={"source": self.base_url})]

        self.vectorstore.add_documents(docs)

        return summary, topic
    