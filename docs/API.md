# API Documentation

## Base URL
`http://localhost:8080`

## Endpoints

### POST /ask
The primary endpoint for all chat interactions. It handles:
1.  **Ambiguity Detection**: Returns `needs_clarification=True` if the query is vague.
2.  **Hard Routing**: If `topic` is provided, skips compression and returns direct policy answers.
3.  **ScaleDown Compression**: If context is retrieved, compresses it before generation.

**Request:**
```json
{
  "question": "Am I eligible?",
  "topic": "attendance" // Optional
}
```

**Response (Standard):**
```json
{
  "answer": "To be eligible for exams, you need 75% attendance.",
  "confidence": 0.9,
  "sources": [...],
  "compression": {
    "used": true,
    "tokens_saved": 150,
    "original_tokens": 500,
    "compressed_tokens": 350
  },
  "needs_clarification": false
}
```

**Response (Ambiguous):**
```json
{
  "answer": "I can help with eligibility, but for which area?",
  "needs_clarification": true,
  "clarification_options": [
    {"id": "attendance", "label": "Attendance"},
    {"id": "scholarship", "label": "Scholarship"}
  ]
}
```

### POST /simulate/eligibility
Deterministic check for numeric rules. No LLM involved.

**Request:**
```json
{
  "attendance": 78.5,
  "cgpa": 8.2,
  "internship_completed": true
}
```

**Response:**
```json
{
  "results": {
    "exam_eligibility": {"status": "yes", "reason": "Attendance is 78.5% (>= 75.0% required)."},
    "merit_scholarship": {"status": "no", "reason": "CGPA is 8.2 (< 8.5 required)."},
    "graduation": {"status": "yes", "reason": "Internship requirement met."}
  }
}
```

### GET /metrics/summary
Returns usage statistics for ScaleDown compression.

**Response:**
```json
{
  "total_requests": 42,
  "total_tokens_saved": 12500,
  "avg_latency_ms": 245.5,
  "avg_compression_ratio": 0.65,
  "fallback_count": 2
}
```
