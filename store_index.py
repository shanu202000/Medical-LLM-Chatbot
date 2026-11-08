from src.helper import filter_to_minimal_docs, load_pdf_file, text_split, download_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

# Set environment variables explicitly if needed
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GROQ_API_KEY"]=GROQ_API_KEY

# 1. Load raw data from the data directory
extracted_data = load_pdf_file(data='data/')

# 2. Filter the data to only contain source as metadata and the original page_content
filtered_data = filter_to_minimal_docs(extracted_data)
# 3. Split the data into smaller chunks
text_chunks = text_split(filtered_data)

# 4. Download/initialize the embeddings model
embeddings = download_embeddings()

# 5. Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medical-chatbot"

# 6. Create index if it doesn't exist already
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,  # Adjust based on your embedding dimension (e.g., 384 for all-MiniLM-L6-v2, 1536 for OpenAI)
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)
# 7. Embed each chunk and upsert into the Pinecone vector store
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings
)

print(f"Successfully stored {len(text_chunks)} chunks into Pinecone index: {index_name}")