import streamlit as st
import requests
import uuid

BASE_URL = "http://localhost:8000" 

st.set_page_config(page_title="AICO Summarizer Chat", layout="wide")

if "session_id" not in st.session_state: st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state["messages"] = []
if "indexed_urls" not in st.session_state: st.session_state["indexed_urls"] = []
if "indexed_meta" not in st.session_state: st.session_state["indexed_meta"] = {}

st.sidebar.header("Summarize Web Pages")

url = st.sidebar.text_area("URL", placeholder="https://example.com")
if st.sidebar.button("Index URL", type="primary"):
    url = url.strip()
    if not url: st.sidebar.warning("Please paste a URL.")
    else:
        with st.spinner("Indexing URL..."):
            try:
                resp = requests.post(f"{BASE_URL}/summarize", json={"url": url}, timeout=120)
            except Exception as e:
                st.sidebar.error(f"Failed to call /summarize for {url}: {e}")

            if resp.status_code == 200:
                data = resp.json()
                st.sidebar.success(f"Indexed: {url}")
                if url not in st.session_state["indexed_urls"]:
                    st.session_state["indexed_urls"].append(url)
                st.session_state["indexed_meta"][url] = {
                    "summary": data.get("summary"),
                    "main_topic": data.get("main_topic")}
            else:
                st.sidebar.error(f"Error indexing {url}: {resp.status_code}")

if st.session_state["indexed_urls"]:
    st.sidebar.markdown("### Web Pages")
    for url in st.session_state["indexed_urls"]:
        meta = st.session_state["indexed_meta"].get(url, {})
        main_topic = meta.get("main_topic", "—")
        with st.sidebar.expander(main_topic, expanded=False):
            st.markdown("**Topic:** " + (meta.get("main_topic") or "—"))
            if meta.get("summary"):
                st.markdown("**Summary:**")
                st.write(meta["summary"])

cols = st.columns([7, 2])
with cols[0]:
    st.subheader("Aico Chat")

with cols[1]:   
    if st.button("Refresh Session"):
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    role = msg.get("role", "user")
    with st.chat_message(role):
        st.markdown(msg["content"])

for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask something about the web pages...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        collected_chunks = []
        final_text = ""

        try:
            request_json = {
                "question": user_input,
                "session_id": st.session_state["session_id"]
            }
            resp = requests.post(f"{BASE_URL}/chat", json=request_json, timeout=120)
        except Exception as e:
            err = f"Request failed: {e}"
            placeholder.markdown(err)
            st.session_state["messages"].append({"role": "assistant", "content": err})
        else:
            if resp.status_code != 200:
                try:
                    txt = resp.text
                except Exception:
                    txt = f"HTTP {resp.status_code}"
                placeholder.markdown(f"Error: {txt}")
                st.session_state["messages"].append({"role": "assistant", "content": f"Error: {txt}"})
            else:
                try:
                    data = resp.json()
                    final_text = data.get("answer", "No answer provided.")
                    placeholder.markdown(final_text)
                    st.session_state["messages"].append({"role": "assistant", "content": final_text})
                except Exception as e:
                    err = f"Error: {e}"
                    placeholder.markdown(err)
                    st.session_state["messages"].append({"role": "assistant", "content": err})

# from dotenv import load_dotenv
# load_dotenv()
# from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings

# def test_vectorstore(path="vectorstore_db"):
#     # init embeddings (same you used during creation)
#     embeddings = OpenAIEmbeddings()

#     # load the FAISS store
#     vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

#     print("✅ Loaded FAISS vectorstore")

#     # check how many docs are inside
#     if hasattr(vectorstore, "docstore") and hasattr(vectorstore.docstore, "_dict"):
#         docs = list(vectorstore.docstore._dict.values())
#         print(f"📄 Total docs stored: {len(docs)}")
#         for i, d in enumerate(docs[:5], start=1):  # show only first 5
#             print(f"\n--- Doc {i} ---")
#             print(d.page_content[:300])  # preview first 300 chars
#             print("Metadata:", d.metadata)
#     else:
#         print("⚠️ No docs found in vectorstore")

# if __name__ == "__main__":
#     test_vectorstore("vectorstore_db")
