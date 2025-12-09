import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()

st.set_page_config(
    page_title="MDN DevBot",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .app-title { font-family: 'Courier New', monospace; font-size: 2.5rem; font-weight: 700; color: #58a6ff; margin-bottom: 0px; }
    .app-subtitle { font-size: 1rem; color: #8b949e; margin-bottom: 2rem; }
    .stChatInputContainer textarea { background-color: #0d1117; border: 1px solid #30363d; color: white; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;} 
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    temperature = st.slider("Creativity", 0.0, 1.0, 0.5)
    st.markdown("---")
    if st.button("🗑️ Clear Context", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("### 📚 Resources")
    st.markdown("- [MDN Web Docs](https://developer.mozilla.org/en-US/)")
    st.markdown("- [React Docs](https://react.dev/)")
    st.markdown("- [Tailwind CSS](https://tailwindcss.com/)")

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. MAIN HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="app-title">🦖 MDN DevBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Your offline-capable Web Development expert</div>', unsafe_allow_html=True)

# --- 6. HERO SECTION (Empty State) ---
if len(st.session_state.messages) == 0:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚀 How can I help you build today?")
    c1, c2, c3, c4 = st.columns(4)
    
    # Logic: If button clicked -> Add to state -> Rerun
    with c1:
        if st.button("CSS Flexbox 🎨", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Explain CSS Flexbox with examples."})
            st.rerun()
    with c2:
        if st.button("React Hooks ⚛️", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "How does useEffect work in React?"})
            st.rerun()
    with c3:
        if st.button("API Fetch 🌐", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Show me how to fetch data in JavaScript."})
            st.rerun()
    with c4:
        if st.button("Debug Code 🐛", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "I need help debugging a Python script."})
            st.rerun()

# --- 7. CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 8. CHAT INPUT (User Typing) ---
if prompt := st.chat_input("Ask about code..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# --- 9. AI RESPONSE LOGIC (The Fix) ---
# Check if the last message is from the user. If so, generate a response.
# This works for BOTH typed input AND button clicks.
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                st.error("❌ API Key missing in .env")
                st.stop()

            client = Groq(api_key=api_key)
            
            # Using your model ID
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=temperature,
                stream=True,
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Force a rerun to ensure state is synced immediately
            st.rerun()
        
        except Exception as e:
            st.error(f"Error: {e}")