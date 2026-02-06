"""Risk Scoring Engine for RedFlag AI.

Aggregates individual red flag results into an overall risk score (0-100)
and provides category-level breakdowns.
"""

import logging
from typing import Dict, List

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagResult

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate composite risk score from red flag results."""

    # Category weights (must sum to 1.0)
    CATEGORY_WEIGHTS = {
        FlagCategory.AUDITOR: 0.20,
        FlagCategory.CASH_FLOW: 0.18,
        FlagCategory.RELATED_PARTY: 0.15,
        FlagCategory.PROMOTER: 0.15,
        FlagCategory.GOVERNANCE: 0.12,
        FlagCategory.BALANCE_SHEET: 0.10,
        FlagCategory.REVENUE: 0.05,
        FlagCategory.TEXTUAL: 0.05,
    }

    # Severity points
    SEVERITY_POINTS = {
        FlagSeverity.CRITICAL: 25,
        FlagSeverity.HIGH: 15,
        FlagSeverity.MEDIUM: 8,
        FlagSeverity.LOW: 3,
    }

    # Flag counts per category (for max points calculation)
    CATEGORY_FLAG_COUNTS = {
        FlagCategory.AUDITOR: 8,
        FlagCategory.CASH_FLOW: 8,
        FlagCategory.RELATED_PARTY: 7,
        FlagCategory.PROMOTER: 6,
        FlagCategory.GOVERNANCE: 7,
        FlagCategory.BALANCE_SHEET: 7,
        FlagCategory.REVENUE: 5,
        FlagCategory.TEXTUAL: 6,
    }

    # Severity distribution per category (for accurate max points)
    CATEGORY_SEVERITY_DISTRIBUTION = {
        FlagCategory.AUDITOR: {
            FlagSeverity.CRITICAL: 3,  # Flags 1, 3, 5
            FlagSeverity.HIGH: 3,  # Flags 2, 4, 6
            FlagSeverity.MEDIUM: 2,  # Flags 7, 8
            FlagSeverity.LOW: 0,
        },
        FlagCategory.CASH_FLOW: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 4,  # Flags 9, 10, 11, 14
            FlagSeverity.MEDIUM: 4,  # Flags 12, 13, 15, 16
            FlagSeverity.LOW: 0,
        },
        FlagCategory.RELATED_PARTY: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 3,  # Flags 17, 18, 22
            FlagSeverity.MEDIUM: 4,  # Flags 19, 20, 21, 23
            FlagSeverity.LOW: 0,
        },
        FlagCategory.PROMOTER: {
            FlagSeverity.CRITICAL: 1,  # Flag 24
            FlagSeverity.HIGH: 2,  # Flags 25, 29
            FlagSeverity.MEDIUM: 2,  # Flags 26, 27
            FlagSeverity.LOW: 1,  # Flag 28
        },
        FlagCategory.GOVERNANCE: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 3,  # Flags 30, 31, 35
            FlagSeverity.MEDIUM: 4,  # Flags 32, 33, 34, 36
            FlagSeverity.LOW: 0,
        },
        FlagCategory.BALANCE_SHEET: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 4,  # Flags 37, 38, 39, 40
            FlagSeverity.MEDIUM: 3,  # Flags 41, 42, 43
            FlagSeverity.LOW: 0,
        },
        FlagCategory.REVENUE: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 1,  # Flag 46
            FlagSeverity.MEDIUM: 3,  # Flags 44, 45, 47
            FlagSeverity.LOW: 1,  # Flag 48
        },
        FlagCategory.TEXTUAL: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 1,  # Flag 53
            FlagSeverity.MEDIUM: 4,  # Flags 49, 51, 52, 54
            FlagSeverity.LOW: 1,  # Flag 50
        },
    }

    def calculate_risk_score(self, flag_results: List[RedFlagResult]) -> Dict:
        """
        Calculate overall risk score from individual flag results.

        Args:
            flag_results: List of RedFlagResult objects from all 54 flags

        Returns:
            Dictionary with:
            - risk_score: Overall risk score (0-100)
            - risk_level: Risk category (LOW/MODERATE/ELEVATED/HIGH/CRITICAL)
            - category_scores: Scores for each category (0-100)
            - flags_triggered_count: Total flags triggered
            - flags_by_severity: Count breakdown by severity
            - top_concerns: List of top triggered flag names
            - category_breakdown: Detailed per-category stats
        """
        logger.info(f"Calculating risk score from {len(flag_results)} flag results")

        # Validate we have all 54 flags
        if len(flag_results) != 54:
            logger.warning(f"Expected 54 flag results, got {len(flag_results)}")

        # Group flags by category
        flags_by_category = self._group_by_category(flag_results)

        # Calculate category scores
        category_scores = {}
        category_breakdown = {}

        for category in FlagCategory:
            category_flags = flags_by_category.get(category, [])
            score, breakdown = self._calculate_category_score(category_flags, category)
            category_scores[category] = score
            category_breakdown[category] = breakdown

        # Calculate weighted overall score
        risk_score = sum(self.CATEGORY_WEIGHTS[cat] * score for cat, score in category_scores.items())

        # Determine risk level
        risk_level = self._get_risk_level(risk_score)

        # Count flags by severity
        flags_by_severity = self._count_by_severity(flag_results)

        # Get top concerns
        top_concerns = self._get_top_concerns(flag_results, limit=10)

        # Calculate additional metrics
        total_triggered = sum(1 for f in flag_results if f.is_triggered)
        trigger_percentage = (total_triggered / 54) * 100

        result = {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "category_scores": {cat.value: round(score, 1) for cat, score in category_scores.items()},
            "flags_triggered_count": total_triggered,
            "flags_total_count": 54,
            "trigger_percentage": round(trigger_percentage, 1),
            "flags_by_severity": flags_by_severity,
            "top_concerns": top_concerns,
            "category_breakdown": {
                cat.value: {
                    "score": round(breakdown["score"], 1),
                    "flags_triggered": breakdown["triggered_count"],
                    "flags_total": breakdown["total_count"],
                    "max_possible_points": breakdown["max_points"],
                    "actual_points": breakdown["actual_points"],
                }
                for cat, breakdown in category_breakdown.items()
            },
        }

        logger.info(
            f"Risk calculation complete: Score={result['risk_score']}, "
            f"Level={result['risk_level']}, Triggered={total_triggered}/54"
        )

        return result

    def _calculate_category_score(self, flags: List[RedFlagResult], category: FlagCategory) -> tuple:
        """
        Calculate score for a single category.

        Formula: (Σ triggered flag points) / (max possible points) * 100

        Returns:
            Tuple of (score: float, breakdown: dict)
        """
        if not flags:
            return 0.0, {"score": 0.0, "triggered_count": 0, "total_count": 0, "max_points": 0, "actual_points": 0}

        # Sum points for triggered flags
        actual_points = 0
        triggered_count = 0

        for flag in flags:
            if flag.is_triggered:
                points = self.SEVERITY_POINTS[flag.severity]
                # Weight by confidence score (0-100 -> 0-1)
                confidence_weight = flag.confidence_score / 100.0
                actual_points += points * confidence_weight
                triggered_count += 1

        # Calculate max possible points for this category
        max_points = 0
        severity_dist = self.CATEGORY_SEVERITY_DISTRIBUTION.get(category, {})

        for severity, count in severity_dist.items():
            max_points += self.SEVERITY_POINTS[severity] * count

        # Calculate percentage score
        score = (actual_points / max_points) * 100 if max_points > 0 else 0.0

        breakdown = {
            "score": score,
            "triggered_count": triggered_count,
            "total_count": len(flags),
            "max_points": max_points,
            "actual_points": round(actual_points, 2),
        }

        return min(score, 100.0), breakdown  # Cap at 100

    def _get_risk_level(self, risk_score: float) -> str:
        """
        Map risk score to risk level category.

        Thresholds:
        - 0-20: LOW
        - 20-40: MODERATE
        - 40-60: ELEVATED
        - 60-80: HIGH
        - 80-100: CRITICAL
        """
        if risk_score < 20:
            return "LOW"
        elif risk_score < 40:
            return "MODERATE"
        elif risk_score < 60:
            return "ELEVATED"
        elif risk_score < 80:
            return "HIGH"
        else:
            return "CRITICAL"

    def _group_by_category(self, flag_results: List[RedFlagResult]) -> Dict:
        """Group flags by category."""
        grouped = {}
        for flag in flag_results:
            if flag.category not in grouped:
                grouped[flag.category] = []
            grouped[flag.category].append(flag)
        return grouped

    def _count_by_severity(self, flag_results: List[RedFlagResult]) -> Dict:
        """Count triggered flags by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for flag in flag_results:
            if flag.is_triggered:
                severity_key = flag.severity.value.lower()
                counts[severity_key] += 1

        return counts

    def _get_top_concerns(self, flag_results: List[RedFlagResult], limit: int = 10) -> List[str]:
        """
        Get top triggered flags sorted by severity and confidence.

        Ranking criteria:
        1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
        2. Confidence score (higher is more concerning)
        """
        severity_order = {FlagSeverity.CRITICAL: 0, FlagSeverity.HIGH: 1, FlagSeverity.MEDIUM: 2, FlagSeverity.LOW: 3}

        # Filter triggered flags
        triggered = [f for f in flag_results if f.is_triggered]

        # Sort by severity first, then by confidence
        triggered.sort(key=lambda f: (severity_order[f.severity], -f.confidence_score))

        # Return flag names
        return [f.flag_name for f in triggered[:limit]]

    def get_risk_description(self, risk_score: float, risk_level: str) -> str:
        """Get human-readable risk description."""
        descriptions = {
            "LOW": "The company exhibits minimal red flags. Financial reporting appears transparent and reliable.",
            "MODERATE": "Some concerns detected but not alarming. Monitor specific flagged areas closely.",
            "ELEVATED": "Multiple red flags detected across categories. Increased scrutiny and due diligence recommended.",
            "HIGH": "Significant accounting and governance red flags present. Exercise caution and consider professional forensic analysis.",
            "CRITICAL": "Severe red flags detected. High probability of accounting irregularities or fraud. Immediate investigation recommended.",
        }

        return descriptions.get(risk_level, "Risk level assessment unavailable")

    def get_category_description(self, category: FlagCategory) -> str:
        """Get description of what each category measures."""
        descriptions = {
            FlagCategory.AUDITOR: "Auditor-related issues: resignations, opinion quality, tenure, and audit fees",
            FlagCategory.CASH_FLOW: "Cash flow quality: CFO vs profits, working capital trends, and cash conversion",
            FlagCategory.RELATED_PARTY: "Related party transactions: volume, loans, complexity, and transparency",
            FlagCategory.PROMOTER: "Promoter behavior: share pledging, stake changes, and compensation",
            FlagCategory.GOVERNANCE: "Corporate governance: board quality, director changes, and regulatory compliance",
            FlagCategory.BALANCE_SHEET: "Balance sheet quality: debt levels, asset quality, and contingent liabilities",
            FlagCategory.REVENUE: "Revenue quality: concentration, policy changes, and recognition patterns",
            FlagCategory.TEXTUAL: "Textual analysis: management tone, disclosure quality, and language patterns",
        }

        return descriptions.get(category, "Category description unavailable")


# Singleton instance
risk_calculator = RiskCalculator()
