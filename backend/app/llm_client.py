from typing import Optional
from app.config import config

class LLMClient:
    def generate_answer(self, question: str, context: str) -> Optional[str]:
        # Stub implementation - return None to use template-based answer
        if not config.LLM_API_KEY:
            return None
        # TODO: Implement actual LLM call
        return None

llm_client = LLMClient()