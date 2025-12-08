import re
from typing import Tuple, Dict

def detect_domain(query: str) -> Tuple[str, float]:
    """
    Domain detection using weighted keyword matching
    Return: main domain, confidence
    """
    query_lower = query.lower()

    # Keywords that would be queried
    weighted_keywords = {
        'holistic' : {
            # High weight - very specific to holistic
            'meditation': 3, 'mindfulness': 3, 'yoga': 3, 'wellness': 3,
            'nutrition': 3, 'diet': 2.5, 'exercise': 2.5, 'sleep': 2.5,
            'stress': 2, 'mental health': 3, 'blood pressure': 3,
            'diabetes': 3, 'chronic': 2, 'healthy eating': 3,
            'fasting': 3, 'intermittent fasting': 3,
            
            # Medium weight - somewhat specific
            'health': 1.5, 'food': 1.5, 'eat': 1, 'meal': 1.5,
            'vitamin': 2, 'supplement': 2, 'fitness': 2,
            'breathing': 2, 'relax': 1.5, 'calm': 1.5,
            
            # Low weight - could be ambiguous
            'body': 0.5, 'weight': 1, 'energy': 1, 'tired': 1,
            'feeling': 0.5, 'better': 0.5
        },
        'financial' : {
            # High weight
            'budget': 3, 'spending': 3, 'expense': 3, 'savings': 3,
            'credit card': 3, 'bank account': 3, 'transaction': 2.5,
            'ombee finance': 5,
            
            # Medium weight  
            'money': 2, 'spend': 2, 'spent': 2, 'cost': 1.5,
            'save': 1.5, 'payment': 2, 'bill': 1.5, 'paid': 1.5,
            'dollar': 2, 'cash': 2, 'debt': 2.5,
            
            # Context-specific
            'restaurant': 1, 'bought': 1, 'purchase': 1.5,
            'balance': 1.5, 'income': 2
        },
        'telecom' : {
            # High weight
            'phone plan': 4, 'data usage': 4, 'mobile plan': 4,
            'ombee wireless': 5, 'carrier': 3, 'cellular': 3,
            
            # Medium weight
            'phone': 2, 'mobile': 2, 'data': 2, 'network': 2,
            'wireless': 2.5, 'signal': 2, 'coverage': 2.5,
            'device': 1.5, 'upgrade': 1.5,
            
            # Low weight (but still relevant)
            'bill': 1, 'plan': 1, 'service': 0.5, 'usage': 1.5,
            'minutes': 1.5, 'text': 1
        }
    }

    # Key phrases that are strong domain indicators
    key_phrases = {
        'holistic' : {
            'blood pressure', 'mental health', 'healthy eating',
            'lose weight', 'gain weight', 'feel better',
            'meditation technique', 'stress management',
            'sleep better', 'improve sleep', 'intermittent fasting', 'fasting'
        },
        'financial' : {
            'how much did i spend', 'spent on', 'my budget',
            'save money', 'credit card', 'bank account',
            'financial plan', 'spending habit'
        },
        'telecom' : {
            'phone plan', 'data usage', 'phone bill',
            'mobile plan', 'data limit', 'wireless plan',
            'ombee wireless', 'my plan', 'current plan'
        }
    }

    BONUS = 5 # Bonus weighting for key phrases
    scores = {'holistic': 0,'financial': 0,'telecom': 0}

    # Score based on keywords
    for domain, keywords in weighted_keywords.items():
        for keyword, weight in keywords.items():
            if keyword in query_lower:
                scores[domain] += weight

    # Bonus score for key phrases
    for domain, phrases in key_phrases.items():
        for phrase in phrases:
            if phrase in query_lower:
                scores[domain] += BONUS

    # If asking about spending money -> likely financial 
    if re.search(r'(spend|spent|cost|paid).*(on|for|at)',query_lower):
        scores['financial'] += 3

    # If asking about eating -> likely holistic
    if re.search(r'(should|can) (i|we) eat',query_lower):
        scores['holistic'] += 3
    
    # If asking about my plan or etc -> likely telecom
    if 'my' in query_lower and any(word in query_lower for word in ['pay','cost','spend']):
        if any(word in query_lower for word in ['wireless','mobile','carrier','network']):
            scores['telecom'] += 2
        elif any(word in query_lower for word in ['spend','spent','cost']):
            scores['financial'] += 2

    # negative indicator of "phone bill" would reduce chance of telecom 
    if 'phone bill' in query_lower and any(word in query_lower for word in ['pay','cost','spend']):
        scores['financial'] +=2
        scores['telecom'] -= 1

    # If no matches then default to holistic
    if all(score == 0 for score in scores.values()):
        return 'holistic', 0.70
    
    best_domain = max(scores,key=scores.get)
    max_score = scores[best_domain]
    total_score = sum(scores.values())

    # Calculate confidence
    if total_score > 0:
        dominance = max_score / total_score
    else: 
        dominance = 0.33 # Equal split
    
    confidence = 0.70 + (dominance * 0.20)

    # Boost confidence if score is very high
    if max_score >= 10:
        confidence += 0.05
    if max_score >= 15:
        confidence += 0.05

    confidence = min(0.95,confidence)

    return best_domain, confidence

def explain_routing(query: str) -> Dict:
    """
    Function to show why a query was routed to a specific domain
    Return: rationale
    """
    domain, confidence = detect_domain(query)

    return {
        'query': query,
        'domain': domain,
        'confidence': confidence,
        'explanation': f"routed to {domain} with {confidence:.0%} confidence."
    }