import os
from typing import Optional, List
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    SCALEDOWN_API_KEY: Optional[str] = os.getenv("SCALEDOWN_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8080"))
    
    # Parse CORS_ORIGINS safely
    _cors = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173"]')
    try:
        CORS_ORIGINS: List[str] = json.loads(_cors)
    except:
        CORS_ORIGINS: List[str] = ["http://localhost:5173"]

config = Config()