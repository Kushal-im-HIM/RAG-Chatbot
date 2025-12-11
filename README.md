# 🦖 MDN DevBot: A RAG ChatBot

**MDN DevBot** is a Retrieval-Augmented Generation (RAG) powered chatbot designed to assist web developers by providing accurate, context-aware answers sourced directly from the **Mozilla Developer Network (MDN)** documentation. 

Unlike standard LLMs that may hallucinate or provide outdated syntax, MDN DevBot retrieves the specific documentation chunks relevant to the user's query before generating an answer, ensuring high technical accuracy.

---

## 🚀 Key Features

* **RAG Architecture:** Combines the creative power of LLMs with the factual accuracy of a Vector Database.
* **Source Citations:** Every answer provides direct links to the MDN documentation sources used to generate the response.
* **Context-Aware:** Understands web development terminology (HTML, CSS, Flexbox, React Hooks).
* **High-Speed Inference:** Powered by **Groq** for near-instant text generation.
* **Vector Search:** Uses **Pinecone** for semantic similarity search, finding the right answers even if the user phrasing is inexact.

---

## 🏗️ Architecture & Workflow

This application operates in two distinct phases: **Ingestion** (Knowledge Base Creation) and **Retrieval** (Live Interaction).

### 1. The Ingestion Pipeline (Offline)
Before the app runs, the knowledge base is built using the following steps:
1.  **Scraping:** The `WebBaseLoader` fetches high-value pages from MDN Web Docs.
2.  **Chunking:** Text is split into smaller, manageable segments using `RecursiveCharacterTextSplitter` to optimize context window usage.
3.  **Embedding:** The **HuggingFace** model (`all-MiniLM-L6-v2`) converts these text chunks into high-dimensional vector embeddings.
4.  **Storage:** These vectors are upserted into a **Pinecone** serverless index for fast retrieval.

### 2. The Retrieval Pipeline (Live App)
When a user asks a question:
1.  **Query Embedding:** The user's input is converted into a vector using the same HuggingFace model.
2.  **Semantic Search:** Pinecone performs a similarity search to find the top 3 most relevant documentation chunks.
3.  **Context Construction:** LangChain combines the user's question + the retrieved MDN chunks into a single prompt.
4.  **Generation:** The **Llama 3** model (via Groq) generates a concise, accurate answer based *only* on the retrieved context.

---

## 🛠️ Tech Stack

* **Framework:** Streamlit (Python)
* **Orchestration:** LangChain
* **LLM:** Llama-3.1-8b-Instant (via Groq API)
* **Vector Database:** Pinecone (Serverless)
* **Embeddings:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)

---

## 🧠 How It Works (Visual Flow)

```mermaid
graph TD;
    User[User Query] -->|Embed| App[Streamlit App];
    App -->|Vector Search| DB[(Pinecone Vector DB)];
    DB -->|Return Relevant Docs| App;
    App -->|Prompt + Context| LLM[Groq Llama 3];
    LLM -->|Generates Answer| UI[User Interface];
