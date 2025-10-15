import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables from backend/.env and accept GEMINI_API_KEY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=False)
google_api_key = os.getenv("GEMINI_API_KEY")

DB_DIR = os.path.join(BASE_DIR, "db")


async def get_answer(query: str, source: str | None = None, user_id: int = None) -> str:
    """
    Retrieve the most relevant document chunks from Chroma,
    feed them into the LLM, and return a synthesized answer.
    """

    # Load stored embeddings from Chroma
    # Read the active model if present, to align with last upload for this user
    active_model_file = os.path.join(DB_DIR, f"user_{user_id}_current_model.txt")
    active_model = None
    if os.path.isfile(active_model_file):
        try:
            with open(active_model_file, "r", encoding="utf-8") as f:
                active_model = f.read().strip()
        except Exception:
            active_model = None

    # Choose embeddings matching the active model if possible
    if active_model == "gemini-embedding-001":
        embedding_fn = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=google_api_key,
        )
        model_db_subdir = "gemini-embedding-001"
    elif active_model == "all-MiniLM-L6-v2":
        embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        model_db_subdir = "all-MiniLM-L6-v2"
    else:
        # Fallback: try Gemini first, then HF
        try:
            embedding_fn = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=google_api_key,
            )
            model_db_subdir = "gemini-embedding-001"
        except Exception:
            embedding_fn = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            model_db_subdir = "all-MiniLM-L6-v2"

    # Use the same model-specific directory as ingestion to avoid dimension mismatch
    user_model_db_dir = os.path.join(DB_DIR, f"user_{user_id}", model_db_subdir)
    db = Chroma(
        persist_directory=user_model_db_dir,
        embedding_function=embedding_fn,
    )

    # Retrieve top-k relevant chunks
    # If a source is provided (or last_source.txt exists), filter to that source
    metadata_filter = {"user_id": str(user_id)}  # Always filter by user
    if source:
        metadata_filter["source"] = source
    else:
        last_source_file = os.path.join(user_model_db_dir, "last_source.txt")
        if os.path.isfile(last_source_file):
            try:
                with open(last_source_file, "r", encoding="utf-8") as f:
                    last_source = f.read().strip()
                    if last_source:
                        metadata_filter["source"] = last_source
            except Exception:
                pass

    if metadata_filter:
        retriever = db.as_retriever(search_kwargs={"k": 4},
                                    search_type="similarity",
                                    filter=metadata_filter)
    else:
        retriever = db.as_retriever(search_kwargs={"k": 4})

    docs = retriever.invoke(query)
    context = "\n\n".join([d.page_content for d in docs])

    if not context.strip():
        return "No relevant information found in the uploaded documents."


    # Construct prompt
    prompt = (
        f"Using the following context, answer the user's question concisely and clearly.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0,
        )
        result = llm.invoke(prompt)
        return getattr(result, "content", str(result))
    except Exception:
        return "LLM request failed. Please try again later."
