from pydantic import BaseModel
from typing import List, Optional, Dict

class AskRequest(BaseModel):
    question: str
    topic: Optional[str] = None

class Source(BaseModel):
    policyTitle: str
    clauseId: str
    text: str

class CompressionInfo(BaseModel):
    used: bool
    original_tokens: int = 0
    compressed_tokens: int = 0
    tokens_saved: int = 0
    latency_ms: int = 0

class AskOption(BaseModel):
    id: str
    label: str

class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Source]
    compression: CompressionInfo
    error: Optional[str] = None
    needs_clarification: Optional[bool] = False
    clarification_question: Optional[str] = None
    clarification_options: Optional[List[AskOption]] = []
    # Legacy field for compatibility if needed, but we'll use clarification_options
    options: Optional[List[str]] = []

class SimulationRequest(BaseModel):
    attendance: float
    cgpa: float
    internship_completed: bool

class SimulationResultDetail(BaseModel):
    status: str
    reason: str

class SimulationResults(BaseModel):
    exam_eligibility: SimulationResultDetail
    merit_scholarship: SimulationResultDetail
    graduation: SimulationResultDetail

class SimulationResponse(BaseModel):
    results: SimulationResults
    confidence: float
    sources: List[Source]

class HealthResponse(BaseModel):
    ok: bool

class MetricsResponse(BaseModel):
    total_requests: int
    total_tokens_saved: int
    avg_latency_ms: float
    avg_compression_ratio: float
    fallback_count: int