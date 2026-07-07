from langchain_ollama import ChatOllama
from typing import Dict, List, Optional, Any
from backend.src.core.config import settings

llm = ChatOllama(
    model=settings.OLLAMA_LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.5,
)