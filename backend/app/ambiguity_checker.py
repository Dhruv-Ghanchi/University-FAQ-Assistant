import re

# AMBIGUITY CONFIGURATION
MEANINGFUL_TOKEN_THRESHOLD = 6

# Topic Keywords (Must be lowercase)
TOPIC_KEYWORDS = {
    # Attendance
    "attendance", "present", "absent", "medical", "leave", "condonation", "shortage", "percent", "%",
    # Scholarship
    "scholarship", "cgpa", "merit", "need-based", "financial", "aid", "funding", "reward", "sports",
    # Internship
    "internship", "training", "industrial", "summer", "practical", "certificate", "graduation", "degree",
    # Re-evaluation
    "re-evaluation", "reevaluation", "scrutiny", "recheck", "rechecking", "reassessment", "dispute", "contest", "marks", "result", "results",
    # Exam
    "exam", "exams", "examination", "eligibility", "finals", "semester"
}

# Ambiguous Intent Patterns (Normalized)
AMBIGUOUS_PATTERNS = [
    "am i eligible",
    "can i apply",
    "is it allowed",
    "is this valid",
    "how does it work",
    "tell me the rule",
    "what are the requirements",
    "what should i do",
    "can i get it"
]

STOP_WORDS = {
    "the", "a", "an", "is", "are", "of", "to", "in", "for", "on", "with", "at", "by",
    "i", "am", "can", "what", "how", "do", "does", "it", "this", "tell", "me", "should", "get"
}

def check_ambiguity(question: str):
    """
    Checks if a question is ambiguous based on token count and content.
    Returns a dict with response if ambiguous, else None.
    """
    cleaned_q = question.lower()
    
    # 1. Normalize for pattern matching (remove punctuation except maybe %?)
    # actually we can just strip non-alphanumeric and spaces
    normalized_text = re.sub(r'[^a-z0-9\s%]', '', cleaned_q).strip() # keep % for attendance
    
    # 2. Tokenize and Counts
    tokens = normalized_text.split()
    meaningful_tokens = [t for t in tokens if t not in STOP_WORDS]
    
    # Check Conditions
    
    # Condition 1: Length check ( < 6 meaningful tokens)
    is_short = len(meaningful_tokens) < MEANINGFUL_TOKEN_THRESHOLD
    
    # Condition 2: Topic Keyword Check
    has_topic = any(keyword in cleaned_q for keyword in TOPIC_KEYWORDS)
    
    # Condition 3: Intent Pattern Match
    # Check if the normalized question contains any of the ambiguous patterns
    matches_pattern = any(pattern in normalized_text for pattern in AMBIGUOUS_PATTERNS)
    
    # Logic: Mark ambiguous if ALL conditions are met?
    
    if is_short and not has_topic and matches_pattern:
        return {
            "answer": "It seems you're asking about eligibility or rules, but I'm not sure for which topic. Could you clarify?",
            "confidence": 0.2, # Low confidence as per requirement
            "sources": [],
            "needs_clarification": True,
            "clarification_question": "Please choose a topic:",
            "clarification_options": [
                {"id": "attendance", "label": "Eligibility for exams (Attendance)"},
                {"id": "scholarship", "label": "Eligibility for scholarships"},
                {"id": "reevaluation", "label": "Re-evaluation / scrutiny"},
                {"id": "internship", "label": "Internship requirements"}
            ],
            "options": [] # Legacy empty list to prevent errors if downstream uses it
        }
    
    return None
