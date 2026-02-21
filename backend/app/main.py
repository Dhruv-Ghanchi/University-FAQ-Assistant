import time
import logging
import uuid
from fastapi import FastAPI
from app.schemas import (
    AskRequest, AskResponse, HealthResponse, MetricsResponse, CompressionInfo,
    SimulationRequest, SimulationResponse, SimulationResults, SimulationResultDetail,
    AskOption
)
from app.retriever import retrieve_relevant_clauses, retrieve_clauses_by_topic
from app.services.scaledown_client import scaledown_client
from app.answer_generator import generate_answer
from app.services.metrics import metrics_service
from app.config import config
from app.ambiguity_checker import check_ambiguity
from app.numeric_reasoning import evaluate_numeric_logic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="University FAQ Assistant", version="1.0.0")

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
async def health():
    return {"ok": True}

@app.post("/simulate/eligibility", response_model=SimulationResponse)
async def simulate_eligibility(request: SimulationRequest):
    # Deterministic logic
    
    # 1. Exam Eligibility: Attendance >= 75.0
    exam_eligible = request.attendance >= 75.0
    exam_status = "yes" if exam_eligible else "no"
    exam_reason = (
        f"Attendance is {request.attendance}% (>= 75.0% required)." 
        if exam_eligible 
        else f"Attendance is {request.attendance}% (< 75.0% required)."
    )
    
    # 2. Merit Scholarship: CGPA >= 8.5
    scholarship_eligible = request.cgpa >= 8.5
    scholarship_status = "yes" if scholarship_eligible else "no"
    scholarship_reason = (
        f"CGPA is {request.cgpa} (>= 8.5 required)." 
        if scholarship_eligible 
        else f"CGPA is {request.cgpa} (< 8.5 required)."
    )

    # 3. Graduation: Internship Completed (Yes/No)
    # The requirement is internship completed -> yes, else warning
    graduation_status = "yes" if request.internship_completed else "warning"
    graduation_reason = (
        "Internship requirement met." 
        if request.internship_completed 
        else "Internship incompletion may delay graduation (mandatory requirement)."
    )

    return SimulationResponse(
        results=SimulationResults(
            exam_eligibility=SimulationResultDetail(status=exam_status, reason=exam_reason),
            merit_scholarship=SimulationResultDetail(status=scholarship_status, reason=scholarship_reason),
            graduation=SimulationResultDetail(status=graduation_status, reason=graduation_reason)
        ),
        confidence=0.95,
        sources=[]
    )

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"Request {request_id}: {request.question} (topic={request.topic})")

    try:
        question = request.question
        
        # 1. Hard Routing (if topic is provided)
        if request.topic:
            logger.info(f"Hard Routing applied for topic: {request.topic}")
            # Skip ambiguity check
            sources_dicts = retrieve_clauses_by_topic(request.topic)
            logger.info(f"Retrieved {len(sources_dicts)} clauses for topic {request.topic}")
            
            # UNIQUE FEATURE FIX: Ensure we only show relevant content for the chosen topic.
            # If multiple clauses exist for one topic code, we might want to be selective, 
            # but usually a topic maps to a specific concern.
            # We already have the correct sources. 
            
            # Generate answer using these specific sources
            answer, confidence = generate_answer(question, sources_dicts)
            
            # Map back to API response format
            response_sources = [
                {"policyTitle": s["policyTitle"], "clauseId": s["clauseId"], "text": s["clauseText"]}
                for s in sources_dicts
            ]
            
            # Metrics (simplified for Hard Routing)
            # We don't compress on hard routing usually, or we can if we want to be fancy.
            # Requirement says "Wire ScaleDown into the main chat pipeline". 
            # To be safe, let's just log zero compression here as it's a direct lookup.
            return AskResponse(
                answer=answer,
                confidence=confidence,
                sources=response_sources,
                compression=CompressionInfo(used=False)
            )

        # 2. Ambiguity Check (only if no topic)
        ambiguity_result = check_ambiguity(question)
        if ambiguity_result:
            return AskResponse(
                answer=ambiguity_result["answer"],
                confidence=ambiguity_result["confidence"],
                sources=ambiguity_result["sources"],
                needs_clarification=ambiguity_result["needs_clarification"],
                clarification_question=ambiguity_result.get("clarification_question"),
                clarification_options=[AskOption(**opt) for opt in ambiguity_result.get("clarification_options", [])],
                options=ambiguity_result.get("options", []), # Legacy
                compression=CompressionInfo(used=False)
            )

        # 3. Retrieve relevant clauses (Standard Flow)
        sources_dicts = retrieve_relevant_clauses(question, top_k=3)

        # Numeric Logic check
        numeric_answer = evaluate_numeric_logic(question)

        # Prepare context for compression
        context = "\n".join([s['clauseText'] for s in sources_dicts]) if sources_dicts else ""
        
        # SCALEDOWN INTEGRATION
        # Compress the context before sending to LLM (or answer generator)
        compression_data = scaledown_client.compress_prompt(context, question)
        
        # Log metrics
        metrics_service.log_request(
            original_tokens=compression_data["original_tokens"],
            compressed_tokens=compression_data["compressed_tokens"],
            latency_ms=compression_data["latency_ms"],
            fallback=compression_data["fallback"]
        )

        compressed_prompt = compression_data["compressed_prompt"]
        
        # Generate answer using COMPRESSED context
        answer, confidence = generate_answer(question, sources_dicts, compressed_prompt=compressed_prompt, numeric_answer=numeric_answer)

        # Prepare response
        response_sources = [
            {
                "policyTitle": s["policyTitle"],
                "clauseId": s["clauseId"],
                "text": s["clauseText"]
            } for s in sources_dicts
        ]

        compression_info = CompressionInfo(
            used=compression_data["successful"],
            original_tokens=compression_data["original_tokens"],
            compressed_tokens=compression_data["compressed_tokens"],
            tokens_saved=max(0, compression_data["original_tokens"] - compression_data["compressed_tokens"]),
            latency_ms=compression_data["latency_ms"]
        )

        logger.info(f"Request {request_id} completed in {time.time() - start_time:.4f}s")

        return AskResponse(
            answer=answer,
            confidence=confidence,
            sources=response_sources,
            compression=compression_info
        )

    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}", exc_info=True)
        return AskResponse(
            answer="Sorry, I encountered an internal error while processing your request.",
            confidence=0.0,
            sources=[],
            compression=CompressionInfo(used=False),
            error="internal_error"
        )

@app.get("/metrics/summary")
async def get_metrics_summary():
    # Helper endpoint for dashboard
    return metrics_service.get_summary()

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    # Legacy endpoint if needed, or redirect to summary logic
    return metrics_service.get_summary()