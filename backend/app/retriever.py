import json
import os
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

# Load policies
with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'policies.json'), 'r') as f:
    policies = json.load(f)

# Define stopword list
stopwords = set(["the", "is", "a", "an", "to", "for", "of", "and", "in", "on", "at", "with", "can", "i", "are", "be", "after", "what", "how", "do"])

# Define synonym dictionary
synonym_dict = {
    "challenge my results": "re-evaluation",
    "contest results": "re-evaluation",
    "paper reassessment": "re-evaluation",
    "marks correction": "re-evaluation",
    "dispute marks": "re-evaluation",
    "practical exposure": "internship",
    "industrial exposure": "internship",
    "degree withheld": "internship incomplete",
    "monetary reward": "scholarship",
    "merit incentive": "scholarship",
    "class presence": "attendance",
    "attendance shortage": "attendance below 75%",
    "rechecking": "re-evaluation",
    "recheck": "re-evaluation",
    "training": "internship",
    "industrial": "internship",
    "financial": "scholarship",
    "aid": "scholarship",
    "graduate": "graduation",
    "degree": "graduation",
    "dispute my exam results": "re-evaluation",
    "dispute exam results": "re-evaluation",
    "challenge exam results": "re-evaluation",
    "review my exam results": "re-evaluation",
    "apply for scrutiny": "re-evaluation",
    "dispute": "re-evaluation",
    "contest": "re-evaluation",
    "reassess": "re-evaluation",
    "scrutiny": "re-evaluation",
    "re-evaluate": "re-evaluation"
}

# Sort synonym keys by length descending
sorted_synonyms = sorted(synonym_dict.keys(), key=len, reverse=True)

def retrieve_clauses_by_topic(topic: str) -> List[Dict]:
    """
    Retrieves clauses based on a specific topic ID (hard routing).
    Filters policies where the title contains the topic keyword.
    """
    # Map topic IDs to title keywords
    topic_keyword_map = {
        "attendance": "Attendance",
        "scholarship": "Scholarship",
        "internship": "Internship",
        "reevaluation": "Re-evaluation"
    }

    target_keyword = topic_keyword_map.get(topic)
    results = []
    
    if not target_keyword:
        return results

    for policy in policies:
        # Check if policy title contains the keyword
        if target_keyword.lower() in policy["title"].lower():
            for clause in policy["clauses"]:
                results.append({
                    "policyTitle": policy["title"],
                    "clauseId": clause["clauseId"],
                    "clauseText": clause["text"]
                })
    
    return results


category_keywords = {
    "attendance": "attendance-policy",
    "present": "attendance-policy",
    "absent": "attendance-policy",
    "exam": "examination-eligibility",
    "examination": "examination-eligibility",
    "eligibility": "examination-eligibility",
    "re-evaluation": "re-evaluation-rules",
    "recheck": "re-evaluation-rules",
    "scholarship": "scholarship-policy",
    "financial": "scholarship-policy",
    "aid": "scholarship-policy",
    "internship": "internship-requirement",
    "training": "internship-requirement",
    "industrial": "internship-requirement",
    "hostel": "hostel-regulations",
    "accommodation": "hostel-regulations",
    "residence": "hostel-regulations"
}

# Define category synonyms for boost logic
category_synonyms = {
    "internship": ["training", "industrial training", "summer training", "practical exposure", "degree withheld", "internship", "internship incomplete", "incomplete internship"],
    "evaluation": ["re-evaluation", "recheck", "scrutiny", "contest results", "dispute marks", "paper reassessment", "dispute", "contest", "reassess", "reassessment", "review", "exam results", "result", "results", "marks"],
    "scholarship": ["funding", "monetary reward", "financial support", "merit incentive"],
    "attendance": ["low attendance", "attendance shortage", "class presence", "below 75%", "attendance"]
}

# Define intent keywords for category detection
intent_keywords = {
    "evaluation": ["dispute", "contest", "reassess", "reassessment", "scrutiny", "recheck", "rechecking", "review", "reevaluate", "re-evaluate", "reevaluation", "re-evaluation"],
    "scholarship": ["scholarship", "funding", "financial", "support", "monetary", "reward", "aid"],
    "attendance": ["attendance", "present", "presence", "absent", "shortage", "condone", "condonation", "relaxation"],
    "internship": ["internship", "training", "industrial", "practical", "exposure", "summer"]
}

# Map categories to policy titles for boost
category_to_title = {
    "internship": "Internship Requirement",
    "evaluation": "Re-evaluation Rules",
    "scholarship": "Scholarship Policy",
    "attendance": "Attendance Policy"
}

@dataclass
class RetrievedClause:
    policyId: str
    policyTitle: str
    clauseId: str
    clauseText: str
    score: int
    normalizedScore: float

def normalize_query(question: str) -> Tuple[str, Set[str]]:
    original_tokens = process_text(question)
    detected_categories = set()

    # Intent detection from original tokens
    for token in original_tokens:
        for category, keywords in intent_keywords.items():
            if token in keywords:
                detected_categories.add(category)

    normalized_query = question.lower()

    for syn in sorted_synonyms:
        canon = synonym_dict[syn]
        # Check if synonym is present before replacement
        if syn in normalized_query:
            # Check which category this synonym belongs to
            for category, synonyms in category_synonyms.items():
                if syn in synonyms:
                    detected_categories.add(category)
        normalized_query = normalized_query.replace(syn, canon)

    # Canonical keyword-based detection after synonym replacement
    if "re-evaluation" in normalized_query:
        detected_categories.add("evaluation")
    if "internship" in normalized_query:
        detected_categories.add("internship")
    if "attendance" in normalized_query:
        detected_categories.add("attendance")
    if "scholarship" in normalized_query:
        detected_categories.add("scholarship")

    # Special conditional replacement for attendance 70%
    if "attendance" in question.lower() and "70" in normalized_query:
        normalized_query += " below 75%"

    return normalized_query, detected_categories

def process_text(text: str) -> List[str]:
    words = text.lower().split()
    processed = []
    for word in words:
        word = ''.join(c for c in word if c.isalnum() or c == '%')
        if word.endswith('s') and len(word) > 3:
            word = word[:-1]
        if word.endswith('%'):
            word = word[:-1]
        if len(word) >= 3 and word not in stopwords:
            processed.append(word)
    return processed

# Flatten clauses into searchable items
clauses = []
for policy in policies:
    for clause in policy['clauses']:
        if clause.get('text') and isinstance(clause['text'], str):
            clauses.append({
                'policyId': policy['id'],
                'policyTitle': policy['title'],
                'clauseId': clause['clauseId'],
                'clauseText': clause['text']
            })

def retrieve_relevant_clauses(question: str, top_k: int = 3, debug: bool = False) -> List[Dict]:
    normalized_query, detected_categories = normalize_query(question)

    # Compute detected_policies using category_keywords word-scan
    detected_policies = set()
    words = process_text(normalized_query)
    for word in words:
        if word in category_keywords:
            detected_policies.add(category_keywords[word])

    # PLUS substring scan for canonical keywords
    if "re-evaluation" in normalized_query:
        detected_policies.add("re-evaluation-rules")
    if "internship" in normalized_query:
        detected_policies.add("internship-requirement")
    if "attendance" in normalized_query:
        detected_policies.add("attendance-policy")
    if "scholarship" in normalized_query:
        detected_policies.add("scholarship-policy")

    # Force-add based on detected_categories
    if "evaluation" in detected_categories:
        detected_policies.add("re-evaluation-rules")
    if "internship" in detected_categories:
        detected_policies.add("internship-requirement")
    if "attendance" in detected_categories:
        detected_policies.add("attendance-policy")
    if "scholarship" in detected_categories:
        detected_policies.add("scholarship-policy")

    question_words = set(process_text(normalized_query))

    if not question_words:
        if debug:
            return {
                'clauses': [],
                'debug': {
                    'originalQuestion': question,
                    'normalizedQuery': normalized_query,
                    'detectedCategories': list(detected_categories),
                    'detectedPolicies': list(detected_policies),
                    'questionWords': list(question_words),
                    'threshold': 0,
                    'decisionPath': 'REJECTED',
                    'topScoresPreview': []
                }
            }
        return []

    if len(detected_policies) >= 2:
        # Special rule: for attendance queries, don't mix with exam eligibility unless query mentions probation/counseling
        if 'attendance-policy' in detected_policies and 'examination-eligibility' in detected_policies:
            has_probation_keywords = 'probation' in normalized_query or 'counseling' in normalized_query or 'additional criteria' in normalized_query
            if not has_probation_keywords:
                detected_policies.discard('examination-eligibility')
        # Return top 1 clause per detected policy, ranked by overlap
        result = []
        top_scores = []
        for policy_id in detected_policies:
            policy = next((p for p in policies if p['id'] == policy_id), None)
            if policy and policy['clauses']:
                # Filter clauses with valid text
                valid_clauses = [c for c in policy['clauses'] if c.get('text') and isinstance(c['text'], str)]
                if valid_clauses:
                    # Score clauses in this policy
                    scored = []
                    for clause in valid_clauses:
                        normalized_clause_text = clause['text'].lower()
                        for syn in sorted_synonyms:
                            canon = synonym_dict[syn]
                            normalized_clause_text = normalized_clause_text.replace(syn, canon)
                        clause_words = set(process_text(normalized_clause_text))
                        score = sum(1 for word in question_words if word in clause_words)
                        scored.append({**clause, 'score': score})
                    # Pick the best clause
                    best_clause = max(scored, key=lambda c: c['score'])
                    result.append(RetrievedClause(
                        policyId=policy['id'],
                        policyTitle=policy['title'],
                        clauseId=best_clause['clauseId'],
                        clauseText=best_clause['text'],
                        score=best_clause['score'],
                        normalizedScore=best_clause['score'] / len(question_words) if question_words else 0
                    ))
                    top_scores.append({
                        'policyTitle': policy['title'],
                        'clauseId': best_clause['clauseId'],
                        'score': best_clause['score'],
                        'normalizedScore': best_clause['score'] / len(question_words) if question_words else 0
                    })
        if debug:
            return {
                'clauses': [c.__dict__ for c in result],
                'debug': {
                    'originalQuestion': question,
                    'normalizedQuery': normalized_query,
                    'detectedCategories': list(detected_categories),
                    'detectedPolicies': list(detected_policies),
                    'questionWords': list(question_words),
                    'threshold': 0,
                    'decisionPath': 'MULTI_POLICY',
                    'topScoresPreview': top_scores
                }
            }
        return [c.__dict__ for c in result]

    if len(detected_policies) == 1:
        # Hard-route to that policy
        policy_id = list(detected_policies)[0]
        policy = next((p for p in policies if p['id'] == policy_id), None)
        if policy and policy['clauses']:
            # Filter clauses with valid text
            valid_clauses = [c for c in policy['clauses'] if c.get('text') and isinstance(c['text'], str)]
            if valid_clauses:
                # Score all clauses
                scored = []
                for clause in valid_clauses:
                    normalized_clause_text = clause['text'].lower()
                    for syn in sorted_synonyms:
                        canon = synonym_dict[syn]
                        normalized_clause_text = normalized_clause_text.replace(syn, canon)
                    clause_words = set(process_text(normalized_clause_text))
                    score = sum(1 for word in question_words if word in clause_words)
                    scored.append({**clause, 'score': score})
                # Sort by score desc, take topK with score > 0
                relevant = [c for c in scored if c['score'] > 0]
                relevant.sort(key=lambda c: c['score'], reverse=True)
                relevant = relevant[:top_k]
                result = []
                for c in relevant:
                    result.append(RetrievedClause(
                        policyId=policy['id'],
                        policyTitle=policy['title'],
                        clauseId=c['clauseId'],
                        clauseText=c['text'],
                        score=c['score'],
                        normalizedScore=c['score'] / len(question_words) if question_words else 0
                    ))
                top_scores = [{'policyTitle': c.policyTitle, 'clauseId': c.clauseId, 'score': c.score, 'normalizedScore': c.normalizedScore} for c in result[:3]]
                if not relevant:
                    # For hostel policy, require specific keywords to avoid random returns
                    if policy_id == 'hostel-regulations':
                        hostel_keywords = ['paint', 'repaint', 'wall', 'decoration', 'furniture', 'room', 'clean', 'maintenance', 'alcohol', 'tobacco', 'visitors', 'curfew', 'allocation']
                        has_hostel_keyword = any(kw in normalized_query for kw in hostel_keywords)
                        if not has_hostel_keyword:
                            # No relevant hostel keywords, reject
                            if debug:
                                return {
                                    'clauses': [],
                                    'debug': {
                                        'originalQuestion': question,
                                        'normalizedQuery': normalized_query,
                                        'detectedCategories': list(detected_categories),
                                        'detectedPolicies': list(detected_policies),
                                        'questionWords': list(question_words),
                                        'threshold': 0,
                                        'decisionPath': 'HOSTEL_REJECTED',
                                        'topScoresPreview': []
                                    }
                                }
                            return []
                    # Fallback to first clause
                    result = [RetrievedClause(
                        policyId=policy['id'],
                        policyTitle=policy['title'],
                        clauseId=valid_clauses[0]['clauseId'],
                        clauseText=valid_clauses[0]['text'],
                        score=0,
                        normalizedScore=0
                    )]
                    top_scores.append({
                        'policyTitle': policy['title'],
                        'clauseId': valid_clauses[0]['clauseId'],
                        'score': 0,
                        'normalizedScore': 0
                    })
                if debug:
                    return {
                        'clauses': [c.__dict__ for c in result],
                        'debug': {
                            'originalQuestion': question,
                            'normalizedQuery': normalized_query,
                            'detectedCategories': list(detected_categories),
                            'detectedPolicies': list(detected_policies),
                            'questionWords': list(question_words),
                            'threshold': 0,
                            'decisionPath': 'SINGLE_POLICY',
                            'topScoresPreview': top_scores
                        }
                    }
                # Special check for hostel: if low relevance, reject
                if policy_id == 'hostel-regulations' and result and max(c.normalizedScore for c in result) < 0.3:
                    return []
                return [c.__dict__ for c in result]

    # Fallback: detected_policies.size === 0, use global scoring
    question_word_count = len(question_words)
    threshold = 0.25 if detected_categories else 0.4
    scored_clauses = []
    for clause in clauses:
        # Normalize clause text
        normalized_clause_text = clause['clauseText'].lower()
        for syn in sorted_synonyms:
            canon = synonym_dict[syn]
            normalized_clause_text = normalized_clause_text.replace(syn, canon)
        clause_words = set(process_text(normalized_clause_text))
        score = sum(1 for word in question_words if word in clause_words)
        normalized_score = score / question_word_count
        scored_clauses.append({**clause, 'score': score, 'normalizedScore': normalized_score})

    highest_normalized_score = max((c['normalizedScore'] for c in scored_clauses), default=0)

    # Group clauses by policyTitle
    policy_groups = {}
    for clause in scored_clauses:
        title = clause['policyTitle']
        if title not in policy_groups:
            policy_groups[title] = {'totalScore': 0, 'clauses': []}
        policy_groups[title]['totalScore'] += clause['score']
        policy_groups[title]['clauses'].append(clause)

    # Apply boost if policyTitle contains meaningful words from question
    for title, data in policy_groups.items():
        normalized_title = title.lower()
        for syn in sorted_synonyms:
            canon = synonym_dict[syn]
            normalized_title = normalized_title.replace(syn, canon)
        title_words = set(process_text(normalized_title))
        has_match = any(word in title_words for word in question_words)
        if has_match:
            data['totalScore'] += 2

        # Category boost
        if (title == "Internship Requirement" and "internship" in detected_categories) or \
           (title == "Re-evaluation Rules" and "evaluation" in detected_categories) or \
           (title == "Scholarship Policy" and "scholarship" in detected_categories) or \
           (title == "Attendance Policy" and "attendance" in detected_categories):
            data['totalScore'] += 0.35

        # Policy focus penalty: for attendance queries, penalize non-attendance policies
        if "attendance" in detected_categories and title != "Attendance Policy":
            data['totalScore'] -= 2

    # Identify bestPolicy with highest totalScore
    best_policy = None
    max_score = -1
    for title, data in policy_groups.items():
        if data['totalScore'] > max_score:
            max_score = data['totalScore']
            best_policy = data

    # Force policy selection if exactly 1 category detected
    if len(detected_categories) == 1:
        forced_policy_title = category_to_title.get(list(detected_categories)[0])
        if forced_policy_title and forced_policy_title in policy_groups:
            best_policy = policy_groups[forced_policy_title]
            max_score = best_policy['totalScore']

    # Reject if no category detected and score too low
    if not detected_categories and highest_normalized_score < 0.15:
        if debug:
            return {
                'clauses': [],
                'debug': {
                    'originalQuestion': question,
                    'normalizedQuery': normalized_query,
                    'detectedCategories': list(detected_categories),
                    'detectedPolicies': list(detected_policies),
                    'questionWords': list(question_words),
                    'threshold': threshold,
                    'decisionPath': 'REJECTED',
                    'topScoresPreview': []
                }
            }
        return []

    # From bestPolicy clauses: filter normalizedScore > threshold, sort descending by normalizedScore, take topK
    relevant_clauses = [c for c in best_policy['clauses'] if c['normalizedScore'] > threshold]
    relevant_clauses.sort(key=lambda c: c['normalizedScore'], reverse=True)
    relevant_clauses = relevant_clauses[:top_k]

    # If no clauses above threshold and category detected, include the best clause anyway
    if not relevant_clauses and detected_categories:
        best_clause = max(best_policy['clauses'], key=lambda c: c['normalizedScore'])
        relevant_clauses = [best_clause]

    result = []
    for c in relevant_clauses:
        result.append(RetrievedClause(
            policyId=c['policyId'],
            policyTitle=c['policyTitle'],
            clauseId=c['clauseId'],
            clauseText=c['clauseText'],
            score=c['score'],
            normalizedScore=c['normalizedScore']
        ))

    top_scores = [{'policyTitle': c.policyTitle, 'clauseId': c.clauseId, 'score': c.score, 'normalizedScore': c.normalizedScore} for c in result[:3]]

    if debug:
        return {
            'clauses': [c.__dict__ for c in result],
            'debug': {
                'originalQuestion': question,
                'normalizedQuery': normalized_query,
                'detectedCategories': list(detected_categories),
                'detectedPolicies': list(detected_policies),
                'questionWords': list(question_words),
                'threshold': threshold,
                'decisionPath': 'GLOBAL_FALLBACK',
                'topScoresPreview': top_scores
            }
        }
    return [c.__dict__ for c in result]