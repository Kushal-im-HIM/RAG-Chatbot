import streamlit as st
import os
from dotenv import load_dotenv

# --- LANGCHAIN IMPORTS (The Brains) ---
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()

st.set_page_config(
    page_title="MDN DevBot",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants (Must match your ingest.py)
INDEX_NAME = "mdn-rag-hackathon"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- 2. CUSTOM CSS (Your Original UI) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .app-title { font-family: 'Courier New', monospace; font-size: 2.5rem; font-weight: 700; color: #58a6ff; margin-bottom: 0px; }
    .app-subtitle { font-size: 1rem; color: #8b949e; margin-bottom: 2rem; }
    .stChatInputContainer textarea { background-color: #0d1117; border: 1px solid #30363d; color: white; }
    .source-box { background-color: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d; margin-top: 10px; font-size: 0.85rem; color: #8b949e; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
</style>
""", unsafe_allow_html=True)

# --- 3. RAG ENGINE INITIALIZATION (Cached) ---
@st.cache_resource
def get_rag_chain(api_key_groq, api_key_pinecone):
    """Initializes the RAG chain only once to speed up the app."""
    
    # 1. Setup Embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # 2. Connect to Pinecone
    vectorstore = PineconeVectorStore(
        index_name=INDEX_NAME, 
        embedding=embeddings,
        pinecone_api_key=api_key_pinecone
    )
    
    # 3. Create Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 4. Setup LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key_groq,
        temperature=0.5 
    )
    
    # 5. Create Prompt & Chain
    system_prompt = (
        "You are a web development expert (MDN Bot). "
        "Use the following pieces of retrieved context to answer the question. "
        "If the context doesn't answer the question, say so. "
        "Keep answers concise and code-focused."
        "\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # Note: Changing temperature here won't update the cached chain dynamically in this simple version
    # to keep it fast, but we keep the UI element.
    st.slider("Creativity (Fixed)", 0.0, 1.0, 0.5, disabled=True) 
    st.markdown("---")
    if st.button("🗑️ Clear Context", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("### 📚 Resources")
    st.markdown("- [MDN Web Docs](https://developer.mozilla.org/en-US/)")
    st.markdown("- [React Docs](https://react.dev/)")

# --- 5. INITIALIZE APP LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load API Keys
groq_key = os.getenv("GROQ_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

if not groq_key or not pinecone_key:
    st.error("❌ Missing API Keys in .env file")
    st.stop()

# Initialize the Chain
try:
    rag_chain = get_rag_chain(groq_key, pinecone_key)
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 6. MAIN HEADER & HERO SECTION ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="app-title">🦖 MDN DevBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Your offline-capable RAG Web Expert</div>', unsafe_allow_html=True)

# Hero Buttons (Only show if empty)
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚀 How can I help you build today?")
    c1, c2, c3, c4 = st.columns(4)
    
    if c1.button("CSS Flexbox 🎨", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Explain CSS Flexbox with examples."})
        st.rerun()
    if c2.button("React Hooks ⚛️", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "How does useEffect work in React?"})
        st.rerun()
    if c3.button("API Fetch 🌐", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "Show me how to fetch data in JavaScript."})
        st.rerun()
    if c4.button("Debug Code 🐛", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": "I need help debugging a Python script."})
        st.rerun()

# --- 7. CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Check if this message has source metadata attached
        if "sources" in message:
            with st.expander("🔍 View Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

# --- 8. CHAT INPUT & PROCESSING ---
if prompt := st.chat_input("Ask about code..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("🔍 Searching Knowledge Base..."):
            try:
                # This is the RAG magic happening
                response = rag_chain.invoke({"input": prompt})
                
                answer = response['answer']
                
                # Extract unique sources
                raw_sources = [doc.metadata.get('source', 'Unknown') for doc in response['context']]
                unique_sources = list(set(raw_sources))
                
                message_placeholder.markdown(answer)
                
                # Show sources immediately below
                if unique_sources:
                    st.markdown(f"""
                    <div class="source-box">
                    📚 <b>Sources:</b><br>
                    {"<br>".join([f"• <a href='{s}' target='_blank' style='color:#58a6ff;'>{s}</a>" for s in unique_sources])}
                    </div>
                    """, unsafe_allow_html=True)

                # Save to history (including sources for the expander above)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": unique_sources
                })
                
            except Exception as e:
                st.error(f"Error: {e}")