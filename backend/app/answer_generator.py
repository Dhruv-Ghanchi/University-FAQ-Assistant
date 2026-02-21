from typing import List, Dict, Optional
from app.llm_client import llm_client

def generate_answer(question: str, retrieved_sources: List[Dict], compressed_prompt: Optional[str] = None, numeric_answer: Optional[str] = None) -> tuple[str, float]:
    if not retrieved_sources:
        return "I'm sorry, I don't have information about that topic in the university policies.", 0.0

    if numeric_answer:
        # If we have a deterministic numeric answer, return it directly.
        # The sources are already returned in the API response for the UI to show.
        return numeric_answer, 1.0

    # If LLM is available, use it (stub for now)
    llm_answer = llm_client.generate_answer(question, compressed_prompt or "\n".join([s['clauseText'] for s in retrieved_sources]))
    if llm_answer:
        confidence = 0.9 if len(retrieved_sources) >= 2 else 0.7
        return llm_answer, confidence

    # Template-based answer
    if len(retrieved_sources) == 1:
        answer = retrieved_sources[0]['clauseText']
        confidence = 0.8
    else:
        # Combine top clauses
        answer = "\n\n".join([s['clauseText'] for s in retrieved_sources])
        confidence = 0.85

    return answer, confidence