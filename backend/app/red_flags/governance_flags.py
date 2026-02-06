"""Category 5: Corporate Governance Red Flags (7 flags, 12% weight).

Strong governance is essential for investor protection. Red flags include director
exits, CFO/CS changes, regulatory penalties, and poor board practices.
"""

import logging
from typing import Dict

from app.models.red_flag import FlagCategory, FlagSeverity
from app.red_flags.base import RedFlagBase, RedFlagResult
from app.red_flags.registry import flag_registry

logger = logging.getLogger(__name__)


class IndependentDirectorExitFlag(RedFlagBase):
    """Flag #30: Independent Director Resignation (HIGH)."""

    def __init__(self):
        self.flag_number = 30
        self.flag_name = "Independent Director Exit"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH
        self.description = "Independent director resigned during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for independent director resignations."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")
        directors_report = data.get("sections", {}).get("directors_report", "")

        # Search for resignation keywords related to independent directors
        resignation_keywords = [
            "independent director resigned",
            "independent director resignation",
            "id resigned",
            "resignation of independent director",
            "independent director ceased",
            "independent director stepped down",
        ]

        combined_text = (governance_text + " " + directors_report).lower()
        resignation_mentions = []

        for keyword in resignation_keywords:
            if keyword in combined_text:
                resignation_mentions.append(keyword)

        # Also search for "independent" near "resignation"
        if "independent" in combined_text and "resign" in combined_text:
            # Check if they appear close together (within 50 characters)
            import re

            pattern = r'independent.{0,50}resign|resign.{0,50}independent'
            if re.search(pattern, combined_text):
                if not resignation_mentions:  # Avoid duplicates
                    resignation_mentions.append("independent director resignation (contextual)")

        # Trigger if resignation mentions found
        if resignation_mentions:
            evidence = (
                f"Independent director resignation detected "
                f"({len(resignation_mentions)} references: {', '.join(set(resignation_mentions[:3]))}). "
                f"ID exits often signal governance concerns or disagreements."
            )

            return self.create_triggered_result(
                evidence=evidence,
                confidence=85.0,
                extracted_data={
                    "resignation_mentions": resignation_mentions,
                },
            )

        return self.create_not_triggered_result("No independent director resignations detected")


class CFOCSChangeFlag(RedFlagBase):
    """Flag #31: CFO or Company Secretary Changed (HIGH)."""

    def __init__(self):
        self.flag_number = 31
        self.flag_name = "CFO/CS Change in Year"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH
        self.description = "Chief Financial Officer or Company Secretary changed during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for CFO or CS changes."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")
        directors_report = data.get("sections", {}).get("directors_report", "")

        # Search for CFO/CS change keywords
        change_keywords = [
            "cfo resigned",
            "cfo appointed",
            "chief financial officer resigned",
            "chief financial officer appointed",
            "company secretary resigned",
            "company secretary appointed",
            "cs resigned",
            "cs appointed",
            "change of cfo",
            "change of company secretary",
            "new cfo",
            "new company secretary",
        ]

        combined_text = (governance_text + " " + directors_report).lower()
        change_mentions = []

        for keyword in change_keywords:
            if keyword in combined_text:
                change_mentions.append(keyword)

        # Categorize changes
        cfo_change = any("cfo" in mention or "chief financial officer" in mention for mention in change_mentions)
        cs_change = any("company secretary" in mention or "cs" in mention for mention in change_mentions)

        # Trigger if any change detected
        if change_mentions:
            evidence_parts = []

            if cfo_change:
                evidence_parts.append("CFO changed during the year")

            if cs_change:
                evidence_parts.append("Company Secretary changed during the year")

            evidence = ". ".join(evidence_parts) + f". {len(change_mentions)} references found. Key management changes may indicate underlying issues."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=90.0,
                extracted_data={
                    "change_mentions": change_mentions,
                    "cfo_change": cfo_change,
                    "cs_change": cs_change,
                },
            )

        return self.create_not_triggered_result("No CFO or CS changes detected")


class LowBoardAttendanceFlag(RedFlagBase):
    """Flag #32: Low Board Meeting Attendance (MEDIUM)."""

    def __init__(self):
        self.flag_number = 32
        self.flag_name = "Low Board Attendance"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Directors have low attendance at board meetings (< 75%)"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for poor board attendance."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")

        if not governance_text:
            return self.create_not_triggered_result("Corporate governance report not found")

        # Search for attendance percentage patterns
        import re

        governance_lower = governance_text.lower()

        # Pattern to find attendance percentages
        attendance_patterns = [
            r'attendance.*?(\d+)%',
            r'(\d+)%.*?attendance',
            r'attended\s+\d+\s+out\s+of\s+(\d+)',
        ]

        attendance_percentages = []

        for pattern in attendance_patterns:
            matches = re.findall(pattern, governance_lower)
            if matches:
                try:
                    percentages = [int(m) for m in matches if 0 <= int(m) <= 100]
                    attendance_percentages.extend(percentages)
                except:
                    pass

        if not attendance_percentages:
            return self.create_not_triggered_result("Board attendance data not found")

        # Calculate average attendance
        avg_attendance = sum(attendance_percentages) / len(attendance_percentages)
        min_attendance = min(attendance_percentages)

        # Trigger if average < 75% or any director < 50%
        low_avg = avg_attendance < 75
        very_low = min_attendance < 50

        if low_avg or very_low:
            evidence = (
                f"Board attendance concerns detected "
                f"(Average: {avg_attendance:.1f}%, Lowest: {min_attendance}%). "
            )

            if very_low:
                evidence += "At least one director attended less than 50% of meetings. "

            evidence += "Poor attendance suggests lack of board engagement."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=80.0,
                extracted_data={
                    "avg_attendance": avg_attendance,
                    "min_attendance": min_attendance,
                    "attendance_records": attendance_percentages,
                },
            )

        return self.create_not_triggered_result("Board attendance is satisfactory")


class RelatedOnAuditCommitteeFlag(RedFlagBase):
    """Flag #33: Related Party on Audit Committee (MEDIUM)."""

    def __init__(self):
        self.flag_number = 33
        self.flag_name = "Related on Audit Committee"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Audit committee composition raises independence concerns"

    def check(self, data: Dict) -> RedFlagResult:
        """Check audit committee independence."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")

        if not governance_text:
            return self.create_not_triggered_result("Corporate governance report not found")

        governance_lower = governance_text.lower()

        # Search for audit committee section
        audit_committee_section = ""
        if "audit committee" in governance_lower:
            # Extract audit committee section (next 500 characters)
            start_idx = governance_lower.find("audit committee")
            audit_committee_section = governance_lower[start_idx:start_idx + 500]

        if not audit_committee_section:
            return self.create_not_triggered_result("Audit committee details not found")

        # Look for independence concerns
        concern_keywords = [
            "executive director",
            "non-independent",
            "promoter",
            "related party",
            "not independent",
        ]

        concerns = []
        for keyword in concern_keywords:
            if keyword in audit_committee_section:
                concerns.append(keyword)

        # Also check if majority are independent
        independent_count = audit_committee_section.count("independent director")
        total_members_match = re.search(r'(\d+)\s+member', audit_committee_section)
        total_members = int(total_members_match.group(1)) if total_members_match else 0

        insufficient_independence = False
        if total_members > 0 and independent_count < total_members * 0.66:  # Less than 2/3 independent
            insufficient_independence = True

        # Trigger if concerns found or insufficient independence
        if concerns or insufficient_independence:
            evidence_parts = []

            if concerns:
                evidence_parts.append(
                    f"Audit committee independence concerns: {', '.join(set(concerns))}"
                )

            if insufficient_independence:
                evidence_parts.append(
                    f"Insufficient independent directors on audit committee ({independent_count}/{total_members})"
                )

            evidence = ". ".join(evidence_parts) + ". Audit committee should be majority independent for effective oversight."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "concerns": concerns,
                    "independent_count": independent_count,
                    "total_members": total_members,
                },
            )

        return self.create_not_triggered_result("Audit committee composition appears independent")


class DelayedAGMResultsFlag(RedFlagBase):
    """Flag #34: Delayed AGM or Results Filing (MEDIUM)."""

    def __init__(self):
        self.flag_number = 34
        self.flag_name = "Delayed AGM/Results"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Annual General Meeting or financial results filed late"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for filing delays."""
        directors_report = data.get("sections", {}).get("directors_report", "")
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Search for delay keywords
        delay_keywords = [
            "delayed",
            "extension",
            "extended time",
            "beyond due date",
            "filing delay",
            "postponed",
            "rescheduled",
            "late filing",
            "penalty for delay",
        ]

        combined_text = (directors_report + " " + notes_text).lower()
        delay_mentions = []

        for keyword in delay_keywords:
            if keyword in combined_text:
                delay_mentions.append(keyword)

        # Check for AGM-specific delays
        agm_delay = "agm" in combined_text and any(
            delay in combined_text[max(0, combined_text.find("agm") - 50):combined_text.find("agm") + 100]
            for delay in ["delay", "postpone", "extended"]
        )

        # Check for results filing delays
        results_delay = "result" in combined_text and any(
            delay in combined_text[max(0, combined_text.find("result") - 50):combined_text.find("result") + 100]
            for delay in ["delay", "late", "extended"]
        )

        # Trigger if delays detected
        if delay_mentions or agm_delay or results_delay:
            evidence_parts = []

            if agm_delay:
                evidence_parts.append("AGM delay mentioned")

            if results_delay:
                evidence_parts.append("Results filing delay mentioned")

            if delay_mentions and not (agm_delay or results_delay):
                evidence_parts.append(
                    f"Delay references in reports ({len(delay_mentions)} mentions)"
                )

            evidence = ". ".join(evidence_parts) + ". Filing delays may indicate operational or compliance issues."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=75.0,
                extracted_data={
                    "delay_mentions": delay_mentions[:5],  # Limit to 5
                    "agm_delay": agm_delay,
                    "results_delay": results_delay,
                },
            )

        return self.create_not_triggered_result("No filing delays detected")


class RegulatoryPenaltiesFlag(RedFlagBase):
    """Flag #35: SEBI/Stock Exchange Penalties (HIGH)."""

    def __init__(self):
        self.flag_number = 35
        self.flag_name = "SEBI/Exchange Penalties"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.HIGH
        self.description = "Company or directors faced regulatory penalties or sanctions"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for regulatory penalties."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")
        directors_report = data.get("sections", {}).get("directors_report", "")
        notes_text = data.get("sections", {}).get("notes_to_accounts", "")

        # Search for penalty keywords
        penalty_keywords = [
            "sebi penalty",
            "sebi fine",
            "stock exchange penalty",
            "regulatory penalty",
            "non-compliance penalty",
            "penalty imposed",
            "fine imposed",
            "penalty paid",
            "adjudication",
            "show cause notice",
            "regulatory action",
        ]

        combined_text = (governance_text + " " + directors_report + " " + notes_text).lower()
        penalty_mentions = []

        for keyword in penalty_keywords:
            if keyword in combined_text:
                penalty_mentions.append(keyword)

        # Extract penalty amounts if mentioned
        import re

        penalty_amount_pattern = r'penalty.*?(?:rs|inr|₹)\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        penalty_amounts = re.findall(penalty_amount_pattern, combined_text)

        total_penalty = 0
        if penalty_amounts:
            try:
                total_penalty = sum([float(amt.replace(',', '')) for amt in penalty_amounts])
            except:
                pass

        # Trigger if penalties mentioned
        if penalty_mentions:
            evidence = (
                f"Regulatory penalties or sanctions detected "
                f"({len(penalty_mentions)} references: {', '.join(set(penalty_mentions[:3]))}). "
            )

            if total_penalty > 0:
                evidence += f"Total penalties: {total_penalty:,.0f}. "

            evidence += "Regulatory actions indicate compliance failures."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=95.0,
                extracted_data={
                    "penalty_mentions": penalty_mentions,
                    "total_penalty": total_penalty,
                },
            )

        return self.create_not_triggered_result("No regulatory penalties detected")


class WhistleblowerComplaintsFlag(RedFlagBase):
    """Flag #36: Whistle-blower Complaints Received (MEDIUM)."""

    def __init__(self):
        self.flag_number = 36
        self.flag_name = "Whistle-blower Complaints"
        self.category = FlagCategory.GOVERNANCE
        self.severity = FlagSeverity.MEDIUM
        self.description = "Company received whistle-blower complaints during the year"

    def check(self, data: Dict) -> RedFlagResult:
        """Check for whistle-blower complaints."""
        governance_text = data.get("sections", {}).get("corporate_governance_report", "")
        directors_report = data.get("sections", {}).get("directors_report", "")

        # Search for whistle-blower mentions
        whistleblower_keywords = [
            "whistle blower complaint",
            "whistleblower complaint",
            "vigil mechanism complaint",
            "complaints received under",
            "whistle blower policy",
            "vigil mechanism",
        ]

        combined_text = (governance_text + " " + directors_report).lower()
        whistleblower_mentions = []

        for keyword in whistleblower_keywords:
            if keyword in combined_text:
                whistleblower_mentions.append(keyword)

        # Try to extract complaint count
        import re

        complaint_count = 0
        count_patterns = [
            r'(\d+)\s+complaint',
            r'complaint.*?(\d+)',
            r'(\d+).*?whistle',
        ]

        for pattern in count_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                try:
                    counts = [int(m) for m in matches if 0 < int(m) < 100]
                    if counts:
                        complaint_count = max(counts)
                        break
                except:
                    pass

        # Trigger if complaints > 0 or keywords suggesting complaints
        has_complaints = complaint_count > 0
        suggests_complaints = len(whistleblower_mentions) > 0 and "nil" not in combined_text[
            max(0, combined_text.find("whistle") - 20):combined_text.find("whistle") + 100
        ]

        if has_complaints or suggests_complaints:
            evidence = f"Whistle-blower mechanism disclosures present. "

            if complaint_count > 0:
                evidence += f"Number of complaints: {complaint_count}. "
            else:
                evidence += "Complaint details mentioned in governance report. "

            evidence += "Presence of complaints suggests internal control concerns."

            return self.create_triggered_result(
                evidence=evidence,
                confidence=70.0,
                extracted_data={
                    "complaint_count": complaint_count,
                    "whistleblower_mentions": whistleblower_mentions,
                },
            )

        return self.create_not_triggered_result("No whistle-blower complaints or complaints reported as nil")


# Register all governance flags
flag_registry.register(IndependentDirectorExitFlag())
flag_registry.register(CFOCSChangeFlag())
flag_registry.register(LowBoardAttendanceFlag())
flag_registry.register(RelatedOnAuditCommitteeFlag())
flag_registry.register(DelayedAGMResultsFlag())
flag_registry.register(RegulatoryPenaltiesFlag())
flag_registry.register(WhistleblowerComplaintsFlag())

logger.info("Registered 7 governance flags (Category 5)")
