# University FAQ Assistant

A production-quality FastAPI backend for answering university policy questions using retrieval-augmented generation with ScaleDown compression.

## Problem Statement

Students often struggle to find answers to policy-related questions buried in lengthy university documents. This system provides instant, accurate answers by retrieving relevant policy clauses and compressing context for efficient LLM processing.

## Architecture

```
User Query → Retriever → ScaleDown Compression → Answer Generator → Response
     ↓           ↓              ↓                    ↓
  Question   Relevant Clauses  Compressed Context   Plain English Answer
```

### Retriever Logic
- **Normalization**: Lowercase, synonym replacement (e.g., "dispute" → "re-evaluation")
- **Category Detection**: Intent keywords detect categories (attendance, evaluation, scholarship, internship)
- **Policy Hard-routing**: Single category → direct policy selection
- **Scoring**: Word overlap with synonym-normalized text
- **Boosting**: Category matches and title keyword matches increase relevance

### ScaleDown Integration
- Compresses retrieved policy context before LLM processing
- Reduces token usage while maintaining answer quality
- Fallback to uncompressed context if compression fails

## How to Run Backend (Python)

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
SCALEDOWN_API_KEY=your_key_here
MODEL_NAME=gpt-4o
LLM_API_KEY=optional_llm_key
```

### Run Server
```bash
# Option 1: Using the convenience script (recommended)
python start_server.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload

# Option 3: Using run.py
python run.py
```

Server will be available at: http://127.0.0.1:8001
API docs at: http://127.0.0.1:8001/docs

## How to Run Frontend (Optional)

The Node.js/React frontend is in the `client/` directory. Refer to its README for setup.

## API Documentation

### GET /health
Returns `{"ok": true}`

### POST /ask
Accepts: `{"question": "string"}`

Returns:
```json
{
  "answer": "Plain English answer without policy references",
  "confidence": 0.85,
  "sources": [
    {
      "policyTitle": "Attendance Policy",
      "clauseId": "att-1",
      "text": "Full clause text..."
    }
  ],
  "compression": {
    "used": true,
    "original_tokens": 150,
    "compressed_tokens": 75,
    "tokens_saved": 75,
    "latency_ms": 250
  }
}
```

### GET /metrics
Returns compression analytics:
```json
{
  "total_calls": 42,
  "total_tokens_saved": 1200,
  "avg_latency_ms": 180,
  "avg_compression_ratio": 0.6
}
```

## Example API Request/Response

Request:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What happens if my attendance is 70%?"}'
```

Response:
```json
{
  "answer": "Students with attendance below 75% may be denied permission to sit for final examinations and will be required to repeat the course.",
  "confidence": 0.9,
  "sources": [
    {
      "policyTitle": "Attendance Policy",
      "clauseId": "att-3",
      "text": "Students with attendance below 75% may be denied permission to sit for the final examinations. In such cases, they will be required to repeat the course in the subsequent semester."
    }
  ],
  "compression": {
    "used": true,
    "original_tokens": 45,
    "compressed_tokens": 28,
    "tokens_saved": 17,
    "latency_ms": 150
  }
}
```

## Metrics Screenshot

After running test queries, check ScaleDown dashboard for:
- Total Calls: > 0
- Tokens Saved: > 0
- Compression Ratio: < 1.0

## Unique Feature: Compression Analytics Panel

Real-time compression analytics with token/cost savings tracking and fail-safe fallback to uncompressed mode. The `/metrics` endpoint provides:
- `original_tokens`: Tokens in uncompressed context
- `compressed_tokens`: Tokens after ScaleDown compression
- `tokens_saved`: Difference (cost savings)
- `compression_ratio`: compressed/original
- `latency_ms`: Compression processing time
- `estimated_cost_savings`: Calculated based on model pricing

## Running the Backend

Ensure you have Python 3.10+ installed.

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Feature Verification (Checklist)

### 1. Smart Disambiguation
- [ ] Ambiguous Query: "Am I eligible?" -> Returns JSON with clarification options.
- [ ] Topic Selection: User clicks "Attendance" -> Logic bypasses ambiguity check -> specific policy retrieval.
- [ ] Passing Criteria: Verify "passing criteria" option is NOT present in ambiguous response unless relevant (removed).

### 2. Eligibility Simulation (New)
- [ ] API Endpoint: POST /simulate/eligibility -> Returns deterministic result.
- [ ] Logic Check: Attendance 74.9 -> "no". Attendance 75.0 -> "yes".
- [ ] Logic Check: CGPA 8.49 -> "no". CGPA 8.5 -> "yes".
- [ ] Logic Check: Internship Completed false -> "warning".

## Testing

Run tests:
```bash
cd backend
pytest
```

Tests cover:
- Retriever accuracy for policy-specific queries
- API response schemas
- Compression integration
- Irrelevant query rejection