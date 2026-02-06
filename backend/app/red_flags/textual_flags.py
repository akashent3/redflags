"""Category 8: Textual Analysis Red Flags (6 flags, 5% weight).

These flags use LLM analysis to detect qualitative red flags in management
discussion, auditor language, and disclosure quality.
"""

import json
import logging
from typing import Dict

from app.llm.gemini_client import gemini_client
from app.llm.prompts import MDA_TONE_ANALYSIS_PROMPT, RED_FLAG_TEXT_DETECTION_PROMPT
from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class MDADefensiveToneFlag(RedFlagBase):
    """Flag #49: MD&A Tone is Defensive (MEDIUM)."""

    def __init__(self):
        self.flag_number = 49
        self.flag_name = "MD&A Tone Defensive"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM
        self.description = "Management discussion and analysis has defensive or evasive tone"

    def check(self, data: Dict) -> RedFlagResult:
        """Use LLM to analyze MD&A tone."""
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")

        if not mda_text or len(mda_text) < 200:
            return self.create_not_triggered_result("MD&A section not found or too short")

        try:
            # Limit text to avoid token limits (use first 10,000 characters)
            mda_sample = mda_text[:10000]

            # Call Gemini for tone analysis
            prompt = MDA_TONE_ANALYSIS_PROMPT.format(
                mda_text=mda_sample, previous_year_context=""  # TODO: Add historical comparison
            )

            response = gemini_client.generate_structured_output(prompt, output_format="json", temperature=0.1)

            # Parse response
            analysis = json.loads(response)

            tone = analysis.get("tone", "").lower()
            tone_score = analysis.get("tone_score", 0)
            key_findings = analysis.get("key_findings", [])

            # Determine if defensive/negative
            is_defensive = tone in ["defensive", "negative", "evasive", "pessimistic"]

            if is_defensive and tone_score >= 6:  # Score 6+ out of 10
                evidence = f"Management tone analysis: {tone.capitalize()} (score: {tone_score}/10). "
                evidence += "Key findings: " + "; ".join(key_findings[:3]) + "."

                return self.create_triggered_result(
                    evidence=evidence,
                    confidence=tone_score * 10,  # Convert 0-10 to 0-100
                    extracted_data={
                        "tone": tone,
                        "tone_score": tone_score,
                        "key_findings": key_findings,
                        "gemini_analysis": analysis,
                    },
                    detection_method="llm",
                )

            return self.create_not_triggered_result(f"MD&A tone is {tone} (acceptable)")

        except Exception as e:
            logger.error(f"Flag 49 LLM analysis failed: {e}")
            return self.create_not_triggered_result(f"Analysis failed: {str(e)}")


class IncreasedJargonFlag(RedFlagBase):
    """Flag #50: Increased Jargon/Complexity (LOW)."""

    def __init__(self):
        self.flag_number = 50
        self.flag_name = "Increased Jargon"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.LOW
        self.description = "MD&A readability declined (more complex language)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if MD&A has become more complex year-over-year."""
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")

        if not mda_text or len(mda_text) < 500:
            return self.create_not_triggered_result("MD&A section not found or too short")

        try:
            # Calculate readability score using simple metrics
            # Flesch-Kincaid grade level approximation

            words = mda_text.split()
            word_count = len(words)

            # Count sentences (approximate using punctuation)
            import re

            sentences = re.split(r'[.!?]+', mda_text)
            sentence_count = len([s for s in sentences if s.strip()])

            # Count syllables (approximate)
            def count_syllables(word):
                word = word.lower()
                vowels = "aeiou"
                syllable_count = 0
                previous_was_vowel = False
                for char in word:
                    is_vowel = char in vowels
                    if is_vowel and not previous_was_vowel:
                        syllable_count += 1
                    previous_was_vowel = is_vowel
                # Adjust for silent e
                if word.endswith("e"):
                    syllable_count -= 1
                # Minimum of 1 syllable per word
                return max(1, syllable_count)

            total_syllables = sum(count_syllables(word) for word in words[:1000])  # Sample first 1000 words

            # Flesch-Kincaid Grade Level
            if sentence_count > 0 and word_count > 0:
                avg_words_per_sentence = word_count / sentence_count
                avg_syllables_per_word = total_syllables / min(1000, word_count)

                grade_level = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
            else:
                grade_level = 0

            # For MVP, we don't have historical data, so trigger if grade level > 16 (college+)
            is_complex = grade_level > 16

            if is_complex:
                evidence = (
                    f"MD&A readability: Grade level {grade_level:.1f} (college+ complexity). "
                    f"Average {avg_words_per_sentence:.1f} words per sentence. "
                    f"High complexity may indicate obfuscation of poor performance."
                )

                return self.create_triggered_result(
                    evidence=evidence,
                    confidence=65.0,
                    extracted_data={
                        "grade_level": grade_level,
                        "avg_words_per_sentence": avg_words_per_sentence,
                        "avg_syllables_per_word": avg_syllables_per_word,
                    },
                )

            return self.create_not_triggered_result(f"MD&A readability is acceptable (grade level {grade_level:.1f})")

        except Exception as e:
            logger.error(f"Flag 50 readability calculation failed: {e}")
            return self.create_not_triggered_result(f"Analysis failed: {str(e)}")


class DecliningDisclosureFlag(RedFlagBase):
    """Flag #51: Declining Disclosure Quality (MEDIUM)."""

    def __init__(self):
        self.flag_number = 51
        self.flag_name = "Declining Disclosure"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM
        self.description = "MD&A or notes disclosure length decreased significantly"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if disclosure length has decreased."""
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Calculate current disclosure length
        current_length = len(mda_text) + len(notes_text)

        if current_length < 1000:
            return self.create_not_triggered_result("Disclosure sections not found or too short")

        # For MVP, we don't have historical data, so check if abnormally short
        # Typical annual report disclosures: 50,000-200,000 characters

        is_unusually_short = current_length < 30000  # Less than 30k characters

        if is_unusually_short:
            evidence = (
                f"Disclosure length is unusually brief: {current_length:,} characters "
                f"(MD&A: {len(mda_text):,}, Notes: {len(notes_text):,}). "
                f"Reduced disclosure may indicate reduced transparency."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "total_length": current_length,
                    "mda_length": len(mda_text),
                    "notes_length": len(notes_text),
                },
            )

        return self.create_not_triggered_result("Disclosure length is adequate")


class RiskFactorsExpandingFlag(RedFlagBase):
    """Flag #52: Risk Factors Section Expanding (MEDIUM)."""

    def __init__(self):
        self.flag_number = 52
        self.flag_name = "Risk Factors Expanding"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM
        self.description = "Number of risk factors mentioned increased significantly"

    def check(self, data: Dict) -> RedFlagResult:
        """Check if risk factor disclosures have expanded."""
        directors_report = data.get("sections", {}).get("directors_report", "")
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")

        combined_text = directors_report + " " + mda_text

        if not combined_text or len(combined_text) < 1000:
            return self.create_not_triggered_result("Risk factor disclosures not found")

        # Count risk-related mentions
        risk_keywords = [
            "risk",
            "threat",
            "challenge",
            "concern",
            "uncertainty",
            "adverse",
            "difficulty",
            "obstacle",
        ]

        combined_lower = combined_text.lower()

        # Count occurrences
        risk_count = sum(combined_lower.count(keyword) for keyword in risk_keywords)

        # Calculate risk mention density (per 1000 words)
        word_count = len(combined_text.split())
        risk_density = (risk_count / word_count) * 1000 if word_count > 0 else 0

        # Trigger if risk density > 20 mentions per 1000 words (high)
        is_high_risk_density = risk_density > 20

        if is_high_risk_density:
            evidence = (
                f"Risk factor disclosures are extensive: {risk_count} risk-related mentions "
                f"({risk_density:.1f} per 1000 words). "
                f"Expanding risk disclosures may signal management concerns about future prospects."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "risk_count": risk_count,
                    "risk_density": risk_density,
                    "word_count": word_count,
                },
            )

        return self.create_not_triggered_result("Risk factor disclosures are normal")


class ContradictionsMDAFinancialsFlag(RedFlagBase):
    """Flag #53: Contradictions Between MD&A and Financials (HIGH)."""

    def __init__(self):
        self.flag_number = 53
        self.flag_name = "Contradictions MD&A vs Financials"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.HIGH
        self.description = "Management narrative contradicts financial performance"

    def check(self, data: Dict) -> RedFlagResult:
        """Use LLM to detect contradictions between narrative and numbers."""
        mda_text = data.get("sections", {}).get("management_discussion_analysis", "")
        financial_data = data.get("financial_data", {})

        if not mda_text or len(mda_text) < 200:
            return self.create_not_triggered_result("MD&A section not found or too short")

        try:
            # Extract key financial metrics for context
            profit_loss = financial_data.get("profit_loss", {})
            cash_flow = financial_data.get("cash_flow", {})

            revenue = self.extract_value(profit_loss, "revenue", "value", default=0.0)
            pat = self.extract_value(profit_loss, "net_profit", "value", default=0.0)
            cfo = self.extract_value(cash_flow, "cash_from_operations", "value", default=0.0)

            # Create financial summary for LLM
            financial_summary = f"""
            Financial Performance:
            - Revenue: {revenue:,.0f}
            - Net Profit: {pat:,.0f}
            - Cash from Operations: {cfo:,.0f}
            """

            # Limit MD&A text
            mda_sample = mda_text[:8000]

            # Build prompt for contradiction detection
            prompt = RED_FLAG_TEXT_DETECTION_PROMPT.format(
                text=mda_sample,
                context=f"Compare this management discussion with actual financial results: {financial_summary}. Look for contradictions, overly optimistic language not supported by numbers, or evasive explanations.",
            )

            response = gemini_client.generate_structured_output(prompt, output_format="json", temperature=0.1)

            # Parse response
            analysis = json.loads(response)

            red_flags_found = analysis.get("red_flags_found", [])
            severity_score = analysis.get("severity_score", 0)

            # Trigger if contradictions detected
            has_contradictions = len(red_flags_found) > 0 and severity_score >= 6

            if has_contradictions:
                evidence = f"LLM detected contradictions between MD&A and financial results (severity: {severity_score}/10). "
                evidence += "Key issues: " + "; ".join(red_flags_found[:3]) + "."

                return self.create_triggered_result(
                    evidence=evidence,
                    confidence=severity_score * 10,
                    extracted_data={
                        "red_flags_found": red_flags_found,
                        "severity_score": severity_score,
                        "gemini_analysis": analysis,
                    },
                    detection_method="llm",
                )

            return self.create_not_triggered_result("No significant contradictions detected")

        except Exception as e:
            logger.error(f"Flag 53 LLM analysis failed: {e}")
            return self.create_not_triggered_result(f"Analysis failed: {str(e)}")


class UnusualAuditLanguageFlag(RedFlagBase):
    """Flag #54: Unusual Audit Report Language (MEDIUM)."""

    def __init__(self):
        self.flag_number = 54
        self.flag_name = "Unusual Audit Language"
        self.category = FlagCategory.TEXTUAL
        self.severity = FlagSeverity.MEDIUM
        self.description = "Auditor report contains unusual or concerning language"

    def check(self, data: Dict) -> RedFlagResult:
        """Use LLM to detect unusual auditor language."""
        auditor_text = data.get("sections", {}).get("auditor_report", "")

        if not auditor_text or len(auditor_text) < 200:
            return self.create_not_triggered_result("Auditor report section not found or too short")

        try:
            # Limit text
            auditor_sample = auditor_text[:8000]

            # Build prompt for unusual language detection
            prompt = RED_FLAG_TEXT_DETECTION_PROMPT.format(
                text=auditor_sample,
                context="Analyze this auditor report for unusual language, hedging statements, expressions of concern, or deviations from standard audit language. Look for phrases like 'however', 'although', 'subject to', 'unable to', or similar qualifiers.",
            )

            response = gemini_client.generate_structured_output(prompt, output_format="json", temperature=0.1)

            # Parse response
            analysis = json.loads(response)

            red_flags_found = analysis.get("red_flags_found", [])
            severity_score = analysis.get("severity_score", 0)

            # Trigger if unusual language detected
            has_unusual_language = len(red_flags_found) > 0 and severity_score >= 5

            if has_unusual_language:
                evidence = f"LLM detected unusual language in auditor report (severity: {severity_score}/10). "
                evidence += "Key concerns: " + "; ".join(red_flags_found[:3]) + "."

                return self.create_triggered_result(
                    evidence=evidence,
                    confidence=severity_score * 10,
                    extracted_data={
                        "red_flags_found": red_flags_found,
                        "severity_score": severity_score,
                        "gemini_analysis": analysis,
                    },
                    detection_method="llm",
                )

            return self.create_not_triggered_result("Auditor language appears standard")

        except Exception as e:
            logger.error(f"Flag 54 LLM analysis failed: {e}")
            return self.create_not_triggered_result(f"Analysis failed: {str(e)}")


# Register all textual flags
flag_registry.register(MDADefensiveToneFlag())
flag_registry.register(IncreasedJargonFlag())
flag_registry.register(DecliningDisclosureFlag())
flag_registry.register(RiskFactorsExpandingFlag())
flag_registry.register(ContradictionsMDAFinancialsFlag())
flag_registry.register(UnusualAuditLanguageFlag())

logger.info("Registered 6 textual/LLM flags (Category 8)")
