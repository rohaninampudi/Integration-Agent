"""Configuration and environment variable loading."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
API_DOCS_DIR = DATA_DIR / "api_docs"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DB_DIR = PROJECT_ROOT / "db"
CHROMA_DIR = DB_DIR / "chroma"
RESULTS_DIR = PROJECT_ROOT / "results"

# Ensure directories exist
for dir_path in [API_DOCS_DIR, PROMPTS_DIR, CHROMA_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # Default to GPT-5

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = "api_docs"

# Embedding Configuration
EMBEDDING_MODEL = "text-embedding-3-small"

# Agent Configuration
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "false").lower() == "true"

def validate_config():
    """Validate that required configuration is present."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Please set it in your .env file or environment."
        )
    return True
