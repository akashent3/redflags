"""Risk scoring engine - combines API and Gemini flag results into a final score."""

from typing import Dict, List

# Category weights (must sum to 100)
CATEGORY_WEIGHTS = {
    "Auditor": 20,
    "Cash Flow": 18,
    "Related Party": 15,
    "Promoter": 15,
    "Governance": 12,
    "Balance Sheet": 10,
    "Revenue": 5,
    "Textual": 5,
}

# Severity point values
SEVERITY_POINTS = {
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 3,
}

# Maximum possible points per category (used for normalization)
MAX_CATEGORY_POINTS = {
    "Auditor": 6,       # 6 flags
    "Cash Flow": 8,     # 8 flags
    "Related Party": 7, # 7 flags
    "Promoter": 6,      # 6 flags
    "Governance": 4,    # 4 flags
    "Balance Sheet": 7, # 7 flags
    "Revenue": 3,       # 3 flags
    "Textual": 1,       # 1 flag
}


def calculate_risk_score(all_flags: List[Dict]) -> Dict:
    """Calculate weighted risk score from all 42 flag results.

    Returns:
        Dict with overall score (0-100), category scores, risk level, and details.
    """
    # Group flags by category
    category_flags = {}
    for flag in all_flags:
        cat = flag.get("category", "Unknown")
        if cat not in category_flags:
            category_flags[cat] = []
        category_flags[cat].append(flag)

    # Calculate category scores
    category_scores = {}
    total_weighted_score = 0

    for cat, weight in CATEGORY_WEIGHTS.items():
        flags_in_cat = category_flags.get(cat, [])
        triggered_flags = [f for f in flags_in_cat if f.get("triggered", False)]

        # Calculate raw points for this category
        raw_points = 0
        max_possible = 0
        for f in flags_in_cat:
            severity = f.get("severity", "MEDIUM")
            points = SEVERITY_POINTS.get(severity, 8)
            max_possible += points
            if f.get("triggered", False):
                confidence = f.get("confidence", 50) / 100
                raw_points += points * confidence

        # Normalize to 0-100 for this category
        cat_score = (raw_points / max_possible * 100) if max_possible > 0 else 0
        cat_score = min(cat_score, 100)

        category_scores[cat] = {
            "score": round(cat_score, 1),
            "weight": weight,
            "triggered_count": len(triggered_flags),
            "total_flags": len(flags_in_cat),
            "weighted_contribution": round(cat_score * weight / 100, 1),
        }

        total_weighted_score += cat_score * weight / 100

    # Overall risk score (0-100)
    overall_score = round(min(total_weighted_score, 100), 1)

    # Determine risk level
    if overall_score >= 60:
        risk_level = "CRITICAL"
        risk_color = "#dc2626"
        risk_description = "Very high risk - multiple serious red flags detected"
    elif overall_score >= 40:
        risk_level = "HIGH"
        risk_color = "#ea580c"
        risk_description = "High risk - several concerning red flags detected"
    elif overall_score >= 20:
        risk_level = "MEDIUM"
        risk_color = "#ca8a04"
        risk_description = "Moderate risk - some red flags need attention"
    elif overall_score >= 5:
        risk_level = "LOW"
        risk_color = "#16a34a"
        risk_description = "Low risk - minor concerns only"
    else:
        risk_level = "CLEAN"
        risk_color = "#059669"
        risk_description = "Very low risk - no significant red flags"

    # Summary stats
    triggered_total = sum(1 for f in all_flags if f.get("triggered", False))
    critical_flags = [f for f in all_flags if f.get("triggered") and f.get("severity") == "CRITICAL"]
    high_flags = [f for f in all_flags if f.get("triggered") and f.get("severity") == "HIGH"]

    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_description": risk_description,
        "category_scores": category_scores,
        "summary": {
            "total_flags_checked": len(all_flags),
            "total_triggered": triggered_total,
            "critical_flags": len(critical_flags),
            "high_flags": len(high_flags),
            "critical_flag_names": [f["flag_name"] for f in critical_flags],
            "high_flag_names": [f["flag_name"] for f in high_flags],
        },
    }
