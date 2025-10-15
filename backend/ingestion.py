import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Resolve paths relative to this file (backend directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DB_DIR = os.path.join(BASE_DIR, "db")

# Load environment variables from backend/.env; accept GOOGLE_API_KEY or GEMINI_API_KEY
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=False)
google_api_key = os.getenv("GEMINI_API_KEY")

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)


async def process_document(file, user_id: int):
    """
    Process a single uploaded PDF file:
    1. Save the file temporarily
    2. Extract text
    3. Split into chunks
    4. Generate embeddings
    5. Store in Chroma vector database
    """

    # Save uploaded file to a temporary folder
    save_path = os.path.join(TEMP_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # Load and extract text from the PDF
    loader = PyPDFLoader(save_path)
    docs = loader.load()

    # Split text into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    if not chunks:
        return

    # Tag chunks with source filename and user_id for traceability
    for d in chunks:
        d.metadata = d.metadata or {}
        d.metadata["source"] = file.filename
        d.metadata["user_id"] = str(user_id)

    # Initialize embeddings with Gemini first, then fallback to local HF model
    # Choose embeddings and corresponding collection directory
    embedding_model_id = None
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key,
        )
        # Quick probe: ensure embedding model returns vectors
        test_vec = embeddings.embed_query("ping")
        if not test_vec or len(test_vec) == 0:
            raise RuntimeError("Gemini embeddings returned empty vector")
        embedding_model_id = "gemini-embedding-001"
    except Exception:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        embedding_model_id = "all-MiniLM-L6-v2"

    # Create a fresh Chroma vector store in a user-specific directory
    user_db_dir = os.path.join(DB_DIR, f"user_{user_id}", embedding_model_id)
    # Single-document mode: clear previous index to avoid mixed context
    if os.path.isdir(user_db_dir):
        shutil.rmtree(user_db_dir, ignore_errors=True)
    os.makedirs(user_db_dir, exist_ok=True)
    db = Chroma.from_documents(chunks, embeddings, persist_directory=user_db_dir)

    # Record active model DB for retrieval
    with open(os.path.join(DB_DIR, f"user_{user_id}_current_model.txt"), "w", encoding="utf-8") as f:
        f.write(embedding_model_id)

    # Record last uploaded source filename for this user/model
    with open(os.path.join(user_db_dir, "last_source.txt"), "w", encoding="utf-8") as f:
        f.write(file.filename)

    print(f"✅ {file.filename} processed and stored successfully.")
