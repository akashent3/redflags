"""Base class for all red flag detectors."""

import logging
from typing import Dict, List

from red_flags.models import FlagCategory, FlagSeverity, RedFlagResult

logger = logging.getLogger(__name__)


class RedFlagBase:
    """Base class for all red flag detectors."""

    def __init__(self):
        self.flag_number: int = 0
        self.flag_name: str = ""
        self.category: FlagCategory = FlagCategory.AUDITOR
        self.severity: FlagSeverity = FlagSeverity.MEDIUM

    def check(self, data: Dict) -> RedFlagResult:
        raise NotImplementedError

    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        if previous == 0 or previous is None:
            return 0.0
        try:
            return (current - previous) / abs(previous)
        except (ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def calculate_ratio(numerator: float, denominator: float) -> float:
        if denominator == 0 or denominator is None:
            return 0.0
        try:
            return numerator / denominator
        except (ValueError, ZeroDivisionError, TypeError):
            return 0.0

    @staticmethod
    def extract_value(data: Dict, *keys, default=0.0) -> float:
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, {})
            else:
                return default
        if isinstance(current, dict) and "value" in current:
            try:
                return float(current.get("value", default))
            except (ValueError, TypeError):
                return default
        try:
            return float(current) if current else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_percentage(value: float) -> float:
        return value * 100.0

    def create_not_triggered_result(self, reason: str = "") -> RedFlagResult:
        return RedFlagResult(
            flag_number=self.flag_number,
            flag_name=self.flag_name,
            category=self.category,
            severity=self.severity,
            is_triggered=False,
            confidence_score=0.0,
            evidence_text=reason or "No red flag detected",
            detection_method="rule_based",
        )

    def create_triggered_result(
        self, evidence: str, confidence: float = 90.0,
        page_refs: List[int] = None, extracted_data: Dict = None,
        detection_method: str = "rule_based",
    ) -> RedFlagResult:
        return RedFlagResult(
            flag_number=self.flag_number,
            flag_name=self.flag_name,
            category=self.category,
            severity=self.severity,
            is_triggered=True,
            confidence_score=confidence,
            evidence_text=evidence,
            page_references=page_refs or [],
            extracted_data=extracted_data or {},
            detection_method=detection_method,
        )
