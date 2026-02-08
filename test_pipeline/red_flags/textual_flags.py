"""Category 8: Textual Analysis Red Flags (6 flags, 5% weight).

These flags use pre-computed LLM analysis from the Gemini pipeline (textual_analysis)
instead of making direct LLM calls, since Gemini analysis is done earlier.
"""

import re
import logging
from typing import Dict

from red_flags.models import FlagCategory, FlagSeverity
from red_flags.base import RedFlagBase
from red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class MDADefensiveToneFlag(RedFlagBase):
    """Flag #49: MD&A Tone is Defensive (MEDIUM). Uses pre-computed textual_analysis."""
    def __init__(self):
        self.flag_number = 49
        self.flag_name = "MD&A Tone Defensive"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        ta = data.get("textual_analysis", {})
        mda_tone = ta.get("mda_tone", {})
        if not mda_tone:
            mda_text = data.get("sections", {}).get("management_discussion_analysis", "")
            if not mda_text or len(mda_text) < 200:
                return self.create_not_triggered_result("MD&A section not found or too short")
            return self.create_not_triggered_result("MD&A tone analysis not available")
        tone = mda_tone.get("tone", "").lower()
        tone_score = mda_tone.get("tone_score", 0)
        findings = mda_tone.get("key_findings", [])
        is_defensive = tone in ["defensive", "negative", "evasive", "pessimistic"]
        if is_defensive and tone_score >= 6:
            evidence = f"Management tone: {tone.capitalize()} (score: {tone_score}/10). "
            if findings:
                evidence += "Key findings: " + "; ".join(findings[:3]) + "."
            return self.create_triggered_result(evidence=evidence, confidence=tone_score * 10, extracted_data={"tone": tone, "tone_score": tone_score, "findings": findings}, detection_method="llm")
        return self.create_not_triggered_result(f"MD&A tone is {tone} (acceptable)")


class IncreasedJargonFlag(RedFlagBase):
    """Flag #50: Increased Jargon/Complexity (LOW). Rule-based Flesch-Kincaid."""
    def __init__(self):
        self.flag_number = 50
        self.flag_name = "Increased Jargon"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.LOW

    def check(self, data: Dict):
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")
        if not mda_text or len(mda_text) < 500:
            return self.create_not_triggered_result("MD&A section not found or too short")
        try:
            words = mda_text.split()
            word_count = len(words)
            sentences = re.split(r'[.!?]+', mda_text)
            sentence_count = len([s for s in sentences if s.strip()])
            def count_syllables(word):
                word = word.lower()
                vowels = "aeiou"
                count = 0
                prev_vowel = False
                for c in word:
                    is_v = c in vowels
                    if is_v and not prev_vowel:
                        count += 1
                    prev_vowel = is_v
                if word.endswith("e"):
                    count -= 1
                return max(1, count)
            total_syllables = sum(count_syllables(w) for w in words[:1000])
            if sentence_count > 0 and word_count > 0:
                avg_wps = word_count / sentence_count
                avg_spw = total_syllables / min(1000, word_count)
                grade = 0.39 * avg_wps + 11.8 * avg_spw - 15.59
            else:
                grade = 0
            if grade > 16:
                return self.create_triggered_result(evidence=f"MD&A readability: Grade level {grade:.1f} (college+ complexity). Avg {avg_wps:.1f} words/sentence. High complexity may indicate obfuscation.", confidence=65.0, extracted_data={"grade_level": grade, "avg_wps": avg_wps})
            return self.create_not_triggered_result(f"MD&A readability acceptable (grade {grade:.1f})")
        except Exception as e:
            return self.create_not_triggered_result(f"Analysis failed: {e}")


class DecliningDisclosureFlag(RedFlagBase):
    """Flag #51: Declining Disclosure Quality (MEDIUM). Uses pre-computed textual_analysis."""
    def __init__(self):
        self.flag_number = 51
        self.flag_name = "Declining Disclosure"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        ta = data.get("textual_analysis", {})
        dq = ta.get("disclosure_quality", {})
        if dq and dq.get("is_unusually_short"):
            mda_wc = dq.get("mda_word_count", 0)
            notes_wc = dq.get("notes_word_count", 0)
            return self.create_triggered_result(evidence=f"Disclosure unusually brief (MD&A: {mda_wc:,} words, Notes: {notes_wc:,} words). Reduced transparency.", confidence=70.0, extracted_data={"mda_words": mda_wc, "notes_words": notes_wc}, detection_method="llm")
        # Fallback: check section text lengths
        mda = data.get("sections", {}).get("management_discussion_analysis", "")
        notes = data.get("sections", {}).get("notes_to_accounts", "")
        total = len(mda) + len(notes)
        if total < 1000:
            return self.create_not_triggered_result("Disclosure sections not found or too short")
        if total < 30000:
            return self.create_triggered_result(evidence=f"Disclosure length unusually brief: {total:,} chars (MD&A: {len(mda):,}, Notes: {len(notes):,}). Reduced transparency.", confidence=70.0, extracted_data={"total_length": total})
        return self.create_not_triggered_result("Disclosure length adequate")


class RiskFactorsExpandingFlag(RedFlagBase):
    """Flag #52: Risk Factors Section Expanding (MEDIUM). Uses pre-computed data."""
    def __init__(self):
        self.flag_number = 52
        self.flag_name = "Risk Factors Expanding"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        ta = data.get("textual_analysis", {})
        rf = ta.get("risk_factors", {})
        if rf:
            density = rf.get("risk_density_per_1000_words", 0)
            count = rf.get("risk_count", 0)
            if density > 20 or rf.get("expanding"):
                return self.create_triggered_result(evidence=f"Risk disclosures extensive: {count} risk mentions ({density:.1f} per 1000 words). May signal management concerns.", confidence=70.0, extracted_data={"risk_count": count, "density": density}, detection_method="llm")
        # Fallback: count risk keywords in text
        dr = data.get("sections", {}).get("directors_report", "")
        mda = data.get("sections", {}).get("management_discussion_analysis", "")
        combined = (dr + " " + mda).lower()
        if len(combined) < 1000:
            return self.create_not_triggered_result("Risk factor disclosures not found")
        risk_keywords = ["risk", "threat", "challenge", "concern", "uncertainty", "adverse", "difficulty", "obstacle"]
        risk_count = sum(combined.count(kw) for kw in risk_keywords)
        word_count = len(combined.split())
        density = (risk_count / word_count) * 1000 if word_count > 0 else 0
        if density > 20:
            return self.create_triggered_result(evidence=f"Risk disclosures extensive: {risk_count} mentions ({density:.1f} per 1000 words). May signal concerns.", confidence=70.0, extracted_data={"risk_count": risk_count, "density": density})
        return self.create_not_triggered_result("Risk factor disclosures normal")


class ContradictionsMDAFinancialsFlag(RedFlagBase):
    """Flag #53: Contradictions Between MD&A and Financials (HIGH). Uses pre-computed data."""
    def __init__(self):
        self.flag_number = 53
        self.flag_name = "Contradictions MD&A vs Financials"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.HIGH

    def check(self, data: Dict):
        ta = data.get("textual_analysis", {})
        contradictions = ta.get("contradictions", {})
        if not contradictions:
            return self.create_not_triggered_result("Contradiction analysis not available")
        found = contradictions.get("found", False)
        severity = contradictions.get("severity_score", 0)
        flags_found = contradictions.get("red_flags_found", [])
        details = contradictions.get("details", [])
        if found and severity >= 6:
            evidence = f"Contradictions detected between MD&A and financials (severity: {severity}/10). "
            items = flags_found or details
            if items:
                evidence += "Key issues: " + "; ".join(items[:3]) + "."
            return self.create_triggered_result(evidence=evidence, confidence=severity * 10, extracted_data={"severity": severity, "flags_found": flags_found}, detection_method="llm")
        return self.create_not_triggered_result("No significant contradictions detected")


class UnusualAuditLanguageFlag(RedFlagBase):
    """Flag #54: Unusual Audit Report Language (MEDIUM). Uses pre-computed data."""
    def __init__(self):
        self.flag_number = 54
        self.flag_name = "Unusual Audit Language"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM

    def check(self, data: Dict):
        ta = data.get("textual_analysis", {})
        ual = ta.get("unusual_audit_language", {})
        if not ual:
            return self.create_not_triggered_result("Audit language analysis not available")
        found = ual.get("found", False)
        severity = ual.get("severity_score", 0)
        flags_found = ual.get("red_flags_found", [])
        details = ual.get("details", [])
        if found and severity >= 5:
            evidence = f"Unusual language in auditor report (severity: {severity}/10). "
            items = flags_found or details
            if items:
                evidence += "Key concerns: " + "; ".join(items[:3]) + "."
            return self.create_triggered_result(evidence=evidence, confidence=severity * 10, extracted_data={"severity": severity, "flags_found": flags_found}, detection_method="llm")
        return self.create_not_triggered_result("Auditor language appears standard")


flag_registry.register(MDADefensiveToneFlag())
flag_registry.register(IncreasedJargonFlag())
flag_registry.register(DecliningDisclosureFlag())
flag_registry.register(RiskFactorsExpandingFlag())
flag_registry.register(ContradictionsMDAFinancialsFlag())
flag_registry.register(UnusualAuditLanguageFlag())
