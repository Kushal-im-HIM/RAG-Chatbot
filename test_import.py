try:
    from langchain.chains import create_retrieval_chain
    print("✅ SUCCESS: 'create_retrieval_chain' was found!")
except ImportError as e:
    print(f"❌ ERROR: Still failing. Details: {e}")