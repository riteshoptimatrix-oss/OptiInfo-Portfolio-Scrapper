from typing import List, Dict, Any, Tuple

class SignalWeight:
    STRONG = 0.90
    MEDIUM = 0.60
    WEAK = 0.30

def calculate_confidence(signals: List[Tuple[float, str]]) -> Tuple[int, List[str]]:
    """
    Combines weighted detection signals into a normalized confidence percentage (0-100%)
    and extracts evidence string items.
    
    Formula uses independent signal probability combination:
    P_total = 1 - (1 - P1) * (1 - P2) * ...
    """
    if not signals:
        return 0, []

    evidence_list = []
    combined_prob = 1.0

    for weight, evidence_text in signals:
        evidence_list.append(evidence_text)
        combined_prob *= (1.0 - weight)

    final_probability = 1.0 - combined_prob
    confidence_score = min(99, max(30, int(final_probability * 100)))

    return confidence_score, evidence_list
