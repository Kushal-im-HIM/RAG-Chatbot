import os
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

print(f"Current Directory: {os.getcwd()}")
print(f"File exists?: {os.path.exists('.env')}")
print(f"Pinecone Key: {os.getenv('PINECONE_API_KEY')}")