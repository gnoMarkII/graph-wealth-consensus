import logging
import os
import time
from pathlib import Path

import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore


class GeminiRAGAgent:
    """Agent wrapper for Gemini summarization and optional RAG index management.
    model name: "gemini-3-flash-preview" or "gemini-2.5-flash" """

    def __init__(
        self,
        data_dir: str | Path = "./data",
        db_dir: str | Path = "./chroma_db_gemini",
        model_name: str = "gemini-3-flash-preview",
    ):
        self.data_dir = Path(data_dir)
        self.db_dir = Path(db_dir)
        self.model_name = model_name
        self.index = None
        self.llm = None
        self._setup_system()

    def _setup_system(self) -> None:
        """Initialize the embedding model, LLM, and Chroma vector store."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is required for GeminiRAGAgent")

        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.llm = GoogleGenAI(model=self.model_name)
        Settings.llm = self.llm

        try:
            db = chromadb.PersistentClient(path=str(self.db_dir))
            chroma_collection = db.get_or_create_collection("investment_knowledge_cloud")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            self.storage_context = StorageContext.from_defaults(vector_store=vector_store)
        except Exception as exc:
            raise RuntimeError(f"Failed to setup vector store: {exc}") from exc

    def summarize_transcript(self, prompt: str) -> str:
        """Generate a summary from the provided prompt using the Gemini LLM."""
        max_attempts = 4
        base_delay = 5

        logger = logging.getLogger(__name__)

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.llm.complete(prompt)
                return response.text
            except Exception as exc:
                message = str(exc).lower()
                if any(keyword in message for keyword in ["503", "unavailable", "429", "resource_exhausted", "quota_exceeded", "rate limit"]):
                    if attempt >= max_attempts:
                        raise RuntimeError(
                            f"Gemini summarization failed after {attempt} attempts: {exc}"
                        ) from exc

                    delay = base_delay * attempt
                    logger.warning(
                        "Gemini temporary failure (%s). Retrying in %s seconds (attempt %s/%s).",
                        exc,
                        delay,
                        attempt,
                        max_attempts,
                    )
                    time.sleep(delay)
                    continue

                raise

    def ingest_data(self, document_list: list[object]) -> None:
        """Build a vector index from a list of documents for retrieval-augmented generation."""
        if self.storage_context is None:
            raise RuntimeError("Storage context is not available for RAG ingestion")

        self.index = VectorStoreIndex.from_documents(
            document_list,
            storage_context=self.storage_context,
            show_progress=True,
        )

    def query(self, question: str, top_k: int = 3) -> object:
        """Query the built RAG index and return a retrieval-based response."""
        if not self.index:
            raise RuntimeError("No index available. Call ingest_data() first.")

        query_engine = self.index.as_query_engine(similarity_top_k=top_k)
        return query_engine.query(question)
