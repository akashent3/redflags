"""Risk scoring engine - calculates composite risk score from red flag results."""

import logging
from typing import Dict, List

from services.models import FlagCategory, FlagSeverity, RedFlagResult

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate composite risk score from red flag results."""

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

    SEVERITY_POINTS = {
        FlagSeverity.CRITICAL: 25,
        FlagSeverity.HIGH: 15,
        FlagSeverity.MEDIUM: 8,
        FlagSeverity.LOW: 3,
    }

    CATEGORY_SEVERITY_DISTRIBUTION = {
        FlagCategory.AUDITOR: {
            FlagSeverity.CRITICAL: 3,
            FlagSeverity.HIGH: 3,
            FlagSeverity.MEDIUM: 2,
            FlagSeverity.LOW: 0,
        },
        FlagCategory.CASH_FLOW: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 4,
            FlagSeverity.MEDIUM: 4,
            FlagSeverity.LOW: 0,
        },
        FlagCategory.RELATED_PARTY: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 3,
            FlagSeverity.MEDIUM: 4,
            FlagSeverity.LOW: 0,
        },
        FlagCategory.PROMOTER: {
            FlagSeverity.CRITICAL: 1,
            FlagSeverity.HIGH: 2,
            FlagSeverity.MEDIUM: 2,
            FlagSeverity.LOW: 1,
        },
        FlagCategory.GOVERNANCE: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 3,
            FlagSeverity.MEDIUM: 4,
            FlagSeverity.LOW: 0,
        },
        FlagCategory.BALANCE_SHEET: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 4,
            FlagSeverity.MEDIUM: 3,
            FlagSeverity.LOW: 0,
        },
        FlagCategory.REVENUE: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 1,
            FlagSeverity.MEDIUM: 3,
            FlagSeverity.LOW: 1,
        },
        FlagCategory.TEXTUAL: {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 1,
            FlagSeverity.MEDIUM: 4,
            FlagSeverity.LOW: 1,
        },
    }

    def calculate_risk_score(self, flag_results: List[RedFlagResult]) -> Dict:
        logger.info(f"Calculating risk score from {len(flag_results)} flags")

        flags_by_category = {}
        for flag in flag_results:
            flags_by_category.setdefault(flag.category, []).append(flag)

        category_scores = {}
        category_breakdown = {}
        for category in FlagCategory:
            flags = flags_by_category.get(category, [])
            score, breakdown = self._calculate_category_score(flags, category)
            category_scores[category] = score
            category_breakdown[category] = breakdown

        risk_score = sum(
            self.CATEGORY_WEIGHTS[cat] * score
            for cat, score in category_scores.items()
        )

        risk_level = self._get_risk_level(risk_score)
        flags_by_severity = self._count_by_severity(flag_results)
        top_concerns = self._get_top_concerns(flag_results, limit=10)
        total_triggered = sum(1 for f in flag_results if f.is_triggered)
        total_flags = len(flag_results)
        trigger_percentage = (total_triggered / total_flags * 100) if total_flags else 0

        return {
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level,
            "risk_description": self.get_risk_description(risk_score, risk_level),
            "category_scores": {
                cat.value: round(score, 1) for cat, score in category_scores.items()
            },
            "flags_triggered_count": total_triggered,
            "flags_total_count": total_flags,
            "trigger_percentage": round(trigger_percentage, 1),
            "flags_by_severity": flags_by_severity,
            "top_concerns": top_concerns,
            "category_breakdown": {
                cat.value: {
                    "score": round(bd["score"], 1),
                    "flags_triggered": bd["triggered_count"],
                    "flags_total": bd["total_count"],
                    "max_possible_points": bd["max_points"],
                    "actual_points": bd["actual_points"],
                }
                for cat, bd in category_breakdown.items()
            },
        }

    def _calculate_category_score(
        self, flags: List[RedFlagResult], category: FlagCategory
    ) -> tuple:
        if not flags:
            return 0.0, {
                "score": 0.0,
                "triggered_count": 0,
                "total_count": 0,
                "max_points": 0,
                "actual_points": 0,
            }

        actual_points = 0
        triggered_count = 0
        for flag in flags:
            if flag.is_triggered:
                points = self.SEVERITY_POINTS[flag.severity]
                confidence_weight = flag.confidence_score / 100.0
                actual_points += points * confidence_weight
                triggered_count += 1

        max_points = 0
        severity_dist = self.CATEGORY_SEVERITY_DISTRIBUTION.get(category, {})
        for severity, count in severity_dist.items():
            max_points += self.SEVERITY_POINTS[severity] * count

        score = (actual_points / max_points) * 100 if max_points > 0 else 0.0
        return min(score, 100.0), {
            "score": min(score, 100.0),
            "triggered_count": triggered_count,
            "total_count": len(flags),
            "max_points": max_points,
            "actual_points": round(actual_points, 2),
        }

    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score < 20:
            return "LOW"
        elif risk_score < 40:
            return "MODERATE"
        elif risk_score < 60:
            return "ELEVATED"
        elif risk_score < 80:
            return "HIGH"
        return "CRITICAL"

    def _count_by_severity(self, flag_results: List[RedFlagResult]) -> Dict:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for flag in flag_results:
            if flag.is_triggered:
                counts[flag.severity.value.lower()] += 1
        return counts

    def _get_top_concerns(
        self, flag_results: List[RedFlagResult], limit: int = 10
    ) -> List[Dict]:
        severity_order = {
            FlagSeverity.CRITICAL: 0,
            FlagSeverity.HIGH: 1,
            FlagSeverity.MEDIUM: 2,
            FlagSeverity.LOW: 3,
        }
        triggered = [f for f in flag_results if f.is_triggered]
        triggered.sort(key=lambda f: (severity_order[f.severity], -f.confidence_score))
        return [
            {
                "flag_number": f.flag_number,
                "flag_name": f.flag_name,
                "severity": f.severity.value,
                "category": f.category.value,
                "confidence": f.confidence_score,
                "evidence": f.evidence_text,
            }
            for f in triggered[:limit]
        ]

    def get_risk_description(self, risk_score: float, risk_level: str) -> str:
        descriptions = {
            "LOW": "The company exhibits minimal red flags. Financial reporting appears transparent and reliable.",
            "MODERATE": "Some concerns detected but not alarming. Monitor specific flagged areas closely.",
            "ELEVATED": "Multiple red flags detected across categories. Increased scrutiny recommended.",
            "HIGH": "Significant accounting and governance red flags present. Exercise caution.",
            "CRITICAL": "Severe red flags detected. High probability of accounting irregularities.",
        }
        return descriptions.get(risk_level, "Risk assessment unavailable")


risk_calculator = RiskCalculator()
