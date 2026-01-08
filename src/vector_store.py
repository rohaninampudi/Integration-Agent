"""ChromaDB Vector Store for API Documentation Retrieval.

This module handles:
- Loading API documentation markdown files
- Chunking documents for optimal retrieval
- Generating embeddings with OpenAI
- Storing and querying with ChromaDB
"""

import hashlib
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.config import (
    API_DOCS_DIR,
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
)


class VectorStore:
    """ChromaDB-based vector store for API documentation retrieval.
    
    Usage:
        store = VectorStore()
        store.initialize()  # Load docs and create embeddings
        results = store.search("How to create a Slack message")
    """
    
    def __init__(
        self,
        persist_directory: Optional[Path] = None,
        collection_name: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """Initialize the vector store.
        
        Args:
            persist_directory: Path for ChromaDB persistence
            collection_name: Name of the ChromaDB collection
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.persist_directory = persist_directory or CHROMA_DIR
        self.collection_name = collection_name or CHROMA_COLLECTION_NAME
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
        
        self._vectorstore: Optional[Chroma] = None
    
    def _load_documents(self) -> list[Document]:
        """Load all markdown documents from the API docs directory."""
        loader = DirectoryLoader(
            str(API_DOCS_DIR),
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
        )
        documents = loader.load()
        
        # Add source metadata
        for doc in documents:
            # Extract filename without extension as the integration name
            source_path = Path(doc.metadata.get("source", ""))
            doc.metadata["integration"] = source_path.stem
            doc.metadata["file_name"] = source_path.name
        
        return documents
    
    def _chunk_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks for better retrieval."""
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            # Create a unique ID for the chunk
            content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()[:8]
            chunk.metadata["chunk_id"] = f"{chunk.metadata.get('integration', 'unknown')}_{content_hash}"
        
        return chunks
    
    def _get_docs_hash(self) -> str:
        """Get a hash of all document contents for change detection."""
        content = ""
        for doc_path in sorted(API_DOCS_DIR.glob("**/*.md")):
            content += doc_path.read_text()
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def initialize(self, force_rebuild: bool = False) -> int:
        """Initialize the vector store by loading and indexing documents.
        
        Args:
            force_rebuild: If True, rebuild even if index exists
            
        Returns:
            Number of chunks indexed
        """
        import shutil
        
        # Check if we need to rebuild
        persist_path = self.persist_directory
        hash_file = persist_path / ".docs_hash"
        current_hash = self._get_docs_hash()
        
        if not force_rebuild and persist_path.exists() and hash_file.exists():
            stored_hash = hash_file.read_text().strip()
            if stored_hash == current_hash:
                # Load existing index
                self._vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(persist_path),
                )
                return self._vectorstore._collection.count()
        
        # Force rebuild: clear existing data
        if force_rebuild and persist_path.exists():
            # Remove all files except .gitkeep
            for item in persist_path.iterdir():
                if item.name != ".gitkeep":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
        
        # Load and process documents
        documents = self._load_documents()
        chunks = self._chunk_documents(documents)
        
        # Create vector store
        self._vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=str(persist_path),
        )
        
        # Store hash for change detection
        persist_path.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(current_hash)
        
        return len(chunks)
    
    def search(
        self,
        query: str,
        k: int = 4,
        filter_integration: Optional[str] = None,
    ) -> list[Document]:
        """Search for relevant document chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_integration: Optional filter by integration name
            
        Returns:
            List of relevant Document objects
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        # Build filter if specified
        where_filter = None
        if filter_integration:
            where_filter = {"integration": filter_integration}
        
        results = self._vectorstore.similarity_search(
            query,
            k=k,
            filter=where_filter,
        )
        
        return results
    
    def search_with_scores(
        self,
        query: str,
        k: int = 4,
        filter_integration: Optional[str] = None,
    ) -> list[tuple[Document, float]]:
        """Search for relevant document chunks with similarity scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_integration: Optional filter by integration name
            
        Returns:
            List of (Document, score) tuples
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        where_filter = None
        if filter_integration:
            where_filter = {"integration": filter_integration}
        
        results = self._vectorstore.similarity_search_with_score(
            query,
            k=k,
            filter=where_filter,
        )
        
        return results
    
    def get_retriever(self, k: int = 4):
        """Get a LangChain retriever for use in chains.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            LangChain retriever object
        """
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        return self._vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        if self._vectorstore is None:
            return {"initialized": False}
        
        return {
            "initialized": True,
            "collection_name": self.collection_name,
            "total_chunks": self._vectorstore._collection.count(),
            "persist_directory": str(self.persist_directory),
            "docs_hash": self._get_docs_hash(),
        }


# Module-level instance for easy access
_default_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the default vector store instance."""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store


def initialize_vector_store(force_rebuild: bool = False) -> int:
    """Initialize the default vector store.
    
    Args:
        force_rebuild: If True, rebuild even if index exists
        
    Returns:
        Number of chunks indexed
    """
    store = get_vector_store()
    return store.initialize(force_rebuild=force_rebuild)


def search_docs(
    query: str,
    k: int = 4,
    filter_integration: Optional[str] = None,
) -> list[Document]:
    """Search the default vector store.
    
    Args:
        query: Search query
        k: Number of results to return
        filter_integration: Optional filter by integration name
        
    Returns:
        List of relevant Document objects
    """
    store = get_vector_store()
    return store.search(query, k=k, filter_integration=filter_integration)
