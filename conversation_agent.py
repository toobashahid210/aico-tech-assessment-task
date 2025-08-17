from utils import get_vectorstore, get_openai_llm, get_embeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

class ConversationAgent:
    def __init__(self):

        self.vectorstore = get_vectorstore()
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1})

        memory = ConversationBufferWindowMemory(
            k=3,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        self.chain = ConversationalRetrievalChain.from_llm(
            llm=get_openai_llm(),
            retriever=retriever,
            memory=memory,
            return_source_documents=True, 
        )

    def ask(self, query: str):
        result = self.chain.invoke({"question": query})
        return {
            "answer": result["answer"],
            "sources": result.get("source_documents", []),
        }
