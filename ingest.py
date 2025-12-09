import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

# --- CONFIGURATION ---
INDEX_NAME = "mdn-rag-hackathon"

# WEBSITES TO SCRAPE (The "High Value" targets)
URLS = [
    # HTML Basics
    "https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML/Getting_started",
    "https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Your_first_form",
    # CSS Layouts & Styling
    "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Flexbox",
    "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Grids",
    "https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model",
    "https://developer.mozilla.org/en-US/docs/Learn/CSS/Styling_text/Fundamentals"
]

def setup_vector_db():
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

def ingest_data():
    setup_vector_db()
    
    # 1. Load Data from the Web
    print(f"🚀 Scraping {len(URLS)} key MDN pages...")
    loader = WebBaseLoader(URLS)
    docs = loader.load()
    print(f"   ✅ Loaded {len(docs)} pages.")

    # 2. Add Metadata (for your UI filter)
    # We roughly categorize them based on the URL text
    for doc in docs:
        if "CSS" in doc.metadata.get("source", ""):
            doc.metadata["category"] = "css"
        elif "HTML" in doc.metadata.get("source", ""):
            doc.metadata["category"] = "html"
        else:
            doc.metadata["category"] = "javascript" # Fallback

    # 3. Split Text
    print("   🔪 Splitting text...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = splitter.split_documents(docs)
    print(f"   ✅ Created {len(splits)} chunks.")
    
    # 4. Upload to Pinecone
    print("   🧠 Uploading to Pinecone...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=INDEX_NAME
    )
    print("\n🎉 SUCCESS: Knowledge Base Updated!")

if __name__ == "__main__":
    ingest_data()