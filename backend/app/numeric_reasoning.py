import re
from typing import Optional

def evaluate_numeric_logic(question: str) -> Optional[str]:
    """
    Evaluates numeric constraints in the question against policy rules.
    Returns a specific answer string if a rule is triggered, else None.
    Handles strict decimal comparisons for:
    - Attendance (>= 75.0%)
    - CGPA (>= 8.5 for merit)
    - Re-evaluation (<= 15 days)
    """
    q_lower = question.lower()
    
    # 1. Attendance Logic
    # Look for "N%" or "attendance is N"
    # Matches: "75%", "74.9%", "attendance is 75"
    att_match = re.search(r'(\d+(?:\.\d+)?)\s*%|attendance\s+(?:is\s+)?(\d+(?:\.\d+)?)', q_lower)
    
    if att_match:
        # Group 1 (N%) or Group 2 (attendance is N)
        val_str = att_match.group(1) or att_match.group(2)
        if val_str:
            try:
                attendance = float(val_str)
                # Validation: 0-100
                if 0 <= attendance <= 100:
                    if attendance < 75.0:
                        return f"Since your attendance is {attendance}%, you are NOT eligible to sit for exams (minimum 75% required)."
                    else:
                        return f"Since your attendance is {attendance}%, you are eligible to sit for exams."
            except ValueError:
                pass

    # 2. Merit Scholarship Logic (CGPA)
    # Look for "X cgpa" or "cgpa X"
    # Matches: "8.5 cgpa", "cgpa 8.49"
    cgpa_match = re.search(r'(\d+(?:\.\d+)?)\s*cgpa|cgpa\s*(?:is\s+)?(\d+(?:\.\d+)?)', q_lower)
    
    if cgpa_match:
        val_str = cgpa_match.group(1) or cgpa_match.group(2)
        if val_str:
            try:
                cgpa = float(val_str)
                # Validation: 0-10
                if 0 <= cgpa <= 10:
                    if cgpa >= 8.5:
                        return f"With a CGPA of {cgpa}, you are eligible for the merit scholarship (minimum 8.5 required)."
                    else:
                        return f"With a CGPA of {cgpa}, you are NOT eligible for the merit scholarship (minimum 8.5 required)."
            except ValueError:
                pass

    # 3. Re-evaluation Deadline Logic
    # Look for "N days"
    # Matches: "16 days", "0 days", "15 days"
    # Added "re-evaluation" related keywords check to avoid false positives with other "days"
    reeval_keywords = ["re-evaluation", "reevaluation", "recheck", "scrutiny", "challenge", "apply"]
    is_reeval = any(word in q_lower for word in reeval_keywords)
    
    days_match = re.search(r'(\d+)\s*days?', q_lower)
    
    if "same day" in q_lower and is_reeval:
         return "Since you applied on the same day (within the 15-day period), your request is valid."

    if days_match and is_reeval:
        try:
            days = int(days_match.group(1))
            if days > 15:
                # 16+ days -> Invalid
                return f"The application period for re-evaluation is 15 days. Since {days} days have passed, you can no longer apply."
            elif days >= 0:
                # 0-15 days -> Valid
                return f"Since it is within the 15-day period ({days} days), you can apply for re-evaluation."
        except ValueError:
            pass
            
    return None
